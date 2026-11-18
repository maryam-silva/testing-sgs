import re
import pytest
from playwright.sync_api import Page, expect
from utils.playwright_helpers import login_cms


@pytest.fixture(autouse=True)
def logged_in(page: Page):
    login_cms(page)


# TP-DASH-01
def test_dashboard_loads(page: Page):
    expect(page).not_to_have_url(re.compile(r"/login"))


# TP-DASH-02
def test_sidebar_navigation_visible(page: Page):
    # Sidebar nav should contain at least one link
    nav = page.locator("nav, aside, [role='navigation']").first
    expect(nav).to_be_visible()


# TP-DASH-04
def test_dashboard_redirects_when_not_logged_in(browser):
    from data.config import CMS_BASE_URL
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(CMS_BASE_URL + "/dashboard")
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
