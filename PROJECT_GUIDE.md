# PROJECT GUIDE: Iranian Customer Churn

> File ini adalah **sumber kebenaran** proyek. Berikan ke AI di awal setiap sesi
> ("baca PROJECT_GUIDE.md dulu"). Perbarui bagian **Status** dan **Log Keputusan** setiap selesai satu fase.
> Terakhir diperbarui: 2026-11-04

---

## 1. Ringkasan Proyek

| Item | Isi |
|---|---|
| Tujuan | **Portofolio / pembelajaran**: menunjukkan alur data science dan MLOps end-to-end yang rapi, jujur, dan bisa dijelaskan |
| Masalah | Memprediksi pelanggan telekomunikasi Iran yang akan churn |
| Dataset | `dataset/Customer Churn.csv` (UCI *Iranian Churn Dataset*, Jafari-Marandi dkk., 2020) |
| Target | `Churn` (1 = berhenti, 0 = bertahan) |
| Cakupan | EDA, cleaning, feature engineering, modeling, MLflow, deployment, monitoring |
| Pekerjaan lama | **Dilanjutkan dan diperbaiki**, bukan dimulai ulang |
| Bahasa | Penjelasan dan komentar dalam Bahasa Indonesia, nama variabel dan fungsi dalam Bahasa Inggris |

**Prinsip utama proyek:** kejujuran analisis lebih penting daripada angka yang bagus.
Untuk portofolio, model dengan AUC 0,79 yang divalidasi benar lebih bernilai daripada AUC 0,98 yang bocor.

---

## 2. Dataset

- 3.150 baris, 14 kolom, tanpa missing value, 300 baris duplikat persis. Setelah dedup: **2.850 baris**.
- Churn rate: 15,7% (mentah), **15,65%** (setelah dedup). Kelas tidak seimbang.
- Nama kolom mentah mengandung **spasi ganda** (`Call  Failure`, `Subscription  Length`, `Charge  Amount`).
  Versi bersih memakai satu underscore (`Call_Failure`). Jangan gunakan `col.replace(' ', '_')` begitu saja
  karena menghasilkan `Call__Failure` (dua underscore).

### Data dictionary

| Kolom (bersih) | Tipe | Arti | Catatan |
|---|---|---|---|
| `Call_Failure` | int | Jumlah panggilan gagal | 0–36 |
| `Complains` | biner | 1 = pernah komplain | Risiko leakage, lihat bagian 4 |
| `Subscription_Length` | int | Lama berlangganan (bulan) | 3–47. Hubungan dengan churn **tidak monoton** |
| `Charge_Amount` | ordinal | Tingkat tagihan, 0 = terendah | 0–10. Efeknya hanya efek `Status` |
| `Seconds_of_Use` | int | Total durasi panggilan (detik) | Skewed, pertimbangkan `log1p` |
| `Frequency_of_use` | int | Jumlah panggilan | |
| `Frequency_of_SMS` | int | Jumlah SMS | |
| `Distinct_Called_Numbers` | int | Jumlah nomor berbeda yang dihubungi | |
| `Age_Group` | ordinal | Kelompok usia 1–5 | Efek **U-terbalik**, jangan di-drop |
| `Age` | int | Usia (15, 25, 30, 45, 55) | Duplikat 1:1 dengan `Age_Group`, **drop** |
| `Tariff_Plan` | biner | 1 = pay-as-you-go, 2 = contractual | Efek kecil, terkonfusi `Status` |
| `Status` | biner | 1 = aktif, 2 = non-aktif | Risiko leakage, lihat bagian 4 |
| `Customer_Value` | float | Nilai pelanggan terhitung | Fungsi dari fitur usage (R² ≈ 0,96), **drop** |
| `Churn` | biner | **Target** | |

### Kolom tambahan di `program/artifacts/Customer_Churn_clean.csv` (19 kolom)

