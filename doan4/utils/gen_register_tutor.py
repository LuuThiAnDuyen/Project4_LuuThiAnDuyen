import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


def generate_register_tutor_test_data():
    # ✅ Tính đường dẫn tuyệt đối tới thư mục `data/`
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, "register_tutor_test_data.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "RegisterTutorTestData"

    # Header
    headers = [
        "TestCaseID",
        "Gender",
        "Name",
        "Phone",
        "Address",
        "Note",
        "ExpectedMessage",
        "ActualResult",
        "Screenshot",
        "VideoPath",
    ]
    ws.append(headers)

    # Style cho header
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Test data mẫu
    data = [
        [
            "TC01",
            "Anh",
            "Nguyen Van A",
            "0987654321",
            "Hà Nội",
            "Ghi chú 1",
            "Đăng ký thành công",
            None,
            None,
            None,
        ],
        [
            "TC02",
            "Chị",
            "Tran Thi B",
            "0123456789",
            "Hồ Chí Minh",
            "",
            "Đăng ký thành công",
            None,
            None,
            None,
        ],
        [
            "TC03",
            "Anh",
            "",
            "0987654321",
            "Hà Nội",
            "",
            "Họ và tên là bắt buộc",
            None,
            None,
            None,
        ],
        [
            "TC04",
            "Chị",
            "Le Thi C",
            "",
            "Đà Nẵng",
            "",
            "Số điện thoại ít nhất 10 chữ số",
            None,
            None,
            None,
        ],
        [
            "TC05",
            "Anh",
            "Nguyen Van D",
            "abcd1234",
            "Huế",
            "",
            "Số điện thoại ít nhất 10 chữ số",
            None,
            None,
            None,
        ],
    ]

    for row in data:
        ws.append(row)

    wb.save(file_path)
    print(f" File test data Register Tutor đã được sinh tại: {file_path}")

if __name__ == "__main__":
    generate_register_tutor_test_data()
