"""
Test data untuk CMS SGS.
Semua data buatan test berawalan [AUTO] dan dihapus otomatis setelah setiap test.
Jangan pernah hardcode password di sini.
"""

AUTO_PREFIX = "[AUTO]"


def auto(name: str) -> str:
    return f"{AUTO_PREFIX} {name}"


# --- Login ---
CMS_TEST_EMAIL = "auto@test.id"

# --- Contoh data CRUD (sesuaikan dengan modul CMS SGS yang ada) ---
SAMPLE_ARTICLE = {
    "title": auto("Test Article SGS"),
    "content": "Ini adalah artikel test otomatis. Konten ini dibuat oleh automation script.",
    "status": "inactive",
}

SAMPLE_PRODUCT = {
    "name": auto("Test Product SGS"),
    "description": "Deskripsi produk test otomatis.",
    "status": "inactive",
}
