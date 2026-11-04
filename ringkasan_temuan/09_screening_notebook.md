# Ringkasan temuan: screening notebook EDA v2

- **Tanggal:** 2026-11-04
- **File:** `program/EDA_Project_Churn_v2.ipynb`
- **Hasil akhir:** isi dan penyajian layak dipakai untuk tahap cleaning. Sebelum repo dipublikasikan, ukuran output dan riwayat Git masih perlu ditangani.

## Penilaian awal sebelum perbaikan

Nilai ini adalah penilaian, bukan hasil perhitungan.

| Aspek | Nilai | Dasar penilaian |
|---|---|---|
| Ketepatan | 4/5 | Angka utama cocok dengan output, tetapi ada detail narasi yang kurang tepat |
| Kekonsistenan | 3/5 | Label, istilah, format angka, dan bahasa campur |
| Kelayakan metode | 4/5 | Metode sesuai jenis data, dan klaim sudah asosiatif |
| Kelengkapan | 3/5 | Cek logika antarkolom tidak ada di notebook |
| Reproduksibilitas | 4/5 | Berjalan dari awal, tetapi seed tertulis di tiga tempat |
| Kualitas kode | 2,5/5 | Banyak pengulangan dan sel sangat panjang |
| Keterbacaan | 3/5 | Beberapa grafik terlalu padat |
| Transparansi | 3/5 | Pola berulang sengaja tidak dibahas di notebook ini |

## Perbaikan

### Isi dan ketepatan
- **Cek kualitas data:** bagian baru berisi rentang nilai, logika antarkolom, dan keputusannya.
- **Heatmap:** sel dengan kurang dari 20 baris dikosongkan, panel dibagi menjadi 6 per gambar, dan kategori mengikuti urutan tingkat.
- **Grafik:** KDE tidak melebar ke nilai negatif, dan label outlier memakai warna netral.
- **Segmentasi:** `Charge_Amount` dan `Age_Group` mengikuti urutan tingkat.
- **Grafik kontribusi bivariat:** memakai label, bukan kode mentah, dan urutan tingkat.
- **Grafik churn per nilai:** garis tidak terpotong, dan label sumbu tidak bertumpuk.

### Konsistensi
- Satu set label: `Aktif` dan `Non-aktif`, `Pay as you go` dan `Kontrak`, `Komplain` dan `Tanpa Komplain`.
- Judul dan narasi berbahasa Indonesia, dengan koma desimal di narasi.
- "FASE 1–4" menjadi "Bagian 1–4", dan daftar isi ditambahkan.

### Kerapian kode

| Ukuran | Sebelum | Sesudah |
|---|---|---|
| Sel kode terpanjang | 234 baris | 160 baris |
| Sel yang memuat import | 12 | 1 |
| Tempat seed ditulis | 3 | 1 |
| Tempat `TARGET` didefinisikan | 4 | 1 |
| Tempat binning ditulis | 4 | 1 fungsi bersama, plus 1 baris di Pertanyaan Bisnis |
| Sel dengan `filterwarnings` | 3 | 0, dan peringatan diperbaiki dari sumbernya |

## Verifikasi

- Notebook berjalan dari awal tanpa error dan tanpa peringatan.
- Tahap kerapian kode dan perbaikan grafik terakhir menghasilkan output teks yang sama persis (953 baris).
- Tahap konsistensi hanya mengubah label dan nama kolom di output. Nilai segmentasi dicek sama.
- Semua 41 gambar dilihat setelah perapian kode, dan gambar yang berubah sesudahnya dicek contohnya.
- Tidak ada rujukan ke file lain, nama, `userId`, atau path lokal.

## Koreksi

Screening awal menyebut kode Pearson tidak ada di notebook. Itu **keliru**, karena pencariannya memakai kata "pearson", padahal heatmap Pearson memakai bawaan `df.corr()`. Saat memeriksa gambar, kesalahan ini ditemukan. Judul metode, judul heatmap, dan kesimpulan sudah dibetulkan.

## Sisa keterbatasan

- Tiga sel masih panjang (151–160 baris), karena satu perulangan grafik atau beberapa fungsi berada dalam satu sel. Sel-sel ini tidak dipecah supaya alurnya tetap utuh.
- Teks tertentu di output kode masih berbahasa Inggris, misalnya "Boxplot" dan "Point-Biserial".
- Beberapa p-value di tabel output masih tertulis `0.0000`, karena nilainya tetap dipakai sebagai angka.
- Ukuran notebook sekitar 6 MB. Keputusan strip output ditunda sampai sebelum repo dipublikasikan.
- Label KW pada panel `Subscription_Length` sedikit menimpa garis.
- Notebook ini sengaja tidak membahas pola berulang, jadi README dan laporan model wajib memuat kalimat keterbatasan.
