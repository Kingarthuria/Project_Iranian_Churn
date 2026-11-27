"""Demo prediksi churn pelanggan telekomunikasi Iran (Fase 5, keputusan 38).

Jalankan lokal dari root project:
    streamlit run streamlit_app.py --server.address 127.0.0.1

Input pengguna tidak disimpan. Model dilatih ulang dari dataset saat aplikasi pertama dinyalakan.
Semua teks tampilan ada di src/texts.py (Bahasa Indonesia dan Inggris).
"""
import os
import time
from html import escape

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from src import charts, config, summary
from src.predict import SEGMENT_IDS, explain_all, load_bundle, predict
from src.schema import BOUNDS, CustomerInput
from src.texts import DEFAULT_LANGUAGE, FORM_GROUPS, LANGUAGES, TEXTS, fmt_number, fmt_score, fmt_value

# Info pembuat, diisi sebelum deploy. Tautan kosong ditampilkan sebagai penanda
AUTHOR_NAME = "Arthur Pendragon"
AUTHOR_LINKS = {"GitHub": "https://github.com/Kingarthuria"}
# Kolom berkode kecil yang memakai slider, bukan angka bebas
SLIDERS = ("Charge_Amount",)
# Pilihan contoh di sidebar, urut sesuai tampilan
EXAMPLE_IDS = ("high", "low", "median")

st.set_page_config(page_title=TEXTS[DEFAULT_LANGUAGE]["page_title"], layout="wide")

