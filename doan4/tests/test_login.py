# tests/test_login.py
import os
import shutil
import pytest
import allure
from playwright.sync_api import sync_playwright, expect

from config.config_utils import get_base_url
from pages.login_page import LoginPage
from utils.excel_reader import read_test_data
from utils.result_writer import write_test_result

DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "test_data.xlsx"
)

# Artifact dirs
SCREENSHOT_DIR = os.path.join("reports", "screenshots", "login")
VIDEO_DIR = os.path.join("reports", "videos", "login")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


@pytest.mark.parametrize(
    "tcid, email, password, expected_message, actual_result, screenshot, video",
    read_test_data(DATA_FILE, "LoginTestData"),
    ids=lambda val: str(val[0]) if isinstance(val, list) else str(val),
)
@allure.feature("Login")
@allure.title("Login Test Case: {tcid}")
def test_login(
    tcid, email, password, expected_message, actual_result, screenshot, video
):
    email = "" if email is None else str(email)
    password = "" if password is None else str(password)
    expected_message = "" if expected_message is None else str(expected_message)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, slow_mo=500, args=["--start-maximized"]
        )
        context = browser.new_context(
            no_viewport=True,
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        login_page = LoginPage(page, get_base_url())
        login_page.goto()
        login_page.login(email, password)

        screenshot_path = os.path.join(SCREENSHOT_DIR, f"{tcid}.png")
        # file đích bạn muốn lưu video
        final_video_path = os.path.join(VIDEO_DIR, f"{tcid}.webm")
        result = "FAIL"

        try:
            # Ưu tiên dùng expect để chờ text xuất hiện (ổn định hơn so với inner_text ngay lập tức)
            if expected_message.strip():
                expect(page.get_by_text(expected_message, exact=False)).to_be_visible(
                    timeout=10000
                )
            else:
                # Nếu dataset không có expected_message: coi pass khi thấy marker thành công
                expect(login_page.success_marker).to_be_visible(timeout=10000)

            result = "PASS"
            page.screenshot(path=screenshot_path)
            allure.attach.file(
                screenshot_path,
                name=f"{tcid}_success",
                attachment_type=allure.attachment_type.PNG,
            )

        except AssertionError:
            page.screenshot(path=screenshot_path)
            allure.attach.file(
                screenshot_path,
                name=f"{tcid}_fail",
                attachment_type=allure.attachment_type.PNG,
            )

        finally:
            # Đóng page rồi đóng context để đảm bảo video được flush ra đĩa
            page.close()
            context.close()

            # Sau khi context đóng, mới lấy được path video gốc
            try:
                src_video = page.video.path()
            except Exception:
                src_video = None

            if src_video and os.path.exists(src_video):
                # Move về tên file theo TCID
                shutil.move(src_video, final_video_path)
                allure.attach.file(
                    final_video_path,
                    name=f"{tcid}_video",
                    attachment_type=allure.attachment_type.WEBM,
                )
            else:
                final_video_path = None  # không có video

            # Ghi ngược kết quả vào Excel
            write_test_result(
                DATA_FILE,
                "LoginTestData",
                tcid,
                result,
                screenshot_path,
                final_video_path,
            )

            browser.close()

        if result == "FAIL":
            pytest.fail(
                f"{tcid} FAIL: Expected='{expected_message}' not found", pytrace=False
            )
