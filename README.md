# Ứng dụng lập thời khóa biểu giảng dạy sử dụng thuật toán Di truyền

## Teaching Timetable Scheduling Application Using Genetic Algorithm

Ứng dụng web hỗ trợ tự động lập thời khóa biểu giảng dạy tại trường đại học bằng thuật toán Di truyền — Genetic Algorithm.

---

## 1. Thông tin đề tài

- **Tên đề tài:** Xây dựng ứng dụng lập thời khóa biểu giảng dạy sử dụng thuật toán Di truyền
- **Tên tiếng Anh:** Teaching Timetable Scheduling Application Using Genetic Algorithm
- **Loại dự án:** Dự án thực tập chuyên ngành Công nghệ phần mềm
- **Đơn vị:** Trường Đại học Công Thương Thành phố Hồ Chí Minh
- **Giảng viên hướng dẫn:** Th.S Đinh Nguyễn Trọng Nghĩa
- **Trạng thái:** Đang phân tích yêu cầu và khởi tạo dự án
- **Repository:** `timetable-ga`

---

## 2. Giới thiệu

Việc xây dựng thời khóa biểu giảng dạy trong trường đại học là một bài toán tối ưu phức tạp.

Một phương án thời khóa biểu hợp lệ cần đồng thời xem xét nhiều yếu tố:

- Phân công giảng viên.
- Danh sách lớp học phần.
- Số buổi và số tiết cần giảng dạy.
- Loại phòng học.
- Sức chứa phòng.
- Khung thời gian được phép sử dụng.
- Lịch bận của giảng viên.
- Thời gian phòng học không thể sử dụng.
- Nguyện vọng giảng dạy.
- Các yêu cầu điều chỉnh lịch phát sinh.

Khi số lượng giảng viên, lớp học phần, phòng học và khung thời gian tăng lên, việc lập lịch bằng phương pháp thủ công trở nên khó khăn, mất nhiều thời gian và dễ phát sinh xung đột.

Dự án này xây dựng một ứng dụng web cho phép Phòng đào tạo nhập dữ liệu, cấu hình thuật toán và tự động tạo thời khóa biểu bằng Genetic Algorithm.

Hệ thống cũng hỗ trợ:

- Kiểm tra tính hợp lệ của dữ liệu đầu vào.
- Hiển thị thời khóa biểu theo nhiều góc nhìn.
- Cho phép giảng viên xem lịch cá nhân theo tuần.
- Gửi và xử lý yêu cầu điều chỉnh lịch.
- Kiểm tra xung đột sau khi điều chỉnh.
- Xuất kết quả ra CSV hoặc Excel.
- Lưu lại thông tin các lần chạy thuật toán để phục vụ đánh giá thực nghiệm.

---

## 3. Mục tiêu dự án

### 3.1. Mục tiêu tổng quát

Xây dựng một ứng dụng web hỗ trợ tự động lập thời khóa biểu giảng dạy bằng thuật toán Di truyền, dựa trên dữ liệu phân công giảng viên, lớp học phần, phòng học, khung thời gian và các ràng buộc nghiệp vụ.

Hệ thống hướng đến việc tạo ra thời khóa biểu:

- Không vi phạm các ràng buộc bắt buộc.
- Hạn chế tối đa các xung đột.
- Đáp ứng hợp lý các nguyện vọng của giảng viên.
- Có thể kiểm tra, tra cứu và điều chỉnh.
- Có khả năng thử nghiệm trên nhiều quy mô dữ liệu.

### 3.2. Mục tiêu cụ thể

Dự án cần thực hiện các mục tiêu sau:

1. Phân tích và chuẩn hóa dữ liệu đầu vào.
2. Xác định các ràng buộc cứng và ràng buộc mềm.
3. Thiết kế cách biểu diễn một phương án lịch dưới dạng nhiễm sắc thể.
4. Xây dựng hàm thích nghi để đánh giá chất lượng thời khóa biểu.
5. Cài đặt các toán tử chọn lọc, lai ghép và đột biến.
6. Cho phép cấu hình các tham số của Genetic Algorithm.
7. Tạo thời khóa biểu tự động từ dữ liệu hợp lệ.
8. Phát hiện và xử lý các xung đột.
9. Hiển thị lịch theo giảng viên, phòng học và lớp học phần.
10. Cho phép giảng viên xem thời khóa biểu cá nhân theo tuần.
11. Hỗ trợ yêu cầu tạm ngưng hoặc chuyển lịch.
12. Kiểm tra lại ràng buộc trước khi áp dụng thay đổi.
13. Xuất thời khóa biểu ra CSV hoặc Excel.
14. Đánh giá thuật toán theo chất lượng lời giải và thời gian xử lý.

---

## 4. Phạm vi hệ thống

### 4.1. Trong phạm vi

Phiên bản thực tập dự kiến bao gồm:

