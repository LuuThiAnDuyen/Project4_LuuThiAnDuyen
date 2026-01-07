
import re
from .base_page import BasePage


class SearchNewClassPage(BasePage):
    RESULTS_CONTAINER = (
        "[data-testid='search-results'], .search-results, .new-class-list, main"
    )
    BTN_VIEW_DETAIL = "a:has-text('Xem chi tiết'), button:has-text('Xem chi tiết')"

    EMPTY_TEXTS = [
        "không có lớp gia sư nào phù hợp",
        "không hiển thị kết quả",
        "không tìm thấy",
        "chưa có dữ liệu",
    ]

    def _container(self):
        cont = self.page.locator(self.RESULTS_CONTAINER).first
        return cont if cont.count() > 0 else self.page.locator("body")

    def get_page_text(self) -> str:
        return self._container().inner_text()

    def has_empty_state(self) -> bool:
        text = self.get_page_text().lower()
        return any(t in text for t in self.EMPTY_TEXTS)

    def get_results_count(self) -> int:
        text = self.get_page_text().lower()

        # 1) Ưu tiên đọc con số trong thông báo tổng
        #    Ví dụ: "Có 8 kết quả được tìm thấy."
        m = re.search(r"có\s+(\d+)\s+kết quả", text)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                pass

        # 2) Fallback: đếm số nút "Xem chi tiết" trong vùng kết quả
        return self._container().locator(self.BTN_VIEW_DETAIL).count()

    def get_ui_total_count(self) -> int | None:
        text = self.get_page_text().lower()
        m = re.search(r"có\s+(\d+)\s+kết quả", text)
        return int(m.group(1)) if m else None
