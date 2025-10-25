# pages/home_page.py
import re
from playwright.sync_api import expect
from .base_page import BasePage


class HomePage(BasePage):
    SEARCH_INPUT = "input[name='keyword'], input[name='q'], [placeholder*='Tìm'], [placeholder*='tìm']"
    SEARCH_BUTTON = (
        "button[type='submit'], button:has-text('Tìm'), button:has-text('Search')"
    )

    def __init__(self, page, base_url):
        super().__init__(page)
        self.base_url = base_url

    def goto(self):
        self.page.goto(self.base_url, wait_until="load")

    def search_from_home(self, kw: str | None):
        kw = (kw or "").strip()
        self.page.locator(self.SEARCH_INPUT).first.click()
        self.page.locator(self.SEARCH_INPUT).first.fill(kw)

        if kw:
            # chỉ chờ điều hướng khi có từ khóa
            with self.page.expect_navigation(
                url=re.compile(r"/search(\?|$)", re.I), wait_until="load"
            ):
                if self.page.locator(self.SEARCH_BUTTON).first.count() > 0:
                    self.page.locator(self.SEARCH_BUTTON).first.click()
                else:
                    self.page.locator(self.SEARCH_INPUT).first.press("Enter")
        else:
            # không chờ điều hướng khi rỗng (nhiều site ở lại trang chủ)
            if self.page.locator(self.SEARCH_BUTTON).first.count() > 0:
                self.page.locator(self.SEARCH_BUTTON).first.click()
            else:
                self.page.locator(self.SEARCH_INPUT).first.press("Enter")
            self.page.wait_for_load_state("networkidle")
