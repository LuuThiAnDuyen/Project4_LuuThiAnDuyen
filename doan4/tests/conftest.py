import os
import pytest
import allure
from playwright.sync_api import sync_playwright
from config.config_utils import get_base_url

SCREENSHOT_DIR = os.path.join("reports", "screenshots")
VIDEO_DIR = os.path.join("reports", "videos")
ALLURE_RESULTS_DIR = os.path.join("reports", "allure-results")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(ALLURE_RESULTS_DIR, exist_ok=True)


@pytest.fixture(scope="session")
def base_url():
    return get_base_url()


@pytest.fixture(scope="session")
def playwright_instance():
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(headless=False)
    yield browser
    browser.close()


@pytest.fixture()
def page(browser, base_url):
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture(scope="function")
def browser_context():
    """Fixture Playwright browser context có quay video"""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, slow_mo=1000, args=["--start-maximized"]
        )
        context = browser.new_context(
            no_viewport=True,
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        yield page, context, browser  # trả ra cho test sử dụng

        # cleanup cuối cùng
        if page.video:
            try:
                video_path = page.video.path()
                if video_path and os.path.exists(video_path):
                    allure.attach.file(
                        video_path,
                        name="video",
                        attachment_type=allure.attachment_type.WEBM,
                    )
            except Exception:
                pass

        context.close()
        browser.close()
