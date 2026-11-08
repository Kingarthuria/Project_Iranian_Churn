# Ringkasan untuk pembaca non-teknis

## Ceritanya

Setiap perusahaan telekomunikasi kehilangan pelanggan dari waktu ke waktu. Kejadian ini disebut *churn*, yaitu saat pelanggan berhenti menjadi pelanggan. Menghubungi semua pelanggan untuk mencegahnya terlalu mahal, jadi pertanyaan yang lebih berguna adalah: **siapa yang perlu dihubungi lebih dulu?**

Proyek ini mencoba menjawabnya dengan data 2.850 pelanggan sebuah perusahaan telekomunikasi Iran, dari dataset publik UCI. Untuk setiap pelanggan tercatat hal-hal seperti berapa lama ia sudah berlangganan, seberapa sering ia menelepon dan mengirim SMS, berapa kali panggilannya gagal, apakah ia pernah komplain, apakah statusnya masih aktif, paket tarif yang dipakainya, serta sebuah **nilai pelanggan** yang dihitung oleh pemilik data. Semua catatan itu berasal dari 9 bulan pertama. Tiga bulan kemudian, di akhir bulan ke-12, barulah terlihat siapa yang churn: sekitar 16 dari setiap 100 pelanggan.

Tentang nilai pelanggan: sumber data tidak menjelaskan cara menghitungnya, dan angkanya bukan rupiah atau mata uang lain. Yang kami tahu, angka ini sangat sejalan dengan seberapa banyak pelanggan memakai telepon dan SMS. Jadi anggap saja sebagai gambaran seberapa aktif dan "berharga" seorang pelanggan.

## Apa yang dibuat

Dari data itu, kami melatih sebuah model yang memberi setiap pelanggan **skor risiko churn**. Makin tinggi skornya, makin mirip pola pelanggan itu dengan pelanggan yang dulu akhirnya churn. Skor ini lalu dibandingkan dengan sebuah batas, dan pelanggan yang skornya mencapai batas disarankan untuk dihubungi.

