# pages/login_page.py
from playwright.sync_api import Page, Locator, expect


class LoginPage:
    def __init__(self, page: Page, base_url: str):
        self.page: Page = page
        self.base_url = base_url.rstrip("/")

        # Locators (ổn định, dễ đọc)
        self.link_login: Locator = page.locator(
            "//a[contains(.,'Đăng nhập vào tài khoản')]"
        )
        self.email: Locator = page.locator("input#email")
        self.password: Locator = page.locator("input#password")
        self.submit: Locator = page.locator("button[type='submit']")
        self.body: Locator = page.locator("body")

        self.success_marker: Locator = page.get_by_text(
            "Tài khoản của tôi", exact=False
        )

    def goto(self):
        self.page.goto(self.base_url, wait_until="domcontentloaded")

    def login(self, email: str = "", password: str = ""):
        self.link_login.click()
        self.email.fill(email or "")
        self.password.fill(password or "")
        self.submit.click()

    def is_login_successful(self, timeout: int = 10000) -> bool:
        try:
            expect(self.success_marker).to_be_visible(timeout=timeout)
            return True
        except AssertionError:
            return False

    def get_page_text(self) -> str:
        return self.body.inner_text()
