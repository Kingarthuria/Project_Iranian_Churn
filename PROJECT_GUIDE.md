# PROJECT GUIDE: Iranian Customer Churn

> File ini adalah **sumber kebenaran** project. Isi hanya fakta yang sudah pasti. Bagian yang belum diketahui dibiarkan kosong.
> Berikan ke AI di awal setiap sesi ("baca PROJECT_GUIDE.md dulu"). Perbarui **Status** dan **Log Keputusan** setiap selesai satu langkah.
> Terakhir diperbarui: 2026-11-08 (Fase 7: README dan ringkasan non-teknis selesai)

---

## 1. Ringkasan Proyek

| Item | Isi |
|---|---|
| Tujuan | **Portofolio / pembelajaran**: menunjukkan alur data science dan MLOps end-to-end yang rapi, jujur, dan bisa dijelaskan |
| Target peran | **Data Scientist (utama) + ML Engineer/MLOps (pendukung).** README dibuka dengan cerita data science (pola berulang, validasi jujur, hasil dengan rentang), lalu "dari notebook ke produk" (`src/`, test, CI, MLflow, demo, dan monitoring secara singkat). Data Analyst tidak menjadi target project ini. Untuk peran itu, lebih baik project terpisah dengan dashboard BI dan SQL |
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
- **Yang tidak dijelaskan UCI:** arti operasional "churn" (berhenti berlangganan, pindah operator, atau tidak aktif), cara `Status` ditentukan, bulan persis pencatatan dalam 9 bulan pertama, cara menghitung `Customer Value`, cara pengambilan sampel acak, siapa pembuat datanya, arti `Age`, dan detail hitungan kolom yang dicatat pada data dictionary.
- **Kolom ID:** UCI mencantumkan `Anonymous Customer ID`, tetapi file kita tidak memuatnya (14 kolom). Jadi kita tidak bisa memastikan apakah baris identik berasal dari pelanggan yang sama.
- Jurnal referensi yang sudah dikumpulkan ada di `jurnal/` (diabaikan Git).

### Data dictionary

> Nama kolom persis seperti header file. Isi mengikuti bagian *Additional Information* di halaman UCI (ditinjau 2026-11-05). Hal yang tidak dijelaskan UCI ditulis apa adanya, bukan diisi dengan tafsiran.

| Kolom | Arti menurut UCI |
|---|---|
| `Call  Failure` | jumlah kegagalan panggilan. Yang dihitung sebagai gagal tidak dijelaskan |
| `Complains` | biner: 0 = tidak ada komplain, 1 = ada komplain |
| `Subscription  Length` | total bulan berlangganan |
| `Charge  Amount` | ordinal: 0 = jumlah terendah, 9 = tertinggi. Data memuat nilai sampai 10 (lihat bagian 4) |
| `Seconds of Use` | total detik panggilan |
| `Frequency of use` | total jumlah panggilan. Tidak dijelaskan apakah panggilan dibuat atau diterima |
| `Frequency of SMS` | total jumlah pesan teks. Tidak dijelaskan apakah SMS dikirim atau diterima |
| `Distinct Called Numbers` | UCI menulis "total number of distinct phone calls". Redaksinya menyebut panggilan, sedangkan nama kolomnya menyebut nomor |
| `Age Group` | ordinal: 1 = lebih muda, 5 = lebih tua |
| `Tariff Plan` | biner: 1 = pay as you go, 2 = kontrak |
| `Status` | biner: 1 = aktif, 2 = non-aktif |
| `Age` | tidak tercantum di dokumentasi UCI. Data hanya memuat 5 nilai (15, 25, 30, 45, 55) yang berpasangan satu-satu dengan `Age Group` |
| `Customer Value` | "nilai pelanggan yang dihitung" (tanpa rumus) |
| `Churn` | **target**: biner, 1 = churn, 0 = non-churn |

### Kolom bantu (BUKAN fitur)

