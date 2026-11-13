"""Strict WAV (RIFF/WAVE PCM) validation for the voice relay.

The browser sends raw WAV bytes, so the header is parsed here instead of
trusting the Content-Type. Only PCM 16-bit mono at 8-48 kHz is accepted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .const import (
    MAX_BODY_BYTES,
    MAX_DURATION_SECONDS,
    MAX_SAMPLE_RATE,
    MIN_SAMPLE_RATE,
    WAV_BITS_PER_SAMPLE,
    WAV_CHANNELS,
)

_RIFF: Final = b"RIFF"
_WAVE: Final = b"WAVE"
_FMT: Final = b"fmt "
_DATA: Final = b"data"
_PCM_FORMAT: Final = 1


class WavValidationError(Exception):
    """Raised when an uploaded file is not an acceptable WAV recording."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True, slots=True)
class WavInfo:
    """Facts read from a validated WAV file."""

    sample_rate: int
    channels: int
    bits_per_sample: int
    data_bytes: int
    duration: float


def _u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "little")


def _u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def parse_wav(
    data: bytes,
    *,
    max_duration: float = MAX_DURATION_SECONDS,
    max_bytes: int = MAX_BODY_BYTES,
) -> WavInfo:
    """Validate WAV bytes and return their audio facts.

    Raises ``WavValidationError`` with a short machine-readable code:
    empty, too_large, not_riff, not_wave, missing_fmt, missing_data,
    not_pcm, not_mono, not_16bit, bad_sample_rate, bad_block_align,
    truncated, zero_length, too_long.
    """
    if not data:
        raise WavValidationError("empty")
    if len(data) > max_bytes:
        raise WavValidationError("too_large")
    if len(data) < 12:
        raise WavValidationError("truncated")
    if data[0:4] != _RIFF:
        raise WavValidationError("not_riff")
    if data[8:12] != _WAVE:
        raise WavValidationError("not_wave")

    offset = 12
    fmt: bytes | None = None
    data_bytes: int | None = None

    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        chunk_size = _u32(data, offset + 4)
        body_start = offset + 8
        body_end = body_start + chunk_size
        if body_end > len(data):
            raise WavValidationError("truncated")
        if chunk_id == _FMT:
            fmt = data[body_start:body_end]
        elif chunk_id == _DATA:
            data_bytes = chunk_size
            # The data chunk is the payload; trailing chunks are not needed.
            break
        # RIFF chunks are word aligned.
        offset = body_end + (chunk_size & 1)

    if fmt is None or len(fmt) < 16:
        raise WavValidationError("missing_fmt")
    if data_bytes is None:
        raise WavValidationError("missing_data")

    audio_format = _u16(fmt, 0)
    channels = _u16(fmt, 2)
    sample_rate = _u32(fmt, 4)
    block_align = _u16(fmt, 12)
    bits_per_sample = _u16(fmt, 14)

    if audio_format != _PCM_FORMAT:
        raise WavValidationError("not_pcm")
    if channels != WAV_CHANNELS:
        raise WavValidationError("not_mono")
    if bits_per_sample != WAV_BITS_PER_SAMPLE:
        raise WavValidationError("not_16bit")
    if not MIN_SAMPLE_RATE <= sample_rate <= MAX_SAMPLE_RATE:
        raise WavValidationError("bad_sample_rate")
    expected_block_align = channels * bits_per_sample // 8
    if block_align != expected_block_align:
        raise WavValidationError("bad_block_align")
    if data_bytes == 0:
        raise WavValidationError("zero_length")

    duration = data_bytes / (sample_rate * expected_block_align)
    if duration > max_duration:
        raise WavValidationError("too_long")

    return WavInfo(
        sample_rate=sample_rate,
        channels=channels,
        bits_per_sample=bits_per_sample,
        data_bytes=data_bytes,
        duration=duration,
    )
