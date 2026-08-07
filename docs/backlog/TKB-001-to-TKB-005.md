# Ban Giao Va Backlog Hien Tai

Cap nhat: 07/08/2026. Day la tai lieu ban giao ky thuat cho phien Codex sau.
URS/SRS trong `docs/requirements/` van la nguon yeu cau nghiep vu chinh thuc.

## Cach Bat Dau Phien Moi

1. Doc `AGENTS.md`, sau do doc `backend/AGENTS.md` hoac `frontend/AGENTS.md`
   truoc khi sua file thuoc khu vuc tuong ung.
2. Doc phan **Trang Thai Hien Tai** va **Backlog Uu Tien** ben duoi.
3. Doi chieu `docs/requirements/UR.md` va `docs/requirements/SRS.md` truoc khi
   thay doi quy tac nghiep vu.
4. Chay kiem thu backend:

```powershell
$env:PYTHONPATH='.'
python -m pytest -q backend/tests
```

May chu web cuc bo: `http://127.0.0.1:8000`. `DATABASE_URL` phai duoc cap qua
bien moi truong; khong ghi mat khau vao ma nguon, tai lieu hay Git.

## Trang Thai Hien Tai

### Da hoan thanh

- Phong Dao tao tai len 7 CSV, xem truoc/kiem tra, xac nhan mot dataset batch
  va chay GA tu batch do. `official` chi la fixture/demo, khong la du lieu van
  hanh mac dinh.
- Sua CSV da xac nhan tao batch/phien ban moi; ban cu duoc giu nguyen.
- GA co selection, crossover, mutation, repair, seed tai lap, rang buoc cung va
  rang buoc mem. Thu Bay, Chu nhat va ca toi la hop le, chi bi han che mem khi
  khong co nguyen vong phu hop cua giang vien.
- Da sinh occurrence theo lich hoc ky; ngay nghi khong sinh buoi binh thuong.
- FastAPI, SQLAlchemy, Alembic va PostgreSQL co migration `20260807_0005` cho
  snapshot dataset, payload GA run, lich chinh thuc, phan doan lich va buoi bu.
  `DATABASE_URL` la bat buoc khi chay he thong; loi cau hinh/ghi DB duoc tra ro
  rang, khong con bo qua de roi ve JSON.
- Phuong an GA la bat bien sau khi luu. Phong Dao tao cong bo mot run hop le
  thanh **lich chinh thuc** rieng; chi lich chinh thuc moi duoc dieu chinh va
  xuat. JSON trong `data/runtime/runs/` chi con la snapshot sau khi ghi DB thanh
  cong.
- Giao dien co 5 luong chinh theo de tai: nhap CSV, cau hinh/chay GA, ket qua
  va chinh sua lich. Trang Ket qua chi de xem/loc/nhom/xuat; trang Chinh sua
  lich rieng cho phep tim kiem, loc, phan trang va sua mot buoi theo ngay.
- Dieu chinh lich chinh thuc theo `ONE_OCCURRENCE`, `DATE_RANGE` hoac
  `FROM_DATE_TO_END` da hoan thanh. Backend kiem tra khung gio, loai/suc chua
  phong, phong khong kha dung, han che co dinh cua giang vien va trung phong/
  giang vien tren tung occurrence hieu luc; ly do va audit duoc luu.
- Da co API tao phan doan lich theo khoang ngay va buoi hoc bu thu cong. Ca hai
  deu kiem tra rang buoc cung truoc khi luu va duoc dong bo vao PostgreSQL.
- Trang Chinh sua lich co tim kiem theo ma lop/ten mon/giang vien/phong, loc
  theo tuan/giang vien/phong, phan trang 25/50/100 buoi va lich su dieu chinh.
- Nut xuat CSV/XLSX tren trang Chinh sua lich xuat cac occurrence hien tai,
  bao gom cac thay doi mot buoi; khong chi xuat assignment lich co so.
- Da co lich su 10 lan chay gan nhat tai Tong quan:
  `GET /api/ga/runs` va `GET /api/ga/runs/{run_code}`.
- Ket qua kiem thu gan nhat: `47 passed`; da kiem tra cu phap `frontend/app.js`
  bang `node --check`.

### Chua hoan thanh

- Chua co dang nhap/phan quyen, lich ca nhan giang vien va yeu cau doi lich.
- Chua co kiem thu giao dien tu dong/end-to-end. Form giao dien chua co thao
  tac rieng de tao phan doan va buoi bu (API va kiem thu backend da co).

