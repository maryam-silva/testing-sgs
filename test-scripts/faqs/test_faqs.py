"""
Test suite: FAQs CMS SGS
Mencakup list, CRUD, validasi, dan cross-check ke web.
Semua data test berawalan [AUTO] dan dihapus di teardown.
"""

import pytest
from playwright.sync_api import Page, expect

from data.cms_data import auto
from data.config import CMS_BASE_URL, WEB_BASE_URL

FAQS_URL = f"{CMS_BASE_URL}/faqs"

QUESTION = auto("Pertanyaan Test SGS")
QUESTION_EDITED = auto("Pertanyaan Test SGS EDITED")
ANSWER = "Ini adalah jawaban test otomatis dari automation script SGS."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go_faqs(page: Page):
    page.goto(FAQS_URL)
    page.wait_for_load_state("networkidle")


def _fill_faq_form(page: Page, question: str, answer: str = ANSWER, set_inactive: bool = True):
    page.wait_for_load_state("networkidle")

    # Pertanyaan
    q_input = page.get_by_label("Question", exact=False).or_(
        page.get_by_label("Pertanyaan", exact=False)
    ).or_(
        page.get_by_placeholder("Question")
    ).first
    q_input.fill(question)

    # Jawaban (textarea atau rich text)
    a_input = page.get_by_label("Answer", exact=False).or_(
        page.get_by_label("Jawaban", exact=False)
    ).first
    if a_input.count() > 0:
        a_input.fill(answer)
    else:
        content_area = page.locator(
            "textarea, [contenteditable='true'], .ql-editor"
        ).first
        if content_area.count() > 0:
            content_area.click()
            content_area.fill(answer)

    # Pilih group pertama yang tersedia
    group_sel = page.locator("select").filter(has_text="Group").first
    if group_sel.count() > 0:
        options = group_sel.locator("option").all()
        non_empty = [o for o in options if o.get_attribute("value")]
        if non_empty:
            group_sel.select_option(value=non_empty[0].get_attribute("value"))

    # Status inactive
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


def _cleanup_faq(page: Page, question: str):
    _go_faqs(page)
    row = _find_row(page, question)
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
def test_faqs_list(cms_page: Page):
    """TP-FAQ-01: Halaman daftar FAQ tampil"""
    _go_faqs(cms_page)
    expect(cms_page).to_have_url(lambda url: "/faqs" in url)
    expect(
        cms_page.locator("table, [class*=table], [class*=list], [class*=grid]").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.crud
def test_create_faq(cms_page: Page):
    """TP-FAQ-02: Buat FAQ baru berhasil"""
    _go_faqs(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).or_(
        cms_page.get_by_role("link", name="Tambah")
    ).first.click()
    _fill_faq_form(cms_page, QUESTION)

    try:
        _go_faqs(cms_page)
        expect(_find_row(cms_page, QUESTION)).to_be_visible()
    finally:
        _cleanup_faq(cms_page, QUESTION)


@pytest.mark.cms
@pytest.mark.crud
def test_edit_faq(cms_page: Page):
    """TP-FAQ-03: Edit FAQ berhasil"""
    _go_faqs(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).first.click()
    _fill_faq_form(cms_page, QUESTION)

    try:
        _go_faqs(cms_page)
        row = _find_row(cms_page, QUESTION)
        row.get_by_role("link", name="Edit").or_(
            row.get_by_role("button", name="Edit")
        ).or_(
            row.locator("a[href*='/edit'], button[aria-label*='edit']")
        ).first.click()
        cms_page.wait_for_load_state("networkidle")

        q_input = cms_page.get_by_label("Question", exact=False).or_(
            cms_page.get_by_label("Pertanyaan", exact=False)
        ).first
        q_input.clear()
        q_input.fill(QUESTION_EDITED)
        cms_page.get_by_role("button", name="Save").or_(
            cms_page.get_by_role("button", name="Submit")
        ).first.click()
        cms_page.wait_for_load_state("networkidle")

        _go_faqs(cms_page)
        expect(_find_row(cms_page, QUESTION_EDITED)).to_be_visible()
    finally:
        _cleanup_faq(cms_page, QUESTION_EDITED)
        _cleanup_faq(cms_page, QUESTION)


@pytest.mark.cms
@pytest.mark.crud
def test_delete_faq(cms_page: Page):
    """TP-FAQ-04: Hapus FAQ berhasil"""
    _go_faqs(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).first.click()
    _fill_faq_form(cms_page, QUESTION)

    _go_faqs(cms_page)
    expect(_find_row(cms_page, QUESTION)).to_be_visible()

    _cleanup_faq(cms_page, QUESTION)

    _go_faqs(cms_page)
    expect(_find_row(cms_page, QUESTION)).not_to_be_visible()


@pytest.mark.cms
def test_create_faq_empty_question(cms_page: Page):
    """TP-FAQ-05: Simpan FAQ tanpa pertanyaan gagal"""
    _go_faqs(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).first.click()
    cms_page.wait_for_load_state("networkidle")

    # Kosongkan pertanyaan, isi jawaban, langsung simpan
    q_input = cms_page.get_by_label("Question", exact=False).or_(
        cms_page.get_by_label("Pertanyaan", exact=False)
    ).first
    q_input.clear()
    a_input = cms_page.get_by_label("Answer", exact=False).first
    if a_input.count() > 0:
        a_input.fill(ANSWER)
    cms_page.get_by_role("button", name="Save").or_(
        cms_page.get_by_role("button", name="Submit")
    ).first.click()

    expect(
        cms_page.locator("[class*=error], [class*=invalid], [role='alert']").first
    ).to_be_visible()


@pytest.mark.cms
@pytest.mark.cross_check
def test_faq_inactive_not_on_web(cms_page: Page, web_page: Page):
    """TP-FAQ-08: FAQ Inactive tidak tampil di web"""
    _go_faqs(cms_page)
    cms_page.get_by_role("link", name="Add").or_(
        cms_page.get_by_role("button", name="Add")
    ).first.click()
    _fill_faq_form(cms_page, QUESTION, set_inactive=True)

    try:
        # Cek di halaman FAQ web (atau homepage yang ada FAQ section)
        web_page.goto(f"{WEB_BASE_URL}/faq")
        web_page.wait_for_load_state("networkidle")
        faq_on_web = web_page.get_by_text(QUESTION, exact=False)
        expect(faq_on_web).not_to_be_visible()
    finally:
        _cleanup_faq(cms_page, QUESTION)
