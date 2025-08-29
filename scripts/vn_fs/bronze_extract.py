
import re
import os
import unicodedata
import pandas as pd
from pathlib import Path

# ==== Helpers ====

def normalize(text: str) -> str:
    if text is None: return ""
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', text).strip()

def detect_scale_from_sheet(df: pd.DataFrame) -> int:
    head_txt = " ".join([ " ".join(map(str, row)) for _, row in df.head(12).iterrows() ])
    head_norm = normalize(head_txt)
    if "trieu" in head_norm: return 1_000_000
    if "ty" in head_norm or "ti" in head_norm: return 1_000_000_000
    return 1

KEY_MAP = {
    "revenue": ["doanh thu thuần", "doanh thu ban hang", "doanh thu"],
    "cogs": ["gia von hang ban", "gia von"],
    "opex": ["chi phi ban hang", "chi phi quan ly", "chi phi hoat dong"],
    "net_profit": ["loi nhuan sau thue", "loi nhuan thuan", "lnst", "loi nhuan sau thue cua cty me"],
    "total_assets": ["tong tai san"],
    "equity": ["von chu so huu", "von csh"],
    "short_term_debt": ["no ngan han"],
    "long_term_debt": ["no dai han"],
    "cashflow_ops": ["luu chuyen tien tu hoat dong kinh doanh", "lctt tu hdkd"],
    "interest_expense": ["chi phi lai vay"],
}

def map_row_to_standard(label: str):
    lab = normalize(label)
    for std_col, keys in KEY_MAP.items():
        for k in keys:
            if k in lab:
                return std_col
    return None

def safe_to_number(x, scale=1):
    if pd.isna(x): return None
    s = str(x).strip()
    # accounting negative (1,234) -> -1234
    neg = s.startswith("(") and s.endswith(")")
    s = s.replace(",", "").replace(".", "")
    s = s.replace("(", "").replace(")", "")
    try:
        val = float(s)
    except:
        try:
            val = float(re.sub(r"[^\d\-\+eE]", "", s))
        except:
            return None
    if neg: val = -abs(val)
    return val * scale

def read_statement_excel(path: Path, year: int, quarter: str, symbol: str, stmt_type: str):
    try:
        df = pd.read_excel(path, header=None)
    except Exception as e:
        print(f"[WARN] Cannot read {path}: {e}")
        return {}

    scale = detect_scale_from_sheet(df)

    tmp = df.copy()
    tmp_cols = tmp.columns.tolist()
    value_col = None
    best_numeric = -1
    for c in tmp_cols[1:6]:
        numeric_count = pd.to_numeric(tmp[c], errors='coerce').notna().sum()
        if numeric_count > best_numeric:
            best_numeric = numeric_count
            value_col = c
    if value_col is None:
        value_col = 1

    result = {}
    for _, row in df.iterrows():
        label = str(row[0])
        std_col = map_row_to_standard(label)
        if std_col:
            val = safe_to_number(row[value_col], scale=scale)
            if val is not None:
                result[std_col] = val

    result.update({
        "company_id": symbol,
        "year": year,
        "quarter": quarter
    })
    return result

def collect_from_company_quarter(root: Path, exchange: str, symbol: str, year: int, quarter: str):
    base = root / exchange / symbol / str(year)
    files = {
        "kqkd": list(base.glob(f"{quarter}_kqkd.*")),
        "cdkt": list(base.glob(f"{quarter}_cdkt.*")),
        "lctt": list(base.glob(f"{quarter}_lctt.*")),
    }
    rec = {"company_id": symbol, "year": year, "quarter": quarter}

    for stmt_type, candidates in files.items():
        if not candidates:
            continue
        f = candidates[0]
        if f.suffix.lower() in [".xlsx", ".xls"]:
            data = read_statement_excel(f, year, quarter, symbol, stmt_type)
            rec.update(data)
        else:
            # TODO: PDF handling later
            pass
    return rec

def build_bronze_table(landing_dir: str, company_list_csv: str, out_csv: str):
    landing = Path(landing_dir)
    comp = pd.read_csv(company_list_csv)
    rows = []
    years = [2022, 2023, 2024]
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    for _, r in comp.iterrows():
        symbol = r["symbol"]
        exchange = r["exchange"]
        for y in years:
            for q in quarters:
                rec = collect_from_company_quarter(landing, exchange, symbol, y, q)
                if any(k in rec for k in ["revenue","cogs","opex","net_profit","total_assets","equity",
                                          "short_term_debt","long_term_debt","cashflow_ops","interest_expense"]):
                    rows.append(rec)

    bronze = pd.DataFrame(rows).drop_duplicates(subset=["company_id","year","quarter"])
    bronze = bronze.sort_values(["company_id","year","quarter"])
    Path(os.path.dirname(out_csv)).mkdir(parents=True, exist_ok=True)
    bronze.to_csv(out_csv, index=False)
    print(f"[OK] Bronze saved: {out_csv}  rows={len(bronze)}")

if __name__ == "__main__":
    build_bronze_table(
        landing_dir="../../data/landing",
        company_list_csv="company_list.csv",
        out_csv="../../lake/bronze/vn_fs/bronze_financials_quarterly.csv"
    )
