# utils/data_generator.py

import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


def generate_login_test_data():
    # ✅ Tính đường dẫn tuyệt đối tới thư mục `data/`
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, "login_test_data.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "LoginTestData"

    # Header
    headers = ["Test Case", "Username/Email", "Password", "Expected Result", "Note"]
    ws.append(headers)

    # Test data
    data = [
        ["TC01", "valid@example.com", "pass123", "Pass", "Đăng nhập thành công"],
        ["TC02", "invalid@example.com", "wrongpass", "Fail", "Tài khoản không tồn tại"],
        ["TC03", "", "somepass", "Validation error", "Thiếu email"],
        ["TC04", "valid@example.com", "", "Validation error", "Thiếu mật khẩu"],
    ]

    for row in data:
        ws.append(row)

    wb.save(file_path)
    print(f"✅ File test data đã được lưu tại: {file_path}")


if __name__ == "__main__":
    generate_login_test_data()
