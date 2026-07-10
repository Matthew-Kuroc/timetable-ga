# Hướng dẫn đóng góp cho dự án Timetable GA

## 1. Mục đích

Tài liệu này quy định cách các thành viên đóng góp mã nguồn, tài liệu, dữ liệu mẫu và các thay đổi khác vào repository `timetable-ga`.

Mục tiêu của quy trình là:

- Không làm việc trực tiếp trên nhánh `main`.
- Mỗi thay đổi có thể truy vết về một công việc cụ thể.
- Hạn chế xung đột giữa các thành viên.
- Mọi thay đổi đều được kiểm tra trước khi hợp nhất.
- Không đưa mật khẩu, token hoặc dữ liệu nhạy cảm lên GitHub.
- Giữ lịch sử Git rõ ràng và dễ hiểu.
- Bảo đảm mã nguồn đáp ứng yêu cầu và có thể kiểm thử.

Tất cả thành viên trong nhóm cần đọc tài liệu này trước khi bắt đầu làm việc.

---

## 2. Tổng quan quy trình làm việc

Quy trình chuẩn của một công việc:

```text
Tạo hoặc nhận GitHub Issue
        ↓
Cập nhật nhánh main
        ↓
Tạo branch từ main
        ↓
Code và kiểm thử
        ↓
Commit thay đổi
        ↓
Push branch lên GitHub
        ↓
Mở Pull Request
        ↓
Thành viên khác review
        ↓
Sửa theo góp ý nếu cần
        ↓
Test và CI thành công
        ↓
Merge vào main
```

Không được bỏ qua Pull Request bằng cách push trực tiếp lên `main`.

---

## 3. Chuẩn bị môi trường

### 3.1. Yêu cầu tối thiểu

Thành viên cần cài đặt:

- Git.
- Visual Studio Code hoặc IDE phù hợp.
- Tài khoản GitHub.
- Quyền truy cập repository.
- Các công nghệ của dự án sau khi được thiết lập:
  - Python.
  - Node.js.
  - PostgreSQL.
  - Docker và Docker Compose nếu được sử dụng.

Kiểm tra Git:

```bash
git --version
```

Cấu hình tên và email:

```bash
git config --global user.name "Tên hoặc GitHub username"
git config --global user.email "email@example.com"
```

Khuyến khích sử dụng email `noreply` của GitHub nếu không muốn công khai email cá nhân.

Kiểm tra cấu hình:

```bash
git config --global user.name
git config --global user.email
```

---

## 4. Clone repository

Clone repository về máy:

```bash
git clone https://github.com/Matthew-Kuroc/timetable-ga.git
cd timetable-ga
```

Kiểm tra remote:

```bash
git remote -v
```

Kiểm tra trạng thái:

```bash
git status
```

Kiểm tra nhánh hiện tại:

```bash
git branch --show-current
```

Sau khi clone, nhánh mặc định phải là:

```text
main
```

---

## 5. Không code trực tiếp trên main

Nhánh `main` được dùng để lưu phiên bản đã được review và tương đối ổn định.

Không thực hiện thay đổi trực tiếp trên `main`.

Trước khi bắt đầu công việc mới:

```bash
git switch main
git pull origin main
```

Sau đó tạo branch mới:

```bash
git switch -c feature/TKB-010-upload-csv
```

Mỗi branch nên phục vụ một Issue hoặc một nhiệm vụ cụ thể.

---

## 6. Quy ước tên branch

Cấu trúc chung:

```text
<loại>/TKB-<mã-issue>-<mô-tả-ngắn>
```

Tên branch:

- Viết bằng chữ thường.
- Không dùng khoảng trắng.
- Dùng dấu gạch ngang `-` để phân tách từ.
- Mô tả ngắn nhưng rõ ràng.
- Không dùng tên thành viên làm tên branch.

### 6.1. Branch chức năng

```text
feature/TKB-010-upload-csv
feature/TKB-011-user-login
feature/TKB-012-weekly-timetable-view
feature/TKB-013-run-genetic-algorithm
```

### 6.2. Branch sửa lỗi

