# Voice Relay & Audio Processing

**English** | [Tiếng Việt](./VOICE_RELAY.md)

Voice Relay allows users to record their real voice directly inside the dashboard card and broadcast it across selected media players without relying on text-to-speech synthesis.

---

## Technical Specifications & Limits

- **Audio format**: Strict RIFF/WAVE PCM mono 16-bit.
- **Client capture**: Browser captures audio via `AudioWorklet` (fallback to `ScriptProcessor`), downsamples to 16 kHz, and generates a valid PCM WAV.
- **Payload limit**: Maximum 3 MiB body size (`MAX_BODY_BYTES = 3 * 1024 * 1024`).
- **Duration limit**: Hard limit 60 seconds; configurable from 5 to 60 seconds via integration options.
- **Storage**: Saved in private folder `config/voice_broadcast_tmp/`. This folder is outside `www/` and is never exposed directly via static file serving.
- **Token lifetime**: Each recording is assigned a random 43-character URL-safe token with a 120-second TTL.

---

## Security & Architecture

1. **Authenticated Upload**:
   - `POST /api/voice_broadcast/recording` requires Home Assistant user authentication (handled transparently via `hass.fetchWithAuth`).
   - Unauthenticated POST attempts receive HTTP 401.

2. **Unauthenticated Speaker Download**:
   - `GET /api/voice_broadcast/recording/{token}.wav` does not require credentials because embedded speakers (such as ESPHome) cannot send custom Authorization bearer headers when streaming media.
   - The token is a 32-byte cryptographic random string (`secrets.token_urlsafe(32)`).
   - Only registered, unexpired tokens are served. The path is looked up from in-memory records; arbitrary filesystem paths cannot be accessed.

3. **Lifecycle & Automatic Cleanup**:
   - The temporary file is automatically removed:
     - When all targeted speakers transition from playing/buffering to idle/off/standby (plus a grace buffer).
     - On timeout (duration + 15 seconds grace period).
     - When the **Stop** button or `voice_broadcast.stop` service is called.
     - On integration reload or Home Assistant shutdown.
     - On Home Assistant startup (leftover files are purged).
     - By a periodic background sweep task every 30 seconds.
   - Audio data, file paths, and tokens are never logged.

4. **Concurrency & Busy Locking**:
   - While a relay recording is actively playing, the integration sets `relay_playing = True`.
   - Any concurrent attempt to broadcast TTS or upload another voice recording immediately returns HTTP 409 / ServiceValidationError (`busy`).
   - Pressing **Stop** immediately cancels playback, deletes the file, and resets `relay_playing = False`.
