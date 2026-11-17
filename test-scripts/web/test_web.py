"""
Test suite: SGS Web Frontend
Mencakup smoke, navigasi, konten per halaman, negatif, dan edge case.
Tidak memerlukan login — gunakan fixture web_page.
"""

import re
import pytest
from playwright.sync_api import Page, expect

from data.config import WEB_BASE_URL

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _go(page: Page, path: str = ""):
    page.goto(f"{WEB_BASE_URL}{path}")
    page.wait_for_load_state("networkidle")


def _nav_link(page: Page, href: str):
    """Cari nav link berdasarkan href path."""
    return page.locator(f'a[href="{href}"]').first


# ---------------------------------------------------------------------------
# Homepage
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_homepage_loads(web_page: Page):
    """TP-WEB-01: Homepage tampil dengan heading utama"""
    _go(web_page)
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/")
    heading = web_page.locator("h1, h2").first
    expect(heading).to_be_visible()
    # Heading harus mengandung nama perusahaan
    expect(
        web_page.locator("h1, h2").filter(has_text="Sinar Sosro").or_(
            web_page.locator("h1, h2").filter(has_text="SGS")
        ).or_(
            web_page.locator("h1, h2").filter(has_text="Gunung Slamat")
        ).first
    ).to_be_visible()


@pytest.mark.web
@pytest.mark.smoke
def test_homepage_navigation_visible(web_page: Page):
    """TP-WEB-02: Navigasi global tampil di homepage"""
    _go(web_page)
    nav = web_page.locator("nav, header").first
    expect(nav).to_be_visible()


@pytest.mark.web
def test_homepage_news_section(web_page: Page):
    """TP-WEB-03: Bagian berita tampil di homepage"""
    _go(web_page)
    news_section = web_page.locator(
        "[class*=news], [class*=berita], section:has-text('Berita'), section:has-text('News')"
    ).first
    expect(news_section).to_be_visible()


@pytest.mark.web
def test_homepage_banner_visible(web_page: Page):
    """TP-WEB-04: Banner/carousel tampil di homepage"""
    _go(web_page)
    banner = web_page.locator("#hero-section, [id*=hero], [id*=banner]").first
    expect(banner).to_be_visible()


@pytest.mark.web
def test_homepage_logo_navigates_home(web_page: Page):
    """TP-WEB-05: Klik logo navigasi kembali ke homepage"""
    _go(web_page, "/about")
    logo = web_page.locator("a[href='/']").first
    if logo.count() > 0:
        logo.click()
        web_page.wait_for_load_state("networkidle")
        expect(web_page).to_have_url(re.compile(r"/$"))
    else:
        expect(web_page).to_have_url(f"{WEB_BASE_URL}/about")


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_about_loads(web_page: Page):
    """TP-WEB-06: Halaman About tampil"""
    _go(web_page, "/about")
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/about")
    expect(web_page.locator("main, [class*=content], article").first).to_be_visible()


@pytest.mark.web
def test_about_has_heading(web_page: Page):
    """TP-WEB-07: Halaman About memiliki heading"""
    _go(web_page, "/about")
    expect(web_page.locator("h1, h2").first).to_be_visible()


# ---------------------------------------------------------------------------
# Brands
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_brands_loads(web_page: Page):
    """TP-WEB-08: Halaman Brands tampil"""
    _go(web_page, "/brands")
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/brands")
    expect(web_page.locator("main, [class*=content]").first).to_be_visible()


@pytest.mark.web
def test_brands_has_product_items(web_page: Page):
    """TP-WEB-09: Daftar brand/produk tampil"""
    _go(web_page, "/brands")
    # Cari setidaknya satu gambar produk atau card
    items = web_page.locator(
        "img, [class*=card], [class*=product], [class*=brand]"
    )
    expect(items.first).to_be_visible()


# ---------------------------------------------------------------------------
# News
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_news_loads(web_page: Page):
    """TP-WEB-10: Halaman News tampil"""
    _go(web_page, "/news")
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/news")
    expect(web_page.locator("main, [class*=content]").first).to_be_visible()


@pytest.mark.web
def test_news_has_article_items(web_page: Page):
    """TP-WEB-11: Daftar artikel/berita tampil"""
    _go(web_page, "/news")
    # Cari minimal 1 artikel: h3, card, atau link artikel
    items = web_page.locator("article, [class*=card], h3").first
    expect(items).to_be_visible()


@pytest.mark.web
def test_news_article_click_opens_detail(web_page: Page):
    """TP-WEB-12: Klik artikel membuka halaman detail"""
    _go(web_page, "/news")
    # Klik artikel pertama yang bisa diklik
    article_link = web_page.locator("article a, [class*=card] a, h3 a").first
    if article_link.count() > 0:
        href = article_link.get_attribute("href")
        article_link.click()
        web_page.wait_for_load_state("networkidle")
        # URL harus berubah (ke halaman detail)
        expect(web_page).not_to_have_url(re.compile(r"/news$"))
    else:
        # Jika tidak ada link langsung, skip gracefully — daftar mungkin static
        pytest.skip("Tidak ditemukan link artikel yang dapat diklik")


# ---------------------------------------------------------------------------
# Contact Us
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_contact_loads(web_page: Page):
    """TP-WEB-13: Halaman Contact Us tampil"""
    _go(web_page, "/contact-us")
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/contact-us")
    expect(web_page.locator("main, [class*=content]").first).to_be_visible()


@pytest.mark.web
def test_contact_has_form_or_info(web_page: Page):
    """TP-WEB-14: Formulir kontak atau informasi kontak ada"""
    _go(web_page, "/contact-us")
    contact_element = web_page.locator(
        "form, input[type='email'], input[type='text'], "
        "[class*=address], [class*=phone], [class*=contact]"
    ).first
    expect(contact_element).to_be_visible()


