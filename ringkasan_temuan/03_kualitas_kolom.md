# Ringkasan temuan: kualitas kolom

- **Tanggal:** 2026-11-04
- **Status:** berjalan, catatan baru ditambahkan di file ini setelah diputuskan
- **Data:** 2.850 baris setelah 300 duplikat persis dihapus
- **Asal angka:** `program/analisis_duplikat_v2.ipynb`, bagian "Bukti Kualitas Kolom" dan "Ringkasan dampak pada baris"
- **Kelompok:** kelompok audit, yaitu sisa bagi 50 dari posisi baris (lihat `02_verifikasi_50_kelompok.md`)

## 0. 14 grup dengan fitur identik tetapi label berbeda

**Keputusan: dipertahankan dan dicatat.** Sesuai asumsi kerja, baris ini dibaca sebagai pelanggan berbeda dengan hasil berbeda, dan tidak ada dasar untuk memilih label yang benar.

- **Temuan:** setelah 300 duplikat persis dihapus, masih ada 14 grup dengan 13 fitur identik tetapi `Churn` berbeda.
- **Aktivitas:** 11 grup melibatkan baris beraktivitas nol, dan 3 grup beraktivitas.
- **Keterbatasan:** ada sedikit noise pada label, dan pasangan ini masih bisa terpisah ke train dan test.

## 1. `Charge Amount` bernilai 10

**Keputusan: dipertahankan dan dicatat.**

- **Temuan:** ada 7 baris bernilai 10, padahal dokumentasi menyebut rentang 0–9.
- **Pola:** nilainya menyambung dari nilai di bawahnya. Median `Seconds of Use` naik dari 10.695 pada nilai 9 menjadi 10.855 pada nilai 10, dan churn rate keduanya 0%.
- **Asal baris:** semua 7 baris berasal dari kelompok 23, jadi bukan 7 bukti terpisah.
- **Dampak:** korelasi Spearman dengan `Churn` adalah −0,2478, dan −0,2470 tanpa baris itu.
- **Jurnal:** `information-17-00680-v2.pdf` menyebut 11 kelas (0–10), sedangkan `3757110.3757152.pdf` menyebut 0–9. Dua paper lain tidak menyebut rentang, dan tidak ada yang membahas perbedaannya.

Paper diperiksa lewat pencarian kata kunci dan tabel variabel, bukan dibaca penuh.

## 2. `Distinct Called Numbers` lebih besar dari `Frequency of use`

**Keputusan: dipertahankan dan dicatat.** Narasi tidak boleh menganggap `Distinct Called Numbers` pasti lebih kecil dari `Frequency of use`.

- **Temuan:** ada 111 baris (3,89%). Selisihnya 1 sampai 44, dengan median 18.
- **Arti kolom belum jelas:** UCI tidak menjelaskan kedua kolom ini di data dictionary kita, dan definisi di paper berbeda-beda.

| Paper | `Frequency of use` | `Distinct Called Numbers` |
|---|---|---|
| `3757110.3757152.pdf` | Total jumlah panggilan | Jumlah nomor berbeda yang dipanggil |
| `information-17-00680-v2.pdf` | Berapa kali pelanggan menelepon | Nomor unik yang dihubungi sejak mulai berlangganan |
| `journal.pone.0303881.pdf` | Jumlah panggilan diterima | Nomor berbeda yang dihubungi |
| `102601.pdf` | Frekuensi penggunaan layanan | Nomor berbeda yang dihubungi |

- **Asal baris:** semuanya berasal dari 13 kelompok, dan tiga kelompok teratas menyumbang 70,3%.
- **Nilai mustahil:** tidak ada baris dengan `Frequency of use` = 0 yang punya `Distinct Called Numbers` > 0.

| Ukuran | 111 baris ini | Baris lainnya |
|---|---|---|
| Churn rate | 21,6% | 15,4% |
| Status non-aktif | 39,6% | 23,4% |
| Median `Seconds of Use` | 1.170 | 3.183 |
| Median `Customer Value` | 81,2 | 244,4 |

Korelasi Spearman dengan `Churn`, untuk semua baris dan tanpa 111 baris ini:

| Kolom | Semua baris | Tanpa 111 baris |
|---|---|---|
| `Distinct Called Numbers` | −0,2908 | −0,2784 |
| `Frequency of use` | −0,3359 | −0,3332 |

## 3. Baris dengan semua aktivitas nol

**Keputusan: dipertahankan dan dicatat.** Penanda `is_zero_activity` bisa dibahas nanti saat feature engineering.

