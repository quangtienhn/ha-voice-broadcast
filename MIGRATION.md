# Migrating from TTS Broadcast

**English** | [Tiếng Việt](./MIGRATION.vi.md)

Voice Broadcast replaces the earlier **TTS Broadcast** integration. It keeps the same
features and adds a voice relay (record in the card, play, delete). It is a different
integration, not an in-place upgrade:

| Item | TTS Broadcast | Voice Broadcast |
|------|---------------|-----------------|
| Domain / folder | `tts_broadcast` | `voice_broadcast` |
| Services | `tts_broadcast.*` | `voice_broadcast.*` |
| Card type | `custom:tts-broadcast-card` | `custom:voice-broadcast-card` |
| Card file | `tts-broadcast-card.js` | `voice-broadcast-card.js` |
| Repository | old repository | `ha-voice-broadcast` (private) |
| Version | 1.2.1 | 0.1.0 |

Entity ids are created by Home Assistant from the new device and entity names, so they
will not be identical to the old ones. Update dashboards, scripts and automations that
refer to the old entities or services.

## Before you start

1. Take a backup: Settings -> System -> Backups -> Create backup.
2. Note which speakers, TTS entity, volume and phrase settings the old integration uses.
3. Keep the old integration installed until the new one is configured and tested. Both
   can run at the same time.

## Install Voice Broadcast

### Manual install (works while the repository is private)

1. Copy `custom_components/voice_broadcast` to `config/custom_components/voice_broadcast`.
2. Restart Home Assistant.
3. Settings -> Devices & Services -> Add integration -> **Voice Broadcast**.

### HACS

HACS cannot install a private repository without extra authentication. If HACS refuses
the repository, use the manual install above. HACS support is expected to work once the
repository is public.

## Import the old settings (read-only)

When a `tts_broadcast` config entry exists, the first setup screen offers **Import from
TTS Broadcast**:

- **Import settings** copies the old speakers, TTS entity, initial volume, language,
  options and phrase settings into the form. Review them and submit.
- Clearing the checkbox starts from an empty form instead.

The import only reads the old entry. It does not modify, disable or delete it, and it
does not copy entity ids, dashboards or automations. You can run the import only while
the old entry still exists.

## Switch your dashboards and automations

1. Add the new card to a test dashboard:

   ```yaml
   type: custom:voice-broadcast-card
   ```

2. Confirm the speaker switches, volume, message, Speak/Stop and the TALK row work.
3. Replace `tts_broadcast.speak` with `voice_broadcast.speak`, and
   `tts_broadcast.stop` with `voice_broadcast.stop`, in scripts and automations.
4. Replace old entity ids used by dashboards and automations with the new ones found in
   Settings -> Devices & Services -> Voice Broadcast.
5. If you used the old blueprint, import the new one from
   `blueprints/automation/voice_broadcast/voice_announce.yaml`.
6. Check the Assist pipeline: create or edit it so the conversation agent is **Voice
   Broadcast**, and point the card at that pipeline (or leave `assist_pipeline_id:
   auto`). Do not make it the default pipeline.

## Try the new voice relay

1. Open the new card over HTTPS or `localhost`.
2. Click **Record**, allow the microphone, speak, and click **Stop recording**.
3. The clip plays on the switched-on speakers. Click **Delete recording** to discard it.
4. Read the relay section of `README.md` for limits and troubleshooting.

## Remove the old integration

Only after the new setup is verified:

1. Settings -> Devices & Services -> TTS Broadcast -> Delete.
2. Delete `config/custom_components/tts_broadcast`.
3. Remove the old card (`custom:tts-broadcast-card`) from dashboards.
4. Remove old `tts_broadcast.*` service calls from scripts and automations.
5. Restart Home Assistant.

Deleting the old integration removes its entities and device. It does not affect the new
integration or the recordings in `config/voice_broadcast_tmp/`.

## Rollback

The change is reversible while the old integration is still installed: disable or remove
the new entry, restore the old card, and point automations back to `tts_broadcast.*`.
There is no automatic data migration in either direction; configuration is copied by the
read-only import step only.

## Common issues

| Symptom | Cause / fix |
|---------|-------------|
| The import step does not appear | No `tts_broadcast` config entry exists, or the new entry is already configured. |
| Old automations call a service that no longer exists | They still use `tts_broadcast.*`; update them to `voice_broadcast.*`. |
| Dashboard card is missing | Use `custom:voice-broadcast-card`, then hard-refresh the browser. |
| Both integrations answer Assist | Two pipelines or two conversation agents match; keep one pipeline for announcements. |
| Speakers announce twice | Both integrations (or an old YAML package) still act on the same message; remove the duplicate. |
| HACS cannot add the repository | It is private; install manually or authenticate HACS. |
