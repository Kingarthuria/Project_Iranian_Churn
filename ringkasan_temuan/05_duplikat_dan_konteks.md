# Ringkasan temuan: keputusan duplikat, classifier test, dan konteks dataset

- **Tanggal:** 2026-11-04
- **Sumber analisis:** `program/EDA_Project_Churn_v2.ipynb` dan `program/analisis_duplikat_v2.ipynb`
- **Pembanding:** `program/EDA_Project_Churn.ipynb` (notebook asli)

File ini hanya memuat hal yang belum tertulis di `01` sampai `04`.

## 1. Keputusan duplikat

**Keputusan: hapus 300 duplikat persis dengan `keep='first'`, sisa 2.850 baris.**

Alasannya:
- baris identik bisa terpisah ke train dan test;
- baris yang sama tidak dipelajari berulang oleh model.

Keterbatasannya:
- penghapusan hanya menangani duplikat persis;
- 47 dari 300 baris yang dihapus beraktivitas nol, jadi sebagian mungkin pelanggan sah.

Versi yang hanya menghapus 253 baris beraktivitas sudah dibandingkan. Versi 300 baris dipilih karena aturannya sederhana dan tidak menyisakan baris identik.

### Yang diperbaiki dari notebook asli

| Bagian notebook asli | Masalah | Perbaikan di v2 |
|---|---|---|
| Label "segmen pasif" | 207 dari 465 baris yang terlibat duplikasi punya `Seconds of Use` di atas atau sama dengan median seluruh data | Label dihapus, perbedaan ditulis apa adanya |
| Perbandingan profil | Pembanding memuat baris duplikat, dan kode `Status` dirata-ratakan | Dibandingkan dengan baris yang tidak pernah duplikat, dan kolom biner ditulis sebagai proporsi |
| Uji AUC (0,9317 dan 0,9324) | Test set berbeda, scaler dipasang sebelum CV, dan AUC yang sama tidak membuktikan penghapusan aman | Uji dan klaim "100% aman" dihapus |

Profil baris yang terlibat duplikasi dibanding baris yang tidak pernah duplikat:

| Ukuran | Terlibat duplikasi (465 baris) | Tidak pernah duplikat (2.685 baris) |
|---|---|---|
| Status non-aktif | 33,1% | 23,4% |
| Ada komplain | 4,3% | 8,2% |
| Churn rate | 17,4% | 15,4% |

Setelah penghapusan, churn rate berubah dari 15,71% menjadi 15,65%.

## 2. AUC classifier test di bawah 0,5

Classifier test menguji apakah model bisa membedakan grup duplikat dari grup lainnya, dengan ROC-AUC. Hasil CV acak dengan RandomForest jauh di bawah 0,5, dan itu tidak diperkirakan.

| Pengujian (ROC-AUC) | `drop_300` | `drop_253` |
|---|---|---|
| RandomForest, CV acak | 0,291 (0,221–0,397) | 0,239 (0,197–0,292) |
| RandomForest, label diacak | 0,514 (0,413–0,592) | 0,521 (0,463–0,594) |
| Logistic Regression, CV acak | 0,536 (0,439–0,622) | 0,446 (0,366–0,529) |
| RandomForest, daun minimal 20 baris | 0,423 (0,350–0,498) | 0,382 (0,324–0,419) |
| RandomForest, grup hampir kembar (beda ≤ 1 fitur) | 0,259 (0,191–0,396) | 0,245 (0,194–0,290) |
| RandomForest, grup per kelompok posisi | **0,658 (0,599–0,741)** | **0,646 (0,550–0,713)** |

Cara membacanya:
- **Metode berjalan normal:** label yang diacak menghasilkan sekitar 0,5.
- **Dugaan pertama gugur:** mengelompokkan baris hampir kembar tidak memperbaiki hasil.
- **Efeknya lokal:** AUC mendekati 0,5 saat daun pohon diperbesar. Pada `drop_253`, tetangga terdekat baris positif hanya 1,1% positif, sedangkan tetangga baris negatif 8,3%.
- **Hasil yang dipakai:** anomali hilang saat kelompok posisi yang sama tidak muncul di train dan test sekaligus. Dengan begitu, profil grup duplikat terbukti berbeda pada kedua versi.

Mekanisme pastinya belum dibuktikan. Yang teramati hanya bahwa anomali itu hilang dengan pemisahan per kelompok.

## 3. Koreksi konteks dataset di sel 4

| Notebook asli | Notebook v2 | Alasan |
|---|---|---|
| Planning gap "secara desain berfungsi mencegah" leakage, dan fitur "aman digunakan" tanpa risiko leakage berbasis waktu | Menurut dokumentasi UCI, fitur mendahului label, tetapi cara dan waktu pengukuran `Status` tidak dijelaskan, jadi risikonya belum bisa disingkirkan | Dokumentasi tidak cukup untuk membuktikan fitur bebas leakage |
| Menyebut 13 kolom, tetapi hanya 12 nama | `Age` ditambahkan | Daftar kolomnya belum lengkap |
