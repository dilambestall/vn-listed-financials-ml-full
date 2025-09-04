import pandas as pd

# ==== Hàm tiện ích ====
def get_value(df, keywords):
    if isinstance(keywords, str):
        keywords = [keywords]

    for kw in keywords:
        row = df[df.iloc[:, 0].astype(str).str.contains(kw, case=False, na=False)]
        if not row.empty:
            val = row.iloc[0, -1]
            val = str(val).replace(",", "").replace(" ", "")
            try:
                return float(val)
            except:
                return None
    return None


def process_company(company_id, year, file_path):
    try:
        xls = pd.ExcelFile(file_path)

        cdkt = pd.read_excel(file_path, sheet_name="CÂN ĐỐI KẾ TOÁN")
        kqkd = pd.read_excel(file_path, sheet_name="KẾT QUẢ KINH DOANH")    
        lctt = pd.read_excel(file_path, sheet_name="LƯU CHUYỂN TIỀN TỆ")

        features = {
            "company_id": company_id,
            "year": year,

            # Balance Sheet
            "total_assets": get_value(cdkt, "Tổng cộng tài sản"),
            "equity": get_value(cdkt, "Vốn chủ sở hữu"),
            "total_liabilities": get_value(cdkt, "Nợ phải trả"),
            "current_assets": get_value(cdkt, "Tài sản ngắn hạn"),
            "current_liabilities": get_value(cdkt, "Nợ ngắn hạn"),
            "cash_and_equivalents": get_value(cdkt, "Tiền và các khoản tương đương tiền"),
            "short_term_debt": get_value(cdkt, "Vay và nợ thuê tài chính ngắn hạn"),
            "long_term_debt": get_value(cdkt, "Vay và nợ thuê tài chính dài hạn"),

            # Income Statement
            "revenue": get_value(kqkd, ["Doanh thu bán hàng", "Doanh thu thuần"]),
            "gross_profit": get_value(kqkd, "Lợi nhuận gộp"),
            "net_income": get_value(kqkd, ["Lợi nhuận sau thuế", "Lợi nhuận sau thuế thu nhập DN"]),
            "selling_expenses": get_value(kqkd, "Chi phí bán hàng"),
            "admin_expenses": get_value(kqkd, "Chi phí quản lý doanh nghiệp"),
            "interest_expenses": get_value(kqkd, "Chi phí tài chính"),

            # Cash Flow
            "cashflow_ops": get_value(lctt, [
                "Lưu chuyển tiền thuần từ hoạt động kinh doanh",
                "I. Lưu chuyển tiền từ hoạt động kinh doanh",
                "hoạt động kinh doanh"
            ]),
            "cashflow_investing": get_value(lctt, [
                "Lưu chuyển tiền thuần từ hoạt động đầu tư",
                "II. Lưu chuyển tiền từ hoạt động đầu tư",
                "hoạt động đầu tư"
            ]),
            "cashflow_financing": get_value(lctt, [
                "Lưu chuyển tiền thuần từ hoạt động tài chính",
                "III. Lưu chuyển tiền từ hoạt động tài chính",
                "hoạt động tài chính"
            ]),
        }

        return features

    except Exception as e:
        print(f"⚠️ Lỗi khi xử lý {company_id}-{year}: {e}")
        return None


# ==== Chạy cho nhiều công ty ====
company_list = pd.read_csv("scripts/vn_fs/company_list.csv")

all_data = []
for _, row in company_list.iterrows():
    features = process_company(row["company_id"], row["year"], row["file_path"])
    if features:
        all_data.append(features)

# Xuất ra file tổng hợp
df_out = pd.DataFrame(all_data)
output_path = "data/cleaned/all_companies.csv"
df_out.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ Done! Đã lưu dữ liệu tổng hợp tại {output_path}")
print(df_out.head())