# CSS tata letak (permintaan pengguna): komponen bawaan Streamlit belum punya pengaturan lebar setara.
# 1) Tiga pilihan contoh sama lebar dalam satu baris, jadi bilah tidak patah dan sudut bulat tetap di ujung.
#    Jika sidebar sempit, teks turun ke baris kedua di dalam pilihannya sendiri.
# 2) Tiga tab sama lebar sampai ujung baris.
# Aturan 1 juga dipakai tombol kelompok usia (lima pilihan sama lebar) dan rasio biaya (keputusan 48).
LAYOUT_CSS = """
<style>
:is(.st-key-example, .st-key-input_Age_Group, .st-key-ratio) [role="radiogroup"] { display: flex; flex-wrap: nowrap; width: 100%; }
:is(.st-key-example, .st-key-input_Age_Group, .st-key-ratio) [role="radiogroup"] > button { flex: 1 1 0; min-width: 0;
  height: auto; min-height: 2.5rem; padding: 0.25rem 0.375rem; }
:is(.st-key-example, .st-key-input_Age_Group, .st-key-ratio) [role="radiogroup"] > button p { white-space: normal;
  text-align: center; font-size: 0.8125rem; }
[data-testid="stTabs"] [role="tablist"] > [role="tab"] { flex: 1 1 0; justify-content: center; text-align: center; }
/* 3) Sidebar lebih rapat: jarak bawaan di atas sidebar, di sekitar garis pemisah, dan di atas judul dikurangi */
[data-testid="stSidebarHeader"] { height: 2.75rem; margin-bottom: 0; }
[data-testid="stSidebar"] hr { margin: 0.5rem 0; }
[data-testid="stSidebar"] h3 { padding-top: 0; }
/* 6) Sidebar tidak bisa ditarik terlalu lebar (bawaan Streamlit 600px), supaya halaman utama tetap lega */
/*    Hanya saat terbuka: saat ditutup Streamlit memakai max-width 0, dan aturan ini tidak boleh menimpanya */
[data-testid="stSidebar"][aria-expanded="true"] { max-width: 420px !important; }
/* 5) Kotak rasio biaya di sidebar: garis putus-putus dan latar putih, beda dari grup isian pelanggan */
.st-key-decision_box { border: 1.5px dashed #94A3B8 !important; background: #FFFFFF; }
/* 4) Angka dan teks di kartu metrik tidak terpotong ("Tidak dihub…"): ukuran huruf mengecil di layar sempit,
      dan jika tetap tidak muat, teks turun ke baris berikutnya */
[data-testid="stMetricValue"] { font-size: clamp(1.75rem, 2.2vw, 2.25rem); }
/*    !important diperlukan karena gaya bawaan Streamlit pada teks metrik lebih spesifik. Label kartu juga dibungkus */
:is([data-testid="stMetricValue"], [data-testid="stMetricLabel"]) :is(div, p) {
  white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }
/* 7) Keputusan 48: judul halaman dan judul bagian lebih kecil, supaya skala keputusan menjadi titik fokus */
[data-testid="stMain"] h1 { font-size: 1.75rem !important; }
[data-testid="stMain"] h3 { font-size: 1.375rem !important; }
/* 8) Skala keputusan (src/charts.py, decision_scale). Biru dan merah sama artinya dengan grafik di tab teknis */
.decision-scale { position: relative; margin: 3rem 0 0.5rem; font-variant-numeric: tabular-nums; }
.decision-scale .lanes { position: relative; display: flex; gap: 3px; height: 3rem; }
.decision-scale .lane { display: flex; align-items: center; padding: 0 1rem; font-size: 0.9375rem; color: #586274;
  background: #EEF1F5; min-width: 0; white-space: nowrap; overflow: hidden; }
.decision-scale .lane.stay { border-radius: 6px 0 0 6px; }
.decision-scale .lane.go { border-radius: 0 6px 6px 0; justify-content: flex-end; flex: 1; }
.decision-scale .lane.on { color: #FFFFFF; font-weight: 600; font-size: 1.125rem; }
.decision-scale .lane.stay.on { background: #1F5FA8; }
.decision-scale .lane.go.on { background: #B42F46; }
.decision-scale .marker { position: absolute; top: -12px; bottom: -12px; left: var(--to); width: 4px; margin-left: -2px;
  background: #0F172A; border-radius: 2px; box-shadow: 0 0 0 2px #FFFFFF; }
.decision-scale .tag { position: absolute; top: -2.6rem; left: var(--to); transform: translateX(-50%); white-space: nowrap;
  font-size: 0.875rem; font-weight: 600; color: #0F172A; }
.decision-scale .tag.edge-r { transform: translateX(-100%); }
.decision-scale .tag.edge-l { transform: none; }
.decision-scale .ticks { position: relative; height: 1.2rem; margin-top: 1rem; font-size: 0.75rem; color: #586274; }
.decision-scale .tick { position: absolute; top: 0; transform: translateX(-50%); }
.decision-scale .tick:first-child { transform: none; }
.decision-scale .tick.last { transform: translateX(-100%); }
.decision-scale .thr { position: relative; display: inline-block; margin-top: 0.5rem; transform: translateX(-50%);
  white-space: nowrap; font-size: 0.8125rem; color: #0F172A; }
/*    Satu gerak setiap halaman digambar ulang: penanda bergeser ke skor, lalu jalur jawabannya menyala */
.decision-scale .marker { animation: scale-slide 0.8s cubic-bezier(0.2, 0.7, 0.2, 1) both; }
.decision-scale .tag { animation: scale-fade 0.3s 0.7s both; }
.decision-scale .lane.on { animation: scale-light 0.35s 0.75s both; }
@keyframes scale-slide { from { left: 0; } }
@keyframes scale-fade { from { opacity: 0; } }
@keyframes scale-light { from { background: #EEF1F5; color: #586274; } }
/* 9) Subjudul alasan (keputusan 48 langkah 2): warna sama dengan skala keputusan */
.reason-head { font-weight: 600; font-size: 0.9375rem; }
.reason-head.up { color: #B42F46; }
.reason-head.down { color: #1F5FA8; }
/* 11) Matriks prioritas (src/charts.py, segment_matrix): sel berlebar tetap, tidak meregang saat sidebar ditutup */
.segment-matrix { display: grid; grid-template-columns: auto repeat(2, 9.5rem); gap: 4px; align-items: center;
  justify-content: start; margin: 0.25rem 0 0.75rem; }
.segment-matrix .col { font-size: 0.75rem; color: #586274; text-align: center; padding-bottom: 2px; }
.segment-matrix .row { font-size: 0.75rem; color: #586274; padding-right: 0.75rem; white-space: nowrap; }
.segment-matrix .cell { height: 4rem; border-radius: 4px; background: #EEF1F5; color: #586274; font-size: 0.875rem;
  display: flex; flex-direction: column; align-items: center; justify-content: center; }
.segment-matrix .cell.on { background: #0F172A; color: #FFFFFF; font-weight: 600; }
.segment-matrix .cell.on small { font-weight: 400; font-size: 0.6875rem; }
/* 10) Linimasa rencana (src/charts.py, plan_timeline): titik dan garis menunjukkan urutan waktu */
.plan-timeline { display: grid; grid-auto-columns: 1fr; grid-auto-flow: column; margin: 0.5rem 0 1.25rem; }
/* 12) Susulan teks keputusan 48: blok teks di halaman utama dibatasi sekitar 72 karakter per baris, supaya tetap
      nyaman dibaca saat sidebar ditutup. Skala, matriks, linimasa, tabel, dan grafik tetap selebar halaman */
[data-testid="stMain"] :is([data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"]) { max-width: 72ch; }
/* 13) Alur baca keputusan 48: konten utama dibatasi sekitar 1.080 px supaya teks, skala, matriks, dan linimasa berada
      dalam satu kolom. Judul bagian 18px semibold dengan jarak di atasnya, lebih besar dari label di dalam bagian */
[data-testid="stMainBlockContainer"] { max-width: 1080px; }
[data-testid="stMarkdownContainer"] p.section-q { font-size: 1.125rem !important; font-weight: 600;
  margin: 1.75rem 0 0.25rem !important; }
/*    Wadah judul selebar teksnya, supaya ikon bantuan menempel di samping judul, bukan di ujung batas 72 karakter */
/*    Streamlit memberi margin bawah -16px pada wadah teks, sehingga baris judul + ikon hanya setinggi ikon dan ikon
      tampak naik. Margin itu dinolkan untuk judul bagian */
[data-testid="stMarkdownContainer"]:has(> p.section-q:only-child) { width: fit-content; margin-bottom: 0 !important; }
/*    Jarak atas judul berikon dipindah ke wadahnya, supaya ikon bantuan sejajar dengan baris judul */
[data-testid="stMarkdownContainer"] > p.section-q:only-child { margin: 0 !important; }
[data-testid="stElementContainer"]:has(p.section-q:only-child) { margin-top: 1.5rem; }
/*    Pengingat keterbatasan diberi jarak dari bagian rencana */
.st-key-limit_note { margin-top: 1rem; }
.plan-timeline .step { padding-right: 1.5rem; }
.plan-timeline .mark { display: flex; align-items: center; height: 12px; margin-bottom: 0.625rem; }
.plan-timeline .mark::before { content: ""; width: 12px; height: 12px; border-radius: 50%; background: #0F172A;
  flex: none; }
.plan-timeline .step:not(:last-child) .mark::after { content: ""; flex: 1; height: 2px; background: #0F172A; }
.plan-timeline .when { font-weight: 600; font-size: 0.9375rem; margin: 0 0 0.25rem; }
.plan-timeline .what { font-size: 0.9375rem; line-height: 1.55; margin: 0; }
@media (prefers-reduced-motion: reduce) {
  .decision-scale .marker, .decision-scale .tag, .decision-scale .lane.on { animation: none; } }
</style>
"""
st.html(LAYOUT_CSS)


