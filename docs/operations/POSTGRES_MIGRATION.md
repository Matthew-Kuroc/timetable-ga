# Huong dan nang cap PostgreSQL

Ung dung yeu cau `DATABASE_URL`; khong co fallback sang JSON khi ghi du lieu.
Hay dat bien moi truong trong phien chay va khong ghi thong tin dang nhap vao
repository.

## Kiem tra migration

Tu thu muc repository:

```powershell
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DB"
python -m alembic -c alembic.ini current
python -m alembic -c alembic.ini upgrade head
python -m alembic -c alembic.ini current
```

Revision hien tai la `20260813_0007`. Revision nay tao bang yeu cau dieu chinh
lich, bang audit su kien va lien ket audit ap dung voi yeu cau. Lenh `upgrade`
khong xoa du lieu cua cac revision truoc.

Lan kiem tra gan nhat da nang cap thanh cong database phat trien den
`20260813_0007 (head)`.

## Kiem tra sau migration

```powershell
$env:PYTHONPATH='.'
python -m pytest -q backend/tests
```

Neu PostgreSQL khong truy cap duoc, chi co the chay unit/API tests voi database
tuyen dung tam thoi; can ghi ro dieu nay trong bien ban trien khai.