- Ứng dụng web.
- Đăng nhập và phân quyền người dùng.
- Quản lý dữ liệu đầu vào từ file CSV.
- Xem trước dữ liệu trước khi lưu.
- Kiểm tra cấu trúc và nội dung dữ liệu.
- Chuẩn hóa dữ liệu đầu vào.
- Cấu hình tham số Genetic Algorithm.
- Chạy thuật toán lập thời khóa biểu.
- Theo dõi trạng thái chạy.
- Xem kết quả theo giảng viên.
- Xem kết quả theo phòng học.
- Xem kết quả theo lớp học phần.
- Xem thời khóa biểu cá nhân theo tuần.
- Gửi yêu cầu điều chỉnh lịch.
- Phê duyệt hoặc từ chối yêu cầu điều chỉnh.
- Kiểm tra xung đột trước khi cập nhật lịch.
- Chạy lại thuật toán để tạo phương án mới.
- Xuất dữ liệu ra CSV.
- Xuất dữ liệu ra Excel.
- Lưu lịch sử chạy và các chỉ số thực nghiệm.
- Cung cấp dữ liệu mẫu để chạy thử.

### 4.2. Ngoài phạm vi

Các nội dung sau không thuộc phạm vi chính của phiên bản thực tập:

- Sinh viên đăng ký học phần.
- Quản lý điểm sinh viên.
- Quản lý học phí.
- Quản lý hồ sơ sinh viên.
- Quản lý chương trình đào tạo đầy đủ.
- Ứng dụng di động riêng.
- Tích hợp chính thức với toàn bộ hệ thống quản lý đào tạo của trường.
- Gửi thông báo SMS hoặc email nếu chưa được bổ sung yêu cầu.
- Bảo đảm tìm được nghiệm tối ưu toàn cục cho mọi bộ dữ liệu.
- Tự động thay thế toàn bộ nghiệp vụ của Phòng đào tạo.
- Cho phép giảng viên tự thêm hoặc xóa lớp được phân công.

---

## 5. Đối tượng sử dụng

### 5.1. Phòng đào tạo hoặc người quản lý

Phòng đào tạo là tác nhân chính của hệ thống.

Quyền dự kiến:

- Đăng nhập.
- Nhập dữ liệu.
- Kiểm tra dữ liệu.
- Quản lý các đợt dữ liệu.
- Cấu hình tham số thuật toán.
- Chạy Genetic Algorithm.
- Xem toàn bộ thời khóa biểu.
- Tra cứu lịch theo giảng viên, phòng và lớp.
- Tiếp nhận yêu cầu điều chỉnh.
- Phê duyệt hoặc từ chối yêu cầu.
- Áp dụng thay đổi hợp lệ.
- Chạy lại thuật toán.
- Xuất dữ liệu.
- Xem lịch sử chạy.
- Xem kết quả thực nghiệm.

### 5.2. Giảng viên

Quyền dự kiến:

- Đăng nhập.
- Xem thời khóa biểu cá nhân.
- Xem lịch theo từng tuần.
- Xem thông tin lớp học phần.
- Gửi yêu cầu tạm ngưng một buổi học.
- Gửi yêu cầu chuyển một buổi học.
- Gửi yêu cầu chuyển toàn bộ lịch cố định khi nghiệp vụ cho phép.
- Theo dõi trạng thái yêu cầu.

Giảng viên không được:

- Tự thêm lớp học phần.
- Tự xóa lớp học phần.
- Tự từ chối lớp đã được phân công.
- Sửa lịch của giảng viên khác.
- Tự áp dụng thay đổi chưa được phê duyệt.
- Truy cập chức năng quản trị của Phòng đào tạo.

### 5.3. Quản trị kỹ thuật

Quyền dự kiến:

- Quản lý tài khoản.
- Quản lý vai trò.
- Cấu hình kỹ thuật.
- Xem log hệ thống.
- Hỗ trợ vận hành.

Quản trị kỹ thuật không mặc nhiên có quyền phê duyệt các quyết định nghiệp vụ của Phòng đào tạo.

### 5.4. Giảng viên hướng dẫn và người kiểm thử

Vai trò:

- Cung cấp dữ liệu mẫu hoặc dữ liệu thực tế.
- Kiểm tra chức năng.
- Đánh giá kết quả thuật toán.
- Góp ý và xác nhận phạm vi.
- Kiểm tra sản phẩm bàn giao.

---

## 6. Quy trình nghiệp vụ tổng quát

Quy trình dự kiến của hệ thống:

1. Phòng đào tạo chuẩn bị dữ liệu.
2. Người quản lý tải các file CSV lên hệ thống.
3. Hệ thống kiểm tra cấu trúc và nội dung dữ liệu.
4. Hệ thống hiển thị dữ liệu xem trước và danh sách lỗi.
5. Người dùng xác nhận lưu dữ liệu hợp lệ.
6. Người quản lý chọn đợt dữ liệu cần sử dụng.
7. Người quản lý cấu hình các tham số Genetic Algorithm.
8. Hệ thống chạy thuật toán và tìm kiếm phương án lịch.
9. Hệ thống lưu phương án tốt nhất cùng các chỉ số liên quan.
10. Người quản lý xem kết quả theo nhiều góc nhìn.
11. Giảng viên đăng nhập và xem lịch cá nhân.
12. Giảng viên gửi yêu cầu điều chỉnh khi cần.
13. Hệ thống kiểm tra các xung đột liên quan.
14. Phòng đào tạo phê duyệt hoặc từ chối yêu cầu.
15. Hệ thống chỉ cập nhật lịch khi yêu cầu hợp lệ và được phê duyệt.
16. Kết quả cuối cùng được xuất ra CSV hoặc Excel.

---

## 7. Chức năng chính

### 7.1. Xác thực và phân quyền

Hệ thống cần:

- Cho phép đăng nhập bằng tài khoản hợp lệ.
- Xác định vai trò của người dùng.
- Giới hạn chức năng theo vai trò.
- Bảo vệ API ở phía backend.
- Bảo vệ trang ở phía frontend.
- Cho phép đăng xuất.
- Không chỉ dựa vào việc ẩn nút trên giao diện để phân quyền.

### 7.2. Nhập và quản lý dữ liệu

Hệ thống cần hỗ trợ nhập các nhóm dữ liệu:

- Phân công giảng dạy.
- Danh sách giảng viên.
- Danh sách phòng học.
- Danh sách khung thời gian.
- Lịch bận của giảng viên.
- Nguyện vọng giảng viên.
- Thời gian phòng không sử dụng được.
- Các cấu hình liên quan đến học kỳ.

Mỗi lần nhập dữ liệu nên được quản lý theo một đợt dữ liệu riêng.

Thông tin một đợt nhập có thể bao gồm:

- Mã đợt nhập.
- Loại dữ liệu.
- Tên file.
- Người nhập.
- Thời gian nhập.
- Trạng thái.
- Tổng số dòng.
- Số dòng hợp lệ.
- Số dòng lỗi.
- Phiên bản dữ liệu.

### 7.3. Kiểm tra dữ liệu

Hệ thống cần kiểm tra:

- File có đúng định dạng CSV hay không.
- File có đọc được hay không.
- Có thiếu cột bắt buộc hay không.
- Mã định danh có bị trống hay không.
- Giá trị số có đúng kiểu hay không.
- Giá trị số có lớn hơn 0 khi được yêu cầu hay không.
- Mã giảng viên có tồn tại hay không.
- Mã phòng có tồn tại hay không.
- Mã lớp học phần có bị trùng hay không.
- Loại lớp có thuộc danh mục hợp lệ hay không.
- Loại phòng có thuộc danh mục hợp lệ hay không.
- Khung thời gian có hợp lệ hay không.
- Sức chứa phòng có phù hợp hay không.
- Các tham chiếu giữa những file có nhất quán hay không.

Thông báo lỗi phải dễ hiểu và nên bao gồm:

- Tên file.
- Số dòng.
- Tên cột.
- Giá trị lỗi.
- Nguyên nhân.
- Hướng xử lý nếu có thể.

Dữ liệu lỗi không được đưa trực tiếp vào Genetic Algorithm.

### 7.4. Cấu hình thuật toán

Người quản lý cần có thể cấu hình:

- Population Size.
- Number of Generations.
- Mutation Rate.
- Crossover Rate.
- Selection Method.
- Elitism Size hoặc Elitism Rate.
- Random Seed.
- Trọng số cho từng ràng buộc mềm.
- Điều kiện dừng.
- Thời gian chạy tối đa nếu được hỗ trợ.

Mọi tham số phải được kiểm tra trước khi bắt đầu chạy.

### 7.5. Chạy thuật toán

Hệ thống cần:

- Nhận dữ liệu đã được xác thực.
- Tạo quần thể ban đầu.
- Đánh giá độ thích nghi.
- Thực hiện chọn lọc.
- Thực hiện lai ghép.
- Thực hiện đột biến.
- Giữ lại cá thể tốt nếu sử dụng elitism.
- Lặp qua các thế hệ.
- Theo dõi cá thể tốt nhất.
- Dừng theo số thế hệ hoặc điều kiện dừng.
- Lưu phương án tốt nhất.
- Trả về các chỉ số đánh giá.

Kết quả chạy nên bao gồm:

- Trạng thái.
- Thời điểm bắt đầu.
- Thời điểm kết thúc.
- Thời gian xử lý.
- Cấu hình tham số.
- Random seed.
- Fitness tốt nhất.
- Số vi phạm ràng buộc cứng.
- Số hoặc điểm phạt ràng buộc mềm.
- Số thế hệ đã chạy.
- Phương án thời khóa biểu tốt nhất.

### 7.6. Hiển thị thời khóa biểu

Hệ thống phải hỗ trợ ít nhất ba góc nhìn:

#### Theo giảng viên

Hiển thị:

- Mã giảng viên.
- Tên giảng viên.
- Lớp học phần.
- Học phần.
- Thứ hoặc ngày học.
- Ca hoặc tiết học.
- Phòng học.
- Tuần học.
- Trạng thái buổi học.

#### Theo phòng học

Hiển thị:

- Mã phòng.
- Tên phòng.
- Lớp sử dụng.
- Giảng viên.
- Thời gian sử dụng.
- Loại phòng.
- Trạng thái.

#### Theo lớp học phần

Hiển thị:

- Mã lớp học phần.
- Tên học phần.
- Giảng viên.
- Phòng.
- Thời gian.
- Số buổi.
- Tuần học.

Giao diện lịch cá nhân của giảng viên nên hiển thị theo tuần, từ thứ Hai đến Chủ nhật.

### 7.7. Điều chỉnh thời khóa biểu

Hệ thống dự kiến hỗ trợ:

- Tạm ngưng một buổi học.
- Chuyển ngày học.
- Chuyển ca hoặc tiết học.
- Đổi phòng học.
- Chuyển một buổi học.
- Chuyển toàn bộ lịch cố định của một lớp khi nghiệp vụ cho phép.
- Chạy lại thuật toán để tạo phương án mới.

Trước khi lưu thay đổi, hệ thống phải kiểm tra:

- Trùng lịch giảng viên.
- Trùng lịch phòng học.
- Loại phòng.
- Sức chứa phòng.
- Khung thời gian hợp lệ.
- Lịch bận của giảng viên.
- Thời gian phòng không sử dụng được.
- Các ràng buộc cứng khác có liên quan.

Nếu thay đổi gây vi phạm ràng buộc cứng, hệ thống phải từ chối và trả về lý do rõ ràng.

### 7.8. Xuất dữ liệu

Hệ thống phải hỗ trợ:

- Xuất thời khóa biểu ra CSV.
- Xuất thời khóa biểu ra Excel `.xlsx`.
- Xuất theo giảng viên.
- Xuất theo phòng.
- Xuất theo lớp học phần.
- Xuất kết quả tổng thể.

File xuất cần phản ánh đúng phương án đang được chọn hoặc đang có hiệu lực.

---

## 8. Dữ liệu đầu vào

### 8.1. Phân công giảng dạy

Các trường dữ liệu dự kiến:

| Trường                       | Ý nghĩa                           |
| ---------------------------- | --------------------------------- |
| `course_code`                | Mã học phần                       |
| `course_name`                | Tên học phần                      |
| `section_code`               | Mã lớp học phần                   |
| `lecturer_code`              | Mã giảng viên                     |
| `number_of_sessions`         | Số buổi cần xếp                   |
| `periods_per_session`        | Số tiết mỗi buổi                  |
| `expected_students`          | Sĩ số dự kiến                     |
| `initial_registration_limit` | Giới hạn đăng ký ban đầu          |
| `approved_max_students`      | Sĩ số tối đa được phê duyệt       |
| `course_type`                | Loại lớp lý thuyết hoặc thực hành |
| `weeks`                      | Tuần học                          |
| `campus_code`                | Mã cơ sở                          |
| `notes`                      | Ghi chú                           |

### 8.2. Giảng viên

Các trường dự kiến:

| Trường                     | Ý nghĩa                         |
| -------------------------- | ------------------------------- |
| `lecturer_code`            | Mã giảng viên                   |
| `lecturer_name`            | Họ tên                          |
| `unavailable_slots`        | Các khung giờ không thể dạy     |
| `preferred_slots`          | Các khung giờ ưu tiên           |
| `max_days_per_week`        | Số ngày dạy tối đa mong muốn    |
| `max_consecutive_sessions` | Số ca liên tục tối đa mong muốn |

### 8.3. Phòng học

Các trường dự kiến:

| Trường              | Ý nghĩa                      |
| ------------------- | ---------------------------- |
| `room_code`         | Mã phòng                     |
| `room_name`         | Tên phòng                    |
| `capacity`          | Sức chứa                     |
| `room_type`         | Loại phòng                   |
| `campus_code`       | Cơ sở                        |
| `available`         | Trạng thái sử dụng           |
| `unavailable_slots` | Khung giờ không sử dụng được |

### 8.4. Khung thời gian

Các trường dự kiến:

| Trường         | Ý nghĩa                               |
| -------------- | ------------------------------------- |
| `slot_code`    | Mã khung giờ                          |
| `day_of_week`  | Thứ trong tuần                        |
| `start_period` | Tiết bắt đầu                          |
| `end_period`   | Tiết kết thúc                         |
| `session_type` | Sáng, chiều hoặc tối                  |
| `active`       | Có được sử dụng để xếp lịch hay không |

Tên trường và cấu trúc chính thức có thể được điều chỉnh khi nhóm nhận được dữ liệu thực tế.

---

## 9. Ràng buộc của bài toán

### 9.1. Ràng buộc cứng

Ràng buộc cứng là các điều kiện không được phép vi phạm.

Phiên bản hiện tại xác định tối thiểu các ràng buộc sau:

1. Một giảng viên không được dạy hai lớp trong cùng một thời điểm.
2. Một phòng không được chứa hai lớp trong cùng một thời điểm.
3. Mỗi lớp học phần phải được xếp đủ số buổi yêu cầu.
4. Phòng học phải phù hợp với loại học phần.
5. Sức chứa phòng phải được kiểm tra theo quy tắc nghiệp vụ đã xác nhận.
6. Lớp chỉ được xếp vào khung thời gian hợp lệ.
7. Giảng viên không được xếp vào khung giờ được đánh dấu là không thể dạy.
8. Phòng không được xếp vào thời gian không thể sử dụng.
9. Một lần chỉnh sửa không được tạo ra xung đột mới.
10. Mỗi buổi học phải tham chiếu đến giảng viên, phòng và lớp hợp lệ.

Các ràng buộc cứng không được âm thầm bỏ qua để tăng điểm fitness.

### 9.2. Ràng buộc mềm

Ràng buộc mềm là các tiêu chí ưu tiên. Vi phạm ràng buộc mềm không làm phương án trở thành không hợp lệ, nhưng làm giảm chất lượng.

Các ràng buộc mềm dự kiến:

1. Hạn chế giảng viên dạy quá nhiều ca liên tục.
2. Hạn chế khoảng trống giữa các ca dạy.
3. Phân bố lịch dạy tương đối đồng đều trong tuần.
4. Ưu tiên nguyện vọng của giảng viên.
5. Hạn chế sử dụng buổi tối.
6. Hạn chế lịch vào thứ Bảy hoặc Chủ nhật nếu không cần thiết.
7. Hạn chế số ngày giảng viên phải đến trường.
8. Hạn chế thay đổi phòng không cần thiết.
9. Ưu tiên phòng có sức chứa phù hợp, tránh lãng phí phòng quá lớn.
10. Hạn chế lịch quá sớm hoặc quá muộn theo cấu hình.