| Kolom | Letak | Arti |
|---|---|---|
| `audit_group` | `dataset_clean/validation_groups.csv`, sejajar per baris dengan file bersih | Sisa bagi 50 dari posisi baris pada data mentah. Hanya untuk cek CV grup (keputusan 22), dan tidak boleh masuk fitur model |

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
| 12 | Selisih churn rate, IK 95%: komplain 72,8 poin (67,3 sampai 77,3), non-aktif 41,9 poin (38,1 sampai 45,8), `Seconds_of_Use` kuartil terendah 25,3 poin (21,7 sampai 29,1). Churn rate per kelompok: pernah komplain 82,6% (230 baris) dan tidak 9,8% (2.620), non-aktif 47,5% (684) dan aktif 5,6% (2.166). Eksploratif | `program/EDA_Project_Churn_v2.ipynb` | 2026-11-04, churn rate per kelompok ditambahkan 2026-11-08 dari `load_clean()` |
| 13 | PR-AUC CV acak pada 2.280 baris latih, parameter default, 12 fitur: XGBoost 0,931 (0,920–0,939), RandomForest 0,914 (0,908–0,919), Logistic Regression 0,773 (0,768–0,776), `DummyClassifier` 0,157. Bukan performa pada pelanggan baru, dan skor setinggi ini dicurigai | `program/Modeling_Project_Churn.ipynb` | 2026-11-05 |
| 14 | Cek internal CV grup, dengan model dan fitur yang sama: Logistic Regression 0,625 (0,484–0,771), RandomForest 0,504 (0,400–0,635), XGBoost 0,474 (0,323–0,588), `DummyClassifier` 0,161. Rentangnya lebar dan bertumpuk | `program/Modeling_Project_Churn.ipynb` | 2026-11-05 |
| 15 | Tanpa `Status` dan `Complains`, PR-AUC XGBoost turun 0,045 pada CV acak dan 0,243 pada CV grup, sedangkan Logistic Regression turun 0,225 dan 0,256 | `program/Modeling_Project_Churn.ipynb` | 2026-11-05 |
| 16 | Pembobotan kelas hampir tidak mengubah PR-AUC CV acak XGBoost: 0,932 (0,927–0,941) dengan bobot, dan 0,931 (0,920–0,939) tanpa bobot | `program/Modeling_Project_Churn.ipynb` | 2026-11-05 |
| 17 | Penyetelan 60 kombinasi tidak jelas lebih baik dari default. Pada 12 fitur dan CV acak, PR-AUC default 0,934 (0,926–0,939) dan disetel 0,935 (0,929–0,942), dengan selisih per ulangan rata-rata +0,0015. Skor saat pencarian 0,941 | `program/Tuning_XGBoost.ipynb` | 2026-11-05 |
| 18 | Data uji, dinilai sekali (570 baris, 89 churn): XGBoost 12 fitur PR-AUC 0,958 (bootstrap 0,927–0,979) dan ROC-AUC 0,991, XGBoost 10 fitur PR-AUC 0,940 (0,900–0,972), `DummyClassifier` 0,156. Skornya lebih tinggi dari CV acak (0,934 dan 0,885), jadi dibaca dengan curiga dan bukan performa pada pelanggan baru | `program/Evaluasi_Data_Uji.ipynb` | 2026-11-05 |
| 19 | Pemeriksaan selisih skor: dari 1.824 ke 2.166 baris latih per fold, PR-AUC 12 fitur naik dari 0,935 ke 0,941 dan 10 fitur dari 0,892 ke 0,904. Pada 10 pembagian 80:20 di dalam data latih, rentangnya 0,917–0,942 dan 0,863–0,933. Baris yang beda maksimal 1 kolom dari tetangga terdekatnya di data latih: 3,5% di data uji dan 3,3% di validasi. Penyebab pasti belum terbukti | `program/Evaluasi_Data_Uji.ipynb` | 2026-11-05 |
| 20 | Threshold dari prediksi out-of-fold data latih: 1:2 = 0,23 (0,12–0,35), 1:5 = 0,06 (0,05–0,14), 1:10 = 0,045 (0,02–0,08). Pada data uji (89 churn), berurutan: precision 0,853, 0,744, dan 0,696, recall 0,910, 0,978, dan 0,978, dengan 95, 117, dan 125 pelanggan dihubungi. 1:5 dan 1:10 sama-sama menangkap 87 churn, tetapi 1:10 menambah 8 salah hubungi. Threshold 0,50: precision 0,918 dan recall 0,753. Rasio adalah asumsi, dan hasilnya bukan performa pada pelanggan baru | `program/Threshold_Biaya.ipynb` | 2026-11-05 |
| 21 | Risiko × nilai pada 2.280 baris latih, dengan threshold 1:5 dan batas nilai median 232,7: korelasi Spearman skor dengan nilai −0,612, dan baris churn memegang 4,3% total nilai di data latih (temuan 10 menyebut 4,4% karena dihitung dari seluruh 2.850 baris). Prioritas I (risiko tinggi, nilai tinggi) berisi 63 pelanggan (rentang antarulangan 59–69) dengan 54 churn, dan memegang 39,7% nilai baris churn. Prioritas III (risiko tinggi, nilai rendah) berisi 401 pelanggan dengan 287 churn. Jika 228 pelanggan dihubungi, urutan skor menangkap 220,7 churn dan 60,0% nilai churn, sedangkan urutan skor × nilai menangkap 203,4 churn dan 81,3% nilai churn. Sebanyak 76% pelanggan Prioritas I berasal dari 3 kelompok audit. Nilai terhitung bukan uang, dan hubungannya asosiatif | `program/Risiko_Nilai.ipynb` | 2026-11-06 |
| 22 | Permutation importance (turun PR-AUC) pada CV acak data latih: kelompok pemakaian 0,446 (0,427–0,463), `Complains` 0,224, `Frequency_of_use` 0,167, `Subscription_Length` 0,127, `Status` 0,099, `Call_Failure` 0,096. `Tariff_Plan` dan `Charge_Amount` mendekati 0. Urutan SHAP bawaan XGBoost: `Frequency_of_use` 1,768, `Status` 1,502, `Call_Failure` 1,106, `Complains` 0,915, dengan kesamaan urutan kedua cara 0,87. Pada cek CV grup, kelompok pemakaian, `Complains`, `Frequency_of_use`, dan `Status` tetap di lima besar, sedangkan `Subscription_Length` turun dari urutan 4 ke 8, dan kesamaan urutan CV acak dengan CV grup 0,61. Kepentingan fitur bukan sebab churn | `program/Interpretasi_Model.ipynb` | 2026-11-06 |
| 23 | Analisis error pada 2.280 baris latih dengan threshold 1:5: TP 341, FN (churn terlewat) 16, FP (salah hubungi) 123, TN 1.800. Sebanyak 8 churn dan 56 non-churn salah di semua 10 ulangan. Skor median FN 0,012, dan 13 dari 16 FN di bawah separuh threshold. Tidak ada FN yang pernah komplain. Baris dengan konflik label salah 62,5% dan baris aktivitas nol salah 25,0% (semuanya FP), dibanding sekitar 5,5% pada baris lain, dan baris berpenanda Fase 1 menyumbang 32 dari 139 kesalahan. Lima kelompok audit menyumbang 84 dari 123 FP, dan pelanggannya 92,7–98,0% non-aktif dengan churn rate 0,0–2,4%. Model tidak diubah | `program/Analisis_Error.ipynb` | 2026-11-06 |

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
| 7 | Pertahankan 111 baris dengan `Distinct Called Numbers` > `Frequency of use`. Narasi tidak boleh menganggap yang pertama pasti lebih kecil | Menurut UCI, `Frequency of use` adalah total panggilan dan `Distinct Called Numbers` adalah "total number of distinct phone calls". Kalau keduanya menghitung panggilan yang sama, nilai kedua seharusnya tidak melebihi nilai pertama, tetapi redaksi UCI belum memastikan hal itu. Menghapusnya membuang baris dengan churn lebih tinggi (21,6% vs 15,4%). Keterbatasan: 111 baris ini terlihat janggal dan sebagian mungkin memang tidak konsisten | 2026-11-04, alasan diperbarui 2026-11-05 |
| 8 | Pertahankan 85 baris dengan semua aktivitas nol. Penanda `is_zero_activity` bisa dibahas saat feature engineering | Tidak ada bukti barisnya salah, dan churn rate-nya tinggi (51,8% vs 14,5%). Keterbatasan: 26 baris berstatus aktif tanpa aktivitas | 2026-11-04 |
| 9 | Pertahankan 54 baris dengan `Subscription Length` di bawah 9. Tidak ada klaim tentang pelanggan baru, dan fitur per bulan tidak boleh menganggap semua baris mencakup 9 bulan penuh | Menurut UCI satuannya bulan, tetapi nilainya naik bertahap dan baris ini hampir seluruhnya berasal dari dua kelompok dengan hasil berlawanan | 2026-11-04, alasan diperbarui 2026-11-05 |
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
| 20 | Notebook EDA v2 diperbaiki menyeluruh setelah screening: cek kualitas data, grafik, konsistensi, dan kerapian kode | Keputusan pengguna, supaya notebook layak sebelum tahap cleaning. Rincian di `ringkasan_temuan/09_screening_notebook.md` | 2026-11-04 |
| 21 | Metadata Colab pada notebook asli ikut dihapus saat membersihkan riwayat Git. Sel dan outputnya tidak berubah. Email commit memakai alamat noreply GitHub | Keputusan pengguna, sebagai pengecualian dari aturan tidak mengubah notebook lama, untuk melindungi data pribadi | 2026-11-04 |
| 22 | Model dipilih dengan CV acak berstrata berulang (`RepeatedStratifiedKFold`). CV grup per `audit_group` hanya menjadi cek internal. Pada kedua CV, skor dihitung per fold lalu dirata-ratakan per ulangan, dan fold tanpa churn dilewati. Keputusan 1 dan 2 tetap berlaku: skor CV acak tidak boleh disebut performa pada pelanggan baru, dan README tidak memuat skor pembanding | Keputusan pengguna setelah meninjau keempat jurnal, yang semuanya membagi data per baris, dan sejalan dengan keputusan 1. Keterbatasan: audit menunjukkan skor CV acak bisa jauh lebih tinggi daripada CV grup, dan tidak ada jurnal yang membahas pola per 50 baris, jadi kesamaan cara dengan jurnal bukan bukti cara ini tepat untuk data ini. Model yang dipilih bisa cenderung menghafal pola. Skor gabungan out-of-fold ditolak, karena ROC-AUC `DummyClassifier` pada CV grup menjadi 0,301 | 2026-11-05 |
| 23 | Metrik utama PR-AUC, dengan baseline churn rate 0,157. ROC-AUC menjadi pendukung. Precision, recall, dan F1 dilaporkan setelah threshold dipilih di Fase 3 | Keputusan pengguna. Churn hanya 15,65%, dan PR-AUC berfokus pada kelas churn tanpa bergantung threshold | 2026-11-05 |
| 24 | Pisahkan 20% data uji acak berstrata di awal, dan pakai sekali di akhir. CV berjalan pada 80% sisanya | Keputusan pengguna, sama dengan keempat jurnal. Keterbatasan: data uji memuat pola yang sama dengan data latih, jadi skornya tidak mewakili pelanggan baru. Catatan: data uji dipakai lagi di Fase 3 (`program/Threshold_Biaya.ipynb`) hanya untuk melaporkan threshold (keputusan 32), tanpa mengubah model atau threshold. Langkah berikutnya tidak membukanya lagi | 2026-11-05, diperbarui 2026-11-06 |
| 25 | Kandidat: Logistic Regression, Decision Tree, KNN, SVM RBF, RandomForest, dan XGBoost. `DummyClassifier` menjadi batas bawah | Keputusan pengguna. XGBoost dipilih karena paling dikenal dan dipakai dua jurnal, bukan karena terbukti lebih baik pada data ini | 2026-11-05 |
| 26 | Pembeda utama project: produk jadi (Fase 4–6), perbandingan dengan dan tanpa `Status` serta `Complains`, dan threshold berbasis skenario biaya. Rentang skor, bahasa asosiatif, dan repo yang bisa dijalankan ulang menjadi standar kerja. Keputusan 2 dan 3 dipertahankan | Keputusan pengguna. Biaya adalah asumsi, bukan data. Klaim dibatasi pada keempat jurnal yang ditinjau, dan peran semua fitur dilihat dengan *permutation importance* di Fase 3 | 2026-11-05 |
| 27 | Ketidakseimbangan kelas: bandingkan tanpa penanganan dan pembobotan kelas (`class_weight`, atau `scale_pos_weight` per fold pada XGBoost). KNN hanya tanpa penanganan. SMOTE belum dipakai | Keputusan pengguna. Tidak membuat baris sintetis dan tidak butuh library baru. SMOTE bisa memperkuat pola berulang | 2026-11-05 |
| 28 | Fitur putaran pertama: 12 fitur tanpa `Age_Binning`, dengan dan tanpa `Status` serta `Complains`. Semua fitur tetap berupa angka untuk semua model. CV 5-fold, 10 kali ulang | Keputusan pengguna. Keterbatasan: Logistic Regression sulit menangkap pola naik lalu turun pada `Subscription_Length` dan `Age_Group`, jadi bisa terlihat lebih lemah dari kemampuan sebenarnya | 2026-11-05 |
| 29 | 12 fitur menjadi model utama. 10 fitur tanpa `Status` dan `Complains` dilaporkan sebagai pembanding | Keputusan pengguna. Tidak ada bukti keduanya leakage. Keterbatasan: cara `Status` ditentukan tidak dijelaskan UCI, jadi skor 12 fitur bisa terlalu tinggi | 2026-11-05 |
| 30 | Penyetelan XGBoost memakai `RandomizedSearchCV` 60 kombinasi dengan PR-AUC pada data latih. Kombinasi terbaik dinilai ulang dengan CV 10 kali ulang memakai seed lain. Hasilnya hanya dipakai kalau rentangnya tidak bertumpuk dengan default pada fold yang sama, dan lebih tinggi | Keputusan pengguna. Tanpa library baru, dan jangkauan nilainya luas. Keterbatasan: penilaian ulang masih memakai data latih yang sama, dan CV acak bisa mendorong model menghafal pola | 2026-11-05 |
| 31 | Model terpilih: XGBoost, parameter default, tanpa pembobotan, 12 fitur. Model tidak diubah berdasarkan hasil data uji | Keputusan pengguna. PR-AUC CV acak tertinggi, rentangnya tidak bertumpuk dengan RandomForest, pembobotan dan penyetelan tidak jelas lebih baik. Keterbatasan: pada cek grup, Logistic Regression lebih tinggi dengan rentang bertumpuk, dan CV acak bisa menguntungkan model yang menghafal pola | 2026-11-05 |
| 32 | Threshold disediakan sebagai pilihan rasio biaya 1:2, 1:5, dan 1:10, dengan default 1:5. Threshold tiap rasio adalah median threshold berbiaya terendah dari 10 ulangan prediksi out-of-fold data latih. Threshold tidak diubah setelah melihat data uji | Keputusan pengguna, supaya perusahaan atau pembaca repo bisa memilih rasio sesuai biaya mereka tanpa melatih ulang model. Biaya adalah asumsi, bukan data. Keterbatasan: rumus biaya tidak menghitung biaya promo untuk pelanggan yang berisiko churn dan mengabaikan keberhasilan menahan pelanggan, skor belum terkalibrasi, threshold tidak stabil antarulangan, dan threshold berasal dari model yang dilatih pada 80% data latih | 2026-11-05 |
| 33 | Analisis risiko × nilai memakai matriks 4 segmen sebagai hasil utama, dengan urutan skor × nilai sebagai pembanding. Risiko adalah skor out-of-fold data latih dengan threshold default 1:5, dan pelanggan disebut berisiko tinggi jika skornya mencapai threshold di lebih dari separuh dari 10 ulangan. Nilai adalah `Customer_Value` dengan batas median data latih. Data uji tidak dipakai. `Customer_Value` disebut **nilai terhitung**, bukan uang. Pemusatan segmen pada kelompok audit dirinci di notebook sebagai cek internal, dan README cukup memuat satu kalimat umum | Keputusan pengguna. UCI hanya menyebut *"the calculated value of customer"*, tanpa rumus dan satuan, dan dataset tidak punya kolom pendapatan. Caranya mirip Damuri dkk. (2026), dan kemiripan ini ditulis terbuka. Keterbatasan: arti pasti `Customer_Value` tidak diketahui dan nilainya sangat bisa dijelaskan oleh penggunaan telepon dan SMS (temuan 8), nilai berasal dari 9 bulan pertama, `Customer_Value` juga fitur model, segmen prioritas kecil dan terpusat pada beberapa kelompok audit, dan tindakan per segmen adalah hipotesis | 2026-11-06 |
| 34 | Interpretasi model memakai *permutation importance* (turunnya PR-AUC) dan SHAP bawaan XGBoost (`pred_contribs`), dihitung pada fold validasi data latih. Data uji tidak dipakai. Kepentingan dilaporkan per fitur dan per kelompok pemakaian (`Seconds_of_Use`, `Frequency_of_use`, `Frequency_of_SMS`, `Distinct_Called_Numbers`, `Customer_Value`). Arah hubungan ditampilkan untuk 4 fitur teratas. CV grup per `audit_group` menjadi cek internal. Penjelasan per pelanggan, kalibrasi, dan interpretasi model 10 fitur belum dikerjakan | Keputusan pengguna. `shap` 0.49.1 sempat dipasang, tetapi gagal membaca model XGBoost 3.2.0 (`base_score` berformat baru), jadi tidak masuk requirements dan SHAP dihitung dengan fungsi bawaan XGBoost. Keterbatasan: kepentingan fitur bukan sebab-akibat, fitur yang saling berkorelasi berbagi kepentingan, cara `Status` ditentukan tidak dijelaskan UCI (keputusan 29), dan CV acak bisa menonjolkan pola berulang | 2026-11-06 |
| 35 | Analisis error memakai prediksi out-of-fold data latih dengan threshold 1:5 dan suara mayoritas, seperti keputusan 33. Data uji tidak dipakai. Isinya: ringkasan churn terlewat (FN) dan salah hubungi (FP), sebaran skor kesalahan, profil kesalahan, kaitan dengan baris janggal Fase 1 (keputusan 5–9), cek internal kelompok audit, dan 3 contoh churn terlewat yang dijelaskan dengan SHAP bawaan XGBoost. Model dan threshold tidak diubah, dan temuan dicatat sebagai keterbatasan serta bahan pemantauan Fase 6 | Keputusan pengguna. Keterbatasan: hanya data latih dengan CV acak, penanda baris janggal mengikuti definisi Fase 1, baris dengan fitur identik tetapi label berbeda adalah kesalahan yang tidak bisa dihindari, dan penjelasan SHAP menggambarkan cara model bekerja, bukan sebab churn | 2026-11-06 |
| 36 | Logika yang dipakai ulang dipindah ke `src/`: `config.py` (satu sumber `SEED`, path, dan fitur), `data.py`, `model.py`, `threshold.py`, lalu `train.py` untuk pelatihan ulang dengan satu perintah. Model final dilatih pada 2.280 baris latih, sama dengan model yang dinilai. Notebook di `program/` tidak diubah, dan test di `tests/` membuktikan `src/` menghasilkan angka yang sama. File model disimpan di `models/` dan tidak dilacak Git. `pytest` 9.2.0 dan `ruff` 0.17.4 dicatat di `requirements-dev.txt` | Keputusan pengguna (pilihan A). Semua angka yang sudah dilaporkan (data uji dan threshold) tetap berlaku untuk model ini. Keterbatasan: model tidak memakai 570 baris uji untuk belajar, dan cara penyimpanan model untuk demo diputuskan lagi di Fase 4 atau 5 | 2026-11-06 |
| 37 | Experiment tracking memakai MLflow 3.18.0 lokal: `mlflow.db` (SQLite) dan `mlartifacts/`, keduanya tidak dilacak Git, dengan experiment `iranian-churn`. Dicatat 4 run inti: XGBoost 12 fitur (final), XGBoost 10 fitur (tanpa `Status` dan `Complains`), Logistic Regression 12 fitur, dan `DummyClassifier`. Tiap run memuat parameter, PR-AUC dan ROC-AUC CV acak (rata-rata, minimum, maksimum per ulangan, dihitung per fold), metrik CV grup berawalan `cek_grup_`, serta tag hash data, commit, keputusan, dan keterbatasan. Data uji tidak dipakai, dan run final hanya memberi tag rujukan ke temuan 18. Pipeline final didaftarkan sebagai `iranian-churn-xgboost` dengan alias `champion`. Semua dijalankan dengan `python -X utf8 -m src.track`. `mlflow` masuk `requirements-dev.txt` | Keputusan pengguna. Empat run cukup untuk perbandingan bermakna di UI tanpa memindah semua kandidat Fase 2 ke `src/`. Demo Fase 5 tidak bisa membaca registry lokal, jadi `requirements.txt` tetap ringan. Keterbatasan: tracking hanya lokal, setiap kali perintah dijalankan run dan versi model bertambah, dan skor CV acak bukan performa pada pelanggan baru | 2026-11-06 |
| 38 | Demo Fase 5: satu halaman Streamlit (`streamlit_app.py`) dengan input 12 fitur yang divalidasi skema `pydantic`, pilihan rasio 1:2, 1:5 (default), dan 1:10, skor risiko, keputusan hubungi, segmen Prioritas I–IV, dan penjelasan 5 fitur teratas dengan SHAP bawaan XGBoost. Platform Streamlit Community Cloud: repo tetap privat dan aplikasi dijadikan publik. Demo dan CI memakai Python 3.12, sedangkan `ds_env` (Python 3.10) tetap untuk notebook. Model dilatih ulang dari dataset saat aplikasi menyala, tanpa file model di Git. `requirements.txt` hanya berisi library demo, dan library notebook pindah ke `requirements-dev.txt`. Test, lint, dan CI GitHub Actions. Input tidak disimpan. Paket `shap` tetap di `ds_env`, tidak masuk requirements, dan tidak di-import kode project | Keputusan pengguna. Python 3.10 sudah melewati akhir masa dukungan keamanan (Oktober 2026), dan Streamlit Community Cloud hanya mendukung versi yang masih menerima pembaruan keamanan. Aplikasi dari repo privat bisa dijadikan publik tanpa membuka repo. Keterbatasan: segmen di demo memakai skor satu model final, bukan suara mayoritas out-of-fold seperti `program/Risiko_Nilai.ipynb`. Demo tidak bisa menyimpan log prediksi, jadi pemantauan Fase 6 perlu cara lain. Skor demo bukan performa pada pelanggan baru | 2026-11-06 |
| 39 | Lingkungan Python 3.12 memakai env conda `ds_env312` (Python 3.12.16 dari channel conda, paket dari `requirements-dev.txt` lewat pip), bukan `venv` dari Python sistem. Mulai sekarang `ds_env312` dipakai untuk demo, test, dan pekerjaan baru. `ds_env` (Python 3.10) disimpan sementara sebagai pembanding hasil notebook lama, dan penghapusannya diputuskan pengguna nanti. Python di luar env conda dan perintah yang membuka akses jaringan tidak dijalankan tanpa penjelasan rinci lebih dulu | Keputusan pengguna (pilihan A). Mengganti Python di `ds_env` secara langsung berisiko merusak 200 paket pip dan sulit dikembalikan. `streamlit_env` memakai Python 3.9, jadi juga tidak cocok untuk Streamlit Community Cloud, dan tidak diubah. `.venv` dari Python 3.12 sistem dihapus setelah `ds_env312` terbukti memberi 46 test lulus dan skor identik | 2026-11-06 |
| 40 | CI memakai GitHub Actions (`.github/workflows/ci.yml`): berjalan setiap push ke branch mana pun dan setiap pull request ke `main`, di `ubuntu-latest` dengan Python 3.12. Langkahnya memasang `requirements-dev.txt`, menjalankan `pip check`, `ruff check src tests streamlit_app.py`, dan `pytest`. Izin workflow hanya membaca kode (`contents: read`), tanpa rahasia atau token. Run lama di branch yang sama dibatalkan jika ada push baru, dengan batas waktu 20 menit | Keputusan pengguna (keputusan 38). Test di `tests/` sudah mencocokkan angka notebook, MLflow, dan demo, jadi CI menjaga hasil tetap sama setiap ada perubahan. Keterbatasan: CI hanya menguji Linux dengan Python 3.12, repo privat memakai kuota menit GitHub Actions akun, dan satu run diperkirakan 5–10 menit | 2026-11-06 |
| 41 | Tampilan demo Fase 5 ditulis ulang. **Sidebar:** judul Bahasa, pilihan contoh berupa segmented control tiga pilihan sama lebar (Risiko tinggi, Risiko rendah, Nilai median), Data pelanggan dalam 4 grup dengan petunjuk median dan rentang di ikon bantuan, kotak **Pengaturan keputusan** (rasio biaya) bergaris putus-putus di antara grup isian dan tombol hitung, tanpa `st.form` supaya rasio langsung berlaku. **Empat tab:** (1) *Hasil & rekomendasi* untuk pembaca bisnis, berjudul "Perlukah pelanggan ini dihubungi?", dengan alur What, So What, Now What tanpa judul per bagian: 3 kartu (keputusan, skor risiko, skor minimal), insight bahasa awam yang membandingkan pelanggan dengan median data latih, kalimat penghubung ke matriks segmen 2×2 (nilai tinggi di kiri), rekomendasi per segmen untuk siklus 12 bulan berikutnya, saran yang disesuaikan dari alasan risiko (komplain, non-aktif, kegagalan panggilan di atas umumnya, pemakaian di bawah umumnya) hanya untuk pelanggan yang disarankan dihubungi, dan pengingat keterbatasan satu baris; (2) *Detail teknis*: posisi skor pada sumbu log, waterfall SHAP 12 fitur, dan tabel SHAP; (3) *Cara kerja model*: alur data, PR-AUC dan ROC-AUC dari `docs/ringkasan_model.csv`, permutation importance dari `docs/kepentingan_fitur.csv` (keduanya dibuat `python -X utf8 -m src.summary`, sama dengan temuan 13 dan 22), dan tabel skor minimal per rasio; (4) *Keterbatasan & data*. Istilah "skor minimal untuk dihubungi" menggantikan "batas hubungi" dan threshold. Dua bahasa (`src/texts.py`, default Indonesia), tema terang `#334155` (`.streamlit/config.toml`), grafik Altair (`src/charts.py`, `altair==6.3.0` dipatok), dan sedikit CSS tata letak di `streamlit_app.py`. Menggantikan bagian tampilan keputusan 38, termasuk penjelasan 5 fitur teratas | Keputusan pengguna setelah 16 putaran peninjauan dari sudut pandang pembaca awam. Bagian bisnis dan teknis dipisah supaya beban baca berkurang. Keterbatasan: tindakan dan contoh penawaran adalah hipotesis, CSS bergantung pada struktur HTML Streamlit 1.65 sehingga bisa rusak saat upgrade, dan di tab hasil kalimat keterbatasan hanya berupa pengingat satu baris (kalimat lengkap ada di tab 4, keputusan 2 berlaku untuk README dan laporan model) | 2026-11-07 |
| 42 | Dua asumsi tampilan di demo, keduanya ditulis di tab Keterbatasan & data. (a) Isian kelompok usia berupa 5 tombol perkiraan umur ≈15, ≈25, ≈30, ≈45, dan ≈55 tahun, yaitu nilai kolom `Age` yang berpasangan satu-satu dengan `Age_Group` 1–5 di data latih (dihitung `src/predict.py`, `_age_by_group`). Model tetap memakai `Age_Group`. (b) Waktu tindakan memakai siklus 12 bulan menurut UCI (fitur dari bulan 1–9, status churn di akhir bulan ke-12): hitung ulang skor di akhir bulan ke-9, bertindak di bulan ke-10 sampai ke-11, dan cek status di akhir bulan ke-12, untuk siklus tahun berikutnya | Keputusan pengguna. Slider 1–5 membingungkan pembaca, dan rekomendasi butuh waktu yang jelas. Keterbatasan: arti `Age` tidak dijelaskan UCI (keputusan 10), UCI tidak menyebut kapan pelanggan benar-benar berhenti, dan pola pelanggan tahun berikutnya diasumsikan mirip dengan data ini | 2026-11-07 |
| 43 | Peringatan "kombinasi input tidak umum" dihapus dari demo beserta fungsi `unusual_combinations`, datanya di `Bundle`, teks, dan test-nya | Keputusan pengguna. Aturan sisa regresi `Customer_Value` (temuan 8) menandai nilai yang masih di dalam rentang data latih, sehingga membingungkan pembaca. Keterbatasan: kombinasi isian yang tidak konsisten tidak lagi ditandai. Input tetap dibatasi rentang data latih oleh `src/schema.py` | 2026-11-07 |
| 44 | Monitoring Fase 6 tanpa library baru. `python -X utf8 -m src.monitor` membuat 4 batch simulasi berisi 500 pelanggan dari data latih (`normal`, `komplain_naik`, `pemakaian_turun`, `nonaktif_naik`, `src/simulate.py`), menilainya dengan model demo dan mencatat log prediksi (`src/score_batch.py`), lalu membandingkannya dengan 2.280 baris data latih (`src/monitor.py`): PSI per fitur (10 kuantil data acuan, atau per kode untuk 5 kolom berkode), uji KS dan chi-kuadrat sebagai pelengkap, dan porsi pelanggan yang disarankan dihubungi. Status fitur memakai batas PSI 0,10 dan 0,25. Batch bergeser jika ada fitur penting (temuan 22) dengan PSI 0,25 ke atas, atau porsi dihubungi bergeser 10 poin persen atau lebih. Hasilnya `monitoring/laporan_drift.md`, `monitoring/drift_per_fitur.csv`, dan `monitoring/prediction_log.csv` (tidak dilacak Git). Aturan retraining dan rollback ada di `docs/monitoring.md`: drift memicu pemeriksaan, retraining menunggu label sekitar 3 bulan, `champion` hanya diganti jika rentang PR-AUC model baru tidak lebih buruk (seperti keputusan 30), dan rollback mengembalikan alias `champion` di MLflow atau me-revert commit `main` untuk demo. Data uji tidak dipakai | Keputusan pengguna: batch simulasi, PSI dengan uji statistik, log dari script batch, dan laporan Markdown + CSV. Dataset hanya punya satu periode, dan demo publik tidak menyimpan input (keputusan 38). Keterbatasan: batch adalah simulasi dari data latih model sendiri, sehingga skornya lebih yakin daripada skor pelanggan baru; drift data tidak sama dengan turunnya performa; label churn datang terlambat; dan batas PSI serta batas porsi dihubungi adalah aturan praktis atau asumsi | 2026-11-08 |
| 45 | Repo dijadikan publik di Fase 7, setelah README selesai. Persiapannya: (a) `CLAUDE.md` dan `PROJECT_GUIDE.md` tetap dilacak, dan README menyebut bahwa proyek dikerjakan dengan bantuan AI dengan semua keputusan tercatat di guide; (b) tag `arsip-v1` dihapus dari GitHub tetapi tetap disimpan lokal; (c) 8 branch fase yang sudah di-merge ke `main` dihapus di GitHub dan lokal; (d) di `program/EDA_Project_Churn.ipynb`, hanya baris path `A:\project_iranian_churn\dataset\...` diganti menjadi `../dataset/Customer Churn.csv`, sedangkan sel lain dan output tidak berubah. Pemeriksaan sebelum publik: tidak ada file rahasia atau pola token di seluruh riwayat, email commit hanya alamat noreply GitHub, dan tidak ada path absolut lain di file yang dilacak | Keputusan pengguna. Pengecualian (d) mengikuti pola keputusan 21. Keterbatasan: path lama dan isi tag `arsip-v1` masih ada di riwayat commit atau cache GitHub, tetapi path itu tidak memuat nama pengguna. Riwayat commit, termasuk catatan kerja, ikut terlihat publik | 2026-11-08 |

