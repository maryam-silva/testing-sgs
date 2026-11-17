from playwright.sync_api import Page
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.config import CMS_BASE_URL


def login_cms(page: Page) -> None:
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url(lambda url: "/login" not in url, timeout=10000)