Trọng số của từng ràng buộc mềm phải có thể điều chỉnh hoặc được định nghĩa tập trung trong cấu hình.

---

## 10. Genetic Algorithm

### 10.1. Thành phần bắt buộc

Phần thuật toán phải trình bày và cài đặt rõ:

- Chromosome representation.
- Gene representation.
- Population initialization.
- Fitness function.
- Selection.
- Crossover.
- Mutation.
- Elitism.
- Constraint checking.
- Repair mechanism nếu có.
- Stopping condition.
- Random seed.
- Metrics.

### 10.2. Nguyên tắc thiết kế

- Một cá thể đại diện cho một phương án thời khóa biểu.
- Mỗi gene phải có ý nghĩa rõ ràng.
- Cấu trúc gene không được phụ thuộc trực tiếp vào giao diện.
- Hàm fitness phải tách riêng phần ràng buộc cứng và mềm.
- Mức phạt ràng buộc cứng phải lớn hơn đáng kể ràng buộc mềm.
- Nên cố gắng tạo cá thể hợp lệ ngay từ bước khởi tạo.
- Các toán tử crossover và mutation không được làm mất dữ liệu lớp học phần.
- Mọi kết quả phải có thể kiểm tra lại bằng bộ kiểm tra ràng buộc độc lập.
- Khi cung cấp cùng dữ liệu, cấu hình và random seed, nên có khả năng tái lập kết quả ở mức hợp lý.
- Không được xem fitness cao là đủ nếu lịch vẫn vi phạm ràng buộc cứng.

### 10.3. Chỉ số thực nghiệm

Cần lưu hoặc tính được:

- Số lớp học phần.
- Số giảng viên.
- Số phòng.
- Số khung thời gian.
- Kích thước quần thể.
- Số thế hệ.
- Tỷ lệ lai ghép.
- Tỷ lệ đột biến.
- Random seed.
- Fitness tốt nhất.
- Fitness trung bình nếu cần.
- Số vi phạm cứng.
- Điểm phạt mềm.
- Thời gian xử lý.
- Mức sử dụng tài nguyên nếu có thể.
- Thế hệ tìm được cá thể tốt nhất.

---

## 11. Công nghệ dự kiến

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- pandas
- NumPy
- openpyxl
- pytest

### Frontend

- ReactJS
- TypeScript
- Vite
- Material UI
- Thư viện gọi API phù hợp
- Công cụ kiểm thử frontend sẽ được lựa chọn trong giai đoạn thiết kế

### Database

- PostgreSQL

### DevOps và công cụ hỗ trợ

- Git
- GitHub
- GitHub Actions
- Docker
- Docker Compose
- Visual Studio Code
- Codex hoặc công cụ AI hỗ trợ lập trình

Không được tự ý thay đổi framework chính hoặc thêm dependency lớn khi chưa có sự thống nhất của nhóm.

---

## 12. Kiến trúc dự kiến

Hệ thống dự kiến sử dụng kiến trúc client-server:

```text
ReactJS Frontend
        |
        | HTTP/REST API
        v
FastAPI Backend
        |
        +-- Authentication and Authorization
        +-- Data Import and Validation
        +-- Timetable Management
        +-- Adjustment Request Management
        +-- Export Service
        +-- Genetic Algorithm Engine
        |
        v
PostgreSQL Database
```

Nguyên tắc phân tách:

- Frontend chịu trách nhiệm hiển thị và tương tác.
- Backend chịu trách nhiệm xử lý nghiệp vụ.
- Database chịu trách nhiệm lưu trữ.
- Genetic Algorithm được xây dựng thành mô-đun độc lập.
- API route không chứa quá nhiều business logic.
- Business logic không được đặt trực tiếp trong React component.
- Kiểm tra quyền phải được thực hiện tại backend.
- Kiểm tra ràng buộc phải dùng chung một nguồn logic, tránh viết nhiều phiên bản khác nhau.

---

## 13. Cấu trúc repository dự kiến

```text
timetable-ga/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── algorithms/
│   │   │   └── genetic/
│   │   └── main.py
│   ├── tests/
│   ├── migrations/
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   └── README.md
│
├── data/
│   ├── samples/
│   └── README.md
│
├── docs/
│   ├── requirements/
│   │   ├── URS.md
│   │   ├── SRS.md
│   │   └── README.md
│   ├── architecture/
│   ├── database/
│   ├── api/
│   ├── algorithm/
│   └── testing/
│
├── scripts/
│
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
│
├── .env.example
├── .gitignore
├── AGENTS.md
├── CONTRIBUTING.md
├── docker-compose.yml
└── README.md
```

Cấu trúc trên là định hướng ban đầu. Chỉ tạo thư mục khi có mục đích rõ ràng và tránh tạo nhiều lớp thư mục không cần thiết.

---

## 14. Nguyên tắc phát triển

### 14.1. Nguồn yêu cầu

Khi triển khai một chức năng, cần đọc tài liệu theo thứ tự:

