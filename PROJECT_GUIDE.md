# PROJECT GUIDE: Iranian Customer Churn

> File ini adalah **sumber kebenaran** project. Isi hanya fakta yang sudah pasti. Bagian yang belum diketahui dibiarkan kosong.
> Berikan ke AI di awal setiap sesi ("baca PROJECT_GUIDE.md dulu"). Perbarui **Status** dan **Log Keputusan** setiap selesai satu langkah.
> Terakhir diperbarui: 2026-11-04 (restart dari nol)

---

## 1. Ringkasan Proyek

| Item | Isi |
|---|---|
| Tujuan | **Portofolio / pembelajaran**: menunjukkan alur data science dan MLOps end-to-end yang rapi, jujur, dan bisa dijelaskan |
| Masalah | Memprediksi pelanggan sebuah perusahaan telekomunikasi Iran yang churn |
| Dataset | `dataset/Customer Churn.csv` (UCI *Iranian Churn Dataset*) |
| Target | `Churn` (1 = churn, 0 = non-churn, menurut UCI) |
| Cakupan | EDA, cleaning, feature engineering, modeling, experiment tracking, deployment, monitoring |
| Bahasa | Penjelasan dan komentar dalam Bahasa Indonesia, nama variabel dan fungsi dalam Bahasa Inggris |
| Alur kode | Notebook untuk eksplorasi, logika yang dipakai ulang dipindah ke `src/` |
| Deployment | Tanpa Docker untuk saat ini |

**Prinsip utama:** kejujuran dan kebenaran analisis lebih penting daripada angka yang bagus.

---

## 2. Dataset

- **Sumber:** UCI Machine Learning Repository, lisensi **CC BY 4.0** (boleh disertakan di repo dengan atribusi).
  Sitasi: *Iranian Churn [Dataset]. (2020). UCI Machine Learning Repository. https://doi.org/10.24432/C5JW3Z*
- **Ukuran menurut UCI:** 3.150 baris, masing-masing mewakili satu pelanggan. UCI menyebut data "dikumpulkan secara acak" dari basis data sebuah perusahaan telekomunikasi Iran selama 12 bulan.
- **Definisi label menurut UCI (ditinjau 2026-11-04):** semua atribut kecuali `Churn` adalah agregat **9 bulan pertama**. `Churn` adalah **status pelanggan di akhir bulan ke-12**. Tiga bulan di antaranya adalah *planning gap*.
- **Yang tidak dijelaskan UCI:** arti operasional "churn" (berhenti berlangganan, pindah operator, atau tidak aktif), cara `Status` ditentukan dan kapan diukur, cara menghitung `Customer Value`, cara pengambilan sampel acak, dan siapa pembuat datanya.
- Jurnal referensi yang sudah dikumpulkan ada di `jurnal/` (diabaikan Git).

### Data dictionary

> Nama kolom persis seperti header file. Kolom yang artinya belum ada: tanyakan ke pengguna.

| Kolom | Arti menurut UCI |
|---|---|
| `Call  Failure` | belum ada deskripsi, tanyakan ke pengguna |
| `Complains` | biner: 0 = tidak ada komplain, 1 = ada komplain |
| `Subscription  Length` | belum ada deskripsi, tanyakan ke pengguna |
| `Charge  Amount` | ordinal: 0 = jumlah terendah, 9 = tertinggi |
| `Seconds of Use` | total detik panggilan |
| `Frequency of use` | belum ada deskripsi, tanyakan ke pengguna |
| `Frequency of SMS` | belum ada deskripsi, tanyakan ke pengguna |
| `Distinct Called Numbers` | belum ada deskripsi, tanyakan ke pengguna |
| `Age Group` | ordinal: 1 = lebih muda, 5 = lebih tua |
| `Tariff Plan` | biner: 1 = pay as you go, 2 = kontrak |
| `Status` | biner: 1 = aktif, 2 = non-aktif |
| `Age` | belum ada deskripsi, tanyakan ke pengguna |
| `Customer Value` | "nilai pelanggan yang dihitung" (tanpa rumus) |
| `Churn` | **target**: biner, 1 = churn, 0 = non-churn |

### Kolom bantu (BUKAN fitur)

Belum ada.

---

## 3. Temuan Kunci

> Hanya hasil yang **dihitung dari kode** dan bisa dilacak ke notebook tertentu.

| # | Temuan | Dihitung di | Tanggal |
|---|---|---|---|
| | Belum ada | | |

