
# vn-listed-financials-ml

End-to-end miễn phí: Lấy **BCTC HOSE/HNX** → Bronze (hợp nhất & scale về VND) → Silver (tính ratios) → Train baseline (RandomForest). Repo này **tách biệt** với dự án trước.

---

## 0) Cài môi trường (Windows PowerShell)
```powershell
cd <THU_MUC_BAN_GIAI_NEN>
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
> Nếu chưa xử lý PDF thì KHÔNG cần cài Java/Ghostscript; chỉ dùng Excel/CSV.

---

## 1) Chọn danh sách mã
Mở `scripts/vn_fs/company_list.csv` và thêm/bớt mã (ưu tiên doanh nghiệp quy mô vừa):
```
symbol,exchange,industry
VNM,HOSE,Food & Beverage
FPT,HOSE,IT Services
HAX,HOSE,Retail
ACB,HNX,Banking
VCS,HNX,Construction Materials
```

---

## 2) Tải BCTC về thư mục landing (ưu tiên Excel/HTML)
Quy ước đặt tên file (ví dụ quý 1 năm 2023 của VNM):
```
data/landing/HOSE/VNM/2023/Q1_kqkd.xlsx   # Kết quả kinh doanh
data/landing/HOSE/VNM/2023/Q1_cdkt.xlsx   # Cân đối kế toán
data/landing/HOSE/VNM/2023/Q1_lctt.xlsx   # Lưu chuyển tiền tệ (nếu có)
```
Lặp lại cho Q2, Q3, Q4 và các năm khác.

---

## 3) Bronze: Hợp nhất & scale về VND
```powershell
cd scripts/vn_fs
python bronze_extract.py
```
Sinh ra: `lake/bronze/vn_fs/bronze_financials_quarterly.csv`

---

## 4) Silver: Tính ratios & làm sạch
```powershell
python silver_transform.py
```
Sinh ra: `lake/silver/vn_fs/silver_financials_quarterly.csv|parquet`

---

## 5) Train baseline (RandomForest)
```powershell
python train_baseline.py
```
- Nếu bạn chưa có dữ liệu thật, script sẽ **fallback** dùng file mẫu `lake/silver/vn_fs/silver_financials_quarterly_sample.csv` để in `classification_report`.

---

## 6) Checklist chất lượng (phải tick trước khi train thật)
- Scale đơn vị **VND/Triệu/Tỷ** đã quy về **VND** đúng.
- Có tối thiểu các cột: `revenue, cogs, opex, net_profit, total_assets, equity, short_term_debt, long_term_debt` (cashflow/interest có thể trống).
- Khóa `(company_id, year, quarter)` là **duy nhất**.
- Ratios hợp lý (không outlier vô lý).

---

## 7) Mở rộng
- Thêm biến phi tài chính ở bước Silver (join theo `company_id`): `industry`, `years_in_business`...
- Cập nhật `KEY_MAP` trong `bronze_extract.py` nếu gặp nhãn chỉ tiêu mới.

---

Made for your student research project ❤
