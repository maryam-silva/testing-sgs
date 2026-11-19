import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL

PAGES_URL = f"{CMS_BASE_URL}/pages"


@pytest.mark.cms
@pytest.mark.smoke
def test_pages_list_loads(cms_page: Page):
    """TP-PAGES-01: Halaman daftar Pages tampil"""
    cms_page.goto(PAGES_URL)
    cms_page.wait_for_load_state("networkidle")
    expect(cms_page).to_have_url(PAGES_URL)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
def test_pages_redirects_when_not_logged_in(browser):
    """TP-PAGES-02: Akses /pages tanpa login redirect ke login"""
    import re
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(PAGES_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