---

## 4. Keputusan yang Sudah Dikunci

> Keputusan analisis diambil **bersama pengguna**, bukan sepihak oleh AI.

| # | Keputusan | Alasan | Tanggal |
|---|---|---|---|
| | Belum ada keputusan analisis | | |

---

## 5. Metrik Evaluasi

Belum diputuskan. Akan dibahas dengan pengguna setelah EDA.

---

## 6. Status Pekerjaan

| Fase | Status |
|---|---|
| 0 Housekeeping | `requirements.txt`, Git, dan GitHub privat sudah ada. Struktur folder belum |
| 1 EDA dan data preparation | Ada `program/EDA_Project_Churn.ipynb` (milik pengguna), belum ditinjau ulang bersama AI |
| 2 Modeling | Belum dimulai |
| 3 Evaluasi dan refactor | Belum dimulai |
| 4 Experiment tracking | Belum dimulai |
| 5 Deployment | Belum dimulai |
| 6 Monitoring | Belum dimulai |
| 7 Dokumentasi portofolio | Belum dimulai |

---

## 7. Masalah yang Diketahui

Belum ada.

---

## 8. Roadmap dan Definition of Done

Kerjakan berurutan. Jangan lanjut sebelum fase sekarang memenuhi DoD.

### Fase 0: Housekeeping
- [x] Environment dan `requirements.txt` (bertahap, lihat bagian 9)
- [x] `git init`, `.gitignore`, repo GitHub privat
- [ ] Struktur folder (bagian 10)
- [x] Baca dokumentasi sumber data dan catat apa yang tidak dijelaskan (bagian 2)

**DoD:** environment bisa dibuat ulang dari file, repo bersih, dokumentasi sumber sudah dibaca.

### Fase 1: EDA dan data preparation
- [ ] Periksa kualitas data: tipe, missing value, duplikat, rentang nilai, logika antar kolom
- [ ] Periksa **independensi baris** dan struktur data sebelum memilih strategi validasi
- [ ] Univariat, hubungan fitur dengan target, hubungan antar fitur
- [ ] Setiap keputusan pembersihan dicatat di bagian 4 beserta alasannya
- [ ] Proses pembersihan dapat dijalankan ulang dengan script, bukan hanya dari notebook

**DoD:** satu perintah menghasilkan data bersih yang sama, dan semua keputusan tercatat.

### Fase 2: Modeling
- [ ] Strategi validasi dipilih berdasarkan struktur data, disetujui pengguna
- [ ] Baseline sederhana dan model kandidat
- [ ] Penanganan ketidakseimbangan kelas (jika relevan), dibandingkan
- [ ] Scaler, encoder, dan resampling di dalam fold
- [ ] Pilih model dengan alasan tertulis. Jika selisih masih dalam rentang ketidakpastian, pilih yang paling sederhana

**DoD:** tabel perbandingan model dengan ketidakpastian dan satu model terpilih dengan alasan.

### Fase 3: Evaluasi, interpretasi, dan refactor
- [ ] Pilih threshold berdasarkan skenario biaya (tandai asumsi)
- [ ] Interpretasi model dengan bahasa asosiatif, bukan kausal
- [ ] Analisis error
- [ ] Pindahkan logika ke `src/`, tambah test sederhana
- [ ] Simpan model final sebagai satu Pipeline

**DoD:** pelatihan ulang dapat dijalankan dengan satu perintah.

### Fase 4: Experiment tracking
- [ ] Satu tracking URI dan satu nama experiment
- [ ] Catat params, metrik (dengan ketidakpastian), artefak, tag versi data
- [ ] Daftarkan model terbaik di registry

**DoD:** run dapat dibandingkan di UI tracking dan model terbaik dapat dimuat.

### Fase 5: Deployment (tanpa Docker untuk saat ini)
- [ ] API atau aplikasi demo dengan skema input/output yang divalidasi
- [ ] Lingkungan dikunci dengan `venv` dan `requirements.txt`
- [ ] Test, lint, dan CI
- [ ] Deploy demo ke layanan gratis (Render, Hugging Face Spaces, atau Streamlit Cloud)

**DoD:** demo publik bisa diakses lewat URL dan CI hijau.

### Fase 6: Monitoring
- [ ] Log prediksi, laporan drift terhadap data referensi
- [ ] Aturan retraining dan prosedur rollback
- [ ] Catatan keterbatasan monitoring (label sering datang terlambat)

