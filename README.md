# Pelanggan Mana yang Perlu Dihubungi? Prediksi churn pelanggan telekomunikasi

Proyek data science end-to-end pada dataset UCI *Iranian Churn*. Pertanyaannya sederhana: **pelanggan mana yang sebaiknya dihubungi supaya tidak berhenti berlangganan?** Proyek ini menjawabnya dengan model yang divalidasi dengan jujur, lalu membawanya sampai ke demo publik, CI, experiment tracking, dan monitoring.

> **Mulai dari sini**
> - **Ingin mencoba?** Buka [demo](https://churn-risk-priority.streamlit.app/). Pilih contoh pelanggan, dan demo menjelaskan apakah pelanggan itu perlu dihubungi dan kenapa. Tersedia dalam Bahasa Indonesia dan Inggris, dan isian tidak disimpan.
> - **Bukan orang teknis?** Baca [ringkasan satu halaman](docs/ringkasan_non_teknis.md): masalahnya, temuannya, cara memakainya, dan letak file penting.
> - **Rekruter atau pembaca teknis?** Lanjutkan membaca README ini. Semua keputusan dan alasannya ada di [PROJECT_GUIDE.md](PROJECT_GUIDE.md).

## Ringkasan hasil

- **Model:** XGBoost dengan 12 fitur. PR-AUC pada CV acak data latih **0,931 (rentang 10 ulangan 0,920–0,939)**, dibanding baseline churn rate **0,157**. Angka ini mengukur kemampuan mengurutkan pelanggan di data yang tersedia, **bukan performa pada pelanggan baru** (lihat [Keterbatasan](#keterbatasan)).
- **Temuan bisnis:** komplain adalah sinyal terkuat. Churn rate pelanggan yang pernah komplain 72,8 poin persen lebih tinggi daripada yang tidak (IK 95%: 67,3–77,3). Hubungan ini asosiatif, bukan sebab-akibat.
- **Temuan data:** audit menemukan **pola yang berulang setiap 50 baris** di file data. Karena itu skor model dibaca dengan curiga, dan keterbatasan ini ditulis terbuka di semua hasil.

## Konteks bisnis

Menghubungi pelanggan yang berisiko churn butuh biaya, tetapi melewatkan pelanggan yang akhirnya churn juga merugikan. Proyek ini membantu tim retensi memutuskan **siapa yang dihubungi lebih dulu**:

1. Model memberi **skor risiko** untuk tiap pelanggan.
2. Pelanggan disarankan dihubungi jika skornya mencapai **skor minimal untuk dihubungi**. Skor minimal dipilih dari **rasio biaya** antara churn terlewat dan salah hubungi (1:2, 1:5, atau 1:10), yang merupakan asumsi dan bisa diatur.
3. Risiko digabung dengan **nilai pelanggan** menjadi empat segmen prioritas, dan tiap segmen punya usulan tindakan untuk siklus 12 bulan berikutnya.

Semua tindakan di demo adalah **hipotesis yang perlu diuji**, misalnya dengan kelompok pembanding yang tidak dihubungi.

## Data

| Item | Isi |
|---|---|
| Sumber | *Iranian Churn [Dataset]. (2020). UCI Machine Learning Repository.* https://doi.org/10.24432/C5JW3Z |
| Lisensi | CC BY 4.0. File mentah disertakan di `dataset/` |
| Ukuran | 3.150 baris mentah. Setelah 300 duplikat persis dihapus, tersisa 2.850 baris |
| Satu baris | Satu pelanggan, menurut dokumentasi UCI. Lihat keterbatasan soal pola berulang |
| Periode | Fitur adalah agregat 9 bulan pertama, dan status churn dicatat di akhir bulan ke-12 |
| Target | `Churn` (1 = churn), 15,65% dari data bersih |
| Yang tidak dijelaskan UCI | Definisi operasional churn, cara `Status` ditentukan, rumus `Customer Value`, dan arti kolom `Age` |

## Metodologi

1. **Pembersihan.** Hanya 300 duplikat persis yang dihapus. Outlier, nilai di luar dokumentasi (`Charge Amount` = 10), dan baris yang terlihat janggal dipertahankan, karena tidak ada bukti nilainya salah. Setiap keputusan dicatat beserta alasannya.
2. **Audit struktur data.** Sebelum memilih cara validasi, baris diperiksa apakah benar-benar saling bebas. Hasilnya: sisa bagi 50 dari posisi baris menjelaskan 99,1% variasi `Seconds of Use`, dan semua 365 pasangan baris kembar yang beraktivitas berada di kelompok posisi yang sama.
3. **Validasi.** Data dibagi 80:20 secara acak berstrata. Model dipilih dengan CV acak berstrata 5-fold yang diulang 10 kali pada data latih. CV per kelompok posisi dijalankan sebagai cek internal. Data uji dinilai sekali di akhir, setelah model dikunci.
4. **Model.** Enam kandidat (Logistic Regression, Decision Tree, KNN, SVM RBF, RandomForest, XGBoost) dibandingkan dengan `DummyClassifier`. Penyetelan 60 kombinasi dan pembobotan kelas tidak jelas lebih baik, jadi dipakai **XGBoost parameter default**.
5. **Metrik.** PR-AUC sebagai metrik utama, karena churn hanya sekitar 16% dan yang dicari adalah urutan pelanggan churn. ROC-AUC menjadi pendukung. Accuracy tidak dipakai.
6. **Skor minimal dari biaya.** Untuk tiap rasio biaya, dipilih skor minimal dengan total biaya terendah pada prediksi out-of-fold data latih, diulang 10 kali, lalu diambil mediannya. Hasilnya 0,23 untuk 1:2, 0,06 untuk 1:5, dan 0,045 untuk 1:10.

## Hasil

PR-AUC pada CV acak data latih (2.280 baris, 12 fitur, parameter default):

| Model | PR-AUC (rentang 10 ulangan) |
|---|---|
| **XGBoost** (terpilih) | **0,931 (0,920–0,939)** |
| RandomForest | 0,914 (0,908–0,919) |
| Logistic Regression | 0,773 (0,768–0,776) |
| `DummyClassifier` (baseline) | 0,157 |

- **Ketergantungan pada dua kolom.** Tanpa `Status` dan `Complains`, PR-AUC XGBoost turun 0,045 pada CV acak. Keduanya tetap dipakai, karena menurut UCI keduanya berasal dari 9 bulan pertama, sebelum label dicatat.
- **Fitur yang paling diandalkan model** (permutation importance): kelompok pemakaian (detik panggilan, jumlah panggilan, SMS, panggilan berbeda, dan nilai terhitung), lalu `Complains`, `Frequency_of_use`, `Subscription_Length`, `Status`, dan `Call_Failure`. Ini pola yang dipakai model, **bukan sebab churn**.
- **Data uji** (570 baris, dinilai sekali) memberi skor yang lebih tinggi daripada CV, dan karena itu juga dibaca dengan curiga, bukan sebagai bukti model bekerja pada pelanggan baru.

## Dari notebook ke produk

| Bagian | Isi | Perintah |
|---|---|---|
| Kode yang dipakai ulang | `src/`: data, model, skor minimal, pelatihan, dan prediksi demo | `python -X utf8 -m src.train` |
| Test dan lint | 80 test pytest yang mencocokkan angka dengan notebook, ditambah `ruff` | `python -X utf8 -m pytest` |
| CI | GitHub Actions di Linux dengan Python 3.12 untuk setiap push dan pull request | otomatis |
| Experiment tracking | MLflow lokal: 4 run inti dan registry dengan alias `champion` | `python -X utf8 -m src.track` |
| Demo | Streamlit Community Cloud, dua bahasa, empat tab: hasil dan rekomendasi, detail teknis, cara kerja model, serta keterbatasan | [churn-risk-priority.streamlit.app](https://churn-risk-priority.streamlit.app/) |
| Monitoring | Laporan drift (PSI per fitur dan uji statistik) dari batch simulasi, beserta aturan retraining dan rollback ([docs/monitoring.md](docs/monitoring.md)) | `python -X utf8 -m src.monitor` |

## Kesalahan yang saya temukan dan perbaiki

| Masalah | Bagaimana ketahuan | Perbaikan |
|---|---|---|
| 300 baris duplikat persis (9,52%) bisa jatuh ke data latih dan data uji sekaligus | Pemeriksaan duplikat di EDA | Dihapus, dan baris lain yang mirip tetap dicatat sebagai keterbatasan |
| Baris di file data tidak saling bebas: polanya berulang setiap 50 baris | Audit independensi baris sebelum memilih cara validasi | Ditulis sebagai keterbatasan utama, dan CV per kelompok dijalankan sebagai cek internal |
| `Status` dan `Complains` sempat dicurigai sebagai kebocoran label | Dokumentasi UCI dibaca ulang: semua fitur berasal dari 9 bulan pertama | Tidak lagi disebut kebocoran, tetapi model tetap dibandingkan dengan dan tanpa keduanya |
| Skor gabungan out-of-fold memberi angka yang menyesatkan pada CV per kelompok | `DummyClassifier`, yang seharusnya sekitar 0,5, mendapat ROC-AUC 0,301 | Skor dihitung per fold lalu dirata-ratakan |
| Arti beberapa kolom sempat ditafsirkan dari jurnal | Dibandingkan dengan halaman UCI. Sebagian tafsiran jurnal ternyata saling bertentangan | Data dictionary disesuaikan dengan UCI, dan hal yang tidak dijelaskan ditulis apa adanya |
| Library `shap` gagal membaca model XGBoost 3 | Error saat interpretasi | Memakai SHAP bawaan XGBoost (`pred_contribs`), tanpa library tambahan |
| Demo publik butuh lebih dari 2 menit saat pertama dibuka | Diukur langsung di browser | Server melaporkan 16 inti CPU. Setelah XGBoost dibatasi ke 1 thread, log mencatat model siap dalam 1,0 detik, dengan skor yang persis sama |

## Keterbatasan

> Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Namun audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis.

- Semua skor berasal dari data dengan pola yang sama, jadi **tidak mewakili performa pada pelanggan baru**.
- Rasio biaya dan tindakan per segmen adalah **asumsi dan hipotesis**, bukan data perusahaan.
- `Customer Value` disebut **nilai terhitung**, bukan uang, karena rumusnya tidak dijelaskan UCI.
- Skor risiko dipakai untuk mengurutkan pelanggan dan **bukan peluang yang terkalibrasi**.
- Monitoring memakai **batch simulasi**, karena dataset hanya punya satu periode.
- Semua temuan bersifat **asosiatif**.

## Cara menjalankan

Butuh Python 3.12. Saya memakai env conda `ds_env312`, tetapi `venv` biasa juga bisa:

```bash
conda create -n ds_env312 python=3.12
conda activate ds_env312
pip install -r requirements-dev.txt
```

Lalu dari root project:

```bash
python -X utf8 src/clean_data.py                                  # data bersih ke dataset_clean/
streamlit run streamlit_app.py --server.address 127.0.0.1        # demo lokal
python -X utf8 -m pytest                                          # test
```

`requirements.txt` hanya berisi library demo, dan `requirements-dev.txt` menambah library notebook, test, lint, dan MLflow. Panduan perintah lain ada di [src/README.md](src/README.md), dan urutan notebook ada di [program/README.md](program/README.md).

## Struktur repo

```
.
├── streamlit_app.py     # demo
├── src/                 # logika yang dipakai ulang, pelatihan, tracking, monitoring
├── tests/               # test pytest
├── program/             # notebook eksplorasi dan analisis
├── ringkasan_temuan/    # ringkasan audit dan EDA
├── docs/                # skor minimal per rasio, ringkasan angka demo, panduan monitoring
├── dataset/             # data mentah UCI (tidak diubah)
├── PROJECT_GUIDE.md     # semua temuan dan keputusan beserta alasannya
├── LICENSE              # MIT untuk kode, dataset tetap CC BY 4.0
└── requirements*.txt
```

## Cara kerja proyek ini

Proyek ini dikerjakan dengan bantuan AI (Claude Code). Setiap keputusan analisis, mulai dari pembersihan, validasi, metrik, sampai model, diambil oleh saya setelah opsinya dibahas, lalu dicatat beserta alasan dan keterbatasannya di [PROJECT_GUIDE.md](PROJECT_GUIDE.md). Angka di dokumen ini berasal dari notebook dan kode, bukan diketik tangan.

## Lisensi

Kode dan dokumentasi proyek ini berlisensi [MIT](LICENSE). Dataset di `dataset/` tidak termasuk lisensi itu: dataset berasal dari UCI dan tetap berlisensi [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), sehingga pemakaian ulang wajib menyebut sumbernya (sitasi ada di bagian [Data](#data)).

## Penulis

Arthur Pendragon · [GitHub](https://github.com/Kingarthuria)
