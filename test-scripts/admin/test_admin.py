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
def test_admin_search_filters_list(cms_page: Page):
    """TP-ADMIN-03: Search admin berdasarkan nama memfilter tabel"""
    cms_goto(cms_page, ADMIN_URL)
    search = cms_page.locator("input[placeholder*='Search'], input[placeholder*='search']").first
    if search.count() == 0:
        pytest.skip("Tidak ada search box di halaman Admin")
    search.fill("zzz-tidak-ada-data-xyz")
    cms_page.wait_for_timeout(1200)
    expect(cms_page.locator(".ant-empty-description", has_text="No data")).to_be_visible()


@pytest.mark.cms
def test_add_admin_form_opens_with_required_fields(cms_page: Page):
    """TP-ADMIN-04: Form Add Admin terbuka dan field wajib tampil (tanpa submit --
    tidak membuat akun admin baru, data user nyata di dev environment)."""
    cms_goto(cms_page, ADMIN_URL)
    cms_page.get_by_role("button", name="Add Admin").or_(
        cms_page.get_by_text("Add Admin")
    ).first.click()
    cms_page.wait_for_load_state("domcontentloaded")
    expect(cms_page).to_have_url(re.compile(r"/admin/add"))
    for field in ("First Name", "Last Name", "Email", "Password", "Role"):
        expect(cms_page.get_by_text(field, exact=False).first).to_be_visible()


@pytest.mark.cms
def test_admin_redirects_when_not_logged_in(browser):
    """TP-ADMIN-02: Akses /admin tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(ADMIN_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
