# Bao cao du lieu tong hop quy mo truong

Cap nhat: 26/08/2026.

## Bo sinh lieu

- Seed: `42`.
- Giang vien: `600`.
- Lop hoc phan: `3.000`.
- Phong hoc: `150`.
- Khung gio: `126`.
- Ngay lich hoc vu: `126`.
- Lop khai bao hai meeting: `600`.
- Validator CSV: hop le, khong co loi tham chieu hoac mien kha thi.

Sinh lai bang:

```powershell
$env:PYTHONPATH='.'
python -m backend.app.cli.generate_synthetic_scale_data --output-dir .tmp/synthetic-scale --seed 42 --lecturers 600 --sections 3000 --rooms 150
```

## Harness benchmark

```powershell
python -m backend.app.cli.benchmark_synthetic_scale .tmp/synthetic-scale --population-size 80 --generations 200 --seed 42 --time-limit-seconds 600
```

Voi gioi han `0.1` giay, GA dung trong giai doan xay mien kha thi va tra ve
`STOPPED/TIME_LIMIT` trong khoang `0.101` giay. Dieu nay cho thay gioi han thoi
gian da bao phu ca giai doan tien xu ly, khong chi vong lap the he.

Chua cong bo ket qua GA day du cho batch 3.000 lop: mien assignment hien tai
co chi phi lon va can mot dot toi uu rieng truoc khi chay thuc nghiem dai.
Khong duoc xem batch tong hop nay la du lieu that cua truong.
