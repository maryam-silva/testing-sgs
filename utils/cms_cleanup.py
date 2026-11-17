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

from playwright.sync_api import sync_playwright, Page
from data.config import CMS_BASE_URL
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.cms_data import AUTO_PREFIX


def _login(page: Page):
    page.goto(CMS_BASE_URL)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url(lambda url: "/login" not in url, timeout=15000)
    print(f"[cleanup] Logged in as {CMS_EMAIL}")


def _delete_auto_items(page: Page, path: str, label: str) -> int:
    """Hapus semua baris yang mengandung AUTO_PREFIX di halaman list CMS."""
    deleted = 0
    try:
        page.goto(f"{CMS_BASE_URL}{path}")
        page.wait_for_load_state("networkidle", timeout=10000)

        while True:
            # Cari baris yang mengandung [AUTO]
            rows = page.locator(f"tr:has-text('{AUTO_PREFIX}')").all()
            if not rows:
                break

            row = rows[0]
            text = row.inner_text().replace("\n", " ")[:80]

            # Klik tombol delete di baris tersebut
            del_btn = row.get_by_role("button", name="Delete").or_(
                row.locator("button[aria-label*='delete'], button[aria-label*='Delete']")
            ).first
            if del_btn.count() == 0:
                # Coba cari via icon atau class
                del_btn = row.locator("[class*=delete], [class*=trash]").first

            if del_btn.count() == 0:
                print(f"[cleanup] Warning: tombol delete tidak ditemukan untuk: {text}", file=sys.stderr)
                break

            del_btn.click()

            # Konfirmasi dialog
            confirm = page.get_by_role("button", name="Confirm").or_(
                page.get_by_role("button", name="Ya")
            ).or_(
                page.get_by_role("button", name="Yes")
            ).first
            try:
                confirm.wait_for(timeout=3000)
                confirm.click()
            except Exception:
                pass

            page.wait_for_load_state("networkidle", timeout=5000)
            deleted += 1
            print(f"[cleanup] Deleted [{label}]: {text}")

    except Exception as e:
        print(f"[cleanup] Warning on {path}: {e}", file=sys.stderr)

    return deleted


def cleanup_auto_data(page: Page) -> int:
    """Hapus semua data [AUTO] dari semua modul CMS SGS."""
    modules = [
        ("/articles", "Article"),
        ("/banners", "Banner"),
        ("/faqs", "FAQ"),
        ("/galleries", "Gallery"),
    ]

    total = 0
    for path, label in modules:
        n = _delete_auto_items(page, path, label)
        total += n

    print(f"[cleanup] Done — {total} item(s) deleted.")
    return total


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
