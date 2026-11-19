import re
import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL
from utils.playwright_helpers import cms_goto

ROLE_URL = f"{CMS_BASE_URL}/role"


@pytest.mark.cms
@pytest.mark.smoke
def test_role_list_loads(cms_page: Page):
    """TP-ROLE-01: Halaman daftar Role & Permission tampil"""
    cms_goto(cms_page, ROLE_URL)
    expect(cms_page).to_have_url(ROLE_URL)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
def test_role_redirects_when_not_logged_in(browser):
    """TP-ROLE-02: Akses /role tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(ROLE_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
