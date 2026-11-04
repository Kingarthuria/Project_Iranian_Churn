# PROJECT GUIDE: Iranian Customer Churn

> File ini adalah **sumber kebenaran** project. Isi hanya fakta yang sudah pasti. Bagian yang belum diketahui dibiarkan kosong.
> Berikan ke AI di awal setiap sesi ("baca PROJECT_GUIDE.md dulu"). Perbarui **Status** dan **Log Keputusan** setiap selesai satu langkah.
> Terakhir diperbarui: 2026-11-04 (audit struktur data disimpan, Fase 1 berjalan)

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
- **Yang tidak dijelaskan UCI:** arti operasional "churn" (berhenti berlangganan, pindah operator, atau tidak aktif), cara `Status` ditentukan, bulan persis pencatatan dalam 9 bulan pertama, cara menghitung `Customer Value`, cara pengambilan sampel acak, dan siapa pembuat datanya.
- Jurnal referensi yang sudah dikumpulkan ada di `jurnal/` (diabaikan Git).

### Data dictionary

> Nama kolom persis seperti header file. Kolom yang artinya belum ada: tanyakan ke pengguna.

| Kolom | Arti menurut UCI |
|---|---|
| `Call  Failure` | belum ada deskripsi, tanyakan ke pengguna |
| `Complains` | biner: 0 = tidak ada komplain, 1 = ada komplain |
| `Subscription  Length` | belum ada deskripsi, tanyakan ke pengguna |
| `Charge  Amount` | ordinal: 0 = jumlah terendah, 9 = tertinggi. Data memuat nilai sampai 10 (lihat bagian 4) |
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
| 1 | Ada 300 duplikat persis (9,52%): 253 baris beraktivitas dan 47 baris beraktivitas nol. Beraktivitas nol berarti `Seconds of Use`, `Frequency of use`, dan `Frequency of SMS` semuanya 0 | `program/analisis_duplikat_v2.ipynb` | 2026-11-04 |
| 2 | Sisa bagi 50 dari posisi baris menjelaskan 99,1% variasi `Seconds of Use` dan 92,7% variasi `Churn`. Pola selisih yang sama diikuti 91,1% nilai `Seconds of Use` | `program/analisis_duplikat_v2.ipynb` | 2026-11-04 |
| 3 | Sebanyak 441 dari 495 baris churn berasal dari 7 kelompok sisa bagi 50 yang seluruh barisnya churn | `program/analisis_duplikat_v2.ipynb` | 2026-11-04 |
| 4 | Semua 365 pasangan kembar beraktivitas berada di kelompok sisa bagi 50 yang sama | `program/analisis_duplikat_v2.ipynb` | 2026-11-04 |
| 5 | ROC-AUC CV acak vs grup per kelompok (audit, bukan skor final): Logistic Regression 0,932 vs 0,841 (0,607–1,000), RandomForest 0,984 vs 0,790 (0,369–0,998) | `program/analisis_duplikat_v2.ipynb` | 2026-11-04 |
| 6 | Semua 59 baris churn dengan `Subscription_Length` di bawah 15,5 berasal dari kelompok audit 49. Tanpa kelompok itu, churn rate grup ini 0,0%, dan baris lainnya 14,6% | `program/analisis_duplikat_v2.ipynb` | 2026-11-04 |
| 7 | Rata-rata MI dari 10 seed: `Seconds_of_Use` 0,1156 (0,1103–0,1192), `Status` 0,1040, `Complains` 0,1023. Urutan `Frequency_of_use` dan `Customer_Value` tidak stabil | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04 |
| 8 | `Customer_Value` sangat bisa dijelaskan oleh `Seconds_of_Use` dan `Frequency_of_SMS` (R-kuadrat 0,957) | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04 |
| 9 | Baris dengan komplain dan berstatus non-aktif punya churn rate 89,3% (133 dari 149). Menurut UCI, kedua kolom berasal dari 9 bulan pertama. Cara `Status` ditentukan dan definisi churn tidak dijelaskan, jadi hubungan ini perlu dibaca hati-hati | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04 |
| 10 | Baris churn hanya memegang 4,4% total `Customer_Value` (median 102,6 berbanding 271,5). Dibaca sebagai porsi relatif, bukan uang | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04 |
| 11 | Gabungan `Complains=1`, `Status=2`, dan `Seconds_of_Use` Rendah mencakup 992 baris (34,8%) dan 90,8% baris churn. Deskriptif, karena sinyal dipilih setelah melihat churn | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04 |
| 12 | Selisih churn rate, IK 95%: komplain 72,8 poin (67,3 sampai 77,3), non-aktif 41,9 poin (38,1 sampai 45,8), `Seconds_of_Use` kuartil terendah 25,3 poin (21,7 sampai 29,1). Eksploratif | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04 |