```text
bugfix/TKB-020-room-time-conflict
bugfix/TKB-021-invalid-csv-header
bugfix/TKB-022-lecturer-permission
```

### 6.3. Branch tài liệu

```text
docs/TKB-030-update-readme
docs/TKB-031-add-srs
docs/TKB-032-update-api-documentation
```

### 6.4. Branch kiểm thử

```text
test/TKB-040-add-fitness-tests
test/TKB-041-add-upload-api-tests
```

### 6.5. Branch refactor

```text
refactor/TKB-050-split-fitness-evaluator
refactor/TKB-051-extract-schedule-service
```

### 6.6. Branch cấu hình

```text
chore/TKB-060-initialize-project
chore/TKB-061-configure-pytest
chore/TKB-062-add-github-actions
```

Không nên sử dụng:

```text
phi-branch
huy-code
tien
test-moi
branch-1
```

---

## 7. GitHub Issue

Mỗi chức năng, lỗi hoặc công việc đáng kể nên có một GitHub Issue.

Issue nên có:

- Tiêu đề rõ ràng.
- Mục tiêu.
- Mô tả yêu cầu.
- Tiêu chí chấp nhận.
- Người phụ trách.
- Nhãn phù hợp.
- Tài liệu liên quan.
- Các điểm chưa rõ.

Ví dụ:

```markdown
# [TKB-010] Nhập dữ liệu phân công giảng dạy từ CSV

## Mục tiêu

Cho phép Phòng đào tạo tải file phân công giảng dạy lên hệ thống.

## Yêu cầu

- Chỉ chấp nhận file CSV.
- Kiểm tra các cột bắt buộc.
- Hiển thị dữ liệu xem trước.
- Hiển thị lỗi theo dòng và cột.
- Không lưu dữ liệu lỗi.

## Tiêu chí chấp nhận

- File hợp lệ được đọc thành công.
- File thiếu cột bị từ chối.
- Lỗi hiển thị tên cột và số dòng.
- Có test cho trường hợp hợp lệ và không hợp lệ.
```

Không bắt đầu một chức năng lớn khi chưa xác định rõ phạm vi.

---

## 8. Làm việc trên branch

Sau khi tạo branch, kiểm tra:

```bash
git status
git branch --show-current
```

Trong quá trình làm việc, thường xuyên kiểm tra:

```bash
git status
```

Xem thay đổi chưa được stage:

```bash
git diff
```

Xem thay đổi đã được stage:

```bash
git diff --staged
```

Không sử dụng `git add .` một cách máy móc nếu thư mục đang có nhiều file không liên quan.

Có thể add từng file:

```bash
git add README.md
git add backend/app/services/import_service.py
```

Hoặc add theo thư mục:

```bash
git add backend/tests/
```

Trước khi commit, luôn chạy:

```bash
git status
```

---

## 9. Quy ước commit message

Dự án sử dụng cấu trúc commit gần với Conventional Commits:

```text
<type>(<scope>): <mô tả ngắn>
```

Phần `scope` có thể bỏ nếu không cần.

### 9.1. Các loại commit

| Loại       | Ý nghĩa                                 |
| ---------- | --------------------------------------- |
| `feat`     | Thêm chức năng mới                      |
| `fix`      | Sửa lỗi                                 |
| `docs`     | Thay đổi tài liệu                       |
| `test`     | Thêm hoặc sửa kiểm thử                  |
| `refactor` | Tái cấu trúc nhưng không đổi hành vi    |
| `chore`    | Cấu hình hoặc công việc hỗ trợ          |
| `perf`     | Cải thiện hiệu năng                     |
| `build`    | Thay đổi hệ thống build hoặc dependency |
| `ci`       | Thay đổi GitHub Actions hoặc CI         |
| `style`    | Thay đổi format không ảnh hưởng logic   |

### 9.2. Ví dụ commit tốt

```text
feat(upload): validate required CSV columns
feat(auth): add lecturer login endpoint
fix(schedule): prevent lecturer time conflicts
fix(export): preserve Vietnamese characters in CSV
test(fitness): add room capacity constraint cases
docs(readme): update project scope
refactor(ga): separate hard and soft penalties
chore: initialize project structure
ci: add backend test workflow
```

