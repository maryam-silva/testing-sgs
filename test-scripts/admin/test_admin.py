import re
import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL
from utils.playwright_helpers import cms_goto

ADMIN_URL = f"{CMS_BASE_URL}/admin"


@pytest.mark.cms
@pytest.mark.smoke
def test_admin_list_loads(cms_page: Page):
    """TP-ADMIN-01: Halaman daftar Admin tampil"""
    cms_goto(cms_page, ADMIN_URL)
    expect(cms_page).to_have_url(re.compile(r"/admin"))
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
def test_admin_redirects_when_not_logged_in(browser):
    """TP-ADMIN-02: Akses /admin tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(ADMIN_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