`orig_pos`, `seed`, `seed_churn`, `fold_r0`, `fold_r1`, `fold_r2` adalah **kolom bantu, BUKAN fitur**.
`seed_churn` memuat label tingkat profil sehingga memakainya sebagai fitur berarti bocor total.

---

## 3. Temuan Kunci dari EDA (v2, `Real_EDA.ipynb`)

Ini fakta yang sudah dihitung dan jadi dasar semua keputusan modeling.

1. **Data bukan sampel acak independen.** Data berasal dari sekitar **50 profil dasar** (`seed = orig_pos mod 50`) yang digandakan dengan sedikit jitter.
   - ICC churn = 0,923
   - **Ukuran sampel efektif ≈ 54**, bukan 2.850
   - Hanya 8 dari 50 profil yang churn
2. **Konsekuensi:** split acak per baris membocorkan "saudara kandung" baris ke test set. Metrik jadi terlalu optimis.
3. **Sinyal yang kuat:** `Complains = 1` dan `Status = 2`. Sinyal lain lemah atau tidak terbukti setelah koreksi.
4. **Baseline yang harus dikalahkan:** `Status + Complains + Seconds_of_Use` dengan AUC group-CV **0,828**.
5. **Semua fitur bersama** hanya menghasilkan AUC group-CV 0,79 (bukan 0,98), dan tanpa `Status` turun ke 0,76.
6. Ada **red flag** yang belum diselesaikan: pelanggan dengan pemakaian tinggi churn tepat 0%. Label `Churn` mungkin lebih "mudah" daripada churn nyata.
7. Churner bernilai rendah: 15,6% pelanggan tetapi hanya ~4,4% total `Customer_Value`. Ini mengubah cerita bisnis.

Sumber detail: `program/artifacts/feature_spec.json`, `program/Real_EDA.ipynb`, `kelemahan/Review_Kelemahan_EDA.docx`.

---

## 4. Keputusan yang Sudah Dikunci (jangan dilanggar tanpa alasan tertulis)

| # | Keputusan | Alasan |
|---|---|---|
| D1 | Pakai data **setelah dedup** (2.850 baris) | 300 salinan persis adalah replikasi baris |
| D2 | **Drop** `Age` dan `Customer_Value` | Redundan / turunan eksak fitur lain |
| D3 | Pertahankan `Age_Group`, `Subscription_Length`, `Frequency_of_use` | Ablasi: membuang ketiganya menurunkan AUC |
| D4 | **Validasi wajib** `StratifiedGroupKFold(n_splits=5, shuffle=True)`, grup = `seed`, 3 ulangan | Mencegah kontaminasi antar baris sejenis |
| D5 | **Dilarang:** random `train_test_split` per baris, KFold biasa, random holdout | Metrik jadi menyesatkan |
| D6 | Ketidakpastian dihitung dengan **bootstrap per profil**, bukan per baris | Baris tidak independen |
| D7 | Bahasa hasil: **asosiatif, bukan kausal** | Tidak ada dimensi waktu atau eksperimen |
| D8 | `Status` dan `Complains` ditandai **berisiko leakage**; selalu laporkan model **dengan dan tanpa** keduanya | Hasil dengan keduanya belum tentu berguna untuk prediksi dini |
| D9 | Seed global `42` | Reproduksibilitas |
| D10 | Preprocessing (scaler dll.) **di dalam Pipeline**, di-fit hanya pada data train per fold | Mencegah leakage |
| D11 | Resampling (SMOTE) hanya boleh **di dalam fold**, dan harus dibandingkan dengan `class_weight`. Perlu waspada karena SMOTE menginterpolasi antar baris yang sudah saling tiruan | Interpolasi pada klaster bisa menggelembungkan skor |

---

## 5. Metrik Evaluasi (usulan, belum final)

Churn hanya 15,7%, jadi **accuracy tidak boleh jadi metrik utama**.

