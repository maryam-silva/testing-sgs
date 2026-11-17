"""
Konteks bug terverifikasi untuk PDF report.
Format: { "TC-ID": { "issue": "...", "actual": "...", "expected": "...", "impact": "...", "severity": "1 - High" } }
Hapus entry-nya kalau bug sudah fixed.
"""

BUG_CONTEXT: dict = {
    # Contoh:
    # "TP-LOGIN-03": {
    #     "issue": "Login dengan password salah tidak menampilkan pesan error",
    #     "actual": "Halaman tidak memberikan feedback setelah klik Login",
    #     "expected": "Muncul pesan 'Email atau password salah'",
    #     "impact": "User tidak tahu kenapa login gagal",
    #     "severity": "2 - Medium",
    # },
}