**DoD:** laporan drift dapat dihasilkan dengan satu perintah.

### Fase 7: Dokumentasi portofolio
- [ ] `README.md` dari template portofolio, termasuk keterbatasan
- [ ] Tabel "kesalahan yang saya temukan dan perbaiki"
- [ ] Ringkasan satu halaman untuk non-teknis

**DoD:** orang lain dapat mengklon, menjalankan, dan memahami hasilnya tanpa bertanya.

---

## 9. Konvensi Teknis

**Kode:** Python 3.10, `pathlib` tanpa path absolut, satu seed global di satu tempat, `snake_case`, satu notebook satu tujuan, logika yang dipakai ulang pindah ke `src/`, jangan menimpa data mentah.

**Requirements bertahap**
- `requirements.txt` hanya berisi library yang dipakai **sekarang**. Library baru masuk di commit yang sama dengan kode yang memakainya, versi dipatok (`==`).
- Verifikasi: `pip install --dry-run -r requirements.txt` (0 paket baru) dan `pip check`.

| Fase | Library yang biasanya ditambahkan |
|---|---|
| 1 EDA (sekarang) | pandas, numpy, scipy, statsmodels, scikit-learn, catboost, matplotlib, seaborn, ipykernel (sesuai import `EDA_Project_Churn.ipynb`) |
| 2 Modeling | `imbalanced-learn` (jika resampling dipakai), opsional `xgboost` / `lightgbm` |
| 3 Evaluasi dan refactor | `shap`; dev: `pytest`, `ruff` |
| 4 Tracking | `mlflow` |
| 5 Deployment | `fastapi`, `uvicorn`, `pydantic`, `streamlit` atau `gradio`. Pecah ke `requirements.txt` (runtime) dan `requirements-dev.txt` karena layanan deploy membaca `requirements.txt` di root |
| 6 Monitoring | opsional `evidently` |

**Git:** commit kecil per langkah, pesan Bahasa Indonesia dengan awalan fase (`fase1: ...`).

---

## 10. Struktur Folder Target

```
project_iranian_churn/
├── PROJECT_GUIDE.md
├── CLAUDE.md
├── README.md
├── requirements.txt
├── .gitignore
├── dataset/          # data mentah, read-only (dilacak, CC BY 4.0)
├── jurnal/           # referensi, diabaikan Git
├── program/          # notebook eksplorasi
├── src/              # logika yang dipakai ulang
├── tests/
└── docs/             # decision log, laporan
```

---

## 11. Log Keputusan dan Pertanyaan Terbuka

| Tanggal | Keputusan / Pertanyaan | Status |
|---|---|---|
| 2026-11-04 | Restart dari nol. Hanya `EDA_Project_Churn.ipynb` dan dataset yang dipertahankan. Pekerjaan sebelumnya diarsipkan di tag Git `arsip-v1` dan **tidak dipakai** | Diputuskan |
| 2026-11-04 | Tujuan portofolio, cakupan EDA sampai monitoring, bahasa Indonesia, notebook lalu `src/` | Diputuskan |
| 2026-11-04 | Tanpa Docker untuk saat ini, deploy lewat `venv` dan layanan gratis | Diputuskan |
| 2026-11-04 | Dataset dilacak di Git (lisensi CC BY 4.0 mengizinkan redistribusi dengan atribusi) | Diputuskan |
| | Penanganan duplikat dan outlier | **Terbuka** |
| | Strategi validasi (setelah memeriksa independensi baris) | **Terbuka** |
| | Metrik evaluasi utama | **Terbuka** |
| | Fitur yang dipakai dan yang dibuang | **Terbuka** |
| | Model kandidat dan penanganan ketidakseimbangan kelas | **Terbuka** |
| | Arti kolom yang belum dijelaskan UCI (bagian 2) | **Terbuka** |
| | Platform demo (Render, Hugging Face Spaces, atau Streamlit Cloud) | **Terbuka** |

---

## 12. Aturan Khusus Project Ini

> Prinsip umum sudah dimuat dari `~/.claude/CLAUDE.md`.

**Wajib:**
- Semua keputusan analisis (pembersihan, fitur, validasi, metrik, model) **ditanyakan ke pengguna dulu**. AI mengusulkan, pengguna memutuskan.
- Temuan hanya ditulis di bagian 3 setelah dihitung dari kode.

**Dilarang:**
- Memakai atau mengutip hasil dari tag Git `arsip-v1` kecuali pengguna memintanya.
