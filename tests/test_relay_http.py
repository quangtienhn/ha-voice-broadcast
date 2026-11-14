"""HTTP tests for the authenticated upload and the token download."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant

from custom_components.voice_broadcast import recording as rec
from custom_components.voice_broadcast.const import DOMAIN
from custom_components.voice_broadcast.wav import parse_wav
from tests.wav_utils import make_wav

POST_URL = "/api/voice_broadcast/recording"
CONFIG_URL = "/api/voice_broadcast/config"


@dataclass
class RelayHarness:
    client: object
    anon: object
    calls: list = field(default_factory=list)
    play_handler: object = None


@pytest.fixture
async def relay(
    hass: HomeAssistant,
    mock_config_entry,
    hass_client,
    hass_client_no_auth,
    monkeypatch,
) -> AsyncIterator[RelayHarness]:
    # Deterministic LAN URL: the upload endpoint refuses loopback URLs.
    monkeypatch.setattr(
        rec, "get_url", lambda *args, **kwargs: "http://192.0.2.5:8123"
    )
    monkeypatch.setattr(rec, "CLEANUP_GRACE_SECONDS", 0.05)
    monkeypatch.setattr(rec, "CLEANUP_POLL_SECONDS", 0.01)

    hass.states.async_set("media_player.speaker_one", "idle")
    hass.states.async_set("media_player.speaker_two", "idle")

    calls: list[tuple[str, dict]] = []

    async def play_media(call) -> None:
        calls.append(("play_media", dict(call.data)))

    async def volume_set(call) -> None:
        calls.append(("volume_set", dict(call.data)))

    hass.services.async_register("media_player", "play_media", play_media)
    hass.services.async_register("media_player", "volume_set", volume_set)
    hass.services.async_register("media_player", "media_stop", play_media)

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    client = await hass_client()
    anon = await hass_client_no_auth()
    yield RelayHarness(client=client, anon=anon, calls=calls)


async def test_upload_requires_auth(relay: RelayHarness) -> None:
    response = await relay.anon.post(POST_URL, data=make_wav(duration=0.2))
    assert response.status == 401
    assert relay.calls == []


async def test_config_requires_auth_and_reports_limits(relay: RelayHarness) -> None:
    assert (await relay.anon.get(CONFIG_URL)).status == 401
    response = await relay.client.get(CONFIG_URL)
    assert response.status == 200
    data = await response.json()
    assert data["max_record_seconds"] == 60
    assert data["max_bytes"] == 3 * 1024 * 1024


async def test_invalid_wav_is_rejected_before_saving(relay: RelayHarness, hass) -> None:
    response = await relay.client.post(POST_URL, data=b"not a wav at all")
    assert response.status == 400
    assert (await response.json())["error"] == "not_riff"

    registry = hass.config_entries.async_entries(DOMAIN)[0].runtime_data.recordings
    assert registry.active_count == 0


async def test_too_long_recording_is_rejected(relay: RelayHarness) -> None:
    response = await relay.client.post(
        POST_URL, data=make_wav(duration=61, sample_rate=8000)
    )
    assert response.status == 400
    assert (await response.json())["error"] == "too_long"


async def test_payload_over_three_megabytes_is_rejected(relay: RelayHarness) -> None:
    response = await relay.client.post(POST_URL, data=b"\0" * (3 * 1024 * 1024 + 1))
    assert response.status == 413
    assert (await response.json())["error"] == "too_large"


async def test_upload_plays_and_token_downloads_without_auth(
    relay: RelayHarness, hass
) -> None:
    wav = make_wav(duration=0.2)
    response = await relay.client.post(
        POST_URL,
        data=wav,
        params={
            "speakers": ["media_player.speaker_one", "media_player.speaker_two"],
            "volume": 70,
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data["ok"] is True
    assert data["played"] == ["media_player.speaker_one", "media_player.speaker_two"]
    assert data["targeted"] == ["media_player.speaker_one", "media_player.speaker_two"]
    assert 0.19 < data["duration"] < 0.21

    plays = [data for kind, data in relay.calls if kind == "play_media"]
    assert len(plays) == 2
    url = plays[0]["media_content_id"]
    assert url.startswith("http://192.0.2.5:8123/api/voice_broadcast/recording/")
    assert url.endswith(".wav")
    assert plays[0]["media_content_type"] == "music"
    assert plays[0]["announce"] is True

    # speaker_two is configured without volume control.
    volumes = [data for kind, data in relay.calls if kind == "volume_set"]
    assert [call["entity_id"] for call in volumes] == ["media_player.speaker_one"]
    assert volumes[0]["volume_level"] == pytest.approx(0.7)

    anon_response = await relay.anon.get(url.removeprefix("http://192.0.2.5:8123"))
    assert anon_response.status == 200
    assert anon_response.headers["Content-Type"] == "audio/wav"
    assert anon_response.headers["Cache-Control"] == "no-store"
    assert await anon_response.read() == wav

    # A speaker may fetch the same token twice.
    path = url.removeprefix("http://192.0.2.5:8123")
    assert (await relay.anon.get(path)).status == 200

    # The cleanup watcher runs as a background task; let it observe idle + grace.
    await asyncio.sleep(0.35)
    await hass.async_block_till_done()
    registry = hass.config_entries.async_entries(DOMAIN)[0].runtime_data.recordings
    assert registry.active_count == 0


async def test_unknown_and_traversal_tokens_are_404(relay: RelayHarness) -> None:
    for path in (
        "/api/voice_broadcast/recording/" + "a" * 43 + ".wav",
        "/api/voice_broadcast/recording/not-a-token.wav",
        "/api/voice_broadcast/recording/..%2f..%2fconfiguration.yaml.wav",
    ):
        response = await relay.anon.get(path)
        # HA's security filter rejects encoded traversal with 400 before routing.
        assert response.status in (400, 404), path


async def test_per_speaker_failure_is_reported(relay: RelayHarness, hass) -> None:
    async def play_media(call) -> None:
        if call.data["entity_id"] == "media_player.speaker_two":
            raise RuntimeError("speaker offline")

    hass.services.async_register("media_player", "play_media", play_media)

    response = await relay.client.post(
        POST_URL,
        data=make_wav(duration=0.2),
        params={
            "speakers": ["media_player.speaker_one", "media_player.speaker_two"],
        },
    )
    assert response.status == 200
    data = await response.json()
    assert data["ok"] is True
    assert data["played"] == ["media_player.speaker_one"]
    assert data["failed"] == ["media_player.speaker_two"]
    await hass.async_block_till_done()


async def test_all_speakers_failing_discards_the_file(
    relay: RelayHarness, hass
) -> None:
    async def play_media(call) -> None:
        raise RuntimeError("offline")

    hass.services.async_register("media_player", "play_media", play_media)
    response = await relay.client.post(
        POST_URL,
        data=make_wav(duration=0.2),
        params={"speakers": ["media_player.speaker_one"]},
    )
    assert response.status == 200
    data = await response.json()
    assert data["ok"] is False
    assert data["failed"] == ["media_player.speaker_one"]

    registry = hass.config_entries.async_entries(DOMAIN)[0].runtime_data.recordings
    assert registry.active_count == 0


async def test_busy_while_another_upload_is_playing(relay: RelayHarness, hass) -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_play(call) -> None:
        started.set()
        await release.wait()

    hass.services.async_register("media_player", "play_media", slow_play)

    first = asyncio.create_task(
        relay.client.post(
            POST_URL,
            data=make_wav(duration=0.2),
            params={"speakers": ["media_player.speaker_one"]},
        )
    )
    await asyncio.wait_for(started.wait(), timeout=2)

    second = await relay.client.post(
        POST_URL,
        data=make_wav(duration=0.2),
        params={"speakers": ["media_player.speaker_one"]},
    )
    assert second.status == 409
    assert (await second.json())["error"] == "busy"

    release.set()
    assert (await asyncio.wait_for(first, timeout=2)).status == 200
    await hass.async_block_till_done()


async def test_delete_discards_the_recording(relay: RelayHarness, hass) -> None:
    response = await relay.client.post(
        POST_URL,
        data=make_wav(duration=0.2),
        params={"speakers": ["media_player.speaker_one"]},
    )
    assert response.status == 200
    registry = hass.config_entries.async_entries(DOMAIN)[0].runtime_data.recordings
    assert registry.active_count == 1

    entry = hass.config_entries.async_entries(DOMAIN)[0]
    deleted = await relay.client.delete(POST_URL)
    assert deleted.status == 200
    assert (await deleted.json())["ok"] is True
    assert registry.active_count == 0
    assert entry.runtime_data.relay_playing is False
    await hass.async_block_till_done()


async def test_stop_service_discards_the_recording(relay: RelayHarness, hass) -> None:
    await relay.client.post(
        POST_URL,
        data=make_wav(duration=0.2),
        params={"speakers": ["media_player.speaker_one"]},
    )
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    assert entry.runtime_data.recordings.active_count == 1

    await hass.services.async_call(DOMAIN, "stop", {}, blocking=True)
    assert entry.runtime_data.recordings.active_count == 0
    assert entry.runtime_data.relay_playing is False
    await hass.async_block_till_done()


async def test_shutdown_discards_recordings(relay: RelayHarness, hass) -> None:
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    registry = entry.runtime_data.recordings
    body = make_wav(duration=0.2)
    record = await registry.async_save(entry.entry_id, body, parse_wav(body))
    assert record.path.exists()
    assert registry.active_count == 1

    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()

    assert registry.active_count == 0
    assert not record.path.exists()


async def test_relay_playing_blocks_tts_and_stop_clears(
    relay: RelayHarness, hass: HomeAssistant
) -> None:
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    entry.runtime_data.relay_playing = True

    # Attempting TTS speak while relay is playing raises ServiceValidationError (busy)
    with pytest.raises(Exception) as exc_info:
        await hass.services.async_call(
            DOMAIN, "speak", {"message": "hello"}, blocking=True
        )
    assert "busy" in str(exc_info.value)

    # Calling stop clears relay_playing and stops speakers
    await hass.services.async_call(DOMAIN, "stop", {}, blocking=True)
    assert entry.runtime_data.relay_playing is False


async def test_no_internal_url_is_a_clear_error(
    relay: RelayHarness, hass, monkeypatch
) -> None:
    from homeassistant.helpers.network import NoURLAvailableError

    def _no_url(*args, **kwargs):
        raise NoURLAvailableError

    monkeypatch.setattr(rec, "get_url", _no_url)
    monkeypatch.setattr(hass.config, "api", None)

    response = await relay.client.post(
        POST_URL,
        data=make_wav(duration=0.2),
        params={"speakers": ["media_player.speaker_one"]},
    )
    assert response.status == 503
    assert (await response.json())["error"] == "no_internal_url"
    assert relay.calls == []