---

## 4. Keputusan yang Sudah Dikunci

> Keputusan analisis diambil **bersama pengguna**, bukan sepihak oleh AI.

| # | Keputusan | Alasan | Tanggal |
|---|---|---|---|
| 1 | Project dilanjutkan dengan asumsi tiap baris adalah satu pelanggan, walau audit menemukan pola berulang per 50 baris | Keputusan pengguna: mengikuti UCI dan keempat paper di `jurnal/`, dan project ini untuk portofolio pembelajaran | 2026-11-04 |
| 2 | README dan laporan model wajib memuat kalimat keterbatasan di bagian 7, tanpa skor pembanding. Narasi tidak boleh menyebut baris terbukti independen, atau menyebut skor CV acak sebagai performa pada pelanggan baru | Keputusan pengguna, agar asumsi tetap terbuka | 2026-11-04 |
| 3 | Audit disimpan di repo sebagai simpanan (`program/analisis_duplikat_v2.ipynb` dan `ringkasan_temuan/`), bukan fokus project | Keputusan pengguna | 2026-11-04 |
| 4 | Hapus 300 duplikat persis (`keep='first'`), sisa 2.850 baris. Diterapkan di `program/EDA_Project_Churn_v2.ipynb` | Baris identik bisa terpisah ke train dan test, dan menghindari pembobotan ganda. Keterbatasan: hanya menangani duplikat persis, dan 47 baris beraktivitas nol mungkin pelanggan sah | 2026-11-04 |
| 5 | Pertahankan 14 grup dengan fitur identik tetapi label `Churn` berbeda | Sesuai asumsi kerja, baris ini dibaca sebagai pelanggan berbeda dengan hasil berbeda, dan tidak ada dasar untuk memilih label. Keterbatasan: ada sedikit noise pada label | 2026-11-04 |
| 6 | Pertahankan nilai `Charge Amount` = 10 (7 baris setelah deduplikasi), walau dokumentasi UCI menyebut 0–9 | Tidak ada bukti barisnya salah, dan korelasi Spearman dengan `Churn` nyaris sama tanpa baris itu (−0,2478 vs −0,2470). Keterbatasan: kolom ini tidak persis sesuai dokumentasi | 2026-11-04 |
| 7 | Pertahankan 111 baris dengan `Distinct Called Numbers` > `Frequency of use`. Narasi tidak boleh menganggap yang pertama pasti lebih kecil | Arti kedua kolom belum jelas, dan menghapusnya membuang baris dengan churn lebih tinggi (21,6% vs 15,4%). Keterbatasan: sebagian baris mungkin memang tidak konsisten | 2026-11-04 |
| 8 | Pertahankan 85 baris dengan semua aktivitas nol. Penanda `is_zero_activity` bisa dibahas saat feature engineering | Tidak ada bukti barisnya salah, dan churn rate-nya tinggi (51,8% vs 14,5%). Keterbatasan: 26 baris berstatus aktif tanpa aktivitas | 2026-11-04 |
| 9 | Pertahankan 54 baris dengan `Subscription Length` di bawah 9. Tidak ada klaim tentang pelanggan baru, dan fitur per bulan tidak boleh menganggap semua baris mencakup 9 bulan penuh | Satuan kolom belum pasti, nilainya naik bertahap, dan baris ini hampir seluruhnya berasal dari dua kelompok dengan hasil berlawanan | 2026-11-04 |
| 10 | Pakai `Age Group` untuk modeling. `Age` tidak masuk fitur model, tetapi tetap ada di data dan EDA | Keduanya berpasangan satu-satu, dan kode `Age Group` didokumentasikan UCI, sedangkan arti `Age` belum dijelaskan | 2026-11-04 |
| 11 | Semua outlier dipertahankan, tidak ada baris yang dihapus atau nilai yang dipotong | Tidak ada bukti bahwa nilainya salah | 2026-11-04 |
| 12 | Rencana flag dari sel kesimpulan outlier dibatalkan untuk sekarang. Bisa dibahas lagi saat feature engineering, dengan batas dihitung di dalam fold | Batasnya dipilih setelah melihat churn pada seluruh data, dan flag merah pada dasarnya menandai satu kelompok audit | 2026-11-04 |
| 13 | `program/EDA_Project_Churn_v2.ipynb` berdiri sendiri: tidak merujuk file lain dan tidak memuat analisis kelompok posisi. Rujukan UCI dipertahankan. README dan laporan model tetap memuat kalimat keterbatasan (bagian 7) | Keputusan pengguna, mengikuti kesepakatan bahwa tiap baris adalah satu pelanggan. UCI adalah sumber data dan atribusinya diwajibkan lisensi. Keterbatasan: pembaca notebook EDA tidak melihat bukti pola berulang | 2026-11-04 |
| 14 | Pertahankan hampir-duplikat (75 baris beraktivitas dengan pasangan yang berbeda di satu kolom) | Sesuai asumsi kerja, tidak ada dasar untuk menyebutnya duplikat. Keterbatasan: baris sangat mirip masih bisa terpisah ke train dan test | 2026-11-04 |
| 15 | Modeling membandingkan hasil dengan dan tanpa `Status` serta `Complains`. Fitur selain `Age_Binning` dan `Age_Group` belum diputuskan dan diuji saat modeling | Perbandingan ini melihat seberapa besar skor bergantung pada kedua kolom, bukan menguji leakage, karena menurut UCI keduanya mendahului label. Keputusan fitur butuh pengujian performa | 2026-11-04 |
| 16 | Sel validasi kombinasi disederhanakan menjadi saringan eksploratif: minimal 50 baris, minimal 1% data, dan stabil di 20 split | Sel lama punya dua masalah kode, dan p-value-nya tidak menguji kombinasi | 2026-11-04 |
| 17 | Value at Risk memakai 3 sinyal, tanpa `Subscription_Length`. Rekomendasi bisnis ditulis sebagai hipotesis yang perlu diuji | Sesuai keputusan tidak membuat klaim pelanggan baru, dan temuannya hanya asosiasi | 2026-11-04 |
| 18 | Bagian Value at Risk di notebook EDA diganti dengan Pertanyaan Bisnis. Analisis risiko × nilai ditunda ke Fase 3 | Nama lama kurang tepat dan `Customer_Value` tidak punya satuan. Pertanyaan bisnis lebih tepat dijawab dengan besar efek dan rentangnya | 2026-11-04 |
| 19 | Dataset bersih disimpan di folder baru `dataset_clean/`, terpisah dari `dataset/`. Script dan folder dibuat saat pengguna memberi aba-aba | Data mentah tetap read-only | 2026-11-04 |