@st.cache_resource(show_spinner="Melatih model dari dataset... / Training the model...")
def get_bundle():
    start = time.perf_counter()
    bundle = load_bundle()
    # Satu baris di log server (Manage app di Streamlit Cloud) untuk memantau lama muat pertama. Tidak memuat data
    # pengguna
    print(f"[demo] model siap dalam {time.perf_counter() - start:.1f} detik, cpu_count={os.cpu_count()}", flush=True)
    return bundle


@st.cache_data
def get_summary():
    return pd.read_csv(summary.METRICS_PATH).set_index("model"), pd.read_csv(summary.IMPORTANCE_PATH)


bundle = get_bundle()
metrics, importance = get_summary()

# --- Bahasa dan state awal ------------------------------------------------------------------------------
st.session_state.setdefault("lang", DEFAULT_LANGUAGE)
st.session_state.setdefault("customer", bundle.defaults.model_dump())
st.session_state.setdefault("source", "median")
# Contoh yang sedang dipilih. Kosong (None) setelah pengguna menghitung dari isiannya sendiri
st.session_state.setdefault("example", "median")
for feature, value in bundle.defaults.model_dump().items():
    st.session_state.setdefault(f"input_{feature}", value)

# Pilihan bahasa ada di kanan atas halaman utama (keputusan 48 langkah 3) dan digambar setelah sidebar. Nilainya
# dibaca dari session_state, yang sudah berisi pilihan terbaru saat halaman digambar ulang
# Pengaman: pilihan yang sempat kosong kembali ke bahasa bawaan
if st.session_state["lang"] not in LANGUAGES:
    st.session_state["lang"] = DEFAULT_LANGUAGE
