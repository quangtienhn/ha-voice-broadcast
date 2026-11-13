"""Unit tests for the strict WAV validator."""

from __future__ import annotations

import pytest

from custom_components.voice_broadcast.const import MAX_BODY_BYTES
from custom_components.voice_broadcast.wav import (
    WavValidationError,
    parse_wav,
)
from tests.wav_utils import make_wav


def test_accepts_mono_16_bit_pcm_at_limits() -> None:
    for rate in (8000, 16000, 48000):
        info = parse_wav(make_wav(duration=0.25, sample_rate=rate))
        assert info.sample_rate == rate
        assert info.channels == 1
        assert info.bits_per_sample == 16
        assert 0.24 < info.duration < 0.26


def test_accepts_extra_chunk_before_data() -> None:
    wav = make_wav(duration=0.1)
    # Insert a LIST chunk (even size) between fmt and data.
    fmt_end = 12 + 8 + 16
    list_chunk = b"LIST" + (4).to_bytes(4, "little") + b"INFO"
    patched = wav[:fmt_end] + list_chunk + wav[fmt_end:]
    patched = patched[:4] + (len(patched) - 8).to_bytes(4, "little") + patched[8:]
    info = parse_wav(patched)
    assert info.channels == 1


@pytest.mark.parametrize(
    ("wav", "code"),
    [
        (b"", "empty"),
        (b"RIFF", "truncated"),
        (b"XXXX" + b"\0" * 20, "not_riff"),
        (b"RIFF" + (20).to_bytes(4, "little") + b"XXXX" + b"\0" * 8, "not_wave"),
        (
            make_wav(duration=0.1, fmt_override={"audio_format": 3}),
            "not_pcm",
        ),
        (make_wav(duration=0.1, channels=2), "not_mono"),
        (make_wav(duration=0.1, fmt_override={"bits": 24}), "not_16bit"),
        (
            make_wav(duration=0.1, fmt_override={"sample_rate": 7999}),
            "bad_sample_rate",
        ),
        (
            make_wav(duration=0.1, fmt_override={"sample_rate": 48001}),
            "bad_sample_rate",
        ),
        (
            make_wav(duration=0.1, fmt_override={"block_align": 3}),
            "bad_block_align",
        ),
    ],
)
def test_rejects_bad_headers(wav: bytes, code: str) -> None:
    with pytest.raises(WavValidationError) as err:
        parse_wav(wav)
    assert err.value.code == code


def test_rejects_missing_fmt_and_data() -> None:
    no_fmt = (
        b"RIFF"
        + (12).to_bytes(4, "little")
        + b"WAVE"
        + b"data"
        + (0).to_bytes(4, "little")
    )
    with pytest.raises(WavValidationError) as err:
        parse_wav(no_fmt)
    assert err.value.code == "missing_fmt"

    no_data = (
        b"RIFF"
        + (36).to_bytes(4, "little")
        + b"WAVE"
        + b"fmt "
        + (16).to_bytes(4, "little")
        + make_wav(duration=0.1)[20:36]
    )
    with pytest.raises(WavValidationError) as err:
        parse_wav(no_data)
    assert err.value.code == "missing_data"


def test_rejects_zero_length_payload() -> None:
    wav = make_wav(duration=0.1)
    # Keep the full data chunk header, but declare a zero-length payload.
    data_offset = len(wav) - int(0.1 * 16000) * 2 - 8
    empty = wav[: data_offset + 4] + (0).to_bytes(4, "little")
    with pytest.raises(WavValidationError) as err:
        parse_wav(empty)
    assert err.value.code == "zero_length"


def test_rejects_truncated_data_chunk() -> None:
    wav = make_wav(duration=0.1)
    with pytest.raises(WavValidationError) as err:
        parse_wav(wav[:-10])
    assert err.value.code == "truncated"


def test_rejects_longer_than_the_requested_limit() -> None:
    wav = make_wav(duration=2.0)
    with pytest.raises(WavValidationError) as err:
        parse_wav(wav, max_duration=1.0)
    assert err.value.code == "too_long"


def test_rejects_payload_over_the_byte_limit() -> None:
    with pytest.raises(WavValidationError) as err:
        parse_wav(make_wav(duration=0.1), max_bytes=100)
    assert err.value.code == "too_large"


def test_byte_limit_constant_is_three_megabytes() -> None:
    assert MAX_BODY_BYTES == 3 * 1024 * 1024
