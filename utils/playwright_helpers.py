import re
from playwright.sync_api import Page, expect
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.config import CMS_BASE_URL

_RE_LOGIN = re.compile(r"/login")


def login_cms(page: Page) -> None:
    page.goto(CMS_BASE_URL)
    page.wait_for_load_state("networkidle")
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_load_state("networkidle")
    # expect keeps retrying until redirect settles — lebih tahan race condition
    expect(page).not_to_have_url(_RE_LOGIN, timeout=15000)