lang = st.session_state["lang"]
t = TEXTS[lang]


def value_text(feature: str, value: float) -> str:
    if feature == "Age_Group":
        # Kelompok usia ditulis bersama perkiraan umurnya, misalnya "3 (≈30 th)"
        return t["age_value"].format(group=int(value), age=bundle.age_by_group[int(value)])
    return fmt_value(lang, feature, value)


def apply_values(values: dict, source: str) -> None:
    # Dipanggil sebelum halaman digambar ulang, jadi formulir dan hasil ikut berubah
    for feature, value in values.items():
        st.session_state[f"input_{feature}"] = value
    st.session_state["customer"] = values
    st.session_state["source"] = source


def choose_example() -> None:
    choice = st.session_state["example"]
    if choice is None:
        # Klik ulang pada pilihan aktif mengosongkan pilihan. Pilihan dikembalikan karena hasilnya masih contoh itu
        st.session_state["example"] = st.session_state["source"] if st.session_state["source"] in EXAMPLE_IDS else None
        return
    values = bundle.defaults if choice == "median" else bundle.examples[choice]
    apply_values(values.model_dump(), choice)


def keep_inputs() -> None:
    # Ganti bahasa mengubah label isian, sehingga Streamlit membuat isian itu ulang dan pilihan radio tampil kosong
    # walau nilainya masih tersimpan. Menulis ulang nilainya membuat pilihan tetap terlihat
    for feature in config.FEATURES:
        st.session_state[f"input_{feature}"] = st.session_state[f"input_{feature}"]
    st.session_state["ratio"] = st.session_state.get("ratio")


def submit_form() -> None:
    # Callback tombol formulir: nilai isian sudah tersimpan di session_state saat callback berjalan
    values = {feature: st.session_state[f"input_{feature}"] for feature in config.FEATURES}
    try:
        st.session_state["customer"] = CustomerInput(**values).model_dump()
    except ValidationError as error:
        st.session_state["input_error"] = error.errors()
        return
    st.session_state["source"] = "form"
    # Hasil kini dari isian sendiri, jadi tidak ada contoh yang ditandai
    st.session_state["example"] = None


def hint(feature: str) -> str:
    median, low, high = bundle.hints[feature]
    return t["hint"].format(
        median=value_text(feature, median if feature == "Customer_Value" else round(median)),
        low=value_text(feature, low),
        high=value_text(feature, high),
    )


def feature_input(feature: str):
    low, high = BOUNDS[feature]
    key, label = f"input_{feature}", t["features"][feature]
    # Petunjuk median dan rentang ada di ikon bantuan (help), bukan teks di bawah isian, supaya sidebar tidak padat
    if feature in t["choices"]:
        choices = t["choices"][feature]
        st.radio(label, list(choices), format_func=choices.get, horizontal=True, key=key)
    elif feature == "Age_Group":
        # Lima tombol berisi perkiraan umur (asumsi dari kolom Age), bukan slider 1–5 yang sulit dibaca.
        # required=True supaya klik ulang tidak mengosongkan pilihan
        ages = bundle.age_by_group
        st.segmented_control(
            label, list(ages), format_func=lambda g: t["age_option"].format(age=ages[g]), key=key, required=True,
            help=t["age_help"], width="stretch",
        )
    elif feature in SLIDERS:
        st.slider(label, min_value=int(low), max_value=int(high), step=1, key=key, help=hint(feature))
    elif feature == "Customer_Value":
        st.number_input(label, min_value=float(low), max_value=float(high), step=1.0, format="%.2f", key=key,
                        help=hint(feature))
    else:
        st.number_input(label, min_value=int(low), max_value=int(high), step=1, key=key, help=hint(feature))


