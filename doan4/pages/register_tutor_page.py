# pages/register_tutor_page.py
from playwright.sync_api import Page, Locator, expect


class RegisterTutorPage:
    def __init__(self, page: Page):
        self.page: Page = page
        self.page.set_default_timeout(10000)

        self.body: Locator = page.locator("body")

        self.gender_anh_val: Locator = page.locator(
            "//div[@class='form-check form-check-radio mr-4']//input[@name='gender']"
        )
        self.gender_chi_val: Locator = page.locator("//input[@value='2']")

        self.name_input: Locator = page.locator("//input[@id='name']")

        self.phone_input: Locator = page.locator("//input[@id='phone']")

        self.address_input: Locator = page.locator(
            "//input[@placeholder='Số nhà, tên đường']"
        )

        self.note_input: Locator = page.locator(
            "//input[@placeholder='Ghi chú (không bắt buộc)']"
        )

        # --- Nút submit (cả button lẫn input submit) ---
        self.submit_btn: Locator = page.locator("//input[@value='Đăng Ký Ngay']")

    def goto(self, marketing_url: str):
        url = f"{marketing_url.rstrip('/')}/dang-ky-thue-gia-su"
        self.page.goto(url, wait_until="domcontentloaded")
        # đảm bảo form hiển thị
        expect(self.submit_btn).to_be_visible(timeout=10000)
        expect(self.name_input).to_be_visible(timeout=10000)

    # helpers
    def _safe_fill(self, locator: Locator, value: str | None):
        if value is not None and str(value).strip() != "":
            expect(locator).to_be_visible()
            locator.click()
            locator.fill(str(value))

    def _select_gender(self, gender: str | None):
        if not gender:
            return
        g = str(gender).strip().lower()

        # thử theo label
        if g in ("anh", "nam", "a", "male", "m"):
            try:
                self.gender_label("Anh").check()
                return
            except Exception:
                pass
            if self.gender_anh_val.count() > 0:
                self.gender_anh_val.first.check()
                return

        if g in ("chị", "chi", "nữ", "nu", "female", "f"):
            try:
                self.gender_label("Chị").check()
                return
            except Exception:
                pass
            if self.gender_chi_val.count() > 0:
                self.gender_chi_val.first.check()
                return

        # nếu không match: chọn radio đầu tiên (tránh treo)
        if self.any_gender.count() > 0:
            self.any_gender.first.check()

    def register(self, gender: str, name: str, phone: str, address: str, note: str):
        self._select_gender(gender)
        self._safe_fill(self.name_input, name)
        self._safe_fill(self.phone_input, phone)
        self._safe_fill(self.address_input, address)
        self._safe_fill(self.note_input, note)
        self.submit_btn.click()

    def get_page_text(self) -> str:
        return self.body.inner_text()
