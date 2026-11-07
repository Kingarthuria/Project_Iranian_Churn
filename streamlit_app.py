"""Demo prediksi churn pelanggan telekomunikasi Iran (Fase 5, keputusan 38).

Jalankan lokal dari root project:
    streamlit run streamlit_app.py --server.address 127.0.0.1

Input pengguna tidak disimpan. Model dilatih ulang dari dataset saat aplikasi pertama dinyalakan.
Semua teks tampilan ada di src/texts.py (Bahasa Indonesia dan Inggris).
"""
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
# Aturan 1 juga dipakai tombol kelompok usia (lima pilihan sama lebar).
LAYOUT_CSS = """
<style>
:is(.st-key-example, .st-key-input_Age_Group) [role="radiogroup"] { display: flex; flex-wrap: nowrap; width: 100%; }
:is(.st-key-example, .st-key-input_Age_Group) [role="radiogroup"] > button { flex: 1 1 0; min-width: 0;
  height: auto; min-height: 2.5rem; padding: 0.25rem 0.375rem; }
:is(.st-key-example, .st-key-input_Age_Group) [role="radiogroup"] > button p { white-space: normal;
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
</style>
"""
st.html(LAYOUT_CSS)


@st.cache_resource(show_spinner="Melatih model dari dataset... / Training the model...")
def get_bundle():
    return load_bundle()


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

with st.sidebar:
    # Judul bahasa memakai gaya yang sama dengan judul bagian sidebar lain, jadi label pilihan disembunyikan
    st.subheader(TEXTS[DEFAULT_LANGUAGE]["language"])
    lang = st.radio(
        TEXTS[DEFAULT_LANGUAGE]["language"], list(LANGUAGES), format_func=LANGUAGES.get, horizontal=True,
        key="lang", label_visibility="collapsed",
    )
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
    # Garis pemisah supaya bahasa, contoh, dan formulir terbaca sebagai bagian yang berbeda
    st.divider()
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
        st.session_state.setdefault("ratio", default_ratio)
        ratio = st.radio(
            t["ratio_label"], ratios, horizontal=True, key="ratio", help=t["ratio_help"],
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
st.title(t["title"])
st.caption(t["subtitle"])
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


def join_items(items: list[str]) -> str:
    # "a dan b" untuk dua butir, "a, b, dan c" untuk tiga butir atau lebih
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {t['and']} {items[1]}"
    return ", ".join(items[:-1]) + f", {t['and']} " + items[-1]


# --- Tab 1: Hasil & rekomendasi (pembaca bisnis): What, So What, Now What --------------------------------
with tab_business:
    if input_errors:
        st.error(t["invalid"] + "\n\n" + "\n".join(f"- {e['loc'][0]}: {e['msg']}" for e in input_errors))
    st.subheader(t["business_title"])
    st.caption(source_caption)

    # Alur tanpa judul bernomor (permintaan pengguna): angka utama, lalu artinya, lalu rekomendasi.
    # The What: hanya angka keputusan. Segmen tidak dibuat kartu karena sudah dijelaskan di bawah bersama matriksnya,
    # dan kalimat di bawah tidak mengulang angka
    c1, c2, c3 = st.columns(3, border=True)
    c1.metric(t["metric_decision"], t["contact"] if result.contact else t["no_contact"])
    c2.metric(t["metric_score"], fmt_score(lang, result.score), help=t["metric_score_help"])
    c3.metric(t["metric_threshold"].format(ratio=ratio), fmt_number(lang, result.threshold, 3),
              help=t["metric_threshold_help"])

    # The So What: cerita singkat dalam bahasa bisnis. Arah utama mengikuti keputusan: alasan yang menaikkan risiko
    # untuk pelanggan yang dihubungi, dan alasan yang menahan risiko untuk yang tidak
    raising = [c for c in contributions if c.shap > 0]
    lowering = [c for c in contributions if c.shap < 0]
    main, other = (raising, lowering) if result.contact else (lowering, raising)
    mode = "contact" if result.contact else "no_contact"
    insight = t[f"insight_{mode}"]
    if main:
        insight += " " + t[f"insight_main_{mode}"].format(items=join_items([reason_phrase(c) for c in main[:3]]))
    if other:
        insight += " " + t[f"insight_other_{mode}"].format(items=join_items([reason_phrase(c) for c in other[:2]]))
    st.markdown(insight)
    st.caption(t["reasons_caption"])

    # Jembatan ke segmen: risiko di atas digabung dengan nilai pelanggan, lalu matriks menunjukkan posisinya
    value, cutoff = customer.Customer_Value, bundle.value_cutoff
    position = "above" if value > cutoff else "equal" if value == cutoff else "below"
    left, right = st.columns([1, 1], vertical_alignment="center")
    with left:
        st.altair_chart(charts.segment_matrix(segment_id, t), width="stretch")
    with right:
        st.markdown(t["segment_bridge"].format(
            risk=t[f"risk_{mode}"], value=value_text("Customer_Value", value), position=t[f"position_{position}"],
            cutoff=fmt_number(lang, cutoff, 2), segment=segment["name"],
            desc=segment["desc"][0].lower() + segment["desc"][1:],
        ), help=t["segment_help"])
        st.caption(t["segment_note"].format(cutoff=fmt_number(lang, cutoff, 2)))

    # The Now What: rekomendasi rinci untuk siklus 12 bulan berikutnya, dengan langkah bertahap per segmen
    lines = [f"**{t['now_title']}**", t["now_intro"], segment["summary"]]
    lines.append("\n".join(f"{i}. {step}" for i, step in enumerate(segment["steps"], start=1)))
    personal = personal_hints(main[:3]) if result.contact else []
    if personal:
        lines.append(f"**{t['personal_title']}:** " + " ".join(personal))
    lines.append(f"**{t['now_caution']}:** {segment['caution']}")
    st.markdown("\n\n".join(lines))
    st.caption(t["now_caption"])

    # Pengingat satu baris. Kalimat keterbatasan lengkap (keputusan 2) ada di tab Keterbatasan & data
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
