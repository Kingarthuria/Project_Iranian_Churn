"""Demo prediksi churn pelanggan telekomunikasi Iran (Fase 5, keputusan 38).

Jalankan lokal dari root project:
    streamlit run streamlit_app.py --server.address 127.0.0.1

Input pengguna tidak disimpan. Model dilatih ulang dari dataset saat aplikasi pertama dinyalakan.
"""
import pandas as pd
import streamlit as st
from pydantic import ValidationError

from src import config
from src.predict import load_bundle, predict
from src.schema import BOUNDS, LABELS, CustomerInput

LIMITATION = (
    "Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. "
    "Audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin "
    "dan skor model bisa terlalu optimistis."
)
# Kolom dengan pilihan kode, ditampilkan sebagai daftar pilihan
CHOICES = {
    "Complains": {0: "0: tidak", 1: "1: ya"},
    "Status": {1: "1: aktif", 2: "2: non-aktif"},
    "Tariff_Plan": {1: "1: pay as you go", 2: "2: kontrak"},
    "Age_Group": {k: str(k) for k in range(1, 6)},
    "Charge_Amount": {k: str(k) for k in range(11)},
}

st.set_page_config(page_title="Demo Prediksi Churn", layout="wide")


@st.cache_resource(show_spinner="Melatih model dari dataset...")
def get_bundle():
    return load_bundle()


bundle = get_bundle()

st.title("Demo Prediksi Churn Pelanggan Telekomunikasi")
st.caption(
    "Model: XGBoost dengan 12 fitur, dilatih pada data latih Iranian Churn Dataset "
    "(UCI, CC BY 4.0). Proyek portofolio, bukan sistem produksi."
)
st.warning(
    f"**Keterbatasan.** {LIMITATION}\n\n"
    "- **Skor risiko bukan peluang** yang terkalibrasi. Skor dipakai untuk mengurutkan dan membandingkan dengan threshold.\n"
    "- **Nilai terhitung (`Customer_Value`) bukan uang.** UCI tidak menjelaskan rumus dan satuannya.\n"
    "- **Hasil bersifat asosiatif.** Demo tidak membuktikan bahwa menghubungi pelanggan akan mencegah churn.\n"
    "- **Input tidak disimpan.**"
)

# Pilihan rasio biaya (keputusan 32)
st.subheader("1. Pilih rasio biaya")
ratios = list(bundle.thresholds.index)
default_ratio = f"1:{config.DEFAULT_RATIO}"
ratio = st.radio(
    "Seberapa merugikan churn terlewat dibanding salah hubungi?",
    ratios,
    index=ratios.index(default_ratio),
    horizontal=True,
    help="Rasio adalah asumsi biaya, bukan data. Default 1:5 adalah titik awal, bukan rasio yang terbukti benar.",
)
st.info(
    f"**{ratio}** (threshold {bundle.thresholds.loc[ratio, 'threshold']}): {bundle.thresholds.loc[ratio, 'penjelasan']}\n\n"
    "Cara menghitung rasio sendiri: kerugian per churn terlewat dibagi biaya per salah hubungi."
)

# Contoh pelanggan dari data latih
st.subheader("2. Isi data pelanggan")
st.write("Semua nilai adalah agregat 9 bulan pertama, sesuai dokumentasi UCI.")


def apply_values(values: dict) -> None:
    # Dipanggil tombol sebelum halaman digambar ulang, jadi nilai formulir ikut berubah
    for feature, value in values.items():
        st.session_state[f"input_{feature}"] = value


for feature, value in bundle.defaults.model_dump().items():
    st.session_state.setdefault(f"input_{feature}", value)

example_cols = st.columns(len(bundle.examples) + 1)
for col, (name, example) in zip(example_cols, bundle.examples.items()):
    col.button(name, on_click=apply_values, args=(example.model_dump(),))
example_cols[-1].button("Kembalikan ke nilai median", on_click=apply_values, args=(bundle.defaults.model_dump(),))


def feature_input(container, feature: str):
    low, high = BOUNDS[feature]
    key = f"input_{feature}"
    if feature in CHOICES:
        return container.selectbox(
            LABELS[feature], list(CHOICES[feature]), format_func=lambda v, f=feature: CHOICES[f][v], key=key
        )
    if feature == "Customer_Value":
        return container.number_input(LABELS[feature], min_value=float(low), max_value=float(high), step=1.0, key=key)
    return container.number_input(LABELS[feature], min_value=int(low), max_value=int(high), step=1, key=key)


with st.form("pelanggan"):
    form_cols = st.columns(3)
    values = {feature: feature_input(form_cols[i % 3], feature) for i, feature in enumerate(config.FEATURES)}
    submitted = st.form_submit_button("Hitung skor risiko", type="primary")

if submitted:
    try:
        customer = CustomerInput(**values)
    except ValidationError as error:
        st.error("Input tidak valid:\n\n" + "\n".join(f"- {e['loc'][0]}: {e['msg']}" for e in error.errors()))
        st.stop()

    result = predict(bundle, customer, ratio)
    st.subheader("3. Hasil")
    c1, c2, c3 = st.columns(3)
    c1.metric("Skor risiko", f"{result.score:.3f}")
    c2.metric(f"Threshold {result.ratio}", f"{result.threshold}")
    c3.metric("Tindakan", "Hubungi" if result.contact else "Tidak dihubungi")
    st.write(f"**Segmen risiko × nilai:** {result.segment}")
    st.caption(
        f"Nilai tinggi berarti nilai terhitung minimal {bundle.value_cutoff:,.2f} (median data latih). "
        "Di demo, risiko memakai skor satu model final, sedangkan analisis di notebook memakai "
        "suara mayoritas dari 10 ulangan out-of-fold, jadi hasil pelanggan di dekat threshold bisa berbeda."
    )

    st.write("**Fitur yang paling mendorong skor pelanggan ini** (SHAP bawaan XGBoost, satuan log-odds):")
    table = pd.DataFrame([
        {
            "Fitur": c.feature,
            "Nilai": c.value,
            "Sumbangan SHAP": round(c.shap, 3),
            "Arah": "menaikkan skor" if c.shap > 0 else "menurunkan skor",
        }
        for c in result.top_contributions
    ])
    st.dataframe(table, hide_index=True, width="stretch")
    st.bar_chart(table.set_index("Fitur")["Sumbangan SHAP"], horizontal=True, color="#2a78d6")
    st.caption(
        "Positif berarti fitur itu menaikkan skor risiko, dan negatif menurunkannya. "
        "Penjelasan ini menggambarkan cara model bekerja, bukan sebab pelanggan churn."
    )
