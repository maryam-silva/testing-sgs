# Test Plan: FAQs — SGS CMS

**Target URL:** https://sgs-cms-dev.qode.biz.id/faqs  
**Environment:** DEV  
**Credentials:** auto@test.id / (from env SGS_CMS_PASSWORD)

---

## Preconditions & Test Data

- Sudah login ke CMS sebagai `auto@test.id`.
- Semua data dibuat dengan prefix `[AUTO]` dan dihapus di teardown.
- FAQ Group minimal 1 sudah ada (atau dibuat lebih dulu).

---

## Positive Test Cases (Happy Path)

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-FAQ-01 | Halaman daftar FAQ tampil | Sudah login | 1. Navigasi ke /faqs | Daftar FAQ muncul dengan kolom pertanyaan, group, status | High |
| TP-FAQ-02 | Buat FAQ baru berhasil | Halaman /faqs terbuka | 1. Klik Add<br>2. Isi pertanyaan `[AUTO] Pertanyaan Test SGS`<br>3. Isi jawaban<br>4. Pilih group<br>5. Set status Inactive<br>6. Klik Save | FAQ baru muncul di daftar | High |
| TP-FAQ-03 | Edit FAQ berhasil | FAQ `[AUTO]` sudah ada | 1. Klik Edit<br>2. Ubah pertanyaan menjadi `[AUTO] Pertanyaan Test SGS EDITED`<br>3. Klik Save | Pertanyaan berubah di daftar | High |
| TP-FAQ-04 | Hapus FAQ berhasil | FAQ `[AUTO]` sudah ada | 1. Klik Delete<br>2. Konfirmasi | FAQ hilang dari daftar | High |

---

## Negative Test Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-FAQ-05 | Simpan FAQ tanpa pertanyaan gagal | Form tambah FAQ terbuka | 1. Kosongkan pertanyaan<br>2. Isi jawaban<br>3. Klik Save | Validasi wajib isi pertanyaan | Medium |
| TP-FAQ-06 | Simpan FAQ tanpa jawaban gagal | Form tambah FAQ terbuka | 1. Isi pertanyaan<br>2. Kosongkan jawaban<br>3. Klik Save | Validasi wajib isi jawaban | Medium |

---

## Cross-check CMS → Web

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-FAQ-07 | FAQ Active tampil di halaman FAQ web | FAQ `[AUTO]` sudah ada | 1. Set status Active di CMS<br>2. Buka halaman FAQ di web SGS<br>3. Cari pertanyaan `[AUTO]` | FAQ muncul di web | High |
| TP-FAQ-08 | FAQ Inactive tidak tampil di web | FAQ `[AUTO]` status Inactive | 1. Pastikan status Inactive<br>2. Buka halaman FAQ di web | FAQ tidak tampil | High |
