"""
Hapus semua data [AUTO] sisa test di SGS CMS.
Jalankan manual bila run pytest terhenti paksa:

    python -m utils.cms_cleanup
"""

from __future__ import annotations
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from playwright.sync_api import sync_playwright
from data.config import CMS_BASE_URL
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.cms_data import AUTO_PREFIX


def _login(page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
    print(f"[cleanup] Logged in as {CMS_EMAIL}")


def cleanup_auto_data(page):
    """
    Iterasi semua halaman daftar yang diketahui dan hapus item berawalan [AUTO].
    Sesuaikan list `modules` dengan modul CMS SGS yang ada.
    """
    modules = [
        # (url_path, row_selector, delete_button_selector)
        # Contoh — sesuaikan dengan CMS SGS setelah eksplorasi manual:
        # ("/articles", "table tbody tr", "button[aria-label='Delete']"),
    ]

    deleted = 0
    for path, row_sel, del_sel in modules:
        try:
            page.goto(f"{CMS_BASE_URL}{path}")
            page.wait_for_load_state("networkidle", timeout=10000)
            rows = page.locator(row_sel).all()
            for row in rows:
                text = row.inner_text()
                if AUTO_PREFIX in text:
                    row.locator(del_sel).click()
                    # Konfirmasi jika ada dialog
                    try:
                        page.get_by_role("button", name="Confirm").click(timeout=3000)
                    except Exception:
                        pass
                    page.wait_for_load_state("networkidle", timeout=5000)
                    deleted += 1
                    print(f"[cleanup] Deleted: {text[:80]}")
        except Exception as e:
            print(f"[cleanup] Warning on {path}: {e}", file=sys.stderr)

    print(f"[cleanup] Done — {deleted} item(s) deleted.")
    return deleted


def main():
    if not CMS_PASSWORD:
        print(
            "ERROR: SGS_CMS_PASSWORD env variable not set.\n"
            "Set it via .env or $env:SGS_CMS_PASSWORD.",
            file=sys.stderr,
        )
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            _login(page)
            cleanup_auto_data(page)
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    main()