---

## 5. Metrik Evaluasi

Belum diputuskan. Akan dibahas dengan pengguna setelah EDA.

---

## 6. Status Pekerjaan

| Fase | Status |
|---|---|
| 0 Housekeeping | **Selesai.** `requirements.txt`, Git, GitHub privat, dan struktur folder sudah ada. Environment `ds_env` terverifikasi (dry-run 0 paket baru, `pip check` bersih) |
| 1 EDA dan data preparation | **Berjalan.** Audit duplikat dan struktur data selesai dan disimpan. Peninjauan seluruh `program/EDA_Project_Churn_v2.ipynb` selesai. Script pembersihan satu perintah belum dibuat, jadi DoD Fase 1 belum terpenuhi |
| 2 Modeling | Belum dimulai |
| 3 Evaluasi dan refactor | Belum dimulai |
| 4 Experiment tracking | Belum dimulai |
| 5 Deployment | Belum dimulai |
| 6 Monitoring | Belum dimulai |
| 7 Dokumentasi portofolio | Belum dimulai |

---

## 7. Masalah yang Diketahui

**Independensi baris tidak terjamin.** Lihat temuan 2–5 di bagian 3 dan `ringkasan_temuan/`. Penyebabnya belum diketahui. Keputusan penanganannya ada di bagian 4.

Kalimat keterbatasan yang wajib masuk README dan laporan model:

> Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis.

---

## 8. Roadmap dan Definition of Done

Kerjakan berurutan. Jangan lanjut sebelum fase sekarang memenuhi DoD.

