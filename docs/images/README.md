# Screenshots

Screenshots used by `README.md` and `README.vi.md`. Links are relative so they
render correctly on GitHub.

| File | Shows | Used in |
|------|-------|---------|
| `dashboard-card.png` | Voice Broadcast card on a dashboard: per-speaker switches, message box, Select all/none, Speak, Stop and volume | README -> Dashboard card |
| `assist-pipeline-setup.png` | Settings -> Voice assistants: conversation agent "Voice Broadcast" with the STT and TTS engines | README -> Voice setup |
| `voice-phrases.png` | Options flow, Voice phrases step: strip/keep phrases, require phrase, fallback agent, accent insensitive | README -> Configuration |

These screenshots were taken before the voice relay row existed, so the card
image does not show the Record/Delete controls. The relay is documented in the
README and `TESTING.md`; a new screenshot would be welcome.

## Redaction

`dashboard-card.png` was processed from the author's own screenshot. The real
speaker names were replaced with neutral placeholders (`Loa 1` .. `Loa 8`) so the
household layout is not revealed. The original file is not part of this
repository.

## Still missing

The following would improve the docs but are not required:

1. `device-page.png` - Voice Broadcast device page in Settings -> Devices & Services.
2. `debug-view.png` - Developer Tools -> Services -> `voice_broadcast.debug_selection`
   result (sanitized).
3. `voice-relay.png` - card with the Record/Stop recording/Delete row.
