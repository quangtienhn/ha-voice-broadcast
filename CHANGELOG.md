# Changelog

All notable changes to the Voice Broadcast integration are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to Semantic Versioning.

## [0.2.1] - 2026-11-16

Dashboard card updated to the approved UI layout (header chip with selected count,
collapsible speaker list, shared volume, tap-to-talk microphone with waveform, TTS
textarea with Send/Stop, and an Assist row with an invisible official button overlay).

### Changed

- `voice-broadcast-card.js` replaced with the approved single-frame layout. Speaker-name
  prefix stripping, the Assist auto pipeline detection, the recorder pipeline
  (AudioWorklet with ScriptProcessor fallback, downsample to 16 kHz, PCM WAV encode),
  `hass.fetchWithAuth`, the `show_record` option and the cache-busted `?v=<version>`
  static URL are all preserved. `VERSION` is now `0.2.1`.
- `tests/test_card_display_name.mjs` rewritten against the new markup: it stubs the
  DOM APIs the card uses (`setAttribute`, `classList`, `classList.toggle`, recursive
  `querySelector`, `createTextNode`, `innerHTML` reset) and asserts the prefix is
  stripped from speaker names in the rendered rows.
- Fix the flaky `test_options_flow`/`test_import_flow` suite: two options-flow tests
  now `await hass.async_block_till_done()` after the `CREATE_ENTRY` submit, which
  eliminates a race where the entry reload timer could outlive the test.

## [0.2.0] - 2026-11-15

First public release of **Voice Broadcast**, bringing TTS multi-speaker broadcasting and dashboard voice relay recording together in a single custom integration.

### Features

- **Multi-speaker TTS announcement**: Announce typed or spoken messages across multiple speakers concurrently with isolated error handling.
- **Voice Relay**: Click-to-talk in the dashboard card, records mono PCM WAV via `AudioWorklet` (or `ScriptProcessor` fallback), downsamples to 16 kHz, and streams to local speakers over LAN HTTP without cloud dependencies.
- **Modern Dashboard Card (`custom:voice-broadcast-card`)**: Integrated compact layout with collapsible speakers list, shared volume slider, tap-to-talk mic button, TTS textarea, and native Assist integration.
- **Assist TALK row**: Automatically binds to Voice Broadcast Assist pipelines with `assist_pipeline_id: "auto"`.
- **Concurrency & Busy protection**: Dedicated busy state management preventing overlapping announcements or relay collisions.
- **Secure token downloads & automatic cleanup**: LAN playback uses unguessable single-purpose tokens; files are purged after playback, on timeout, on Stop, or on HA shutdown.
- **Read-only settings import**: Seamless migration from the predecessor integration (`tts_broadcast`) during initial setup.
- **Configurable limits & Diagnostics**: Customizable maximum recording length (5–60s), audit unexpected speaker playback, and redacted diagnostics.
- **Bilingual documentation**: Complete English and Vietnamese documentation covering installation, card options, Voice Relay, HTTPS/LAN setup, and troubleshooting.

### Changed

- The `audit_all_media_players` option is now exposed in the Speakers & TTS step (English and Vietnamese labels with helper text; default off). It was read internally since 1.1.2 but was not reachable from the UI.
- `strings.json` is now an exact key-parity copy of `translations/en.json`. A test fails if `en.json`, `vi.json` and `strings.json` key sets diverge.
- `RecordingUploadView` handles both `POST` (upload) and `DELETE` (discard) on `/api/voice_broadcast/recording`; the separate delete view (a duplicate route/name) was removed.
- While a relay is playing, a TTS announcement or a second relay returns a clear busy error (HTTP 409 for uploads, localized service error for `speak`) instead of overlapping playback; the **Stop** button clears the state and deletes the temporary file. The announce lock is not held during playback, so Stop stays responsive.
- Removed the `max_body_size` view attribute (absent from the HA 2026.10 typings); the 3 MiB limit is enforced with manual chunked reads. `dt_util.dt.timedelta` replaced with `datetime.timedelta`.
- Brand icons regenerated trimmed and centred; `hacs.json` trimmed to supported keys; documentation and README screenshots replaced with redacted images; README badges (HACS, minimum HA version, MIT) and the "Add to HACS" button.

## [0.1.0] - 2026-11-13

First release of **Voice Broadcast**, a renamed and extended copy of TTS Broadcast
1.2.1. This is a new project: the integration domain, services, card type and
repository all changed, so it can be installed next to the old one during a
migration.

### Added

- Voice relay: record a short voice message in the dashboard card
  (`show_record`, default on), upload it as a raw WAV, play it on the selected
  speakers, and delete it. The card uses Web Audio with an `AudioWorklet`
  (ScriptProcessor fallback), downsamples to 16 kHz and encodes PCM WAV in the
  browser; recording stops automatically at the configured limit.
