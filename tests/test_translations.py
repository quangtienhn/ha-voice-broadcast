"""Tests for translation key parity."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "voice_broadcast"
TRANS = COMPONENT / "translations"


def _keys(obj, prefix=""):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            out |= _keys(v, f"{prefix}.{k}" if prefix else k)
    return out


def test_translation_key_parity() -> None:
    en = json.loads((TRANS / "en.json").read_text(encoding="utf-8"))
    vi = json.loads((TRANS / "vi.json").read_text(encoding="utf-8"))
    strings = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))

    en_keys = _keys(en)
    vi_keys = _keys(vi)
    strings_keys = _keys(strings)

    assert en_keys == vi_keys, en_keys.symmetric_difference(vi_keys)
    assert en_keys == strings_keys, en_keys.symmetric_difference(strings_keys)
