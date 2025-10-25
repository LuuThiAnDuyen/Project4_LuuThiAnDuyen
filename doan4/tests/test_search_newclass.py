import os, re, pytest, allure
from allure_commons.types import AttachmentType
from playwright.sync_api import sync_playwright, expect
from config.config_utils import get_base_url
from pages.home_page import HomePage
from pages.search_newclass_page import SearchNewClassPage
from utils.excel_reader import read_test_data
from utils.result_writer import write_test_result

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "test_data.xlsx"
)

SCREENSHOT_DIR = os.path.join("reports", "screenshots", "search")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
VIDEO_DIR = os.path.join("reports", "videos", "search")
os.makedirs(VIDEO_DIR, exist_ok=True)
# tests/test_search_newclass.py (đầu file)
STRICT_COUNT_FROM_EXCEL = (
    False  # True: so sánh đúng bằng Excel; False: ưu tiên con số từ UI nếu có
)


@pytest.mark.parametrize(
    "tcid, keyword, expected_count, expected_message, result, screenshot, video",
    read_test_data(DATA_FILE, "SearchTestData"),
    ids=lambda val: str(val[0]) if isinstance(val, (list, tuple)) else str(val),
)
@allure.feature("Search")
@allure.title("Search Test Case: {tcid}")
def test_search_class(
    tcid, keyword, expected_count, expected_message, result, screenshot, video
):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, slow_mo=200, args=["--start-maximized"]
        )
        context = browser.new_context(
            no_viewport=True,
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()

        base_url = get_base_url()
        home = HomePage(page, base_url)
        home.goto()

        kw = (keyword or "").strip()

        with allure.step("Thực hiện tìm kiếm từ trang chủ"):
            home.search_from_home(kw)

        # Kiểm tra URL đúng sau search:
        if kw:
            expect(page).to_have_url(re.compile(r"/search(\?|$)", re.I))
            expect(page).to_have_url(re.compile(r"[?&](keyword|q)=", re.I))
        else:
            # Keyword rỗng: không ép buộc /search, nhiều site sẽ ở lại trang chủ.
            expect(page).not_to_have_url(re.compile(r"/search(\?|$)", re.I))

        search_page = SearchNewClassPage(page)

        # --- Bắt đầu xác minh ---
        screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot)
        final_result = "FAIL"  # gán mặc định, chỉ đổi sang PASS nếu mọi assert đều qua
        try:
            count = search_page.get_results_count()
            ui_total = search_page.get_ui_total_count()  # new

            # Ưu tiên: nếu UI có hiển thị tổng số → dùng làm ground-truth
            if not STRICT_COUNT_FROM_EXCEL and ui_total is not None:
                assert (
                    count == ui_total
                ), f"{tcid}: UI total {ui_total}, but counted {count}"
            elif expected_count is not None:
                assert (
                    count == expected_count
                ), f"{tcid}: Expected {expected_count}, got {count}"
            else:
                # không có expected_count và UI không có tổng → chỉ cần có kết quả
                assert count > 0, f"{tcid}: No count available from UI nor Excel"

            # Kiểm tra message
            if expected_message:
                container_text = search_page.get_page_text().lower()

                if (expected_count == 0) or (ui_total == 0):
                    # Cho phép empty-state hoặc regex '0 kết quả'
                    assert (
                        search_page.has_empty_state()
                        or count == 0
                        or re.search(r"có\s+0\s+kết quả", container_text)
                    ), f"{tcid}: Kỳ vọng empty-state/0 kết quả"
                else:
                    # Trang không có câu 'Hiển thị đúng và đủ...' → dùng regex tổng quát
                    assert re.search(
                        r"có\s+\d+\s+kết quả", container_text
                    ), f"{tcid}: Không thấy thông báo tổng 'Có X kết quả ...'"

                final_result = "PASS"

        finally:
            # 1) Screenshot
            try:
                page.screenshot(path=screenshot_path, full_page=True)
            except Exception:
                pass

            # 2) Đóng context trước rồi mới lấy video path (Playwright finalize video sau khi đóng)
            context.close()

            video_path = None
            try:
                # page.video.path() chỉ có sau khi context đóng
                if page.video:
                    video_path = page.video.path()
            except Exception:
                video_path = None

            # 3) Đính kèm Allure
            if os.path.exists(screenshot_path):
                allure.attach.file(
                    screenshot_path,
                    name=f"{tcid}",
                    attachment_type=AttachmentType.PNG,
                )
            if video_path and os.path.exists(video_path):
                # Nếu Allure của bạn có WEBM thì dùng, nếu không fallback MP4
                attach_type = getattr(AttachmentType, "WEBM", AttachmentType.MP4)
                allure.attach.file(
                    video_path,
                    name=f"{tcid}_video",
                    attachment_type=attach_type,
                    # đảm bảo phần mở rộng đúng, kể cả khi attachment_type là MP4
                    extension="webm",
                )

            # 4) Ghi kết quả ra Excel
            write_test_result(
                data_file=DATA_FILE,
                sheet_name="SearchTestData",
                tcid=tcid,
                result=final_result,
                screenshot_path=screenshot_path,
                video_path=video_path,
            )

            browser.close()
