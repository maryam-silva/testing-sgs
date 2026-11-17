# Panduan Onboarding QA: Test Case & Bug Report

Selamat datang di tim QA! Dokumen ini adalah panduan dasar bagi QA Intern dan Junior untuk memahami standar pembuatan **Test Case** dan penulisan **Bug Report** di dalam tim kita. Harap baca dengan teliti dan gunakan format ini sebagai acuan dalam pekerjaan sehari-hari.

---

## 1. Panduan Pembuatan Test Case

Test Case adalah skenario terstruktur yang kita gunakan untuk memvalidasi apakah suatu fitur berjalan sesuai dengan dokumen spesifikasi (*requirements*).

### Penjelasan Kolom Test Case

- **TEST ID**: Nomor identifikasi unik. Format standar: `TC/[module]-000`.
- **FEATURES**: Nama modul/fitur utama (contoh: Auth).
- **SUB FEATURES**: Sub-fitur spesifik (contoh: Login, Registration).
- **DESCRIPTION**: Penjelasan singkat mengenai skenario pengetesan.
- **STEP TO REPRODUCE**: Langkah-langkah detail untuk melakukan tes secara berurutan.
- **EXPECTED RESULT**: Hasil akhir yang seharusnya terjadi jika sistem berfungsi normal.
- **TEST TYPE**: Kategori tes (*Positive*, *Negative*, *Edge*).
- **STATUS**: Hasil pengujian (*Pass*, *Fail*, *Not Applicable*, *Cancel*, *Hold*).
- **TESTER**: Nama anggota QA yang menjalankan tes.
- **TEST DATE**: Tanggal eksekusi tes.
- **REMARK**: Catatan tambahan (wajib diisi dengan detail error jika status *Fail*).

### Contoh Test Case (Modul: Auth - Login)

| TEST ID | FEATURES | SUB FEATURES | DESCRIPTION | STEP TO REPRODUCE | EXPECTED RESULT | TEST TYPE | STATUS | TESTER | TEST DATE | REMARK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TC-LOGIN-001 | Auth | Login | Login with registered number | 1. Open login page<br>2. Enter valid number<br>3. Click login | Login successful | Positive | Pass | Reyhan | 13 August 2026 |  |
| TC-LOGIN-003 | Auth | Login | Invalid number length | Input <10 or >15 digits | Validation error | Negative | Fail | Reyhan | 13 August 2026 | masih bisa dibawah 10 digit |
| TC-LOGIN-005 | Auth | Registration | Unregistered number | Input new number | Redirect to registration | Edge | Hold | Reyhan |  |  |

---

## 2. Panduan Pembuatan Bug Report (Report Issue)

Bug Report digunakan untuk melacak *error*, anomali, permintaan perubahan (*Change Request*), atau pertanyaan terkait pengembangan fitur yang sedang berjalan.

### Penjelasan Kolom Bug Report

- **Date**: Tanggal pelaporan (Format: DD-MMM-YYYY).
- **Platform**: *Environment* aplikasi tempat isu ditemukan (CMS, Website, dll).
- **Menu/Item**: Nama halaman atau fitur yang terdampak.
- **Condition / State**: Deskripsi temuan, kondisi saat ini, atau pertanyaan secara jelas.
- **Raised by**: Nama/inisial pelapor tiket (contoh: PM, Reyhan, atau Client).
- **Priority**: Tingkat urgensi (`1 - High`, `2 - Medium`, `3 - Low`, `QUESTION`).
- **Evidence (if any)**: Bukti pendukung seperti *Screenshot* atau *Screen Record* (Sangat direkomendasikan untuk diisi).
- **Type**: Jenis pelaporan (`1 - Bug`, `2 - CR`, `3 - NR`, `4 - QST`, `5 - IPV`).
- **Assigned to**: Nama *Developer* / PIC yang bertugas menangani isu (ini nanti diisi sama PM).
- **Status**: Tahapan tiket (`1 - Raised`, `2 - Debugging`, `3 - QA`, `4 - Solved`, `8 - Prod`, `9 - Done Prod Test [CLEAR]`, dll).
- **Remarks**: Catatan komunikasi antar tim (misal: alasan reject dari QA, klarifikasi dari Dev).

### Contoh Bug Report