---

## 5. Metrik Evaluasi

| Peran | Metrik |
|---|---|
| Utama | PR-AUC, dengan baseline churn rate 0,157 |
| Pendukung | ROC-AUC |
| Setelah threshold dipilih di Fase 3 | Precision, recall, dan F1 kelas churn |

Accuracy tidak dipakai sebagai metrik utama. Lihat keputusan 22 dan 23 di bagian 4.

---

## 6. Status Pekerjaan

| Fase | Status |
|---|---|
| 0 Housekeeping | **Selesai.** `requirements.txt`, Git, GitHub privat, dan struktur folder sudah ada. Environment `ds_env` terverifikasi (dry-run 0 paket baru, `pip check` bersih) |
| 1 EDA dan data preparation | **Selesai.** Audit duplikat dan struktur data disimpan, dan `program/EDA_Project_Churn_v2.ipynb` sudah diperbaiki. `python -X utf8 src/clean_data.py` menghasilkan `dataset_clean/customer_churn_clean.csv` (2.850 baris, 14 kolom). Dua kali jalan menghasilkan hash yang sama |
| 2 Modeling | **Selesai.** Perbandingan ada di `program/Modeling_Project_Churn.ipynb`, penyetelan di `program/Tuning_XGBoost.ipynb`, dan data uji di `program/Evaluasi_Data_Uji.ipynb`. Model terpilih: XGBoost default, tanpa pembobotan, 12 fitur (keputusan 31). Data uji sudah dipakai, jadi model tidak diubah berdasarkan hasilnya |
| 3 Evaluasi dan refactor | **Selesai.** Threshold skenario biaya (`program/Threshold_Biaya.ipynb`, `docs/threshold_skenario.csv`, keputusan 32), risiko × nilai (`program/Risiko_Nilai.ipynb`, keputusan 33), interpretasi model (`program/Interpretasi_Model.ipynb`, keputusan 34), dan analisis error (`program/Analisis_Error.ipynb`, keputusan 35). Logika dipindah ke `src/` dengan 19 test, dan `python -X utf8 -m src.train` melatih ulang Pipeline final pada 2.280 baris latih serta menyimpannya ke `models/` (keputusan 36). Dua kali jalan menghasilkan hash model yang sama |
| 4 Experiment tracking | **Selesai.** `python -X utf8 -m src.track` mencatat 4 run ke MLflow lokal (`mlflow.db`, experiment `iranian-churn`) dan mendaftarkan Pipeline final sebagai `iranian-churn-xgboost@champion` (keputusan 37). Metrik di MLflow sama dengan temuan 13–15, model dari registry memberi skor sama dengan `models/churn_pipeline.joblib`, dan UI (`mlflow ui --backend-store-uri sqlite:///mlflow.db`) menampilkan keempat run. Ada 26 test |
| 5 Deployment | **Selesai.** Demo publik: https://churn-risk-priority.streamlit.app/ (Streamlit Community Cloud, branch `main`, Python 3.12). `streamlit_app.py` dengan skema input `src/schema.py` dan prediksi `src/predict.py` sudah berjalan lokal. Env conda `ds_env312` (Python 3.12.16) dibuat dari `requirements-dev.txt`, dan 46 test lulus di `ds_env312` maupun `ds_env` dengan skor model identik (keputusan 39). CI GitHub Actions hijau di Linux dengan Python 3.12 (keputusan 40). Tampilan demo ditulis ulang dan dikunci (keputusan 41–43): 4 tab, dua bahasa, dan rekomendasi per segmen. 73 test lulus, dan PR #4 di-merge ke `main` setelah CI hijau |
| 6 Monitoring | **Selesai**, di-merge ke `main` lewat PR #8. `python -X utf8 -m src.monitor` membuat laporan drift dari 4 batch simulasi (keputusan 44). Batch `normal` stabil (PSI semua fitur di bawah 0,015), dan ketiga skenario buatan tertangkap pada fitur yang diubah. Aturan retraining dan rollback ada di `docs/monitoring.md`. 80 test lulus |
| 7 Dokumentasi portofolio | **Berjalan** di branch `fase7-dokumentasi`. README portofolio (dengan tabel kesalahan yang ditemukan dan diperbaiki serta kalimat keterbatasan) dan `docs/ringkasan_non_teknis.md` sudah ditulis dan disetujui pengguna. Sisa: lisensi kode, PR ke `main`, lalu repo dijadikan publik (keputusan 45) |