### Fase 0: Housekeeping
- [x] Environment dan `requirements.txt` (bertahap, lihat bagian 9)
- [x] `git init`, `.gitignore`, repo GitHub privat
- [x] Struktur folder (bagian 10)
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
- [ ] Analisis risiko × nilai: peluang churn dari prediksi di luar data latih × `Customer_Value`
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
| 1 EDA (sekarang) | pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib, seaborn, ipykernel (sesuai import `EDA_Project_Churn_v2.ipynb`) |
| 2 Modeling | `imbalanced-learn` (jika resampling dipakai), opsional `xgboost` / `lightgbm` / `catboost` |
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
├── dataset_clean/    # data bersih, dibuat ulang dari script (belum dibuat)
├── jurnal/           # referensi, diabaikan Git
├── program/          # notebook eksplorasi
├── ringkasan_temuan/ # ringkasan temuan bernomor (.md)
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
| 2026-11-04 | Folder `src/`, `tests/`, `docs/` dibuat dengan `README.md` singkat per folder (bukan `.gitkeep`) | Diputuskan |
| 2026-11-04 | `program/EDA_Project_Churn.ipynb` (5,9 MB karena output tersimpan) tidak diubah di Fase 0. Keputusan strip output ditunda ke Fase 1 | Diputuskan |
| 2026-11-04 | Lanjut dengan asumsi tiap baris adalah satu pelanggan, dengan kalimat keterbatasan di hasil akhir. Audit disimpan di repo (bagian 4) | Diputuskan |
| 2026-11-04 | Hapus 300 duplikat persis. Analisis duplikat diperbaiki di notebook v2, notebook asli tidak diubah (bagian 4) | Diputuskan |
| 2026-11-04 | 14 grup dengan fitur identik tetapi label `Churn` berbeda dipertahankan (bagian 4) | Diputuskan |
| 2026-11-04 | Nilai `Charge Amount` = 10 dipertahankan (bagian 4) | Diputuskan |
| 2026-11-04 | 111 baris dengan `Distinct Called Numbers` > `Frequency of use` dipertahankan (bagian 4) | Diputuskan |
| 2026-11-04 | 85 baris dengan semua aktivitas nol dipertahankan (bagian 4) | Diputuskan |
| 2026-11-04 | 54 baris dengan `Subscription Length` di bawah 9 dipertahankan (bagian 4) | Diputuskan |
| 2026-11-04 | `Age Group` dipakai untuk modeling, `Age` tidak masuk fitur model (bagian 4). Fitur lain belum diputuskan | Diputuskan |
| 2026-11-04 | Semua outlier dipertahankan, dan rencana flag dibatalkan untuk sekarang (bagian 4) | Diputuskan |
| 2026-11-04 | Notebook EDA v2 berdiri sendiri, analisis kelompok posisi hanya ada di notebook audit (bagian 4) | Diputuskan |
| 2026-11-04 | Sitasi empat paper di `jurnal/` ditambahkan ke sel 4 notebook EDA v2 sebagai bacaan terkait, bukan dasar analisis | Diputuskan |
| 2026-11-04 | Sitasi Jafari-Marandi dkk. (2020) dihapus dari notebook EDA v2, karena halaman UCI tidak mencantumkan nama pembuat. Sumber dataset memakai sitasi resmi UCI | Diputuskan |
| 2026-11-04 | Hampir-duplikat dipertahankan (bagian 4) | Diputuskan |
| 2026-11-04 | MI dilaporkan dengan rata-rata 10 seed dan rentang (bagian 3) | Diputuskan |
| 2026-11-04 | Koreksi: `Status` dan `Complains` tidak disebut risiko leakage, karena menurut UCI semua fitur berasal dari 9 bulan pertama. Perbandingan dengan dan tanpa keduanya tetap dilakukan untuk melihat ketergantungan skor (bagian 4) | Diputuskan |
| 2026-11-04 | Klaim lama seperti "pelanggan baru" dan "loyal" dihapus dari notebook EDA v2. Sel validasi disederhanakan dan Value at Risk memakai 3 sinyal (bagian 4) | Diputuskan |
| 2026-11-04 | Value at Risk diganti dengan Pertanyaan Bisnis, dan dataset bersih nanti di `dataset_clean/` (bagian 4) | Diputuskan |
| | Riwayat Git masih memuat nama tampilan dan `userId` Google dari metadata Colab. Dibersihkan sebelum repo dipublikasikan | **Terbuka** |
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
