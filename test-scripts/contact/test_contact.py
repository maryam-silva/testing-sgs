import re
import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL
from utils.playwright_helpers import cms_goto

CONTACT_URL = f"{CMS_BASE_URL}/contact"


@pytest.mark.cms
@pytest.mark.smoke
def test_contact_list_loads(cms_page: Page):
    """TP-CONTACT-01: Halaman Contact (CMS) tampil"""
    cms_goto(cms_page, CONTACT_URL)
    expect(cms_page).to_have_url(CONTACT_URL)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid], main").first
    ).to_be_visible()


@pytest.mark.cms
def test_contact_search_filters_list(cms_page: Page):
    """TP-CONTACT-03: Search contact berdasarkan nama memfilter tabel"""
    cms_goto(cms_page, CONTACT_URL)
    search = cms_page.locator("input[placeholder*='Search'], input[placeholder*='search']").first
    if search.count() == 0:
        pytest.skip("Tidak ada search box di halaman Contact")
    search.fill("zzz-tidak-ada-data-xyz")
    cms_page.wait_for_timeout(1200)
    expect(cms_page.locator(".ant-empty-description", has_text="No data")).to_be_visible()


@pytest.mark.cms
def test_contact_status_filter_visible(cms_page: Page):
    """TP-CONTACT-04: Filter Status pada halaman Contact tersedia"""
    cms_goto(cms_page, CONTACT_URL)
    status_filter = cms_page.get_by_text("Status", exact=True).first
    expect(status_filter).to_be_visible()


@pytest.mark.cms
def test_contact_redirects_when_not_logged_in(browser):
    """TP-CONTACT-02: Akses /contact tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(CONTACT_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
