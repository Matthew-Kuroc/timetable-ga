# Ban Giao Va Backlog Hien Tai

Cap nhat: 10/08/2026. Day la tai lieu ban giao ky thuat cho phien Codex sau.
URS/SRS trong `docs/requirements/` van la nguon yeu cau nghiep vu chinh thuc.

## Checkpoint Tuan 7 - 21/08/2026

Tuan 7 da hoan tat nhom cong viec van hanh va trinh dien: bao ve tai khoan
bootstrap, cap tai khoan giang vien theo `lecturer_code` on dinh, hien thi ten
batch do Training Office dat, dat ten file export theo batch, gioi han mot
`ADMIN` va mot `TRAINING_OFFICE`, bo sung lich giang vien theo tuan voi bo
chon ngay/thang/nam va cot ca hoc, cung cac kiem thu workflow/API/UI.

Ket qua xac minh cuoi tuan: backend `74 passed, 2 skipped`; frontend build
thanh cong; Playwright E2E `6 passed`; benchmark fixture 120 lop khong co vi
pham rang buoc cung. Migration PostgreSQL moi nhat la
`20260821_0009_protect_existing_bootstrap_admin.py`.

Bao cao Word tuan 7 va script tao bao cao chi giu local trong
`docs/reports/`, khong dua vao GitHub.

## Checkpoint Phien 21/08/2026

Tuan 7 da dong bo cac khoang trong van hanh: tai khoan giang vien lay ma tu
batch da xac nhan, web chi cho phep chay GA tu batch, export co bo loc va
timestamp, co API workflow test day du, PostgreSQL smoke test trong CI va
benchmark fixture 120 lop. Bao cao Word va script tao bao cao van chi giu o
may local, khong thuoc pham vi theo doi cua Git.

## Checkpoint Phien 13/08/2026

Trang thai: **P2.7 da hoan tat**, migration da nang cap thanh cong tren
PostgreSQL muc tieu; da bo sung va chay smoke UI/E2E.

- Da kiem ke worktree va giu nguyen toan bo thay doi dang do ve dang nhap,
  phan quyen, cong Quan tri vien va cong Giang vien. Khong reset/ghi de thay
  doi co san.
- Da xac minh lai sau khi phien bi dung: backend `67 passed`; frontend
  `npm run build` thanh cong voi 28 modules.
- P2 muc 7 da co API, service, migration, giao dien va test cho viec giang
  vien gui/theo doi/huy; Phong Dao tao kiem tra, phe duyet, tu choi/ap dung;
  moi buoc co lich su va kiem tra lai rang buoc cung.
- Chua tu dat han khoa cho yeu cau doi toan bo lich lap. URS/SRS van ghi han
  nay la quyet dinh can xac nhan, nen phan do se phai tra loi ro rang cho den
  khi co cau hinh nghiep vu chinh thuc.
- Migration `20260813_0007` da chay thanh cong tren PostgreSQL that; Alembic
  dang o revision `20260813_0007 (head)` va ba bang yeu cau/audit da ton tai.

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
- Da hoan thanh dang nhap/phan quyen MVP voi dung mot role tren moi tai khoan:
  `ADMIN`, `TRAINING_OFFICE` hoac `LECTURER`. Backend bao ve API theo role;
  frontend co cong rieng cho tung role va xu ly phien dang nhap het han.
- Da co migration `20260810_0006`, CLI bootstrap `ADMIN` dau tien khong dung
  mat khau mac dinh, phien opaque-token luu bang cookie HttpOnly va audit tai
  khoan/xac thuc.
- Xac minh cuoi phien: backend `67 passed`; frontend `npm run build` thanh cong
  voi 28 modules; Playwright smoke E2E `2 passed`.

### Chua hoan thanh

- Chot voi nguoi huong dan cac van de dang mo trong UR/SRS: han doi toan bo
  lich lap, quy tac hoc bu sau tam ngung, trong so mem va cau truc CSV thuc te.