---

## 7. Masalah yang Diketahui

**Independensi baris tidak terjamin.** Lihat temuan 2–5 di bagian 3 dan `ringkasan_temuan/`. Penyebabnya belum diketahui. Keputusan penanganannya ada di bagian 4.

Kalimat keterbatasan yang wajib masuk README dan laporan model:

> Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Namun audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis.

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
- [x] Periksa kualitas data: tipe, missing value, duplikat, rentang nilai, logika antar kolom
- [x] Periksa **independensi baris** dan struktur data sebelum memilih strategi validasi
- [x] Univariat, hubungan fitur dengan target, hubungan antar fitur
- [x] Setiap keputusan pembersihan dicatat di bagian 4 beserta alasannya
- [x] Proses pembersihan dapat dijalankan ulang dengan script, bukan hanya dari notebook

**DoD:** satu perintah menghasilkan data bersih yang sama, dan semua keputusan tercatat.

### Fase 2: Modeling
- [x] Strategi validasi dipilih berdasarkan struktur data, disetujui pengguna
- [x] Baseline sederhana dan model kandidat
- [x] Penanganan ketidakseimbangan kelas (jika relevan), dibandingkan
- [x] Scaler, encoder, dan resampling di dalam fold
- [x] Pilih model dengan alasan tertulis. Jika selisih masih dalam rentang ketidakpastian, pilih yang paling sederhana