1. `docs/requirements/URS.md`
2. `docs/requirements/SRS.md`
3. GitHub Issue liên quan
4. Tài liệu kiến trúc
5. Tài liệu cơ sở dữ liệu
6. Tài liệu API
7. Tài liệu thuật toán

Khi các tài liệu mâu thuẫn:

- Không tự chọn một cách hiểu.
- Ghi rõ điểm mâu thuẫn.
- Báo cho nhóm.
- Chờ quyết định hoặc cập nhật tài liệu.
- Không tự phát minh thêm quy tắc nghiệp vụ.

### 14.2. Quy trình Git

Không code trực tiếp trên `main`.

Quy trình chuẩn:

1. Cập nhật `main`.
2. Chọn một GitHub Issue.
3. Tạo branch theo Issue.
4. Thực hiện thay đổi nhỏ và đúng phạm vi.
5. Commit rõ ràng.
6. Push branch.
7. Mở Pull Request.
8. Chạy test.
9. Review.
10. Sửa theo review nếu cần.
11. Merge khi đáp ứng Definition of Done.

Ví dụ tên branch:

```text
feature/TKB-001-upload-csv
feature/TKB-002-authentication
feature/TKB-003-genetic-algorithm
bugfix/TKB-020-room-conflict
docs/TKB-030-update-readme
test/TKB-040-add-constraint-tests
refactor/TKB-050-fitness-service
chore/TKB-060-project-configuration
```

Ví dụ commit:

```text
feat(upload): validate required CSV columns
fix(schedule): prevent lecturer time conflicts
test(ga): add hard constraint test cases
docs(readme): update project scope
refactor(fitness): separate hard and soft penalties
chore: configure backend dependencies
```

---

## 15. Hướng dẫn dành cho Codex và AI coding agents

Codex hoặc công cụ AI hỗ trợ lập trình phải tuân thủ các nguyên tắc sau.

### 15.1. Trước khi thay đổi code

Codex phải:

1. Đọc toàn bộ Issue được giao.
2. Đọc phần liên quan trong README.
3. Đọc URS và SRS nếu đã có trong repository.
4. Kiểm tra cấu trúc và code hiện tại.
5. Xác định các file sẽ thay đổi.
6. Trình bày kế hoạch ngắn trước khi thực hiện.
7. Nêu rõ giả định nếu có.
8. Dừng lại và báo khi yêu cầu chưa rõ.

### 15.2. Trong quá trình triển khai

Codex phải:

- Thực hiện thay đổi nhỏ nhất đủ đáp ứng yêu cầu.
- Tái sử dụng cấu trúc hiện có.
- Không tạo framework hoặc kiến trúc mới nếu chưa cần.
- Không đổi công nghệ chính.
- Không tự tạo quy tắc nghiệp vụ.
- Không bỏ qua ràng buộc cứng.
- Không đặt business logic trong API controller nếu có thể tách service.
- Không gọi database trực tiếp từ frontend.
- Không sửa các file không liên quan.
- Không thực hiện refactor lớn trong PR tính năng nhỏ.
- Không xóa test chỉ để làm CI thành công.
- Không thêm dependency khi chưa giải thích lý do.
- Không commit secret hoặc dữ liệu nhạy cảm.
- Phải thêm hoặc cập nhật test cho hành vi mới.
- Phải giữ mã nguồn dễ đọc và có type hint khi phù hợp.

### 15.3. Sau khi triển khai

Codex phải cung cấp:

- Tóm tắt thay đổi.
- Danh sách file đã sửa hoặc tạo.
- Cách chạy kiểm thử.
- Kết quả test.
- Các giả định đã sử dụng.
- Rủi ro hoặc vấn đề còn lại.
- Những nội dung cần nhóm xác nhận.

### 15.4. Những hành động bị cấm

Codex không được:

- Push trực tiếp vào `main`.
- Tự merge Pull Request.
- Commit file `.env`.
- Ghi cứng mật khẩu hoặc token.
- Tự thay đổi phạm vi dự án.
- Tự đổi database hoặc framework.
- Âm thầm bỏ kiểm tra ràng buộc.
- Đánh dấu hoàn thành khi chưa chạy test.
- Sửa migration đã được áp dụng nếu chưa được phép.
- Dùng dữ liệu cá nhân thật làm dữ liệu mẫu.
- Tạo lượng lớn file không cần thiết.
- Sao chép code mà không kiểm tra giấy phép hoặc nguồn gốc.
- Coi README là tài liệu thay thế hoàn toàn cho SRS.

Khi `AGENTS.md` được bổ sung, Codex phải đọc và ưu tiên các hướng dẫn cụ thể trong file đó.

---

## 16. Kiểm thử

### 16.1. Backend

Dự kiến sử dụng:

```bash
cd backend
pytest
```

Các nhóm test cần có:

- Unit test cho kiểm tra CSV.
- Unit test cho quy tắc dữ liệu.
- Unit test cho từng ràng buộc cứng.
- Unit test cho từng ràng buộc mềm.
- Unit test cho fitness function.
- Unit test cho selection.
- Unit test cho crossover.
- Unit test cho mutation.
- Unit test cho conflict checker.
- Integration test cho API.
- Test phân quyền.
- Test xuất CSV và Excel.

### 16.2. Frontend

Các nhóm test dự kiến:

- Render màn hình.
- Form validation.
- Trạng thái loading.
- Hiển thị lỗi.
- Hiển thị thời khóa biểu.
- Phân quyền giao diện.
- Luồng nhập CSV.
- Luồng gửi yêu cầu điều chỉnh.
- Luồng xem kết quả.

### 16.3. Kiểm thử thuật toán

Cần kiểm thử tối thiểu trên ba mức dữ liệu:

#### Dữ liệu nhỏ

Mục tiêu:

- Kiểm tra tính đúng đắn.
- Có thể kiểm tra kết quả bằng tay.
- Phát hiện lỗi biểu diễn và ràng buộc.

#### Dữ liệu trung bình

Mục tiêu:

- Tinh chỉnh tham số.
- So sánh các cấu hình.
- Đánh giá độ ổn định.

#### Dữ liệu lớn hoặc dữ liệu thực tế

Mục tiêu:

- Đánh giá thời gian xử lý.
- Đánh giá khả năng mở rộng.
- Đo chất lượng lời giải.
- Đo số vi phạm.
- Đo tài nguyên nếu có thể.

---

## 17. Definition of Done

Một Issue chỉ được xem là hoàn thành khi:

- Đáp ứng đầy đủ acceptance criteria.
- Không vượt ngoài phạm vi Issue.
- Code đã được lưu trên branch riêng.
- Có test phù hợp.
- Test mới thành công.
- Test cũ không bị hỏng.
- Lint thành công.
- Build thành công nếu có liên quan.
- Không có secret trong commit.
- Không có file debug không cần thiết.
- Không còn lỗi rõ ràng trong chức năng.
- Tài liệu được cập nhật khi hành vi thay đổi.
- Pull Request có mô tả và hướng dẫn kiểm tra.
- Có ít nhất một thành viên review.
- Mọi yêu cầu sửa quan trọng đã được xử lý.
- CI thành công trước khi merge.

“Code chạy được trên máy cá nhân” chưa đủ để xem là hoàn thành.

---

## 18. Yêu cầu phi chức năng

Hệ thống cần hướng đến:

### Bảo mật

- Mật khẩu không được lưu dưới dạng văn bản thuần.
- Kiểm tra quyền ở backend.
- Không để lộ thông tin lỗi nhạy cảm.
- Không commit secret.
- Kiểm tra file upload.
- Giới hạn loại và kích thước file hợp lý.

### Khả năng sử dụng

- Giao diện dễ hiểu.
- Thông báo lỗi rõ ràng.
- Các thao tác nguy hiểm cần xác nhận.
- Thời khóa biểu dễ tra cứu.
- Trạng thái xử lý phải được hiển thị.

### Khả năng bảo trì

- Tách module rõ ràng.
- Tránh lặp business logic.
- Có test.
- Có type hint.
- Có migration database.
- Có tài liệu API.
- Có quy tắc code chung.

### Khả năng truy vết

- Yêu cầu phải liên kết được với Issue.
- Issue liên kết với branch và Pull Request.
- Lần chạy GA liên kết với dữ liệu và cấu hình.
- Yêu cầu điều chỉnh lưu người gửi, người xử lý và thời gian xử lý.

### Hiệu năng

- Không chặn giao diện trong thời gian chạy dài.
- Hiển thị trạng thái xử lý.
- Không đọc toàn bộ file lớn theo cách không cần thiết.
- Tối ưu sau khi đã có dữ liệu đo thực tế.
- Không tối ưu sớm bằng cách làm code khó hiểu.

---

## 19. Dữ liệu và bảo mật

Không được commit:

```text
.env
.env.local
.env.production
*.pem
*.key
credentials.json
secret.json
database dump có dữ liệu thật
file chứa mật khẩu
access token
API key
dữ liệu cá nhân chưa được phép sử dụng
```

File `.env.example` chỉ chứa tên biến và giá trị minh họa không nhạy cảm.

Ví dụ:

```env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/timetable
SECRET_KEY=change-me
CORS_ORIGINS=http://localhost:5173
```

Dữ liệu trong `data/samples/` phải là dữ liệu giả lập hoặc đã được phép sử dụng.

---

## 20. Cài đặt và chạy dự án

> Phần này sẽ được cập nhật khi backend, frontend và Docker Compose được khởi tạo.

### Yêu cầu dự kiến

- Git
- Python
- Node.js
- npm
- PostgreSQL
- Docker
- Docker Compose

### Clone repository

```bash
git clone https://github.com/Matthew-Kuroc/timetable-ga.git
cd timetable-ga
```

### Chạy bằng Docker Compose

Dự kiến:

```bash
docker compose up --build
```

### Chạy backend

Dự kiến:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Cài dependency và chạy:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Chạy frontend

Dự kiến:

```bash
cd frontend
npm install
npm run dev
```

Các lệnh chính thức phải được cập nhật sau khi cấu trúc dự án được tạo.

---

## 21. Sản phẩm bàn giao dự kiến

Dự án cần cung cấp:

### Mã nguồn

- Source code backend.
- Source code frontend.
- Source code Genetic Algorithm.
- Database migration.
- File cấu hình mẫu.
- Hướng dẫn cài đặt.
- Hướng dẫn chạy.
- Test tự động.

### Tài liệu

- User Requirements Specification.
- Software Requirements Specification.
- Tài liệu kiến trúc.
- Thiết kế cơ sở dữ liệu.
- Đặc tả API.
- Tài liệu Genetic Algorithm.
- Mô tả hàm fitness.
- Kế hoạch và kết quả kiểm thử.
- Báo cáo thực nghiệm.
- Báo cáo thực tập.

