"""Tests for options flow."""

from __future__ import annotations

import pytest
from homeassistant import data_entry_flow
from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_options_flow_opens(hass: HomeAssistant, mock_config_entry) -> None:
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] == data_entry_flow.FlowResultType.MENU

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "voice"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM


@pytest.mark.asyncio
async def test_options_flow_speakers_audit_all_media_players(
    hass: HomeAssistant, mock_config_entry
) -> None:
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "speakers"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM

    hass.states.async_set("tts.mock", "online")
    hass.states.async_set("media_player.one", "idle")

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "tts_entity": "tts.mock",
            "speakers": ["media_player.one"],
            "no_volume_speakers": [],
            "volume": 60,
            "audit_all_media_players": True,
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert mock_config_entry.options["audit_all_media_players"] is True
