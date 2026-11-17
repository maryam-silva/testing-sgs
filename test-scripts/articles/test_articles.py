"""
Test suite: Articles CMS SGS
Mencakup list, CRUD, validasi, dan cross-check ke web.
Semua data test berawalan [AUTO] dan dihapus di teardown.
"""

import pytest
from playwright.sync_api import Page, expect

from data.cms_data import auto, SAMPLE_ARTICLE
from data.config import CMS_BASE_URL, WEB_BASE_URL

ARTICLES_URL = f"{CMS_BASE_URL}/articles"
ARTICLES_ADD_URL = f"{CMS_BASE_URL}/articles/add"

TITLE = auto("Test Article SGS")
TITLE_EDITED = auto("Test Article SGS EDITED")
CONTENT = "Ini konten artikel otomatis dari automation test SGS. Jangan hapus manual."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_articles(page: Page):
    page.goto(ARTICLES_URL)
    page.wait_for_load_state("networkidle")


def _fill_article_form(page: Page, title: str, content: str = CONTENT, set_inactive: bool = True):
    """Isi form artikel dan simpan."""
    page.wait_for_load_state("networkidle")

    # Judul
    title_input = page.get_by_label("Title", exact=False).first
    title_input.fill(title)

    # Konten (rich text editor atau textarea)
    content_area = page.locator(
        "textarea, [contenteditable='true'], .ql-editor, .tox-edit-area__iframe"
    ).first
    if content_area.count() > 0:
        content_area.click()
        content_area.fill(content)

    # Pilih kategori pertama yang tersedia (jika ada dropdown)
    cat_select = page.locator("select, [class*=select]").filter(has_text="Kategori").first
    if cat_select.count() > 0:
        options = cat_select.locator("option").all()
        non_empty = [o for o in options if o.get_attribute("value")]
        if non_empty:
            non_empty[0].click()

    # Set status inactive supaya tidak tampil di web
    if set_inactive:
        status_toggle = page.locator(
            "select[name*=status], input[type='checkbox'][name*=status]"
        ).first
        if status_toggle.count() > 0:
            # dropdown
            if status_toggle.evaluate("el => el.tagName") == "SELECT":
                status_toggle.select_option(label="Inactive")
        else:
            # cari label "Status" lalu switch/radio
            status_section = page.locator("label:has-text('Status')").locator("..")
            inactive_opt = status_section.get_by_text("Inactive", exact=False).first
            if inactive_opt.count() > 0:
                inactive_opt.click()

    # Submit
    page.get_by_role("button", name="Save").or_(
        page.get_by_role("button", name="Submit")
    ).or_(
        page.get_by_role("button", name="Simpan")
    ).first.click()
    page.wait_for_load_state("networkidle")


def _find_row(page: Page, text: str):
    """Cari baris tabel yang mengandung text."""
    return page.locator(f"tr:has-text('{text}')").first


def _cleanup_article(page: Page, title: str):
    """Hapus artikel berdasarkan judul — dipanggil di teardown."""
    _go_articles(page)
    row = _find_row(page, title)
    if row.count() == 0:
        return
    # Klik tombol delete / hapus di baris tersebut
    row.get_by_role("button", name="Delete").or_(
        row.get_by_role("button", name="Hapus")
    ).or_(
        row.locator("button[aria-label*='delete'], button[aria-label*='Delete']")
    ).first.click()
    # Konfirmasi dialog
    confirm_btn = page.get_by_role("button", name="Confirm").or_(
        page.get_by_role("button", name="Ya")
    ).or_(
        page.get_by_role("button", name="Yes")
    ).first
    if confirm_btn.count() > 0:
        confirm_btn.click()
    page.wait_for_load_state("networkidle")


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

@pytest.mark.cms
@pytest.mark.smoke
def test_articles_list(cms_page: Page):
    """TP-ART-01: Halaman daftar artikel tampil"""
    _go_articles(cms_page)
    expect(cms_page).to_have_url(lambda url: "/articles" in url)
    # Pastikan ada tabel atau daftar konten (bukan halaman error)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.crud
def test_create_article(cms_page: Page):
    """TP-ART-02: Buat artikel baru berhasil"""
    _go_articles(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_article_form(cms_page, TITLE)

    try:
        _go_articles(cms_page)
        expect(_find_row(cms_page, TITLE)).to_be_visible()
    finally:
        _cleanup_article(cms_page, TITLE)


@pytest.mark.cms
@pytest.mark.crud
def test_edit_article(cms_page: Page):
    """TP-ART-03: Edit artikel berhasil"""
    # Buat dulu
    _go_articles(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_article_form(cms_page, TITLE)

    try:
        _go_articles(cms_page)
        row = _find_row(cms_page, TITLE)
        row.get_by_role("link", name="Edit").or_(
            row.get_by_role("button", name="Edit")
        ).or_(
            row.locator("a[href*='/edit'], button[aria-label*='edit']")
        ).first.click()
        cms_page.wait_for_load_state("networkidle")

        # Ubah judul
        title_input = cms_page.get_by_label("Title", exact=False).first
        title_input.clear()
        title_input.fill(TITLE_EDITED)
        cms_page.get_by_role("button", name="Save").or_(
            cms_page.get_by_role("button", name="Submit")
        ).or_(
            cms_page.get_by_role("button", name="Simpan")
        ).first.click()
        cms_page.wait_for_load_state("networkidle")

        _go_articles(cms_page)
        expect(_find_row(cms_page, TITLE_EDITED)).to_be_visible()
    finally:
        _cleanup_article(cms_page, TITLE_EDITED)
        _cleanup_article(cms_page, TITLE)


@pytest.mark.cms
@pytest.mark.crud
def test_delete_article(cms_page: Page):
    """TP-ART-04: Hapus artikel berhasil"""
    # Buat dulu
    _go_articles(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_article_form(cms_page, TITLE)

    _go_articles(cms_page)
    expect(_find_row(cms_page, TITLE)).to_be_visible()

    _cleanup_article(cms_page, TITLE)

    _go_articles(cms_page)
    expect(_find_row(cms_page, TITLE)).not_to_be_visible()


@pytest.mark.cms
def test_create_article_empty_title(cms_page: Page):
    """TP-ART-05: Simpan artikel tanpa judul gagal"""
    _go_articles(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    cms_page.wait_for_load_state("networkidle")

    # Pastikan judul kosong, langsung simpan
    title_input = cms_page.get_by_label("Title", exact=False).first
    title_input.clear()
    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).first.click()

    # Harus tetap di form atau muncul pesan error
    expect(
        cms_page.locator("[class*=error], [class*=invalid], [role='alert']").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.cross_check
def test_article_inactive_not_on_web(cms_page: Page, web_page: Page):
    """TP-ART-08: Artikel Inactive tidak tampil di web"""
    # Buat artikel status Inactive
    _go_articles(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_article_form(cms_page, TITLE, set_inactive=True)

    try:
        # Verifikasi di web
        web_page.goto(f"{WEB_BASE_URL}/articles")
        web_page.wait_for_load_state("networkidle")
        article_on_web = web_page.get_by_text(TITLE, exact=False)
        expect(article_on_web).not_to_be_visible()
    finally:
        _cleanup_article(cms_page, TITLE)