| Metrik | Peran | Kelebihan | Kekurangan |
|---|---|---|---|
| **PR-AUC** | **Utama (usulan)** | Tidak bergantung threshold, peka pada kelas minoritas | Sulit dijelaskan ke non-teknis |
| **Recall@top-K** (misal top 10% / 20% skor) | **Metrik bisnis (usulan)** | Langsung terjemah ke anggaran kampanye retensi | Bergantung pilihan K |
| ROC-AUC | Pendamping | Standar, bisa dibandingkan dengan literatur | Optimis pada data imbalanced |
| Recall / F1 kelas churn | Pelaporan di threshold terpilih | Mudah dipahami | Bergantung threshold |
| Accuracy | **Hanya informasi** | - | Model "tebak semua bertahan" sudah 84% |

Ini selaras dengan `cv_protocol.metrics` di `feature_spec.json` (PR-AUC, ROC-AUC, recall@top-K).
**Keputusan final dicatat di bagian 11.**

Aturan pelaporan: selalu sertakan baseline (`DummyClassifier` dan model 3 fitur di atas) dan **rentang ketidakpastian** (bootstrap per profil).

---

## 6. Status Pekerjaan Saat Ini

```
A:\project_iranian_churn\
├── PROJECT_GUIDE.md              <- file ini
├── dataset\Customer Churn.csv    <- data mentah, JANGAN DIUBAH
├── kelemahan\Review_Kelemahan_EDA.docx   <- review kelemahan EDA v1
├── mlflow.db                     <- backend MLflow (SQLite)
└── program\
    ├── EDA_Project_Churn.ipynb   <- EDA v1 (usang, ada banyak klaim keliru)
    ├── Real_EDA.ipynb            <- EDA v2 (acuan, sadar klaster)
    ├── model.ipynb               <- modeling v1 (PERLU DIPERBAIKI)
    └── artifacts\
        ├── Customer_Churn_clean.csv   <- 2.850 baris + kolom bantu
        └── feature_spec.json          <- kontrak antara EDA dan modeling
```

| Fase | Status |
|---|---|
| EDA v1 | Usang, dipertahankan hanya sebagai riwayat |
| EDA v2 + serah-terima | Selesai (perlu pemeriksaan red flag label) |
| Modeling | **Ada, tetapi tidak mengikuti keputusan D2, D4, D5, D10.** Lihat bagian 7 |
| MLflow | Berjalan, tetapi konfigurasi tidak konsisten |
| Deployment dan monitoring | Belum dimulai |

---

## 7. Masalah Diketahui di `model.ipynb` (harus diperbaiki di Fase 2)

| # | Masalah | Dampak | Perbaikan |
|---|---|---|---|
| M1 | Memakai `train_test_split(test_size=0.2, stratify=y)` per baris | Data bocor antar baris saudara. Skor AUC 0,92–0,98 terlalu optimis | Ganti ke `StratifiedGroupKFold` dengan grup `seed` (D4, D5) |
| M2 | `Customer_Value` dipakai sebagai fitur | Turunan eksak dari fitur lain | Hapus (D2) |
| M3 | Membaca CSV mentah dan menulis ulang dedup serta rename sendiri | Tidak konsisten dengan data bersih. `Call__Failure` (dua underscore) | Baca `program/artifacts/Customer_Churn_clean.csv` |
| M4 | Fitur dipilih lewat "MI tinggi" dari EDA v1 | EDA v1 punya klaim keliru | Ikuti `feature_spec.json` |
| M5 | SMOTE tanpa memperhatikan klaster | Skor bisa menggelembung | Terapkan di dalam fold, bandingkan dengan `class_weight` (D11) |
| M6 | Tracking URI tidak konsisten: `file:///.../mlruns`, output menampilkan `file:./mlruns`, sedangkan ada `mlflow.db` | Run tersebar di dua tempat | Satukan ke `sqlite:///mlflow.db` (bagian 9) |
| M7 | Path absolut `A:\project_iranian_churn\...` di-hardcode | Tidak portabel, tidak bisa dijalankan di komputer lain atau layanan deploy | Pakai `pathlib` relatif terhadap root proyek |
| M8 | Tidak ada baseline, tidak ada ketidakpastian | Angka tidak bisa ditafsirkan | Tambah `DummyClassifier`, baseline 3 fitur, bootstrap per profil |
| M9 | Run lama (10 run) bercampur dengan hasil bocor | Membingungkan | Beri tag `legacy_leaky` atau pindah ke experiment baru |
| M10 | Notebook dipakai sebagai satu-satunya tempat logika | Sulit di-deploy dan di-test | Pindahkan logika ke modul `src/` (Fase 3) |