### 9.3. Commit không nên sử dụng

```text
update
fix
sửa code
code mới
test
done
final
update lần 2
```

### 9.4. Nguyên tắc commit

Một commit nên:

- Có một mục đích chính.
- Không chứa nhiều chức năng không liên quan.
- Không chứa file tạm.
- Không chứa file bí mật.
- Có thể đọc hiểu qua commit message.
- Không làm hỏng build hoặc test một cách có chủ ý.

Không cần tạo commit cho từng dòng code. Tuy nhiên, cũng không nên dồn toàn bộ công việc trong nhiều ngày vào một commit duy nhất.

---

## 10. Push branch

Lần đầu push một branch:

```bash
git push -u origin feature/TKB-010-upload-csv
```

Các lần sau:

```bash
git push
```

Kiểm tra branch trên GitHub trước khi mở Pull Request.

Không push trực tiếp:

```bash
git push origin main
```

---

## 11. Pull Request

Sau khi hoàn thành công việc, mở Pull Request từ branch hiện tại vào `main`.

### 11.1. Tiêu đề Pull Request

Tiêu đề nên tương tự commit chính:

```text
feat(upload): add CSV import validation
```

Hoặc:

```text
[TKB-010] Thêm chức năng nhập file CSV
```

### 11.2. Nội dung Pull Request

Mẫu đề xuất:

```markdown
## Issue liên quan

Closes #10

## Mục tiêu

Cho phép Phòng đào tạo tải và kiểm tra file CSV phân công giảng dạy.

## Nội dung thay đổi

- Thêm API upload CSV.
- Kiểm tra định dạng file.
- Kiểm tra các cột bắt buộc.
- Trả lỗi theo dòng và cột.
- Thêm unit test.

## Cách kiểm thử

1. Khởi chạy backend.
2. Upload file CSV hợp lệ.
3. Upload file thiếu cột `lecturer_code`.
4. Kiểm tra nội dung lỗi trả về.

## Kết quả kiểm thử

- `pytest`: thành công.
- `ruff check .`: thành công.

## Checklist

- [ ] Đáp ứng acceptance criteria.
- [ ] Không code trực tiếp trên main.
- [ ] Đã thêm hoặc cập nhật test.
- [ ] Test cũ không bị hỏng.
- [ ] Không commit `.env`.
- [ ] Không chứa mật khẩu hoặc token.
- [ ] Đã cập nhật tài liệu nếu hành vi thay đổi.
- [ ] Không có thay đổi ngoài phạm vi Issue.

## Ảnh chụp màn hình

Thêm ảnh nếu Pull Request thay đổi giao diện.

## Lưu ý hoặc rủi ro

Nêu các điểm còn thiếu hoặc cần xác nhận.
```

Không mở Pull Request có quá nhiều chức năng không liên quan.

---

## 12. Review code

Một Pull Request phải được ít nhất một thành viên khác kiểm tra trước khi merge, nếu cấu hình repository cho phép.

Người review cần kiểm tra:

- Thay đổi có đúng Issue không?
- Có đáp ứng acceptance criteria không?
- Có vượt phạm vi không?
- Có vi phạm URS hoặc SRS không?
- Có tự thêm quy tắc nghiệp vụ không?
- Có test không?
- Test có kiểm tra đúng hành vi không?
- Có làm hỏng chức năng cũ không?
- Có lỗi bảo mật không?
- Có commit secret không?
- Có kiểm tra quyền ở backend không?
- Có dependency mới không?
- Có cập nhật tài liệu khi cần không?
- Code có dễ đọc không?
- Có thay đổi file không liên quan không?

### 12.1. Các loại phản hồi review

- **Approve:** Đồng ý merge.
- **Request changes:** Cần sửa trước khi merge.
- **Comment:** Góp ý hoặc đặt câu hỏi.

Không approve chỉ vì người mở PR là thành viên cùng nhóm.