# --- Sidebar: contoh dan formulir -----------------------------------------------------------------------
with st.sidebar:
    # Keterangan pindah ke ikon bantuan di judul, supaya sidebar tidak padat
    st.subheader(t["examples"], help=t["examples_note"])
    # Pilihan aktif ditandai warna, berbeda dari tombol biasa yang tidak menunjukkan pilihan. Lebar ketiga pilihan
    # disamakan dalam satu baris lewat CSS (LAYOUT_CSS), supaya bilah tidak patah dan sudutnya tetap rapi
    st.segmented_control(
        t["examples"], EXAMPLE_IDS, format_func=t["example_labels"].get, key="example", on_change=choose_example,
        label_visibility="collapsed", width="stretch",
    )

    st.divider()
    st.subheader(t["form_title"], help=t["form_note"])
    # Tanpa st.form, supaya rasio biaya bisa berada di antara grup isian dan tombol hitung, tetapi tetap langsung
    # berlaku. Isian pelanggan baru dipakai setelah tombol ditekan, karena hasil membaca session_state["customer"]
    for group, features in FORM_GROUPS.items():
        with st.expander(t["group_labels"][group], expanded=group == "status"):
            for feature in features:
                feature_input(feature)

    # Rasio biaya juga input, tetapi bukan fitur dataset. Kotaknya bergaris putus-putus dan selalu terbuka
    # (LAYOUT_CSS), supaya terlihat berbeda dari grup isian pelanggan
    with st.container(border=True, key="decision_box"):
        st.markdown(f":material/tune: **{t['decision_title']}**", help=t["decision_help"])
        ratios = list(bundle.thresholds.index)
        default_ratio = f"1:{config.DEFAULT_RATIO}"
        # Pengaman: rasio yang sempat kosong kembali ke rasio bawaan, supaya keputusan selalu bisa dihitung
        if st.session_state.get("ratio") not in ratios:
            st.session_state["ratio"] = default_ratio
        # Segmented control seperti pilihan contoh (keputusan 48 langkah 3). required=True supaya klik ulang tidak
        # mengosongkan rasio. Lebar ketiga pilihan disamakan lewat CSS
        ratio = st.segmented_control(
            t["ratio_label"], ratios, key="ratio", help=t["ratio_help"], required=True, width="stretch",
            format_func=lambda r: t["ratio_default"].format(ratio=r) if r == default_ratio else r,
        )
        st.caption(t["ratio_explanations"][ratio])

    st.button(t["submit"], type="primary", width="stretch", on_click=submit_form, key="submit")

    st.divider()
    author = AUTHOR_NAME or t["author_placeholder"]
    links = " · ".join(
        f"[{name}]({url})" if url else t["link_placeholder"].format(name=name) for name, url in AUTHOR_LINKS.items()
    )
    st.caption(f"{t['author'].format(name=author)}  \n{links}")

# Kesalahan isian dari tombol formulir, ditampilkan sekali di tab hasil
input_errors = st.session_state.pop("input_error", None)

# --- Bagian atas ----------------------------------------------------------------------------------------
# Judul di kiri, pilihan bahasa di kanan atas (keputusan 48 langkah 3). Label selalu dua bahasa supaya pembaca yang
# tidak mengerti bahasa aktif tetap menemukannya
head, lang_col = st.columns([6, 1], vertical_alignment="top")
with head:
    st.title(t["title"])
    st.caption(t["subtitle"])
with lang_col:
    st.segmented_control(
        TEXTS[DEFAULT_LANGUAGE]["language"], list(LANGUAGES), key="lang", required=True, on_change=keep_inputs,
        format_func=lambda code: code.upper(), label_visibility="collapsed", width="stretch",
    )
# Pengantar dan langkah dilipat (keputusan 48), supaya hasil terlihat tanpa scroll
with st.expander(t["howto_title"]):
    st.markdown(t["intro"])
    st.markdown(t["steps"])

tab_business, tab_technical, tab_model, tab_limits = st.tabs(t["tabs"])

