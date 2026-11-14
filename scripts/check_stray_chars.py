# Scan tracked files for stray characters (non-ASCII, non-Vietnamese)
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Allowed character classes:
# - Standard ASCII (0 - 127)
# - Latin Extended / Vietnamese vowels with diacritics
# - Standard punctuation (smart quotes, em dash, bullets, etc.)

exts = {".py", ".json", ".js", ".mjs", ".md", ".yml", ".yaml", ".toml", ".txt"}
errors = []

for p in ROOT.rglob("*"):
    if not p.is_file() or p.suffix not in exts:
        continue
    if any(
        part in p.parts
        for part in (
            ".git",
            ".venv",
            ".ha-core",
            "dist",
            ".pytest_cache",
            ".ruff_cache",
            "node_modules",
        )
    ):
        continue

    try:
        text = p.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"{p.relative_to(ROOT)}: Encoding error: {e}")
        continue

    for line_idx, line in enumerate(text.splitlines(), start=1):
        for char in line:
            # Check for non-Latin / non-Vietnamese scripts
            name = unicodedata.name(char, "")
            # Disallow CJK, Hangul, Cyrillic, Arabic, Hebrew, Thai, etc.
            forbidden_scripts = (
                "CJK",
                "HANGUL",
                "CYRILLIC",
                "ARABIC",
                "HEBREW",
                "THAI",
                "HIRAGANA",
                "KATAKANA",
            )
            if any(s in name for s in forbidden_scripts):
                errors.append(
                    f"{p.relative_to(ROOT)}:{line_idx}: Stray script character"
                    f" '{char}' ({name})"
                )
                break

if errors:
    print(f"Found {len(errors)} stray characters:")
    for err in errors[:20]:
        print("  -", err)
    sys.exit(1)
else:
    print("Stray character scan passed clean!")
