# Ringkasan temuan: Pertanyaan Bisnis

- **Tanggal:** 2026-11-04
- **Data:** 2.850 baris setelah 300 duplikat persis dihapus
- **Sumber analisis:** `program/EDA_Project_Churn_v2.ipynb`, bagian "C. Pertanyaan Bisnis"

## Keputusan

- Bagian "Value at Risk" diganti dengan "Pertanyaan Bisnis".
- Analisis risiko × nilai ditunda ke Fase 3, karena membutuhkan peluang churn dari model.
- Dataset bersih nanti disimpan di folder baru `dataset_clean/`, terpisah dari `dataset/`. Script dan folder belum dibuat.

## Alasan penggantian

- **Nama kurang tepat:** Value at Risk adalah ukuran kerugian pada tingkat peluang tertentu, sedangkan bagian lama hanya menjumlahkan `Customer_Value` per segmen.
- **Satuan tidak jelas:** `Customer_Value` tidak punya rumus dan satuan yang dijelaskan dokumentasi UCI.
- **p-value saja tidak cukup:** p-value hanya menjawab ada beda atau tidak. Pertanyaan bisnis lebih butuh besar selisih dan rentangnya.

## Jawaban

Hasil ini eksploratif, karena pertanyaan dibuat setelah melihat data yang sama. Rentang mengasumsikan tiap baris independen, jadi bisa terlalu sempit.

| Perbandingan | n kelompok | n pembanding | Churn kelompok | Churn pembanding | Selisih (poin persen) | IK 95% |
|---|---|---|---|---|---|---|
| Komplain vs tanpa komplain | 230 | 2.620 | 82,6% | 9,8% | 72,8 | 67,3 sampai 77,3 |
| Non-aktif vs aktif | 684 | 2.166 | 47,5% | 5,6% | 41,9 | 38,1 sampai 45,8 |
| `Seconds_of_Use` kuartil terendah vs lainnya | 713 | 2.137 | 34,6% | 9,3% | 25,3 | 21,7 sampai 29,1 |

Interval memakai metode Newcombe.

### Konsentrasi churn dan nilai

| Ukuran | Hasil |
|---|---|
| Gabungan `Complains=1`, `Status=2`, dan `Seconds_of_Use` kuartil terendah | 992 baris (34,8%) |
| Churn rate gabungan | 40,8% |
| Porsi baris churn pada gabungan | 90,8% |
| Porsi `Customer_Value` pada gabungan | 11,0% |
| Porsi `Customer_Value` pada baris churn | 4,4% (rentang 3,8 sampai 5,0) |
| Median `Customer_Value` | Churn 102,6, tidak churn 271,5 |
| Selisih median | 169,0 (rentang 148,6 sampai 188,3) |

Rentang ini memakai bootstrap persentil dengan 2.000 pengulangan dan seed 180915. Sinyal gabungan dipilih setelah melihat churn pada data yang sama, jadi angkanya bukan kemampuan prediksi. `Customer_Value` dibaca sebagai skor relatif, bukan uang.

## Yang belum bisa dijawab

- Apakah menangani komplain akan menurunkan churn.
- Bagaimana `Status` ditentukan, dan apa definisi churn yang dipakai.
- Apakah penggunaan rendah adalah penyebab atau hanya gejala.
