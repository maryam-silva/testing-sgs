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

# --- Articles ---
SAMPLE_ARTICLE = {
    "title": auto("Test Article SGS"),
    "content": "Ini adalah artikel test otomatis. Konten ini dibuat oleh automation script.",
    "status": "inactive",
}

# --- Banners ---
SAMPLE_BANNER = {
    "title": auto("Test Banner SGS"),
    "status": "inactive",
}

# --- FAQs ---
SAMPLE_FAQ = {
    "question": auto("Pertanyaan Test SGS"),
    "answer": "Ini adalah jawaban test otomatis dari automation script SGS.",
    "status": "inactive",
}

# --- Galleries ---
SAMPLE_GALLERY = {
    "title": auto("Test Gallery SGS"),
    "status": "inactive",
}

# --- Products ---
SAMPLE_PRODUCT = {
    "name": auto("Test Product SGS"),
    "description": "Deskripsi produk test otomatis.",
    "status": "inactive",
}
