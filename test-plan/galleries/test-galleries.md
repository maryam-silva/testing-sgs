# Test Plan: Galleries — SGS CMS

**Target URL:** https://sgs-cms-dev.qode.biz.id/galleries  
**Environment:** DEV  
**Credentials:** auto@test.id / (from env SGS_CMS_PASSWORD)

---

## Preconditions & Test Data

- Sudah login ke CMS sebagai `auto@test.id`.
- File gambar test tersedia di `data/assets/test-image.jpg`.
- Semua data dibuat dengan prefix `[AUTO]` dan dihapus di teardown.

---

## Positive Test Cases (Happy Path)

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-GAL-01 | Halaman daftar galeri tampil | Sudah login | 1. Navigasi ke /galleries | Daftar item galeri muncul | High |
| TP-GAL-02 | Tambah item galeri berhasil | Halaman /galleries terbuka | 1. Klik Add<br>2. Isi judul `[AUTO] Test Gallery SGS`<br>3. Upload gambar<br>4. Set status Inactive<br>5. Klik Save | Item galeri baru muncul di daftar | High |
| TP-GAL-03 | Edit item galeri berhasil | Item galeri `[AUTO]` sudah ada | 1. Klik Edit<br>2. Ubah judul menjadi `[AUTO] Test Gallery SGS EDITED`<br>3. Klik Save | Judul berubah di daftar | High |
| TP-GAL-04 | Hapus item galeri berhasil | Item galeri `[AUTO]` sudah ada | 1. Klik Delete<br>2. Konfirmasi | Item hilang dari daftar | High |

---

## Negative Test Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-GAL-05 | Simpan galeri tanpa gambar gagal | Form tambah galeri terbuka | 1. Isi judul<br>2. Tidak upload gambar<br>3. Klik Save | Validasi wajib upload gambar | Medium |

---

## Cross-check CMS → Web

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-GAL-06 | Item galeri Active tampil di web | Item galeri `[AUTO]` sudah ada | 1. Set status Active di CMS<br>2. Buka halaman galeri di web SGS<br>3. Cari item `[AUTO]` | Item galeri muncul di web | High |
| TP-GAL-07 | Item galeri Inactive tidak tampil di web | Item galeri `[AUTO]` status Inactive | 1. Pastikan status Inactive<br>2. Buka halaman galeri di web | Item tidak tampil | High |
