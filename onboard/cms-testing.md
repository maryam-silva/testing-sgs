# Guide Onboarding: Testing CMS (Content Management System)

Halo tim! Kalau kalian dapet *project* untuk ngetes bagian CMS, pendekatannya bakal sedikit beda sama ngetes aplikasi *mobile* atau *website* biasa. CMS ini ibarat "dapur" tempat admin ngatur data, jadi fokus utama kalian adalah mastiin datanya aman, alurnya bener, dan nggak bikin *error* di sisi *user*.

Beberapa contoh *project* CMS yang mungkin bakal kalian pegang nanti misalnya Matta CMS/Admin, ACDC CMS, atau APCM CMS Admin. Biar lancar, perhatiin poin-poin di bawah ini ya:

### 🔄 Fundamental Testing: CRUD itu Wajib!

Setiap kali ada modul atau halaman baru di CMS, wajib banget buat ngetes siklus **CRUD**:

- **C (Create):** Bisa nggak bikin data baru? Tes masukin data normal, data dikosongin, sampai karakter aneh (simbol).
- **R (Read):** Setelah dibikin, datanya muncul nggak di tabel CMS? Tampilannya sesuai sama yang di-*input* tadi atau malah berantakan?
- **U (Update):** Coba edit data yang udah ada. Bisa kesimpen dengan bener dan datanya berubah nggak?
- **D (Delete):** Hapus data. Pastiin datanya beneran hilang dari tabel. Kalau ada fitur *confirmation pop-up* sebelum hapus, pastiin itu juga jalan.

### 🔗 Kroscek ke Front-End (Web / Mobile)

Ini bagian paling krusial! Apa pun yang kalian *setting* di CMS, **wajib** dicek efeknya di *front-end* (aplikasi atau web yang dilihat *user*).

- Misalnya kalian *upload banner* atau nambahin *campaign* baru di CMS. Langsung buka web/aplikasi *user*nya.
- Pastiin *banner*nya muncul, ukurannya pas (nggak gepeng/pecah), dan teksnya sesuai.

### 🛡️ Role & Permission (Hak Akses)

Biasanya CMS punya beberapa level *user*, kayak *Superadmin*, *Admin*, atau *Operator*.

- Pastiin tiap *user* cuma bisa buka menu yang emang jadi haknya.
- Misal: *Operator* cuma boleh lihat data, tombol *Edit* dan *Delete* harusnya nggak ada atau di-*disable*.

### 📊 Tabel, Pagination, Filter & Search

Data di CMS itu lama-lama bakal ribuan. Jadi fitur-fitur pendukung tabel ini harus dites:

- **Search:** Tes nyari pake nama, ID, atau nomor HP. Hasilnya akurat nggak?
- **Filter:** Coba saring data berdasarkan status (misal *Active* / *Inactive*) atau rentang tanggal.
- **Pagination:** Kalau datanya banyak, tes klik halaman 2, halaman 3, atau fitur `Next`/`Previous`. Pastiin halamannya beneran pindah dan datanya ganti.

### ⚠️ Validasi Form & File Upload

CMS itu sarangnya input *form*, jadi kalian harus rajin nguji batasannya:

- **Input Teks:** Tes masukin karakter yang kepanjangan (misal lebih dari 255 karakter).
- **File Upload:** Cek validasi ukurannya (misal disuruh max 2MB, coba *upload* file 5MB). Cek juga formatnya (misal wajib JPG/PNG, coba kalian *upload* PDF). Harusnya sistem nolak dan munculin pesan *error* yang jelas, bukan malah sistemnya yang *nge-hang*.

### 📋 Aturan Laporan

- Format **Test Case** dan **Bug Report** tetep sama persis pake *template* yang udah kita bahas sebelumnya (baik buat di Spreadsheet, Notion, atau Trello).
- Kalau nemu *bug* di *front-end* gara-gara *settingan* CMS, kasih *remark* yang jelas di laporannya (Contoh di *Bug Report*: "Input SOW di CMS udah disubmit ulang, tapi *reason* lama masih muncul di web").