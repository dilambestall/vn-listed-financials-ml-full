import pandas as pd
from pathlib import Path

# === Đường dẫn tới folder chứa file gốc ===
base_dir = Path("data/landing/HOSE/VNM/2023")

files = {
    "cdkt": "2023_cdkt.xlsx.xlsx",
    "kqkd": "2023_kqkd.xlsx.xlsx",
    "lctt": "2023_lctt.xlsx.xlsx",
}


# === Hàm load và clean file gốc ===
def load_clean(path):
    df = pd.read_excel(path, engine="openpyxl", header=None)
    df = df.iloc[5:, :]                       # bỏ 5 dòng đầu meta
    df = df.rename(columns={0: "chi_tieu"})   # cột đầu là chi_tieu
    df = df.dropna(how="all")                 # bỏ dòng NaN
    df = df.dropna(axis=1, how="all")         # bỏ cột NaN
    return df

# === Clean từng file và lưu lại vào cleaned/ ===
clean_dir = base_dir / "cleaned"
clean_dir.mkdir(exist_ok=True)

cleaned = {}
for key, fname in files.items():
    fpath = base_dir / fname
    df = load_clean(fpath)
    df.to_csv(clean_dir / f"{key}_2023_clean.csv", index=False)
    cleaned[key] = df
    print(f"✅ Cleaned {fname} -> {key}_2023_clean.csv")

cdkt, kqkd, lctt = cleaned["cdkt"], cleaned["kqkd"], cleaned["lctt"]

# === Hàm lấy giá trị theo tên chỉ tiêu (lấy cột cuối cùng) ===
def get_value(df, keyword):
    row = df[df["chi_tieu"].astype(str).str.contains(keyword, case=False, na=False)]
    if row.shape[0] == 0:
        return None
    val = row.iloc[0, -1]
    try:
        val = float(str(val).replace(",", "").replace(" ", ""))
    except:
        val = None
    return val

# === Trích xuất chỉ tiêu quan trọng ===
features = {
    "company_id": "VNM",
    "year": 2023,

    # Balance sheet
    "total_assets": get_value(cdkt, "TỔNG CỘNG TÀI SẢN"),
    "equity": get_value(cdkt, "Vốn chủ sở hữu"),
    "total_liabilities": get_value(cdkt, "Nợ phải trả"),
    "current_assets": get_value(cdkt, "Tài sản ngắn hạn"),
    "current_liabilities": get_value(cdkt, "Nợ ngắn hạn"),
    "cash_and_equivalents": get_value(cdkt, "Tiền và các khoản tương đương tiền"),
    "short_term_debt": get_value(cdkt, "Vay và nợ thuê tài chính ngắn hạn"),
    "long_term_debt": get_value(cdkt, "Vay và nợ thuê tài chính dài hạn"),

    # Income statement
    "revenue": get_value(kqkd, "Doanh thu thuần"),
    "gross_profit": get_value(kqkd, "Lợi nhuận gộp"),
    "net_income": get_value(kqkd, "Lợi nhuận sau thuế"),
    "selling_expenses": get_value(kqkd, "Chi phí bán hàng"),
    "admin_expenses": get_value(kqkd, "Chi phí quản lý"),
    "interest_expenses": get_value(kqkd, "Chi phí lãi vay"),

    # Cash flow
    "cashflow_ops": get_value(lctt, "Lưu chuyển tiền thuần từ hoạt động kinh doanh"),
    "cashflow_investing": get_value(lctt, "Lưu chuyển tiền thuần từ hoạt động đầu tư"),
    "cashflow_financing": get_value(lctt, "Lưu chuyển tiền thuần từ hoạt động tài chính"),
}

# === Tính thêm ratios ===
try:
    features["ROA"] = features["net_income"] / features["total_assets"]
except: features["ROA"] = None

try:
    features["ROE"] = features["net_income"] / features["equity"]
except: features["ROE"] = None

try:
    features["Debt_to_Equity"] = features["total_liabilities"] / features["equity"]
except: features["Debt_to_Equity"] = None

try:
    features["Current_Ratio"] = features["current_assets"] / features["current_liabilities"]
except: features["Current_Ratio"] = None

try:
    features["Net_Profit_Margin"] = features["net_income"] / features["revenue"]
except: features["Net_Profit_Margin"] = None

try:
    EBIT = (features["gross_profit"] or 0) - (features["selling_expenses"] or 0) - (features["admin_expenses"] or 0)
    features["Interest_Coverage"] = EBIT / features["interest_expenses"] if features["interest_expenses"] else None
except: features["Interest_Coverage"] = None

# === Xuất summary cuối ===
df_out = pd.DataFrame([features])
out_path = clean_dir / "vnm_2023_full_summary.csv"
df_out.to_csv(out_path, index=False)

print("✅ Xuất file tổng hợp:", out_path)
print(df_out.T)
