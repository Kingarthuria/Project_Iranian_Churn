# tests/

Test sederhana (pytest) untuk kode di `src/`. Jalankan dari root project dengan `python -X utf8 -m pytest`.

| File | Yang diperiksa |
|---|---|
| `conftest.py` | Data bersama untuk test. Data bersih dibuat dulu jika belum ada |
| `test_data.py` | Data bersih 2.850 baris tanpa duplikat, kelompok audit sejajar, 12 fitur sama dengan notebook, serta pembagian 2.280 dan 570 baris tanpa tumpang tindih |
| `test_threshold.py` | Fungsi biaya dan threshold pada contoh kecil. Skor out-of-fold, threshold, dan suara mayoritas sama dengan notebook Fase 3 dan `docs/threshold_skenario.csv` |
| `test_model.py` | Pipeline final sama dengan XGBoost biasa, membuang kolom berlebih, tidak terpengaruh urutan kolom, dan menolak data yang kehilangan fitur |
| `test_train.py` | Pelatihan ulang menulis model dan metadata, metadata sesuai keputusan yang dikunci, model yang dimuat ulang sama dengan model baru, dan proses berhenti jika threshold berbeda dari file yang dikunci |

Data uji hanya dipakai untuk memeriksa jumlah baris dan memastikan tidak tumpang tindih dengan data latih. Skornya tidak dihitung.
