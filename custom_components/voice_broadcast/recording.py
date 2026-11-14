"""Voice relay: upload a WAV once, play it on the selected speakers, delete it.

Security notes:
- The upload endpoint requires authentication.
- The download endpoint is intentionally unauthenticated because ESPHome
  speakers cannot send a bearer token. It only serves paths that were
  registered in memory under an unguessable token; the URL is never used to
  build a filesystem path.
- Audio bytes and tokens are never logged.
"""

from __future__ import annotations

import asyncio
import datetime
import ipaddress
import logging
import re
import secrets
import time
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import Context, HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import (
    API_PREFIX,
    ATTR_FAILED,
    ATTR_PLAYED,
    ATTR_SKIPPED,
    ATTR_TARGETED,
    CLEANUP_GRACE_SECONDS,
    CLEANUP_POLL_SECONDS,
    CONF_MAX_RECORD_SECONDS,
    CONF_NO_VOLUME_SPEAKERS,
    CONF_VOLUME,
    CONFIG_GET_PATH,
    DEFAULT_MAX_RECORD_SECONDS,
    DEFAULT_VOLUME,
    DOMAIN,
    IDLE_STATES,
    MAX_BODY_BYTES,
    MAX_DURATION_SECONDS,
    PLAYING_STATES,
    RECORDING_GET_PATH,
    RECORDING_POST_PATH,
    RECORDING_TTL_SECONDS,
    SWEEP_INTERVAL_SECONDS,
    TEMP_DIR_NAME,
    TOKEN_BYTES,
    TOKEN_PATTERN,
    VERSION,
)
from .wav import WavInfo, WavValidationError, parse_wav

_LOGGER = logging.getLogger(__name__)

_TOKEN_RE = re.compile(TOKEN_PATTERN)


