# Verifikasi struktur 50 kelompok

- **Tanggal:** 2026-11-04
- **Sumber analisis:** `program/analisis_duplikat_v2.ipynb`, bagian "Verifikasi struktur 50 kelompok"
- **Kelompok:** sisa bagi 50 dari posisi baris. **Blok:** hasil bagi 50 (63 blok)

## Pola selisih pada semua kelompok

Porsi nilai yang mengikuti selisih terbanyak di bloknya, dibandingkan dengan kelompok yang diacak di dalam tiap blok.

| Kolom | Ikut pola | Urutan acak | Kelompok yang 100% ikut pola |
|---|---|---|---|
| `Subscription Length` | 99,9% | 15,5% | 48 dari 50 |
| `Frequency of use` | 94,4% | 4,7% | 36 |
| `Distinct Called Numbers` | 93,4% | 6,7% | 28 |
| `Seconds of Use` | 91,1% | 2,8% | 32 |
| `Call Failure` | 79,0% | 11,3% | 8 |
| `Frequency of SMS` | 77,5% | 7,2% | 15 |
| `Customer Value` | 14,7% | 2,1% | 0 |

Pada `Frequency of use`, `Frequency of SMS`, dan `Call Failure`, sebagian besar nilai yang menyimpang berada di batas minimum atau maksimum kolom. Ini cocok dengan nilai yang terpotong di batas, tetapi belum membuktikannya.

## `Churn` per kelompok

- 35 kelompok tidak punya churn sama sekali.
- 7 kelompok seluruh barisnya churn, dan menyumbang 441 dari 495 baris churn.
- Satu kelompok campuran punya 38 baris churn dari 63 baris.

## Hubungan dengan duplikat

| Pemeriksaan | Beraktivitas | Beraktivitas nol |
|---|---|---|
| Pasangan kembar di kelompok yang sama | 365 dari 365 | 61 dari 92 |

Sebanyak 362 dari 365 pasangan beraktivitas berasal dari blok dengan pola selisih utama yang sama. Sebagian pasangan beraktivitas nol berada di kelompok berbeda, jadi sebagian mungkin memang sama secara kebetulan.

## Skor prediksi `Churn` (CV 5x5)

| Model | Metrik | CV acak | Grup per kelompok |
|---|---|---|---|
| Logistic Regression | ROC-AUC | 0,932 (0,913–0,959) | 0,841 (0,607–1,000) |
| | PR-AUC | 0,755 (0,690–0,847) | 0,571 (0,162–1,000) |
| RandomForest | ROC-AUC | 0,984 (0,976–0,991) | 0,790 (0,369–0,998) |
| | PR-AUC | 0,930 (0,897–0,956) | 0,454 (0,035–0,822) |

Baseline PR-AUC (churn rate) adalah 0,157. Skor ini untuk audit, bukan hasil model final.

## Pemeriksaan sumber

| Sumber | Pernyataan | Cara membagi data |
|---|---|---|
| UCI | "3150 rows of data, each representing a customer"; duplikat atau augmentasi tidak disebut | Tidak berlaku |
| `information-17-00680-v2.pdf` | "each row representing a distinct customer" | Hold-out 80:20 |
| `102601.pdf` | "3.150 pelanggan" | 80:20 berstrata, ditambah CV 5-fold |
| `3757110.3757152.pdf` | "3,150 customer records", lalu menghapus 300 duplikat | 80:20 berstrata, ditambah CV 10-fold |
| `journal.pone.0303881.pdf` | "3150 subscribers" | Acak 70:10:20 |

Paper diperiksa lewat bagian data dan pencarian kata kunci, bukan dibaca penuh. Dari pemeriksaan itu, tidak ada yang memakai pemisahan per kelompok atau membahas struktur ini. Paper pengantar yang dikutip, seperti Keramati dkk. dan Jafari-Marandi dkk. (2020), tidak ada di `jurnal/`.

## Keputusan pengguna

- Project dilanjutkan dengan asumsi tiap baris adalah satu pelanggan, mengikuti UCI dan keempat paper tersebut.
- Hasil akhir memuat kalimat keterbatasan yang ada di `01_struktur_data.md`, tanpa skor pembanding.
- Audit disimpan di repo sebagai simpanan.
