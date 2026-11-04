# Ringkasan temuan: hubungan fitur dengan churn

- **Tanggal:** 2026-11-04
- **Data:** 2.850 baris setelah 300 duplikat persis dihapus
- **Sumber analisis:** `program/EDA_Project_Churn_v2.ipynb`, bagian Feature Relationship Analysis

## Keputusan

- **Narasi:** angka dicocokkan dengan output, rujukan yang tidak ada dihapus, dan klaim dilunakkan menjadi asosiasi.
- **Mutual Information (MI):** dilaporkan dengan rata-rata, minimum, dan maksimum dari 10 seed.
- **Fitur:** tabel menjadi kandidat tanpa putusan. `Age_Binning` tidak masuk fitur model, dan `Age_Group` dipakai.
- **`Status` dan `Complains`:** risiko leakage dicatat, dan modeling membandingkan hasil dengan dan tanpa kedua fitur.

## Temuan utama

### 1. Angka di narasi lama tidak cocok dengan output

| Klaim lama | Hasil hitung ulang |
|---|---|
| `Customer_Value` dan `Frequency_of_SMS` berkorelasi 0,92 | Pearson 0,923, Spearman 0,776 |
| `Age_Group` dan `Age_Binning` "korelasi sempurna 0,96" | Spearman 1,000, Pearson 0,961 |
| Heatmap memakai Spearman dan Pearson | Hanya Spearman yang ada di kode |
| `Call_Failure` punya MI 0,000000, "noise mutlak" | Rata-rata 10 seed 0,0015 (0,0000–0,0084) |

Narasi lama juga merujuk "FASE 5", "clustering korelasi terpisah", "notebook selanjutnya", dan "draft sebelumnya", yang tidak ada di notebook.

### 2. MI tidak stabil antar-seed

| Fitur | Rata-rata | Minimum | Maksimum |
|---|---|---|---|
| `Seconds_of_Use` | 0,1156 | 0,1103 | 0,1192 |
| `Status` | 0,1040 | 0,1040 | 0,1040 |
| `Complains` | 0,1023 | 0,1023 | 0,1023 |
| `Frequency_of_use` | 0,0894 | 0,0822 | 0,0949 |
| `Customer_Value` | 0,0868 | 0,0829 | 0,0892 |
| `Frequency_of_SMS` | 0,0523 | 0,0432 | 0,0687 |
| `Distinct_Called_Numbers` | 0,0497 | 0,0414 | 0,0601 |
| `Charge_Amount` | 0,0371 | 0,0371 | 0,0371 |
| `Subscription_Length` | 0,0224 | 0,0150 | 0,0306 |
| `Age_Group` | 0,0146 | 0,0146 | 0,0146 |
| `Tariff_Plan` | 0,0079 | 0,0079 | 0,0079 |
| `Call_Failure` | 0,0015 | 0,0000 | 0,0084 |

Rentang `Frequency_of_use` dan `Customer_Value` tumpang tindih, jadi urutan keduanya tidak dibaca. Rentang `Frequency_of_SMS` dan `Distinct_Called_Numbers` juga tumpang tindih.

Perubahan skor antara notebook asli dan v2 kini lebih mudah dijelaskan: skor fitur kontinu berubah menurut seed. Perbedaan environment belum bisa dikesampingkan.

### 3. `Age_Group` punya asosiasi, tetapi polanya tidak searah

Kruskal-Wallis (p = 0,796) dan Point-Biserial (p = 0,753) tidak mendeteksi hubungan, tetapi chi-square jelas (p < 0,001).

| `Age_Group` | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Churn rate | 0,0% | 17,0% | 16,4% | 20,2% | 1,3% |

Label lama "tidak ada hubungan, kandidat DROP" di sel Kruskal-Wallis diganti menjadi "tidak terdeteksi".

### 4. `Customer_Value` sangat bisa dijelaskan oleh fitur lain

| Prediktor regresi linier | R-kuadrat |
|---|---|
| `Frequency_of_SMS` | 0,852 |
| `Seconds_of_Use`, `Frequency_of_use` | 0,168 |
| `Seconds_of_Use`, `Frequency_of_SMS` | 0,957 |

Kolom ini sangat mungkin hasil hitungan dari fitur lain, tetapi rumusnya tidak dijelaskan dokumentasi UCI. Setelah `Age_Binning` dan `Customer_Value` dikeluarkan, VIF `Frequency_of_SMS` turun dari 39,68 menjadi 1,17. VIF `Seconds_of_Use` (14,03) dan `Frequency_of_use` (18,15) tetap tinggi.

### 5. Risiko leakage pada `Status` dan `Complains`

Waktu pengukuran keduanya tidak dijelaskan dokumentasi UCI. Risiko ini belum terbukti.

| `Complains` | `Status` | Baris | Baris churn | Churn rate |
|---|---|---|---|---|
| 0 | 1 (aktif) | 2.085 | 64 | 3,1% |
| 0 | 2 (non-aktif) | 535 | 192 | 35,9% |
| 1 | 1 (aktif) | 81 | 57 | 70,4% |
| 1 | 2 (non-aktif) | 149 | 133 | 89,3% |

## Klaim yang dihapus dari sel 46–71

"2,3 kali lipat" dan profil pelanggan baru, "hampir pasti berhenti", "loyal", "intervensi paling efektif", "prediktor absolut", "terbukti semu", "suspended", "tagihan bulanan", dan ambang `Customer_Value` 103.

## Yang masih perlu ditinjau

Sel segmentasi dan executive summary masih memuat klaim lama, dan sebagian mungkin mengutip angka MI lama.
