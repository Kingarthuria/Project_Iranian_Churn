# src/

Logika yang dipakai ulang dan dipindah dari notebook di `program/`, misalnya pembersihan data, pembuatan fitur, dan pelatihan model. Mulai terisi sejak Fase 1 dan dirapikan di Fase 3.

## Membuat data bersih

Jalankan dari root project:

```
python -X utf8 src/clean_data.py
```

Hasilnya `dataset_clean/customer_churn_clean.csv` dan `dataset_clean/validation_groups.csv`. Kolom di file kedua hanya untuk cek CV grup, bukan fitur model. Kedua file tidak dilacak Git.
