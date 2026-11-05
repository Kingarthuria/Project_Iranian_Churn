# Ringkasan temuan: segmentasi, Value at Risk, dan executive summary

- **Tanggal:** 2026-11-04
- **Data:** 2.850 baris setelah 300 duplikat persis dihapus
- **Sumber analisis:** `program/EDA_Project_Churn_v2.ipynb`, bagian Deep Dive Business Insights

## Keputusan

- **Sel validasi:** disederhanakan menjadi saringan eksploratif, dengan label "lolos saringan".
- **Value at Risk:** memakai 3 sinyal, yaitu `Complains=1`, `Status=2`, dan `Seconds_of_Use` Rendah, ditambah insight nilai. Bagian ini kemudian diganti dengan "Pertanyaan Bisnis" (lihat `08_pertanyaan_bisnis.md`), dan angka 3 sinyalnya tetap dipakai.
- **Rekomendasi bisnis:** ditulis sebagai hipotesis yang perlu diuji.

## Temuan utama

### 1. Sel validasi lama punya dua masalah kode

- **Uji signifikansi memakai kolom asli:** `Customer_Value` (2.654 nilai unik) dan `Frequency_of_SMS` (405 nilai unik) menghasilkan p = 0,96 dan 1,00, padahal setelah dibagi kuartil p < 0,001. Akibatnya, 113 dari 114 kombinasi yang gagal memang gagal karena ini.
- **Pengecekan `is False` tidak bekerja pada hasil numpy:** label "tidak stabil" dan "fitur tidak signifikan" tidak pernah muncul.

Selain itu, stabilitas hanya dicek dengan satu split, p-value menguji fitur dan bukan kombinasinya, dan kandidat dipilih dari seluruh data.

### 2. Hasil saringan baru

Syaratnya minimal 50 baris, minimal 1% data, dan selisih train dan test paling besar 10 poin persen di setiap dari 20 split.

| Kelompok | Kandidat | Lolos |
|---|---|---|
| Churn tinggi (≥ 80%) | 16 | 5 |
| Churn rendah (≤ 5%) | 186 | 166 |
| Total | 202 | 171 |

Saringan ini tidak mengoreksi banyaknya kombinasi, jadi lolos bukan bukti pola berlaku di data baru. Kombinasi yang tidak lolos juga belum tentu tidak ada polanya. Contohnya, `Complains` x `Status 2` (89,3%, n = 149) tidak lolos karena selisih terbesarnya 13,0 poin.

Hasil tetap bergantung pada seed dan cara menghitung split yang sampelnya kecil. Pada pengecekan sebelumnya dengan seed 0–19, kombinasi churn tinggi yang lolos semua seed hanya 3. Notebook memakai seed `180915 + i`.

### 3. Angka yang diperbaiki

| Narasi lama | Hasil hitung ulang |
|---|---|
| Selisih churn komplain 67 poin | 72,8 poin. Angka 67,0 adalah selisih terhadap rata-rata |
| 18 dari 20 kombinasi teratas melibatkan komplain | 19 dari 20 |
| 10 dari 11 kombinasi tervalidasi melibatkan komplain | Semua 5 kombinasi churn tinggi yang lolos melibatkan komplain |
| `Status 2` x `Seconds of Use` Tinggi tervalidasi | n = 28, jadi tidak memenuhi syarat sampel |
| Pemakaian rendah 2,0–2,2x rata-rata | 1,9–2,2x |
| Komplain x Plan 2 tidak tersedia | 31,6% (6 dari 19 baris) |
| Dataset 3.150 pelanggan | Analisis memakai 2.850 baris |

Klaim clustering dan bagian "pelanggan baru" juga dihapus, karena kodenya tidak ada dan klaimnya bertentangan dengan keputusan.

### 4. Asosiasi komplain tidak berlaku merata

Komplain dengan `Seconds_of_Use` Sangat Tinggi punya churn rate 0% (0 dari 22 baris). Kelompok ini kecil, tetapi menunjukkan bahwa klaim "di semua kombinasi" terlalu luas.

### 5. Value at Risk dengan 3 sinyal

| Metrik | 4 sinyal (lama) | 3 sinyal (baru) |
|---|---|---|
| Baris | 1.145 (40,2%) | 992 (34,8%) |
| Churn rate | 36,4% | 40,8% |
| Porsi baris churn | 93,5% | 90,8% |
| Porsi `Customer_Value` | 17,7% | 11,0% |
| `Customer_Value` pada baris churn | 50.122 | 48.899 |

Irisan ketiga sinyal ada 59 baris, dengan churn rate 100,0%. Angka ini deskriptif, karena sinyalnya dipilih setelah melihat churn pada data yang sama.

### 6. Insight baru: churn terkonsentrasi pada nilai rendah

Baris churn hanya memegang 4,4% total `Customer_Value`, dengan median 102,6 berbanding 271,5 pada baris tidak churn. `Customer_Value` tidak punya rumus dan satuan yang dijelaskan dokumentasi UCI, jadi ini dibaca sebagai porsi relatif, bukan uang.

## Hipotesis yang perlu diuji

- Menangani komplain lebih cepat bisa menurunkan churn.
- Baris non-aktif bisa menjadi kelompok awal program retensi, setelah cara `Status` ditentukan dipastikan.
- Mendorong penggunaan bisa menurunkan churn, tetapi penggunaan rendah bisa juga hanya gejala.

## Asal angka

Angka saringan baru, Value at Risk, dan insight nilai ada di notebook EDA. Angka lama dan pengecekan masalah kode (termasuk p-value kolom asli dan seed 0–19) berasal dari output lama atau pengecekan terpisah, dan tidak tersimpan di notebook.
