# pages/new_classes_page.py
import re
from playwright.sync_api import Page, expect


class NewClassesPage:
    def __init__(self, page: Page):
        self.page = page
        self.first_detail_by_xpath = self.page.locator(
            "xpath=//body[1]/main[1]/section[2]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]"
        )
        self.first_detail_by_text = self.page.get_by_role(
            "link", name="Xem chi tiết", exact=True
        ).first

    def open_first_detail(self):
        self.page.wait_for_load_state("domcontentloaded")
        if self.first_detail_by_xpath.count():
            expect(self.first_detail_by_xpath).to_be_visible(timeout=5000)
            with self.page.expect_navigation():
                self.first_detail_by_xpath.click()
        else:
            expect(self.first_detail_by_text).to_be_visible(timeout=5000)
            with self.page.expect_navigation():
                self.first_detail_by_text.click()

        expect(self.page).to_have_url(re.compile("/(lop|chi-tiet|nhan-lop)", re.I))
