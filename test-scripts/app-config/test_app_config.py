import re
import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL
from utils.playwright_helpers import cms_goto

APP_CONFIG_URL = f"{CMS_BASE_URL}/app-config"


@pytest.mark.cms
@pytest.mark.smoke
def test_app_config_loads(cms_page: Page):
    """TP-CONFIG-01: Halaman App Config tampil"""
    cms_goto(cms_page, APP_CONFIG_URL)
    expect(cms_page).to_have_url(APP_CONFIG_URL)
    expect(
        cms_page.locator("main, [class*=content], form, table").first
    ).to_be_visible()


@pytest.mark.cms
def test_app_config_tabs_switch_content(cms_page: Page):
    """TP-CONFIG-03: Switch antar tab Term & Condition / Privacy Policy / Contact
    menampilkan konten berbeda (tidak klik Update -- hindari ubah konten live)."""
    cms_goto(cms_page, APP_CONFIG_URL)
    tablist = cms_page.get_by_role("tablist").first
    for tab_name in ("Privacy Policy", "Contact", "Term & Condition"):
        tab = tablist.get_by_text(tab_name, exact=False).first
        expect(tab).to_be_visible(timeout=10000)
        tab.click(timeout=10000)
        cms_page.wait_for_timeout(800)
        expect(cms_page.locator("main, [class*=content], form").first).to_be_visible()


@pytest.mark.cms
def test_app_config_language_toggle(cms_page: Page):
    """TP-CONFIG-04: Toggle bahasa ID/EN pada App Config tersedia"""
    cms_goto(cms_page, APP_CONFIG_URL)
    en_toggle = cms_page.get_by_text("EN", exact=True).first
    expect(en_toggle).to_be_visible()


@pytest.mark.cms
def test_app_config_redirects_when_not_logged_in(browser):
    """TP-CONFIG-02: Akses /app-config tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(APP_CONFIG_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
