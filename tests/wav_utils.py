"""Build WAV files for the relay tests."""

from __future__ import annotations

import math
import struct


def make_wav(
    duration: float = 1.0,
    sample_rate: int = 16000,
    channels: int = 1,
    bits: int = 16,
    *,
    frequency: float = 440.0,
    amplitude: float = 0.2,
    fmt_override: dict | None = None,
) -> bytes:
    """Return a valid PCM WAV, with optional header field overrides."""
    frames = max(1, int(duration * sample_rate))
    block_align = channels * bits // 8
    data = bytearray()
    for index in range(frames):
        value = int(
            amplitude * math.sin(2 * math.pi * frequency * index / sample_rate) * 0x7FFF
        )
        for _ in range(channels):
            if bits == 16:
                data += struct.pack("<h", value)
            elif bits == 8:
                data += struct.pack("<B", max(0, min(255, value // 256 + 128)))
            else:  # pragma: no cover - only used by explicit bad-header tests
                data += struct.pack("<i", value)

    audio_format = 1
    header_channels = channels
    header_rate = sample_rate
    header_bits = bits
    header_align = block_align
    if fmt_override:
        audio_format = fmt_override.get("audio_format", audio_format)
        header_channels = fmt_override.get("channels", header_channels)
        header_rate = fmt_override.get("sample_rate", header_rate)
        header_bits = fmt_override.get("bits", header_bits)
        header_align = fmt_override.get("block_align", header_align)

    fmt = struct.pack(
        "<HHIIHH",
        audio_format,
        header_channels,
        header_rate,
        header_rate * max(1, header_channels) * max(1, header_bits) // 8,
        header_align,
        header_bits,
    )
    data_bytes = len(data)
    riff_size = 4 + (8 + len(fmt)) + (8 + data_bytes)
    return b"".join(
        [
            b"RIFF",
            struct.pack("<I", riff_size),
            b"WAVE",
            b"fmt ",
            struct.pack("<I", len(fmt)),
            fmt,
            b"data",
            struct.pack("<I", data_bytes),
            bytes(data),
        ]
    )
