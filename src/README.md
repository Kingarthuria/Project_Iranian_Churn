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
| `evaluate.py` | Penilaian dengan CV acak dan cek CV grup, sama dengan notebook Fase 2 |
| `track.py` | Experiment tracking dan registry dengan MLflow lokal |
| `schema.py` | Skema input dan output demo, divalidasi dengan pydantic |
| `predict.py` | Skor, keputusan hubungi, segmen, dan penjelasan satu pelanggan untuk demo |

## Lingkungan

Project memakai env conda **`ds_env312`** (Python 3.12, keputusan 38 dan 39), karena Python 3.10 sudah tidak menerima pembaruan keamanan dan tidak didukung Streamlit Community Cloud. Buat env ini dari root project:

```
conda create -n ds_env312 python=3.12
conda activate ds_env312
pip install -r requirements-dev.txt
```

`requirements.txt` hanya berisi library demo, dan `requirements-dev.txt` menambah library notebook, test, lint, dan MLflow. Notebook lama di `program/` dibuat dengan Python 3.10 (`ds_env`), dan test menunjukkan hasil model sama di kedua versi.

## Menjalankan demo

Jalankan dari root project:

```
streamlit run streamlit_app.py --server.address 127.0.0.1
```

Opsi `--server.address 127.0.0.1` membuat demo hanya bisa dibuka dari komputer sendiri di `http://127.0.0.1:8501`. Tanpa opsi ini, Streamlit menerima koneksi dari semua jaringan, dan Windows Firewall akan meminta izin. Pilih **Cancel** jika peringatan itu muncul, karena demo lokal tidak membutuhkan akses jaringan. Opsi ini tidak dipakai di Streamlit Community Cloud, yang mengatur alamatnya sendiri. Matikan demo dengan `Ctrl + C`.

Saat pertama dinyalakan, aplikasi melatih model dari dataset dalam beberapa detik. Pengguna bisa memilih rasio biaya, mengisi 12 fitur pelanggan, lalu melihat skor risiko, keputusan hubungi, segmen risiko × nilai, dan 5 fitur yang paling mendorong skor. Input divalidasi dengan `src/schema.py` dan tidak disimpan.

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

## Experiment tracking

Butuh library pengembangan (`pip install -r requirements-dev.txt`). Jalankan dari root project:

```
python -X utf8 -m src.track
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Perintah pertama mencatat 4 run ke `mlflow.db` dan `mlartifacts/`: XGBoost 12 fitur (final), XGBoost 10 fitur, Logistic Regression 12 fitur, dan `DummyClassifier`. Tiap run memuat PR-AUC dan ROC-AUC CV acak dengan rata-rata, minimum, dan maksimum per ulangan, serta metrik cek CV grup berawalan `cek_grup_`. Data uji tidak dipakai. Pipeline final dari `src.train` didaftarkan sebagai `iranian-churn-xgboost` dengan alias `champion`.

Perintah kedua membuka tampilan web di `http://127.0.0.1:5000`, hanya di komputer sendiri. Setiap kali `src.track` dijalankan, run baru dan versi model baru bertambah. Kedua lokasi penyimpanan tidak dilacak Git.

Model dari registry bisa dimuat dengan:

```python
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
model = mlflow.sklearn.load_model("models:/iranian-churn-xgboost@champion")
```

## Menjalankan test dan lint

Pasang library pengembangan dulu dengan `pip install -r requirements-dev.txt`, lalu jalankan dari root project:

```
python -X utf8 -m pytest
python -m ruff check src tests streamlit_app.py
```