# Dihitung sekali, dipakai tab bisnis dan tab teknis
customer = CustomerInput(**st.session_state["customer"])
result = predict(bundle, customer, ratio)
base, contributions = explain_all(bundle, customer)
segment_id = SEGMENT_IDS[(result.contact, customer.Customer_Value >= bundle.value_cutoff)]
segment = t["segments"][segment_id]
# Sumber data yang sedang ditampilkan, ditulis di bawah judul tab bisnis dan teknis
source_caption = t["business_source"].format(source=t["sources"][st.session_state["source"]])


def typical_value(feature: str) -> float:
    # Nilai yang umum di data latih (median). Untuk kolom pilihan, median sama dengan pilihan terbanyak
    median = bundle.hints[feature][0]
    return median if feature == "Customer_Value" else round(median)


def feature_phrase(feature: str, value: float) -> str:
    # Frasa bahasa awam untuk satu fitur, misalnya "pernah komplain" atau "kegagalan panggilan 12 kali"
    phrase = t["phrases"][feature]
    if isinstance(phrase, dict):
        return phrase[int(value)]
    return phrase.format(value=value_text(feature, value))


def reason_phrase(contribution) -> str:
    # Frasa ditambah pembanding dengan pelanggan pada umumnya, hanya jika nilainya berbeda
    feature, value = contribution.feature, contribution.value
    typical = typical_value(feature)
    text = feature_phrase(feature, value)
    if feature in t["choices"]:
        if int(value) != int(typical):
            typical_text = feature_phrase(feature, typical)
            if t["subject"]:
                typical_text = typical_text.removeprefix(t["subject"])
            text += " " + t["compare_choice"].format(typical=typical_text)
    elif value_text(feature, value) != value_text(feature, typical):
        key = "compare_above" if value > typical else "compare_below"
        text += " " + t[key].format(typical=value_text(feature, typical))
    return text


def personal_hints(factors) -> list[str]:
    # Saran tambahan dari alasan risiko teratas pelanggan ini. Hanya untuk tanda yang memang lebih buruk dari
    # umumnya: pernah komplain, non-aktif, kegagalan panggilan tinggi, atau pemakaian rendah. Tetap hipotesis
    hints = []
    for c in factors:
        typical = typical_value(c.feature)
        if c.feature == "Complains" and c.value == 1:
            key = "Complains"
        elif c.feature == "Status" and c.value == 2:
            key = "Status"
        elif c.feature == "Call_Failure" and c.value > typical:
            key = "Call_Failure"
        elif c.feature in ("Seconds_of_Use", "Frequency_of_use") and c.value < typical:
            key = "low_usage"
        else:
            continue
        if t["hints"][key] not in hints:
            hints.append(t["hints"][key])
    return hints


def section_title(text: str) -> str:
    # Judul bagian di tab hasil (keputusan 48, alur): satu tingkat ukuran di atas teks isi, tanpa tautan jangkar
    return f'<p class="section-q">{escape(text)}</p>'


def reason_item(contribution) -> str:
    # Satu butir alasan: kalimat utuh dengan huruf besar di awal dan titik di akhir
    text = t["item_prefix"] + reason_phrase(contribution)
    return text[0].upper() + text[1:] + "."


