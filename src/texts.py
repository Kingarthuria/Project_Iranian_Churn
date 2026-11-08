"""Teks tampilan demo dalam Bahasa Indonesia (default) dan Inggris.

Kunci kedua bahasa harus sama persis (diperiksa di tests/test_texts.py). Kalimat keterbatasan Bahasa
Indonesia wajib sama dengan PROJECT_GUIDE.md bagian 7 (keputusan 2).
"""
LANGUAGES = {"id": "Indonesia", "en": "English"}
DEFAULT_LANGUAGE = "id"

LIMITATION_ID = (
    "Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. "
    "Namun audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin "
    "dan skor model bisa terlalu optimistis."
)
LIMITATION_EN = (
    "The analysis follows the UCI documentation, which states that each row represents one customer. "
    "However, an audit found a pattern repeating every 50 rows, so independence between rows is not guaranteed "
    "and model scores may be overly optimistic."
)

# Pengelompokan isian formulir (struktur sama untuk kedua bahasa)
FORM_GROUPS = {
    "status": ["Complains", "Status", "Call_Failure"],
    "usage": ["Seconds_of_Use", "Frequency_of_use", "Frequency_of_SMS", "Distinct_Called_Numbers", "Customer_Value"],
    "subscription": ["Subscription_Length", "Charge_Amount", "Tariff_Plan"],
    "profile": ["Age_Group"],
}

