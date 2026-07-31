# Báo Cáo Tiến Độ Tuần 3

## 1. Thông Tin Chung

Đề tài: Ứng dụng lập thời khóa biểu giảng dạy sử dụng thuật toán di truyền.

Thời gian báo cáo: Tuần 3, từ 20/07/2026 đến 26/07/2026.

Trọng tâm tuần này là hoàn thiện phần nền của hệ thống trước khi phát triển giao diện và các chức năng đầy đủ:

- Chuẩn hóa dữ liệu đầu vào CSV.
- Xây dựng module đọc và kiểm tra dữ liệu.
- Xây dựng kiểm tra ràng buộc cứng.
- Tạo bản thử nghiệm GA v0.1.
- Thiết kế model cơ sở dữ liệu cốt lõi.
- Làm rõ xử lý lịch học kỳ và ngày lễ.

## 2. Nội Dung Đã Thực Hiện

### 2.1. Cập Nhật Bộ CSV Mẫu

Em đã chuẩn hóa lại bộ CSV mẫu trong thư mục:

```text
data/samples/small
```

Bộ dữ liệu mẫu hiện gồm 7 file:

```text
lecturers.csv
rooms.csv
time_slots.csv
course_sections.csv
lecturer_time_preferences.csv
room_unavailable_slots.csv
academic_calendar.csv
```

Các file CSV dùng UTF-8 và có dữ liệu tiếng Việt có dấu để kiểm tra khả năng hiển thị sau này trên web.

Dữ liệu mẫu hiện có:

- 4 giảng viên.
- 5 phòng học.
- 9 khung giờ hợp lệ.
- 5 lớp học phần.
- 4 dòng dữ liệu giảng viên không khả dụng hoặc không ưu tiên.
- 2 dòng dữ liệu phòng không khả dụng.
- 14 dòng lịch học kỳ, trong đó có ngày không học để kiểm tra xử lý ngày lễ.

### 2.2. Làm Rõ Mô Hình Lớp Học Phần

Em đã thiết kế dữ liệu theo hướng:

```text
Một môn học có thể có nhiều lớp học phần.
Một giảng viên có thể dạy nhiều lớp học phần.
Nhiều giảng viên có thể dạy cùng một môn, nhưng ở các lớp học phần khác nhau.
Thuật toán GA không phân công giảng viên, mà chỉ xếp ngày, khung giờ và phòng học.
```

Trong `course_sections.csv`, dữ liệu được tách rõ:

```text
course_code
course_name
section_code
lecturer_code
```

Vì vậy hệ thống xếp lịch theo `section_code`, không xếp trực tiếp theo `course_code`.

### 2.3. Xây Dựng Domain Models

Em đã tạo các model dữ liệu nghiệp vụ trong backend, gồm:

- `Lecturer`
- `Room`
- `TimeSlot`
- `CourseSection`
- `ScheduleAssignment`
- `AcademicCalendarDate`
- `ScheduleOccurrence`
- `SkippedHolidaySession`

Các model này là dữ liệu đã được chuẩn hóa sau khi đọc CSV, dùng chung cho validator, kiểm tra ràng buộc và GA.

### 2.4. Xây Dựng CSV Validator

Em đã xây dựng module đọc và kiểm tra CSV.

Module này kiểm tra được:

- Thiếu file CSV bắt buộc.
- Thiếu cột bắt buộc.
- File CSV phải đọc được bằng UTF-8.
- Trùng mã lớp học phần.
- Mã giảng viên không tồn tại.
- Mã phòng hoặc mã khung giờ không tồn tại.
- Loại lớp không hợp lệ.
- Loại phòng yêu cầu không hợp lệ.
- Số lượng sinh viên dùng để xếp lịch phải đúng quy tắc ưu tiên.
- Mỗi lớp học phần phải có ít nhất một khung giờ và phòng học khả thi.

Quy tắc tính số lượng sinh viên xếp lịch:

```text
scheduling_student_count =
  approved_max_students
  nếu không có thì dùng initial_registration_limit
  nếu không có thì dùng expected_students
```

### 2.5. Xây Dựng Kiểm Tra Ràng Buộc Cứng

Em đã xây dựng module kiểm tra ràng buộc cứng dùng chung cho GA và các chức năng chỉnh sửa lịch sau này.