| Date | Platform | Menu/Item | Condition / State | Raised by | Priority | Evidence | Type | Assigned to | Status | Remarks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30-Mar-2026 | CMS - Website | Campaign | tambah inputan untuk komisi di detail campaign. di web ambil dari isian ini aja, jangan dari data TAP | PM | 1 - High |  | 1 - Bug | Ringgo | 1 - Raised |  |
| 30-Mar-2026 | Website | Campaign + Event | Kalau ada diminta masukin note, kasih info apakah internal atau external, dan klo ada revisi reason lama nya gak perlu ditampilin lagi | PM | 2 - Medium |  | 2 - CR | Vedian | 2 - Debugging | kalau di reject halaman campaign dan event SOW: reason lamanya masih muncul di cms walaupun udah submit ulang |
| 30-Mar-2026 | Website | Campaign | Product campaign udah dimunculin walaupun belum di generate link | Client | QUESTION |  | 4 - QST | Vedian | 4 - Solved |  |
| 30-Mar-2026 | CMS - Website | Campaign | Make sure fungsi tracking pengiriman sample - penagihan SOW | Reyhan | QUESTION |  | 4 - QST | Ringgo | 7 - Fail | ini cek nya dimana ya? |
| 30-Mar-2026 | Website | Event | Event di home hilang tergantung settingan tugas event (none, quiz, SOW) | Reyhan | 2 - Medium |  | 5 - IPV | Ananda | 9 - Done Prod Test [CLEAR] |  |

---

## 3. Maintenance Test Case & Alur Pelaporan Alternatif

Dalam keseharian QA, kita perlu melakukan pemeliharaan (maintenance) terhadap skenario pengujian. Anda dapat memanfaatkan **AI** untuk membantu proses ini:

1. **Pembuatan Test Case dari Bug (via AI)**:
Jika Anda menemukan *bug*, salin deskripsi dan ekspetasi yang diharapkan dari *bug* tersebut dan berikan ke AI (seperti Gemini/ChatGPT). Mintalah AI untuk membuatkan skenario *Test Case* baru yang mencakup tipe *Positive*, *Negative*, dan *Edge* yang sesuai dengan format template kita. Lalu masukan ke file test case dan feature sesuai tempat bug nya.
2. **Re-Test Bug Fix**:
Jika *bug* tersebut sudah diperbaiki (*fixed*) oleh *Developer*, lakukan pengetesan menggunakan *Test Case* yang baru saja dibuat oleh AI tadi.
    - **Wajib di-update:** Ubah `STATUS`, nama `TESTER`, dan `TEST DATE`.
    - **Remarks:** Tambahkan catatan pada kolom `REMARK` bahwa ini adalah pengetesan dari *bug* tanggal sekian (contoh: "Retest untuk bug report 30-Mar-2026").
3. **Drafting Bug Report (via AI) & Evidence**:
Saat menemukan *bug*, Anda juga bisa meminta AI untuk menyusun format *Bug Report* sesuai template kita. Setelah itu, **wajib** tambahkan *Evidence* pendukung ke dalamnya, bisa berupa *Screenshot* (SS) atau *link* rekaman video (sangat direkomendasikan menggunakan tools seperti **Jam.dev**).
4. **Pelaporan Multi-Platform**:
Selain direkapitulasi secara internal, pelaporan *bug* juga dapat didistribusikan ke *tools project management* lain:
    - **Notion**: Lakukan pelaporan *bug* di Notion dengan komposisi dan isi yang sama persis dengan template tabel di atas.
    - **Trello**: Jika menggunakan Trello, laporkan isu dalam bentuk *card* dengan tetap mempertahankan format data yang ada di template (seperti Date, Platform, Type, Status, dsb).

---

## 4. 💡 Best Practices untuk QA Intern & Junior

1. **Selalu Lampirkan Bukti (Evidence)**: Jangan biarkan kolom *Evidence* kosong saat melaporkan bug visual atau fungsional. Gunakan link *screenshot* atau video (contoh: Jam.dev) agar *Developer* lebih mudah melakukan investigasi.
2. **Deskriptif pada Remark**: Jika *Test Case* gagal (Fail) atau tiket di-reject kembali ke Developer, tuliskan secara jelas bagian mana yang masih tidak sesuai pada kolom *Remark*.
3. **Pahami Tipe Laporan (Type)**: Pastikan Anda membedakan mana yang murni *Bug*, mana yang *Change Request* (CR), atau hanya pertanyaan (QST) agar penanganan Developer bisa lebih terarah.