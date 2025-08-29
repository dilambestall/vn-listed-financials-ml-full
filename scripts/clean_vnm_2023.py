import pandas as pd
from pathlib import Path

# === Đường dẫn ===
base_dir = Path("data/landing/HOSE/VNM/2023")
files = {
    "cdkt": "2023_cdkt.xlsx",
    "kqkd": "2023_kqkd.xlsx",
    "lctt": "2023_lctt.xlsx",
}

def load_clean(path):
    # Đọc toàn bộ, bỏ header phụ
    df = pd.read_excel(path, engine="openpyxl", header=None)
    df = df.iloc[5:, :]                       # bỏ 5 dòng đầu meta
    df = df.rename(columns={0: "chi_tieu"})   # cột đầu là "chi_tieu"
    df = df.dropna(how="all")                 # bỏ dòng toàn NaN
    df = df.dropna(axis=1, how="all")         # bỏ cột toàn NaN
    return df

# === Clean từng file và lưu lại ===
out_dir = base_dir / "cleaned"
out_dir.mkdir(exist_ok=True)

for key, fname in files.items():
    fpath = base_dir / fname
    df = load_clean(fpath)

    # Xuất ra CSV & Parquet
    out_csv = out_dir / f"{key}_2023_clean.csv"
    out_parquet = out_dir / f"{key}_2023_clean.parquet"

    df.to_csv(out_csv, index=False)
    df.to_parquet(out_parquet, index=False)

    print(f"✅ Cleaned {fname} → {out_csv}")
