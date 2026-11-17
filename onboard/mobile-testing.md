# 📱Guide Onboarding: Mobile & Responsive Web Testing

Halo! Buat kalian yang kebagian ngetes *project* di platform *mobile* (aplikasi maupun web), wajib baca panduan ini dulu ya. Biar alurnya enak dan aman.

### 📋 Format Test Case & Bug Report

- Format penulisan **Test Case** dan **Bug Report** buat *mobile* itu **tetep sama persis** kayak di web. Jadi, tinggal pake *template* yang udah ada.

### Cara Dapetin Aplikasi Buat Dites

- **Android:** Nanti file aplikasinya (`.apk`) bakal di-*share* langsung di grup WhatsApp/komunikasi *project* masing-masing. Tinggal *download* dan *install*.
- **iOS (iPhone/iPad):** Nah, kalau iOS beda dikit. Nanti kalian bakal di-*invite* sama Mas Ringgo ke aplikasi **TestFlight**. Dari situ, baru deh kalian di-*invite* lagi buat masuk ke *project* spesifiknya.

### Paham Environment (Env) & Versi Aplikasi

Setiap rilis versi baru, pasti ada identitasnya (ini versi berapa) dan lagi pake *environment* (*env*) apa. Kita punya 3 *env* utama, tolong perhatiin fungsinya:

- **DEV (Development):** Ini tempatnya main kasar. Bebas dipake buat eksekusi semua *test case*, *random case*, sampai *extreme case*. Mau diobrak-abrik juga nggak apa-apa.
- **STAGING:** Kalau di sini, *database*nya itu hasil *copy* dari *production*. Jadi datanya mirip banget sama data *live* / data *user* asli.
- **PROD (Production):** **Dilarang keras buat *testing*!** Ini cuma buat pengecekan skala kecil atau sekadar *make sure* fitur aman. Kalau emang ada kebutuhan mendesak buat ngecek di *prod*, **wajib** minta izin dulu ke QA Lead, PM, dan Product Manager.

### Laporan Bug & Keterbatasan Device

- **Evidence:** Kalau nemu *bug*, wajib lampirin bukti. Bisa berupa *screenshot* (SS) atau hasil rekam layar (kalau *bug*nya berupa *flow* atau animasi).
- **Device Terbatas:** Kalau kamu cuma pegang 1 jenis *device* (misal cuma punya Android atau cuma iOS), langsung kabarin QA Lead ya. Biar nanti dibantu cari solusi buat *testing* di *device* yang kamu nggak punya.

### 🌐 Mobile Testing Bukan Cuma Buat Aplikasi!

- Inget ya, *testing* di HP itu bukan cuma khusus buat *project* *Mobile App*.
- Buat *project* Web (terutama halaman *front-end* / yang dilihat *user*, bukan CMS), kita juga **wajib** ngetes *responsiveness*nya di *browser* HP biar tampilannya nggak berantakan.