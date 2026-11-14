# Dashboard Card (`custom:voice-broadcast-card`)

**English** | [Tiếng Việt](./CARD.vi.md)

The integration includes a custom Lovelace dashboard card (`voice-broadcast-card.js`) that automatically discovers integration entities and provides an all-in-one broadcast interface.

---

## Features

- **Header chip & collapsible speakers**: Compact view with quick toggle.
- **Shared volume slider**: Controls volume across all enabled speakers.
- **Microphone tap-to-talk**: Click to record your voice and broadcast via Voice Relay.
- **TTS textarea**: Type a message and broadcast immediately.
- **Assist TALK row**: Directly trigger Home Assistant Assist pipelines with automatic detection (`assist_pipeline_id: "auto"`).
- **Device-name prefix stripping**: Automatically cleans up friendly names for clean display.

---

## Card Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `type` | string | **Required** | Must be `custom:voice-broadcast-card`. |
| `title` | string | `"Voice Broadcast"` | Custom title displayed at the top of the card. |
| `show_volume` | boolean | `true` | Show or hide the shared volume slider. |
| `show_message` | boolean | `true` | Show or hide the typed message box and Speak button. |
| `show_assist` | boolean | `true` | Show or hide the Assist TALK button. |
| `show_record` | boolean | `true` | Show or hide the Voice Relay microphone recording interface. |
| `show_select_buttons` | boolean | `true` | Show or hide Select All / Select None buttons. |
| `assist_pipeline_id` | string | `"auto"` | `"auto"`, `"preferred"`, `"last_used"`, or a concrete Assist pipeline ID. |
| `assist_name` | string | localized | Override the TALK button label. |
| `assist_icon` | string | `"mdi:microphone"` | Override the TALK button icon. |
| `max_record_seconds` | number | server limit | Client-side recording time limit cap (5–60 s). |

---

## YAML Examples

### Basic Example (Default)

```yaml
type: custom:voice-broadcast-card
```

### Customized Card Example

```yaml
type: custom:voice-broadcast-card
title: "Announcements"
show_volume: true
show_record: true
show_message: true
show_assist: true
assist_pipeline_id: "auto"
assist_name: "Speak"
max_record_seconds: 30
```

---

## Cache Refresh Tips

When updating the card, your browser or the Home Assistant Companion app may cache older JavaScript assets.

- **Desktop Browser**: Press `Ctrl + F5` (or `Cmd + Shift + R` on macOS) to perform a hard refresh.
- **Companion App (Android / iOS)**:
  - Go to **Settings** > **Companion App** > **Debugging** > **Reset frontend cache**.
  - Or force-close and restart the app.
