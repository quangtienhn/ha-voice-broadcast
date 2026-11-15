"""OCR every image in docs/images and grep the text for sensitive patterns."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"

PATTERNS = {
    "example.com": re.compile(r"example\.com", re.I),
    "example.org": re.compile(r"example.org", re.I),
    "192.0.2.": re.compile(r"192\.0\.2\.", re.I),
    "10.x": re.compile(r"\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "172.16-31": re.compile(r"\b172\.(1[6-9]|2\d|3[01])\.\d", re.I),
    ".local": re.compile(r"\.local\b", re.I),
    "@": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "token": re.compile(r"token", re.I),
    "bearer": re.compile(r"bearer", re.I),
    "jwt eyJ": re.compile(r"eyJ[A-Za-z0-9_-]{8,}"),
    "url": re.compile(r"https?://", re.I),
    "mac": re.compile(r"\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"),
    "wifi/ssid": re.compile(r"wi-?fi|ssid", re.I),
    "setup names": re.compile(
        r"esphome_speaker|speaker_room|speaker_c|speaker_d|speaker_e|speaker_f|"
        r"speaker_g|speaker_h|Loa 3|Loa 1|Loa 6|Loa 4|Loa 5|floor 4",
        re.I,
    ),
}

engine = RapidOCR()

fails = []
for path in sorted(IMAGES.glob("*")):
    if path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        continue
    result, _ = engine(str(path))
    text = "\n".join(item[1] for item in result) if result else ""
    print(f"=== {path.name} ===")
    print(text[:600].replace("\n", " | "))
    hits = [name for name, pat in PATTERNS.items() if pat.search(text)]
    if hits:
        fails.append((path.name, hits))
        print(f"  >>> MATCHES: {hits}")
    print()

if fails:
    print("PRIVACY GATE FAILED:")
    for name, hits in fails:
        print(f"  {name}: {hits}")
    sys.exit(1)
print("OCR privacy gate passed: no sensitive pattern found.")
