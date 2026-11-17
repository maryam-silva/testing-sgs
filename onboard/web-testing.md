# 🌐 Guide Onboarding: Web Testing (Compro, Landing Page & Web App)

Halo lagi! Kalau sebelumnya kita udah bahas Mobile dan CMS, sekarang kita bahas *testing* website secara umum.

Ngetes web itu pendekatannya beda-beda, tergantung jenis webnya apa. Biar nggak bingung, kita bagi jadi 3 kategori utama ya: **Company Profile (Compro)**, **Landing Page**, dan **Web App**. Yuk, disimak!

### 🏢 1. Company Profile (Compro)

Compro ini ibarat "wajah" perusahaan. Jarang ada fitur ribet, tapi tampilannya harus *perfect*. Fokus kalian di sini lebih ke *UI/UX* dan detail visual:

- **Visual & Typo:** Pastiin nggak ada gambar pecah (*pixelated*), *font* yang belang-belang, atau teks yang *typo*.
- **Broken Links:** Cek semua tombol, menu navigasi, dan *icon* sosmed (Instagram, LinkedIn, dll). Pastiin semuanya ngarah ke halaman yang bener, jangan sampai dapet *error 404* atau halamannya nggak bisa diklik.
- **Formulir Kontak (Contact Us):** Kalau ada *form* "Hubungi Kami", coba diisi dan di-*submit*. Pastiin notifikasinya sukses dan *email*nya beneran masuk ke tujuan (bisa minta tolong *dev* atau PM buat ngecek data masuknya).

### 🚀 2. Landing Page

Biasanya web ini dibikin khusus buat *campaign* atau promo tertentu, jadi umurnya lebih pendek tapi *traffic*-nya padat. Fokus utamanya ada di konversi:

- **Tombol CTA (Call to Action):** Tombol kayak "Daftar Sekarang", "Beli", atau "Klaim Promo" itu urat nadinya Landing Page. Tes klik semuanya! Pastiin *flow*nya bener, entah itu ngelempar ke WhatsApp, *scroll* ke bawah (*anchor link*), atau buka halaman pendaftaran.
- **Formulir Pendaftaran / Leads:** Tes masukin data normal sampai data aneh. Cek pesannya kalau sukses kayak gimana, dan kalau *error* (misal format email salah) pesannya jelas atau nggak.
- **Loading Speed (Visual):** Perhatiin pas buka webnya, apakah *loading* gambarnya berat banget? Kalau kerasa lama, laporin aja biar *dev* bisa *compress* ukurannya.

### 💻 3. Web App (Aplikasi Web)

Nah, ini yang paling kompleks. Web App itu udah kayak sistem atau *software* (contoh: *dashboard user*, sistem absensi, atau alat manajemen *project*). Fokus kalian di sini adalah *logic* dan fungsionalitas:

- **Alur Utama (Core Logic):** Pahami PRD-nya. Kalau ini aplikasi buat *submit* tugas (SOW), pastiin dari proses *upload*, status berubah jadi *pending*, sampai dapet persetujuan dari admin berjalan mulus tanpa macet.
- **Session & Security:** Tes *login* terus biarin *tab*nya kebuka agak lama (*idle*). Harusnya kalau terlalu lama, otomatis ke-*logout* (*session expired*). Cek juga fitur *Forgot Password*.
- **Error Handling:** Coba bikin sistemnya "marah". Masukin tipe file yang salah, kosongin *field* yang wajib (tanda bintang ), atau masukin input di luar nalar. Pastiin muncul pesan *error* yang manusiawi, bukan *codingan* kotor atau halaman jadi *blank*.
- **Integrasi ke CMS:** Kalau Web App ini nyambung ke CMS yang dipegang admin, cek siklus bolak-baliknya. Kalau di Web App kita hapus item, di CMS harusnya juga ilang atau statusnya berubah.

### 📱 Reminder Penting: Responsive Mobile!

- Mau ngetes Compro, Landing Page, atau Web App, **wajib banget** dites juga via *browser* HP (atau Inspect Element > mode Mobile di Chrome/Safari).
- Sering banget kejadian di layar laptop cakep, tapi pas dibuka di HP teksnya numpuk, tombolnya ketutupan, atau menunya (*hamburger menu*) nggak bisa diklik. Jangan sampai kelewat, ya!

### 📋 Format Laporan

- Tetep sama! *Test Case* dan *Bug Report* ngikutin *template* utama kita.
- Bisa ditaruh di Notion, Trello, atau Spreadsheet sesuai instruksi *project*.
- Kalau ada *bug* tampilan (*UI issue*) atau *flow* yang *stuck*, jangan lupa sertakan *screenshot* (SS) atau rekaman pakai **Jam.dev** biar *developer* gampang nge-*trace*nya.