# Screenshots

Screenshots used by `README.md`, `README.vi.md`, `docs/CARD.md`, `docs/CARD.vi.md`,
`docs/VOICE_RELAY.md` and `docs/VOICE_RELAY.vi.md`. Links are relative so they render
correctly on GitHub.

| File | Shows |
|------|-------|
| `card-speakers.jpg` | Dashboard card with the speaker list expanded, volume, tap-to-talk mic, TTS text and Assist row |
| `card-collapsed.jpg` | Dashboard card with the speaker list collapsed |
| `card-full.jpg` | Dashboard card in full view |
| `device-info.jpg` | Device page with one switch per speaker |
| `config-voice-phrases.jpg` | Options flow, Voice phrases step |

## Privacy

The screenshots come from the author's own Home Assistant instance. Real speaker and
entity names were covered with the surrounding background colour using
`scripts/redact_images.py`, and all EXIF/XMP metadata was stripped by re-saving the
images. `scripts/ocr_images.py` re-reads the finished files and fails if any personal
name, private address, token or URL pattern reappears.

The originals are not part of this repository.
