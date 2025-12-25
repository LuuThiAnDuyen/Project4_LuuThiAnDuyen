# tests/test_login.py
import os
import shutil
import pytest
import allure
from playwright.sync_api import sync_playwright, expect

from config.config_utils import get_base_url
from pages.login_page import LoginPage

from utils.login_data_loader import read_login_cases_any
from utils.universal_result_writer import write_test_result_any
from utils.result_writer import write_test_result  # Excel writer cũ

from utils.sqlserver_client import load_login_cases_from_db, write_login_result_to_db
from pathlib import Path


# --- Data source selection ---
DATA_SOURCE = "data/login_test_data.csv"
#DATA_SOURCE = "data/login_test_data.json"
#DATA_SOURCE = "data/login_test_data.xml"
#DATA_SOURCE = "data/login_test_data.yaml"
#DATA_SOURCE = "data/test_data.xlsx"
#DATA_SOURCE = "db"  

def _get_test_data():
    if DATA_SOURCE == "db":
        print("[DATA SOURCE] SQL SERVER")
        data = load_login_cases_from_db(active_only=True)
        print(f"[DATA SOURCE] DB cases loaded: {len(data)}")
        return data

    print(f"[DATA SOURCE] FILE: {DATA_SOURCE}")
    data = read_login_cases_any(DATA_SOURCE, sheet_name="LoginTestData")
    print(f"[DATA SOURCE] FILE cases loaded: {len(data)}")
    return data
# Artifact dirs
SCREENSHOT_DIR = os.path.join("reports", "screenshots", "login")
VIDEO_DIR = os.path.join("reports", "videos", "login")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


@pytest.mark.parametrize(
    "tcid, email, password, expected_message, actual_result, screenshot, video",
    _get_test_data(),
)
@allure.feature("Login")
@allure.title("Login Test Case: {tcid}")
def test_login(tcid, email, password, expected_message, actual_result, screenshot, video):

    if DATA_SOURCE == "db":
        allure.attach(
            "SQL SERVER",
            name="DATA SOURCE",
            attachment_type=allure.attachment_type.TEXT,
        )
    else:
        allure.attach(
            DATA_SOURCE,
            name="DATA SOURCE",
            attachment_type=allure.attachment_type.TEXT,
        )

    email = "" if email is None else str(email)
    password = "" if password is None else str(password)
    expected_message = "" if expected_message is None else str(expected_message)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500, args=["--start-maximized"])
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
        final_video_path = os.path.join(VIDEO_DIR, f"{tcid}.webm")
        result = "FAIL"

        try:
            if expected_message.strip():
                expect(page.get_by_text(expected_message, exact=False)).to_be_visible(timeout=10000)
            else:
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
            page.close()
            context.close()

            # video flush xong mới lấy path
            try:
                src_video = page.video.path()
            except Exception:
                src_video = None

            if src_video and os.path.exists(src_video):
                shutil.move(src_video, final_video_path)
                allure.attach.file(
                    final_video_path,
                    name=f"{tcid}_video",
                    attachment_type=allure.attachment_type.WEBM,
                )
            else:
                final_video_path = ""  # DB/file writer nên nhận "" thay vì None

            # --- Write back result ---
            if DATA_SOURCE == "db":
                write_login_result_to_db(
                    tcid=tcid,
                    result=result,
                    screenshot=screenshot_path,
                    video=final_video_path,
                )
            else:
                ext = Path(DATA_SOURCE).suffix.lower()
                if ext in [".xlsx", ".xls"]:
                    write_test_result(
                        DATA_SOURCE,
                        "LoginTestData",
                        tcid,
                        result,
                        screenshot_path,
                        final_video_path,
                    )
                else:
                    write_test_result_any(
                        DATA_SOURCE,
                        tcid,
                        result,
                        screenshot_path,
                        final_video_path,
                    )

            browser.close()

        if result == "FAIL":
            pytest.fail(f"{tcid} FAIL: Expected='{expected_message}' not found", pytrace=False)
