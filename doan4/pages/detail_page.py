# pages/detail_page.py
import re
from playwright.sync_api import Page, expect


class DetailPage:
    def __init__(self, page: Page):
        self.page = page
        self.btn_register = self.page.locator(
            ".btn.btn-cta.py-2.px-5.font-weight-bold"
        ).first
        self.btn_register_text = self.page.get_by_role(
            "button", name=re.compile(r"Đăng (kí|ký) nhận lớp|Nhận lớp", re.I)
        ).first
        self.btn_continue = self.page.locator(
            "xpath=//a[contains(text(),'Tiếp tục')]"
        ).first

        #  Tiêu đề/đoạn text chứa "Nhận lớp" (không phân biệt hoa/thường)
        self.note_nhan_lop_heading = self.page.locator("h1,h2,h3").filter(
            has_text=re.compile(r"Nhận\s*lớp", re.I)
        )
        # Fallback: bất kỳ text node nào chứa "Nhận lớp"
        self.any_nhan_lop_text = self.page.get_by_text(re.compile(r"Nhận\s*lớp", re.I))

    def click_register(self):
        target = (
            self.btn_register if self.btn_register.count() else self.btn_register_text
        )
        expect(target, "Không tìm thấy nút 'Đăng ký nhận lớp'").to_be_visible(
            timeout=5000
        )
        target.scroll_into_view_if_needed()
        target.click()

    def click_continue(self):
        expect(self.btn_continue, "Không tìm thấy nút 'Tiếp tục'").to_be_visible(
            timeout=5000
        )
        self.btn_continue.scroll_into_view_if_needed()
        self.btn_continue.click()

    def verify_nhan_lop_text(self, class_code: str | None = None):
        """Xác minh heading 'Note Nhận lớp <MÃ LỚP>' hiển thị sau khi nhấn Tiếp tục."""
        # 1) URL đúng trang note
        expect(self.page).to_have_url(re.compile(r"/note/", re.I))

        # 2) Chỉ vào vùng nội dung chính để tránh match menu/dropdown
        container = self.page.locator("main, .container, .content").first

        # 3) Tạo regex heading duy nhất
        if class_code:
            pattern = rf"^Note\s+Nhận\s+lớp\s+{re.escape(class_code)}$"
        else:
            pattern = r"^Note\s+Nhận\s+lớp\b"

        # 4) Ưu tiên role 'heading' để bắt đúng H1/H2/H3
        heading = container.get_by_role("heading", name=re.compile(pattern, re.I)).first
        expect(heading).to_be_visible(timeout=5000)