---

## 8. Roadmap dan Definition of Done

Kerjakan **berurutan**. Jangan lanjut ke fase berikutnya sebelum fase sekarang memenuhi DoD.

### Fase 0: Housekeeping
- [ ] Buat `requirements.txt` / `environment.yml` (Python 3.10, mlflow 3.11, scikit-learn 1.7.2, imbalanced-learn 0.14.1)
- [ ] `git init`, buat `.gitignore` (`mlruns/`, `*.db`, `.env`, `__pycache__/`)
- [ ] Susun folder target (bagian 10)
- [ ] Selesaikan red flag label `Churn`: baca dokumentasi UCI, tulis hasilnya di Log Keputusan

**DoD:** environment bisa dibuat ulang dari file, repo bersih, red flag terdokumentasi.

### Fase 1: EDA dan Data Preparation (sebagian besar selesai)
- [ ] Verifikasi ulang angka kunci di bagian 3 langsung dari CSV
- [ ] Pastikan `Customer_Churn_clean.csv` bisa dibuat ulang dengan script (`src/data/prepare.py`), bukan hanya dari notebook
- [ ] Tandai `EDA_Project_Churn.ipynb` sebagai usang di sel pertama

**DoD:** satu perintah menghasilkan data bersih dan `feature_spec.json` yang identik.

### Fase 2: Modeling (perbaikan `model.ipynb`)
- [ ] Buat notebook baru `program/model_v2.ipynb` (jangan timpa v1)
- [ ] Baca data bersih, buang kolom bantu dari fitur
- [ ] Bangun **kerangka evaluasi** satu fungsi: `StratifiedGroupKFold` × 3 ulangan, hitung PR-AUC, ROC-AUC, recall@top-K, bootstrap per profil
- [ ] Baseline: `DummyClassifier` → Logistic Regression 3 fitur (target AUC ≈ 0,828)
- [ ] Kandidat: Logistic Regression, Random Forest, HistGradientBoosting, (opsional) XGBoost/LightGBM
- [ ] Tiga skenario fitur wajib: (a) semua fitur sah, (b) tanpa `Complains`, (c) tanpa `Status` dan `Complains`
- [ ] Penanganan imbalance: `none` vs `class_weight` vs SMOTE di dalam fold
- [ ] Tuning dengan nested/grouped CV, **bukan** menyetel di test fold yang sama
- [ ] Pilih model dengan alasan tertulis. Jika selisih antar model masih dalam rentang ketidakpastian, pilih yang paling sederhana

**DoD:** tabel perbandingan model dengan rentang ketidakpastian, tidak ada pelanggaran D4/D5/D10, dan satu model terpilih dengan alasan.

### Fase 3: Evaluasi, Interpretasi, dan Refactor
- [ ] Pilih threshold berdasarkan skenario biaya (biaya kontak, peluang retensi berhasil, nilai pelanggan). Tandai sebagai **asumsi**, bukan data
- [ ] Kurva PR, lift/gain, calibration
- [ ] Interpretasi: koefisien (LR), permutation importance, SHAP. Bahasa asosiatif (D7)
- [ ] Analisis error: profil mana yang salah diprediksi
- [ ] Pindahkan logika ke `src/` (`data`, `features`, `train`, `evaluate`, `predict`) dengan test sederhana (`pytest`)
- [ ] Simpan model final sebagai **satu Pipeline sklearn** (preprocessing + model)

