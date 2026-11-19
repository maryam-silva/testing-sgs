"""
Test suite: Articles CMS SGS
Mencakup list, CRUD, validasi, dan cross-check ke web.
Semua data test berawalan [AUTO] dan dihapus di teardown.
"""

import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from data.cms_data import auto, SAMPLE_ARTICLE
from data.config import CMS_BASE_URL, WEB_BASE_URL
from utils.playwright_helpers import cms_goto

TEST_IMAGE = str(Path(__file__).parent.parent.parent / "data" / "assets" / "test-image.jpg")

ARTICLES_URL = f"{CMS_BASE_URL}/article"
ARTICLES_ADD_URL = f"{CMS_BASE_URL}/article/create"
_RE_ARTICLE = re.compile(r"/article")

TITLE = auto("Test Article SGS")
TITLE_EDITED = auto("Test Article SGS EDITED")
CONTENT = "Ini konten artikel otomatis dari automation test SGS. Jangan hapus manual."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_articles(page: Page):
    cms_goto(page, ARTICLES_URL)


def _click_add(page: Page):
    """Klik tombol tambah artikel — coba berbagai label yang umum di CMS."""
    page.locator(
        "a[href*='create'], a[href*='add'], "
        "button:has-text('Create'), button:has-text('Add'), "
        "button:has-text('Tambah'), button:has-text('Buat'), "
        "a:has-text('Create'), a:has-text('Add'), a:has-text('Tambah')"
    ).first.click()
    page.wait_for_load_state("networkidle")


def _fill_article_form(page: Page, title: str, content: str = CONTENT, set_inactive: bool = True):
    """Isi form artikel dan simpan."""
    page.wait_for_load_state("networkidle")

    # Gambar (wajib — form menolak submit tanpa image)
    image_input = page.locator("input[type='file']").first
    if image_input.count() > 0:
        image_input.set_input_files(TEST_IMAGE)

    # Judul + konten bahasa Indonesia (default)
    title_input = page.get_by_label("Title", exact=False).first
    title_input.fill(title)

    content_area = page.locator(
        "textarea, [contenteditable='true'], .ql-editor, .tox-edit-area__iframe"
    ).first
    if content_area.count() > 0:
        content_area.click()
        content_area.fill(content)

    # Pilih kategori pertama yang tersedia (Ant Design select combobox)
    cat_input = page.get_by_label("Category", exact=False).first
    if cat_input.count() > 0:
        cat_input.click()
        option = page.locator(".ant-select-dropdown .ant-select-item-option").first
        if option.count() > 0:
            option.click()
            page.wait_for_timeout(300)

    # Form wajib konten di semua bahasa (ID + EN) -- switch language lalu isi EN juga
    lang_item = page.locator(".ant-select-selection-item[title='Indonesia (ID)']").first
    if lang_item.count() > 0:
        lang_item.click()
        en_option = page.locator(".ant-select-dropdown .ant-select-item-option", has_text="English").first
        if en_option.count() > 0:
            en_option.click()
            page.wait_for_timeout(300)
            title_input_en = page.get_by_label("Title", exact=False).first
            title_input_en.fill(title)
            content_area_en = page.locator(
                "textarea, [contenteditable='true'], .ql-editor, .tox-edit-area__iframe"
            ).first
            if content_area_en.count() > 0:
                content_area_en.click()
                content_area_en.fill(content)
            page.wait_for_timeout(300)

    # Status adalah radio button (Active/Inactive) -- set inactive supaya tidak tampil di web
    if set_inactive:
        inactive_radio = page.locator("input[type='radio'][value='inactive']").first
        if inactive_radio.count() > 0:
            inactive_radio.check(force=True)

    # Submit
    page.get_by_role("button", name="Save").or_(
        page.get_by_role("button", name="Submit")
    ).or_(
        page.get_by_role("button", name="Simpan")
    ).first.click()
    page.wait_for_load_state("networkidle")


def _find_row(page: Page, text: str):
    """Cari baris tabel yang mengandung text (filter, bukan interpolasi CSS,
    supaya aman dari title berisi tanda kutip/karakter khusus)."""
    return page.locator("tr").filter(has_text=text).first


def _wait_for_row(page: Page, title: str, attempts: int = 4, delay_ms: int = 1500):
    """Cari row baru dengan retry+reload -- backend punya sedikit delay indexing
    setelah create, sehingga row tidak selalu langsung muncul di list pertama kali."""
    for i in range(attempts):
        row = _find_row(page, title)
        if row.count() > 0:
            return row
        page.wait_for_timeout(delay_ms)
        page.reload()
        page.wait_for_load_state("networkidle")
    return _find_row(page, title)


def _row_action(page: Page, row, name: str):
    """Klik aksi (Detail/Edit/Archive) dari menu 'more' (⋮) pada baris tabel.
    UI tidak punya hard-delete -- hanya Archive (soft-delete)."""
    row.locator(".anticon-more, [aria-label='more']").first.click()
    page.get_by_role("menuitem", name=name).click()