TEXTS = {
    "id": {
        "page_title": "Pelanggan Mana yang Perlu Dihubungi?",
        "title": "Pelanggan Mana yang Perlu Dihubungi?",
        "subtitle": "Prediksi risiko churn pelanggan telekomunikasi · dataset UCI Iranian Churn",
        "intro": (
            "Demo ini memberi **skor risiko churn** untuk satu pelanggan dan menyarankan apakah pelanggan itu "
            "**perlu dihubungi**. Model yang dipakai adalah XGBoost dengan 12 fitur dari 9 bulan pertama data "
            "pelanggan. Ini proyek portofolio, bukan sistem produksi."
        ),
        "steps": (
            "**1.** Isi data pelanggan atau pilih contoh di sidebar  \n"
            "**2.** Tekan **Hitung skor risiko**  \n"
            "**3.** Atur rasio biaya di sidebar bila perlu, lalu baca hasilnya di bawah"
        ),
        "loading": "Melatih model dari dataset...",
        "tabs": ["Hasil & rekomendasi", "Detail teknis", "Cara kerja model", "Keterbatasan & data"],
        "limitation": LIMITATION_ID,
        # Sidebar
        "language": "Bahasa / Language",
        "examples": "Isi dengan contoh",
        "example_labels": {"high": "Risiko tinggi", "low": "Risiko rendah", "median": "Nilai median"},
        "examples_note": "Contoh risiko tinggi dan rendah adalah pelanggan nyata dari data latih.",
        "form_title": "Data pelanggan",
        "form_note": "Semua nilai adalah agregat 9 bulan pertama, sesuai dokumentasi UCI.",
        "group_labels": {
            "status": "Status & keluhan",
            "usage": "Pemakaian",
            "subscription": "Langganan & tarif",
            "profile": "Profil",
        },
        "submit": "Hitung skor risiko",
        "hint": "umumnya {median} · rentang {low}–{high}",
        # Kelompok usia: tombol berisi perkiraan umur dari kolom Age (asumsi, lihat tab keterbatasan)
        "age_option": "≈{age}",
        "age_value": "{group} (≈{age} th)",
        "age_help": (
            "Model memakai kelompok usia 1–5 (1 = lebih muda, 5 = lebih tua, menurut UCI). Angka di tombol adalah "
            "nilai kolom Age yang selalu berpasangan dengan tiap kelompok di data, dibaca sebagai umur dalam tahun. "
            "Ini asumsi, karena UCI tidak menjelaskan arti Age."
        ),
        "author": "Dibuat oleh {name}",
        "author_placeholder": "[nama pembuat, diisi sebelum deploy]",
        "link_placeholder": "[tautan {name}]",
        # Label fitur: panjang untuk formulir, pendek untuk kalimat dan grafik
        "features": {
            "Call_Failure": "Jumlah kegagalan panggilan",
            "Complains": "Pernah komplain",
            "Subscription_Length": "Lama berlangganan (bulan)",
            "Charge_Amount": "Tingkat tagihan (0 = terendah, 10 = tertinggi)",
            "Seconds_of_Use": "Total detik panggilan",
            "Frequency_of_use": "Total jumlah panggilan",
            "Frequency_of_SMS": "Total jumlah SMS",
            "Distinct_Called_Numbers": "Jumlah panggilan berbeda (Distinct Called Numbers)",
            "Age_Group": "Kelompok usia (perkiraan umur, tahun)",
            "Tariff_Plan": "Paket tarif",
            "Status": "Status",
            "Customer_Value": "Nilai terhitung (Customer_Value, tanpa satuan)",
        },
        "features_short": {
            "Call_Failure": "Kegagalan panggilan",
            "Complains": "Komplain",
            "Subscription_Length": "Lama berlangganan",
            "Charge_Amount": "Tingkat tagihan",
            "Seconds_of_Use": "Detik panggilan",
            "Frequency_of_use": "Jumlah panggilan",
            "Frequency_of_SMS": "Jumlah SMS",
            "Distinct_Called_Numbers": "Panggilan berbeda",
            "Age_Group": "Kelompok usia",
            "Tariff_Plan": "Paket tarif",
            "Status": "Status",
            "Customer_Value": "Nilai terhitung",
        },
        "choices": {
            "Complains": {0: "Tidak", 1: "Ya"},
            "Status": {1: "Aktif", 2: "Non-aktif"},
            "Tariff_Plan": {1: "Pay as you go", 2: "Kontrak"},
        },
        # Tab 1: hasil
        # Bagian pengaturan keputusan di sidebar, terpisah dari data pelanggan
        "decision_title": "Pengaturan keputusan",
        "decision_help": (
            "Bagian ini bukan data pelanggan dan bukan fitur model. Rasio biaya adalah asumsi untuk menentukan skor "
            "minimal untuk dihubungi, dan perubahannya langsung berlaku tanpa menekan tombol hitung."
        ),
        "ratio_label": "Rasio biaya: seberapa merugikan churn terlewat dibanding salah hubungi?",
        "ratio_help": (
            "Rasio adalah asumsi biaya, bukan data. Hitung rasio sendiri: kerugian per churn terlewat dibagi "
            "biaya per salah hubungi. Default 1:5 adalah titik awal, bukan rasio yang terbukti benar."
        ),
        "ratio_default": "{ratio} (default)",
        "ratio_explanations": {
            "1:2": "Churn terlewat dianggap 2 kali lebih merugikan daripada salah hubungi. "
                   "Cocok jika biaya menghubungi cukup mahal.",
            "1:5": "Churn terlewat dianggap 5 kali lebih merugikan daripada salah hubungi. "
                   "Cocok jika biaya menghubungi sedang.",
            "1:10": "Churn terlewat dianggap 10 kali lebih merugikan daripada salah hubungi. "
                    "Cocok jika biaya menghubungi murah.",
        },
        "sources": {
            "median": "nilai median data latih",
            "high": "contoh risiko tinggi",
            "low": "contoh risiko rendah",
            "form": "data yang kamu isi",
        },
        "invalid": "Input tidak valid:",
        "metric_score": "Skor risiko",
        "metric_score_help": "Skor model antara 0 dan 1 untuk mengurutkan pelanggan. Bukan peluang yang terkalibrasi.",
        # Label pendek supaya muat satu baris di kartu. Artinya dijelaskan di ikon bantuan
        "metric_threshold": "Skor minimal dihubungi ({ratio})",
        "metric_threshold_help": (
            "Pelanggan disarankan dihubungi jika skor risikonya sama dengan atau di atas angka ini. Angkanya "
            "bergantung pada rasio biaya yang dipilih di atas."
        ),
        "metric_decision": "Keputusan",
        "contact": "Hubungi",
        "no_contact": "Tidak dihubungi",
        # Penjelasan hasil dalam bahasa awam, dipilih sesuai keputusan
        "position_explain_contact": (
            "**Pelanggan ini disarankan dihubungi.** Skor risikonya {score}, sudah mencapai skor minimal untuk dihubungi "
            "({threshold}). Artinya, menurut model, pola pelanggan ini mirip pelanggan yang churn."
        ),
        "position_explain_no_contact": (
            "**Pelanggan ini belum perlu dihubungi.** Skor risikonya {score}, masih di bawah skor minimal untuk dihubungi "
            "({threshold}). Artinya, menurut model, pola pelanggan ini lebih mirip pelanggan yang bertahan."
        ),
        "position_caption": (
            "Titik adalah skor pelanggan ini, dan area merah muda adalah zona hubungi. Makin ke kanan, makin tinggi "
            "risiko churn menurut model. Jarak angka pada sumbu dibuat bertingkat (skala log) supaya skor yang sangat "
            "kecil tetap terlihat."
        ),
        "position_threshold": "Skor minimal {ratio}",
        "position_axis": "Skor risiko (skala log)",
        "position_zone": "Zona hubungi",
        "why_title": "Mengapa skornya begini?",
        # Frasa bahasa awam per fitur untuk insight di tab bisnis
        "phrases": {
            "Call_Failure": "kegagalan panggilannya {value} kali",
            "Complains": {0: "ia tidak pernah komplain", 1: "ia pernah komplain"},
            "Subscription_Length": "ia sudah berlangganan {value} bulan",
            "Charge_Amount": "tingkat tagihannya {value}",
            "Seconds_of_Use": "total waktu panggilannya {value} detik",
            "Frequency_of_use": "jumlah panggilannya {value} kali",
            "Frequency_of_SMS": "jumlah SMS-nya {value}",
            "Distinct_Called_Numbers": "jumlah panggilan berbedanya {value}",
            "Age_Group": "kelompok usianya {value}",
            "Tariff_Plan": {1: "ia memakai paket pay as you go", 2: "ia memakai paket kontrak"},
            "Status": {1: "statusnya aktif", 2: "statusnya non-aktif"},
            "Customer_Value": "nilai terhitungnya {value}",
        },
        "compare_above": "(di atas umumnya, {typical})",
        "compare_below": "(di bawah umumnya, {typical})",
        "compare_choice": "(kebanyakan pelanggan {typical})",
        "and": "dan",
        # Subjek di awal frasa kata kerja, dibuang saat frasa dipakai sebagai pembanding
        "subject": "ia ",
        "insight_contact": "Menurut model, pola pelanggan ini **mirip pelanggan yang churn**.",
        "insight_no_contact": "Menurut model, pola pelanggan ini **mirip pelanggan yang bertahan**.",
        "insight_main_contact": "Tanda yang paling kuat: {items}.",
        "insight_main_no_contact": "Hal yang paling menahan risikonya: {items}.",
        "insight_other_contact": "Sebaliknya, ada hal yang sedikit menahan risikonya: {items}.",
        "insight_other_no_contact": "Meski begitu, ada hal yang sedikit menaikkan risikonya: {items}.",
        "risk_contact": "Karena polanya mirip pelanggan yang churn, risiko pelanggan ini tergolong tinggi.",
        "risk_no_contact": "Karena polanya mirip pelanggan yang bertahan, risiko pelanggan ini tergolong rendah.",
        "position_above": "di atas",
        "position_equal": "sama dengan",
        "position_below": "di bawah",
        "segment_bridge": (
            "{risk} Namun, risiko saja belum cukup untuk menentukan prioritas, karena nilai tiap pelanggan "
            "berbeda. Nilai terhitung pelanggan ini {value}, {position} nilai tengah semua pelanggan ({cutoff}). "
            "Gabungan risiko dan nilai itu menempatkannya di **{segment}** pada matriks: {desc}."
        ),
        "now_title": "Rekomendasi untuk siklus tahun berikutnya (hipotesis, perlu diuji)",
        "now_intro": (
            "Data ini mencakup satu siklus 12 bulan: perilaku pelanggan dicatat selama 9 bulan pertama, lalu status "
            "churn dilihat di akhir bulan ke-12. Rekomendasi di bawah memakai siklus yang sama untuk tahun berikutnya."
        ),
        "now_caution": "Yang perlu diperhatikan",
        "personal_title": "Disesuaikan dengan pelanggan ini",
        # Saran tambahan dari alasan risiko pelanggan ini (hanya untuk pelanggan yang disarankan dihubungi)
        "hints": {
            "Complains": "Karena ia pernah komplain, pastikan keluhannya sudah selesai sebelum menawarkan apa pun.",
            "Status": "Karena statusnya non-aktif, ajak ia kembali memakai layanan, misalnya dengan bonus pemakaian.",
            "Call_Failure": (
                "Karena kegagalan panggilannya di atas umumnya, periksa kualitas sinyal di area tempat ia biasa "
                "menelepon."
            ),
            "low_usage": "Karena pemakaiannya di bawah umumnya, tawarkan paket yang lebih sesuai dengan kebutuhannya.",
        },
        "reasons_caption": (
            "Ini pola yang dipakai model, bukan sebab pelanggan churn. Rinciannya ada di tab **Detail teknis**."
        ),
        "why_caption": (
            "Grafik menunjukkan dorongan tiap fitur, dari skor dasar (rata-rata model) sampai skor akhir pelanggan "
            "ini. Merah menaikkan skor dan biru menurunkan. Ini menggambarkan cara model bekerja, bukan sebab "
            "pelanggan churn."
        ),
        "waterfall_base": "Skor dasar",
        "waterfall_final": "Skor akhir",
        "waterfall_axis": "Dorongan ke skor (log-odds)",
        "waterfall_up": "Menaikkan",
        "waterfall_down": "Menurunkan",
        "technical": "Rincian angka (SHAP)",
        "technical_text": (
            "Dorongan dihitung dengan SHAP bawaan XGBoost (`pred_contribs`), dalam satuan log-odds. Skor dasar "
            "{base} ditambah semua dorongan ({total}) sama dengan {margin} log-odds, yang setara skor {score}. "
            "Library `shap` tidak dipakai karena belum mendukung XGBoost 3."
        ),
        "table_feature": "Fitur",
        "table_value": "Nilai",
        "table_shap": "Dorongan (log-odds)",
        "segment_title": "Segmen risiko × nilai",
        "segment_axis_value": "Nilai terhitung",
        "segment_axis_risk": "Risiko",
        "segment_low": "Rendah",
        "segment_high": "Tinggi",
        "segment_you": "pelanggan ini",
        "segments": {
            "I": {
                "name": "Prioritas I",
                "desc": "Risiko tinggi, nilai terhitung tinggi",
                "summary": (
                    "Pelanggan ini paling layak didahulukan. Kemungkinan churn-nya tinggi, dan nilainya di atas "
                    "nilai tengah, sehingga kehilangan dia paling terasa dibanding pelanggan lain."
                ),
                "steps": [
                    ("**Akhir bulan ke-9:** setelah data 9 bulan terkumpul, hitung ulang skornya. Jika masih masuk "
                     "Prioritas I, taruh di urutan paling atas daftar pelanggan yang akan dihubungi."),
                    ("**Awal bulan ke-10:** hubungi secara pribadi, misalnya lewat telepon oleh petugas layanan "
                     "pelanggan. Tanyakan pengalamannya lebih dulu, sebelum menawarkan apa pun."),
                    ("**Bulan ke-10 sampai ke-11:** tawarkan sesuatu yang sepadan dengan nilainya, misalnya potongan "
                     "harga atau bonus paket selama beberapa bulan."),
                    ("**Akhir bulan ke-12:** cek apakah ia masih menjadi pelanggan, lalu catat hasilnya. Catatan ini "
                     "berguna untuk menilai tindakan dan memperbarui model."),
                ],
                "caution": (
                    "Sisihkan sebagian kecil pelanggan Prioritas I yang sengaja tidak dihubungi sebagai pembanding. "
                    "Tindakan dianggap berhasil jika churn di kelompok yang dihubungi lebih rendah daripada di "
                    "kelompok pembanding. Tanpa pembanding, kita tidak tahu apakah pelanggan bertahan karena "
                    "dihubungi atau memang akan bertahan."
                ),
            },
            "II": {
                "name": "Prioritas II",
                "desc": "Risiko rendah, nilai terhitung tinggi",
                "summary": (
                    "Pelanggan ini bernilai tinggi dan kemungkinan besar bertahan. Fokusnya adalah menjaga hubungan "
                    "baik, bukan mencegah churn."
                ),
                "steps": [
                    ("**Sepanjang tahun:** ikutkan dalam program loyalitas, misalnya poin pemakaian atau hadiah "
                     "kecil di hari jadi berlangganan."),
                    ("**Akhir bulan ke-9:** hitung ulang skornya. Jika skornya naik sampai skor minimal untuk "
                     "dihubungi, perlakukan seperti Prioritas I."),
                    "**Akhir bulan ke-12:** pastikan ia masih menjadi pelanggan.",
                ],
                "caution": (
                    "Hindari potongan harga besar. Pelanggan ini kemungkinan bertahan tanpa itu, jadi biayanya bisa "
                    "terbuang."
                ),
            },
            "III": {
                "name": "Prioritas III",
                "desc": "Risiko tinggi, nilai terhitung rendah",
                "summary": (
                    "Pelanggan ini kemungkinan churn, tetapi nilainya di bawah nilai tengah. Ia tetap perlu "
                    "dihubungi, tetapi dengan cara yang murah dan setelah pelanggan Prioritas I selesai ditangani."
                ),
                "steps": [
                    ("**Akhir bulan ke-9:** hitung ulang skornya. Jika masih berisiko tinggi, masukkan ke daftar "
                     "kontak setelah Prioritas I."),
                    ("**Bulan ke-10 sampai ke-11:** kirim pesan otomatis, misalnya SMS atau notifikasi aplikasi, "
                     "berisi penawaran ringan seperti bonus kuota atau SMS gratis."),
                    ("**Akhir bulan ke-12:** cek apakah ia masih menjadi pelanggan, lalu catat hasilnya untuk "
                     "menilai tindakan dan memperbarui model."),
                ],
                "caution": (
                    "Jaga biaya per pelanggan tetap kecil, karena nilainya rendah. Seperti Prioritas I, sisihkan "
                    "sebagian kecil pelanggan yang tidak dihubungi sebagai pembanding."
                ),
            },
            "IV": {
                "name": "Prioritas IV",
                "desc": "Risiko rendah, nilai terhitung rendah",
                "summary": (
                    "Pelanggan ini kemungkinan bertahan dan nilainya di bawah nilai tengah, jadi belum perlu "
                    "tindakan khusus."
                ),
                "steps": [
                    "**Sepanjang tahun:** layani seperti biasa, tanpa penawaran khusus.",
                    ("**Akhir bulan ke-9:** hitung ulang skornya. Jika skornya naik sampai skor minimal untuk "
                     "dihubungi, perlakukan seperti Prioritas III."),
                ],
                "caution": (
                    "Perubahan yang perlu diwaspadai: komplain baru, status berubah menjadi non-aktif, atau pemakaian "
                    "yang turun tajam. Di data latih, tanda-tanda ini sering muncul pada pelanggan yang churn."
                ),
            },
        },
        # Tab Hasil & rekomendasi: satu judul, lalu alur What, So What, Now What tanpa judul per bagian
        "business_title": "Perlukah pelanggan ini dihubungi?",
        "business_source": "Berdasarkan: {source}",
        "now_caption": (
            "Semua langkah adalah hipotesis yang perlu diuji, dan contoh penawaran hanyalah gambaran. Rekomendasi "
            "mengasumsikan pola pelanggan di tahun berikutnya mirip dengan data ini."
        ),
        # Tab Detail teknis
        "tech_customer_title": "Bagaimana model sampai ke skor ini?",
        "position_title": "Posisi skor terhadap skor minimal",
        # Catatan segmen versi singkat untuk pembaca awam. Detail teknis ada di ikon bantuan judul segmen
        "segment_note": (
            # Batas nilai sudah disebut di kalimat segmen, jadi catatan ini tidak mengulangnya
            "Pelanggan masuk kelompok risiko tinggi jika disarankan untuk dihubungi. Nilai terhitung bukan jumlah "
            "uang."
        ),
        "segment_help": (
            "Nilai terhitung adalah kolom Customer_Value dari UCI, tanpa rumus dan satuan. Di demo, segmen memakai "
            "skor satu model final, sedangkan notebook memakai suara mayoritas dari 10 ulangan out-of-fold, jadi "
            "pelanggan di dekat batas bisa berbeda segmen."
        ),
        # Pengingat singkat di bawah hasil. Kalimat keterbatasan lengkap ada di tab Keterbatasan & data
        "limitation_box": (
            "**Catatan:** skor model bisa terlalu optimistis karena data memuat pola berulang. Selengkapnya di tab "
            "**Keterbatasan & data**."
        ),
        # Tab 2: cara kerja model
        "flow_title": "Alur data dan model",
        "flow": {
            "raw": "Data mentah UCI\n{raw} baris",
            "clean": "Hapus {duplicates} duplikat persis\n{clean} baris",
            "train": "Data latih 80%\n{train} baris, {train_churn} churn",
            "test": "Data uji 20%\n{test} baris, {test_churn} churn\ndinilai sekali di akhir",
            "model": "XGBoost default\n12 fitur",
            "threshold": "Skor minimal dihubungi\ndari rasio biaya",
            "decision": "Keputusan hubungi\n+ segmen risiko × nilai",
        },
        "flow_caption": (
            "Model, skor minimal untuk dihubungi, dan semua angka di tab ini berasal dari data latih. Data uji hanya dipakai "
            "sekali untuk penilaian akhir, dan tidak dipakai demo."
        ),
        "metrics_title": "Seberapa baik model mengurutkan pelanggan churn?",
        "metric_pr": "PR-AUC XGBoost",
        "metric_pr_base": "PR-AUC baseline",
        "metric_roc": "ROC-AUC XGBoost",
        "metric_range": "rentang 10 ulangan: {low}–{high}",
        "metric_base_note": "DummyClassifier, sama dengan churn rate",
        "metrics_text": (
            "PR-AUC (0 sampai 1) mengukur seberapa baik model menaruh pelanggan churn di urutan atas. Baseline "
            "adalah model yang menebak tanpa melihat fitur. Angka berasal dari CV acak 5-fold yang diulang 10 kali "
            "di data latih. **Angka ini bukan performa pada pelanggan baru**, dan skor setinggi ini dibaca dengan "
            "curiga (lihat tab Keterbatasan & data)."
        ),
        "importance_title": "Fitur apa yang paling diandalkan model?",
        "importance_axis": "Turunnya PR-AUC saat fitur diacak",
        "importance_group": "Kelompok pemakaian (5 kolom)",
        "importance_text": (
            "Panjang batang adalah turunnya PR-AUC saat nilai satu fitur diacak di data validasi. Makin panjang, "
            "makin besar model bergantung pada fitur itu, dan garis menunjukkan rentang 10 ulangan. Lima kolom "
            "pemakaian (detik, panggilan, SMS, panggilan berbeda, dan nilai terhitung) saling berkaitan, jadi juga "
            "dinilai bersama sebagai satu kelompok. Kepentingan fitur menunjukkan pola yang dipakai model, bukan "
            "sebab churn."
        ),
        "ratio_title": "Bagaimana skor minimal untuk dihubungi dipilih?",
        "ratio_text": (
            "Model memberi skor, lalu pelanggan dihubungi jika skornya sama dengan atau di atas skor minimal "
            "(threshold). Skor minimal dipilih dari **rasio biaya**, yaitu kerugian satu churn terlewat dibanding biaya satu salah hubungi. "
            "Untuk tiap rasio, dicari skor minimal dengan total biaya terendah pada prediksi out-of-fold data latih. "
            "Pencarian diulang 10 kali, lalu diambil mediannya. Rasio adalah asumsi, bukan data."
        ),
        "ratio_table": {"ratio": "Rasio", "threshold": "Skor minimal dihubungi", "range": "Rentang 10 ulangan",
                        "meaning": "Arti"},
        # Tab 3: keterbatasan dan data
        "lim_pattern_title": "Pola berulang per 50 baris",
        "lim_pattern_text": (
            # Melengkapi kotak keterbatasan di atasnya tanpa mengulang isinya
            "Pada pola itu, baris di file data yang menempati posisi sama, misalnya baris ke-1, ke-51, dan ke-101, "
            "cenderung sangat mirip. Karena itu, data latih dan data uji bisa memuat pelanggan yang hampir sama, "
            "sehingga model terlihat lebih baik daripada kemampuannya saat menghadapi pelanggan yang benar-benar "
            "baru. Penyebab pola ini belum diketahui, dan audit lengkapnya tersimpan di repo."
        ),
        "lim_uci_title": "Informasi yang tidak tersedia di dokumentasi data (UCI)",
        "lim_uci_items": [
            "**Definisi churn**: apakah berhenti berlangganan, pindah operator, atau tidak aktif.",
            "**Cara `Status` ditentukan** (aktif atau non-aktif).",
            "**Rumus `Customer_Value`.** Karena itu kolom ini disebut **nilai terhitung**, bukan uang.",
            "**Arti kolom `Age`.** Kolom ini tidak dipakai model, dan model memakai `Age_Group`.",
        ],
        "lim_assumption_title": "Asumsi yang dipakai demo, jadi baca hasilnya dengan hati-hati",
        "lim_assumption_items": [
            "**Rasio biaya adalah asumsi**, bukan data dari perusahaan.",
            ("**Skor risiko bukan peluang** yang terkalibrasi. Skor dipakai untuk mengurutkan dan dibandingkan "
            "dengan skor minimal untuk dihubungi."),
            ("**Segmen memakai skor satu model final**, sedangkan notebook memakai suara mayoritas dari 10 ulangan "
            "out-of-fold."),
            "**Hasil bersifat asosiatif.** Demo tidak membuktikan bahwa menghubungi pelanggan akan mencegah churn.",
            ("**Input harus berada dalam rentang data latih**, karena model tidak pernah melihat pelanggan di luar "
            "rentang itu."),
            ("**Umur di formulir adalah perkiraan.** Tiap kelompok usia ditampilkan dengan nilai kolom `Age` yang "
            "selalu berpasangan dengannya di data ({ages}), lalu dibaca sebagai umur dalam tahun. UCI tidak "
            "menjelaskan arti `Age`, jadi ini asumsi. Model tetap memakai kelompok 1–5."),
            ("**Waktu tindakan adalah tafsiran.** Menurut UCI, fitur berasal dari 9 bulan pertama dan status churn "
            "dicatat di akhir bulan ke-12. Jeda 3 bulan di antaranya dipakai sebagai waktu untuk menghubungi "
            "pelanggan, padahal UCI tidak menyebut kapan pelanggan benar-benar berhenti. Rekomendasi juga "
            "mengasumsikan pola pelanggan di tahun berikutnya mirip dengan data ini, padahal pola bisa berubah."),
        ],
        "lim_source_title": "Sumber, lisensi & privasi",
        "lim_source_items": [
            ("Data: *Iranian Churn [Dataset]. (2020). UCI Machine Learning Repository.* "
            "https://doi.org/10.24432/C5JW3Z, lisensi CC BY 4.0."),
            "Input yang kamu isi hanya dipakai untuk menghitung skor saat itu dan **tidak disimpan**.",
            "Model dilatih ulang dari dataset setiap kali aplikasi menyala, tanpa file model tersimpan.",
        ],
    },
    "en": {
        "page_title": "Which Customers Should Be Contacted?",
        "title": "Which Customers Should Be Contacted?",
        "subtitle": "Churn risk prediction for telecom customers · UCI Iranian Churn dataset",
        "intro": (
            "This demo gives a **churn risk score** for one customer and suggests whether that customer "
            "**should be contacted**. The model is XGBoost with 12 features from the first 9 months of customer "
            "data. This is a portfolio project, not a production system."
        ),
        "steps": (
            "**1.** Fill in customer data or pick an example in the sidebar  \n"
            "**2.** Press **Calculate risk score**  \n"
            "**3.** Adjust the cost ratio in the sidebar if needed, then read the result below"
        ),
        "loading": "Training the model from the dataset...",
        "tabs": ["Results & recommendation", "Technical details", "How the model works", "Limitations & data"],
        "limitation": LIMITATION_EN,
        "language": "Bahasa / Language",
        "examples": "Fill with an example",
        "example_labels": {"high": "High risk", "low": "Low risk", "median": "Median values"},
        "examples_note": "The high and low risk examples are real customers from the training data.",
        "form_title": "Customer data",
        "form_note": "All values are totals for the first 9 months, following the UCI documentation.",
        "group_labels": {
            "status": "Status & complaints",
            "usage": "Usage",
            "subscription": "Subscription & tariff",
            "profile": "Profile",
        },
        "submit": "Calculate risk score",
        "hint": "typical {median} · range {low}–{high}",
        "age_option": "≈{age}",
        "age_value": "{group} (≈{age} yrs)",
        "age_help": (
            "The model uses age groups 1–5 (1 = younger, 5 = older, according to UCI). The number on each button is "
            "the value of the Age column always paired with that group in the data, read as age in years. This is an "
            "assumption, because UCI does not explain Age."
        ),
        "author": "Made by {name}",
        "author_placeholder": "[author name, filled in before deploy]",
        "link_placeholder": "[{name} link]",
        "features": {
            "Call_Failure": "Number of call failures",
            "Complains": "Has complained",
            "Subscription_Length": "Subscription length (months)",
            "Charge_Amount": "Charge level (0 = lowest, 10 = highest)",
            "Seconds_of_Use": "Total call seconds",
            "Frequency_of_use": "Total number of calls",
            "Frequency_of_SMS": "Total number of SMS",
            "Distinct_Called_Numbers": "Number of distinct calls (Distinct Called Numbers)",
            "Age_Group": "Age group (estimated age, years)",
            "Tariff_Plan": "Tariff plan",
            "Status": "Status",
            "Customer_Value": "Calculated value (Customer_Value, no unit)",
        },
        "features_short": {
            "Call_Failure": "Call failures",
            "Complains": "Complained",
            "Subscription_Length": "Subscription length",
            "Charge_Amount": "Charge level",
            "Seconds_of_Use": "Call seconds",
            "Frequency_of_use": "Number of calls",
            "Frequency_of_SMS": "Number of SMS",
            "Distinct_Called_Numbers": "Distinct calls",
            "Age_Group": "Age group",
            "Tariff_Plan": "Tariff plan",
            "Status": "Status",
            "Customer_Value": "Calculated value",
        },
        "choices": {
            "Complains": {0: "No", 1: "Yes"},
            "Status": {1: "Active", 2: "Inactive"},
            "Tariff_Plan": {1: "Pay as you go", 2: "Contract"},
        },
        "decision_title": "Decision setting",
        "decision_help": (
            "This section is not customer data and not a model feature. The cost ratio is an assumption used to set "
            "the minimum score to contact, and changes apply immediately without pressing the calculate button."
        ),
        "ratio_label": "Cost ratio: how much worse is a missed churner than an unnecessary contact?",
        "ratio_help": (
            "The ratio is a cost assumption, not data. Your own ratio: the loss per missed churner divided by the "
            "cost per unnecessary contact. The default 1:5 is a starting point, not a proven ratio."
        ),
        "ratio_default": "{ratio} (default)",
        "ratio_explanations": {
            "1:2": "A missed churner is treated as 2 times worse than an unnecessary contact. "
                   "Suits a fairly expensive contact.",
            "1:5": "A missed churner is treated as 5 times worse than an unnecessary contact. "
                   "Suits a moderately priced contact.",
            "1:10": "A missed churner is treated as 10 times worse than an unnecessary contact. "
                    "Suits a cheap contact.",
        },
        "sources": {
            "median": "median values of the training data",
            "high": "high risk example",
            "low": "low risk example",
            "form": "the data you entered",
        },
        "invalid": "Invalid input:",
        "metric_score": "Risk score",
        "metric_score_help": "Model score between 0 and 1 for ranking customers. Not a calibrated probability.",
        "metric_threshold": "Minimum score to contact ({ratio})",
        "metric_threshold_help": (
            "A customer is suggested for contact if their risk score is equal to or above this number. The number "
            "depends on the cost ratio selected above."
        ),
        "metric_decision": "Decision",
        "contact": "Contact",
        "no_contact": "No contact",
        "position_explain_contact": (
            "**This customer should be contacted.** Their risk score is {score}, which reaches the minimum score to "
            "contact ({threshold}). In other words, the model sees this customer's pattern as similar to customers who "
            "churned."
        ),
        "position_explain_no_contact": (
            "**This customer does not need to be contacted yet.** Their risk score is {score}, below the minimum score to "
            "contact ({threshold}). In other words, the model sees this customer's pattern as closer to customers who "
            "stayed."
        ),
        "position_caption": (
            "The dot is this customer's score, and the pink area is the contact zone. Further right means a higher "
            "churn risk according to the model. The axis uses stepped spacing (log scale) so very small scores stay "
            "visible."
        ),
        "position_threshold": "Minimum {ratio}",
        "position_axis": "Risk score (log scale)",
        "position_zone": "Contact zone",
        "why_title": "Why this score?",
        "phrases": {
            "Call_Failure": "had {value} call failures",
            "Complains": {0: "never complained", 1: "has complained"},
            "Subscription_Length": "has subscribed for {value} months",
            "Charge_Amount": "has a charge level of {value}",
            "Seconds_of_Use": "used {value} seconds of calls",
            "Frequency_of_use": "made {value} calls",
            "Frequency_of_SMS": "sent {value} SMS",
            "Distinct_Called_Numbers": "made {value} distinct calls",
            "Age_Group": "is in age group {value}",
            "Tariff_Plan": {1: "uses the pay as you go plan", 2: "uses the contract plan"},
            "Status": {1: "is active", 2: "is inactive"},
            "Customer_Value": "has a calculated value of {value}",
        },
        "compare_above": "(above the typical {typical})",
        "compare_below": "(below the typical {typical})",
        "compare_choice": "(most customers: {typical})",
        "and": "and",
        "subject": "",
        "insight_contact": "According to the model, this customer's pattern is **similar to customers who churned**.",
        "insight_no_contact": "According to the model, this customer's pattern is **similar to customers who stayed**.",
        "insight_main_contact": "The strongest signs: the customer {items}.",
        "insight_main_no_contact": "What holds the risk down most: the customer {items}.",
        "insight_other_contact": "On the other hand, a few things slightly lower the risk: the customer {items}.",
        "insight_other_no_contact": "Even so, a few things slightly raise the risk: the customer {items}.",
        "risk_contact": "Because the pattern resembles customers who churned, this customer's risk is high.",
        "risk_no_contact": "Because the pattern resembles customers who stayed, this customer's risk is low.",
        "position_above": "above",
        "position_equal": "equal to",
        "position_below": "below",
        "segment_bridge": (
            "{risk} But risk alone does not set the priority, because customers differ in value. This "
            "customer's calculated value is {value}, {position} the middle value of all customers ({cutoff}). "
            "Together, risk and value place the customer in **{segment}** on the matrix: {desc}."
        ),
        "now_title": "Recommendation for the next yearly cycle (hypothesis, needs testing)",
        "now_intro": (
            "This data covers one 12-month cycle: customer behaviour is recorded during the first 9 months, then "
            "the churn status is checked at the end of month 12. The recommendation below uses the same cycle for "
            "the next year."
        ),
        "now_caution": "Keep in mind",
        "personal_title": "Tailored to this customer",
        "hints": {
            "Complains": "Because they have complained, make sure the complaint is resolved before offering anything.",
            "Status": "Because they are inactive, invite them back to the service, for example with bonus usage.",
            "Call_Failure": (
                "Because their call failures are above typical, check the signal quality where they usually make "
                "calls."
            ),
            "low_usage": "Because their usage is below typical, offer a plan that better fits their needs.",
        },
        "reasons_caption": (
            "These are patterns the model uses, not causes of churn. The details are in the **Technical details** tab."
        ),
        "why_caption": (
            "The chart shows each feature's push, from the base score (the model average) to this customer's final "
            "score. Red raises the score and blue lowers it. This describes how the model works, not why a customer "
            "churns."
        ),
        "waterfall_base": "Base score",
        "waterfall_final": "Final score",
        "waterfall_axis": "Push on the score (log-odds)",
        "waterfall_up": "Raises",
        "waterfall_down": "Lowers",
        "technical": "Full numbers (SHAP)",
        "technical_text": (
            "Pushes are computed with XGBoost's built-in SHAP (`pred_contribs`), in log-odds. The base score {base} "
            "plus all pushes ({total}) equals {margin} log-odds, which corresponds to a score of {score}. The `shap` "
            "library is not used because it does not support XGBoost 3 yet."
        ),
        "table_feature": "Feature",
        "table_value": "Value",
        "table_shap": "Push (log-odds)",
        "segment_title": "Risk × value segment",
        "segment_axis_value": "Calculated value",
        "segment_axis_risk": "Risk",
        "segment_low": "Low",
        "segment_high": "High",
        "segment_you": "this customer",
        "segments": {
            "I": {
                "name": "Priority I",
                "desc": "High risk, high calculated value",
                "summary": (
                    "This customer deserves attention first. The churn risk is high and the value is above the "
                    "middle value, so losing this customer would hurt more than losing others."
                ),
                "steps": [
                    ("**End of month 9:** once 9 months of data are collected, recalculate the score. If the "
                     "customer is still Priority I, put them at the top of the contact list."),
                    ("**Start of month 10:** contact them personally, for example a phone call from customer "
                     "service. Ask about their experience first, before offering anything."),
                    ("**Months 10 to 11:** offer something that matches their value, for example a discount or a "
                     "bonus package for a few months."),
                    ("**End of month 12:** check whether they are still a customer and record the result. This "
                     "record helps evaluate the action and update the model."),
                ],
                "caution": (
                    "Set aside a small share of Priority I customers who are deliberately not contacted as a "
                    "comparison group. The action works if churn among contacted customers is lower than in the "
                    "comparison group. Without it, we cannot tell whether customers stayed because of the contact or "
                    "would have stayed anyway."
                ),
            },
            "II": {
                "name": "Priority II",
                "desc": "Low risk, high calculated value",
                "summary": (
                    "This customer has high value and will most likely stay. The focus is keeping a good "
                    "relationship, not preventing churn."
                ),
                "steps": [
                    ("**All year:** include them in a loyalty programme, for example usage points or a small gift on "
                     "their subscription anniversary."),
                    ("**End of month 9:** recalculate the score. If it rises to the minimum score to contact, treat "
                     "them like Priority I."),
                    "**End of month 12:** make sure they are still a customer.",
                ],
                "caution": (
                    "Avoid large discounts. This customer will likely stay without them, so the cost may be wasted."
                ),
            },
            "III": {
                "name": "Priority III",
                "desc": "High risk, low calculated value",
                "summary": (
                    "This customer may churn, but their value is below the middle value. They still need contact, "
                    "but in a cheap way and after Priority I customers have been handled."
                ),
                "steps": [
                    ("**End of month 9:** recalculate the score. If the risk is still high, add them to the contact "
                     "list after Priority I."),
                    ("**Months 10 to 11:** send an automated message, for example an SMS or app notification, with "
                     "a light offer such as bonus data or free SMS."),
                    ("**End of month 12:** check whether they are still a customer and record the result to "
                     "evaluate the action and update the model."),
                ],
                "caution": (
                    "Keep the cost per customer small, because the value is low. As with Priority I, set aside a "
                    "small share of customers who are not contacted as a comparison group."
                ),
            },
            "IV": {
                "name": "Priority IV",
                "desc": "Low risk, low calculated value",
                "summary": (
                    "This customer will likely stay and their value is below the middle value, so no special action "
                    "is needed yet."
                ),
                "steps": [
                    "**All year:** serve them as usual, without special offers.",
                    ("**End of month 9:** recalculate the score. If it rises to the minimum score to contact, treat "
                     "them like Priority III."),
                ],
                "caution": (
                    "Changes to watch for: a new complaint, a status change to inactive, or a sharp drop in usage. In "
                    "the training data, these signs often appear among customers who churned."
                ),
            },
        },
        "business_title": "Should this customer be contacted?",
        "business_source": "Based on: {source}",
        "now_caption": (
            "All steps are hypotheses that need testing, and the example offers are only illustrations. The "
            "recommendation assumes that next year's customer patterns resemble this data."
        ),
        "tech_customer_title": "How did the model reach this score?",
        "position_title": "Score position against the minimum score",
        "segment_note": (
            "A customer is high risk if they are suggested for contact. The calculated value is not an amount of "
            "money."
        ),
        "segment_help": (
            "The calculated value is the Customer_Value column from UCI, with no formula or unit. In the demo, the "
            "segment uses the score of one final model, while the notebook uses a majority vote over 10 out-of-fold "
            "repeats, so customers near the minimum score may fall in a different segment."
        ),
        "limitation_box": (
            "**Note:** model scores may be overly optimistic because the data contains a repeating pattern. More in "
            "the **Limitations & data** tab."
        ),
        "flow_title": "Data and model flow",
        "flow": {
            "raw": "UCI raw data\n{raw} rows",
            "clean": "Remove {duplicates} exact duplicates\n{clean} rows",
            "train": "Training data 80%\n{train} rows, {train_churn} churn",
            "test": "Test data 20%\n{test} rows, {test_churn} churn\nevaluated once at the end",
            "model": "Default XGBoost\n12 features",
            "threshold": "Minimum score to contact\nfrom cost ratio",
            "decision": "Contact decision\n+ risk × value segment",
        },
        "flow_caption": (
            "The model, the minimum score to contact, and every number in this tab come from the training data. The test "
            "data was used once for the final evaluation and is not used by the demo."
        ),
        "metrics_title": "How well does the model rank churners?",
        "metric_pr": "XGBoost PR-AUC",
        "metric_pr_base": "Baseline PR-AUC",
        "metric_roc": "XGBoost ROC-AUC",
        "metric_range": "range over 10 repeats: {low}–{high}",
        "metric_base_note": "DummyClassifier, equal to the churn rate",
        "metrics_text": (
            "PR-AUC (0 to 1) measures how well the model puts churners at the top of the ranking. The baseline is a "
            "model that guesses without looking at features. The numbers come from 5-fold random CV repeated 10 "
            "times on the training data. **These numbers are not performance on new customers**, and a score this "
            "high is read with suspicion (see the Limitations & data tab)."
        ),
        "importance_title": "Which features does the model rely on most?",
        "importance_axis": "Drop in PR-AUC when the feature is shuffled",
        "importance_group": "Usage group (5 columns)",
        "importance_text": (
            "Bar length is the drop in PR-AUC when one feature's values are shuffled in the validation data. The "
            "longer the bar, the more the model relies on that feature, and the line shows the range over 10 "
            "repeats. The five usage columns (seconds, calls, SMS, distinct calls, and calculated value) are related, "
            "so they are also scored together as one group. Feature importance shows patterns the model uses, not "
            "causes of churn."
        ),
        "ratio_title": "How is the minimum score to contact chosen?",
        "ratio_text": (
            "The model gives a score, and a customer is contacted if the score reaches the minimum score "
            "(threshold). The minimum comes from a **cost ratio**: the loss from one missed churner compared with the cost of one "
            "unnecessary contact. For each ratio, the threshold with the lowest total cost is found on out-of-fold "
            "predictions of the training data. The search is repeated 10 times and the median is taken. The ratio "
            "is an assumption, not data."
        ),
        "ratio_table": {"ratio": "Ratio", "threshold": "Minimum score to contact", "range": "Range over 10 repeats",
                        "meaning": "Meaning"},
        "lim_pattern_title": "A pattern repeating every 50 rows",
        "lim_pattern_text": (
            "Within this pattern, rows in the same position in the data file, for example rows 1, 51, and 101, tend "
            "to be very similar. As a result, the training and test data may contain nearly identical customers, so "
            "the model looks better than it would on truly new customers. The cause of the pattern is unknown, and "
            "the full audit is kept in the repo."
        ),
        "lim_uci_title": "Information missing from the data documentation (UCI)",
        "lim_uci_items": [
            "**The definition of churn**: cancelling, switching operator, or becoming inactive.",
            "**How `Status` is determined** (active or inactive).",
            "**The formula of `Customer_Value`.** That is why it is called the **calculated value**, not money.",
            "**The meaning of `Age`.** This column is not used; the model uses `Age_Group`.",
        ],
        "lim_assumption_title": "Assumptions behind this demo, so read results with care",
        "lim_assumption_items": [
            "**The cost ratio is an assumption**, not company data.",
            ("**The risk score is not a calibrated probability.** It is used for ranking and for comparison with the "
            "minimum score to contact."),
            ("**The segment uses the score of one final model**, while the notebook uses a majority vote over 10 "
            "out-of-fold repeats."),
            "**Results are associative.** The demo does not prove that contacting a customer prevents churn.",
            ("**Inputs must stay within the training data range**, because the model has never seen customers outside "
            "it."),
            ("**Ages in the form are estimates.** Each age group is shown with the value of the `Age` column it is "
            "always paired with in the data ({ages}), read as age in years. UCI does not explain `Age`, so this is an "
            "assumption. The model still uses groups 1–5."),
            ("**The timing of actions is an interpretation.** According to UCI, features come from the first 9 months "
            "and the churn status is recorded at the end of month 12. The 3-month gap in between is used as the time "
            "to contact customers, although UCI does not say when customers actually leave. The recommendation "
            "also assumes that next year's customer patterns resemble this data, although patterns can change."),
        ],
        "lim_source_title": "Source, license & privacy",
        "lim_source_items": [
            ("Data: *Iranian Churn [Dataset]. (2020). UCI Machine Learning Repository.* "
            "https://doi.org/10.24432/C5JW3Z, license CC BY 4.0."),
            "The data you enter is only used to calculate the score at that moment and is **not stored**.",
            "The model is retrained from the dataset every time the app starts, without a stored model file.",
        ],
    },
}


def fmt_number(lang: str, value: float, decimals: int = 0) -> str:
    """Format angka: Indonesia memakai titik ribuan dan koma desimal, Inggris sebaliknya."""
    text = f"{value:,.{decimals}f}"
    if lang == "id":
        text = text.replace(",", "_").replace(".", ",").replace("_", ".")
    return text


def fmt_score(lang: str, score: float) -> str:
    """Skor dengan 3 desimal. Skor di bawah 0,001 ditulis '< 0,001' supaya tidak terbaca 0."""
    if score < 0.001:
        return "< " + fmt_number(lang, 0.001, 3)
    return fmt_number(lang, score, 3)


def fmt_value(lang: str, feature: str, value: float) -> str:
    """Nilai fitur untuk dibaca manusia: label pilihan, atau angka dengan format bahasa."""
    choices = TEXTS[lang]["choices"].get(feature)
    if choices is not None:
        return choices[int(value)]
    return fmt_number(lang, value, 2 if feature == "Customer_Value" else 0)
