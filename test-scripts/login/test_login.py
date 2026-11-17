import pytest
from playwright.sync_api import Page, expect
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.config import CMS_BASE_URL


@pytest.fixture(autouse=True)
def go_to_login(page: Page):
    page.goto(CMS_BASE_URL)
    expect(page).to_have_url(lambda url: "/login" in url or url == CMS_BASE_URL + "/")


# TP-LOGIN-01
def test_login_success(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    expect(page).not_to_have_url(lambda url: "/login" in url)


# TP-LOGIN-03
def test_login_wrong_password(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill("wrongpassword123")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(lambda url: "/login" in url or url == CMS_BASE_URL + "/")


# TP-LOGIN-04
def test_login_unregistered_email(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill("notexist@example.com")
    page.get_by_label("Password").fill("anypassword")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(lambda url: "/login" in url or url == CMS_BASE_URL + "/")


# TP-LOGIN-05
def test_login_empty_email(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    # Expects validation message or stays on login
    expect(page).to_have_url(lambda url: "/login" in url or url == CMS_BASE_URL + "/")


# TP-LOGIN-06
def test_login_empty_password(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(lambda url: "/login" in url or url == CMS_BASE_URL + "/")
