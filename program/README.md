# program/

Notebook eksplorasi dan analisis. Alasan setiap keputusan ada di `PROJECT_GUIDE.md` bagian 4, dan angka temuannya di bagian 3.

## Alur utama

Baca dan jalankan sesuai urutan nomor. Sebelum nomor 2, buat dulu data bersih dari root project:

```
python -X utf8 src/clean_data.py
```

| No | Notebook | Fase | Tujuan | Membaca | Menghasilkan |
|---|---|---|---|---|---|
| 1 | `EDA_Project_Churn_v2.ipynb` | 1 | Mengenal data: kualitas kolom, hubungan fitur dengan churn, dan pertanyaan bisnis | `dataset/` | - |
| 2 | `Modeling_Project_Churn.ipynb` | 2 | Membandingkan enam model dan `DummyClassifier`, dengan dan tanpa `Status` serta `Complains` | `dataset_clean/` | - |
| 3 | `Tuning_XGBoost.ipynb` | 2 | Menyetel XGBoost dengan random search, lalu membandingkannya dengan parameter default | `dataset_clean/` | - |
| 4 | `Evaluasi_Data_Uji.ipynb` | 2 | Menilai model yang sudah dikunci pada data uji, sekali | `dataset_clean/` | - |
| 5 | `Threshold_Biaya.ipynb` | 3 | Memilih threshold untuk rasio biaya 1:2, 1:5, dan 1:10 | `dataset_clean/` | `docs/threshold_skenario.csv` |
| 6 | `Risiko_Nilai.ipynb` | 3 | Membagi pelanggan ke empat segmen berdasarkan skor risiko dan nilai terhitung | `dataset_clean/`, `docs/threshold_skenario.csv` | - |
| 7 | `Interpretasi_Model.ipynb` | 3 | Melihat fitur yang paling dipakai model dengan permutation importance dan SHAP, beserta cek CV grup | `dataset_clean/` | - |
| 8 | `Analisis_Error.ipynb` | 3 | Melihat di mana dan kenapa model salah: churn terlewat, salah hubungi, dan kaitannya dengan baris janggal Fase 1 | `dataset_clean/`, `docs/threshold_skenario.csv` | - |

Notebook 6 dan 8 membutuhkan CSV dari notebook 5. Notebook 2–8 memakai pembagian data latih dan uji yang sama.

## Simpanan, bukan alur utama

| Notebook | Isi | Kenapa disimpan |
|---|---|---|
| `EDA_Project_Churn.ipynb` | Notebook EDA asli sebelum project dimulai ulang | Dipertahankan apa adanya sebagai titik awal. Versi yang dipakai adalah `_v2` |
| `analisis_duplikat_v2.ipynb` | Audit duplikat dan pola berulang per 50 baris (Fase 1) | Bukti untuk kalimat keterbatasan di README. Ringkasannya ada di `ringkasan_temuan/` (keputusan 3) |

## Keterbatasan

Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis.
