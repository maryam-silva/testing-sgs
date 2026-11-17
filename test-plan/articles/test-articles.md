# Test Plan: Articles — SGS CMS

**Target URL:** https://sgs-cms-dev.qode.biz.id/articles  
**Environment:** DEV  
**Credentials:** auto@test.id / (from env SGS_CMS_PASSWORD)

---

## Preconditions & Test Data

- Sudah login ke CMS sebagai `auto@test.id`.
- Semua data dibuat dengan prefix `[AUTO]` dan dihapus di teardown.
- Kategori artikel minimal 1 sudah ada (atau dibuat lebih dulu).

---

## Positive Test Cases (Happy Path)

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-ART-01 | Halaman daftar artikel tampil | Sudah login | 1. Navigasi ke /articles | Tabel daftar artikel muncul dengan kolom judul, kategori, status | High |
| TP-ART-02 | Buat artikel baru berhasil | Halaman /articles terbuka | 1. Klik tombol Add/Tambah<br>2. Isi judul `[AUTO] Test Article SGS`<br>3. Isi konten minimal<br>4. Pilih kategori tersedia<br>5. Set status Inactive<br>6. Klik Save/Submit | Artikel baru muncul di daftar dengan judul yang sesuai | High |
| TP-ART-03 | Edit artikel berhasil | Artikel `[AUTO]` sudah ada | 1. Klik Edit pada artikel `[AUTO]`<br>2. Ubah judul menjadi `[AUTO] Test Article SGS EDITED`<br>3. Klik Save | Judul artikel berubah di daftar | High |
| TP-ART-04 | Hapus artikel berhasil | Artikel `[AUTO]` sudah ada | 1. Klik Delete/Hapus pada artikel `[AUTO]`<br>2. Konfirmasi dialog | Artikel hilang dari daftar | High |

---

## Negative Test Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-ART-05 | Simpan artikel tanpa judul gagal | Form tambah artikel terbuka | 1. Kosongkan judul<br>2. Isi konten<br>3. Klik Save | Muncul validasi wajib isi judul, artikel tidak tersimpan | Medium |
| TP-ART-06 | Simpan artikel tanpa kategori gagal | Form tambah artikel terbuka | 1. Isi judul<br>2. Tidak pilih kategori<br>3. Klik Save | Muncul validasi wajib pilih kategori | Medium |

---

## Cross-check CMS → Web

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-ART-07 | Artikel status Active tampil di web | Artikel `[AUTO]` sudah ada di CMS | 1. Set status artikel menjadi Active di CMS<br>2. Buka halaman artikel di web SGS<br>3. Cari artikel `[AUTO]` | Artikel muncul di halaman web | High |
| TP-ART-08 | Artikel status Inactive tidak tampil di web | Artikel `[AUTO]` status Inactive | 1. Pastikan artikel status Inactive di CMS<br>2. Buka halaman artikel di web<br>3. Cari artikel `[AUTO]` | Artikel tidak tampil di web | High |