- **Temuan:** ada 85 baris (2,98%) dengan `Seconds of Use`, `Frequency of use`, dan `Frequency of SMS` semuanya 0. Pada data mentah jumlahnya 132.
- **Konsistensi:** semua 85 baris juga punya `Customer Value`, `Distinct Called Numbers`, dan `Call Failure` = 0. Hanya 2 baris yang `Charge Amount`-nya di atas 0.
- **Asal baris:** semuanya berasal dari 14 kelompok, dan tiga kelompok teratas menyumbang 52,9%.
- **Kombinasi janggal:** 26 baris berstatus aktif tanpa aktivitas, dan UCI tidak menjelaskan cara `Status` ditentukan. Selain itu, 13 baris punya komplain tanpa aktivitas.
- **Jurnal:** dari pencarian kata kunci, tidak ada paper yang membahas baris ini.

| Ukuran | Baris nol | Baris lainnya |
|---|---|---|
| Churn rate | 51,8% | 14,5% |
| Status non-aktif | 69,4% | 22,6% |
| Ada komplain | 15,3% | 7,8% |
| Median `Subscription Length` | 32 | 35 |

Hubungan ini asosiatif, bukan kausal.

## 4. `Subscription Length` di bawah 9

**Keputusan: dipertahankan dan dicatat.** Tidak ada klaim tentang pelanggan baru, dan fitur per bulan nanti tidak boleh menganggap semua baris mencakup 9 bulan penuh.

- **Temuan:** ada 54 baris (1,89%) dengan nilai 3 sampai 8. Pada data mentah jumlahnya 57.
- **Sebaran:** nilainya naik bertahap tanpa lompatan di angka 9.
- **Satuan belum pasti:** UCI tidak menjelaskan kolom ini di data dictionary kita. `3757110.3757152.pdf` dan `information-17-00680-v2.pdf` membacanya sebagai bulan.
- **Asal baris:** 26 baris dari kelompok 49 (churn 100%), 25 baris dari kelompok 48 (churn 0%), dan 3 baris dari kelompok 46 serta 47 (churn 0%).
- **Churn rate:** 48,1% berbanding 15,0% pada baris lainnya, tetapi angka ini hampir seluruhnya ditentukan oleh kelompok 49.
- **Dampak:** korelasi Spearman dengan `Churn` adalah −0,0331, dan −0,0038 tanpa 54 baris ini.

## 5. `Age` dan `Age Group` berisi informasi yang sama

**Keputusan: `Age Group` dipakai untuk modeling dan `Age` tidak masuk fitur model.** Kolom `Age` tetap ada di data dan EDA.

- **Temuan:** pasangannya tepat satu-satu pada 2.850 baris (15→1, 25→2, 30→3, 45→4, 55→5). Korelasi Spearman 1,0 dan Pearson 0,9609.
- **Arti `Age`:** hanya punya 5 nilai, jadi bukan usia sebenarnya. UCI tidak menjelaskan kolom ini di data dictionary kita.
- **Jurnal:** `3757110.3757152.pdf` dan `information-17-00680-v2.pdf` membuang `Age`. `102601.pdf` tampaknya memakai keduanya.
- **Cara membaca:** korelasi Spearman `Age Group` dengan `Churn` hanya 0,0049, tetapi hubungannya tidak searah, jadi angka itu tidak berarti usia tidak berhubungan dengan churn.

| `Age Group` | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Baris | 112 | 921 | 1.296 | 367 | 154 |
| Churn rate | 0,0% | 17,0% | 16,4% | 20,2% | 1,3% |

## 6. Hampir-duplikat

**Keputusan: dipertahankan dan dicatat.** Sesuai asumsi kerja, tidak ada dasar untuk menyebut baris ini duplikat.

- **Temuan:** setelah deduplikasi persis, 75 baris beraktivitas masih punya pasangan yang berbeda di satu kolom saja.
- **Keterbatasan:** baris yang sangat mirip masih bisa terpisah ke train dan test.

| Kolom yang berbeda | Semua pasangan | Keduanya beraktivitas |
|---|---|---|
| `Subscription Length` | 335 | 39 |
| `Complains` | 27 | 18 |
| `Churn` | 14 | 3 |
| `Tariff Plan` | 4 | 4 |
| `Status` | 2 | 0 |
| `Charge Amount` | 1 | 0 |

## 7. Kerapian kode di `program/EDA_Project_Churn_v2.ipynb`

**Keputusan: diperbaiki.** Output teks tidak berubah selain nama kolom dan lebar kolom tabel.

- **Nama kolom:** `Call__Failure`, `Subscription__Length`, dan `Charge__Amount` diganti menjadi satu underscore.
- **Import dihapus:** `CatBoostClassifier`, `Pool`, `LinearSegmentedColormap`, dan `stats`. `warnings` dipertahankan karena terpakai.
- **Requirements:** `catboost` dihapus dari `requirements.txt`, dan bisa ditambahkan lagi jika dipakai saat modeling. Notebook asli masih mengimpor `catboost`, jadi notebook itu butuh paket tersebut jika dijalankan di environment baru.