- `POST /api/voice_broadcast/recording` (authenticated, 3 MiB, 60 s, 16-bit mono
  PCM WAV at 8–48 kHz), `GET /api/voice_broadcast/recording/{token}.wav`
  (token-only, no auth, 120 s TTL), `DELETE /api/voice_broadcast/recording`, and
  `GET /api/voice_broadcast/config`.
- Recording cleanup after playback, on timeout, on Stop, on entry unload, on Home
  Assistant shutdown, at startup and by a 30-second sweep, using the private
  `config/voice_broadcast_tmp/` directory.
- Busy handling shared with TTS announcements: a second relay or announcement gets
  HTTP 409 / a clear service error instead of queueing.
- New options step **Recording** (`max_record_seconds`, 5–60 s, default 60).
- One-time, read-only **Import from TTS Broadcast** step when a legacy
  `tts_broadcast` entry exists. The old entry is left untouched, and both
  integrations can run side by side.
- Strict WAV validator, relay HTTP/unit tests, browser-helper Node tests,
  coexistence and import tests, and a rename/identity guard test.
- Bilingual `MIGRATION.md` / `MIGRATION.vi.md` and relay instructions in
  `TESTING.md`.
- New brand icon (microphone with broadcast waves), independent of the old
  speaker icon.

### Changed

- Renamed everything from TTS Broadcast to Voice Broadcast: domain
  `voice_broadcast`, folder `custom_components/voice_broadcast`, services
  `voice_broadcast.*`, card `custom:voice-broadcast-card`, file
  `voice-broadcast-card.js`, static prefix `/voice_broadcast/`, API prefix
  `/api/voice_broadcast/`, version `0.1.0`.
- Card JS URL is cache-busted with the manifest version (`?v=0.1.0`); `VERSION` in
  `const.py` is read from `manifest.json` so the two cannot drift.
- Card entity rows strip the device-name prefix, and the card records with
  `hass.fetchWithAuth`.
- Diagnostics add a `relay` section (`active_recordings`, `temp_files`,
  `max_record_seconds`).
- Minimum Home Assistant version is `2026.11.0`.

### Security

- Upload and delete endpoints require authentication; audio bytes, tokens and file
  paths are never logged.
- The speaker-facing download endpoint accepts only a 43-character random token
  registered in memory; the token is never used as a filesystem path, and files
  live outside `www/`.

## History from TTS Broadcast

The entries below describe the code base this project was forked from. Version
numbers and repository links in them refer to the old project.

## [1.2.1]
### Added
- Dashboard card, Assist pipeline setup and Voice phrases screenshots in
  `docs/images/`, referenced from both READMEs.

### Fixed
- Card: entity rows drop the `Voice Broadcast` device prefix, so speakers display
  as configured (`Loa 1` instead of `Voice Broadcast Loa 1`). Display-only;
  entity ids, registry names and services are unchanged.
- README no longer lists the unimplemented `playback_mode` and
  `audit_all_media_players` options; manual install no longer references the
  gitignored `dist/voice_broadcast.zip`.
- Minimum HA version declared as `2026.11.0` (verified against HA 2026.10.4 source and the 2026.11.0 tag; removed the unverified 2025.1 assumption).
- Repairs issue "No Assist pipeline uses the Voice Broadcast agent" made non-intrusive: warning severity, not fixable, created only when voice phrases are configured, cleared automatically when a pipeline exists.
- Audit `audit: true` no longer holds the announce lock while waiting for the audit window; added a regression test proving a second announcement completes while the first waits for its audit.
- Card editor documents the `assist_pipeline_id` control (text field) and README/TESTING.md kept consistent.
- Language quality pass on README.md and README.vi.md.
- Secrets/PII scan: gitleaks 8.30.1 attempted (binary unavailable via PATH); manual grep of working tree and full git history found no secrets, tokens, emails, personal names, real IPs, or tracked prompt/work-log files in voice_broadcast.

## [1.2.0]

### Fixed
- Card: the TALK (Assist) row now defaults to `assist_pipeline_id: "auto"` and
  selects the Assist pipeline whose conversation engine is the Voice Broadcast
  agent, instead of falling back to the user's default pipeline (which could
  broadcast to all Assist satellites). `preferred` and `last_used` still work
  only when set explicitly. `assist_name` / `assist_icon` editor options added.
- Card: when no Assist pipeline uses the Voice Broadcast agent, the TALK row is
  hidden and a localized info line is shown instead of silently falling back.
- `_build_dashboard_card_yaml` emits the discovered `pipeline_id` (never
  `preferred`) when exactly one pipeline uses the Voice Broadcast agent; a
  commented placeholder is shown otherwise.
