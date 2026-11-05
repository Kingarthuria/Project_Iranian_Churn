# Ringkasan temuan: struktur data Iranian Churn

- **Tanggal:** 2026-11-04
- **Status:** audit disimpan sebagai simpanan. Project dilanjutkan dengan asumsi UCI (lihat "Keputusan")
- **Sumber analisis:** `program/analisis_duplikat_v2.ipynb`
- **Rincian verifikasi:** `ringkasan_temuan/02_verifikasi_50_kelompok.md`

## Kesimpulan

Dataset ini tampaknya **bukan 3.150 pelanggan independen**, melainkan sekitar 50 profil dasar yang masing-masing muncul 63 kali dengan variasi berpola sama. Ini tidak sejalan dengan keterangan UCI bahwa setiap baris mewakili satu pelanggan. Penyebabnya belum diketahui.

## Bukti utama

| Bukti | Hasil |
|---|---|
| Variasi yang dijelaskan sisa bagi 50 baris | `Seconds of Use` 99,1%, `Customer Value` 98,0%, `Churn` 92,7% (batas urutan acak sekitar 2%) |
| Tetangga terdekat pada jarak kelipatan 50 | 88,6% baris (urutan acak 2,0%) |
| Jarak yang lolos uji permutasi | Semua dari 60 kelipatan 50, dan 404 dari 2.940 jarak lainnya |
| Nilai yang mengikuti selisih terbanyak di bloknya | `Subscription Length` 99,9%, `Frequency of use` 94,4%, `Seconds of Use` 91,1% |
| `Churn` per kelompok | 41 kelompok ≤ 5%, 7 kelompok ≥ 95%, 2 kelompok di antaranya |
| Pergeseran `Subscription Length` dibanding blok 1.050 baris pertama | Blok ketiga +2 pada 1.050 baris, blok kedua −2 pada 1.046 baris |

## Dampak

### 1. AUC di atas 0,9 kemungkinan besar terlalu optimistis

CV acak melatih dan menguji pada profil yang sama. Angka berikut adalah ROC-AUC dari CV 5x5:

| Model | CV acak | Grup per kelompok |
|---|---|---|
| Logistic Regression | 0,932 (0,913–0,959) | 0,841 (0,607–1,000) |
| RandomForest | 0,984 (0,976–0,991) | 0,790 (0,369–0,998) |

Angka grup ini bukan skor final. Rentangnya sangat lebar karena hasil tiap fold bergantung pada segelintir kelompok churn yang masuk test.

### 2. Duplikat bukan masalah utamanya

- **Jumlah:** ada 300 duplikat persis, terdiri dari 253 baris beraktivitas dan 47 baris beraktivitas nol.
- **Definisi:** baris beraktivitas nol berarti `Seconds of Use`, `Frequency of use`, dan `Frequency of SMS` semuanya 0.
- **Asal:** semua 365 pasangan kembar beraktivitas berada di kelompok yang sama, jadi duplikat ini terkait struktur 50 kelompok.
- **Tafsiran:** label "segmen pasif" di notebook lama tidak didukung bukti.
- **Keterbatasan penghapusan:** menghapus 253 atau 300 baris tidak membuat sisa baris menjadi independen.

### 3. Penghapusan duplikat mengubah profil data pada kedua versi

| Pemeriksaan | `drop_300` | `drop_253` |
|---|---|---|
| Kolom dengan \|SMD\| > 0,2 | 4 kolom | Tidak ada |
| Pergeseran rata-rata terbesar | 0,024 SD | 0,015 SD |
| Classifier test dengan grup per kelompok | AUC 0,658 (0,599–0,741) | AUC 0,646 (0,550–0,713) |

Perbandingan per kolom saja tidak menangkap perbedaan pada `drop_253`.

### 4. Hasil yang perlu dibaca hati-hati

- Notebook EDA lama memperlakukan tiap baris sebagai pelanggan independen, jadi p-value di dalamnya bisa terlalu kecil.
- Kelompok C dari rencana audit tidak dijalankan setelah keputusan pengguna.

## Yang belum diketahui

- Penyebab struktur ini: data sintetis, augmentasi, atau proses lain.
- Performa model yang sebenarnya pada profil yang benar-benar baru.

## Keputusan

Pengguna memutuskan untuk melanjutkan project dengan asumsi tiap baris adalah satu pelanggan, mengikuti UCI dan keempat paper di `jurnal/`. Hasil akhir memuat kalimat keterbatasan berikut:

> Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis.

## Kesimpulan untuk pembaca umum

Data ini disebut berisi 3.150 pelanggan yang berbeda, tetapi hasil analisis menunjukkan data tersebut lebih mirip sekitar 50 pola pelanggan yang diulang 63 kali dengan sedikit perubahan angka, seperti memfotokopi 50 formulir lalu mengubah sedikit isinya. Akibatnya, saat diuji dengan cara biasa, model terlihat sangat pintar, padahal ia sering diuji dengan pola yang sudah pernah dilihatnya, seperti murid yang mendapat soal ujian yang mirip dengan latihannya. Saat diuji dengan pola yang benar-benar baru, skor model turun (Logistic Regression dari 0,93 menjadi 0,84, RandomForest dari 0,98 menjadi 0,79) dan hasilnya sangat naik-turun, jadi kemampuan aslinya belum bisa dipastikan. Kami belum tahu mengapa data ini berpola seperti itu, sehingga belum bisa menyebut data ini palsu atau buatan. Yang sudah jelas, skor tinggi dari pengujian biasa pada data ini tidak boleh langsung dipercaya.
