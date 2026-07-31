# Hướng dẫn đóng góp

Tài liệu này quy định cách các thành viên làm việc với mã nguồn, tài liệu, dữ
liệu mẫu, nhánh Git và Pull Request trong dự án:

**Xây dựng ứng dụng lập thời khóa biểu giảng dạy sử dụng thuật toán Di truyền**

Mọi thành viên cần tuân thủ tài liệu này để hạn chế xung đột mã nguồn, sai lệch
nghiệp vụ và mất khả năng truy vết thay đổi.

---

## Mục lục

- [1. Nguyên tắc chung](#1-nguyên-tắc-chung)
- [2. Nguồn yêu cầu nghiệp vụ](#2-nguồn-yêu-cầu-nghiệp-vụ)
- [3. Hướng dẫn AGENTS.md](#3-hướng-dẫn-agentsmd)
- [4. Chuẩn bị môi trường làm việc](#4-chuẩn-bị-môi-trường-làm-việc)
- [5. Quy trình làm việc với Git](#5-quy-trình-làm-việc-với-git)
- [6. Quy ước đặt tên branch](#6-quy-ước-đặt-tên-branch)
- [7. Quy ước commit](#7-quy-ước-commit)
- [8. Quy trình Pull Request](#8-quy-trình-pull-request)
- [9. Quy tắc review](#9-quy-tắc-review)
- [10. Thay đổi yêu cầu nghiệp vụ](#10-thay-đổi-yêu-cầu-nghiệp-vụ)
- [11. Quy tắc đối với backend](#11-quy-tắc-đối-với-backend)
- [12. Quy tắc đối với frontend](#12-quy-tắc-đối-với-frontend)
- [13. Quy tắc đối với thuật toán](#13-quy-tắc-đối-với-thuật-toán)
- [14. Quy tắc kiểm thử](#14-quy-tắc-kiểm-thử)
- [15. Quy tắc dữ liệu CSV](#15-quy-tắc-dữ-liệu-csv)
- [16. Quy tắc tài liệu](#16-quy-tắc-tài-liệu)
- [17. Bảo mật và dữ liệu riêng tư](#17-bảo-mật-và-dữ-liệu-riêng-tư)
- [18. Quy tắc merge](#18-quy-tắc-merge)
- [19. Checklist trước khi hoàn thành](#19-checklist-trước-khi-hoàn-thành)
- [20. Các hành vi không được phép](#20-các-hành-vi-không-được-phép)

---

## 1. Nguyên tắc chung

Mọi thay đổi trong repository phải tuân theo các nguyên tắc sau:

- Làm đúng phạm vi đề tài thực tập.
- Không tự ý mở rộng nghiệp vụ.
- Không thay đổi quy tắc đã chốt mà không cập nhật tài liệu.
- Không làm yếu ràng buộc cứng để thuật toán dễ tìm nghiệm hơn.
- Không sửa trực tiếp trên nhánh `main`.
- Mỗi công việc phải được thực hiện trên một branch riêng.
- Mỗi Pull Request chỉ nên tập trung vào một mục tiêu chính.
- Mã nguồn phải có khả năng đọc, kiểm thử và truy vết.
- Không đưa thông tin nhạy cảm vào repository.
- Không sử dụng dữ liệu cá nhân thật khi chưa được phép.
- Không merge khi chưa có thành viên khác review.
- Không bỏ qua lỗi chỉ để Pull Request được merge.

Ưu tiên:

1. Tính đúng đắn của nghiệp vụ.
2. Tính an toàn của dữ liệu.
3. Khả năng kiểm thử.
4. Khả năng đọc và bảo trì.
5. Hiệu năng.
6. Tối ưu hóa nhỏ.

---

## 2. Nguồn yêu cầu nghiệp vụ

Các tài liệu yêu cầu chính của dự án được lưu trong:

```text
docs/requirements/
```

Các tài liệu hiện tại gồm:

```text
docs/requirements/TaiLieu_UR_cap_nhat_0.2.docx
docs/requirements/TaiLieu_SRS_cap_nhat_0.3.docx
```

Trong đó:

- URS mô tả nhu cầu người dùng và phạm vi nghiệp vụ.
- SRS mô tả yêu cầu chức năng, dữ liệu, ràng buộc và tiêu chí chấp nhận.
- `README.md` giới thiệu tổng quan dự án.
- `AGENTS.md` hướng dẫn AI coding agents và thành viên khi sửa mã nguồn.
- `CONTRIBUTING.md` quy định quy trình đóng góp.

Khi có sự khác biệt giữa tài liệu và mã nguồn:

1. Kiểm tra phiên bản URS và SRS mới nhất.
2. Xác định thay đổi nào được phê duyệt gần nhất.
3. Không tự suy diễn yêu cầu.
4. Cập nhật tài liệu trước hoặc đồng thời với mã nguồn.
5. Thêm kiểm thử cho hành vi mới.
6. Ghi rõ thay đổi trong Pull Request.

Mã nguồn không được xem là nguồn yêu cầu duy nhất.

---

## 3. Hướng dẫn AGENTS.md

Trước khi sửa một thư mục, phải đọc file `AGENTS.md` gần nhất.

Các file dự kiến gồm:

```text
AGENTS.md
backend/AGENTS.md
backend/app/algorithms/AGENTS.md
backend/app/algorithms/genetic/AGENTS.md
frontend/AGENTS.md
```

Quy tắc ưu tiên:

1. `AGENTS.md` ở thư mục gốc áp dụng cho toàn repository.
2. `AGENTS.md` trong thư mục con bổ sung quy tắc chi tiết.
3. File `AGENTS.md` gần file đang sửa nhất được ưu tiên khi có khác biệt.

Ví dụ:

Khi sửa file trong:

```text
backend/app/algorithms/genetic/
```

cần đọc:

```text
AGENTS.md
backend/AGENTS.md
backend/app/algorithms/AGENTS.md
backend/app/algorithms/genetic/AGENTS.md
```

Không bỏ qua hướng dẫn ở các file này.

---

## 4. Chuẩn bị môi trường làm việc

Trước khi bắt đầu một công việc:

```powershell
cd D:\DoAn\DuAn\timetable-ga
git status
git switch main
git pull origin main
```

Kết quả mong đợi:

- Đang đứng ở nhánh `main`.
- Nhánh `main` đã được cập nhật.
- Không có file chưa commit từ công việc trước.
- Không có xung đột đang tồn tại.

Kiểm tra danh sách branch:

```powershell
git branch
```

Kiểm tra branch từ xa:

```powershell
git branch -r
```

Không bắt đầu công việc mới khi thư mục làm việc còn thay đổi chưa được xử lý.

Khi có thay đổi chưa hoàn thành, cần:

- Commit vào branch phù hợp.
- Hoặc stash tạm thời.
- Hoặc loại bỏ thay đổi nếu chắc chắn không cần.

Ví dụ stash:

```powershell
git stash push -m "WIP: unfinished timetable work"
```

Khôi phục:

```powershell
git stash pop
```

---

## 5. Quy trình làm việc với Git

Mỗi công việc nên đi theo quy trình:

```text
Cập nhật main
    ↓
Tạo branch mới
    ↓
Đọc URS/SRS và AGENTS.md
    ↓
Thực hiện thay đổi
    ↓
Chạy kiểm thử
    ↓
Kiểm tra git diff
    ↓
Commit
    ↓
Push branch
    ↓
Tạo Pull Request
    ↓
Review
    ↓
Sửa theo góp ý
    ↓
Merge vào main
```

Ví dụ:

```powershell
git switch main
git pull origin main
git switch -c docs/TKB-003-update-contributing
```

Sau khi sửa:

```powershell
git status
git diff
```

Thêm file:

```powershell
git add CONTRIBUTING.md
```

Commit:

```powershell
git commit -m "docs: update contribution guidelines"
```

Push:

```powershell
git push -u origin docs/TKB-003-update-contributing
```

Không thực hiện công việc trực tiếp trên `main`.

---

## 6. Quy ước đặt tên branch

Cấu trúc:

```text
<type>/TKB-<number>-<short-description>
```

Các loại branch:

| Loại       | Mục đích                                  |
| ---------- | ----------------------------------------- |
| `feature`  | Thêm chức năng mới                        |
| `fix`      | Sửa lỗi                                   |
| `docs`     | Sửa tài liệu                              |
| `test`     | Thêm hoặc sửa kiểm thử                    |
| `refactor` | Cải tiến cấu trúc mã mà không đổi hành vi |
| `chore`    | Công việc cấu hình, công cụ hoặc khởi tạo |
| `perf`     | Cải thiện hiệu năng                       |
| `build`    | Thay đổi quy trình build                  |
| `ci`       | Thay đổi CI/CD                            |

Ví dụ hợp lệ:

```text
feature/TKB-010-csv-import
feature/TKB-015-ga-configuration
fix/TKB-021-room-overlap
fix/TKB-024-period-range-overlap
docs/TKB-003-update-contributing
docs/TKB-004-update-requirements
test/TKB-030-ga-capacity-tests
refactor/TKB-035-extract-constraint-service
chore/TKB-001-initialize-project
perf/TKB-040-optimize-fitness-evaluation
```

Không dùng:

```text
my-branch
new-feature
phi-test
fix
update
branch1
```

Tên branch phải:

- Viết thường.
- Dùng dấu gạch ngang.
- Mô tả ngắn gọn công việc.
- Không chứa dấu tiếng Việt.
- Không chứa khoảng trắng.
- Không dùng tên thành viên làm mục đích chính.

---

## 7. Quy ước commit

Commit message nên theo cấu trúc:

```text
<type>: <short description>
```

Các loại commit:

| Loại       | Mục đích                        |
| ---------- | ------------------------------- |
| `feat`     | Thêm chức năng                  |
| `fix`      | Sửa lỗi                         |
| `docs`     | Sửa tài liệu                    |
| `test`     | Thêm hoặc sửa test              |
| `refactor` | Cải tiến cấu trúc mã            |
| `chore`    | Cấu hình hoặc công việc phụ trợ |
| `perf`     | Cải thiện hiệu năng             |
| `build`    | Thay đổi build                  |
| `ci`       | Thay đổi CI/CD                  |
| `style`    | Chỉ thay đổi định dạng mã       |

Ví dụ:

```text
feat: add CSV preview
feat: add lecturer timetable view
feat: support schedule segments
fix: detect partial period overlap
fix: reject insufficient room capacity
fix: preserve timetable after rejected request
docs: update scheduling requirements
docs: revise project README
test: add room capacity validation tests
test: cover weekend lecturer preferences
refactor: extract timetable constraint service
perf: reduce repeated room compatibility checks
chore: initialize frontend structure
```

Commit message cần:

- Ngắn gọn.
- Mô tả kết quả thay đổi.
- Viết ở thể mệnh lệnh hoặc mô tả hành động.
- Không kết thúc bằng dấu chấm.
- Không dùng nội dung mơ hồ.

Không dùng:

```text
update
fix bug
done
test
abc
final
final final
code mới
sửa chút
```

### 7.1. Quy mô commit

Một commit nên chứa một thay đổi có ý nghĩa.

Ví dụ tốt:

```text
fix: detect lecturer overlap by period range
```

Ví dụ không tốt:

```text
feat: add login, update README, fix GA, change database and format files
```

Không gộp nhiều công việc không liên quan vào cùng một commit.

### 7.2. Kiểm tra trước khi commit

```powershell
git status
git diff
git diff --staged
```

Không commit:

- File tạm.
- File build.
- File log.
- File `.env` thật.
- Thư mục IDE không cần thiết.
- Dữ liệu riêng tư.
- Mật khẩu hoặc token.
- File thay đổi ngoài phạm vi công việc.

---

## 8. Quy trình Pull Request

Mọi thay đổi vào `main` phải thông qua Pull Request.

### 8.1. Nội dung Pull Request

Pull Request cần mô tả:

- Vấn đề hoặc yêu cầu được xử lý.
- Các file hoặc mô-đun chính đã thay đổi.
- Hành vi mới.
- Cách kiểm thử.
- Ảnh chụp màn hình nếu thay đổi giao diện.
- Ảnh hưởng đến dữ liệu hoặc API.
- Ảnh hưởng đến URS/SRS.
- Nội dung còn chưa hoàn thành.
- Rủi ro hoặc giới hạn đã biết.

Ví dụ:

```markdown
## Mục tiêu

Thêm kiểm tra xung đột giảng viên theo khoảng tiết thực tế.

## Thay đổi chính

- Thêm hàm kiểm tra hai khoảng tiết chồng nhau.
- Áp dụng cho kiểm tra giảng viên.
- Áp dụng cho kiểm tra phòng.
- Bổ sung test cho tiết 1–5 và tiết 2–6.

## Cách kiểm thử

- Chạy unit test của constraint service.
- Kiểm tra hai lớp tiết 1–5 và 2–6 bị báo trùng.
- Kiểm tra hai lớp tiết 1–3 và 4–6 không bị báo trùng.

## Tài liệu liên quan

Không thay đổi yêu cầu nghiệp vụ.
```

### 8.2. Tiêu đề Pull Request

Tiêu đề nên mô tả rõ công việc.

Ví dụ:

```text
[TKB-010] Add CSV import preview
[TKB-021] Fix partial period overlap detection
[TKB-003] Update contribution guidelines
```

Không dùng:

```text
Update
Fix
My work
Done
Final
Pull request 1
```

### 8.3. Quy mô Pull Request

Một Pull Request nên:

- Tập trung vào một mục tiêu.
- Có số lượng file thay đổi hợp lý.
- Có thể review trong một lần.
- Không trộn định dạng toàn bộ dự án với thay đổi nghiệp vụ.
- Không sửa file không liên quan.

Khi công việc quá lớn, chia thành nhiều Pull Request.

Ví dụ:

```text
PR 1: tạo domain models
PR 2: tạo validation service
PR 3: tạo API endpoints
PR 4: tạo frontend workflow
```

---

## 9. Quy tắc review

Mỗi Pull Request cần ít nhất một thành viên khác review trước khi merge.

Reviewer cần kiểm tra:

- Thay đổi có đúng mục tiêu không.
- Có tuân theo URS và SRS không.
- Có đọc đúng `AGENTS.md` không.
- Có mở rộng phạm vi ngoài đề tài không.
- Có làm yếu ràng buộc cứng không.
- Có nhân bản logic nghiệp vụ không.
- Có thiếu kiểm thử không.
- Có dữ liệu nhạy cảm không.
- Có lỗi phân quyền không.
- Có lỗi xử lý trạng thái không.
- Có thông báo lỗi rõ ràng không.
- Có ảnh hưởng đến file CSV mẫu không.
- Có cần cập nhật tài liệu không.

### 9.1. Cách ghi nhận xét

Nhận xét nên rõ và có hướng xử lý.

Ví dụ tốt:

```text
Hàm này chỉ so sánh slot_code nên chưa phát hiện được trường hợp
tiết 1–5 chồng với tiết 2–6. Nên dùng start_period và end_period.
```

Ví dụ không tốt:

```text
Sai.
```

Reviewer nên phân biệt:

- `Blocking`: cần sửa trước khi merge.
- `Suggestion`: đề xuất cải thiện, không bắt buộc.
- `Question`: cần giải thích.
- `Nit`: góp ý nhỏ về cách trình bày.

### 9.2. Phản hồi review

Người tạo Pull Request cần:

- Đọc toàn bộ nhận xét.
- Trả lời khi cần làm rõ.
- Sửa trực tiếp trên cùng branch.
- Push commit mới.
- Không tạo Pull Request khác chỉ để sửa review.
- Đánh dấu nhận xét đã xử lý sau khi kiểm tra.
- Không tự ý bỏ qua nhận xét blocking.

---

## 10. Thay đổi yêu cầu nghiệp vụ

Một thay đổi được xem là thay đổi nghiệp vụ khi ảnh hưởng đến:

- Vai trò người dùng.
- Quyền truy cập.
- Quy trình xử lý.
- Dữ liệu đầu vào.
- Ràng buộc cứng.
- Ràng buộc mềm.
- Cách tính sức chứa.
- Cách xếp ngày hoặc khung giờ.
- Mô hình gene.
- Loại lớp học phần.
- Phòng học.
- Ngày lễ.
- Học bù.
- Phân đoạn lịch.
- Phạm vi dự án.

Khi thay đổi nghiệp vụ:

1. Đọc URS và SRS hiện tại.
2. Xác định thay đổi đã được thống nhất chưa.
3. Cập nhật URS/SRS.
4. Cập nhật `README.md` khi ảnh hưởng tổng quan.
5. Cập nhật `AGENTS.md` liên quan.
6. Cập nhật domain models.
7. Cập nhật validation.
8. Cập nhật GA nếu có liên quan.
9. Cập nhật frontend.
10. Cập nhật CSV mẫu.
11. Thêm hoặc sửa kiểm thử.
12. Ghi rõ ảnh hưởng trong Pull Request.

Không thay đổi nghiệp vụ chỉ bằng cách sửa code.

### 10.1. Ràng buộc cứng

Các ràng buộc cứng không được tự ý giảm mức xử lý.

Ví dụ:

- Trùng giảng viên.
- Trùng phòng.
- Sai loại phòng.
- Phòng không đủ sức chứa.
- Khung giờ không hợp lệ.
- Vi phạm hạn chế bắt buộc.
- Thiếu lịch cơ sở.

Không được chuyển một lỗi cứng thành cảnh báo mềm để thuật toán dễ tìm nghiệm.

### 10.2. Ràng buộc mềm

Ràng buộc mềm có thể thay đổi trọng số, nhưng phải:

- Có cấu hình rõ ràng.
- Có kiểm thử.
- Có giải thích.
- Được lưu cùng lần chạy GA.
- Không làm phương án vi phạm cứng tốt hơn phương án hợp lệ.

### 10.3. Ngày cuối tuần

Thứ Bảy và Chủ nhật là ngày dạy hợp lệ.

Không thêm mức phạt mặc định cho cuối tuần.

Chỉ áp dụng điểm ưu tiên hoặc không mong muốn dựa trên dữ liệu nguyện vọng của
từng giảng viên.

### 10.4. Phòng lớn

Phòng khoảng 130 chỗ:

- Không bị khóa riêng cho môn đại cương.
- Có thể dùng cho lớp phù hợp.
- Nên được ưu tiên cho lớp đông hoặc khi thiếu phòng tiêu chuẩn.
- Sử dụng cho lớp nhỏ chỉ là vấn đề tối ưu mềm.
- Không được xem là lỗi cứng nếu đủ loại phòng và sức chứa.

---

## 11. Quy tắc đối với backend

Khi thay đổi backend:

- Đọc `backend/AGENTS.md`.
- Không đặt nghiệp vụ trong route handler.
- Không truy cập database trực tiếp từ thuật toán.
- Không để API tự suy diễn dữ liệu chưa được chuẩn hóa.
- Kiểm tra quyền tại backend.
- Trả về lỗi có cấu trúc.
- Dùng kiểu dữ liệu rõ ràng.
- Tách validation khỏi persistence.
- Không nhân bản cùng một quy tắc ở nhiều service.
- Không trả lỗi chung chung khi có thể cung cấp nguyên nhân cụ thể.

Backend là nguồn quyết định cuối cùng đối với:

- Xác thực.
- Phân quyền.
- Ràng buộc cứng.
- Kiểm tra xung đột.
- Áp dụng thay đổi lịch.
- Xử lý yêu cầu.
- Lưu dữ liệu.
- Xuất kết quả.

Frontend không được xem là lớp bảo vệ duy nhất.

---

## 12. Quy tắc đối với frontend

Khi thay đổi frontend:

- Đọc `frontend/AGENTS.md`.
- Sử dụng tiếng Việt cho nội dung giao diện.
- Không hiển thị enum thô cho người dùng.
- Không nhân bản toàn bộ logic nghiệp vụ từ backend.
- Hiển thị đầy đủ trạng thái loading, empty và error.
- Kiểm tra quyền theo vai trò trên giao diện.
- Vẫn phải dựa vào backend để bảo vệ thao tác.
- Không sử dụng `any` tùy tiện.
- Không gọi API trực tiếp từ nhiều component không liên quan.
- Không tải toàn bộ dữ liệu khi chỉ cần một tuần hoặc một bộ lọc.
- Không dùng màu sắc làm cách duy nhất để truyền đạt trạng thái.
- Không thêm giao diện sinh viên ngoài phạm vi.

Mọi form cần:

- Có nhãn.
- Đánh dấu trường bắt buộc.
- Hiển thị lỗi gần trường nhập.
- Giữ lại dữ liệu khi có lỗi.
- Ngăn gửi lặp.
- Xác nhận trước thao tác quan trọng.

---

## 13. Quy tắc đối với thuật toán

Khi thay đổi thuật toán:

- Đọc `backend/app/algorithms/AGENTS.md`.
- Đọc `backend/app/algorithms/genetic/AGENTS.md` nếu sửa GA.
- Không để thuật toán đọc CSV trực tiếp.
- Không để thuật toán truy cập database.
- Không phụ thuộc HTTP hoặc framework API.
- Nhận dữ liệu đã được kiểm tra và chuẩn hóa.
- Trả kết quả có kiểu rõ ràng.
- Sử dụng một gene cho lịch cơ sở của một lớp học phần trong MVP.
- Không thay đổi giảng viên đã phân công.
- Không sinh khung tiết tùy ý.
- Không mặc định phạt Thứ Bảy hoặc Chủ nhật.
- Kiểm tra xung đột bằng khoảng tiết thực tế.
- Không chỉ so sánh `slot_code`.
- Phòng không đủ sức chứa là vi phạm cứng.
- Phòng quá lớn chỉ là vấn đề mềm.
- Ghi nhận seed để tái lập.
- Trả chi tiết vi phạm thay vì một fitness không giải thích.

Một phương án hợp lệ luôn phải được xếp trên phương án có vi phạm cứng.

---

## 14. Quy tắc kiểm thử

Mọi thay đổi nghiệp vụ hoặc sửa lỗi phải có kiểm thử phù hợp.

### 14.1. Kiểm thử backend

Nên bao gồm:

- Unit test.
- Service test.
- API test.
- Authorization test.
- Validation test.
- Database integration test khi cần.

### 14.2. Kiểm thử frontend

Nên bao gồm:

- Component behavior.
- Form validation.
- Role-based navigation.
- Loading state.
- Empty state.
- Error state.
- API success và failure.
- Các luồng quan trọng từ góc nhìn người dùng.

### 14.3. Kiểm thử thuật toán

Tối thiểu cần kiểm tra:

- Trùng giảng viên.
- Trùng phòng.
- Chồng một phần khoảng tiết.
- Tiết 1–5 với tiết 2–6.
- Hai ca liên tiếp không bị xem là chồng.
- Lớp lý thuyết với ca ba tiết.
- Lớp thực hành với ca năm hoặc sáu tiết.
- Lớp tích hợp.
- Loại phòng tương thích.
- Phòng không đủ sức chứa.
- Phòng lớn hợp lệ nhưng bị phạt mềm khi phù hợp.
- Thứ Bảy và Chủ nhật hợp lệ.
- Nguyện vọng cuối tuần.
- Hạn chế bắt buộc của giảng viên.
- Crossover giữ đủ lớp học phần.
- Mutation không đổi giảng viên.
- Seed cố định tạo kết quả tái lập.
- Phương án hợp lệ tốt hơn phương án vi phạm cứng.

### 14.4. Test dữ liệu nhỏ

Các quy tắc mới nên được kiểm tra trước với dữ liệu nhỏ có thể tính bằng tay.

Ví dụ:

- 2 giảng viên.
- 3 phòng.
- 5 lớp học phần.
- 4 khung giờ.

Không chỉ kiểm thử bằng dữ liệu lớn mà không biết đáp án mong đợi.

### 14.5. Không bỏ qua test

Không được:

- Xóa test đang thất bại chỉ để pipeline xanh.
- Đánh dấu skip mà không ghi lý do.
- Giảm assertion để che lỗi.
- Sửa dữ liệu test trái nghiệp vụ.
- Bắt mọi exception và coi là thành công.

---

## 15. Quy tắc dữ liệu CSV

Nhóm tự thiết kế cấu trúc CSV cho dự án.

Quy ước mặc định:

- Mã hóa UTF-8.
- Dùng dấu phẩy để phân tách.
- Có dòng tiêu đề.
- Tên cột ổn định.
- Mã định danh duy nhất.
- Ngày có định dạng thống nhất.
- Không bỏ qua giá trị sai một cách im lặng.

Các nhóm dữ liệu có thể gồm:

- Giảng viên.
- Nguyện vọng giảng viên.
- Hạn chế cố định của giảng viên.
- Học phần.
- Lớp học phần.
- Phân công giảng dạy.
- Phòng học.
- Thời gian phòng không sử dụng.
- Khung giờ.
- Lịch học kỳ.
- Ngày lễ.
- Phân đoạn lịch.

Khi thay đổi cấu trúc CSV:

1. Cập nhật tài liệu mô tả cột.
2. Cập nhật file mẫu.
3. Cập nhật bộ kiểm tra dữ liệu.
4. Cập nhật schema backend.
5. Cập nhật frontend upload hoặc preview.
6. Cập nhật test.
7. Ghi rõ breaking change trong Pull Request.

Lỗi CSV phải chỉ rõ:

- Tệp.
- Dòng.
- Cột.
- Giá trị.
- Nguyên nhân.
- Hướng xử lý khi có thể.

Không commit dữ liệu thật chưa được phép sử dụng.

---

## 16. Quy tắc tài liệu

Tài liệu phải được cập nhật khi thay đổi:

- Nghiệp vụ.
- API.
- Cấu trúc CSV.
- Cấu trúc thư mục.
- Cách cài đặt.
- Cách chạy.
- Quy trình đóng góp.
- Quy trình kiểm thử.
- Tham số thuật toán.
- Phạm vi chức năng.

Các file có thể cần cập nhật:

```text
README.md
CONTRIBUTING.md
AGENTS.md
backend/AGENTS.md
frontend/AGENTS.md
backend/app/algorithms/AGENTS.md
backend/app/algorithms/genetic/AGENTS.md
docs/requirements/*
data/samples/README.md
```

Không cập nhật số phiên bản URS hoặc SRS mà không thêm lịch sử thay đổi trong
tài liệu.

Không xóa nội dung còn giá trị lịch sử nếu chưa có lý do rõ ràng.

Khi thay đổi đường dẫn file tài liệu, cần cập nhật liên kết trong `README.md`.

---

## 17. Bảo mật và dữ liệu riêng tư

Không commit:

- Mật khẩu.
- API key.
- Access token.
- Refresh token.
- Private key.
- Chuỗi kết nối database thật.
- File `.env` thật.
- Cookie phiên đăng nhập.
- Tài khoản quản trị thật.
- Dữ liệu sinh viên thật.
- Dữ liệu giảng viên nhạy cảm chưa được phép.
- File sao lưu database chứa dữ liệu riêng tư.

Chỉ commit:

```text
.env.example
```

File `.env.example` chỉ chứa:

- Tên biến.
- Giá trị giả.
- Hướng dẫn cấu hình.

Ví dụ:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/timetable
SECRET_KEY=replace-with-a-secure-secret
```

Không đặt bí mật thật trong ví dụ.

### 17.1. Dữ liệu mẫu

Dữ liệu mẫu phải:

- Là dữ liệu giả lập.
- Hoặc đã được ẩn danh.
- Không chứa thông tin nhận dạng cá nhân không cần thiết.
- Không chứa email, số điện thoại hoặc mã sinh viên thật.
- Không chứa mật khẩu thật.

### 17.2. Khi phát hiện bí mật đã commit

Thực hiện ngay:

1. Không chỉ xóa file ở commit mới.
2. Thông báo cho nhóm.
3. Thu hồi hoặc thay đổi bí mật.
4. Kiểm tra lịch sử Git.
5. Làm sạch lịch sử khi cần.
6. Kiểm tra log và Pull Request.
7. Cập nhật `.gitignore`.

---

## 18. Quy tắc merge

Nhánh `main` phải luôn ở trạng thái có thể sử dụng.

Chỉ merge khi:

- Pull Request đã được review.
- Không còn nhận xét blocking.
- Không có xung đột.
- Test liên quan đã chạy thành công.
- Formatter và linter thành công.
- Type checking thành công khi có.
- Không có dữ liệu nhạy cảm.
- Tài liệu đã được cập nhật khi cần.
- Thay đổi đúng phạm vi.
- Người tạo Pull Request đã kiểm tra lại diff cuối cùng.

Ưu tiên `Squash and merge` đối với Pull Request có nhiều commit sửa review nhỏ.

Commit squash cuối cùng nên có tên rõ ràng.

Ví dụ:

```text
feat: add timetable CSV import
```

Không merge một Pull Request chỉ vì:

- Đã tồn tại lâu.
- Người thực hiện cần chuyển sang công việc khác.
- Chỉ còn lỗi test nhỏ.
- “Chạy được trên máy em”.
- Không ai muốn review thêm.

### 18.1. Sau khi merge

Cập nhật máy cục bộ:

```powershell
git switch main
git pull origin main
```

Xóa branch cục bộ đã hoàn thành:

```powershell
git branch -d docs/TKB-003-update-contributing
```

Xóa branch từ xa nếu GitHub chưa tự xóa:

```powershell
git push origin --delete docs/TKB-003-update-contributing
```

Không tiếp tục dùng lại branch đã merge cho công việc mới.

---

## 19. Checklist trước khi hoàn thành

### 19.1. Checklist chung

- [ ] Công việc đúng mục tiêu của branch.
- [ ] Đã đọc URS và SRS liên quan.
- [ ] Đã đọc các file `AGENTS.md` áp dụng.
- [ ] Không mở rộng phạm vi ngoài yêu cầu.
- [ ] Không có file thay đổi ngoài dự kiến.
- [ ] Không có debug code.
- [ ] Không có dữ liệu nhạy cảm.
- [ ] Không có secret.
- [ ] Đã kiểm tra `git diff`.
- [ ] Commit message rõ ràng.

### 19.2. Checklist nghiệp vụ

- [ ] Thay đổi tuân theo URS và SRS mới nhất.
- [ ] Không làm yếu ràng buộc cứng.
- [ ] Thứ Bảy và Chủ nhật vẫn là ngày dạy hợp lệ.
- [ ] Quyền Phòng đào tạo và Giảng viên vẫn chính xác.
- [ ] Không thêm chức năng sinh viên ngoài phạm vi.
- [ ] Phân công giảng viên vẫn là dữ liệu đầu vào cố định.
- [ ] Sức chứa phòng vẫn là ràng buộc cứng.
- [ ] Phòng lớn cho lớp nhỏ chỉ là cảnh báo hoặc điểm mềm.
- [ ] Xung đột sử dụng khoảng tiết thực tế.
- [ ] Ngày lễ không tự động biến thành buổi tạm ngưng.
- [ ] Học bù không tự động tìm lịch rảnh của sinh viên.

### 19.3. Checklist code

- [ ] Code có kiểu dữ liệu rõ ràng.
- [ ] Không có logic nghiệp vụ bị nhân bản.
- [ ] Không có hàm quá lớn không cần thiết.
- [ ] Không có mutable global state không kiểm soát.
- [ ] Không có broad exception bị nuốt.
- [ ] Thông báo lỗi có thể hành động được.
- [ ] API kiểm tra quyền ở backend.
- [ ] Frontend xử lý loading, empty và error.
- [ ] Thuật toán độc lập với HTTP, ORM và CSV.

### 19.4. Checklist test

- [ ] Đã thêm hoặc cập nhật test.
- [ ] Test mới thực sự kiểm tra hành vi.
- [ ] Test cũ không bị xóa để che lỗi.
- [ ] Test với seed cố định khi có ngẫu nhiên.
- [ ] Test trường hợp thành công.
- [ ] Test trường hợp thất bại.
- [ ] Test biên.
- [ ] Test phân quyền khi có liên quan.
- [ ] Tất cả test liên quan đều chạy thành công.

### 19.5. Checklist tài liệu và dữ liệu

- [ ] URS/SRS đã cập nhật khi thay đổi nghiệp vụ.
- [ ] README đã cập nhật khi thay đổi tổng quan.
- [ ] AGENTS.md đã cập nhật khi thay đổi hướng dẫn.
- [ ] CSV mẫu đã cập nhật khi thay đổi schema.
- [ ] API contract đã được tài liệu hóa.
- [ ] Đường dẫn tài liệu vẫn đúng.
- [ ] Không có dữ liệu thật chưa được phép.

### 19.6. Checklist Pull Request

- [ ] Tiêu đề PR rõ ràng.
- [ ] Có mô tả mục tiêu.
- [ ] Có mô tả thay đổi.
- [ ] Có hướng dẫn kiểm thử.
- [ ] Có ảnh giao diện khi cần.
- [ ] Có ghi ảnh hưởng đến tài liệu.
- [ ] Có ghi breaking change khi có.
- [ ] Đã tự review diff.
- [ ] Đã yêu cầu thành viên khác review.

---

## 20. Các hành vi không được phép

Không thực hiện các hành vi sau:

- Push trực tiếp lên `main`.
- Force push lên `main`.
- Merge khi chưa review.
- Commit bí mật hoặc dữ liệu riêng tư.
- Xóa test để che lỗi.
- Bỏ qua lỗi kiểm thử mà không giải thích.
- Tự ý đổi ràng buộc cứng thành mềm.
- Tự ý thêm chức năng sinh viên.
- Tự ý thêm quy trình ngoài URS/SRS.
- Để frontend là nơi duy nhất kiểm tra quyền.
- Để thuật toán đọc trực tiếp CSV.
- Để thuật toán truy cập database.
- Dùng `slot_code` làm cách duy nhất để kiểm tra chồng thời gian.
- Phạt Thứ Bảy hoặc Chủ nhật mặc định.
- Khóa phòng lớn chỉ cho môn đại cương.
- Cho phép phòng nhỏ hơn sĩ số chỉ bằng cảnh báo.
- Thay đổi giảng viên đã phân công trong GA.
- Tự động dời buổi ngày lễ mà không có yêu cầu.
- Tự động tìm lịch rảnh của sinh viên.
- Gộp nhiều công việc không liên quan vào một Pull Request.
- Dùng commit message không có ý nghĩa.
- Đưa file build hoặc file tạm vào repository.
- Bỏ qua `AGENTS.md` gần nhất.
- Tự suy diễn yêu cầu chưa được xác nhận.

---

## Tóm tắt quy trình

```text
1. Cập nhật main
2. Tạo branch theo mã công việc
3. Đọc URS, SRS và AGENTS.md
4. Thực hiện thay đổi đúng phạm vi
5. Thêm hoặc cập nhật test
6. Chạy kiểm tra
7. Xem lại git diff
8. Commit rõ ràng
9. Push branch
10. Tạo Pull Request
11. Review và sửa góp ý
12. Merge khi mọi điều kiện đạt
13. Cập nhật main và xóa branch cũ
```

Mục tiêu của quy trình này không chỉ là tránh xung đột Git mà còn bảo đảm mã
nguồn, tài liệu và nghiệp vụ của dự án luôn đồng bộ.