**DoD:** `python -m src.train` melatih ulang dan mencatat ke MLflow. Pipeline bisa dimuat dan memprediksi satu baris contoh.

### Fase 4: Experiment Tracking (MLflow)
- [ ] Tracking URI tunggal: `sqlite:///mlflow.db`, artifact di `./mlartifacts`
- [ ] Satu experiment: `iranian_churn_v2`
- [ ] Setiap run mencatat: params (model, fitur, handling, seed), metrik (mean ± std per metrik), artifact (feature_spec, plot, confusion matrix), tag (`stage`, `leakage_scenario`, `data_version`)
- [ ] Hash data (`sha256` dari CSV bersih) dicatat sebagai tag
- [ ] Daftarkan model terbaik di **Model Registry**, alias `champion`
- [ ] Beri tag `legacy_leaky` pada run lama

**DoD:** `mlflow ui --backend-store-uri sqlite:///mlflow.db` menampilkan run baru yang bisa dibandingkan, dan model `champion` bisa dimuat dengan `models:/iranian_churn@champion`.

### Fase 5: Deployment
- [ ] API FastAPI: `POST /predict` (satu pelanggan), `POST /predict/batch`, `GET /health`, `GET /model-info`
- [ ] Skema input/output dengan **Pydantic** (rentang valid sesuai data dictionary)
- [ ] Memuat model dari MLflow Registry atau file artefak
- [ ] Lingkungan terkunci dengan `venv` dan `requirements.txt` (versi dipatok), tanpa Docker untuk saat ini
- [ ] Test API (`pytest` + `TestClient`)
- [ ] CI GitHub Actions: lint (`ruff`) dan `pytest`
- [ ] Deploy demo ke layanan gratis tanpa Docker: **Render** (API FastAPI) dan/atau **Hugging Face Spaces** (antarmuka Streamlit/Gradio yang memanggil model)

**DoD:** `uvicorn api.main:app` di lingkungan bersih lalu `curl` ke `/predict` mengembalikan probabilitas churn, dan demo publik bisa diakses lewat URL. CI hijau.

> Docker bisa ditambahkan nanti sebagai peningkatan opsional, bukan syarat.

### Fase 6: Monitoring
- [ ] Log setiap prediksi (input, skor, versi model, timestamp)
- [ ] Laporan **data drift** (Evidently atau PSI/KS buatan sendiri) terhadap data referensi
- [ ] Simulasi drift pada data sintetis untuk demo
- [ ] Aturan retraining (pemicu, siapa yang menyetujui) dan prosedur rollback ditulis di README
- [ ] Catatan keterbatasan: label churn baru diketahui belakangan, jadi monitoring performa bergantung pada feedback tertunda

**DoD:** satu perintah menghasilkan laporan drift HTML, dan dokumen retraining tersedia.

### Fase 7: Dokumentasi Portofolio
- [ ] `README.md`: masalah, temuan, cara menjalankan, hasil, **keterbatasan** (struktur klaster, sampel efektif ≈ 54, risiko leakage)
- [ ] Diagram arsitektur
- [ ] Ringkasan 1 halaman untuk non-teknis, termasuk temuan bahwa churner bernilai rendah
- [ ] Tabel "kesalahan yang saya temukan dan perbaiki" (EDA v1 → v2, model v1 → v2). Ini nilai jual portofolio

**DoD:** orang lain bisa mengklon repo, menjalankan, dan memahami hasilnya tanpa bertanya.

---

## 9. Konvensi Teknis

**Kode**
- Python 3.10, `pathlib` untuk semua path, tidak ada path absolut
- Seed global `SEED = 42` dari satu tempat (`src/config.py`)
- Fungsi punya type hint dan docstring singkat
- Satu notebook = satu tujuan. Logika yang dipakai ulang pindah ke `src/`
- Jangan pernah menimpa `dataset/` dan `program/artifacts/` secara diam-diam. Hasil baru diberi versi (`..._v2`)

