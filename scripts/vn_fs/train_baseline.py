
import os
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

SILVER_PATH = "../../lake/silver/vn_fs/silver_financials_quarterly.csv"
SAMPLE_PATH = "../../lake/silver/vn_fs/silver_financials_quarterly_sample.csv"

if os.path.exists(SILVER_PATH):
    df = pd.read_csv(SILVER_PATH)
else:
    print(f"[WARN] Silver not found. Using sample: {SAMPLE_PATH}")
    if not os.path.exists(SAMPLE_PATH):
        raise FileNotFoundError("No data available. Please run silver_transform.py or ensure the sample exists.")
    df = pd.read_csv(SAMPLE_PATH)

if "credit_risk" not in df.columns:
    conds = (df.get("debt_to_equity",0) > 2.5).astype(int)
    conds += (df.get("net_margin",0) < -0.05).astype(int)
    conds += (df.get("interest_coverage",0) < 1.5).astype(int)
    conds += ((df.get("cashflow_ops",0) < 0) & (df.get("current_ratio",0).fillna(0) < 1.0)).astype(int)
    df["credit_risk"] = (conds >= 2).astype(int)

features = [
    "revenue","cogs","opex","net_profit","total_assets","equity",
    "short_term_debt","long_term_debt","cashflow_ops",
    "roe","roa","debt_to_equity","current_ratio","interest_coverage","net_margin"
]
for f in features:
    if f not in df.columns:
        df[f] = 0.0

X = df[features].fillna(0.0)
y = df["credit_risk"]
groups = df["company_id"].astype(str)

gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=groups))
X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

clf = RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced")
clf.fit(X_train, y_train)
pred = clf.predict(X_test)

print(classification_report(y_test, pred, digits=3))
