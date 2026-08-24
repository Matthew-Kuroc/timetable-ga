# Checklist demo Tuan 8

## Moi truong

- PostgreSQL dang chay va `DATABASE_URL` duoc dat qua `.env`/bien moi truong.
- Chay `python -m alembic upgrade head`; revision hien tai la `20260824_0010`.
- Khong dua `.env`, mat khau hoac du lieu that vao Git.

## Kich ban chinh

1. Training Office dang nhap va tai du bo bay CSV.
2. Xem preview, sua loi neu co, sau do xac nhan batch.
3. Chay GA voi seed, population size va generation limit; chi publish khi
   `hard_violation_count = 0`.
4. Xem lich theo giang vien/phong/lop, loc theo tuan/ngay va mo lich su run.
5. Tao segment phong theo khoang ngay (giu nguyen thu/tiet sau publish).
6. Tao buoi hoc bu trong tuan 16, 17 hoac 18; kiem tra lien ket
   `original_missing_date`; tuan 19 phai bi tu choi.
7. Dieu chinh mot occurrence, gui request voi tai khoan Lecturer, sau do
   Training Office phe duyet/tu choi/ap dung.
8. Tai CSV va XLSX; kiem tra ngay `DD-MM-YYYY`, UTF-8 BOM cho CSV va ten file
   co batch/run code.

## Lenh kiem thu

```powershell
$env:PYTHONPATH='.'
python -m alembic upgrade head
python -m pytest -q backend/tests
cd frontend
npm run build
npm run test:e2e
npm run test:e2e:real
```

## So lieu da xac minh (24/08/2026)

- PostgreSQL migration: thanh cong den `20260824_0010`.
- PostgreSQL integration: `1 passed`.
- Backend: `80 passed, 1 skipped` khi chay voi PostgreSQL.
- Official fixture 120 lop, 80 ca the, 200 the he, seed 42: khoang 38 giay,
  0 vi pham cung.
- Frontend build: thanh cong; Playwright E2E: `6 passed` (mock API).
- Playwright PostgreSQL that: `1 passed`; da xac minh truc tiep
  `app_users=3`, `import_batches=1`, `ga_runs=1`, `official_timetables=1`,
  `makeup_sessions=1`, `schedule_change_requests=1`.

Playwright mock van duoc giu de phan hoi nhanh. Lenh `test:e2e:real` dung
database rieng co hau to `_e2e`, chay migration va toan bo React -> FastAPI ->
PostgreSQL; database nay bi reset truoc moi luot test.

## Stress test quy mo truong (phien sau)

- [ ] Sinh batch an danh co seed voi khoang 600 giang vien, 3.000 lop hoc phan
  va 150 phong hoc theo cung schema bay CSV.
- [ ] Chay validator, import PostgreSQL, GA va occurrence expansion.
- [ ] Ghi runtime, bo nho, so gene, so occurrence, hard violations va
  best-so-far; khong tu y ha rang buoc cung neu bai test cham.