# --- Tab 1: Hasil & rekomendasi (pembaca bisnis): What, So What, Now What --------------------------------
with tab_business:
    if input_errors:
        st.error(t["invalid"] + "\n\n" + "\n".join(f"- {e['loc'][0]}: {e['msg']}" for e in input_errors))
    st.subheader(t["business_title"])
    st.caption(source_caption)

    # Alur tanpa judul bernomor: keputusan, lalu artinya, lalu rekomendasi.
    # The What (keputusan 48): skala keputusan menggantikan 3 kartu metrik. Keputusan, skor risiko, dan skor minimal
    # untuk dihubungi tetap tampil, tetapi jawabannya dibaca dari posisi pelanggan di skala
    st.html(charts.decision_scale(
        result.score, result.threshold, result.contact, t, ratio,
        fmt_score(lang, result.score), fmt_number(lang, result.threshold, 3),
        lambda value, digits: fmt_number(lang, value, digits),
    ))
    st.caption(t["scale_caption"])

    # The So What: cerita singkat dalam bahasa bisnis. Arah utama mengikuti keputusan: alasan yang menaikkan risiko
    # untuk pelanggan yang dihubungi, dan alasan yang menahan risiko untuk yang tidak
    raising = [c for c in contributions if c.shap > 0]
    lowering = [c for c in contributions if c.shap < 0]
    main, other = (raising, lowering) if result.contact else (lowering, raising)
    mode = "contact" if result.contact else "no_contact"
    # Keputusan 48 langkah 2: satu kalimat pembuka, lalu alasan dikelompokkan dengan subjudul berwarna sesuai arah
    # (merah menaikkan, biru menahan), sama dengan skala dan grafik di tab teknis
    groups = (("raise", main[:3]), ("lower_slight", other[:2])) if result.contact else (
        ("lower", main[:3]), ("raise_slight", other[:2]))
    reasons = [section_title(t["reasons_title"]), t[f"insight_{mode}"]]
    for group, factors in groups:
        if factors:
            direction = "up" if group.startswith("raise") else "down"
            items = "\n".join(f"- {reason_item(c)}" for c in factors)
            reasons.append(f'<span class="reason-head {direction}">{t["groups"][group]}</span>\n\n{items}')

    # Satu jalur baca dari atas ke bawah (keputusan 48, alur): keputusan, kenapa, seberapa diprioritaskan, lalu apa yang
    # dilakukan. Judul bagian berupa pertanyaan dengan satu tingkat ukuran, di atas label di dalam bagian
    st.markdown("\n\n".join(reasons), unsafe_allow_html=True)
    st.caption(t["reasons_caption"])

    # Matriks berlebar sel tetap di kiri dan kalimat jembatan di sampingnya, jadi tidak meregang saat sidebar ditutup
    value, cutoff = customer.Customer_Value, bundle.value_cutoff
    position = "above" if value > cutoff else "equal" if value == cutoff else "below"
    risk_level = "high" if result.contact else "low"
    value_level = "high" if value >= cutoff else "low"
    st.markdown(section_title(t["matrix_title"]), help=t["segment_help"], unsafe_allow_html=True)
    left, right = st.columns([0.45, 0.55], gap="large", vertical_alignment="center")
    with left:
        st.html(charts.segment_matrix(segment_id, t))
    with right:
        st.markdown(t["segment_bridge"].format(
            value=value_text("Customer_Value", value), position=t[f"position_{position}"],
            cutoff=fmt_number(lang, cutoff, 2), risk=t["level"][risk_level], level=t["level"][value_level],
            segment=segment["name"],
        ))
        st.caption(t["segment_note"])

    # Rencana langsung mengikuti matriks, karena langkahnya bergantung pada segmen. Status hipotesis dan konteks waktu
    # di satu baris keterangan, catatan asumsi di ikon bantuan judul
    st.markdown(section_title(t["now_title"]), help=t["now_caption"], unsafe_allow_html=True)
    st.markdown(segment["summary"])
    st.caption(t["now_intro"])
    st.html(charts.plan_timeline(segment["steps"]))
    lines = []
    personal = personal_hints(main[:3]) if result.contact else []
    if personal:
        lines.append(f"**{t['personal_title']}:** " + " ".join(personal))
    lines.append(f"**{t['now_caution']}:** {segment['caution']}")
    st.markdown("\n\n".join(lines))

    # Pengingat satu baris, diberi jarak karena berlaku untuk seluruh hasil, bukan bagian rencana. Kalimat keterbatasan
    # lengkap (keputusan 2) ada di tab Keterbatasan & data
    with st.container(key="limit_note"):
        st.caption(f":material/info: {t['limitation_box']}")

