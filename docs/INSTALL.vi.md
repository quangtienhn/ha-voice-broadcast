# Hướng dẫn cài đặt Voice Broadcast

[English](./INSTALL.md) | **Tiếng Việt**

Bạn có thể cài đặt Voice Broadcast thông qua HACS (khuyến nghị sau khi kho lưu trữ được mở công khai) hoặc cài đặt thủ công bằng cách sao chép thư mục.

---

## Cách 1: Qua HACS (Khuyến nghị)

> **Lưu ý:** HACS yêu cầu kho lưu trữ ở chế độ công khai (public). Nếu kho lưu trữ đang ở chế độ riêng tư, hãy dùng Cách 2 (Cài đặt thủ công).

1. Trong Home Assistant, vào **HACS** > **Integrations**.
2. Bấm vào biểu tượng ba chấm ở góc trên bên phải, chọn **Custom repositories**.
3. Nhập đường dẫn kho lưu trữ:
   ```text
   https://github.com/quangtienhn/ha-voice-broadcast
   ```
4. Chọn **Category** là **Integration** rồi bấm **Add**.
5. Tìm kiếm **Voice Broadcast** trong HACS và bấm **Download**.
6. Khởi động lại Home Assistant: **Cài đặt** > **Hệ thống** > **Khởi động lại**.
7. Thêm tích hợp: **Cài đặt** > **Thiết bị & Dịch vụ** > **Thêm tích hợp** > tìm **Voice Broadcast**.

---

## Cách 2: Cài đặt thủ công

1. Tải về hoặc sao chép kho lưu trữ này.
2. Sao chép thư mục `custom_components/voice_broadcast` vào thư mục `custom_components/` trong thư mục cấu hình của Home Assistant:
   ```text
   config/custom_components/voice_broadcast/
   ```
3. Đảm bảo cấu trúc thư mục như sau:
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
4. Khởi động lại Home Assistant hoàn toàn.
5. Vào **Cài đặt** > **Thiết bị & Dịch vụ** > **Thêm tích hợp**.
6. Tìm kiếm **Voice Broadcast** và làm theo hướng dẫn thiết lập.
