# Security Policy

## Supported versions

The following versions of Voice Broadcast receive security updates:

| Version | Supported |
|---------|-----------|
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x: |

## Reporting a vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Send details privately to the repository owner via GitHub (the contact method
on the profile page), describing:

- The affected version of Voice Broadcast.
- The Home Assistant version.
- Steps to reproduce the issue.
- The expected and actual behavior.

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