- Repairs issue "No Assist pipeline uses the Voice Broadcast agent" created on
  setup and cleared when a pipeline exists.

### Changed
- `services.yaml` now declares `debug_selection`, plus the `cache` and `audit`
  fields of `speak`; English and Vietnamese translations added.
- `voice_broadcast.speak` gains an optional `audit: true` field: wait up to 20 s
  and return `unexpected_started` details in the response.
- Audit now counts only real state transitions, dedupes entities, records
  `from_state`/`to_state`/context ids per unexpected player, and keeps the last
  5 announcements keyed by context id. Defaults to observing configured
  speakers; new option `audit_all_media_players` observes everything.
- Card editor `assist_pipeline_id` is a plain text field documenting the
  allowed values (`auto`, `preferred`, `last_used`, concrete id).
- Minimum HA version declared as 2025.1 in `hacs.json` and the README.

### Added
- `voice_broadcast.debug_selection` diagnostic service (already in 1.1.3, now
  also returns `audit_store`).
- `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`,
  issue/PR templates, Dependabot config, and a `PUBLISH_CHECKLIST.md` to
  prepare the repository for going public.

## [1.1.3] - Investigation: extra speakers play

### Added
- Dedicated `Context` per announcement, passed to every `volume_set` /
  `tts.speak` / `media_stop` call; `context.id` stored in the last result.
- 20 s state-change audit listener that classifies unexpected media players
  (started but not targeted by this integration) and logs them at WARNING.
- `targeted` and `unexpected_started` in the `speak` response and in
  `diagnostics.py` / `voice_broadcast.debug_selection`.
- Registry hygiene warnings for stale or duplicate switch mappings.
- `voice_broadcast.debug_selection` diagnostic service (no side effects, no
  speech).

## [1.1.2] - Follow-up 4

### Fixed
- `tts.speak` is called once per speaker (`media_player_entity_id: [speaker]`)
  concurrently with `asyncio.gather(return_exceptions=True)`; a failing speaker
  never marks the others as failed.
- `volume_set` runs concurrently per speaker; a volume failure does not block
  TTS.
- Response keeps `played` / `skipped` / `failed` and adds `errors`
  `{entity_id: short error text}`. "played" means HA accepted the request.
- One info log per announcement with entity ids only (never message text);
  warning per failed speaker with exception type + message; debug timing.
- Last announcement result stored in `runtime_data` and returned by
  `diagnostics.py`.
- New optional `cache` field (bool, default false) for `tts.speak`.
- Volume slider is now the single source of truth
  (`runtime_data.volume`, synced from `async_set_native_value` and restored
  state). Precedence: service `volume` argument > slider value > options
  "Initial volume".
- Options field "Default volume" relabeled to "Initial volume" (en/vi).
- Empty `blueprints/` folder removed from the integration.

### Added
- Tests: one speaker failing does not stop the others; response shape;
  `volume_set` skip for no-volume speakers; unavailable speaker skipped;
  diagnostics contains the last result; slider value used / overridden /
  restored after reload.

## [1.1.1] - Follow-up 3

### Fixed
- Voice phrases options step could never be saved: validation split into
  per-step sections (`_validate_speakers_section` / `_validate_voice_section`);
  cleared optional fields are removed (not preserved); fallback agent cannot be
  the integration's own conversation entity (validation + runtime guard).
- Wrong spoken replies: reply keys mapped to a localized en/vi table;
  `reply_text` overrides only the success reply.
- Fallback agent cannot be cleared fixed; fallback errors logged and answered
  with a localized reply instead of being swallowed.
- Static path / card JS registered once in `async_setup` (guarded by
  `hass.data[DOMAIN]["static_registered"]`), not removed on unload.
- Public `homeassistant.components.conversation` exports used
  (`ConversationEntity`, `async_converse`, `ConversationResult`).
- `options.error` added to en/vi translations; config step labels and
  descriptions added; `entity.switch.speaker.name` added to vi; conversation
  entity name translated; translation parity test added.
- Card: `assist_pipeline_id` uses the `assist_pipeline` selector; dashboard YAML
  emits `pipeline_id: preferred` and localized Assist name.
- Duplicate aliased imports removed; typed runtime data used throughout.
- Version bumped to 1.1.1.

## [1.1.0] - Built-in voice phrases and conversation agent

### Added
- Built-in conversation agent with phrase matching (strip / keep / require /
  accent-insensitive).
- Options flow with Speakers & TTS and Voice phrases steps.
- `voice_broadcast.speak` / `stop` / `get_dashboard_card` services.
- Dashboard card (`voice-broadcast-card`), brand icon, switch/number/text/button
  entities.
- Translations en/vi.
