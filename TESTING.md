# Testing

## Automated

```bash
ruff check .
ruff format --check .
pytest tests
node --check custom_components/voice_broadcast/www/voice-broadcast-card.js
node tests/test_card_display_name.mjs
node tests/test_card_recording.mjs
```

`hassfest` runs in CI (`.github/workflows/hassfest.yml`). The automated suite covers WAV
validation, upload authentication, token/path-traversal rejection, playback selection and
volume, per-speaker failure, cleanup, concurrency, the browser helpers (downsample, WAV
encoder, diagnostics), the import step and coexistence with a stubbed legacy
`tts_broadcast` integration. It uses mocked media players and does **not** prove real
hardware, a real browser or the Companion app.

## Manual checklist (real Home Assistant)

- (a) Configure -> Speakers & TTS -> change a phrase/speaker -> Submit works and the entry
  reloads.
- (b) Set a fallback agent, then clear it, and confirm it is really cleared.
- (c) Selecting the Voice Broadcast agent as its own fallback is rejected.
- (d) "thông báo" alone gets a spoken request for content, never "missing_content".
- (e) With `reply_text` set and no speaker selected, the assistant does NOT claim it sent.
- (f) After changing options, the card is still in the card picker without restarting HA.
- (g) Card TALK row: with `assist_pipeline_id: auto`, the card finds the pipeline whose
  conversation agent is Voice Broadcast; with no such pipeline, the TALK row is hidden and
  an info line is shown; an explicit pipeline id is honored.
- (h) Configure -> Recording: set the maximum to 5 s, save, reload, and confirm the value
  is kept and the card shows a 5 s cap.

## Voice relay — real hardware checklist

These steps need a real speaker and a real browser. They have **not** been run by the
project author on real hardware at release time.

### Prerequisites

1. Home Assistant is reachable over HTTPS (Nabu Casa, a reverse proxy, or a local
   certificate) or through `localhost`.
2. The speakers can reach Home Assistant over plain HTTP on the LAN. Check the internal
   URL in Settings -> System -> Network, or open the card: a `no_internal_url` message
   means the integration could not build a LAN URL.
3. At least one speaker switch is on and the speaker is not `unavailable`.

### Steps

1. Open the dashboard with the Voice Broadcast card and hard-refresh the browser.
2. Click **Record**. The browser asks for microphone permission the first time. Allow it.
3. Speak for 3–5 seconds, then click **Stop recording**. Confirm:
   - the card shows an uploading/playing state;
   - the clip is audible on every switched-on speaker;
   - a speaker that was turned off does not play;
   - the volume matches the slider (except speakers in "without volume control").
4. Wait for the clip to finish. Confirm there is no repeated playback and the card returns
   to a ready state.
5. Click **Record**, speak, click **Stop**, then immediately click **Speak** (TTS). Confirm
   the TTS call reports busy or waits, and that the relay and TTS never play on top of each
   other.
6. Click **Delete recording** and confirm the card reports the recording deleted.
7. Repeat once with a microphone permission denied (block the microphone in the browser).
   Confirm a localized permission message appears and no upload is attempted.
8. Repeat over plain HTTP on a non-localhost origin. Confirm the card explains that a
   secure connection is required instead of silently failing.
9. Repeat in the Home Assistant Companion app on a phone over HTTPS. Confirm recording
   works and the clip plays.
10. Record with the maximum length set to 5 s and confirm auto-stop; record a very short
    tap and confirm the "too short" message.

### Cleanup check

1. Note the current time and start a recording.
2. While the clip plays, inspect `config/voice_broadcast_tmp/` (SSH, Samba, or the File
   editor add-on). A `.wav` file should exist briefly.
3. After playback (plus at most 15 seconds of grace) the file must be gone.
4. Press **Stop** during a longer message and confirm the file disappears immediately.
5. Restart Home Assistant with a leftover file in that folder and confirm it is removed at
   startup.

### Failure checks

1. Make one speaker `unavailable`, then record. Confirm the other speakers play, the card
   lists the failed speaker, and the integration logs a warning with the entity id only.
2. Send a request larger than 3 MiB or longer than 60 s with `curl` and a long-lived token.
   Confirm HTTP 413/400 and a short error code, and no file left behind.
3. Send an upload without an authorization header. Confirm HTTP 401.
4. Request a random token from the speaker-facing URL. Confirm HTTP 404.
5. Check the Home Assistant log: no audio bytes, file paths or tokens should appear.

Example upload with a long-lived token (the token is sensitive; do not paste it into an
issue):

```bash
curl -X POST \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: audio/wav" \
  --data-binary @clip.wav \
  "http://homeassistant.local:8123/api/voice_broadcast/recording?volume=60"
```

## Coexistence / migration checklist

1. With an old `tts_broadcast` entry present, start adding Voice Broadcast. Confirm the
   **Import from TTS Broadcast** step appears and the form is prefilled.
2. Confirm the old entry is unchanged after importing (still present, same options).
3. Confirm both integrations can announce; if both react to the same Assist sentence,
   disable the duplicate.
4. Remove the old entry and folder; confirm Voice Broadcast still works.

## Extra speakers play — runbook

If more speakers play than the one you selected:

1. Call `voice_broadcast.debug_selection` from Developer Tools and read the output.
2. Turn exactly one switch ON, call `voice_broadcast.speak` with `return_response`, and
   compare `targeted` (exact list sent to tts.speak) with `unexpected_started`.
3. If `unexpected_started` is empty and `targeted` has exactly one entity but other
   speakers still play, the cause is OUTSIDE this integration: check the Logbook for who
   started those players, list automations/scripts that call `tts.speak` or
   `media_player.play_media`, and look for the old YAML package (script `old_broadcast_script`, the
   "Assist - old announcement" automation, `input_boolean.old_*`).
4. If `targeted` has more than one entity, send the full `debug_selection` output, the
   switch states, and the integration log lines.

## Manual hardware checklist (TTS path)

1. Call `voice_broadcast.speak` from Developer Tools with a message.
2. Type a sentence in Assist using the configured trigger phrase.
3. Speak a sentence through Assist.
4. Press Stop during a long message and observe whether ESPHome announcement playback stops.
5. Restart Home Assistant and verify restored switch, volume and message states; nothing
   speaks automatically.
6. Disable one speaker and confirm the remaining speakers still play.
7. Card appears in picker after hard browser refresh.
8. Card renders all speakers and toggles/volume/message/Speak/Stop/Assist work.
9. Add a speaker in options flow and confirm card updates without edits.
10. Brand icon visible in Devices & services.
11. YAML generator output pastes and works.