def _cleanup_article(page: Page, title: str):
    """Archive artikel berdasarkan judul (soft-delete) — dipanggil di teardown."""
    _go_articles(page)
    row = _find_row(page, title)
    if row.count() == 0:
        return
    _row_action(page, row, "Archive")
    confirm_btn = page.get_by_role("button", name="Confirm").or_(
        page.get_by_role("button", name="Ya")
    ).or_(
        page.get_by_role("button", name="Yes")
    ).or_(
        page.get_by_role("button", name="OK")
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
    expect(cms_page).to_have_url(_RE_ARTICLE)
    # Pastikan ada tabel atau daftar konten (bukan halaman error)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.crud
def test_create_article(cms_page: Page):
    """TP-ART-02: Buat artikel baru berhasil"""
    _go_articles(cms_page)
    _click_add(cms_page)
    _fill_article_form(cms_page, TITLE)

    try:
        _go_articles(cms_page)
        expect(_wait_for_row(cms_page, TITLE)).to_be_visible()
    finally:
        _cleanup_article(cms_page, TITLE)


@pytest.mark.cms
@pytest.mark.crud
def test_edit_article(cms_page: Page):
    """TP-ART-03: Edit artikel berhasil"""
    # Buat dulu
    _go_articles(cms_page)
    _click_add(cms_page)
    _fill_article_form(cms_page, TITLE)

    try:
        _go_articles(cms_page)
        row = _find_row(cms_page, TITLE)
        _row_action(cms_page, row, "Edit")
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
def test_archive_article(cms_page: Page):
    """TP-ART-04: Archive artikel berhasil (tidak ada hard-delete di UI)"""
    # Buat dulu
    _go_articles(cms_page)
    _click_add(cms_page)
    _fill_article_form(cms_page, TITLE)

    _go_articles(cms_page)
    expect(_wait_for_row(cms_page, TITLE)).to_be_visible()

    _cleanup_article(cms_page, TITLE)

    _go_articles(cms_page)
    expect(_find_row(cms_page, TITLE)).not_to_be_visible()


@pytest.mark.cms
def test_create_article_empty_title(cms_page: Page):
    """TP-ART-05: Simpan artikel tanpa judul gagal"""
    _go_articles(cms_page)
    _click_add(cms_page)
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
def test_create_article_no_category(cms_page: Page):
    """TP-ART-06: Simpan artikel tanpa kategori gagal"""
    _go_articles(cms_page)
    _click_add(cms_page)
    cms_page.wait_for_load_state("networkidle")

    # Isi judul dan konten, tapi pastikan kategori kosong/default
    title_input = cms_page.get_by_label("Title", exact=False).first
    title_input.fill(auto("No Category Article"))

    content_area = cms_page.locator(
        "textarea, [contenteditable='true'], .ql-editor"
    ).first
    if content_area.count() > 0:
        content_area.click()
        content_area.fill(CONTENT)

    # Reset kategori ke pilihan kosong/default jika ada
    cat_select = cms_page.locator("select").filter(has_text="Kategori").or_(
        cms_page.locator("select").filter(has_text="Category")
    ).first
    if cat_select.count() > 0:
        cat_select.select_option(index=0)

    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).first.click()

    # Harus muncul pesan validasi atau tetap di form
    expect(
        cms_page.locator("[class*=error], [class*=invalid], [role='alert']").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.cross_check
def test_article_active_on_web(cms_page: Page, web_page: Page):
    """TP-ART-07: Artikel status Active tampil di web"""
    _go_articles(cms_page)
    _click_add(cms_page)
    # Buat artikel dengan status Active (set_inactive=False)
    _fill_article_form(cms_page, TITLE, set_inactive=False)

    try:
        web_page.goto(f"{WEB_BASE_URL}/news")
        web_page.wait_for_load_state("networkidle")
        article_on_web = web_page.get_by_text(TITLE, exact=False)
        for _ in range(3):
            if article_on_web.count() > 0:
                break
            web_page.wait_for_timeout(1500)
            web_page.reload()
            web_page.wait_for_load_state("networkidle")
            article_on_web = web_page.get_by_text(TITLE, exact=False)
        expect(article_on_web).to_be_visible()
    finally:
        _cleanup_article(cms_page, TITLE)


@pytest.mark.cms
@pytest.mark.cross_check
def test_article_inactive_not_on_web(cms_page: Page, web_page: Page):
    """TP-ART-08: Artikel Inactive tidak tampil di web"""
    # Buat artikel status Inactive
    _go_articles(cms_page)
    _click_add(cms_page)
    _fill_article_form(cms_page, TITLE, set_inactive=True)

    try:
        # Verifikasi di web
        web_page.goto(f"{WEB_BASE_URL}/news")
        web_page.wait_for_load_state("networkidle")
        article_on_web = web_page.get_by_text(TITLE, exact=False)
        expect(article_on_web).not_to_be_visible()
    finally:
        _cleanup_article(cms_page, TITLE)


@pytest.mark.cms
def test_create_article_special_chars_title(cms_page: Page):
    """Edge: Judul artikel dengan karakter khusus tersimpan aman (tidak XSS)"""
    special_title = auto("Article <script>alert(1)</script> & 'test'")
    _go_articles(cms_page)
    _click_add(cms_page)
    _fill_article_form(cms_page, special_title, set_inactive=True)

    try:
        _go_articles(cms_page)
        # Halaman harus tetap normal (tidak ada alert/script executed)
        expect(cms_page).to_have_url(_RE_ARTICLE)
        # Script tag tidak boleh ter-execute — cek tidak ada dialog aktif
        expect(cms_page.locator("dialog[open]")).to_have_count(0)
    finally:
        _cleanup_article(cms_page, special_title)


@pytest.mark.cms
def test_create_article_very_long_title(cms_page: Page):
    """Edge: Judul artikel sangat panjang ditolak atau dipotong"""
    long_title = auto("A" * 300)
    _go_articles(cms_page)
    _click_add(cms_page)

    title_input = cms_page.get_by_label("Title", exact=False).first
    title_input.fill(long_title)
    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).first.click()

    # Ekspektasi: validasi error ATAU tersimpan dengan judul terpotong
    # Pastikan tidak crash (halaman masih valid)
    expect(cms_page).to_have_url(re.compile(r"sgs-cms-dev"))
    # Cleanup jika tersimpan
    _cleanup_article(cms_page, auto("A" * 100))
