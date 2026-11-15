# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | :white_check_mark: |
| < 0.2.0 | :x: |

## Reporting a vulnerability

Please do **not** report security vulnerabilities through public GitHub issues.

Use [GitHub private vulnerability reporting](https://github.com/quangtienhn/ha-voice-broadcast/security/advisories/new) (Security tab → "Report a vulnerability"). Describe:

- The affected version of Voice Broadcast.
- The Home Assistant version and installation type (HAOS / Container / Core).
- Steps to reproduce the issue.
- The expected and actual behavior.

If private vulnerability reporting is unavailable, open a regular issue asking the
maintainer to enable it, or contact the owner privately through the profile page on
GitHub; do not include exploit details in a public issue.

## Scope

Voice Broadcast is a local, cloud-free integration:

- It never sends message text to an external service.
- It logs no message text at info level, and no audio bytes, recording tokens or
  temporary file paths.
- It uses only public Home Assistant APIs and makes no outbound network calls
  of its own.
- Relay uploads and deletes require authentication. The speaker-facing download is
  token-only, serves files from `config/voice_broadcast_tmp/` (outside `www/`), and
  the token expires after 120 seconds.
- Anyone who can reach an Assist pipeline using the Voice Broadcast agent can
  trigger announcements on your speakers; protect your Assist pipeline access
  accordingly.

## Disclaimer

This integration is not affiliated with or endorsed by Home Assistant, Nabu
Casa, Tapo/TP-Link, Zalo, or Google.