### 12.2. Khi được yêu cầu sửa

Người tạo PR:

1. Đọc từng comment.
2. Trao đổi nếu chưa rõ.
3. Sửa trên cùng branch.
4. Commit và push tiếp.
5. Trả lời comment.
6. Yêu cầu review lại.

Không cần đóng PR và tạo PR mới chỉ vì có thay đổi nhỏ.

---

## 13. Kiểm thử trước khi merge

Các lệnh chính thức sẽ được cập nhật sau khi backend và frontend được khởi tạo.

### 13.1. Backend dự kiến

```bash
cd backend
pytest
ruff check .
ruff format --check .
```

### 13.2. Frontend dự kiến

```bash
cd frontend
npm run lint
npm test
npm run build
```

### 13.3. Nguyên tắc

Không ghi trong PR rằng kiểm thử thành công nếu chưa thật sự chạy.

Nếu chưa thể chạy test, phải ghi rõ:

- Test nào chưa chạy.
- Vì sao chưa chạy.
- Người review cần thực hiện bước nào.
- Rủi ro còn lại.

---

## 14. Definition of Done

Một Issue chỉ được xem là hoàn thành khi:

- Đáp ứng đầy đủ acceptance criteria.
- Code nằm trên branch riêng.
- Không vượt phạm vi Issue.
- Có test phù hợp.
- Test mới thành công.
- Test cũ không bị hỏng.
- Lint hoặc build thành công nếu đã cấu hình.
- Không có secret.
- Không có file debug không cần thiết.
- Không có dữ liệu cá nhân trái phép.
- Xử lý được các trường hợp lỗi quan trọng.
- Phân quyền được kiểm tra ở backend nếu có liên quan.
- Tài liệu được cập nhật khi hành vi thay đổi.
- Pull Request được review.
- Các yêu cầu sửa quan trọng đã được xử lý.
- Pull Request được merge vào `main`.

Chỉ code xong nhưng chưa test và chưa review chưa được xem là hoàn thành.

---

## 15. Merge Pull Request

Chỉ merge khi:

- Pull Request đã được review.
- Các comment quan trọng đã được xử lý.
- Test thành công.
- Không còn conflict.
- Không có secret hoặc dữ liệu nhạy cảm.
- Thay đổi đúng phạm vi.

Với nhóm nhỏ, khuyến khích sử dụng:

```text
Squash and merge
```

Cách này giúp lịch sử `main` gọn hơn, mỗi Pull Request thường trở thành một commit chính.

Có thể sử dụng `Merge commit` khi cần giữ toàn bộ lịch sử branch, nhưng nhóm cần thống nhất trước.

Sau khi merge, branch đã hoàn thành có thể được xóa trên GitHub.

---

## 16. Cập nhật main sau khi Pull Request được merge

Sau khi một PR được merge:

```bash
git switch main
git pull origin main
```

Xóa branch local đã hoàn thành:

```bash
git branch -d feature/TKB-010-upload-csv
```

Nếu Git từ chối xóa vì branch chưa được nhận diện là đã merge, kiểm tra kỹ trước khi dùng:

```bash
git branch -D feature/TKB-010-upload-csv
```

Không dùng `-D` khi chưa chắc chắn rằng thay đổi đã được merge hoặc không còn cần thiết.

---

## 17. Cập nhật branch đang làm việc

Nếu `main` có thay đổi mới trong khi bạn đang làm:

```bash
git switch main
git pull origin main
git switch feature/TKB-010-upload-csv
git merge main
```

Hoặc sử dụng rebase nếu nhóm đã hiểu và thống nhất:

```bash
git rebase main
```

Trong giai đoạn đầu, nhóm có thể ưu tiên `merge main` vì dễ hiểu và ít rủi ro hơn.

Không tự ý rebase branch của thành viên khác.

---

## 18. Xử lý merge conflict

Khi có conflict, Git sẽ đánh dấu:

```text
<<<<<<< HEAD
Nội dung trên branch hiện tại
=======
Nội dung từ branch được merge
>>>>>>> main
```

Quy trình xử lý:

1. Đọc cả hai phần thay đổi.
2. Không xóa một phía theo cảm tính.
3. Trao đổi với người đã sửa file nếu cần.
4. Giữ lại nội dung đúng hoặc kết hợp hai phần.
5. Xóa các dấu conflict.
6. Lưu file.
7. Chạy test.
8. Add và commit.

Ví dụ:

```bash
git status
git add path/to/conflicted-file
git commit
```

Không sử dụng:

```bash
git reset --hard
```

chỉ để né conflict.

Không dùng công cụ tự động chọn “Accept Current” hoặc “Accept Incoming” nếu chưa hiểu nội dung.

---

## 19. File không được commit

Không commit:

```text
.env
.env.local
.env.production
*.pem
*.key
credentials.json
secret.json
access-token.txt
node_modules/
.venv/
__pycache__/
dist/
build/
coverage/
database dump có dữ liệu thật
file cấu hình chứa mật khẩu
dữ liệu cá nhân chưa được phép sử dụng
```

Danh sách cụ thể phải được cập nhật trong `.gitignore`.

Nếu lỡ add một file chưa commit:

```bash
git restore --staged .env
```

Nếu file bí mật đã được commit hoặc push, phải báo ngay cho nhóm. Chỉ xóa file khỏi commit là chưa đủ; token hoặc mật khẩu phải được thay mới.

---

## 20. Quản lý dependency

Không thêm dependency tùy tiện.

Trước khi thêm dependency lớn, cần giải thích:

- Dependency giải quyết vấn đề gì?
- Có thể dùng thư viện hiện có không?
- Dependency có được duy trì không?
- Có ảnh hưởng bảo mật không?
- Có làm tăng độ phức tạp của dự án không?

Sau khi thêm dependency:

- Cập nhật file dependency.
- Commit lock file phù hợp.
- Cập nhật hướng dẫn cài đặt nếu cần.
- Kiểm tra build và test.

Không cài thư viện trên máy nhưng quên cập nhật file dependency.

---

## 21. Database và migration

Khi hệ thống database được thiết lập:

- Mọi thay đổi schema phải đi qua migration.
- Không yêu cầu thành viên sửa database bằng tay.
- Không tự chỉnh sửa migration đã được dùng chung.
- Tạo migration mới cho thay đổi tiếp theo.
- Review kỹ migration có xóa dữ liệu hoặc cột hay không.
- Các thao tác có nguy cơ mất dữ liệu cần được thảo luận trước.

Pull Request có thay đổi database phải ghi rõ:

- Bảng hoặc cột thay đổi.
- Migration được thêm.
- Cách chạy migration.
- Có ảnh hưởng dữ liệu cũ hay không.

---

## 22. Quy tắc tài liệu

Khi thay đổi hành vi hệ thống, cần xem xét cập nhật:

- `README.md`.
- URS.
- SRS.
- Tài liệu API.
- Tài liệu database.
- Tài liệu thuật toán.
- Hướng dẫn kiểm thử.

Không mô tả một chức năng dự kiến như thể đã hoàn thành.

Sử dụng rõ các trạng thái:

- Dự kiến.
- Đang phát triển.
- Đã hoàn thành.
- Cần xác nhận.

---

## 23. Sử dụng Codex hoặc công cụ AI

Có thể sử dụng Codex hoặc công cụ AI để hỗ trợ:

- Phân tích Issue.
- Đề xuất kế hoạch.
- Viết code.
- Viết test.
- Review code.
- Viết tài liệu.
- Giải thích lỗi.

Tuy nhiên, thành viên vẫn chịu trách nhiệm:

- Đọc và hiểu code được tạo.
- Kiểm tra code đúng yêu cầu.
- Chạy test.
- Kiểm tra bảo mật.
- Không chấp nhận code chỉ vì AI tạo ra.
- Không để AI tự phát minh nghiệp vụ.
- Không đưa secret hoặc dữ liệu nhạy cảm vào prompt.

Codex phải tuân theo các file `AGENTS.md` áp dụng cho thư mục đang làm việc.

---

