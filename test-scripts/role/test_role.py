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
def test_role_search_filters_list(cms_page: Page):
    """TP-ROLE-03: Search role berdasarkan nama memfilter tabel"""
    cms_goto(cms_page, ROLE_URL)
    search = cms_page.locator("input[placeholder*='Search'], input[placeholder*='search']").first
    if search.count() == 0:
        pytest.skip("Tidak ada search box di halaman Role")
    search.fill("zzz-tidak-ada-data-xyz")
    cms_page.wait_for_timeout(1200)
    expect(cms_page.locator(".ant-empty-description", has_text="No data")).to_be_visible()


@pytest.mark.cms
def test_add_role_form_opens_with_permission_matrix(cms_page: Page):
    """TP-ROLE-04: Form Add Role terbuka dengan matrix permission (tanpa submit --
    tidak membuat role baru, struktur permission nyata di dev environment)."""
    cms_goto(cms_page, ROLE_URL)
    cms_page.get_by_role("button", name="Add Role").or_(
        cms_page.get_by_text("Add Role")
    ).first.click()
    cms_page.wait_for_timeout(800)
    for field in ("Role Name", "Role Description", "Permission"):
        expect(cms_page.get_by_text(field, exact=False).first).to_be_visible()


@pytest.mark.cms
def test_role_redirects_when_not_logged_in(browser):
    """TP-ROLE-02: Akses /role tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(ROLE_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
