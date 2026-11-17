# Test Plan: SGS Web Frontend

**URL:** https://sgs-web-dev.qode.biz.id  
**Platform:** Web (Next.js SSR)  
**Framework:** Playwright Python + pytest  
**Marker:** `@pytest.mark.web`

---

## Halaman yang Diuji

| Halaman | URL |
|---------|-----|
| Homepage | `/` |
| About | `/about` |
| Brands | `/brands` |
| News | `/news` |
| Contact Us | `/contact-us` |
| Careers | `/careers` |
| Sustainability | `/sustainability` |

---

## Test Cases

### Homepage (`/`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-01 | Homepage tampil dengan heading utama | Positive / Smoke | H1/H2 mengandung teks "Sinar Sosro" atau "SGS" |
| TP-WEB-02 | Navigasi global tampil di homepage | Positive | Nav links (About, Brands, News, Contact) terlihat |
| TP-WEB-03 | Bagian berita (news section) tampil di homepage | Positive | Section dengan label "Berita" / "News" terlihat |
| TP-WEB-04 | Banner/carousel tampil di homepage | Positive | Minimal 1 elemen banner/slider terlihat |
| TP-WEB-05 | Klik logo navigasi kembali ke homepage | Positive | URL kembali ke `/` |

### About (`/about`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-06 | Halaman About tampil | Positive / Smoke | Status 200, ada konten teks visible |
| TP-WEB-07 | Judul halaman About ada | Positive | Heading atau title mengandung kata "About" / "Tentang" |

### Brands (`/brands`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-08 | Halaman Brands tampil | Positive / Smoke | Status 200, konten brand terlihat |
| TP-WEB-09 | Daftar brand/produk tampil | Positive | Minimal 1 item brand/produk terlihat |

### News (`/news`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-10 | Halaman News tampil | Positive / Smoke | Status 200, konten daftar berita terlihat |
| TP-WEB-11 | Daftar artikel/berita tampil | Positive | Minimal 1 item berita terlihat |
| TP-WEB-12 | Klik artikel membuka detail | Positive | URL berubah ke halaman detail artikel |

### Contact Us (`/contact-us`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-13 | Halaman Contact Us tampil | Positive / Smoke | Status 200, ada informasi kontak atau form |
| TP-WEB-14 | Formulir kontak atau info kontak ada | Positive | Form input atau alamat/telepon terlihat |
| TP-WEB-15 | Submit form kosong gagal atau ditolak | Negative | Validasi error muncul atau form tidak tersubmit |

### Careers (`/careers`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-16 | Halaman Careers tampil | Positive / Smoke | Status 200, konten karir terlihat |
| TP-WEB-17 | Konten lowongan atau info karir ada | Positive | Minimal 1 elemen teks/section karir terlihat |

### Sustainability (`/sustainability`)

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-18 | Halaman Sustainability tampil | Positive / Smoke | Status 200, konten terlihat |
| TP-WEB-19 | Konten sustainability ada | Positive | Minimal 1 heading atau teks section terlihat |

### Navigasi Global

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-20 | Link navigasi About berfungsi | Positive | Klik nav → URL `/about` |
| TP-WEB-21 | Link navigasi Brands berfungsi | Positive | Klik nav → URL `/brands` |
| TP-WEB-22 | Link navigasi News berfungsi | Positive | Klik nav → URL `/news` |
| TP-WEB-23 | Link navigasi Contact Us berfungsi | Positive | Klik nav → URL `/contact-us` |

### Edge Cases & Negatif

| ID | Judul | Tipe | Ekspektasi |
|----|-------|------|------------|
| TP-WEB-24 | URL tidak valid menampilkan 404 | Negative | `/halaman-tidak-ada-xyz` → 404 atau pesan "not found" |
| TP-WEB-25 | Halaman tampil di mobile viewport | Edge | Viewport 375×812, tidak ada horizontal scroll |
| TP-WEB-26 | Tidak ada console error kritis di homepage | Edge | Tidak ada JS error `Uncaught` di console |

---

## Catatan

- Semua test menggunakan `web_page` fixture (tidak perlu login)
- CMS cross-check: artikel CMS yang Active muncul di `/news` (bukan `/articles`)
- `/faq` dan `/gallery` tidak tersedia di web — test cross-check CMS untuk modul tersebut skip verifikasi web