## 24. Các thao tác Git nguy hiểm

Không chạy các lệnh sau khi chưa hiểu rõ và chưa được xác nhận:

```bash
git reset --hard
git clean -fd
git restore .
git checkout -- .
git push --force
git branch -D <branch>
```

Các lệnh này có thể làm mất thay đổi.

Khi gặp vấn đề Git, ưu tiên:

1. Chạy `git status`.
2. Chụp hoặc sao chép kết quả.
3. Trao đổi với nhóm.
4. Sao lưu file nếu cần.
5. Chỉ chạy lệnh xử lý sau khi hiểu tác động.

---

## 25. Quy tắc giao tiếp trong nhóm

Khi bắt đầu một Issue:

- Gán người phụ trách.
- Thông báo trong nhóm.
- Không để hai người cùng làm một Issue mà không phối hợp.

Khi bị chặn:

- Gắn trạng thái `blocked`.
- Ghi rõ nguyên nhân.
- Báo sớm thay vì chờ đến gần hạn.

Khi phát hiện yêu cầu chưa rõ:

- Đưa vào Issue.
- Nêu các phương án.
- Không tự quyết định rồi triển khai âm thầm.

Khi thay đổi phạm vi:

- Cập nhật Issue.
- Cập nhật tài liệu liên quan.
- Thống nhất với nhóm và giảng viên hướng dẫn nếu cần.

---

## 26. Checklist trước khi mở Pull Request

Trước khi mở PR, kiểm tra:

```text
[ ] Tôi đang ở đúng branch.
[ ] Branch được tạo từ main tương đối mới.
[ ] Thay đổi đúng phạm vi Issue.
[ ] Không có file bí mật.
[ ] Không có file tạm hoặc debug.
[ ] Commit message rõ ràng.
[ ] Code đã được kiểm tra.
[ ] Test liên quan đã được chạy.
[ ] Không làm hỏng test cũ.
[ ] Tài liệu được cập nhật nếu cần.
[ ] Pull Request có hướng dẫn kiểm thử.
[ ] Các giả định và rủi ro đã được ghi rõ.
```

---

## 27. Checklist dành cho người review

```text
[ ] PR giải quyết đúng Issue.
[ ] Acceptance criteria được đáp ứng.
[ ] Không vượt phạm vi.
[ ] Không tự thêm quy tắc nghiệp vụ.
[ ] Không chứa secret.
[ ] Có test phù hợp.
[ ] Test kiểm tra cả trường hợp lỗi.
[ ] Phân quyền được xử lý đúng.
[ ] Không có thay đổi database nguy hiểm.
[ ] Không có dependency không cần thiết.
[ ] Code dễ hiểu.
[ ] Không lặp logic.
[ ] Tài liệu được cập nhật.
[ ] Có thể merge an toàn.
```

---

## 28. Cập nhật tài liệu này

`CONTRIBUTING.md` cần được cập nhật khi:

- Quy trình Git thay đổi.
- Nhóm thống nhất cách merge khác.
- Có lệnh build hoặc test chính thức.
- Có quy chuẩn code mới.
- Có quy trình release.
- Có lỗi lặp lại cần phòng tránh.

Không thêm quy tắc chỉ áp dụng cho một Issue duy nhất.

Quy tắc chuyên biệt nên được đặt trong:

- `backend/AGENTS.md`.
- `frontend/AGENTS.md`.
- `backend/app/algorithms/genetic/AGENTS.md`.
- Tài liệu tương ứng trong `docs/`.

---

## 29. Nguyên tắc cuối cùng

- Không code trực tiếp trên `main`.
- Mỗi công việc dùng một branch.
- Mỗi thay đổi quan trọng cần một Issue.
- Mọi thay đổi phải đi qua Pull Request.
- Một thành viên khác nên review.
- Không merge khi test thất bại.
- Không commit secret.
- Không tự phát minh quy tắc nghiệp vụ.
- Không dùng lệnh Git nguy hiểm khi chưa hiểu.
- Chất lượng và khả năng kiểm tra quan trọng hơn việc hoàn thành thật nhanh.
