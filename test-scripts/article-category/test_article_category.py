import re
import pytest
from playwright.sync_api import Page, expect

from data.cms_data import auto
from data.config import CMS_BASE_URL
from utils.playwright_helpers import cms_goto

CATEGORY_URL = f"{CMS_BASE_URL}/article-category"
TITLE = auto("Test Category SGS")


def _go_categories(page: Page):
    cms_goto(page, CATEGORY_URL)


def _click_add(page: Page):
    page.locator(
        "a[href*='create'], a[href*='add'], "
        "button:has-text('Create'), button:has-text('Add'), "
        "button:has-text('Tambah'), button:has-text('Buat'), "
        "a:has-text('Create'), a:has-text('Add'), a:has-text('Tambah')"
    ).first.click()
    page.wait_for_load_state("networkidle")


def _find_row(page: Page, text: str):
    return page.locator(f"tr:has-text('{text}')").first


def _cleanup_category(page: Page, title: str):
    _go_categories(page)
    row = _find_row(page, title)
    if row.count() == 0:
        return
    row.get_by_role("button", name="Delete").or_(
        row.get_by_role("button", name="Hapus")
    ).or_(
        row.locator("button[aria-label*='delete'], button[aria-label*='Delete']")
    ).first.click()
    confirm_btn = page.get_by_role("button", name="Confirm").or_(
        page.get_by_role("button", name="Ya")
    ).or_(
        page.get_by_role("button", name="Yes")
    ).first
    if confirm_btn.count() > 0:
        confirm_btn.click()
    page.wait_for_load_state("networkidle")


@pytest.mark.cms
@pytest.mark.smoke
def test_article_category_list_loads(cms_page: Page):
    """TP-ARTCAT-01: Halaman daftar News Categories tampil"""
    _go_categories(cms_page)
    expect(cms_page).to_have_url(CATEGORY_URL)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.crud
def test_create_article_category(cms_page: Page):
    """TP-ARTCAT-02: Buat kategori artikel baru berhasil"""
    _go_categories(cms_page)
    _click_add(cms_page)
    cms_page.wait_for_load_state("networkidle")

    name_input = cms_page.get_by_label("Name", exact=False).or_(
        cms_page.get_by_label("Title", exact=False)
    ).first
    name_input.fill(TITLE)

    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).or_(
        cms_page.get_by_role("button", name="Simpan")
    ).first.click()
    cms_page.wait_for_load_state("networkidle")

    try:
        _go_categories(cms_page)
        expect(_find_row(cms_page, TITLE)).to_be_visible()
    finally:
        _cleanup_category(cms_page, TITLE)


@pytest.mark.cms
def test_create_article_category_empty_name(cms_page: Page):
    """TP-ARTCAT-03: Simpan kategori tanpa nama gagal"""
    _go_categories(cms_page)
    _click_add(cms_page)
    cms_page.wait_for_load_state("networkidle")

    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).first.click()

    expect(
        cms_page.locator("[class*=error], [class*=invalid], [role='alert']").first
    ).to_be_visible()


@pytest.mark.cms
def test_article_category_redirects_when_not_logged_in(browser):
    """TP-ARTCAT-04: Akses /article-category tanpa login redirect ke login"""
    context = browser.new_context(base_url=CMS_BASE_URL)
    p = context.new_page()
    p.goto(CATEGORY_URL)
    expect(p).to_have_url(re.compile(r"/login|/$"))
    p.close()
    context.close()
