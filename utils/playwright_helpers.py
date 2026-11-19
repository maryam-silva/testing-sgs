import re
from playwright.sync_api import Page, expect, TimeoutError as PwTimeoutError
from data.account_development import CMS_EMAIL, CMS_PASSWORD
from data.config import CMS_BASE_URL

_RE_LOGIN = re.compile(r"/login")


def safe_idle(page: Page, timeout: int = 8000) -> None:
    """wait_for_load_state('networkidle') dengan timeout dibatasi dan tidak fatal.

    App ini polling terus-menerus (misal fetch notifikasi), jadi network tidak
    pernah benar-benar idle -- networkidle bisa timeout 30s meski halaman sudah
    sepenuhnya siap. Lebih aman tunggu sebentar lalu lanjut; locator berikutnya
    tetap auto-wait untuk elemen yang actionable."""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except PwTimeoutError:
        pass


def login_cms(page: Page) -> None:
    page.goto(CMS_BASE_URL)
    safe_idle(page)
    page.get_by_label("Email").fill(CMS_EMAIL)
    page.get_by_label("Password").fill(CMS_PASSWORD)
    page.get_by_role("button", name="Login").click()
    safe_idle(page)
    # expect keeps retrying until redirect settles — lebih tahan race condition
    expect(page).not_to_have_url(_RE_LOGIN, timeout=15000)


def cms_goto(page: Page, url: str) -> None:
    """Navigasi ke halaman CMS via klik link sidebar (SPA client-side routing).

    PENTING: hard navigation (page.goto() langsung ke sub-route) selalu berakhir
    401 Unauthorized + redirect ke /login di app ini -- token auth hanya hidup di
    memory JS dan tidak di-restore saat full page reload. Klik link sidebar adalah
    satu-satunya cara navigasi antar modul yang tetap authenticated.
    """
    path = url.replace(CMS_BASE_URL, "")
    if _RE_LOGIN.search(page.url):
        login_cms(page)

    link = page.locator(f"a[href='{path}']").first
    try:
        # .click() auto-wait sampai elemen actionable -- sidebar render async
        # setelah login, jadi .count() instan tidak cukup untuk deteksi
        link.click(timeout=10000)
    except Exception:
        # Fallback terakhir jika link sidebar benar-benar tidak ada (rute tanpa menu)
        page.goto(url)

    safe_idle(page)
