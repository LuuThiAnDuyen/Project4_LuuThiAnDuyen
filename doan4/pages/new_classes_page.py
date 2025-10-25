# pages/new_classes_page.py
from playwright.sync_api import expect
import os, time
from .base_page import BasePage


class NewClassesPage(BasePage):
    def __init__(self, page, base_url):
        super().__init__(page)
        self.base_url = base_url
        self.url_path_candidates = [
            "/danh-sach-lop-moi",
            "/new-classes",
            "/classes/new",
        ]

    def ensure_on_page(self):
        # nếu chưa ở đúng path, cố gắng điều hướng
        if not any(p in self.page.url for p in self.url_path_candidates):
            for p in self.url_path_candidates:
                try:
                    self.page.goto(self.base_url.rstrip("/") + p, wait_until="load")
                    self.page.wait_for_load_state("networkidle")
                    if p in self.page.url:
                        break
                except Exception:
                    pass

    def open_first_class_detail(self):
        self.ensure_on_page()
        self.page.wait_for_load_state("networkidle")

        candidates = [
            "a:has-text('Chi tiết')",
            "a:has-text('Xem chi tiết')",
            "a:has-text('Xem lớp')",
            ".class-item a[href*='/lop-']",
            ".class-card a[href*='/lop-']",
            "a[href*='/chi-tiet']",
            "a[href*='class-detail']",
        ]
        for sel in candidates:
            loc = self.page.locator(sel).first
            if loc.count() and loc.is_visible():
                try:
                    loc.scroll_into_view_if_needed(timeout=1000)
                    loc.click()
                    self.page.wait_for_load_state("networkidle")
                    return
                except Exception:
                    pass

        os.makedirs("reports/screenshots", exist_ok=True)
        snap = (
            f"reports/screenshots/new_classes_open_detail_debug_{int(time.time())}.png"
        )
        self.page.screenshot(path=snap, full_page=True)
        raise AssertionError(f"Không mở được chi tiết lớp. Ảnh debug: {snap}")
