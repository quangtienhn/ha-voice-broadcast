# HTTPS & Local Network Setup

**English** | [Tiếng Việt](./HTTPS_LAN.vi.md)

Voice Relay requires two network conditions to operate smoothly:
1. **Secure Context (HTTPS)** for the browser or Companion app to access the microphone.
2. **Local HTTP Access** for local media players (such as ESPHome) to stream the recorded audio without SSL overhead or certificate errors.

---

## 1. Why HTTPS is Required for Microphones

Modern browsers block `navigator.mediaDevices.getUserMedia` on plain HTTP origins for security reasons. The only exception is `http://localhost`.

If you access Home Assistant via `http://<IP_ADDRESS>:8123`, the browser will refuse to provide microphone permissions, and the card will display:
> *"Recording needs a secure connection (HTTPS) or localhost. Open Home Assistant over HTTPS."*

---

## 2. Generic Split-Brain DNS / Reverse Proxy Setup

To use HTTPS both outside and inside your home without breaking local LAN speakers:

1. **Reverse Proxy / SSL**: Set up Nginx Proxy Manager, Caddy, or Cloudflare Tunnel to handle SSL certificates for your domain (e.g. `https://ha.example.com`).
2. **Local DNS Rewrite**:
   - In AdGuard Home, Pi-hole, or your router's DNS settings, add a DNS rewrite rule:
     ```text
     ha.example.com  ->  <Local_IP_of_HA_or_Reverse_Proxy>
     ```
   - When your phone is connected to home Wi-Fi, it connects directly to the local reverse proxy over HTTPS.
3. **Home Assistant Companion App**:
   - In App Settings > Connection:
     - **Home Assistant URL**: `https://ha.example.com`
     - **Internal Connection URL**: `https://ha.example.com`
     - **Home Wi-Fi SSIDs**: Select your home Wi-Fi network.

---

## 3. Keep Home Assistant Internal HTTP on Port 8123

Local speakers (ESPHome media players) cannot easily validate SSL certificates or stream over HTTPS on local networks.

- Ensure Home Assistant's internal network configuration (**Settings** > **System** > **Network**) has **Local Network** enabled or configured to:
  ```text
  http://<HA_LOCAL_IP>:8123
  ```
- Voice Broadcast automatically detects this internal HTTP URL to construct playback URLs for speakers:
  ```text
  http://<HA_LOCAL_IP>:8123/api/voice_broadcast/recording/<TOKEN>.wav
  ```

---

## 4. Nginx Reverse Proxy `client_max_body_size`

The default body size limit in Nginx is 1 MB. An audio recording of 30–60 seconds can reach up to 2–3 MB. If Nginx rejects the upload, you will receive an HTTP 413 error (*Payload Too Large*).

In your Nginx configuration, increase the body size limit and ensure WebSocket support:

```nginx
client_max_body_size 10m;

location / {
    proxy_pass http://127.0.0.1:8123;
    proxy_set_header Host $host;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```
