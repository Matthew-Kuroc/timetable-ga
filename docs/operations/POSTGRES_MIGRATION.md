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

Revision hien tai la `20260824_0010`. Revision `0007` tao bang yeu cau dieu
chinh lich; `0008` va `0009` bao ve tai khoan bootstrap/system Administrator;
`0010` them du lieu meeting thu hai va meeting_number on dinh.
Lenh `upgrade` khong xoa du lieu cua cac revision truoc.

Lan kiem tra gan nhat da nang cap thanh cong database phat trien den
`20260824_0010 (head)` ngay 24/08/2026.

## Kiem tra sau migration

```powershell
$env:PYTHONPATH='.'
python -m pytest -q backend/tests
```

Neu PostgreSQL khong truy cap duoc, chi co the chay unit/API tests voi database
tuyen dung tam thoi; can ghi ro dieu nay trong bien ban trien khai.
