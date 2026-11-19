import re
import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL

CONTACT_URL = f"{CMS_BASE_URL}/contact"


@pytest.mark.cms
@pytest.mark.smoke
def test_contact_list_loads(cms_page: Page):
    """TP-CONTACT-01: Halaman Contact (CMS) tampil"""
    cms_page.goto(CONTACT_URL)
    cms_page.wait_for_load_state("networkidle")
    expect(cms_page).to_have_url(CONTACT_URL)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid], main").first
    ).to_be_visible()


@pytest.mark.cms
def test_contact_redirects_when_not_logged_in(browser):
    """TP-CONTACT-02: Akses /contact tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(CONTACT_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