# --- Tab 2: Detail teknis (pembaca teknis): bagaimana model sampai ke skor pelanggan ini --------------------
with tab_technical:
    # Satu judul tab seperti tab bisnis. Bagian di bawahnya memakai judul lebih kecil supaya tidak bersaing
    st.subheader(t["tech_customer_title"])
    st.caption(source_caption)

    st.markdown(f"**{t['position_title']}**")
    explain_key = "position_explain_contact" if result.contact else "position_explain_no_contact"
    st.markdown(t[explain_key].format(score=fmt_score(lang, result.score),
                                      threshold=fmt_number(lang, result.threshold, 3)))
    st.altair_chart(charts.score_position(result.score, result.threshold, result.contact, t, ratio), width="stretch")
    st.caption(t["position_caption"])

    st.markdown(f"**{t['why_title']}**")
    st.altair_chart(charts.waterfall(base, contributions, t, value_text), width="stretch")
    st.caption(t["why_caption"])
    with st.expander(t["technical"]):
        total = sum(c.shap for c in contributions)
        st.markdown(t["technical_text"].format(
            base=fmt_number(lang, base, 3), total=fmt_number(lang, total, 3),
            margin=fmt_number(lang, base + total, 3), score=fmt_score(lang, result.score),
        ))
        st.dataframe(
            pd.DataFrame([
                {
                    t["table_feature"]: f"{t['features_short'][c.feature]} ({c.feature})",
                    t["table_value"]: value_text(c.feature, c.value),
                    t["table_shap"]: round(c.shap, 3),
                }
                for c in contributions
            ]),
            hide_index=True, width="stretch",
        )

# --- Tab 3: Cara kerja model (pembaca teknis): berlaku untuk semua pelanggan, dipisah dari tab 2 -----------
with tab_model:
    st.subheader(t["flow_title"])
    st.graphviz_chart(charts.flow_dot(bundle.counts, t, lambda v: fmt_number(lang, v)), width="stretch")
    st.caption(t["flow_caption"])

    st.subheader(t["metrics_title"])
    xgb_row, dummy_row = metrics.loc["xgboost_12_fitur"], metrics.loc["dummy"]
    m1, m2, m3 = st.columns(3, border=True)
    m1.metric(t["metric_pr"], fmt_number(lang, xgb_row["pr_auc_mean"], 3))
    m1.caption(t["metric_range"].format(low=fmt_number(lang, xgb_row["pr_auc_min"], 3),
                                        high=fmt_number(lang, xgb_row["pr_auc_max"], 3)))
    m2.metric(t["metric_pr_base"], fmt_number(lang, dummy_row["pr_auc_mean"], 3))
    m2.caption(t["metric_base_note"])
    m3.metric(t["metric_roc"], fmt_number(lang, xgb_row["roc_auc_mean"], 3))
    m3.caption(t["metric_range"].format(low=fmt_number(lang, xgb_row["roc_auc_min"], 3),
                                        high=fmt_number(lang, xgb_row["roc_auc_max"], 3)))
    st.markdown(t["metrics_text"])

    st.subheader(t["importance_title"])
    st.altair_chart(charts.importance(importance, t), width="stretch")
    st.caption(t["importance_text"])

    st.subheader(t["ratio_title"])
    st.markdown(t["ratio_text"])
    columns = t["ratio_table"]
    # st.table (bukan st.dataframe) supaya kalimat panjang di kolom Arti turun ke baris berikutnya, tidak terpotong.
    # Kolom rasio dijadikan indeks karena st.table selalu menampilkan indeks
    st.table(
        pd.DataFrame([
            {
                columns["ratio"]: ratio_name + (" (default)" if row["is_default"] else ""),
                columns["threshold"]: fmt_number(lang, row["threshold"], 3),
                columns["range"]: f"{fmt_number(lang, row['threshold_min'], 2)}–{fmt_number(lang, row['threshold_max'], 2)}",
                columns["meaning"]: t["ratio_explanations"][ratio_name],
            }
            for ratio_name, row in bundle.thresholds.iterrows()
        ]).set_index(columns["ratio"])
    )

# --- Tab 4: Keterbatasan & data -------------------------------------------------------------------------
with tab_limits:
    st.subheader(t["lim_pattern_title"])
    with st.container(border=True):
        st.markdown(f"**{t['limitation']}**")
    st.markdown(t["lim_pattern_text"])
    for section in ("uci", "assumption", "source"):
        st.subheader(t[f"lim_{section}_title"])
        # {ages} diisi dari data (pasangan kelompok usia dan kolom Age), bukan diketik tangan
        ages = ", ".join(f"{group} = {age}" for group, age in bundle.age_by_group.items())
        st.markdown("\n".join(f"- {item.format(ages=ages)}" for item in t[f"lim_{section}_items"]))
