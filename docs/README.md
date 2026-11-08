# docs/

Dokumentasi pendukung: catatan keputusan analisis dan laporan hasil. Ringkasan keputusan yang sudah dikunci tetap ada di `PROJECT_GUIDE.md`.

- `threshold_skenario.csv`: threshold tiap rasio biaya 1:2, 1:5 (default), dan 1:10 (keputusan 32). Dibuat oleh `program/Threshold_Biaya.ipynb` dan dibaca demo Fase 5.
- `ringkasan_model.csv`: PR-AUC dan ROC-AUC CV acak XGBoost final dan `DummyClassifier` (temuan 13), untuk tab Cara kerja model di demo. Dibuat oleh `python -X utf8 -m src.summary`.
- `ringkasan_non_teknis.md`: ringkasan satu halaman untuk pembaca non-teknis: temuan, cara memakai, dan batasannya.
- `monitoring.md`: cara membuat laporan drift, aturan retraining, dan rollback (Fase 6, keputusan 44).
- `kepentingan_fitur.csv`: permutation importance pada CV acak data latih (temuan 22), untuk tab yang sama. Dibuat oleh perintah yang sama.
