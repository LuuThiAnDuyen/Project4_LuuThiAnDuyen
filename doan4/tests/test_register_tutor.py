import os, pytest, allure
from allure_commons.types import AttachmentType
from playwright.sync_api import sync_playwright, expect
from config.config_utils import get_marketing_url
from pages.register_tutor_page import RegisterTutorPage  # giả sử tên POM như vậy
from utils.excel_reader import read_test_data

SCREENSHOT_DIR = os.path.join("reports", "screenshots", "register_tutor")
VIDEO_DIR = os.path.join("reports", "videos")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


@pytest.mark.parametrize(
    "tcid, gender, name, phone, address, note, expected_message, result, screenshot, video",
    read_test_data(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "test_data.xlsx"
        ),
        "RegisterTutorTestData",
    ),
    ids=lambda val: str(val[0]) if isinstance(val, (list, tuple)) else str(val),
)
@allure.feature("Register Tutor")
@allure.title("Register Tutor Test Case: {tcid}")
def test_register_tutor(
    tcid,
    gender,
    name,
    phone,
    address,
    note,
    expected_message,
    result,
    screenshot,
    video,
):
    gender = "" if gender is None else str(gender)
    name = "" if name is None else str(name)
    phone = "" if phone is None else str(phone)
    address = "" if address is None else str(address)
    note = "" if note is None else str(note)
    expected_message = "" if expected_message is None else str(expected_message)

    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{tcid}.png")
    final_result = "FAIL"

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

        reg_page = RegisterTutorPage(page)
        marketing_url = get_marketing_url()
        reg_page.goto(marketing_url)

        with allure.step("Điền form và gửi"):
            reg_page.register(gender, name, phone, address, note)

        try:
            if expected_message.strip():
                expect(page.get_by_text(expected_message, exact=False)).to_be_visible(
                    timeout=10000
                )
            else:
                # khi không có expected_message -> kỳ vọng ở lại trang form
                expect(page).to_have_url(
                    marketing_url + "/dang-ky-thue-gia-su", timeout=10000
                )

            final_result = "PASS"
        except AssertionError:
            final_result = "FAIL"
        finally:
            # 1) Screenshot
            try:
                page.screenshot(path=screenshot_path, full_page=True)
            except Exception:
                pass

            if os.path.exists(screenshot_path):
                allure.attach.file(
                    screenshot_path,
                    name=f"{tcid}_{final_result.lower()}",
                    attachment_type=AttachmentType.PNG,
                )

            # 2) Giữ handle video trước khi đóng
            page_video = getattr(page, "video", None)

            # 3) Đóng context (sẽ đóng luôn page) để finalize video
            context.close()
            browser.close()

            # 4) Lấy đường dẫn video sau khi context đóng
            video_path = None
            try:
                if page_video:
                    video_path = page_video.path()
            except Exception:
                video_path = None

            # 5) Đính kèm video vào Allure (WEBM nếu có, fallback MP4)
            if video_path and os.path.exists(video_path):
                attach_type = getattr(AttachmentType, "WEBM", AttachmentType.MP4)
                allure.attach.file(
                    video_path,
                    name=f"{tcid}_video",
                    attachment_type=attach_type,
                    extension="webm",
                )

    # KHÔNG đóng page/context/browser ở ngoài khối `with` nữa
