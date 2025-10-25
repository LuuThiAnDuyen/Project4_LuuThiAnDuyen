import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


def generate_login_test_data():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, "login_test_data.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "LoginTestData"

    headers = [
        "TestCaseID",
        "Email",
        "Password",
        "ExpectedMessage",
        "ActualResult",
        "Screenshot",
        "VideoPath",
    ]
    ws.append(headers)

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    data = [
        [
            "TC01",
            "luuthianduyen@gmail.com",
            "luuthianduyen247",
            "Tài khoản của tôi",
            "",
            "",
            "",
        ],
        ["TC02", "", "123456789", "Email là bắt buộc", "", "", ""],
        ["TC03", "valid_user@gmail.com", "", "Mật khẩu là bắt buộc", "", "", ""],
        [
            "TC04",
            "invalid_user@gmail.com",
            "wrongpass",
            "Sai tên đăng nhập hoặc mật khẩu",
            "",
            "",
            "",
        ],
    ]

    for row in data:
        ws.append(row)

    wb.save(file_path)
    print(f" File test data đã sinh tại: {file_path}")


if __name__ == "__main__":
    generate_login_test_data()