**DoD:** tabel perbandingan model dengan ketidakpastian dan satu model terpilih dengan alasan.

### Fase 3: Evaluasi, interpretasi, dan refactor
- [x] Pilih threshold berdasarkan skenario biaya (tandai asumsi)
- [x] Analisis risiko × nilai: skor churn dari prediksi di luar data latih × `Customer_Value` (nilai terhitung)
- [x] Interpretasi model dengan bahasa asosiatif, bukan kausal
- [x] Analisis error
- [x] Pindahkan logika ke `src/`, tambah test sederhana
- [x] Simpan model final sebagai satu Pipeline

**DoD:** pelatihan ulang dapat dijalankan dengan satu perintah.

### Fase 4: Experiment tracking
- [x] Satu tracking URI dan satu nama experiment
- [x] Catat params, metrik (dengan ketidakpastian), artefak, tag versi data
- [x] Daftarkan model terbaik di registry

**DoD:** run dapat dibandingkan di UI tracking dan model terbaik dapat dimuat.

### Fase 5: Deployment (tanpa Docker untuk saat ini)
- [x] API atau aplikasi demo dengan skema input/output yang divalidasi
- [x] Lingkungan dikunci dengan `venv` dan `requirements.txt` (env conda `ds_env312` dari `requirements-dev.txt`, keputusan 39)
- [x] Test, lint, dan CI
- [x] Deploy demo ke layanan gratis (Streamlit Community Cloud: https://churn-risk-priority.streamlit.app/)

**DoD:** demo publik bisa diakses lewat URL dan CI hijau.

### Fase 6: Monitoring
- [x] Log prediksi, laporan drift terhadap data referensi (`src/score_batch.py`, `src/monitor.py`)
- [x] Aturan retraining dan prosedur rollback (`docs/monitoring.md`)
- [x] Catatan keterbatasan monitoring (label sering datang terlambat)

**DoD:** laporan drift dapat dihasilkan dengan satu perintah.

### Fase 7: Dokumentasi portofolio
- [x] `README.md` dari template portofolio, termasuk keterbatasan
- [x] Tabel "kesalahan yang saya temukan dan perbaiki"
- [x] Ringkasan satu halaman untuk non-teknis (`docs/ringkasan_non_teknis.md`)

**DoD:** orang lain dapat mengklon, menjalankan, dan memahami hasilnya tanpa bertanya.

---

## 9. Konvensi Teknis

**Kode:** Python 3.12 di env conda `ds_env312` untuk demo, test, CI, dan pekerjaan baru (keputusan 38 dan 39). Notebook lama dibuat dengan Python 3.10 di `ds_env`, yang disimpan sebagai pembanding, `pathlib` tanpa path absolut, satu seed global di satu tempat, `snake_case`, satu notebook satu tujuan, logika yang dipakai ulang pindah ke `src/`, jangan menimpa data mentah.

**Requirements bertahap**
- `requirements.txt` hanya berisi library yang dipakai **sekarang**. Library baru masuk di commit yang sama dengan kode yang memakainya, versi dipatok (`==`).
- Verifikasi: `pip install --dry-run -r requirements.txt` (0 paket baru) dan `pip check`.

| Fase | Library yang biasanya ditambahkan |
|---|---|
| 1 EDA | pandas, numpy, scipy, statsmodels, scikit-learn, matplotlib, seaborn, ipykernel (sesuai import `EDA_Project_Churn_v2.ipynb`) |
| 2 Modeling | `imbalanced-learn` (jika resampling dipakai), opsional `xgboost` / `lightgbm` / `catboost` |
| 3 Evaluasi dan refactor | `joblib` (runtime). Dev di `requirements-dev.txt`: `pytest`, `ruff`, `nbconvert`, `jupyter_core`. `shap` tidak dipakai (keputusan 34) |
| 4 Tracking | `mlflow==3.18.0` di `requirements-dev.txt` (keputusan 37) |
| 5 Deployment | `streamlit` dan `pydantic` di `requirements.txt`, yang kini hanya berisi library demo. Library notebook pindah ke `requirements-dev.txt` (keputusan 38). `altair` dipatok untuk grafik demo (keputusan 41). FastAPI tidak dipakai |
| 6 Monitoring | Tidak ada library baru. PSI dan uji statistik memakai `numpy` dan `scipy` yang sudah ada, `evidently` tidak dipakai (keputusan 44) |

**Git:** commit kecil per langkah, pesan Bahasa Indonesia dengan awalan fase (`fase1: ...`).

---

## 10. Struktur Folder Target

```
project_iranian_churn/
├── PROJECT_GUIDE.md
├── CLAUDE.md
├── README.md
├── streamlit_app.py      # demo Fase 5
├── requirements.txt      # library runtime demo (dibaca Streamlit Community Cloud)
├── .streamlit/config.toml # tema demo (keputusan 41)
├── requirements-dev.txt  # library pengembangan (test, lint, notebook)
├── pyproject.toml        # pengaturan pytest dan ruff
├── .gitignore
├── dataset/          # data mentah, read-only (dilacak, CC BY 4.0)
├── dataset_clean/    # data bersih, dibuat ulang dari script (tidak dilacak Git)
├── models/           # Pipeline terlatih dan metadata, dibuat ulang dengan src.train (tidak dilacak Git)
├── monitoring/       # batch simulasi, log prediksi, dan laporan drift dari src.monitor (tidak dilacak Git)
├── jurnal/           # referensi, diabaikan Git
├── program/          # notebook eksplorasi (peta di program/README.md)
├── ringkasan_temuan/ # ringkasan temuan bernomor (.md)
├── src/              # logika yang dipakai ulang
├── tests/            # test pytest untuk src/
└── docs/             # decision log, laporan, threshold_skenario.csv, ringkasan angka demo, monitoring.md
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
| 2026-11-04 | Screening dan perbaikan menyeluruh notebook EDA v2 selesai (bagian 4). Strip output ditunda sampai sebelum repo dipublikasikan | Diputuskan |
| 2026-11-04 | Riwayat Git dibersihkan dari metadata Colab dan email pribadi, lalu `main` dan `arsip-v1` di GitHub diperbarui dengan force push. Commit lama masih bisa tersimpan sementara di cache GitHub | Diputuskan |
| 2026-11-05 | Data dictionary dikoreksi dari bagian *Additional Information* di halaman UCI, dan alasan keputusan 7 dan 9 diperbarui, tanpa perubahan baris. Keempat jurnal di `jurnal/` tidak menunjukkan bukti konkret tentang arti kolom, dan sebagian tafsirannya bertentangan | Diputuskan |
| 2026-11-05 | `program/EDA_Project_Churn_v2.ipynb` dan `ringkasan_temuan/03_kualitas_kolom.md` diselaraskan dengan dokumentasi UCI. Hanya teks markdown yang berubah | Diputuskan |
| 2026-11-05 | `src/clean_data.py` dibuat: menghapus 300 duplikat persis dan merapikan nama kolom, sama dengan langkah notebook EDA v2. Kolom `Age` bernama `Age_Binning` di file bersih. `dataset_clean/` tidak dilacak Git | Diputuskan |
| 2026-11-05 | Strategi validasi: CV acak berstrata berulang sebagai pemilih model, dan CV grup per `audit_group` sebagai cek internal. Pilihan awal CV grup diganti setelah meninjau keempat jurnal. Metrik utama: PR-AUC (bagian 4 dan 5). `src/clean_data.py` kini juga menulis `dataset_clean/validation_groups.csv` | Diputuskan |
| 2026-11-05 | Data uji 20%, enam model kandidat, dan pembeda utama project diputuskan (keputusan 24, 25, dan 26). XGBoost 3.2.0 diinstal di `ds_env`, dan masuk `requirements.txt` bersama kode yang memakainya | Diputuskan |
| 2026-11-05 | Ketidakseimbangan kelas, fitur putaran pertama, dan ulangan CV diputuskan (keputusan 27 dan 28). Kode putaran pertama ditulis di notebook baru, dan dipindah ke `src/` di Fase 3 | Diputuskan |
| 2026-11-05 | Koreksi keputusan 22: skor dihitung per fold untuk kedua CV, setelah pemeriksaan batas bawah menunjukkan skor gabungan tidak layak untuk CV grup | Diputuskan |
| 2026-11-05 | 12 fitur menjadi model utama, dan XGBoost disetel dengan random search 60 kombinasi di `program/Tuning_XGBoost.ipynb` (keputusan 29 dan 30) | Diputuskan |
| 2026-11-05 | Model dikunci sebelum data uji dibuka: XGBoost default, tanpa pembobotan, 12 fitur (keputusan 31) | Diputuskan |
| 2026-11-05 | Data uji dinilai sekali di `program/Evaluasi_Data_Uji.ipynb` (temuan 18), dan Fase 2 memenuhi DoD. Skor yang lebih tinggi dari CV acak masih dibaca dengan curiga | Diputuskan |
| 2026-11-05 | Baris co-author dihapus dari 30 commit, lalu semua branch dan tag `arsip-v1` diperbarui dengan force push. Isi file tidak berubah. Commit lama masih bisa tersimpan sementara di cache GitHub | Diputuskan |
| 2026-11-05 | Threshold disediakan sebagai pilihan rasio 1:2, 1:5, dan 1:10, dengan default 1:5 (keputusan 32). Tampilan pilihan di demo dibuat di Fase 5 | Diputuskan |
| 2026-11-06 | Analisis risiko × nilai memakai matriks 4 segmen dan `Customer_Value` sebagai nilai terhitung, bukan uang (keputusan 33). UCI dan keempat jurnal tidak menjelaskan rumus kolom ini | Diputuskan |
| 2026-11-06 | Pengecekan konsistensi Fase 0–3: semua angka temuan 13–21 cocok dengan output notebook, dan pembagian data, fitur, model, serta threshold sama di semua notebook. Diperbaiki: catatan pemakaian kedua data uji di keputusan 24, label PR-AUC gabungan di notebook Fase 3, istilah "skor" di checklist Fase 3, dan dokumentasi pendukung | Diputuskan |
| 2026-11-06 | Ditutup (keputusan 36): `SEED` dan konstanta lain kini bersumber satu di `src/config.py`. Notebook di `program/`, termasuk angka CV yang disalin tangan di `Evaluasi_Data_Uji.ipynb`, tetap sebagai catatan eksperimen dan tidak diubah. `jupyter_core` dan `nbconvert` masuk `requirements-dev.txt` | Diputuskan |
| | Ukuran notebook EDA v2 (sekitar 6 MB): output tetap disimpan, dan resolusi gambar dikurangi sekali saat notebook final | **Terbuka** |
| | Fitur putaran berikutnya dan fitur final | **Terbuka** |
| | Hal yang belum dijelaskan UCI: definisi operasional churn, cara `Status` ditentukan, rumus `Customer Value`, arti `Age`, dan detail hitungan `Call  Failure`, `Frequency of use`, `Frequency of SMS`, serta `Distinct Called Numbers` (bagian 2) | **Terbuka** |
| | Platform demo: Streamlit Community Cloud (keputusan 38) | Diputuskan |
| 2026-11-06 | `program/README.md` dibuat sebagai peta notebook: urutan baca dan jalan, tujuan tiap notebook, serta penanda alur utama dan simpanan | Diputuskan |
| 2026-11-08 | Ditutup (keputusan 45): `CLAUDE.md` dan `PROJECT_GUIDE.md` tetap dilacak, tag `arsip-v1` dihapus dari GitHub, 8 branch yang sudah di-merge dihapus, dan path absolut di notebook asli diganti | Diputuskan |
| 2026-11-08 | Kalimat keterbatasan wajib (bagian 7) diubah atas permintaan pengguna menjadi "... satu pelanggan. Namun audit menemukan ..." supaya lebih mengalir, beserta versi Inggrisnya ("However, an audit found ..."). Diterapkan di guide, demo (`src/texts.py`), `src/train.py`, `src/track.py`, `src/monitor.py`, README, `docs/monitoring.md`, `program/README.md`, dan `ringkasan_temuan/01_struktur_data.md`. Notebook di `program/` tidak diubah (keputusan 36) | Diputuskan |
| 2026-11-06 | Interpretasi model memakai permutation importance dan SHAP bawaan XGBoost (keputusan 34). `shap` 0.49.1 tidak cocok dengan XGBoost 3.2.0, jadi tidak masuk requirements | Diputuskan |
| | `shap` 0.49.1, `numba`, `llvmlite`, dan `slicer` tetap terpasang di `ds_env` atas keputusan pengguna (keputusan 38), tetapi tidak ada di requirements dan tidak di-import kode project. Demo memakai SHAP bawaan XGBoost. `shap` dipakai lagi hanya jika versi barunya sudah mendukung XGBoost 3, dan saat itu harus dimasukkan ke requirements lebih dulu | **Terbuka** |
| 2026-11-06 | Analisis error memakai data latih, threshold 1:5, dan suara mayoritas, tanpa mengubah model (keputusan 35) | Diputuskan |
| | Bahan tabel pembeda README Fase 7, dari pencarian kata kunci dan bagian prapemrosesan keempat jurnal. Kelima penanda baris janggal (keputusan 5–9) tidak dibahas secara eksplisit oleh jurnal mana pun. Damuri dkk. mempertahankan 314 baris berfitur identik, yang pada data mentah terdiri atas 300 duplikat persis dan 14 baris konflik label. Wang dkk. menghapus 300 duplikat dan mengklaim tidak ada outlier Tukey, padahal dengan rumus yang sama data bersih kita punya 44–333 baris di luar batas per kolom numerik. Information mengganti outlier dengan rata-rata data latih dan menganggap `Charge Amount` 0–10. PLOS ONE tidak membahas pembersihan data. Angka-angka ini dihitung ulang dengan kode sebelum masuk README | **Terbuka** |
| 2026-11-06 | Logika yang dipakai ulang dipindah ke `src/` (`config`, `data`, `model`, `threshold`) dengan test di `tests/`. Model final dilatih pada 2.280 baris latih. `pytest` dan `ruff` dipasang (keputusan 36) | Diputuskan |
| 2026-11-06 | `src/train.py` melatih ulang Pipeline final dengan satu perintah, memeriksa threshold terhadap `docs/threshold_skenario.csv` tanpa menimpanya, lalu menyimpan model dan metadata ke `models/` (tidak dilacak Git). `joblib==1.5.3` masuk `requirements.txt`. Fase 3 memenuhi DoD | Diputuskan |
| 2026-11-06 | Fase 3 di-merge ke `main` lewat PR #2. Fase 4 memakai MLflow lokal dengan 4 run inti dan registry (keputusan 37) | Diputuskan |
| 2026-11-06 | `src/evaluate.py` dan `src/track.py` dibuat. MLflow 3.18 menyimpan model dengan `skops` dan menolak tipe XGBoost, jadi hanya `xgboost.core.Booster` dan `xgboost.sklearn.XGBClassifier` yang ditandai tepercaya (`skops_trusted_types`), bukan beralih ke `cloudpickle`. Fase 4 memenuhi DoD | Diputuskan |
| 2026-11-06 | Fase 4 di-merge ke `main` lewat PR #3. Fase 5 memakai demo Streamlit di Streamlit Community Cloud dengan Python 3.12 (keputusan 38) | Diputuskan |
| 2026-11-06 | Requirements dipisah: `requirements.txt` hanya untuk demo, dan library notebook pindah ke `requirements-dev.txt`. `.venv` Python 3.12.7 dibuat dari `requirements-dev.txt`. Ditambahkan `src/schema.py`, `src/predict.py`, `streamlit_app.py`, dan 20 test. Skor model untuk 200 baris latih identik di Python 3.10 dan 3.12 | Diputuskan |
| 2026-11-06 | Demo lokal dijalankan hanya untuk komputer sendiri (`--server.address 127.0.0.1`). Saat uji pertama, Streamlit menerima koneksi dari semua jaringan sehingga Windows Firewall meminta izin, dan dua aturan masuk untuk Python 3.12 pada profil Public yang terbentuk dari peringatan itu sudah dihapus atas persetujuan pengguna | Diputuskan |
| 2026-11-06 | Env conda `ds_env312` (Python 3.12.16) dibuat dan diisi dari `requirements-dev.txt`. 46 test lulus dan skor model identik dengan `ds_env`. Folder `.venv` (dari Python 3.12 sistem) dihapus (keputusan 39) | Diputuskan |
| 2026-11-06 | `.gitattributes` ditambahkan dengan `docs/*.csv text eol=lf`. Sebelumnya `core.autocrlf=true` mengubah `docs/threshold_skenario.csv` ke CRLF saat pindah branch, sehingga hash-nya di Windows (`1697bccd...`) berbeda dari isi repo (`38f68339...`), walaupun isinya sama. `dataset/` sengaja tidak diatur supaya data mentah tidak tersentuh | Diputuskan |
| 2026-11-06 | Langkah 5b: CI GitHub Actions dibuat di `.github/workflows/ci.yml` (keputusan 40). Perbaikan tampilan demo dibahas setelah CI, sebelum deploy | Diputuskan |
| 2026-11-06 | Run CI pertama (commit `20818d2`) hijau dalam sekitar 2 menit: `pip check` bersih, `ruff` lulus, dan 46 test lulus di Linux dengan Python 3.12. Angka test sama dengan hasil di Windows | Diputuskan |
| 2026-11-07 | Mockup HTML demo (`mockup/`, tidak dilacak Git) dinilai, lalu pengguna memilih memperbaiki tampilan Streamlit yang ada. Setelah 16 putaran peninjauan, tampilan demo dikunci (keputusan 41–43). Tiap putaran dicadangkan di `cadangan/` (tidak dilacak Git). 72 test lulus di `ds_env312` | Diputuskan |
| 2026-11-07 | Info pembuat diisi (Arthur Pendragon, tautan GitHub). Fase 5 di-merge ke `main` lewat PR #4 (merge commit `2091b72`) setelah CI hijau. Auto-merge GitHub tidak diizinkan di repo ini | Diputuskan |
| 2026-11-08 | Demo di-deploy pengguna ke Streamlit Community Cloud: https://churn-risk-priority.streamlit.app/, dari branch `main` dengan Python 3.12.16. Log build bersih: paket dipasang dengan `uv` dari `requirements.txt`, Streamlit Cloud mengganti `pyarrow` 25.0.1 dengan 24.0.0 (masalah segfault yang diketahui), dan memberi peringatan karena `pyproject.toml` juga terdeteksi, tetapi tetap memakai `requirements.txt`. Halaman awal memberi skor 0,002 dan skor minimal 0,060 untuk nilai median, sama dengan hasil lokal. Fase 5 memenuhi DoD | Diputuskan |
| 2026-11-08 | Ditutup: muat pertama demo di Streamlit Cloud sempat lebih dari 2 menit, padahal pelatihan lokal sekitar 0,2 detik. Setelah XGBoost di demo dibatasi ke 1 thread (`DEMO_N_JOBS` di `src/predict.py`, PR #6, merge `f9e0077`), log server mencatat `model siap dalam 1.0 detik, cpu_count=16`, dan halaman tampil sekitar 10 detik setelah dibuka. Server melaporkan 16 inti, sehingga dugaan thread yang berebut jatah CPU kecil didukung, walau log versi lama tidak punya angka pembanding. Skor dengan 1 thread persis sama dengan model bawaan (diuji), jadi keputusan 31 tidak berubah. Log juga mencatat `KeyError: 'src.config'` sekali saat Streamlit Cloud menarik kode baru di tengah sesi pengunjung, lalu aplikasi berjalan normal. Setelah merge ke `main`, sebaiknya tekan Reboot app di Manage app | Diputuskan |
| | `xgboost` di Linux ikut memasang `nvidia-nccl-cu12` (335 MB) yang tidak dipakai demo. Bisa dipertimbangkan paket `xgboost-cpu` nanti, setelah dicek versi dan dampaknya ke CI | **Terbuka** |
| 2026-11-08 | Pelajaran dari Fase 6: target peran (Data Analyst, Data Scientist, ML Engineer/MLOps) tidak pernah ditulis di guide ini, sehingga kedalaman fase tidak dicek terhadap tujuan. Mulai sekarang target peran dicatat di bagian 1, dan aturan ini ditambahkan ke `ai-playbooks` (template `PROJECT_GUIDE` dan `CLAUDE.global.md`) untuk project berikutnya | Diputuskan |
| 2026-11-08 | Fase 6 di branch `fase6-monitoring`: `src/simulate.py`, `src/score_batch.py`, `src/monitor.py`, `docs/monitoring.md`, dan 6 test (keputusan 44). `monitoring/` dan `.claude/` masuk `.gitignore`. Folder lokal `cadangan/` dan `mockup/` dipindah ke Recycle Bin | Diputuskan |
| 2026-11-08 | Fase 6 di-merge ke `main` lewat PR #8 (`a4d3dec`). Target peran project ditetapkan: Data Scientist (utama) + ML Engineer/MLOps (pendukung), atas saran AI yang disetujui pengguna. Alasan: bagian data science (audit pola berulang, validasi, rentang skor, threshold biaya, interpretasi) paling kuat dan khas, MLOps cukup kuat tetapi versi ringan, dan sisi analyst paling tipis karena tidak ada dashboard BI atau SQL | Diputuskan |
| 2026-11-08 | `docs/ringkasan_non_teknis.md` ditulis dengan gaya bercerita untuk pembaca awam: istilah diperkenalkan sebelum dipakai, angka ditulis sebagai "X dari 100 pelanggan", dan alasan kenapa temuan belum membuktikan sebab-akibat dijelaskan. Semua angka dihitung ulang dengan kode, dan churn rate per kelompok ditambahkan ke temuan 12. README dan `docs/README.md` menautkan ringkasan ini | Diputuskan |

---

## 12. Aturan Khusus Project Ini

> Prinsip umum sudah dimuat dari `~/.claude/CLAUDE.md`.

**Wajib:**
- Semua keputusan analisis (pembersihan, fitur, validasi, metrik, model) **ditanyakan ke pengguna dulu**. AI mengusulkan, pengguna memutuskan.
- Temuan hanya ditulis di bagian 3 setelah dihitung dari kode.

**Dilarang:**
- Memakai atau mengutip hasil dari tag Git `arsip-v1` kecuali pengguna memintanya.
