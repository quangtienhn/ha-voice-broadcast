# Chuyển từ TTS Broadcast

[English](./MIGRATION.md) | **Tiếng Việt**

Voice Broadcast thay thế integration **TTS Broadcast** trước đây. Bản mới giữ nguyên
tính năng cũ và thêm chuyển tiếp giọng nói (ghi âm trên card, phát, xóa). Đây là một
integration khác, không phải bản nâng cấp tại chỗ:

| Mục | TTS Broadcast | Voice Broadcast |
|-----|---------------|-----------------|
| Domain / thư mục | `tts_broadcast` | `voice_broadcast` |
| Dịch vụ | `tts_broadcast.*` | `voice_broadcast.*` |
| Loại card | `custom:tts-broadcast-card` | `custom:voice-broadcast-card` |
| File card | `tts-broadcast-card.js` | `voice-broadcast-card.js` |
| Repository | repository cũ | `ha-voice-broadcast` |
| Phiên bản | 1.2.1 | 0.2.0 |

Home Assistant tạo entity id từ tên thiết bị và entity mới, nên chúng sẽ không giống hệt
bản cũ. Hãy cập nhật dashboard, script và automation đang dùng entity hoặc dịch vụ cũ.

## Trước khi bắt đầu

1. Sao lưu: Settings -> System -> Backups -> Create backup.
2. Ghi lại loa, TTS entity, âm lượng và cấu hình cụm từ của integration cũ.
3. Giữ integration cũ cho đến khi cấu hình và kiểm tra xong bản mới. Hai bản có thể chạy
   song song.

## Cài Voice Broadcast

### Cài thủ công

1. Sao chép `custom_components/voice_broadcast` vào
   `config/custom_components/voice_broadcast`.
2. Khởi động lại Home Assistant.
3. Settings -> Devices & Services -> Add integration -> **Voice Broadcast**.

### HACS

Thêm repository vào HACS dưới dạng custom repository: HACS -> Integrations -> Custom
repositories -> `https://github.com/quangtienhn/ha-voice-broadcast`, danh mục
"Integration". Nếu gặp lỗi, hãy dùng cách cài thủ công ở trên.

## Nhập cấu hình cũ (chỉ đọc)

Khi đã có entry `tts_broadcast`, màn hình thiết lập đầu tiên sẽ mời **Nhập từ TTS
Broadcast**:

- **Nhập cấu hình** sao chép loa, TTS entity, âm lượng ban đầu, ngôn ngữ, tùy chọn và
  cấu hình cụm từ vào form. Hãy xem lại rồi gửi.
- Bỏ chọn để bắt đầu với form trống.

Bước nhập chỉ đọc entry cũ. Nó không sửa, không tắt và không xóa entry đó, cũng không
sao chép entity id, dashboard hay automation. Chỉ nhập được khi entry cũ còn tồn tại.

## Chuyển dashboard và automation

1. Thêm card mới vào một dashboard thử nghiệm:

   ```yaml
   type: custom:voice-broadcast-card
   ```

2. Kiểm tra công tắc từng loa, âm lượng, tin nhắn, Phát/Dừng và hàng TALK.
3. Thay `tts_broadcast.speak` bằng `voice_broadcast.speak`, và `tts_broadcast.stop` bằng
   `voice_broadcast.stop`, trong script và automation.
4. Thay entity id cũ trong dashboard/automation bằng entity id mới trong Settings ->
   Devices & Services -> Voice Broadcast.
5. Nếu dùng blueprint cũ, hãy nhập blueprint mới từ
   `blueprints/automation/voice_broadcast/voice_announce.yaml`.
6. Kiểm tra pipeline Assist: tạo hoặc sửa để conversation agent là **Voice Broadcast**,
   rồi trỏ card vào pipeline đó (hoặc để `assist_pipeline_id: auto`). Đừng đặt làm
   pipeline mặc định.

## Thử chuyển tiếp giọng nói

1. Mở card mới qua HTTPS hoặc `localhost`.
2. Bấm **Ghi âm**, cho phép micro, nói, rồi bấm **Dừng ghi âm**.
3. Đoạn ghi phát trên các loa đang bật. Bấm **Xóa bản ghi** để hủy.
4. Đọc mục chuyển tiếp giọng nói trong `README.vi.md` để biết giới hạn và cách xử lý.

## Gỡ integration cũ

Chỉ sau khi đã kiểm tra xong bản mới:

1. Settings -> Devices & Services -> TTS Broadcast -> Delete.
2. Xóa `config/custom_components/tts_broadcast`.
3. Gỡ card cũ (`custom:tts-broadcast-card`) khỏi dashboard.
4. Gỡ các lệnh gọi `tts_broadcast.*` trong script và automation.
5. Khởi động lại Home Assistant.

Xóa integration cũ sẽ xóa entity và thiết bị của nó. Việc này không ảnh hưởng bản mới
hay các bản ghi trong `config/voice_broadcast_tmp/`.

## Quay lại bản cũ

Có thể quay lại khi integration cũ vẫn còn: tắt hoặc gỡ entry mới, khôi phục card cũ và
trỏ automation về `tts_broadcast.*`. Không có chuyển dữ liệu tự động theo chiều nào; cấu
hình chỉ được sao chép qua bước nhập chỉ đọc.

## Lỗi thường gặp

| Hiện tượng | Nguyên nhân / cách xử lý |
|------------|--------------------------|
| Không thấy bước nhập | Không có entry `tts_broadcast`, hoặc entry mới đã được cấu hình. |
| Automation cũ gọi dịch vụ không còn | Vẫn dùng `tts_broadcast.*`; đổi sang `voice_broadcast.*`. |
| Không thấy card | Dùng `custom:voice-broadcast-card` rồi tải lại trang (hard refresh). |
| Cả hai integration cùng trả lời Assist | Có hai pipeline hoặc hai conversation agent khớp; chỉ giữ một pipeline cho thông báo. |
| Loa thông báo hai lần | Cả hai integration (hoặc gói YAML cũ) cùng xử lý một nội dung; gỡ bản trùng. |
| HACS không thêm được repository | Thêm bằng custom repositories trong HACS, hoặc cài thủ công. |