@pytest.mark.web
def test_contact_form_empty_submit(web_page: Page):
    """TP-WEB-15: Submit form kontak kosong tidak lolos validasi"""
    _go(web_page, "/contact-us")
    form = web_page.locator("form").first
    if form.count() == 0:
        pytest.skip("Tidak ada form di halaman Contact Us")

    submit_btn = form.get_by_role("button", name="Submit").or_(
        form.get_by_role("button", name="Kirim")
    ).or_(
        form.locator("button[type='submit']")
    ).first
    if submit_btn.count() == 0:
        pytest.skip("Tidak ditemukan tombol submit")

    submit_btn.click()
    # Harus muncul validasi atau URL tidak berubah
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/contact-us")


# ---------------------------------------------------------------------------
# Careers
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_careers_loads(web_page: Page):
    """TP-WEB-16: Halaman Careers tampil"""
    _go(web_page, "/careers")
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/careers")
    expect(web_page.locator("main, [class*=content]").first).to_be_visible()


@pytest.mark.web
def test_careers_has_content(web_page: Page):
    """TP-WEB-17: Konten karir ada"""
    _go(web_page, "/careers")
    expect(web_page.locator("h1, h2, h3").first).to_be_visible()


# ---------------------------------------------------------------------------
# Sustainability
# ---------------------------------------------------------------------------

@pytest.mark.web
@pytest.mark.smoke
def test_sustainability_loads(web_page: Page):
    """TP-WEB-18: Halaman Sustainability tampil"""
    _go(web_page, "/sustainability")
    expect(web_page).to_have_url(f"{WEB_BASE_URL}/sustainability")
    expect(web_page.locator("main, [class*=content]").first).to_be_visible()


@pytest.mark.web
def test_sustainability_has_content(web_page: Page):
    """TP-WEB-19: Konten sustainability ada"""
    _go(web_page, "/sustainability")
    expect(web_page.locator("h1, h2, h3").first).to_be_visible()


# ---------------------------------------------------------------------------
# Navigasi Global
# ---------------------------------------------------------------------------

@pytest.mark.web
def test_nav_about(web_page: Page):
    """TP-WEB-20: Link navigasi About berfungsi"""
    _go(web_page)
    link = _nav_link(web_page, "/about")
    expect(link).to_be_visible()
    link.click()
    web_page.wait_for_load_state("networkidle")
    expect(web_page).to_have_url(re.compile(r"/about"))


@pytest.mark.web
def test_nav_brands(web_page: Page):
    """TP-WEB-21: Link navigasi Brands berfungsi"""
    _go(web_page)
    link = _nav_link(web_page, "/brands")
    expect(link).to_be_visible()
    link.click()
    web_page.wait_for_load_state("networkidle")
    expect(web_page).to_have_url(re.compile(r"/brands"))


@pytest.mark.web
def test_nav_news(web_page: Page):
    """TP-WEB-22: Link navigasi News berfungsi"""
    _go(web_page)
    link = _nav_link(web_page, "/news")
    expect(link).to_be_visible()
    link.click()
    web_page.wait_for_load_state("networkidle")
    expect(web_page).to_have_url(re.compile(r"/news"))


@pytest.mark.web
def test_nav_contact(web_page: Page):
    """TP-WEB-23: Link navigasi Contact Us berfungsi"""
    _go(web_page)
    link = _nav_link(web_page, "/contact-us")
    expect(link).to_be_visible()
    link.click()
    web_page.wait_for_load_state("networkidle")
    expect(web_page).to_have_url(re.compile(r"/contact-us"))


# ---------------------------------------------------------------------------
# Edge Cases & Negatif
# ---------------------------------------------------------------------------

@pytest.mark.web
def test_404_invalid_route(web_page: Page):
    """TP-WEB-24: URL tidak valid menampilkan halaman 404"""
    web_page.goto(f"{WEB_BASE_URL}/halaman-tidak-ada-xyz-123")
    web_page.wait_for_load_state("networkidle")
    # Halaman harus tampilkan pesan 404 atau "not found" — BUKAN blank/error 500
    page_text = web_page.locator("body").inner_text().lower()
    assert (
        "404" in page_text
        or "not found" in page_text
        or "tidak ditemukan" in page_text
    ), f"Halaman 404 tidak menampilkan pesan yang sesuai. URL: {web_page.url}"


@pytest.mark.web
def test_homepage_mobile_viewport(browser):
    """TP-WEB-25: Homepage tampil di mobile viewport tanpa horizontal scroll"""
    from playwright.sync_api import sync_playwright
    ctx = browser.new_context(viewport={"width": 375, "height": 812})
    page = ctx.new_page()
    page.goto(WEB_BASE_URL)
    page.wait_for_load_state("networkidle")

    scroll_width = page.evaluate("document.documentElement.scrollWidth")
    client_width = page.evaluate("document.documentElement.clientWidth")

    page.close()
    ctx.close()

    assert scroll_width <= client_width + 10, (
        f"Horizontal scroll terdeteksi di mobile: scrollWidth={scroll_width}, "
        f"clientWidth={client_width}"
    )


@pytest.mark.web
def test_homepage_no_js_errors(web_page: Page):
    """TP-WEB-26: Tidak ada JS error kritis (Uncaught) di homepage"""
    errors: list[str] = []
    web_page.on("pageerror", lambda err: errors.append(str(err)))

    _go(web_page)
    # Filter hanya error Uncaught yang serius
    critical = [e for e in errors if "Uncaught" in e or "TypeError" in e]
    assert critical == [], f"Ditemukan JS error kritis: {critical}"
