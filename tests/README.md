# tests/

Test sederhana (pytest) untuk kode di `src/`. Jalankan dari root project dengan `python -X utf8 -m pytest`.

| File | Yang diperiksa |
|---|---|
| `conftest.py` | Data bersama untuk test. Data bersih dibuat dulu jika belum ada |
| `test_data.py` | Data bersih 2.850 baris tanpa duplikat, kelompok audit sejajar, 12 fitur sama dengan notebook, serta pembagian 2.280 dan 570 baris tanpa tumpang tindih |
| `test_threshold.py` | Fungsi biaya dan threshold pada contoh kecil. Skor out-of-fold, threshold, dan suara mayoritas sama dengan notebook Fase 3 dan `docs/threshold_skenario.csv` |
| `test_model.py` | Pipeline final sama dengan XGBoost biasa, membuang kolom berlebih, tidak terpengaruh urutan kolom, dan menolak data yang kehilangan fitur |
| `test_train.py` | Pelatihan ulang menulis model dan metadata, metadata sesuai keputusan yang dikunci, model yang dimuat ulang sama dengan model baru, dan proses berhenti jika threshold berbeda dari file yang dikunci |
| `test_track.py` | Experiment tracking ke folder sementara: 4 run selesai, metrik sama dengan Fase 2 (temuan 13–15), data uji tidak dipakai, dan model `@champion` bisa dimuat dengan skor sama |
| `test_schema.py` | Skema input menerima data valid, menolak nilai di luar rentang, kode tidak valid, kolom hilang, dan kolom berlebih, serta batasnya sama dengan data latih |
| `test_predict.py` | Skor demo sama dengan Pipeline, threshold dan keputusan sesuai CSV, segmen sesuai median nilai, penjelasan SHAP konsisten dengan skor, dan kelompok usia berpasangan satu-satu dengan kolom `Age` |
| `test_summary.py` | Angka di `docs/ringkasan_model.csv` dan `docs/kepentingan_fitur.csv` sama dengan temuan 13 dan 22, serta sama dengan hasil hitung ulang |
| `test_texts.py` | Kedua bahasa punya kunci teks yang sama, kalimat keterbatasan sama persis dengan `PROJECT_GUIDE.md`, tiap fitur punya label, format angka per bahasa, dan tidak ada kata yang dilarang |
| `test_monitor.py` | PSI nol untuk data identik dan tinggi untuk data yang digeser, batch simulasi bisa diulang, batch normal stabil, ketiga skenario tertangkap, log prediksi sesuai model demo, dan laporan dibuat dengan satu perintah |
| `test_app.py` | Uji aplikasi Streamlit: empat tab, kalimat keterbatasan terlihat, pilihan contoh dan rasio di sidebar, isian sendiri, alur tab bisnis (angka, arti, rekomendasi), saran yang disesuaikan, tab teknis, dan matriks segmen |

Data uji hanya dipakai untuk memeriksa jumlah baris dan memastikan tidak tumpang tindih dengan data latih. Skornya tidak dihitung.
