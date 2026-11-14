# Check that all internal Markdown links point to existing files
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
md_files = list(ROOT.rglob("*.md"))

link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
errors = []

for md in md_files:
    if ".git" in md.parts or ".venv" in md.parts or ".ha-core" in md.parts:
        continue
    content = md.read_text(encoding="utf-8")
    for match in link_pattern.finditer(content):
        target = match.group(2).split("#")[0].strip()
        if (
            not target
            or target.startswith("http://")
            or target.startswith("https://")
            or target.startswith("mailto:")
        ):
            continue
        # Relative file check
        resolved = (md.parent / target).resolve()
        if not resolved.exists():
            errors.append(
                f"{md.relative_to(ROOT)}: Link to '{target}' does not exist"
                f" (resolved: {resolved})"
            )

if errors:
    print("Broken links found:")
    for err in errors:
        print("  -", err)
    sys.exit(1)
else:
    print("All internal Markdown links are valid!")
