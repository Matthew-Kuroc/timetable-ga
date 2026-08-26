# Tiến độ Tuần 9

Ngày cập nhật: 26/08/2026

Tài liệu này ghi nhận các công việc triển khai sau khi mốc Tuần 8 đã kết thúc. Không dùng tài liệu này để thay đổi hoặc hồi tố kết quả nghiệm thu Tuần 8.

## Công việc đã hoàn thành trong phiên Tuần 9

- Thêm migration `20260826_0011_password_lifecycle` với cờ `must_change_password`.
- Bổ sung đổi mật khẩu lần đầu, đổi mật khẩu khi đã đăng nhập, cấp lại mật khẩu Lecturer bởi Administrator, thu hồi session và audit `PASSWORD_RESET_BY_ADMIN`.
- Bổ sung cấp tài khoản Lecturer hàng loạt từ catalog batch đã xác nhận, hỗ trợ cấp theo mã, cấp toàn bộ và `--dry-run`.
- Bổ sung giao diện Admin cho cấp tài khoản, hiển thị mật khẩu tạm một lần và cấp lại mật khẩu.
- Tạo generator dữ liệu tổng hợp có seed tại `backend/app/cli/generate_synthetic_scale_data.py`.
- Đã sinh và validate thành công batch 600 giảng viên, 3.000 lớp, 150 phòng; trong đó có 600 lớp hai meeting.
- Thêm benchmark harness tại `backend/app/cli/benchmark_synthetic_scale.py`.
- Bổ sung `time_limit_seconds`, progress callback, cancellation callback, trạng thái `STOPPED`, stop reason và best-so-far cho GA.
- Bổ sung dừng ngay trong giai đoạn xây miền khả thi để giới hạn thời gian áp dụng cho cả tiền xử lý.

## Kiểm thử sau thay đổi

- Backend: `82 passed, 2 skipped`.
- Frontend build: thành công.
- Playwright mock E2E: `6 passed`.
- Batch tổng hợp: CSV validator hợp lệ.
- Stress harness với giới hạn 0,1 giây: dừng trong khoảng 0,1 giây với `STOPPED/TIME_LIMIT`.

## Việc còn lại của Tuần 9

- Chạy migration trên PostgreSQL rehearsal và chạy lại real E2E.
- Thiết kế worker/background execution và endpoint hủy GA từ giao diện; hiện core đã hỗ trợ callback dừng nhưng API vẫn chạy đồng bộ.
- Tối ưu miền assignment trước khi chạy GA đầy đủ trên 3.000 lớp.
- Ghi runtime, bộ nhớ, số gene, số occurrence và best-so-far của bài stress sau khi tối ưu.