## Backlog Uu Tien

### Da hoan thanh trong tuan nay

1. Tach phuong an GA va lich chinh thuc; cong bo run, bao toan run goc.
2. Doc/ghi run va audit bang PostgreSQL; JSON chi la snapshot.
3. Dieu chinh theo pham vi occurrence/khoang ngay/tu ngay den het hoc phan.
4. Phan doan lich va buoi bu thu cong co kiem tra rang buoc.
5. Bo sung migration, kiem thu API va cap nhat tai lieu ban giao.

### P1 - Lich theo ngay va ngoai le

3. Bo sung form giao dien rieng cho phan doan lich va buoi bu; hien thi buoi
   thieu do ngay nghi va lien ket buoi bu voi buoi bi thieu.

### P2 - Nguoi dung va phe duyet

6. Dang nhap/phan quyen MVP: `ADMIN`, `TRAINING_OFFICE` va `LECTURER` theo
   URS/SRS. Theo quyet dinh hien tai, bat dau sau khi ket thuc 5 muc tren.
7. Yeu cau doi lich: giang vien gui, Phong Dao tao duyet/tu choi/ap dung sau
   kiem tra rang buoc cung; luu day du lich su.

### P3 - Chat luong

8. Xuat theo giang vien, phong, lop hoc phan va occurrence theo ngay; ten file
   co run code va thoi diem.
9. Mo rong test API/UI cho adjustment scope, segment, buoi bu, phan quyen,
   request workflow va PostgreSQL persistence.

## Doi Chieu De Tai Thuc Tap Goc

Da doc `C:\Users\ADMIN\Downloads\De tai thục tap.docx` ngay 31/07/2026.
Huong hien tai phu hop voi de tai: Phong Dao tao upload CSV, GA xep lich co
rang buoc, hien thi theo giang vien/phong/lop, chinh sua va xuat CSV/Excel.

### Da phu hop

- CSV duoc tai len, xem truoc, kiem tra va xac nhan truoc khi chay GA.
- GA co chromosome lich co so, fitness, selection, crossover, mutation, repair
  va cac tham so population size, generations, mutation rate, crossover rate.
- Da kiem tra trung giang vien, trung phong, loai phong, suc chua, khung gio va
  cac rang buoc mem: ca lien tiep, khoang trong, phan tan lich, toi/cuoi tuan.
- Da hien thi ket qua theo giang vien, phong va lop hoc phan; da xuat CSV/XLSX.

### Khoang thieu can xu ly de khop hoan toan

- Ngay nghi da duoc bo qua khi sinh occurrence, nhung chua co them buoi bu de
  dam bao du so buoi yeu cau.
- UI hien chi bao "Dang chay...", chua co tien trinh GA theo the he/phan tram.
- API GA khong duoc cho phep chay runtime tu `data_dir` tuy y; web phai chi chay
  tu batch 7 CSV da xac nhan. CLI co the giu du lieu mau cho muc dich phat trien.
- Loi PostgreSQL hien dang co the bi nuot im lang trong persistence; can log va
  thong bao loi ro rang de dam bao lich su da duoc luu that su.

### Luu Y Ve Pham Vi

Dang nhap, phan quyen va quy trinh yeu cau doi lich cua giang vien khong duoc
neu chi tiet trong de tai goc, nhung la yeu cau bat buoc trong URS/SRS hien tai.
Khong bo cac muc nay sau khi hoan thanh cac yeu cau cot loi cua de tai.

## Buoc Nen Lam Tiep

Bat dau P2: dang nhap/phan quyen voi ba vai tro theo URS/SRS, sau do ket noi
quy trinh yeu cau doi lich cua giang vien. Khong mo rong GA thanh mot gene cho
moi occurrence.

## Ghi Chu Luu Tru (Khong Con Phan Anh Trang Thai Hien Tai)

Project: Teaching Timetable Scheduling Application Using Genetic Algorithm.

Keep implementation inside the approved MVP scope:

- Training Office imports and validates CSV data.
- Genetic Algorithm schedules day, configured time slot and room.
- Lecturer assignment is fixed input data.
- One course section has one primary lecturer.
- One GA gene represents one base weekly assignment for one course section.
- PostgreSQL is the intended persistent database for larger data later.
- Do not add student accounts, student registration, automatic lecturer assignment or student-availability matching.

## Work Completed In This Session

