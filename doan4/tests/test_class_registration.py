from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.detail_page import DetailPage
from pages.new_classes_page import NewClassesPage


def test_register_class_flow(page, base_url):
    login = LoginPage(page, base_url)
    login.goto()
    login.login("luuthianduyen@gmail.com", "luuthianduyen247")
    login.is_login_successful()

    home = HomePage(page, base_url)
    home.goto()
    home.open_new_classes()
    new_classes = NewClassesPage(page, base_url)
    new_classes.open_first_class_detail()

    detail = DetailPage(page)
    detail.click_register()
    detail.click_continue()
    detail.verify_nhan_lop_text()