- Chuan bi kich ban demo voi PostgreSQL muc tieu va du lieu 100–200 lop sau khi
  moi truong trien khai duoc cap credential hop le.

## Backlog Uu Tien

### Da hoan thanh trong tuan nay

1. Tach phuong an GA va lich chinh thuc; cong bo run, bao toan run goc.
2. Doc/ghi run va audit bang PostgreSQL; JSON chi la snapshot.
3. Dieu chinh theo pham vi occurrence/khoang ngay/tu ngay den het hoc phan.
4. Phan doan lich va buoi bu thu cong co kiem tra rang buoc.
5. Bo sung migration, kiem thu API va cap nhat tai lieu ban giao.
6. Dang nhap/phan quyen MVP voi ba role, quan ly tai khoan `ADMIN`, lich ca
   nhan giang vien va route/navigation theo role.

### P1 - Lich theo ngay va ngoai le

- [x] 3. Da bo sung form giao dien rieng cho phan doan lich va buoi bu; hien
  thi buoi thieu do ngay nghi va lien ket buoi bu voi buoi bi thieu.

### P2 - Nguoi dung va phe duyet

- [x] 6. Dang nhap/phan quyen MVP: `ADMIN`, `TRAINING_OFFICE` va `LECTURER`
  theo URS/SRS; moi tai khoan co dung mot role va backend la lop phan quyen
  quyet dinh.
- [x] 7. Yeu cau doi lich: giang vien gui, Phong Dao tao duyet/tu choi/ap dung
  sau kiem tra rang buoc cung; luu day du lich su. Da hoan tat trong worktree.

### P3 - Chat luong

8. [x] Xuat theo giang vien, phong, lop hoc phan va occurrence theo ngay; ten
   file co run code va thoi diem.
9. [x] Mo rong test API/UI cho adjustment scope, segment, buoi bu, phan quyen,
   request workflow va PostgreSQL persistence; bo sung E2E/API workflow.

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

Mo rong E2E cho cac form phan doan, buoi bu va hien thi buoi thieu; sau do mo
rong kiem thu export theo P3. Khong mo rong GA thanh mot gene cho moi occurrence.

## Ke Hoach Tuan 8

### Muc tieu

On dinh hoa ban demo cuoi, chuan hoa du lieu va hoan tat cac luong kiem thu
cho buoi bao ve/thuc tap ma khong mo rong pham vi sang tai khoan sinh vien,
tu dong gan giang vien hoac tim lich theo kha nang ranh cua sinh vien.

### Cong viec uu tien

1. Chay rehearsal end-to-end tren PostgreSQL voi batch 100-200 lop; ghi lai
   thoi gian chay, so vi pham cung, so occurrence va ket qua cong bo.
2. Mo rong E2E cho tao phan doan, them buoi hoc bu, dieu chinh mot occurrence
   va quy trinh gui/duyet/ap dung yeu cau giang vien.
3. Hoan thien bo loc va kiem tra ten batch trong trang ket qua, trang chinh
   sua va ten file CSV/XLSX; them test khong de mat ten khi publish.
4. Ra soat accessibility/UI responsive tren man hinh nho, dac biet lich 7
   ngay va form cap tai khoan.
5. Chot cac cau hoi URS/SRS con mo voi nguoi huong dan: han khoa lich, quy tac
   hoc bu sau tam ngung, trong so rang buoc mem va schema CSV thuc te.
6. Tao checklist demo va huong dan khoi dong local/triển khai PostgreSQL,
   khong ghi credential vao repository.

### Tieu chi ket thuc Tuan 8

- Mot kich ban demo tu upload 7 CSV den dang nhap giang vien va export chay
  lai duoc tren PostgreSQL.
- Backend, build frontend va E2E deu xanh; moi loi con lai duoc ghi ro trong
  backlog.
- URS/SRS duoc cap nhat theo cac quyet dinh da duoc nguoi huong dan xac nhan.

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
