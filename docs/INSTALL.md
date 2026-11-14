# Installing Voice Broadcast

**English** | [Tiếng Việt](./INSTALL.vi.md)

Voice Broadcast can be installed via HACS (recommended once the repository is public) or manually.

---

## Method 1: HACS (Recommended)

> **Note:** HACS requires the repository to be public. If the repository is currently private, use Method 2 (Manual Installation).

1. In Home Assistant, open **HACS** > **Integrations**.
2. Click the top-right menu (three vertical dots) and choose **Custom repositories**.
3. Enter the repository URL:
   ```text
   https://github.com/quangtienhn/ha-voice-broadcast
   ```
4. Set **Category** to **Integration** and click **Add**.
5. Find **Voice Broadcast** in HACS and click **Download**.
6. Restart Home Assistant: **Settings** > **System** > **Restart**.
7. Add the integration: **Settings** > **Devices & Services** > **Add Integration** > search for **Voice Broadcast**.

---

## Method 2: Manual Installation

1. Download or clone this repository.
2. Copy the `custom_components/voice_broadcast` directory into your Home Assistant configuration directory under `custom_components/`:
   ```text
   config/custom_components/voice_broadcast/
   ```
3. Ensure directory structure looks like:
   ```text
   config/
   └── custom_components/
       └── voice_broadcast/
           ├── __init__.py
           ├── manifest.json
           ├── const.py
           ├── ...
           └── www/
               └── voice-broadcast-card.js
   ```
4. Restart Home Assistant completely.
5. In Home Assistant, go to **Settings** > **Devices & Services** > **Add Integration**.
6. Search for **Voice Broadcast** and follow the setup wizard.
