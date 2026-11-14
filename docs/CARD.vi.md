# Thẻ bảng điều khiển (`custom:voice-broadcast-card`)

[English](./CARD.md) | **Tiếng Việt**

Tích hợp đi kèm với một thẻ Lovelace tùy chỉnh (`voice-broadcast-card.js`) tự động nhận diện các thực thể của tích hợp và cung cấp giao diện phát thanh toàn diện.

---

## Tính năng nổi bật

- **Khung gọn gàng & danh sách loa thu gọn**: Hiển thị trạng thái các loa nhỏ gọn, có thể bấm mở rộng.
- **Thanh trượt âm lượng chung**: Điều khiển mức âm lượng đồng bộ cho các loa được bật.
- **Nút micro bấm để ghi âm**: Ghi âm giọng nói trực tiếp và phát ra loa qua Voice Relay.
- **Ô nhập tin nhắn TTS**: Nhập văn bản để đọc thông báo bằng giọng đọc nhân tạo.
- **Hàng nút Assist TALK**: Kích hoạt trợ lý ảo Assist của Home Assistant với khả năng tự chọn pipeline (`assist_pipeline_id: "auto"`).
- **Tự động lược bỏ tiền tố tên thiết bị**: Rút gọn tên thực thể giúp giao diện trực quan, dễ nhìn.

---

## Các tùy chọn cấu hình thẻ

| Tùy chọn | Kiểu dữ liệu | Mặc định | Mô tả |
|---|---|---|---|
| `type` | string | **Bắt buộc** | Phải là `custom:voice-broadcast-card`. |
| `title` | string | `"Voice Broadcast"` | Tiêu đề tùy chỉnh ở đầu thẻ. |
| `show_volume` | boolean | `true` | Bật/tắt thanh trượt âm lượng chung. |
| `show_message` | boolean | `true` | Bật/tắt ô gõ văn bản và nút Phát TTS. |
| `show_assist` | boolean | `true` | Bật/tắt hàng nút Assist TALK. |
| `show_record` | boolean | `true` | Bật/tắt cụm micro ghi âm Voice Relay. |
| `show_select_buttons` | boolean | `true` | Bật/tắt các nút Chọn tất cả / Bỏ chọn tất cả. |
| `assist_pipeline_id` | string | `"auto"` | `"auto"`, `"preferred"`, `"last_used"`, hoặc ID cụ thể của một pipeline. |
| `assist_name` | string | theo ngôn ngữ | Đổi nhãn chữ trên nút TALK. |
| `assist_icon` | string | `"mdi:microphone"` | Đổi biểu tượng icon trên nút TALK. |
| `max_record_seconds` | number | theo server | Giới hạn tối đa thời gian ghi âm phía trình duyệt (5–60 giây). |

---

## Ví dụ cấu hình YAML

### Cấu hình mặc định cơ bản

```yaml
type: custom:voice-broadcast-card
```

### Cấu hình tùy biến nâng cao

```yaml
type: custom:voice-broadcast-card
title: "Phát thanh gia đình"
show_volume: true
show_record: true
show_message: true
show_assist: true
assist_pipeline_id: "auto"
assist_name: "Nói"
max_record_seconds: 30
```

---

## Mẹo làm mới bộ nhớ đệm (Cache)

Khi cập nhật phiên bản mới của thẻ, trình duyệt hoặc ứng dụng Companion có thể vẫn lưu trữ file script cũ.

- **Trên trình duyệt máy tính**: Nhấn tổ hợp phím `Ctrl + F5` (hoặc `Cmd + Shift + R` trên macOS) để xóa bộ nhớ đệm và tải lại trang.
- **Trên ứng dụng Companion (Android / iOS)**:
  - Vào **Cài đặt** > **Ứng dụng Companion** > **Gỡ lỗi** > **Xóa bộ nhớ đệm giao diện** (Reset frontend cache).
  - Hoặc đóng hẳn ứng dụng và mở lại.
