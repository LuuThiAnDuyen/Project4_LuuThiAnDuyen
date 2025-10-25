import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment


def generate_search_test_data():
    #  Xác định đường dẫn data/
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    file_path = os.path.join(data_dir, "search_test_data.xlsx")

    wb = Workbook()
    ws = wb.active
    ws.title = "SearchTestData"

    # Header
    headers = ["TestCaseID", "Keyword", "ExpectedCount", "ExpectedMessage"]
    ws.append(headers)

    # Style cho header
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    # Test data mẫu
    data = [
        ["TC01", "Lớp 10", 9, ""],
        ["TC02", "abcdefxyz", 0, "Không tìm thấy lớp gia sư"],
        ["TC03", "", 0, ""],  # Ô rỗng
        ["TC04", "   ", 0, ""],  # Toàn khoảng trắng
        ["TC05", "@@@!!!", 0, "Không tìm thấy lớp gia sư"],
        ["TC06", "lớp 10", 9, ""],  # Không phân biệt hoa/thường
        ["TC07", "   Lớp 10   ", 9, ""],  # Trim khoảng trắng
        ["TC08", "10", None, ""],  # Từ khóa một phần (số lượng không cố định)
    ]

    for row in data:
        ws.append(row)

    wb.save(file_path)
    print(f" File test data đã được sinh tại: {file_path}")


if __name__ == "__main__":
    generate_search_test_data()
