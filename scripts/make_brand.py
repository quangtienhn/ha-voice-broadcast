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
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (255, 255, 255, 255) if dark else (31, 111, 235, 255)
    stroke = 10

    # Microphone capsule.
    d.rounded_rectangle((94, 44, 158, 146), radius=32, fill=color)
    # Cradle (open U below the capsule).
    d.arc((72, 92, 180, 176), start=0, end=180, fill=color, width=stroke)
    # Stem and base.
    d.rounded_rectangle((121, 168, 131, 206), radius=5, fill=color)
    d.rounded_rectangle((98, 206, 154, 216), radius=5, fill=color)
    # Broadcast waves, just right of the capsule.
    d.arc((158, 66, 214, 130), start=-55, end=55, fill=color, width=stroke)
    d.arc((174, 46, 246, 150), start=-55, end=55, fill=color, width=stroke)

    # Trim to the artwork and center it with a fixed margin.
    bbox = img.getbbox()
    if bbox is None:  # pragma: no cover - drawing always produces artwork
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    art = img.crop(bbox)
    side = max(art.width, art.height)
    margin = int(side * 0.12)
    canvas = Image.new("RGBA", (side + 2 * margin, side + 2 * margin), (0, 0, 0, 0))
    canvas.paste(
        art, ((canvas.width - art.width) // 2, (canvas.height - art.height) // 2)
    )
    return canvas.resize((size, size), Image.LANCZOS)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, size in SIZES.items():
        dark = name.startswith("dark_")
        draw(size, dark).save(OUT / name)
        print(f"wrote {OUT / name}")


if __name__ == "__main__":
    main()
