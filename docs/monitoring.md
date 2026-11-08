# Monitoring, retraining, dan rollback (Fase 6)

Dokumen ini menjelaskan cara memantau model churn, kapan model perlu dilatih ulang, dan cara kembali ke model sebelumnya. Dasarnya keputusan 44 di `PROJECT_GUIDE.md`.

## 1. Laporan drift dengan satu perintah

Jalankan dari root project, di env `ds_env312`:

```
python -X utf8 -m src.monitor
```

Perintah ini menjalankan empat langkah:

1. Membuat 4 batch simulasi berisi 500 pelanggan dari data latih (`src/simulate.py`).
2. Menilai tiap batch dengan model yang sama seperti demo, lalu mencatat log prediksi (`src/score_batch.py`).
3. Membandingkan tiap batch dengan 2.280 baris data latih sebagai acuan (`src/monitor.py`).
4. Menulis hasilnya ke folder `monitoring/`, yang tidak dilacak Git:

| File | Isi |
|---|---|
| `laporan_drift.md` | Ringkasan status per batch, PSI per fitur, tindak lanjut, dan keterbatasan |
| `drift_per_fitur.csv` | PSI, jenis uji, p-value, dan status untuk tiap batch dan fitur |
| `prediction_log.csv` | Log prediksi: waktu, batch, hash data latih, rasio, skor minimal, skor, keputusan, segmen, dan 12 fitur |
| `batches/*.csv` | Batch simulasi yang dinilai |

Batch baru, misalnya data pelanggan bulan berikutnya jika nanti tersedia, bisa dinilai dan dicatat dengan:

```
python -X utf8 -m src.score_batch path/ke/batch.csv
```

### Batch simulasi

Dataset UCI hanya punya satu periode, jadi tidak ada data bulan berikutnya yang asli. Data uji juga tidak dipakai (keputusan 24).

| Batch | Perubahan dari sampel acak data latih |
|---|---|
| `normal` | Tidak ada. Seharusnya stabil |
| `komplain_naik` | 30% pelanggan yang belum pernah komplain diubah menjadi pernah komplain |
| `pemakaian_turun` | Detik panggilan, jumlah panggilan, jumlah SMS, panggilan berbeda, dan nilai terhitung dikali 0,6 |
| `nonaktif_naik` | 40% pelanggan aktif diubah menjadi non-aktif |

### Cara mengukur drift

- **PSI (Population Stability Index)** per fitur. Untuk kolom angka, kelompoknya dibuat dari 10 kuantil data acuan. Untuk kolom berkode (`Complains`, `Status`, `Tariff_Plan`, `Charge_Amount`, `Age_Group`), kelompoknya adalah tiap kode.
- **Status fitur:** PSI di bawah 0,10 stabil, 0,10 sampai 0,25 perlu dicek, dan 0,25 ke atas bergeser. Batas ini aturan praktis yang umum dipakai, bukan hasil hitungan dari data ini.
- **Uji statistik:** uji KS untuk kolom angka dan chi-kuadrat untuk kolom berkode. Hasilnya dicatat di CSV sebagai pelengkap. Dengan sampel besar, p-value bisa kecil untuk perbedaan yang tidak berarti, jadi status memakai PSI.
- **Status batch:** bergeser jika ada fitur penting dengan PSI 0,25 ke atas, atau porsi pelanggan yang disarankan dihubungi (rasio 1:5) bergeser 10 poin persen atau lebih dari acuan. Batas 10 poin persen adalah asumsi. Fitur penting diambil dari temuan 22: kelompok pemakaian (`Seconds_of_Use`, `Frequency_of_use`, `Frequency_of_SMS`, `Distinct_Called_Numbers`, `Customer_Value`), `Complains`, `Subscription_Length`, `Status`, dan `Call_Failure`.

## 2. Kapan model dilatih ulang

Drift data adalah **pemicu untuk memeriksa**, bukan bukti bahwa performa model turun. Urutannya:

1. **Status bergeser:** periksa dulu apakah perubahannya nyata, misalnya karena kampanye, perubahan tarif, atau gangguan jaringan, atau hanya karena kesalahan pencatatan data.
2. **Tunggu label.** Menurut UCI, status churn dicatat di akhir bulan ke-12, sekitar 3 bulan setelah data 9 bulan terkumpul. Performa hanya bisa dinilai setelah label tiba.
3. **Nilai performa dengan label baru.** Hitung PR-AUC pada pelanggan yang labelnya sudah diketahui, lalu bandingkan dengan acuan PR-AUC CV acak 0,931 (0,920–0,939, temuan 13). Acuan ini kemungkinan terlalu optimistis (bagian 7 di guide), jadi penurunan kecil belum tentu masalah.
4. **Latih ulang** jika performa jelas turun, atau drift di fitur penting bertahan lebih dari satu periode:
   ```
   python -X utf8 -m src.train
   python -X utf8 -m src.track
   ```
   `src.track` mencatat run baru di MLflow dan mendaftarkan versi model baru.
5. **Tetapkan `champion` hanya jika model baru tidak lebih buruk**, yaitu rentang PR-AUC-nya tidak berada di bawah rentang model lama pada data yang sama. Ini sama dengan aturan penyetelan di keputusan 30.

## 3. Rollback

Model untuk analisis disimpan di registry MLflow lokal sebagai `iranian-churn-xgboost`, dengan alias `champion` (keputusan 37). Untuk kembali ke versi sebelumnya:

```python
import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()
name = "iranian-churn-xgboost"
current = client.get_model_version_by_alias(name, "champion")
print("champion sekarang: versi", current.version)
client.set_registered_model_alias(name, "champion", "<versi sebelumnya>")
```

Demo publik tidak membaca registry. Demo melatih model dari dataset di branch `main` setiap kali menyala (keputusan 38), jadi rollback demo berarti me-revert commit yang mengubah data atau model di `main`, lalu menekan **Reboot app** di Streamlit Cloud.

## 4. Keterbatasan

- Semua batch adalah **simulasi**. Hasilnya menunjukkan bahwa laporan bisa menangkap pergeseran yang sengaja dibuat, bukan bahwa data nyata akan bergeser seperti itu.
- Batch diambil dari data latih model itu sendiri, jadi skornya lebih yakin daripada skor untuk pelanggan baru.
- Drift data tidak sama dengan turunnya performa, dan label churn datang terlambat sekitar 3 bulan.
- Batas PSI dan batas porsi dihubungi adalah aturan praktis atau asumsi, bukan hasil hitungan dari data ini.
- Demo publik tidak menyimpan input, jadi log prediksi hanya berasal dari `src.score_batch` dan `src.monitor`.
- Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis.
