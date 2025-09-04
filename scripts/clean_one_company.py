import pandas as pd

# ==== Cấu hình ====
file_path = "data/landing/HOSE/VNM/2023/VNM_2023.xlsx"
company_id = "VNM"
year = 2023
output_path = "data/cleaned/VNM_2023_clean.csv"

# ==== Hàm tiện ích ====
def get_value(df, keywords):
    """
    Tìm giá trị theo nhiều keyword (list hoặc str).
    Trả về số float, nếu không tìm thấy thì None.
    """
    if isinstance(keywords, str):
        keywords = [keywords]

    for kw in keywords:
        row = df[df.iloc[:, 0].astype(str).str.contains(kw, case=False, na=False)]
        if not row.empty:
            val = row.iloc[0, -1]  # lấy cột cuối
            val = str(val).replace(",", "").replace(" ", "")
            try:
                return float(val)
            except:
                return None
    return None


# ==== Đọc dữ liệu từ Excel ====
xls = pd.ExcelFile(file_path)
print("📑 Các sheet có trong file:", xls.sheet_names)

cdkt = pd.read_excel(file_path, sheet_name="CÂN ĐỐI KẾ TOÁN")
kqkd = pd.read_excel(file_path, sheet_name="KẾT QUẢ KINH DOANH")
lctt = pd.read_excel(file_path, sheet_name="LƯU CHUYỂN TIỀN TỆ")

# ==== Trích xuất chỉ tiêu ====
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

    # Cash Flow – thêm fallback để không bị NaN
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

# ==== Xuất ra file CSV ====
df_out = pd.DataFrame([features])
df_out.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"✅ Done! File cleaned đã lưu tại: {output_path}")
print(df_out)