### CSV sample data

- Replaced the old sample dataset with a long-term `data/samples/small` dataset.
- CSV files use UTF-8 and include Vietnamese text with diacritics.
- Current required sample files:
  - `lecturers.csv`
  - `rooms.csv`
  - `time_slots.csv`
  - `course_sections.csv`
  - `lecturer_time_preferences.csv`
  - `room_unavailable_slots.csv`
- Removed the old `expected_timetable.csv` because it belonged to the previous schema.

### CSV validation

- Added normalized domain models in `backend/app/domain/models.py`.
- Added CSV loader and validator in `backend/app/importing/csv_validator.py`.
- Validation checks include required files, required columns, UTF-8 CSV decoding, duplicate IDs, cross-file references, allowed enum values, scheduling student count priority, feasible slot existence and feasible room existence.

### Hard constraints

- Added shared hard-constraint checker in `backend/app/scheduling/hard_constraints.py`.
- Current checks include lecturer overlap, room overlap, missing or duplicate base assignment, invalid or inactive slot, slot/course-type mismatch, room-type mismatch, room-capacity violation, room unavailable slot, officially confirmed lecturer restriction and missing references.
- Partial period overlap is checked by period range, not by slot code only.

### Feasible assignment generation

- Added `backend/app/scheduling/feasible_assignments.py`.
- For each course section, it builds locally valid `(section_code, room_code, slot_code)` assignments before GA runs.

### GA v0.1

- Added `backend/app/algorithms/genetic/simple_ga.py`.
- Current version is a simple fixed-seed random-search baseline.
- It receives normalized domain data, uses feasible assignment domains, evaluates hard violations through the shared checker and uses room-capacity waste as an initial soft cost.
- It does not yet implement real selection, crossover or mutation.

### CLI demo

- Added `backend/app/cli/run_ga.py`.
- It runs: `CSV -> validation -> feasible domains -> GA v0.1 -> printed timetable result`.
- CLI output is configured for UTF-8 so Vietnamese text prints correctly in PowerShell.

### SQLAlchemy database models

- Added SQLAlchemy 2.0 models in `backend/app/db/models.py`.
- Added `backend/app/db/base.py`.
- Current core tables: `import_batches`, `lecturers`, `rooms`, `time_slots`, `course_sections`, `ga_runs`, `schedule_assignments`.
- These are database model definitions only. PostgreSQL, migrations and persistence services are not implemented yet.

### Tests

- Added tests under `backend/tests`.
- Latest result in this session: `Ran 30 tests OK`.

## Manual Test Commands

Run all backend tests:

```powershell
python -m unittest discover backend\tests
```

Run the GA demo pipeline:

```powershell
python -m backend.app.cli.run_ga --data-dir data/samples/small --population-size 80 --generations 200 --seed 42
```

Expected signs of success:

```text
status=COMPLETED
stop_reason=VALID_TIMETABLE_FOUND
hard_violation_count=0
assignments:
```

## Things To Remember Next Session

- `docs/requirements/*.md` must match the updated UR/SRS and repository `AGENTS.md`.
- Course types are `THEORY`, `PRACTICE`, `INTEGRATED`.
- Room types currently used are `THEORY_ROOM`, `COMPUTER_LAB`, `SPECIALIZED_LAB`.
- Time slots must be configured. Do not generate arbitrary period ranges.
- Valid THEORY slots: `1-3`, `4-6`, `7-9`, `10-12`, `13-15`.
- Valid PRACTICE/INTEGRATED slots: `1-5`, `1-6`, `2-6`.
- Saturday, Sunday and evening are valid teaching times. Configurable soft weights may avoid them by default, while explicit lecturer preferences waive the matching default cost.
- `scheduling_student_count` priority: `approved_max_students`, else `initial_registration_limit`, else `expected_students`.
- CSV import means importing a complete dataset batch, not only one CSV file.
- `reason` fields in preference/unavailable-slot files are notes only; validation must not infer business rules from reason text.
- Database currently exists only as SQLAlchemy model definitions, not as a running PostgreSQL database.

## Good Next Implementation Steps

1. Add persistence mappers/services from validated domain data to SQLAlchemy models.
2. Add PostgreSQL configuration and Alembic migrations.
3. Add API endpoints for CSV validation/import preview.
4. Improve GA from random-search baseline to real GA operators: selection, crossover, mutation and repair.
5. Add export output contract after the base schedule result shape stabilizes.
