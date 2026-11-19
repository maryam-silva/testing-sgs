import re

import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL
from utils.playwright_helpers import cms_goto

PAGES_URL = f"{CMS_BASE_URL}/pages"


@pytest.mark.cms
@pytest.mark.smoke
def test_pages_list_loads(cms_page: Page):
    """TP-PAGES-01: Halaman daftar Pages tampil"""
    cms_goto(cms_page, PAGES_URL)
    expect(cms_page).to_have_url(PAGES_URL)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
def test_pages_portfolio_banner_detail_loads(cms_page: Page):
    """TP-PAGES-03: Halaman detail Manage Page (Banner) per halaman statis tampil"""
    cms_goto(cms_page, PAGES_URL)
    cms_page.locator("a[href='/pages/portfolio']").first.click()
    cms_page.wait_for_load_state("domcontentloaded")
    expect(cms_page).to_have_url(re.compile(r"/pages/portfolio"))
    expect(cms_page.get_by_text("Manage Page", exact=False)).to_be_visible()
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
def test_pages_redirects_when_not_logged_in(browser):
    """TP-PAGES-02: Akses /pages tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(PAGES_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