**MLflow**
```python
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("iranian_churn_v2")
```
Penamaan run: `{model}__{skenario_fitur}__{handling}`, contoh `hgb__no_status_complains__class_weight`.

**Penamaan fitur:** `snake_case` satu underscore: `Seconds_of_Use`, bukan `Seconds__of__Use`.

**Git:** commit kecil per langkah. Pesan: `fase2: tambah group-CV evaluator`.

---

## 10. Struktur Folder Target

```
project_iranian_churn/
├── PROJECT_GUIDE.md
├── README.md
├── requirements.txt
├── .gitignore
├── dataset/                 # mentah, read-only
├── program/                 # notebook eksplorasi
│   ├── Real_EDA.ipynb
│   ├── model_v2.ipynb
│   └── artifacts/
├── src/
│   ├── config.py
│   ├── data/prepare.py
│   ├── features/build.py
│   ├── models/train.py, evaluate.py, predict.py
│   └── monitoring/drift.py
├── api/main.py, schemas.py
├── tests/
├── .github/workflows/ci.yml
└── docs/                    # diagram, ringkasan, keputusan
```

---

## 11. Log Keputusan dan Pertanyaan Terbuka

| Tanggal | Keputusan / Pertanyaan | Status |
|---|---|---|
| 2026-11-04 | Tujuan: portofolio. Cakupan: EDA sampai monitoring. Lanjutkan pekerjaan lama | Diputuskan |
| 2026-11-04 | Metrik utama: PR-AUC + recall@top-K (usulan, lihat bagian 5) | **Menunggu persetujuan** |
| 2026-11-04 | Apakah definisi label `Churn` di dokumentasi UCI menjelaskan pola "pemakaian tinggi = 0% churn"? | **Terbuka** |
| 2026-11-04 | Apakah model dengan `Status`/`Complains` boleh jadi model final, atau model "tanpa keduanya" yang dideploy? | **Terbuka** |
| 2026-11-04 | Nilai K untuk recall@top-K (10%, 20%, atau 40%)? | **Terbuka** |
| 2026-11-04 | Docker **tidak dipakai untuk saat ini**; deploy lewat `venv` + layanan gratis (Render / Hugging Face Spaces) | Diputuskan |
| 2026-11-04 | Pilih Render, Hugging Face Spaces, atau keduanya untuk demo? | **Terbuka** |

---

## 12. Aturan untuk AI Asisten

**Wajib**
1. Baca file ini sebelum mengerjakan apa pun. Jika permintaan bertentangan dengan bagian 4, **beri tahu saya dulu**.
2. Jelaskan asumsi sebelum menulis kode, kerjakan **satu langkah kecil** per permintaan.
3. Setelah setiap langkah data, tampilkan pengecekan: jumlah baris, distribusi `Churn`, bentuk fitur.
4. Laporkan hasil apa adanya. Kalau skor terlihat terlalu bagus (misal AUC > 0,9), **curigai leakage lebih dulu**.
5. Setiap angka di narasi harus dihitung dari kode, bukan disalin tangan.
6. Tulis ringkasan keputusan baru ke bagian 11 setelah disetujui.

**Dilarang**
- Memakai `seed`, `seed_churn`, `orig_pos`, `fold_*`, `Age`, `Customer_Value` sebagai fitur
- Random split per baris, atau `fit` scaler/SMOTE di seluruh data sebelum split
- Menimpa file di `dataset/` atau artefak lama tanpa konfirmasi
- Klaim kausal ("menyebabkan", "intervensi paling efektif")
- Menginstal library baru tanpa memberi tahu saya
- Menyimpan kredensial atau path absolut di kode

**Template prompt per fase**
```
Baca PROJECT_GUIDE.md. Kita sedang di Fase [N], langkah: [checklist item].
Input: [file]. Keluaran yang diharapkan: [file/tabel].
Sebelum menulis kode, sebutkan asumsimu dan risiko leakage yang relevan.
Setelah selesai, tunjukkan cara saya memverifikasi hasilnya.
```