Anda bisa mencobanya sendiri di **[demo](https://churn-risk-priority.streamlit.app/)**. Pilih salah satu contoh pelanggan, atau isi datanya sendiri. Demo akan menjelaskan apakah pelanggan itu perlu dihubungi, apa alasannya, dan langkah apa yang disarankan.

## Apa yang kami temukan

**Komplain adalah tanda paling kuat.** Dari setiap 100 pelanggan yang pernah komplain, sekitar 83 akhirnya churn. Pada pelanggan yang tidak pernah komplain, angkanya hanya sekitar 10 dari 100.

**Status yang tidak aktif juga patut diwaspadai.** Hampir separuh pelanggan non-aktif churn (sekitar 48 dari 100), sedangkan pelanggan yang aktif hanya sekitar 6 dari 100. Bila keduanya muncul bersamaan, risikonya makin besar: dari 149 pelanggan yang pernah komplain sekaligus berstatus non-aktif, 133 di antaranya churn.

**Sebagian besar yang churn adalah pelanggan bernilai rendah.** Jika semua nilai pelanggan dijumlahkan, pelanggan yang churn hanya menyumbang sekitar 4 dari setiap 100 bagian. Kehilangan mereka tetap merugikan, tetapi tidak sebesar yang dibayangkan dari jumlah orangnya.

**Kelompok yang paling penting justru kecil.** Pelanggan yang berisiko tinggi *dan* bernilai tinggi hanya 63 dari 2.280 pelanggan yang dianalisis. Namun 54 di antaranya akhirnya churn, dan mereka menyumbang hampir 40% dari seluruh nilai pelanggan yang hilang. Kelompok inilah yang paling layak didahulukan.

### Kenapa temuan ini belum membuktikan sebab-akibat

Data ini hanya *mengamati* apa yang terjadi, tanpa pernah mencoba memperlakukan pelanggan secara berbeda. Karena itu, kita tahu bahwa komplain dan churn sering muncul bersamaan, tetapi belum tahu mana yang menjadi penyebab. Bisa jadi komplain memang memicu pelanggan pergi. Bisa juga keduanya disebabkan hal lain, misalnya jaringan yang sering bermasalah, atau pelanggan yang sudah berniat pindah lalu sempat komplain sebelum pergi. Kalau penyebabnya jaringan, menangani komplain saja tidak akan banyak membantu. Satu-satunya cara memastikan adalah mengujinya langsung, seperti dijelaskan di bagian terakhir.

## Bagaimana memakainya

Pertama, tentukan seberapa mahal menghubungi pelanggan dibanding kerugian kehilangan pelanggan. Demo menyebutnya **rasio biaya**. Jika menghubungi pelanggan murah, misalnya cukup dengan SMS, wajar untuk menghubungi lebih banyak orang, termasuk yang risikonya sedang. Jika mahal, misalnya harus ditelepon petugas, sebaiknya hanya yang risikonya paling tinggi.

Kedua, gabungkan risiko dengan nilai pelanggan. Hasilnya empat kelompok prioritas. Pelanggan berisiko dan bernilai tinggi didahulukan dan dihubungi secara pribadi. Pelanggan berisiko tetapi bernilai rendah cukup dihubungi dengan cara murah, misalnya pesan otomatis. Pelanggan yang risikonya rendah cukup dijaga lewat program loyalitas atau dipantau saja.

Ketiga, ikuti siklus yang sama dengan data. Setelah catatan 9 bulan terkumpul, hitung skornya, hubungi pelanggan di bulan ke-10 dan ke-11, lalu lihat siapa yang bertahan di akhir bulan ke-12.

Sebagai gambaran, kami menyisihkan 570 pelanggan yang tidak dipakai untuk melatih model. Dengan pengaturan biaya yang sedang, model menyarankan menghubungi 117 orang di antaranya, dan dari 89 pelanggan yang akhirnya churn, 87 termasuk yang disarankan. Hasil ini menjanjikan, tetapi jangan dianggap pasti terulang, karena alasannya dijelaskan di bagian berikut.

## Seberapa bisa dipercaya

Model ini sangat baik mengenali pelanggan yang churn **di data ini**. Masalahnya, saat diperiksa, data ini ternyata punya pola aneh: baris-barisnya seperti berulang setiap 50 baris, sehingga banyak pelanggan punya "kembaran" yang sangat mirip. Akibatnya, model bisa terlihat lebih pintar daripada kenyataannya, karena ia diuji pada pelanggan yang mirip dengan yang sudah pernah ia lihat. Pada pelanggan yang benar-benar baru, hasilnya kemungkinan lebih rendah.

Selain itu, ada beberapa hal yang tidak dijelaskan oleh sumber data, misalnya arti pasti "churn" (berhenti berlangganan, pindah operator, atau sekadar tidak aktif) dan cara status aktif ditentukan. Rasio biaya dan usulan tindakan di demo juga masih berupa asumsi, bukan angka dari perusahaan.

## Langkah yang disarankan

Sebelum alat ini dipakai secara luas, kami menyarankan uji coba kecil. Ambil pelanggan yang disarankan untuk dihubungi, lalu bagi menjadi dua kelompok secara acak: satu kelompok dihubungi, kelompok lain sengaja tidak. Di akhir siklus, bandingkan berapa banyak yang churn di masing-masing kelompok. Jika kelompok yang dihubungi lebih sedikit churn, barulah ada bukti bahwa menghubungi pelanggan memang membantu. Setelah itu, model sebaiknya dilatih ulang dengan data perusahaan sendiri dan dipantau setiap periode (lihat [panduan monitoring](monitoring.md)).

## Di mana letak filenya

Saat membuka repo di GitHub, daftar file di halaman depan mungkin terlihat membingungkan. Tidak perlu membuka semuanya. Berikut yang paling berguna:

| Yang ingin Anda lihat | Letaknya |
|---|---|
| Penjelasan lengkap proyek | [README.md](../README.md), yang tampil di halaman depan repo |
| Data asli dari UCI | folder [dataset/](../dataset) |
| Catatan analisis langkah demi langkah, lengkap dengan grafik | folder [program/](../program). Urutan bacanya ada di [program/README.md](../program/README.md) |
| Ringkasan hasil pemeriksaan data | folder [ringkasan_temuan/](../ringkasan_temuan) |
| Semua keputusan beserta alasannya | [PROJECT_GUIDE.md](../PROJECT_GUIDE.md) |
| Kode demo dan model | `streamlit_app.py` dan folder [src/](../src) |
| Pemeriksaan otomatis untuk kode | folder [tests/](../tests) |

File lain, seperti `pyproject.toml`, `requirements.txt`, dan folder `.github/`, adalah pengaturan untuk programmer dan bisa dilewati.
