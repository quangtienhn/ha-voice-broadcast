# Troubleshooting Guide

**English** | [Tiếng Việt](./TROUBLESHOOTING.vi.md)

This runbook covers common setup and runtime issues for Voice Broadcast.

---

## 1. Browser & Frontend Cache

**Symptom**: Dashboard card shows outdated buttons, missing features, or does not appear in the card picker after an update.

**Solution**:
- **Desktop**: Perform a hard refresh by pressing `Ctrl + F5` (or `Cmd + Shift + R`).
- **Mobile Companion App**: Go to **Settings** > **Companion App** > **Debugging** > **Reset frontend cache**, then restart the app.

---

## 2. "Recording needs a secure connection (HTTPS)"

**Symptom**: The card displays an error indicating that recording requires HTTPS or localhost.

**Cause**: Web browsers enforce secure context requirements for microphone APIs. Accessing Home Assistant over plain `http://<IP>:8123` blocks `getUserMedia`.

**Solution**:
- Access Home Assistant using an HTTPS URL or use `http://localhost:8123`.
- See the [HTTPS & LAN Network Guide](./HTTPS_LAN.md) for setting up local DNS rewrites.

---

## 3. "no_internal_url"

**Symptom**: Voice Relay upload fails with error code `no_internal_url`.

**Cause**: Voice Broadcast could not detect a plain HTTP internal URL for speakers to fetch the WAV file. Embedded speakers on the LAN cannot fetch through external HTTPS proxies.

**Solution**:
- Go to **Settings** > **System** > **Network**.
- In **Home Assistant URL**, ensure **Automatic** is enabled or configure **Local Network** to `http://<YOUR_LOCAL_IP>:8123`.

---

## 4. Reverse Proxy HTTP 413 (Payload Too Large)

**Symptom**: Voice recordings fail to upload when accessed through a reverse proxy (such as Nginx Proxy Manager).

**Cause**: The reverse proxy has a body size limit (often default 1 MB), rejecting audio payloads up to 3 MiB.

**Solution**:
- Add `client_max_body_size 10m;` to your Nginx proxy configuration. See [HTTPS & LAN Network Guide](./HTTPS_LAN.md).

---

## 5. Entities Show Redundant Device Prefix

**Symptom**: In stock entity cards, entities appear as *"Voice Broadcast Living Room Speaker"*.

**Explanation & Solution**:
- Home Assistant automatically prefixes entity friendly names with their parent device name when using default display names.
- The dedicated `custom:voice-broadcast-card` automatically strips this device name prefix so speaker names appear clean (e.g. *"Living Room Speaker"*).

---

## 6. Assist TALK Button & "No Assist Pipeline" Warning

**Symptom**: A warning in Repairs indicates that no Assist pipeline uses the Voice Broadcast conversation agent, or the card hides the TALK button.

**Cause**:
- By default, the card uses `assist_pipeline_id: "auto"`. If no pipeline is assigned to the Voice Broadcast agent, the TALK button is hidden to prevent accidental broadcast to all smart satellites.

**Solution**:
1. Go to **Settings** > **Voice assistants** > **Add assistant**.
2. Name it (e.g., *Voice Broadcast*).
3. Set **Conversation agent** to **Voice Broadcast**.
4. Configure your preferred STT and TTS engines.
5. Save the pipeline (do **not** make it the default assistant for the whole home).
6. Refresh your dashboard.

---

## 7. Extra Speakers Play Unexpectedly

**Symptom**: An announcement plays on speakers that were toggled off in the card.

**Runbook**:
1. In Developer Tools > Services, call `voice_broadcast.debug_selection` and review the output.
2. Turn ON exactly one speaker switch.
3. Call `voice_broadcast.speak` with `audit: true` and compare `targeted` against `unexpected_started`.
4. If `targeted` contains only the selected speaker and `unexpected_started` is empty, check Home Assistant's Logbook for third-party automations, scripts, or legacy speaker groups that may be reacting to media player state changes.
