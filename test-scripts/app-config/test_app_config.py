import re
import pytest
from playwright.sync_api import Page, expect
from data.config import CMS_BASE_URL

APP_CONFIG_URL = f"{CMS_BASE_URL}/app-config"


@pytest.mark.cms
@pytest.mark.smoke
def test_app_config_loads(cms_page: Page):
    """TP-CONFIG-01: Halaman App Config tampil"""
    cms_page.goto(APP_CONFIG_URL)
    cms_page.wait_for_load_state("networkidle")
    expect(cms_page).to_have_url(APP_CONFIG_URL)
    expect(
        cms_page.locator("main, [class*=content], form, table").first
    ).to_be_visible()


@pytest.mark.cms
def test_app_config_redirects_when_not_logged_in(browser):
    """TP-CONFIG-02: Akses /app-config tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(APP_CONFIG_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
