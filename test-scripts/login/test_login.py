import pytest
from playwright.sync_api import Page, expect
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.config import CMS_BASE_URL

# App tidak punya route khusus "/login" -- unauthenticated landing tetap di "/"
# dan menampilkan form login langsung. Jadi status login dicek dari visibility
# form (Email/Password/Login button), bukan dari URL path.


def _login_form_visible(page: Page):
    return page.get_by_role("button", name="Login")


@pytest.fixture(autouse=True)
def go_to_login(page: Page):
    page.goto(CMS_BASE_URL)
    expect(_login_form_visible(page)).to_be_visible(timeout=15000)


# TP-LOGIN-01
@pytest.mark.cms
@pytest.mark.smoke
def test_login_success(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    expect(_login_form_visible(page)).not_to_be_visible(timeout=15000)


# TP-LOGIN-03
@pytest.mark.cms
def test_login_wrong_password(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill("wrongpassword123")
    page.get_by_role("button", name="Login").click()
    expect(_login_form_visible(page)).to_be_visible()


# TP-LOGIN-04
@pytest.mark.cms
def test_login_unregistered_email(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill("notexist@example.com")
    page.get_by_label("Password").fill("anypassword")
    page.get_by_role("button", name="Login").click()
    expect(_login_form_visible(page)).to_be_visible()


# TP-LOGIN-05
@pytest.mark.cms
def test_login_empty_email(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    expect(_login_form_visible(page)).to_be_visible()


# TP-LOGIN-06
@pytest.mark.cms
def test_login_empty_password(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_role("button", name="Login").click()
    expect(_login_form_visible(page)).to_be_visible()