### Demo

- Dữ liệu mẫu.
- Video demo.
- Phiên bản chạy thử.
- File kết quả CSV hoặc Excel.

---

## 22. Tiêu chí ưu tiên

Trong trường hợp thời gian có hạn, ưu tiên theo thứ tự:

1. Nhập và kiểm tra được dữ liệu CSV.
2. Cài đặt đúng Genetic Algorithm.
3. Không vi phạm ràng buộc cứng.
4. Hiển thị được thời khóa biểu trên web.
5. Chỉnh sửa được ít nhất một buổi học và kiểm tra xung đột.
6. Xuất được CSV hoặc Excel.
7. Hoàn thiện phân quyền và quy trình yêu cầu điều chỉnh.
8. Lưu lịch sử chạy và đánh giá thực nghiệm.
9. Tối ưu giao diện và các chức năng mở rộng.

Không được dành quá nhiều thời gian cho giao diện nếu phần thuật toán và kiểm tra ràng buộc chưa hoạt động đúng.

---

## 23. Lộ trình dự kiến

### Giai đoạn 1 — Phân tích và chuẩn bị

- Hoàn thiện URS.
- Hoàn thiện SRS.
- Thiết lập repository.
- Thiết lập quy trình Git.
- Xây dựng CSV mẫu.
- Xác nhận ràng buộc.
- Thiết kế kiến trúc.

### Giai đoạn 2 — Dữ liệu và backend nền tảng

- Khởi tạo FastAPI.
- Kết nối PostgreSQL.
- Xây dựng migration.
- Xây dựng model.
- Upload CSV.
- Preview dữ liệu.
- Validate dữ liệu.
- Lưu các đợt nhập.

### Giai đoạn 3 — Genetic Algorithm

- Thiết kế chromosome.
- Khởi tạo population.
- Xây dựng constraint checker.
- Xây dựng fitness.
- Selection.
- Crossover.
- Mutation.
- Elitism.
- Lưu kết quả.
- Viết test.

### Giai đoạn 4 — Frontend

- Đăng nhập.
- Upload dữ liệu.
- Cấu hình thuật toán.
- Chạy thuật toán.
- Hiển thị tiến trình.
- Hiển thị kết quả.
- Lịch theo tuần.

### Giai đoạn 5 — Điều chỉnh và xuất dữ liệu

- Yêu cầu điều chỉnh.
- Kiểm tra xung đột.
- Phê duyệt hoặc từ chối.
- Cập nhật lịch.
- Xuất CSV.
- Xuất Excel.

### Giai đoạn 6 — Thực nghiệm và hoàn thiện

- Kiểm thử dữ liệu nhỏ.
- Kiểm thử dữ liệu trung bình.
- Kiểm thử dữ liệu lớn.
- So sánh cấu hình.
- Đo thời gian.
- Sửa lỗi.
- Hoàn thiện tài liệu.
- Quay video demo.

---

## 24. Vấn đề còn cần xác nhận

Các nội dung sau chưa được xem là quyết định cuối cùng nếu chưa có xác nhận chính thức:

1. Quy tắc chính xác về sức chứa phòng.
2. Giá trị sĩ số nào được dùng để kiểm tra sức chứa.
3. Trường hợp lớp có sĩ số lớn hơn sức chứa phòng được xử lý thế nào.
4. Quy trình phê duyệt yêu cầu đổi lịch.
5. Mốc khóa chức năng chuyển toàn bộ lịch cố định.
6. Tạm ngưng một buổi có bắt buộc tạo lịch dạy bù hay không.
7. Người đề xuất và người chọn lịch dạy bù.
8. Quy tắc cụ thể đối với lớp thực hành.
9. Các ngoại lệ về khung giờ.
10. Danh sách cột chính thức trong dữ liệu thực tế.
11. Quy mô dữ liệu dùng để nghiệm thu.
12. Trọng số ban đầu của các ràng buộc mềm.
13. Cơ chế xác thực cuối cùng.
14. Chính sách lưu lịch sử và phục hồi phương án.

Khi gặp một nội dung chưa xác nhận, không tự suy đoán và không âm thầm triển khai theo ý riêng.

---

## 25. Đóng góp

Mọi thành viên phải tuân thủ quy trình trong `CONTRIBUTING.md`.

Tóm tắt:

- Không code trực tiếp trên `main`.
- Mỗi Issue sử dụng một branch.
- Commit phải rõ ràng.
- Mọi thay đổi phải đi qua Pull Request.
- Cần review trước khi merge.
- Chỉ merge khi test và CI thành công.

---

## 26. Giấy phép

Repository hiện được sử dụng cho mục đích học tập và thực hiện đề tài thực tập.

Chưa áp dụng giấy phép mã nguồn mở.

Không sao chép hoặc sử dụng lại mã nguồn ngoài phạm vi nhóm khi chưa có sự đồng ý của chủ sở hữu dự án.

---

## 27. Ghi chú

README cung cấp cái nhìn tổng quan về dự án nhưng không thay thế cho URS, SRS, tài liệu kiến trúc, đặc tả API hoặc tài liệu thuật toán.

Khi hành vi hệ thống thay đổi, tài liệu liên quan phải được cập nhật cùng với code.
