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
        expect(self.page).to_have_url(re.compile(r"/note/", re.I), timeout=15000)

        title = self.page.locator("main[role='main'] h1.h3.text-primary").first
        expect(title).to_be_visible(timeout=15000)
        if class_code:
            expect(title).to_have_text(
                re.compile(rf"Note\s+Nhận\s+lớp\s+{re.escape(class_code)}", re.I)
            )
        else:
            expect(title).to_have_text(re.compile(r"Note\s+Nhận\s+lớp", re.I))
