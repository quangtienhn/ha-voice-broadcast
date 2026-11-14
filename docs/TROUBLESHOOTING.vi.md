# Cẩm nang gỡ lỗi & Xử lý sự cố

[English](./TROUBLESHOOTING.md) | **Tiếng Việt**

Tài liệu này tổng hợp các tình huống sự cố thường gặp và quy trình xử lý chi tiết cho Voice Broadcast.

---

## 1. Vấn đề bộ nhớ đệm (Cache) giao diện

**Hiện tượng**: Thẻ bảng điều khiển hiển thị phiên bản cũ, thiếu nút mới hoặc không tìm thấy thẻ sau khi cập nhật.

**Cách xử lý**:
- **Trình duyệt máy tính**: Nhấn `Ctrl + F5` (hoặc `Cmd + Shift + R` trên macOS) để tải lại toàn bộ tài nguyên.
- **Ứng dụng Companion**: Vào **Cài đặt** > **Ứng dụng Companion** > **Gỡ lỗi** > **Xóa bộ nhớ đệm giao diện**, sau đó khởi động lại ứng dụng.

---

## 2. Lỗi "Ghi âm cần kết nối bảo mật (HTTPS)"

**Hiện tượng**: Thẻ thông báo tính năng ghi âm yêu cầu HTTPS hoặc localhost.

**Nguyên nhân**: Trình duyệt web chặn quyền truy cập micro trên các trang HTTP thông thường để đảm bảo quyền riêng tư.

**Cách xử lý**:
- Truy cập Home Assistant qua đường dẫn HTTPS hoặc địa chỉ `http://localhost:8123`.
- Xem hướng dẫn chi tiết tại [Tài liệu cấu hình mạng HTTPS & LAN](./HTTPS_LAN.vi.md).

---

## 3. Lỗi "no_internal_url"

**Hiện tượng**: Khi ghi âm xong và gửi, hệ thống báo lỗi `no_internal_url`.

**Nguyên nhân**: Tích hợp không tìm thấy địa chỉ HTTP nội bộ của Home Assistant trong mạng LAN để gửi cho loa tải file âm thanh.

**Cách xử lý**:
- Vào **Cài đặt** > **Hệ thống** > **Mạng**.
- Tại phần **Home Assistant URL**, đảm bảo đã bật **Tự động** hoặc điền địa chỉ **Mạng nội bộ** (Local Network) dạng `http://<IP_LAN>:8123`.

---

## 4. Lỗi HTTP 413 trên Reverse Proxy (Payload Too Large)

**Hiện tượng**: Ghi âm không gửi được khi truy cập qua Nginx Proxy Manager hoặc các hệ thống Reverse Proxy khác.

**Nguyên nhân**: Nginx mặc định chỉ cho phép tệp tải lên tối đa 1 MB, trong khi file ghi âm âm thanh có thể lên tới 2–3 MB.

**Cách xử lý**:
- Thêm dòng `client_max_body_size 10m;` vào cấu hình Nginx. Xem chi tiết tại [Tài liệu HTTPS & LAN](./HTTPS_LAN.vi.md).

---

## 5. Tên thực thể bị thừa tiền tố tên thiết bị

**Hiện tượng**: Khi xem trên các thẻ entities mặc định, tên hiển thị thành *"Voice Broadcast Loa Phòng Khách"*.

**Nguyên nhân & Cách khắc phục**:
- Home Assistant mặc định tự động ghép tên thiết bị vào đầu tên thực thể.
- Thẻ chuyên dụng `custom:voice-broadcast-card` đã được tích hợp bộ lọc tự động cắt bỏ tiền tố này, giúp tên hiển thị luôn ngắn gọn và thẩm mỹ.

---

## 6. Nút TALK và cảnh báo "Chưa có pipeline Assist"

**Hiện tượng**: Thẻ ẩn nút TALK hoặc có cảnh báo trong mục Sửa chữa (Repairs) về việc chưa có pipeline dùng agent Voice Broadcast.

**Nguyên nhân**:
- Thẻ mặc định dùng cơ chế tự động tìm kiếm pipeline (`assist_pipeline_id: "auto"`). Nếu chưa có pipeline nào được chỉ định, nút TALK sẽ ẩn để tránh phát thanh nhầm tới tất cả các loa thông minh trong nhà.

**Cách xử lý**:
1. Vào **Cài đặt** > **Trợ lý giọng nói** > **Thêm trợ lý**.
2. Đặt tên (ví dụ: *Voice Broadcast*).
3. Mục **Đạo lý trò chuyện** (Conversation agent), chọn **Voice Broadcast**.
4. Chọn engine STT và TTS mong muốn.
5. Lưu lại (lưu ý: **không** đặt làm trợ lý mặc định cho toàn bộ nhà).
6. Tải lại trang bảng điều khiển.

---

## 7. Các loa không chọn nhưng vẫn phát âm thanh

**Hiện tượng**: Loa đang ở trạng thái tắt trên thẻ nhưng vẫn phát tiếng khi thông báo.

**Quy trình kiểm tra**:
1. Vào Công cụ nhà phát triển > Dịch vụ, gọi `voice_broadcast.debug_selection` để xem trạng thái loa được nhận diện.
2. Bật đúng một loa trên thẻ.
3. Gọi dịch vụ `voice_broadcast.speak` với tùy chọn `audit: true` và so sánh danh sách `targeted` với `unexpected_started`.
4. Nếu `targeted` chỉ có duy nhất loa đã chọn và `unexpected_started` trống, hãy kiểm tra Nhật ký (Logbook) của Home Assistant để tìm các tự động hóa (automation) hoặc script của bên thứ ba đang kích hoạt đồng thời.
