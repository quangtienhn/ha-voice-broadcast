# Release & Deployment Guide

This guide is for repository maintainers when preparing a public release.

---

## Steps for Publishing a Release

1. **Verify CI status**:
   - Ensure all automated checks (Ruff, Pytest, Node unit tests, Hassfest) are green on `main`.

2. **Verify Version Alignment**:
   - `custom_components/voice_broadcast/manifest.json`: `"version": "0.2.1"`
   - `custom_components/voice_broadcast/www/voice-broadcast-card.js`: `const VERSION = "0.2.1";`
   - `CHANGELOG.md`: Top entry matches `[0.2.1]`.

3. **Visibility**:
   - Go to GitHub Repository Settings > General > Danger Zone.
   - Click **Change visibility** and select **Make public**.

4. **Tag & Publish Release**:
   - Go to **Releases** > **Draft a new release**.
   - Choose tag: `v0.2.1` (target `main`).
   - Title: `Voice Broadcast 0.2.1`.
   - Copy the `[0.2.1]` section from `CHANGELOG.md` into the release description.
   - Click **Publish release**.
   - The GitHub Actions `release.yml` workflow will automatically build `voice_broadcast.zip` containing the contents of `custom_components/voice_broadcast` and attach it to the release.
