# Cấu hình mạng HTTPS & Mạng cục bộ (LAN)

[English](./HTTPS_LAN.md) | **Tiếng Việt**

Tính năng ghi âm giọng nói (Voice Relay) yêu cầu hai điều kiện mạng hoạt động song song:
1. **Kết nối bảo mật (HTTPS)**: Trình duyệt hoặc ứng dụng Companion cần HTTPS để cấp quyền truy cập micro.
2. **Kết nối HTTP nội bộ**: Các loa thông minh trong mạng LAN (như ESPHome) cần tải file âm thanh qua HTTP thông thường để tránh lỗi chứng chỉ SSL và giảm tải xử lý.

---

## 1. Tại sao cần HTTPS để thu âm?

Các trình duyệt hiện đại chặn hoàn toàn API `navigator.mediaDevices.getUserMedia` khi truy cập qua giao thức HTTP thường (ngoại trừ địa chỉ `http://localhost`).

Nếu bạn mở Home Assistant bằng `http://<IP_LAN>:8123`, trình duyệt sẽ chặn micro và thẻ sẽ hiển thị cảnh báo:
> *"Ghi âm cần kết nối bảo mật (HTTPS) hoặc localhost. Hãy mở Home Assistant qua HTTPS."*

---

## 2. Giải pháp DNS nội bộ & Reverse Proxy

Để điện thoại vừa truy cập được bằng HTTPS khi ở nhà vừa không làm gián đoạn các thiết bị loa trong mạng LAN:

1. **Reverse Proxy / Chứng chỉ SSL**: Cấu hình Nginx Proxy Manager, Caddy hoặc Cloudflare Tunnel với tên miền của bạn (ví dụ `https://ha.example.com`).
2. **Điều hướng DNS nội bộ (Local DNS Rewrite)**:
   - Trong AdGuard Home, Pi-hole hoặc cấu hình DNS trên Router, thêm một bản ghi điều hướng:
     ```text
     ha.example.com  ->  <Địa_chỉ_IP_nội_bộ_của_Home_Assistant_hoặc_Reverse_Proxy>
     ```
   - Khi điện thoại kết nối vào Wi-Fi nhà, nó sẽ truy cập trực tiếp tới Reverse Proxy nội bộ qua HTTPS có chứng chỉ hợp lệ.
3. **Cấu hình trên ứng dụng Home Assistant Companion**:
   - Vào Cài đặt ứng dụng > Kết nối:
     - **Địa chỉ URL Home Assistant**: `https://ha.example.com`
     - **Địa chỉ URL kết nối nội bộ**: `https://ha.example.com`
     - **Tên mạng Wi-Fi gia đình (SSID)**: Chọn mạng Wi-Fi nhà bạn.

---

## 3. Giữ cổng HTTP 8123 nội bộ cho Home Assistant

Các thiết bị loa thông minh ESPHome trong mạng LAN không thể tự xác thực chứng chỉ SSL công cộng.

- Đảm bảo trong phần cấu hình mạng của Home Assistant (**Cài đặt** > **Hệ thống** > **Mạng**), mục **Mạng nội bộ** (Internal URL) được bật tự động hoặc trỏ về:
  ```text
  http://<IP_LAN>:8123
  ```
- Voice Broadcast sẽ tự động nhận diện địa chỉ HTTP nội bộ này để gửi lệnh phát trực tiếp cho loa:
  ```text
  http://<IP_LAN>:8123/api/voice_broadcast/recording/<TOKEN>.wav
  ```

---

## 4. Tùy chỉnh `client_max_body_size` trên Nginx

Mặc định Nginx giới hạn kích thước tệp tải lên là 1 MB. Một đoạn ghi âm từ 30 đến 60 giây có thể đạt dung lượng từ 1.5 đến 3 MB. Nếu Nginx chặn, bạn sẽ gặp lỗi HTTP 413 (*Payload Too Large*).

Hãy tăng giới hạn dung lượng tải lên và kích hoạt hỗ trợ WebSocket trong cấu hình Nginx:

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
