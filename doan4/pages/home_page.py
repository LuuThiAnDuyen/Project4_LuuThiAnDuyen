# pages/home_page.py
import re
import os, time
from playwright.sync_api import expect
from .base_page import BasePage


class HomePage(BasePage):
    SEARCH_INPUT = "input[name='keyword'], input[name='q'], [placeholder*='Tìm'], [placeholder*='tìm']"
    SEARCH_BUTTON = (
        "button[type='submit'], button:has-text('Tìm'), button:has-text('Search')"
    )
    # 👉 CHỈNH LẠI TEXT/HREF CHO ĐÚNG THỰC TẾ MENU CỦA BẠN (nếu khác)
    NEW_CLASS_LINK = (
        "a:has-text('Lớp học mới'), "
        "a:has-text('New Classes'), "
        "a:has-text('Danh sách lớp'), "
        "a:has-text('Tìm lớp'), "
        "a[href*='new-class'], a[href*='new-classes'], a[href*='classes/new'], a[href*='lop-moi']"
    )

    def __init__(self, page, base_url):
        super().__init__(page)
        self.base_url = base_url

    def goto(self):
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

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

    def open_new_classes(self):
        """
        Mở trang 'Lớp học mới' với nhiều chiến lược:
        - Đảm bảo đang ở Home
        - Mở hamburger/dropdown nếu có
        - Thử nhiều selector/text khác nhau
        - Fallback điều hướng trực tiếp theo path phổ biến
        - Chụp ảnh debug nếu vẫn không tìm thấy
        """
        # 0) về Home cho chắc
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        self.page.wait_for_load_state("networkidle")

        # 1) mở hamburger/menu nếu có
        hamburger_selectors = [
            "[aria-label='Menu']",
            "[data-testid='menu']",
            ".navbar-toggler",
            ".hamburger",
            "button:has(svg)",
        ]
        for sel in hamburger_selectors:
            loc = self.page.locator(sel)
            if loc.count() and loc.first.is_visible():
                try:
                    loc.first.click()
                    self.page.wait_for_timeout(250)
                    break
                except Exception:
                    pass

        # 2) thử tìm bằng nhiều cách
        name_regex = re.compile(
            r"(Lớp\s*học\s*mới|Lop\s*hoc\s*moi|New\s*Classes|Danh\s*sách\s*lớp|Tìm\s*lớp)",
            re.I,
        )
        candidates = [
            lambda: self.page.get_by_role("link", name=name_regex),
            lambda: self.page.get_by_role("button", name=name_regex),
            lambda: self.page.get_by_text(name_regex),
            lambda: self.page.locator(self.NEW_CLASS_LINK),
        ]

        for factory in candidates:
            loc = factory()
            if loc.count() > 0:
                cand = loc.first
                try:
                    cand.scroll_into_view_if_needed(timeout=1000)
                    expect(cand).to_be_visible(timeout=2000)
                    cand.click()
                    self.page.wait_for_load_state("networkidle")
                    return
                except Exception:
                    # thử ứng viên khác
                    pass

        # 3) fallback: đoán path và đi thẳng URL
        for path in ["/new-class", "/new-classes", "/classes/new", "/lop-moi"]:
            try:
                self.page.goto(self.base_url.rstrip("/") + path, wait_until="load")
                self.page.wait_for_load_state("networkidle")
                # có dấu hiệu là trang danh sách lớp?
                if (
                    self.page.locator(
                        "h1, h2, .class-item, [data-testid*='class']"
                    ).count()
                    > 0
                ):
                    return
            except Exception:
                pass

        # 4) chụp ảnh debug rồi raise lỗi rõ ràng
        os.makedirs("reports/screenshots", exist_ok=True)
        snap = f"reports/screenshots/open_new_classes_debug_{int(time.time())}.png"
        self.page.screenshot(path=snap, full_page=True)
        raise AssertionError(
            f"Không tìm thấy menu/đường dẫn 'Lớp học mới'. Đã chụp ảnh debug: {snap}. "
            "Hãy chỉnh lại NEW_CLASS_LINK hoặc name_regex cho khớp text/URL thực tế."
        )
