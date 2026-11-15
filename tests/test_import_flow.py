"""Tests for the read-only TTS Broadcast settings import."""

from __future__ import annotations

from homeassistant import data_entry_flow
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.voice_broadcast.const import DOMAIN, LEGACY_DOMAIN

LEGACY_OPTIONS = {
    "tts_entity": "tts.wyoming_vietnamese",
    "speakers": ["media_player.loa_1", "media_player.loa_khach"],
    "no_volume_speakers": ["media_player.loa_khach"],
    "volume": 35,
    "language": "vi",
    "options": {"voice": "VaiNeural"},
    "strip_phrases": ["thông báo"],
    "keep_phrases": [],
    "require_phrase": True,
    "accent_insensitive": True,
    "reply_text": "Đã gửi",
}

USER_INPUT = {
    "tts_entity": "tts.wyoming_vietnamese",
    "speakers": ["media_player.loa_1"],
    "no_volume_speakers": [],
    "volume": 50,
    "language": "",
    "options": {},
    "strip_phrases": ["thông báo"],
    "keep_phrases": [],
    "require_phrase": True,
    "accent_insensitive": True,
    "reply_text": "",
}


def _legacy_entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=LEGACY_DOMAIN,
        data={},
        options=LEGACY_OPTIONS,
        entry_id="legacy_entry",
        title="TTS Broadcast",
    )
    entry.add_to_hass(hass)
    return entry


def _suggested(result, key: str):
    for marker in result["data_schema"].schema:
        if getattr(marker, "schema", None) == key:
            description = getattr(marker, "description", None)
            if isinstance(description, dict):
                return description.get("suggested_value")
    return None


async def test_import_step_is_offered_when_legacy_entry_exists(
    hass: HomeAssistant,
) -> None:
    _legacy_entry(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "import_old"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"import_old": True}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert _suggested(result, "speakers") == LEGACY_OPTIONS["speakers"]
    assert _suggested(result, "volume") == LEGACY_OPTIONS["volume"]


async def test_user_can_decline_the_import(hass: HomeAssistant) -> None:
    _legacy_entry(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"import_old": False}
    )
    assert result["step_id"] == "user"
    assert _suggested(result, "speakers") is None


async def test_no_import_step_without_a_legacy_entry(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert result["step_id"] == "user"


async def test_import_only_writes_the_new_entry(hass: HomeAssistant) -> None:
    hass.states.async_set("tts.wyoming_vietnamese", "idle")
    legacy = _legacy_entry(hass)
    legacy_snapshot = dict(legacy.options)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"import_old": True}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["options"]["speakers"] == USER_INPUT["speakers"]

    # The legacy entry is read-only: its options are byte-for-byte unchanged.
    assert legacy.options == legacy_snapshot
    assert hass.config_entries.async_entries(LEGACY_DOMAIN) == [legacy]


async def test_recording_options_step(hass: HomeAssistant, mock_config_entry) -> None:
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "recording"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "recording"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"max_record_seconds": 30}
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert mock_config_entry.options["max_record_seconds"] == 30
