"""Diagnostics for Voice Broadcast."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import VoiceBroadcastConfigEntry
from .recording import async_count_temp_files


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: VoiceBroadcastConfigEntry
) -> dict[str, Any]:
    """Return diagnostics."""
    config = {**entry.data, **entry.options}
    runtime_data = entry.runtime_data
    recordings = runtime_data.recordings if runtime_data else None
    return {
        "entry_id": entry.entry_id,
        "state": entry.state.value,
        "tts_entity": config.get("tts_entity"),
        "speakers": config.get("speakers", []),
        "no_volume_speakers": config.get("no_volume_speakers", []),
        "volume": config.get("volume"),
        "language": config.get("language"),
        "last_result": runtime_data.last_result if runtime_data else None,
        "audit_store": {
            cid: details for cid, details in list(runtime_data.audit_store.items())[-5:]
        }
        if runtime_data
        else None,
        "relay": {
            "active_recordings": recordings.active_count if recordings else 0,
            "temp_files": await async_count_temp_files(hass),
            "max_record_seconds": config.get("max_record_seconds"),
        },
    }