Các ràng buộc hiện đã kiểm tra:

- Một giảng viên không được dạy hai lớp trùng thời gian.
- Một phòng không được có hai lớp trùng thời gian.
- Mỗi lớp học phần phải có một lịch học cơ bản.
- Khung giờ phải tồn tại và đang được kích hoạt.
- Khung giờ phải phù hợp với loại lớp và số tiết.
- Phòng phải đúng loại phòng yêu cầu.
- Phòng phải đủ sức chứa.
- Phòng không được xếp vào ca không khả dụng.
- Giảng viên không được xếp vào ca bận bắt buộc.
- Các tham chiếu lớp học phần, phòng, khung giờ phải tồn tại.

Đặc biệt, kiểm tra trùng lịch dùng khoảng tiết thực tế, không chỉ so sánh mã khung giờ.

Ví dụ:

```text
Tiết 1-5 và tiết 2-6 được xem là trùng nhau.
```

### 2.6. Sinh Miền Gán Lịch Khả Thi

Em đã xây dựng module sinh miền gán lịch khả thi cho từng lớp học phần.

Ý tưởng:

```text
Với mỗi lớp học phần, hệ thống tạo danh sách các tổ hợp phòng và khung giờ có thể dùng.
Những tổ hợp chắc chắn sai sẽ bị loại trước khi đưa vào GA.
```

Các trường hợp bị loại trước:

- Slot không phù hợp loại lớp hoặc số tiết.
- Phòng sai loại.
- Phòng không đủ sức chứa.
- Phòng không khả dụng.
- Giảng viên bận bắt buộc ở slot đó.
- Phòng không khả dụng ở slot đó.

### 2.7. Xây Dựng GA v0.1

Em đã tạo bản GA v0.1 để chạy thử trên dữ liệu nhỏ.

Ở phiên bản hiện tại:

- Một gene tương ứng với một lớp học phần.
- Gene chọn `room_code` và `slot_code`.
- Giảng viên và lớp học phần là dữ liệu cố định.
- GA nhận dữ liệu đã validate, không đọc CSV trực tiếp.
- GA không truy cập database.
- Có `seed` để kết quả có thể tái lập.

GA v0.1 hiện là bản nền đơn giản, chủ yếu để kiểm chứng pipeline:

```text
CSV -> validation -> feasible domains -> GA v0.1 -> kết quả lịch
```

Phiên bản này chưa triển khai đầy đủ selection, crossover và mutation phức tạp.

### 2.8. Xử Lý Lịch Học Kỳ Và Ngày Lễ

Em đã bổ sung `academic_calendar.csv` để làm rõ rằng thời khóa biểu được lập trước khi sinh viên đăng ký môn học.

GA chỉ tạo lịch cơ bản hằng tuần. Sau đó hệ thống dùng lịch học kỳ để mở rộng thành từng buổi học theo ngày cụ thể.

Quy tắc ngày lễ:

```text
Nếu buổi học rơi vào ngày lễ hoặc ngày không học:
- Không sinh buổi học bình thường.
- Không tự động dời sang ngày khác.
- Không hiển thị là SUSPENDED.
- Ghi nhận để sau này Phòng Đào tạo có thể xếp buổi học bù nếu cần.
```

Em đã tạo service mở rộng lịch cơ bản thành các buổi học theo ngày và test trường hợp ngày lễ không sinh buổi học.

### 2.9. Thiết Kế SQLAlchemy Models Cho Database

Em đã tạo model cơ sở dữ liệu bằng SQLAlchemy.

Các bảng cốt lõi hiện có:

```text
import_batches
lecturers
rooms
time_slots
course_sections
ga_runs
schedule_assignments
academic_terms
academic_calendar_dates
schedule_occurrences
```

Lưu ý: đây mới là lớp thiết kế bảng bằng code. PostgreSQL thật, migration và service lưu dữ liệu sẽ được triển khai ở bước sau.

### 2.10. CLI Demo

Em đã tạo lệnh chạy thử pipeline từ CSV đến kết quả lịch.

Lệnh chạy:

```powershell
python -m backend.app.cli.run_ga --data-dir data/samples/small --population-size 80 --generations 200 --seed 42
```

Lệnh chạy có mở rộng theo lịch học kỳ:

```powershell
python -m backend.app.cli.run_ga --data-dir data/samples/small --population-size 80 --generations 200 --seed 42 --show-occurrences
```

Kết quả chạy thử hiện tại tìm được lịch hợp lệ với:

```text
hard_violation_count=0
```

## 3. Kiểm Thử Đã Thực Hiện

Em đã viết test tự động cho các phần:

- CSV validation.
- Hard constraint checker.
- Feasible assignment generation.
- GA v0.1.
- SQLAlchemy database models.
- Calendar expansion và xử lý ngày lễ.

Lệnh chạy toàn bộ test:

```powershell
python -m unittest discover backend\tests
```

Kết quả hiện tại:

```text
Ran 32 tests
OK
```

## 4. Kết Quả Đạt Được

Trong tuần 3, em đã hoàn thành vượt mức phần thiết kế nền và có prototype backend chạy được.

Pipeline hiện tại:

```text
CSV mẫu
-> đọc và validate dữ liệu
-> chuẩn hóa thành domain models
-> kiểm tra ràng buộc cứng
-> sinh miền gán lịch khả thi
-> chạy GA v0.1
-> sinh lịch cơ bản
-> mở rộng theo lịch học kỳ, bỏ qua ngày lễ
```

Điểm quan trọng là các module nghiệp vụ được tách khỏi giao diện, API và database để sau này có thể tái sử dụng cho:

- GA.
- Chỉnh sửa lịch thủ công.
- Duyệt yêu cầu đổi lịch của giảng viên.
- Kiểm tra dữ liệu import.

## 5. Hạn Chế Hiện Tại

Các phần hiện chưa làm:

- Chưa có giao diện web.
- Chưa có API upload CSV.
- Chưa kết nối PostgreSQL thật.
- Chưa có Alembic migration.
- GA v0.1 chưa có đầy đủ selection, crossover, mutation và repair.
- Chưa lưu kết quả GA vào database thật.
- Chưa có chức năng export CSV/Excel.
- Chưa có màn hình giảng viên gửi yêu cầu đổi lịch.

## 6. Kế Hoạch Tiếp Theo

Các bước tiếp theo nên làm:

1. Tạo service lưu dữ liệu CSV đã validate vào database models.
2. Dựng PostgreSQL và migration bằng Alembic.
3. Tạo API import/preview/validate CSV.
4. Nâng cấp GA từ v0.1 sang v0.2 với selection, crossover, mutation.
5. Bổ sung chấm điểm mềm theo nguyện vọng giảng viên.
6. Chuẩn bị API chạy GA và trả kết quả lịch cho frontend.

## 7. Nội Dung Có Thể Trình Bày Ngắn Gọn Với Giảng Viên Hướng Dẫn

Trong tuần 3, em tập trung xây dựng phần nền cho hệ thống lập thời khóa biểu. Em đã chuẩn hóa lại bộ CSV mẫu theo UR/SRS cập nhật, xây dựng module đọc và kiểm tra CSV, tạo các domain model cho giảng viên, phòng học, khung giờ và lớp học phần. Em cũng đã xây dựng module kiểm tra ràng buộc cứng như trùng giảng viên, trùng phòng, sai loại phòng, thiếu sức chứa, sai khung giờ và giảng viên/phòng không khả dụng.

Ngoài ra, em đã xây dựng module sinh miền gán lịch khả thi và một bản GA v0.1 để kiểm chứng pipeline từ dữ liệu CSV đến kết quả lịch. Hệ thống hiện có thể chạy thử bằng command line và sinh được lịch hợp lệ trên bộ dữ liệu nhỏ với `hard_violation_count=0`.

Em cũng đã bổ sung phần lịch học kỳ để xử lý trường hợp ngày lễ. Khi một buổi học rơi vào ngày lễ hoặc ngày không học, hệ thống không sinh buổi học bình thường, không tự động dời lịch và ghi nhận để sau này Phòng Đào tạo có thể xếp bù nếu cần.

Về database, em đã thiết kế các SQLAlchemy models cốt lõi như giảng viên, phòng học, khung giờ, lớp học phần, lần chạy GA, lịch cơ bản và buổi học theo ngày. PostgreSQL thật và migration sẽ được triển khai ở bước tiếp theo.
