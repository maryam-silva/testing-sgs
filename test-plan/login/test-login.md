# Test Plan: Login — SGS CMS

**Target URL:** https://sgs-cms-dev.qode.biz.id  
**Environment:** DEV  
**Credentials:** auto@test.id / (from env SGS_CMS_PASSWORD)

---

## Preconditions & Test Data

- Browser dibuka fresh (tidak ada sesi sebelumnya).
- Akun `auto@test.id` sudah terdaftar dan aktif di environment DEV.
- Password disimpan di environment variable `SGS_CMS_PASSWORD`.

---

## Positive Test Cases (Happy Path)

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-LOGIN-01 | Login berhasil dengan kredensial valid | Halaman login terbuka | 1. Isi email valid<br>2. Isi password valid<br>3. Klik tombol Login | Redirect ke halaman dashboard, URL tidak mengandung `/login` | High |
| TP-LOGIN-02 | Halaman dashboard tampil setelah login | Login berhasil (TP-LOGIN-01) | Amati halaman setelah redirect | Judul/elemen utama dashboard terlihat | High |

---

## Negative Test Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-LOGIN-03 | Login gagal dengan password salah | Halaman login terbuka | 1. Isi email valid<br>2. Isi password salah<br>3. Klik Login | Muncul pesan error, tetap di halaman login | High |
| TP-LOGIN-04 | Login gagal dengan email tidak terdaftar | Halaman login terbuka | 1. Isi email tidak terdaftar<br>2. Isi password apapun<br>3. Klik Login | Muncul pesan error credential tidak valid | Medium |
| TP-LOGIN-05 | Validasi field email kosong | Halaman login terbuka | 1. Kosongkan email<br>2. Isi password<br>3. Klik Login | Muncul pesan validasi wajib isi email | Medium |
| TP-LOGIN-06 | Validasi field password kosong | Halaman login terbuka | 1. Isi email valid<br>2. Kosongkan password<br>3. Klik Login | Muncul pesan validasi wajib isi password | Medium |
| TP-LOGIN-07 | Validasi format email tidak valid | Halaman login terbuka | 1. Isi email tanpa `@` (misal: `testqbit`)<br>2. Isi password<br>3. Klik Login | Muncul pesan format email tidak valid | Low |

---

## Edge Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-LOGIN-08 | Login dengan spasi di awal/akhir email | Halaman login terbuka | 1. Isi email dengan spasi di depan/belakang<br>2. Isi password valid<br>3. Klik Login | Sistem trim spasi dan login berhasil, atau munculkan error format | Low |
| TP-LOGIN-09 | Akses halaman login saat sudah login | Sudah login (ada sesi aktif) | Navigasi langsung ke URL `/login` | Redirect otomatis ke dashboard | Low |
