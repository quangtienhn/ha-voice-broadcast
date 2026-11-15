# Contributing to Voice Broadcast

Thanks for your interest in contributing to Voice Broadcast! This is a Home
Assistant custom integration that broadcasts TTS announcements to multiple
speakers, and relays short voice recordings from the dashboard card.

## How to contribute

1. Fork the repository (once it is public) or work in a clone.
2. Create a branch from `main`.
3. Make your change, add or update tests, and keep commits small and focused.
4. Run the checks below and make sure they are green.
5. Open a pull request against `main` and describe what changed and why.

Forks and pull requests are welcome.

## Development setup

This project was developed against Home Assistant Core 2026.10.4 and checked against
the 2026.11.0 source tree. Minimum supported version is 2026.11.0.

```bash
# Clone the repo into your HA config's custom_components folder, or run the
# test harness from this repository root.
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements_test.txt
```

## Checks

Run these before pushing:

```bash
ruff check .
ruff format --check .
pytest tests
node --check custom_components/voice_broadcast/www/voice-broadcast-card.js
node tests/test_card_display_name.mjs
node tests/test_card_recording.mjs
```

Optionally validate the integration manifest with hassfest:

```bash
python -m script.hassfest --integration-path custom_components/voice_broadcast --core-path <path-to-home-assistant-core>
```

## Working on the voice relay

- Keep the speaker-facing download endpoint token-only. Never build a filesystem path
  from a request parameter, and never log audio bytes, tokens or file paths.
- Temporary WAV files belong in `config/voice_broadcast_tmp/`, never in `www/` or
  `.storage`.
- Any new cleanup path must be covered by a test that proves the file disappears.
- The card may use only `hass.fetchWithAuth` (no unauthenticated upload) and must keep
  the `AudioWorklet` + `ScriptProcessor` fallback.

## Style

- Follow the existing code style (ruff, black-compatible formatting).
- Keep commits small and write a clear message.
- For every bug fix, add a regression test that fails first, then passes.
- All user-facing strings must have English and Vietnamese translations (including the
  card strings); run the translation parity test (`tests/test_translations.py`).
- Update `README.md`, `README.vi.md` and `CHANGELOG.md` for user-visible changes.

## License

MIT. See `LICENSE`.
