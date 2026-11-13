"""Unit tests for the recording registry, URL builder and cleanup watcher."""

from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from homeassistant.helpers.network import NoURLAvailableError

from custom_components.voice_broadcast import recording as rec
from custom_components.voice_broadcast.const import TEMP_DIR_NAME
from tests.wav_utils import make_wav


def _info(duration: float = 0.5):
    from custom_components.voice_broadcast.wav import parse_wav

    return parse_wav(make_wav(duration=duration))


async def test_registry_save_and_discard(hass) -> None:
    registry = rec.RecordingRegistry(hass)
    body = make_wav(duration=0.5)
    record = await registry.async_save("entry", body, _info(0.5))

    assert registry.active_count == 1
    assert record.path.exists()
    assert record.path.parent == Path(hass.config.path(TEMP_DIR_NAME))
    assert record.token in record.path.name
    assert record.size == len(body)

    await registry.async_discard(record.token)
    assert registry.active_count == 0
    assert not record.path.exists()
    # Idempotent.
    await registry.async_discard(record.token)


async def test_registry_discard_entry_and_all(hass) -> None:
    registry = rec.RecordingRegistry(hass)
    first = await registry.async_save("a", make_wav(), _info())
    second = await registry.async_save("b", make_wav(), _info())
    await registry.async_discard_entry("a")
    assert registry.active_count == 1
    assert not first.path.exists()
    assert second.path.exists()
    await registry.async_discard_all()
    assert registry.active_count == 0
    assert not second.path.exists()


async def test_registry_sweep_removes_expired_and_orphans(hass) -> None:
    registry = rec.RecordingRegistry(hass)
    record = await registry.async_save("entry", make_wav(), _info())
    record.expires_at = 0.0

    registry.temp_dir.mkdir(parents=True, exist_ok=True)
    orphan = registry.temp_dir / "orphan.wav"
    orphan.write_bytes(b"old")
    import os
    import time

    old = time.time() - 3600
    os.utime(orphan, (old, old))

    await registry.async_sweep()

    assert registry.active_count == 0
    assert not record.path.exists()
    assert not orphan.exists()


async def test_wipe_temp_dir_removes_previous_run_files(hass) -> None:
    temp_dir = Path(hass.config.path(TEMP_DIR_NAME))
    temp_dir.mkdir(parents=True, exist_ok=True)
    stale = temp_dir / "stale.wav"
    stale.write_bytes(b"stale")

    await rec.async_wipe_temp_dir(hass)

    assert not stale.exists()


def test_build_playback_url_uses_internal_http(hass) -> None:
    with patch.object(
        rec, "get_url", return_value="http://192.0.2.5:8123"
    ) as get_url:
        url = rec.build_playback_url(hass, "token")

    assert url == "http://192.0.2.5:8123/api/voice_broadcast/recording/token.wav"
    get_url.assert_called_once()


def test_build_playback_url_falls_back_when_internal_url_is_https(hass) -> None:
    hass.config.api = SimpleNamespace(use_ssl=False, local_ip="192.0.2.10", port=8123)
    with patch.object(rec, "get_url", return_value="https://home.example.com"):
        url = rec.build_playback_url(hass, "tok")

    assert url == "http://192.0.2.10:8123/api/voice_broadcast/recording/tok.wav"


def test_build_playback_url_rejects_loopback(hass) -> None:
    hass.config.api = None
    with (
        patch.object(rec, "get_url", return_value="http://127.0.0.1:8123"),
        pytest.raises(rec.RecordingError) as err,
    ):
        rec.build_playback_url(hass, "tok")

    assert err.value.code == "no_internal_url"


def test_build_playback_url_wraps_ipv6(hass) -> None:
    hass.config.api = SimpleNamespace(use_ssl=False, local_ip="::1", port=8123)
    with (
        patch.object(rec, "get_url", side_effect=NoURLAvailableError),
        pytest.raises(rec.RecordingError),
    ):
        # ::1 is loopback and must be rejected.
        rec.build_playback_url(hass, "tok")

    hass.config.api = SimpleNamespace(use_ssl=False, local_ip="fd00::5", port=8123)
    with patch.object(rec, "get_url", side_effect=NoURLAvailableError):
        url = rec.build_playback_url(hass, "tok")

    assert url == "http://[fd00::5]:8123/api/voice_broadcast/recording/tok.wav"


async def test_cleanup_waits_for_idle_then_deletes(hass, monkeypatch) -> None:
    monkeypatch.setattr(rec, "CLEANUP_GRACE_SECONDS", 1.0)
    monkeypatch.setattr(rec, "CLEANUP_POLL_SECONDS", 0.01)
    registry = rec.RecordingRegistry(hass)
    record = await registry.async_save("entry", make_wav(), _info(0.1))
    speaker = "media_player.speaker_one"
    hass.states.async_set(speaker, "playing")

    task = asyncio.create_task(
        rec._async_wait_and_cleanup(hass, registry, record, [speaker], 0.1)
    )
    await asyncio.sleep(0.05)
    hass.states.async_set(speaker, "idle")
    await asyncio.wait_for(task, timeout=2)

    assert registry.active_count == 0
    assert not record.path.exists()


async def test_cleanup_times_out_and_deletes(hass, monkeypatch) -> None:
    monkeypatch.setattr(rec, "CLEANUP_GRACE_SECONDS", 0.05)
    monkeypatch.setattr(rec, "CLEANUP_POLL_SECONDS", 0.01)
    registry = rec.RecordingRegistry(hass)
    record = await registry.async_save("entry", make_wav(), _info(0.05))
    speaker = "media_player.speaker_one"
    hass.states.async_set(speaker, "playing")

    await asyncio.wait_for(
        rec._async_wait_and_cleanup(hass, registry, record, [speaker], 0.05),
        timeout=2,
    )

    assert registry.active_count == 0
    assert not record.path.exists()
