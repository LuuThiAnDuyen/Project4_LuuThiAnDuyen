import os
from openpyxl import load_workbook



def read_excel_data(filename: str, sheetname: str):
    """
    Đọc dữ liệu từ file Excel bất kỳ trong thư mục data/
    Trả về list các dòng (tuple).
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "data", filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f" Không tìm thấy file: {file_path}")

    wb = load_workbook(file_path)
    ws = wb[sheetname]

    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:  # bỏ header
            continue
        rows.append(row)
    wb.close()
    return rows


def read_test_data(data_file: str, sheet_name: str):
    wb = load_workbook(data_file)
    ws = wb[sheet_name]
    rows = []
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:  # bỏ header
            continue
        rows.append(list(row))
    wb.close()
    return rows


def read_login_data():
    """
    Đọc login_test_data.xlsx → trả về list dict
    """
    rows = read_excel_data("login_test_data.xlsx", "LoginTestData")
    return [
        {
            "tc": row[0],
            "username": row[1],
            "password": row[2],
            "expected": row[3],
            "note": row[4],
        }
        for row in rows
    ]

def read_search_test_data():
    """
    Đọc search_test_data.xlsx → trả về list tuple (tc, keyword, expected_count, expected_message)
    """
    rows = read_excel_data("search_test_data.xlsx", "SearchTestData")
    return [(row[0], row[1] if row[1] else "", row[2], row[3]) for row in rows]


def read_register_tutor_data():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "data", "register_tutor_test_data.xlsx")
    wb = load_workbook(file_path)
    ws = wb["RegisterTutorTestData"]

    data = []
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if i == 1:
            continue
        tcid, name, phone, message, expected_result, expected_message = row
        data.append(
            (
                tcid,
                name or "",
                phone or "",
                message or "",
                expected_result,
                expected_message,
            )
        )
    wb.close()
    return data
