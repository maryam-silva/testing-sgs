"""
Test suite: Banners CMS SGS
Mencakup list, CRUD, validasi, dan cross-check ke web.
Semua data test berawalan [AUTO] dan dihapus di teardown.
"""

import os
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect

from data.cms_data import auto
from data.config import CMS_BASE_URL, WEB_BASE_URL

BANNERS_URL = f"{CMS_BASE_URL}/banners"
IMAGE_PATH = str(Path(__file__).parent.parent.parent / "data" / "assets" / "test-image.jpg")

TITLE = auto("Test Banner SGS")
TITLE_EDITED = auto("Test Banner SGS EDITED")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_banners(page: Page):
    page.goto(BANNERS_URL)
    page.wait_for_load_state("networkidle")


def _fill_banner_form(page: Page, title: str, upload_image: bool = True, set_inactive: bool = True):
    page.wait_for_load_state("networkidle")

    title_input = page.get_by_label("Title", exact=False).or_(
        page.get_by_placeholder("Title")
    ).first
    title_input.fill(title)

    if upload_image and os.path.exists(IMAGE_PATH):
        file_input = page.locator("input[type='file']").first
        if file_input.count() > 0:
            file_input.set_input_files(IMAGE_PATH)
            page.wait_for_timeout(1000)

    if set_inactive:
        status_section = page.locator("label:has-text('Status')").locator("..")
        inactive_opt = status_section.get_by_text("Inactive", exact=False).first
        if inactive_opt.count() > 0:
            inactive_opt.click()
        else:
            status_sel = page.locator("select").filter(has_text="Active").first
            if status_sel.count() > 0:
                status_sel.select_option(label="Inactive")

    page.get_by_role("button", name="Save").or_(
        page.get_by_role("button", name="Submit")
    ).or_(
        page.get_by_role("button", name="Simpan")
    ).first.click()
    page.wait_for_load_state("networkidle")


def _find_row(page: Page, text: str):
    return page.locator(f"tr:has-text('{text}')").first


def _cleanup_banner(page: Page, title: str):
    _go_banners(page)
    row = _find_row(page, title)
    if row.count() == 0:
        return
    row.get_by_role("button", name="Delete").or_(
        row.locator("button[aria-label*='delete'], button[aria-label*='Delete']")
    ).first.click()
    confirm = page.get_by_role("button", name="Confirm").or_(
        page.get_by_role("button", name="Ya")
    ).or_(
        page.get_by_role("button", name="Yes")
    ).first
    if confirm.count() > 0:
        confirm.click()
    page.wait_for_load_state("networkidle")


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

@pytest.mark.cms
@pytest.mark.smoke
def test_banners_list(cms_page: Page):
    """TP-BAN-01: Halaman daftar banner tampil"""
    _go_banners(cms_page)
    expect(cms_page).to_have_url(lambda url: "/banners" in url)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.crud
def test_create_banner(cms_page: Page):
    """TP-BAN-02: Buat banner baru berhasil"""
    _go_banners(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_banner_form(cms_page, TITLE)

    try:
        _go_banners(cms_page)
        expect(_find_row(cms_page, TITLE)).to_be_visible()
    finally:
        _cleanup_banner(cms_page, TITLE)


@pytest.mark.cms
@pytest.mark.crud
def test_edit_banner(cms_page: Page):
    """TP-BAN-03: Edit banner berhasil"""
    _go_banners(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_banner_form(cms_page, TITLE)

    try:
        _go_banners(cms_page)
        row = _find_row(cms_page, TITLE)
        row.get_by_role("link", name="Edit").or_(
            row.get_by_role("button", name="Edit")
        ).or_(
            row.locator("a[href*='/edit'], button[aria-label*='edit']")
        ).first.click()
        cms_page.wait_for_load_state("networkidle")

        title_input = cms_page.get_by_label("Title", exact=False).or_(
            cms_page.get_by_placeholder("Title")
        ).first
        title_input.clear()
        title_input.fill(TITLE_EDITED)
        cms_page.get_by_role("button", name="Save").or_(
            cms_page.get_by_role("button", name="Submit")
        ).first.click()
        cms_page.wait_for_load_state("networkidle")

        _go_banners(cms_page)
        expect(_find_row(cms_page, TITLE_EDITED)).to_be_visible()
    finally:
        _cleanup_banner(cms_page, TITLE_EDITED)
        _cleanup_banner(cms_page, TITLE)


@pytest.mark.cms
@pytest.mark.crud
def test_delete_banner(cms_page: Page):
    """TP-BAN-04: Hapus banner berhasil"""
    _go_banners(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_banner_form(cms_page, TITLE)

    _go_banners(cms_page)
    expect(_find_row(cms_page, TITLE)).to_be_visible()

    _cleanup_banner(cms_page, TITLE)

    _go_banners(cms_page)
    expect(_find_row(cms_page, TITLE)).not_to_be_visible()


@pytest.mark.cms
def test_create_banner_empty_title(cms_page: Page):
    """TP-BAN-05: Simpan banner tanpa judul gagal"""
    _go_banners(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).first.click()
    cms_page.wait_for_load_state("networkidle")

    # Pastikan judul kosong, langsung simpan
    title_input = cms_page.get_by_label("Title", exact=False).or_(
        cms_page.get_by_placeholder("Title")
    ).first
    title_input.clear()
    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).first.click()

    expect(
        cms_page.locator("[class*=error], [class*=invalid], [role='alert']").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.cross_check
def test_banner_inactive_not_on_web(cms_page: Page, web_page: Page):
    """TP-BAN-07: Banner Inactive tidak tampil di web"""
    _go_banners(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).first.click()
    _fill_banner_form(cms_page, TITLE, set_inactive=True)

    try:
        web_page.goto(WEB_BASE_URL)
        web_page.wait_for_load_state("networkidle")
        # Banner section di homepage
        banner_text = web_page.get_by_text(TITLE, exact=False)
        expect(banner_text).not_to_be_visible()
    finally:
        _cleanup_banner(cms_page, TITLE)
