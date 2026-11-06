# src/

Logika yang dipakai ulang dan dipindah dari notebook di `program/` (keputusan 36). Notebook tetap sebagai catatan eksperimen, dan test di `tests/` membuktikan `src/` menghasilkan angka yang sama.

| File | Isi |
|---|---|
| `config.py` | Satu tempat untuk `SEED`, path, 12 fitur model, jumlah fold dan ulangan, rasio biaya, dan jumlah baris yang diharapkan |
| `clean_data.py` | Membuat data bersih dari data mentah (Fase 1) |
| `data.py` | Memuat data bersih dan kelompok audit, lalu membagi data latih dan uji sama persis dengan notebook |
| `model.py` | Model terkunci (XGBoost default), Pipeline final, dan skor out-of-fold berulang |
| `threshold.py` | Hitungan biaya, pemilihan threshold per rasio, dan suara mayoritas |
| `train.py` | Pelatihan ulang model final dengan satu perintah |

## Melatih ulang model

Jalankan dari root project:

```
python -X utf8 -m src.train
```

Perintah ini membuat data bersih jika belum ada, memeriksa bahwa threshold hasil hitung ulang sama dengan `docs/threshold_skenario.csv` (file itu tidak ditimpa), lalu melatih Pipeline final pada 2.280 baris latih. Data uji tidak dipakai. Hasilnya `models/churn_pipeline.joblib` dan `models/metadata.json`, yang tidak dilacak Git. Metadata mencatat fitur, hash data, threshold, dan versi library. File model hanya bisa dimuat dengan versi library yang sama.

## Membuat data bersih

Jalankan dari root project:

```
python -X utf8 src/clean_data.py
```

Hasilnya `dataset_clean/customer_churn_clean.csv` dan `dataset_clean/validation_groups.csv`. Kolom di file kedua hanya untuk cek CV grup, bukan fitur model. Kedua file tidak dilacak Git.

## Menjalankan test dan lint

Pasang library pengembangan dulu dengan `pip install -r requirements-dev.txt`, lalu jalankan dari root project:

```
python -X utf8 -m pytest
python -m ruff check src tests
```
