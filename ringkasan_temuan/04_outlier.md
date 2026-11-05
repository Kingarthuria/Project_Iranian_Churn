# Ringkasan temuan: univariat dan outlier

- **Tanggal:** 2026-11-04
- **Data:** 2.850 baris setelah 300 duplikat persis dihapus
- **Sumber analisis:** `program/EDA_Project_Churn_v2.ipynb`, bagian Univariate Analysis dan Outlier. Angka per kelompok ada di `program/analisis_duplikat_v2.ipynb`, bagian "Asal Baris Outlier"
- **Kelompok:** kelompok audit, yaitu sisa bagi 50 dari posisi baris (lihat `02_verifikasi_50_kelompok.md`)

## Keputusan

- **Outlier:** semua dipertahankan. Tidak ada baris yang dihapus dan tidak ada nilai yang dipotong, karena tidak ada bukti bahwa nilainya salah.
- **Rencana *flag*:** dibatalkan untuk sekarang. Bisa dibahas lagi saat feature engineering, dengan batas yang dihitung di dalam fold.
- **Narasi:** klaim yang terlalu kuat ditulis ulang.
- **Notebook EDA berdiri sendiri:** tidak merujuk file lain dan tidak memuat analisis kelompok posisi. Rujukan UCI dipertahankan. Kalimat keterbatasan tetap wajib di README dan laporan model.

## Hasil outlier (IQR dari seluruh data)

| Fitur | Outlier | Kelompok asal | Churn rate outlier | Churn rate normal | Baris churn | Kelompok asal churn |
|---|---|---|---|---|---|---|
| `Call_Failure` | 44 | 4 | 20,5% | 15,6% | 9 | 22 |
| `Subscription_Length` | 208 | 6 | 28,4% | 14,6% | 59 | 49 |
| `Seconds_of_Use` | 189 | 4 | 0,0% | 16,8% | 0 | Tidak ada |
| `Frequency_of_use` | 118 | 3 | 0,0% | 16,3% | 0 | Tidak ada |
| `Frequency_of_SMS` | 333 | 9 | 0,0% | 17,7% | 0 | Tidak ada |
| `Distinct_Called_Numbers` | 82 | 2 | 0,0% | 16,1% | 0 | Tidak ada |
| `Customer_Value` | 104 | 3 | 0,0% | 16,2% | 0 | Tidak ada |

## Temuan utama

### 1. Klaim "pelanggan baru rentan churn" tidak didukung

Notebook lama menyebut baris dengan `Subscription_Length` di bawah 15,5 lebih mungkin churn (OR 2,307). Padahal semua 59 baris churn di grup itu berasal dari kelompok audit 49.

| Pembanding | Churn rate |
|---|---|
| Di bawah 15,5, semua kelompok | 28,4% |
| Di bawah 15,5, tanpa kelompok 49 | 0,0% |
| Baris lainnya, tanpa kelompok 49 | 14,6% |

### 2. Churn 0% adalah fakta deskriptif, bukan bukti loyalitas

Lima fitur penggunaan tidak punya baris churn pada grup outlier, tetapi outlier-nya hanya berasal dari 2 sampai 9 kelompok. P-value di bawah 0,001 bisa terlalu kecil karena independensi antarbaris tidak terjamin.

Uji kasar per kelompok tidak signifikan untuk fitur yang bisa diuji (Fisher p ≥ 0,41). Jumlah kelompoknya sedikit, jadi ini bukan bukti bahwa hubungannya tidak ada. `Call_Failure` tidak bisa diuji karena tidak ada kelompok yang mayoritas barisnya outlier. Uji ini ada di `program/analisis_duplikat_v2.ipynb`, bagian "Bukti Pelengkap Outlier".

### 3. Rencana *flag* berisiko

Batas dan pilihan *flag* ditentukan setelah melihat churn pada seluruh data, sehingga bisa membuat skor terlalu optimistis. *Flag* merah pada dasarnya menandai kelompok 49. Gabungan *flag* hijau mencakup 548 baris dari 14 kelompok, tanpa baris churn.

### 4. Perubahan narasi di notebook v2

- Klaim pelanggan baru, "bukan kebetulan", "loyal", dan "threshold siap dipakai bisnis" dihapus dari sel outlier.
- Label `Insight` kini memakai p-value dan arah selisih.
- Tafsir p-value `Call_Failure` diperbaiki.
- Batas di sel irisan outlier kini dihitung dari kode.
- `Subscription_Length` ditulis deskriptif (28,4% berbanding 14,6%), tanpa klaim tentang pelanggan baru dan tanpa pembahasan kelompok.
- Uji statistik ditulis mengasumsikan tiap baris independen, mengikuti dokumentasi UCI.

## Yang masih perlu ditinjau

Sel setelah bagian outlier masih memuat klaim serupa, termasuk soal pelanggan baru. Narasi itu ditinjau di bagian berikutnya.
