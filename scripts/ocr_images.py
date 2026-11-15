"""OCR every image in docs/images and fail if any sensitive pattern reappears.

The sensitive-word list lives in ``scripts/private_words.local.txt`` (gitignored) or in
the file pointed to by the ``VB_PRIVATE_WORDS`` environment variable. Format: one
``name = regex`` entry per line; ``#`` starts a comment.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
DENYLIST = Path(
    os.environ.get("VB_PRIVATE_WORDS") or ROOT / "scripts" / "private_words.local.txt"
)


def _load_patterns() -> dict[str, re.Pattern]:
    if not DENYLIST.is_file():
        raise SystemExit(f"deny list not found: {DENYLIST} (set VB_PRIVATE_WORDS)")
    patterns: dict[str, re.Pattern] = {}
    for raw in DENYLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, sep, regex = line.partition("=")
        if not sep:
            raise SystemExit(f"invalid deny list line: {line!r}")
        patterns[name.strip()] = re.compile(regex.strip(), re.I)
    return patterns


def main() -> int:
    patterns = _load_patterns()
    engine = RapidOCR()
    fails = []
    for path in sorted(IMAGES.glob("*")):
        if path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        result, _ = engine(str(path))
        text = "\n".join(item[1] for item in result) if result else ""
        print(f"=== {path.name} ===")
        print(text[:600].replace("\n", " | "))
        hits = [name for name, pat in patterns.items() if pat.search(text)]
        if hits:
            fails.append((path.name, hits))
            print(f"  >>> MATCHES: {hits}")
        print()

    if fails:
        print("PRIVACY GATE FAILED:")
        for name, hits in fails:
            print(f"  {name}: {hits}")
        return 1
    print("OCR privacy gate passed: no sensitive pattern found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
