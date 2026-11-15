"""Redact personal device names from the screenshots added by the owner.

The owner approved covering the real speaker/entity names. Each OCR text box
that matches a sensitive pattern is painted over with the surrounding background
colour, then the image is re-saved without metadata.

The sensitive patterns live in ``scripts/private_words.local.txt`` (gitignored) or
in the file pointed to by the ``VB_PRIVATE_WORDS`` environment variable. Format:
one ``name = regex`` entry per line; ``#`` starts a comment. Set ``VB_RAW_DIR`` to
the directory holding the original files; by default the files are read from
``docs/images``.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
SOURCE = Path(os.environ.get("VB_RAW_DIR", IMAGES))
DENYLIST = Path(
    os.environ.get("VB_PRIVATE_WORDS") or ROOT / "scripts" / "private_words.local.txt"
)

# Source file prefix (the timestamp) -> final public name.
MAPPING = {
    "1794748062524": "device-info.jpg",
    "1794748062822": "card-speakers.jpg",
    "1794748062992": "card-collapsed.jpg",
    "1794748063184": "card-full.jpg",
    "1794748155666": "config-voice-phrases.jpg",
}


def _load_sensitive() -> re.Pattern:
    if not DENYLIST.is_file():
        raise SystemExit(f"deny list not found: {DENYLIST} (set VB_PRIVATE_WORDS)")
    alternatives = []
    for raw in DENYLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        _name, sep, regex = line.partition("=")
        if not sep:
            raise SystemExit(f"invalid deny list line: {line!r}")
        alternatives.append(regex.strip())
    if not alternatives:
        raise SystemExit(f"deny list is empty: {DENYLIST}")
    return re.compile("|".join(f"(?:{item})" for item in alternatives), re.I)


SENSITIVE = _load_sensitive()

engine = RapidOCR()


def _box_bounds(box) -> tuple[int, int, int, int]:
    xs = [point[0] for point in box]
    ys = [point[1] for point in box]
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))


def _strip_colour(img: Image.Image, box: tuple[int, int, int, int]):
    """Return the dominant background colour of a strip."""
    if box[2] <= box[0] or box[3] <= box[1]:
        return None
    raw = img.crop(box).convert("RGB").tobytes()
    counts: dict[tuple[int, int, int], int] = {}
    for offset in range(0, len(raw), 3):
        pixel = (raw[offset], raw[offset + 1], raw[offset + 2])
        counts[pixel] = counts.get(pixel, 0) + 1
    return max(counts.items(), key=lambda item: item[1])[0]


def _row_background(
    img: Image.Image, bounds: tuple[int, int, int, int]
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    """Sample background colours left and right of the text row."""
    x1, y1, x2, y2 = bounds
    left = None
    right = None
    if x1 - 24 >= 0:
        left = _strip_colour(img, (x1 - 24, y1, x1 - 6, y2))
    if x2 + 24 <= img.width:
        right = _strip_colour(img, (x2 + 6, y1, x2 + 24, y2))
    if left is None and right is None:
        left = right = _strip_colour(img, (x1, max(0, y1 - 20), x2, max(1, y1 - 6)))
    if left is None:
        left = right or (255, 255, 255)
    if right is None:
        right = left
    return left, right


def _paint_gradient(
    img: Image.Image,
    bounds: tuple[int, int, int, int],
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> None:
    """Fill the box with a horizontal gradient matching the row background."""
    x1, y1, x2, y2 = bounds
    width = max(1, x2 - x1)
    height = max(1, y2 - y1)
    gradient = Image.new("RGB", (width, 1))
    for index in range(width):
        ratio = index / (width - 1) if width > 1 else 0.0
        gradient.putpixel(
            (
                index,
                0,
            ),
            tuple(
                int(left[channel] * (1 - ratio) + right[channel] * ratio)
                for channel in range(3)
            ),
        )
    img.paste(gradient.resize((width, height)), (x1, y1))


def redact(src: Path, dst: Path) -> int:
    result, _ = engine(str(src))
    img = Image.open(src).convert("RGB")
    count = 0
    if result:
        for box, text, _score in result:
            if not SENSITIVE.search(text):
                continue
            x1, y1, x2, y2 = _box_bounds(box)
            x1 = max(0, x1 - 8)
            y1 = max(0, y1 - 4)
            x2 = min(img.width, x2 + 12)
            y2 = min(img.height, y2 + 4)
            left, right = _row_background(img, (x1, y1, x2, y2))
            _paint_gradient(img, (x1, y1, x2, y2), left, right)
            count += 1
    img.save(dst, "JPEG", quality=88, optimize=True, progressive=True)
    return count


def main() -> None:
    for src in sorted(SOURCE.glob("*.jpg")):
        dst_name = MAPPING.get(src.name.split("_")[0])
        if dst_name is None:
            print(f"skip unknown screenshot: {src.name}")
            continue
        dst = IMAGES / dst_name
        count = redact(src, dst)
        print(f"{src.name} -> {dst_name}: redacted {count} text boxes")
    print("done")


if __name__ == "__main__":
    main()
