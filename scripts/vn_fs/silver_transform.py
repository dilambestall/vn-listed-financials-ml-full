
import os
import pandas as pd
from pathlib import Path

def compute_ratios(df: pd.DataFrame) -> pd.DataFrame:
    eps = 1e-9
    if "expenses" not in df.columns:
        df["expenses"] = df[["cogs","opex"]].sum(axis=1, min_count=1)
    if "operating_profit" not in df.columns:
        df["operating_profit"] = (df["revenue"] - df["expenses"]).where(df["revenue"].notna() & df["expenses"].notna())

    if "debt_total" not in df.columns:
        df["debt_total"] = df[["short_term_debt","long_term_debt"]].sum(axis=1, min_count=1)
    if "current_assets" not in df.columns:
        df["current_assets"] = pd.NA
    if "current_liabilities" not in df.columns:
        df["current_liabilities"] = df["short_term_debt"]

    df["roe"] = df["net_profit"] / (df["equity"] + eps)
    df["roa"] = df["net_profit"] / (df["total_assets"] + eps)
    df["debt_to_equity"] = df["debt_total"] / (df["equity"] + eps)
    df["current_ratio"] = df["current_assets"] / (df["current_liabilities"] + eps)
    df["interest_coverage"] = df["operating_profit"] / (df["interest_expense"] + eps)
    df["net_margin"] = df["net_profit"] / (df["revenue"] + eps)

    for c in ["roe","roa","debt_to_equity","current_ratio","interest_coverage","net_margin"]:
        df[c] = df[c].astype(float).round(4)
    return df

def silver_transform(bronze_csv: str, out_parquet: str, out_csv: str):
    if not os.path.exists(bronze_csv):
        raise FileNotFoundError(f"Bronze CSV not found: {bronze_csv}")
    df = pd.read_csv(bronze_csv)

    df["company_id"] = df["company_id"].astype("string")
    df["year"] = df["year"].astype(int)
    df["quarter"] = df["quarter"].astype("string")

    num_cols = [c for c in df.columns if c not in ["company_id","year","quarter"]]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = compute_ratios(df)
    df = df.sort_values(["company_id","year","quarter"])

    Path(os.path.dirname(out_parquet)).mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)
    df.to_csv(out_csv, index=False)
    print(f"[OK] Silver saved: {out_csv}  rows={len(df)}")

if __name__ == "__main__":
    silver_transform(
        bronze_csv="../../lake/bronze/vn_fs/bronze_financials_quarterly.csv",
        out_parquet="../../lake/silver/vn_fs/silver_financials_quarterly.parquet",
        out_csv="../../lake/silver/vn_fs/silver_financials_quarterly.csv"
    )
