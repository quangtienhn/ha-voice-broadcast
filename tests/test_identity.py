"""Guard the rename: names, version and asset paths must stay consistent."""

from __future__ import annotations

import json
from pathlib import Path

from custom_components.voice_broadcast.const import (
    API_PREFIX,
    CARD_URL_PATH,
    DOMAIN,
    RECORDING_GET_PATH,
    RECORDING_POST_PATH,
    VERSION,
)

ROOT = Path(__file__).resolve().parents[1]
INTEGRATION = ROOT / "custom_components" / "voice_broadcast"


def test_manifest_identity() -> None:
    manifest = json.loads((INTEGRATION / "manifest.json").read_text("utf-8"))
    assert manifest["domain"] == "voice_broadcast"
    assert manifest["name"] == "Voice Broadcast"
    assert manifest["version"] == "0.2.1"
    assert manifest["config_flow"] is True
    assert manifest["single_config_entry"] is True
    assert manifest["documentation"].endswith("/ha-voice-broadcast")


def test_version_is_read_from_the_manifest() -> None:
    manifest = json.loads((INTEGRATION / "manifest.json").read_text("utf-8"))
    assert manifest["version"] == VERSION

    card = (INTEGRATION / "www" / "voice-broadcast-card.js").read_text("utf-8")
    assert f'const VERSION = "{manifest["version"]}";' in card


def test_paths_and_domains() -> None:
    assert DOMAIN == "voice_broadcast"
    assert CARD_URL_PATH == "/voice_broadcast/voice-broadcast-card.js"
    assert API_PREFIX == "/api/voice_broadcast"
    assert RECORDING_POST_PATH == "/api/voice_broadcast/recording"
    assert RECORDING_GET_PATH == "/api/voice_broadcast/recording/{token}.wav"


def test_hacs_minimum_version() -> None:
    hacs = json.loads((ROOT / "hacs.json").read_text("utf-8"))
    assert hacs["name"] == "Voice Broadcast"
    assert hacs["homeassistant"] == "2026.11.0"


def test_no_legacy_domain_leaks_into_python_code() -> None:
    """The old domain name may only appear in the explicit migration hooks."""
    allowed = {
        INTEGRATION / "const.py",  # LEGACY_DOMAIN / LEGACY_CARD_TYPE
    }
    offenders = []
    for path in INTEGRATION.rglob("*.py"):
        if path in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        if "tts_broadcast" in text or "tts-broadcast" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
