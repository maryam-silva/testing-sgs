# Test Plan: Dashboard — SGS CMS

**Target URL:** https://sgs-cms-dev.qode.biz.id  
**Environment:** DEV  

---

## Preconditions & Test Data

- User sudah login menggunakan akun `auto@test.id`.
- Berada di halaman dashboard utama CMS.

---

## Positive Test Cases (Happy Path)

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-DASH-01 | Dashboard berhasil dimuat setelah login | Login berhasil | Amati halaman dashboard | Halaman dashboard tampil lengkap tanpa error | High |
| TP-DASH-02 | Menu navigasi sidebar tersedia | Dashboard terbuka | Amati sidebar navigasi | Semua menu utama tampil dan dapat diklik | High |
| TP-DASH-03 | Statistik / widget utama tampil | Dashboard terbuka | Amati area konten utama | Widget/kartu statistik terisi data (bukan kosong/error) | Medium |

---

## Negative Test Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-DASH-04 | Akses dashboard tanpa login | Tidak ada sesi aktif | Buka URL dashboard secara langsung | Redirect ke halaman login | High |

---

## Edge Cases

| Test Case ID | Title | Pre-conditions | Test Steps | Expected Result | Priority |
|---|---|---|---|---|---|
| TP-DASH-05 | Tampilan responsif mobile | Dashboard terbuka | Set viewport ke ukuran mobile (375×667) | Layout tidak rusak, menu masih bisa diakses | Low |
