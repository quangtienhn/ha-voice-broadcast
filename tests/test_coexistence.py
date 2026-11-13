"""The old TTS Broadcast integration and Voice Broadcast must coexist.

The old package is not shipped here, so the test registers the same public
surface it uses: a domain, services, a static asset, HTTP views, entity
registry entries and a Repairs issue. Both sides are then exercised together.
"""

from __future__ import annotations

from pathlib import Path

from aiohttp import web
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.voice_broadcast.const import DOMAIN, LEGACY_DOMAIN

LEGACY_ASSET = "/tts_broadcast/legacy-card.js"


class LegacyView(HomeAssistantView):
    """A stand-in for the old integration's HTTP endpoint."""

    url = "/api/tts_broadcast/legacy"
    name = "api:tts_broadcast:legacy"
    requires_auth = False

    async def get(self, request: web.Request) -> web.Response:
        return web.json_response({"ok": True, "from": LEGACY_DOMAIN})


async def test_both_integrations_run_side_by_side(
    hass: HomeAssistant, mock_config_entry, hass_client, tmp_path: Path
) -> None:
    await async_setup_component(hass, "http", {})
    asset = tmp_path / "legacy-card.js"
    asset.write_text("// legacy card", encoding="utf-8")

    legacy_entry = MockConfigEntry(
        domain=LEGACY_DOMAIN,
        data={},
        options={
            "tts_entity": "tts.wyoming_vietnamese",
            "speakers": ["media_player.loa_cu"],
            "volume": 40,
        },
        entry_id="legacy_entry",
        title="TTS Broadcast",
    )
    legacy_entry.add_to_hass(hass)

    legacy_calls: list = []

    async def legacy_speak(call) -> None:
        legacy_calls.append(dict(call.data))

    hass.services.async_register(LEGACY_DOMAIN, "speak", legacy_speak)

    await hass.http.async_register_static_paths(
        [StaticPathConfig(LEGACY_ASSET, str(asset), cache_headers=False)]
    )
    hass.http.register_view(LegacyView())

    ir.async_create_issue(
        hass,
        LEGACY_DOMAIN,
        "legacy_issue",
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key="legacy_issue",
    )

    registry = er.async_get(hass)
    legacy_entity = registry.async_get_or_create(
        "switch", LEGACY_DOMAIN, f"{legacy_entry.entry_id}_switch_loa_cu"
    )

    hass.states.async_set("media_player.loa_cu", "idle")
    hass.states.async_set("media_player.speaker_one", "idle")
    hass.states.async_set("media_player.speaker_two", "idle")

    tts_calls: list = []

    async def tts_speak(call) -> None:
        tts_calls.append(dict(call.data))

    hass.services.async_register("tts", "speak", tts_speak)

    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Both service domains exist and both handlers receive their own calls.
    assert hass.services.has_service(LEGACY_DOMAIN, "speak")
    assert hass.services.has_service(DOMAIN, "speak")

    await hass.services.async_call(
        LEGACY_DOMAIN, "speak", {"message": "legacy"}, blocking=True
    )
    assert legacy_calls[0]["message"] == "legacy"

    await hass.services.async_call(
        DOMAIN,
        "speak",
        {"message": "new", "speakers": ["media_player.speaker_one"]},
        blocking=True,
    )
    assert tts_calls[-1]["message"] == "new"
    assert tts_calls[-1]["media_player_entity_id"] == ["media_player.speaker_one"]

    # Entity registry entries from both platforms survive untouched.
    assert registry.async_get(legacy_entity.entity_id) is not None

    # Repairs issues are namespaced per domain.
    issues = ir.async_get(hass)
    assert issues.async_get_issue(LEGACY_DOMAIN, "legacy_issue") is not None
    assert issues.async_get_issue(DOMAIN, "legacy_issue") is None

    client = await hass_client()
    legacy_response = await client.get("/api/tts_broadcast/legacy")
    assert legacy_response.status == 200
    assert (await legacy_response.json())["from"] == LEGACY_DOMAIN

    our_response = await client.get("/api/voice_broadcast/config")
    assert our_response.status == 200
    assert (await our_response.json())["ok"] is True

    # Unloading the new integration must not touch the old service or entry.
    await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert hass.services.has_service(LEGACY_DOMAIN, "speak")
    assert hass.config_entries.async_entries(LEGACY_DOMAIN) == [legacy_entry]
