"""Generate brand PNGs for the Voice Broadcast integration.

The mark is a microphone with broadcast waves: recording (the voice relay) plus
broadcasting (the TTS path). It deliberately differs from the old speaker icon.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "custom_components" / "voice_broadcast" / "brand"
SIZES = {
    "icon.png": 256,
    "icon@2x.png": 512,
    "dark_icon.png": 256,
    "dark_icon@2x.png": 512,
}


def draw(size: int, dark: bool) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (255, 255, 255, 255) if dark else (31, 111, 235, 255)
    s = size / 256
    stroke = max(1, int(round(10 * s)))

    # Microphone capsule.
    d.rounded_rectangle(
        (94 * s, 44 * s, 158 * s, 146 * s),
        radius=32 * s,
        fill=color,
    )
    # Cradle (open U below the capsule).
    d.arc(
        (72 * s, 92 * s, 180 * s, 176 * s),
        start=0,
        end=180,
        fill=color,
        width=stroke,
    )
    # Stem and base.
    d.rounded_rectangle(
        (121 * s, 168 * s, 131 * s, 206 * s),
        radius=5 * s,
        fill=color,
    )
    d.rounded_rectangle(
        (98 * s, 206 * s, 154 * s, 216 * s),
        radius=5 * s,
        fill=color,
    )
    # Broadcast waves, just right of the capsule.
    d.arc(
        (158 * s, 66 * s, 214 * s, 130 * s),
        start=-55,
        end=55,
        fill=color,
        width=stroke,
    )
    d.arc(
        (174 * s, 46 * s, 246 * s, 150 * s),
        start=-55,
        end=55,
        fill=color,
        width=stroke,
    )
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, size in SIZES.items():
        dark = name.startswith("dark_")
        draw(size, dark).save(OUT / name)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
