# Báo cáo tiến độ tuần 6

## Phạm vi

Tuần 6 tập trung hoàn thiện kiểm thử giao diện, kiểm tra tích hợp PostgreSQL,
mở rộng kiểm thử các chức năng P3 và ghi nhận kết quả triển khai. Phần liên
kết tài khoản giảng viên với mã giảng viên trong CSV được giữ lại cho tuần sau.

## Kết quả đã thực hiện

- Migration PostgreSQL đã chạy thật từ `20260810_0006` lên
  `20260813_0007 (head)` trên database `timetable_ga`.
- Đã xác nhận các bảng `schedule_change_requests`,
  `schedule_change_request_events` và liên kết audit tồn tại.
- Đã cài Playwright và Chromium, thêm script `npm run test:e2e` có tự khởi
  động và dừng web server.
- Đã viết E2E cho đăng nhập, cổng giảng viên, lịch sử/hủy yêu cầu, luồng
  Phòng Đào tạo kiểm tra-phê duyệt-áp dụng, lọc/xuất kết quả và công cụ ngày
  nghỉ, phân đoạn, buổi học bù.
- Đã bổ sung kiểm tra export XLSX ở backend.

## Kết quả kiểm thử

```text
Backend: 67 passed
Frontend build: passed
Playwright E2E: 4 passed
Alembic: 20260813_0007 (head)
```

## Việc chuyển sang tuần sau

- Liên kết và quản lý tài khoản giảng viên theo `lecturer_code` trên dữ liệu
  CSV với quy trình vận hành đầy đủ.
- Mở rộng E2E cho upload/preview CSV, chạy GA và tạo makeup thực tế qua API.
- Bổ sung PostgreSQL integration test tự động trong pipeline CI nếu môi trường
  CI có PostgreSQL service.
