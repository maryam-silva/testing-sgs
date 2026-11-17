# Test Plan: Banners — SGS CMS

**Target URL:** https://sgs-cms-dev.qode.biz.id/banners  
**Environment:** DEV  
**Credentials:** auto@test.id / (from env SGS_CMS_PASSWORD)

---

## Preconditions & Test Data

- Sudah login ke CMS sebagai `auto@test.id`.
- File gambar test tersedia di `data/assets/test-banner.jpg`.
- Semua data dibuat dengan prefix `[AUTO]` dan dihapus di teardown.

---

## Positive Test Cases (Happy Path)

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-BAN-01 | Halaman daftar banner tampil | Sudah login | 1. Navigasi ke /banners | Tabel daftar banner muncul | High |
| TP-BAN-02 | Buat banner baru berhasil | Halaman /banners terbuka | 1. Klik Add<br>2. Isi judul `[AUTO] Test Banner SGS`<br>3. Upload gambar<br>4. Set status Inactive<br>5. Klik Save | Banner baru muncul di daftar | High |
| TP-BAN-03 | Edit banner berhasil | Banner `[AUTO]` sudah ada | 1. Klik Edit<br>2. Ubah judul menjadi `[AUTO] Test Banner SGS EDITED`<br>3. Klik Save | Judul banner berubah di daftar | High |
| TP-BAN-04 | Hapus banner berhasil | Banner `[AUTO]` sudah ada | 1. Klik Delete<br>2. Konfirmasi | Banner hilang dari daftar | High |

---

## Negative Test Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-BAN-05 | Simpan banner tanpa judul gagal | Form tambah banner terbuka | 1. Kosongkan judul<br>2. Klik Save | Validasi wajib isi judul | Medium |

---

## Cross-check CMS → Web

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-BAN-06 | Banner Active tampil di homepage web | Banner `[AUTO]` sudah ada | 1. Set status Active di CMS<br>2. Buka homepage web SGS<br>3. Cek section banner/carousel | Banner `[AUTO]` muncul di homepage | High |
| TP-BAN-07 | Banner Inactive tidak tampil di web | Banner `[AUTO]` status Inactive | 1. Pastikan status Inactive<br>2. Buka homepage web | Banner tidak tampil | High |