class RecordingError(Exception):
    """A relay error that maps to a JSON HTTP response."""

    def __init__(self, code: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        super().__init__(code)
        self.code = code
        self.status = status


class RecordingBusyError(RecordingError):
    """Another announcement or recording is already running."""

    def __init__(self) -> None:
        super().__init__("busy", HTTPStatus.CONFLICT)


@dataclass(slots=True)
class Recording:
    """One uploaded WAV, registered in memory under a random token."""

    token: str
    path: Path
    entry_id: str
    duration: float
    size: int
    expires_at: float


class RecordingRegistry:
    """In-memory token registry for temporary recordings."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.temp_dir = Path(hass.config.path(TEMP_DIR_NAME))
        self._records: dict[str, Recording] = {}

    @property
    def active_count(self) -> int:
        """Return the number of registered tokens."""
        return len(self._records)

    def peek(self, token: str) -> Recording | None:
        """Return a record without removing it (a speaker may fetch twice)."""
        return self._records.get(token)

    async def async_save(self, entry_id: str, body: bytes, info: WavInfo) -> Recording:
        """Write the WAV to the private temp dir and register its token."""

        def _write() -> tuple[str, Path]:
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            while True:
                token = secrets.token_urlsafe(TOKEN_BYTES)
                path = self.temp_dir / f"{token}.wav"
                if token not in self._records and not path.exists():
                    break
            path.write_bytes(body)
            return token, path

        token, path = await self.hass.async_add_executor_job(_write)
        record = Recording(
            token=token,
            path=path,
            entry_id=entry_id,
            duration=info.duration,
            size=len(body),
            expires_at=time.monotonic() + RECORDING_TTL_SECONDS,
        )
        self._records[token] = record
        return record

    async def async_discard(self, token: str) -> None:
        """Unregister a token and delete its file (idempotent)."""
        record = self._records.pop(token, None)
        if record is not None:
            await self._async_unlink(record.path)

    async def async_discard_entry(self, entry_id: str) -> None:
        """Discard every recording owned by a config entry."""
        tokens = [
            token
            for token, record in self._records.items()
            if record.entry_id == entry_id
        ]
        for token in tokens:
            await self.async_discard(token)

    async def async_discard_all(self) -> None:
        """Discard all recordings (entry unload / Home Assistant stop)."""
        for token in list(self._records):
            await self.async_discard(token)

    async def async_sweep(self) -> None:
        """Remove expired tokens and orphaned files older than the TTL."""
        now = time.monotonic()
        expired = [
            token for token, record in self._records.items() if record.expires_at <= now
        ]
        for token in expired:
            await self.async_discard(token)
        cutoff = time.time() - RECORDING_TTL_SECONDS
        await self.hass.async_add_executor_job(self._remove_old_files, cutoff)

    async def _async_unlink(self, path: Path) -> None:
        await self.hass.async_add_executor_job(_unlink_quietly, path)

    def _remove_old_files(self, cutoff: float) -> None:
        if not self.temp_dir.is_dir():
            return
        keep = {record.path for record in self._records.values()}
        for path in self.temp_dir.iterdir():
            if path in keep or not path.is_file() or path.suffix != ".wav":
                continue
            try:
                if path.stat().st_mtime < cutoff:
                    _unlink_quietly(path)
            except OSError:  # pragma: no cover - race with a delete
                continue


def _unlink_quietly(path: Path) -> None:
    """Delete a file, tolerating races and Windows sharing violations."""
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError as err:  # pragma: no cover - Windows file in use
        _LOGGER.debug("Could not delete temporary recording yet: %s", err)


def _wipe_temp_dir(temp_dir: Path) -> None:
    if not temp_dir.is_dir():
        return
    for path in temp_dir.iterdir():
        if path.is_file() and path.suffix == ".wav":
            _unlink_quietly(path)


def _count_temp_files(temp_dir: Path) -> int:
    if not temp_dir.is_dir():
        return 0
    return sum(
        1 for path in temp_dir.iterdir() if path.is_file() and path.suffix == ".wav"
    )


async def async_wipe_temp_dir(hass: HomeAssistant) -> None:
    """Delete leftovers from a previous run (called on entry setup)."""
    await hass.async_add_executor_job(
        _wipe_temp_dir, Path(hass.config.path(TEMP_DIR_NAME))
    )


async def async_count_temp_files(hass: HomeAssistant) -> int:
    """Return the number of WAV files currently in the temp dir."""
    return await hass.async_add_executor_job(
        _count_temp_files, Path(hass.config.path(TEMP_DIR_NAME))
    )


@callback
def async_setup_sweep(hass: HomeAssistant, registry: RecordingRegistry) -> callback:
    """Run a periodic sweep of expired tokens and orphaned files."""

    async def _sweep(_now: Any) -> None:
        try:
            await registry.async_sweep()
        except Exception:  # noqa: BLE001 - a sweep must never break setup
            _LOGGER.exception("voice_broadcast recording sweep failed")

    return async_track_time_interval(
        hass,
        _sweep,
        datetime.timedelta(seconds=SWEEP_INTERVAL_SECONDS),
        cancel_on_shutdown=True,
    )


def _is_loopback(host: str) -> bool:
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def build_playback_url(hass: HomeAssistant, token: str) -> str:
    """Build the LAN URL a speaker must fetch.

    Home Assistant's internal URL is preferred; external, cloud and HTTPS
    URLs are never used because ESPHome speakers fetch over plain HTTP on the
    LAN. When the configured internal URL is HTTPS, the detected LAN IP is
    used instead. A clear error is raised when neither is usable.
    """
    base: str | None = None
    try:
        candidate = get_url(
            hass,
            allow_internal=True,
            allow_external=False,
            allow_cloud=False,
            allow_ip=True,
            require_ssl=False,
        )
    except NoURLAvailableError:
        candidate = None

    if candidate:
        parsed = urlparse(candidate)
        if (
            parsed.scheme == "http"
            and parsed.hostname
            and not _is_loopback(parsed.hostname)
        ):
            base = candidate

    if base is None:
        api = hass.config.api
        if api is not None and not api.use_ssl and api.local_ip:
            host = api.local_ip
            if ":" in host and not host.startswith("["):
                host = f"[{host}]"
            candidate = f"http://{host}:{api.port}"
            if not _is_loopback(urlparse(candidate).hostname or ""):
                base = candidate

    if base is None:
        raise RecordingError("no_internal_url", HTTPStatus.SERVICE_UNAVAILABLE)

    return f"{base.rstrip('/')}{API_PREFIX}/recording/{token}.wav"


def _parse_speakers(raw: list[str]) -> list[str] | None:
    if not raw:
        return None
    result: list[str] = []
    seen: set[str] = set()
    for item in raw:
        for part in str(item).split(","):
            speaker = part.strip()
            if speaker and speaker not in seen:
                seen.add(speaker)
                result.append(speaker)
    return result or None


def _effective_max_duration(config: dict[str, Any]) -> float:
    configured = config.get(CONF_MAX_RECORD_SECONDS, DEFAULT_MAX_RECORD_SECONDS)
    try:
        value = float(configured)
    except (TypeError, ValueError):
        value = DEFAULT_MAX_RECORD_SECONDS
    return max(1.0, min(value, float(MAX_DURATION_SECONDS)))


def _resolve_volume(entry: Any, requested: float | None) -> int:
    """Explicit value > slider (runtime data) > options default."""
    if requested is not None:
        volume = float(requested)
    else:
        runtime_volume = entry.runtime_data.volume
        volume = (
            runtime_volume
            if runtime_volume is not None
            else entry.options.get(CONF_VOLUME, DEFAULT_VOLUME)
        )
    if not 0 <= float(volume) <= 100:
        raise RecordingError("bad_volume", HTTPStatus.BAD_REQUEST)
    return int(round(float(volume)))


async def async_play_recording(
    hass: HomeAssistant,
    entry: Any,
    record: Recording,
    url: str,
    requested_speakers: list[str] | None,
    requested_volume: float | None,
) -> dict[str, Any]:
    """Play the uploaded file on the resolved speakers, once per speaker.

    The announce lock is shared with TTS announcements: a second relay or a
    TTS call while this one runs gets a clear busy error instead of queueing.
    """
    # Lazy imports avoid a circular import at module load time.
    from . import _coerce_speakers, _resolve_speakers  # noqa: PLC0415

    lock: asyncio.Lock = entry.runtime_data.lock
    if lock.locked() or entry.runtime_data.relay_playing:
        raise RecordingBusyError

    registry: RecordingRegistry = entry.runtime_data.recordings
    played: list[str] = []
    failed: list[str] = []
    skipped: list[str] = []
    errors: dict[str, str] = {}
    context = Context()

    await lock.acquire()
    try:
        try:
            resolved, skipped = await _resolve_speakers(hass, entry, requested_speakers)
        except ServiceValidationError as err:
            raise RecordingError(
                "speaker_not_configured", HTTPStatus.BAD_REQUEST
            ) from err
        if not resolved:
            raise RecordingError("no_speaker", HTTPStatus.BAD_REQUEST)

        volume_int = _resolve_volume(entry, requested_volume)
        config = {**entry.data, **entry.options}
        no_volume = set(_coerce_speakers(config.get(CONF_NO_VOLUME_SPEAKERS)))

        volume_targets = [speaker for speaker in resolved if speaker not in no_volume]
        volume_results = await asyncio.gather(
            *(
                _async_volume_call(hass, speaker, volume_int, context)
                for speaker in volume_targets
            ),
            return_exceptions=True,
        )
        for speaker, result in zip(volume_targets, volume_results, strict=False):
            if isinstance(result, BaseException):
                errors[speaker] = f"{type(result).__name__}: {result}"
                _LOGGER.warning(
                    "voice_broadcast relay volume failed for %s: %s",
                    speaker,
                    errors[speaker],
                )

        play_results = await asyncio.gather(
            *(_async_play_one(hass, speaker, url, context) for speaker in resolved),
            return_exceptions=True,
        )
        for speaker, result in zip(resolved, play_results, strict=False):
            if result is None:
                played.append(speaker)
            else:
                failed.append(speaker)
                errors[speaker] = f"{type(result).__name__}: {result}"
                _LOGGER.warning(
                    "voice_broadcast relay failed for speaker %s: %s",
                    speaker,
                    errors[speaker],
                )

        _LOGGER.info(
            "voice_broadcast relay context=%s targeted=%s played=%s "
            "skipped=%s failed=%s duration=%.2fs size=%d",
            context.id,
            resolved,
            played,
            skipped,
            failed,
            record.duration,
            record.size,
        )

        result: dict[str, Any] = {
            "ok": bool(played),
            "duration": round(record.duration, 3),
            ATTR_PLAYED: played,
            ATTR_SKIPPED: skipped,
            ATTR_FAILED: failed,
            ATTR_TARGETED: resolved,
            "context_id": context.id,
        }
    finally:
        lock.release()

    if played:
        entry.runtime_data.relay_playing = True
        entry.async_create_background_task(
            hass,
            _async_wait_and_cleanup(
                hass, entry, registry, record, list(played), record.duration
            ),
            "voice_broadcast_recording_cleanup",
        )
    else:
        entry.runtime_data.relay_playing = False
        await registry.async_discard(record.token)

    return result


async def _async_volume_call(
    hass: HomeAssistant, speaker: str, volume_int: int, context: Context
) -> None:
    await hass.services.async_call(
        "media_player",
        "volume_set",
        {"entity_id": speaker, "volume_level": volume_int / 100.0},
        blocking=True,
        context=context,
    )


async def _async_play_one(
    hass: HomeAssistant, speaker: str, url: str, context: Context
) -> None:
    await hass.services.async_call(
        "media_player",
        "play_media",
        {
            "entity_id": speaker,
            "media_content_id": url,
            "media_content_type": "music",
            # ESPHome speakers use their announcement pipeline for this and
            # therefore do not need ffmpeg to repackage a plain WAV URL.
            "announce": True,
        },
        blocking=True,
        context=context,
    )


async def _async_wait_and_cleanup(
    hass: HomeAssistant,
    entry: Any,
    registry: RecordingRegistry,
    record: Recording,
    speakers: list[str],
    duration: float,
) -> None:
    """Delete the file once every target left playing, or after the timeout."""
    started: set[str] = set()
    finished: set[str] = set()

    @callback
    def _listener(event: Any) -> None:
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        if entity_id is None or new_state is None:
            return
        if new_state.state in PLAYING_STATES:
            started.add(entity_id)
        elif entity_id in started:
            finished.add(entity_id)

    unsub = async_track_state_change_event(hass, speakers, _listener)
    deadline = time.monotonic() + duration + CLEANUP_GRACE_SECONDS
    try:
        while time.monotonic() < deadline:
            for speaker in speakers:
                state = hass.states.get(speaker)
                if state is None:
                    # Removed entity: nothing left to wait for.
                    finished.add(speaker)
                elif state.state in PLAYING_STATES:
                    started.add(speaker)
                elif speaker in started and state.state in IDLE_STATES:
                    finished.add(speaker)
            if all(speaker in finished for speaker in speakers):
                break
            await asyncio.sleep(CLEANUP_POLL_SECONDS)
    finally:
        unsub()
        if hasattr(entry, "runtime_data") and entry.runtime_data is not None:
            entry.runtime_data.relay_playing = False
        await registry.async_discard(record.token)


class RecordingUploadView(HomeAssistantView):
    """POST raw WAV bytes (or DELETE to clear); validate, store, play, and cleanup."""

    url = RECORDING_POST_PATH
    name = f"api:{DOMAIN}:recording"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def delete(self, request: web.Request) -> web.Response:
        from . import _get_entry  # noqa: PLC0415

        entry = _get_entry(self.hass)
        if entry is None:
            return _json_error("no_config_entry", HTTPStatus.SERVICE_UNAVAILABLE)
        entry.runtime_data.relay_playing = False
        await entry.runtime_data.recordings.async_discard_entry(entry.entry_id)
        return self.json({"ok": True})

    async def post(self, request: web.Request) -> web.Response:
        from . import _config, _get_entry  # noqa: PLC0415

        entry = _get_entry(self.hass)
        if entry is None:
            return _json_error("no_config_entry", HTTPStatus.SERVICE_UNAVAILABLE)

        runtime = entry.runtime_data
        if runtime.lock.locked() or runtime.relay_playing:
            return _json_error("busy", HTTPStatus.CONFLICT)

        content_length = request.content_length
        if content_length is not None and content_length > MAX_BODY_BYTES:
            return _json_error("too_large", HTTPStatus.REQUEST_ENTITY_TOO_LARGE)

        body = bytearray()
        async for chunk in request.content.iter_chunked(64 * 1024):
            body.extend(chunk)
            if len(body) > MAX_BODY_BYTES:
                return _json_error("too_large", HTTPStatus.REQUEST_ENTITY_TOO_LARGE)

        speakers = _parse_speakers(request.query.getall("speakers", []))
        raw_volume = request.query.get("volume")
        volume: float | None = None
        if raw_volume is not None:
            try:
                volume = float(raw_volume)
            except ValueError:
                return _json_error("bad_volume", HTTPStatus.BAD_REQUEST)

        config = _config(entry)
        try:
            info = parse_wav(bytes(body), max_duration=_effective_max_duration(config))
        except WavValidationError as err:
            return _json_error(err.code, HTTPStatus.BAD_REQUEST)

        try:
            url = build_playback_url(self.hass, "placeholder")
        except RecordingError as err:
            return _json_error(err.code, err.status)

        record: Recording | None = None
        try:
            record = await runtime.recordings.async_save(
                entry.entry_id, bytes(body), info
            )
            url = build_playback_url(self.hass, record.token)
            result = await async_play_recording(
                self.hass, entry, record, url, speakers, volume
            )
        except RecordingBusyError as err:
            if record is not None:
                await runtime.recordings.async_discard(record.token)
            return _json_error(err.code, err.status)
        except RecordingError as err:
            if record is not None:
                await runtime.recordings.async_discard(record.token)
            return _json_error(err.code, err.status)
        except Exception:  # noqa: BLE001 - never leak a token in the response
            if record is not None:
                await runtime.recordings.async_discard(record.token)
            _LOGGER.exception("voice_broadcast relay failed")
            return _json_error("playback_failed", HTTPStatus.INTERNAL_SERVER_ERROR)

        return self.json(result)


class RecordingConfigView(HomeAssistantView):
    """Return the limits the dashboard card must respect."""

    url = CONFIG_GET_PATH
    name = f"api:{DOMAIN}:config"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def get(self, request: web.Request) -> web.Response:
        from . import _config, _get_entry  # noqa: PLC0415

        entry = _get_entry(self.hass)
        if entry is None:
            return _json_error("no_config_entry", HTTPStatus.SERVICE_UNAVAILABLE)
        return self.json(
            {
                "ok": True,
                "version": VERSION,
                "max_record_seconds": int(_effective_max_duration(_config(entry))),
                "max_bytes": MAX_BODY_BYTES,
            }
        )


class RecordingFileView(HomeAssistantView):
    """Serve a registered WAV to speakers, without authentication."""

    url = RECORDING_GET_PATH
    name = f"api:{DOMAIN}:recording_file"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def get(self, request: web.Request, token: str = "") -> web.StreamResponse:
        from . import _get_entry  # noqa: PLC0415

        if not _TOKEN_RE.fullmatch(token):
            raise web.HTTPNotFound

        entry = _get_entry(self.hass)
        if entry is None:
            raise web.HTTPNotFound

        registry: RecordingRegistry = entry.runtime_data.recordings
        record = registry.peek(token)
        if record is None or record.expires_at <= time.monotonic():
            await registry.async_discard(token)
            raise web.HTTPNotFound

        return web.FileResponse(
            record.path,
            headers={
                "Cache-Control": "no-store",
                "Content-Type": "audio/wav",
            },
        )


def _json_error(code: str, status: HTTPStatus) -> web.Response:
    return web.json_response({"ok": False, "error": code}, status=int(status))


def version_string() -> str:
    """Expose the integration version for the card cache buster."""
    return VERSION
