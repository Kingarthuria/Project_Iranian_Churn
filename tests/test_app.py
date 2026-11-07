"""Uji asap aplikasi demo dengan alat uji bawaan Streamlit (tanpa server dan tanpa port)."""
import pytest
from streamlit.testing.v1 import AppTest

from src import config
from src.texts import LIMITATION_EN, LIMITATION_ID, TEXTS


@pytest.fixture
def app(clean_df):
    at = AppTest.from_file(str(config.ROOT / "streamlit_app.py"), default_timeout=180)
    return at.run()


def submit_button(app):
    return next(b for b in app.button if b.label in (TEXTS["id"]["submit"], TEXTS["en"]["submit"]))


def all_markdown(app):
    return " ".join(m.value for m in app.markdown)


def text_of(block):
    return " ".join(m.value for m in block.markdown)


def test_app_runs_in_indonesian_by_default(app):
    assert not app.exception
    assert app.title[0].value == TEXTS["id"]["title"]
    assert len(app.tabs) == 4


def test_limitation_always_visible(app):
    assert LIMITATION_ID in all_markdown(app)


def test_result_shown_on_first_load(app):
    labels = [m.label for m in app.metric]
    assert TEXTS["id"]["metric_score"] in labels
    assert app.radio(key="ratio").value == f"1:{config.DEFAULT_RATIO}"


def test_high_risk_example_is_contacted(app):
    app.segmented_control(key="example").set_value("high").run()
    assert not app.exception
    assert app.segmented_control(key="example").value == "high"
    assert app.session_state["source"] == "high"
    assert any(m.value == TEXTS["id"]["contact"] for m in app.metric)


def test_median_example_marked_on_first_load(app):
    assert app.segmented_control(key="example").value == "median"


def test_reclicking_active_example_keeps_it_marked(app):
    # Klik ulang pada pilihan aktif mengirim None. Pilihan harus tetap ditandai karena hasilnya masih contoh itu
    app.segmented_control(key="example").set_value(None).run()
    assert not app.exception
    assert app.segmented_control(key="example").value == "median"


def test_own_input_clears_example_mark(app):
    app.segmented_control(key="example").set_value("low").run()
    app.number_input(key="input_Call_Failure").set_value(20)
    submit_button(app).click().run()
    assert not app.exception
    assert app.segmented_control(key="example").value is None
    assert app.session_state["source"] == "form"
    assert app.session_state["customer"]["Call_Failure"] == 20


def test_plain_explanation_follows_decision(app):
    # Awal: nilai median, tidak dihubungi. Contoh risiko tinggi: dihubungi
    assert "Pelanggan ini belum perlu dihubungi." in all_markdown(app)
    app.segmented_control(key="example").set_value("high").run()
    assert "Pelanggan ini disarankan dihubungi." in all_markdown(app)


def test_ratio_table_is_static_table(app):
    # st.table membungkus kalimat panjang, sedangkan st.dataframe memotongnya
    assert len(app.table) == 1


def test_hints_moved_to_help(app):
    # Petunjuk median dan rentang tidak lagi tampil sebagai teks di bawah isian
    assert app.number_input(key="input_Call_Failure").help
    assert not any(TEXTS["id"]["examples_note"] in c.value for c in app.caption)


def test_switch_to_english_keeps_submitted_input(app):
    app.number_input(key="input_Call_Failure").set_value(20)
    submit_button(app).click().run()
    app.radio(key="lang").set_value("en").run()
    assert not app.exception
    assert app.title[0].value == TEXTS["en"]["title"]
    assert LIMITATION_EN in all_markdown(app)
    assert app.session_state["customer"]["Call_Failure"] == 20
    assert app.number_input(key="input_Call_Failure").value == 20


def test_age_group_uses_estimated_age_buttons(app):
    # Slider 1–5 diganti lima tombol perkiraan umur. Nilai yang dikirim ke model tetap kelompok 1–5
    age = app.segmented_control(key="input_Age_Group")
    assert age.options == [TEXTS["id"]["age_option"].format(age=a) for a in sorted_ages(app)]
    assert age.value == app.session_state["customer"]["Age_Group"]
    assert all(s.key != "input_Age_Group" for s in app.slider)


def sorted_ages(app):
    # Urutan umur sama dengan urutan kelompok, diambil dari data lewat sesi aplikasi
    from src.data import load_clean
    pairs = load_clean().groupby("Age_Group")["Age_Binning"].first()
    return [int(a) for a in pairs.sort_index()]


def test_short_limitation_reminder_and_segment_help(app):
    # Di bawah hasil cukup pengingat satu baris, kalimat lengkap tetap di tab Keterbatasan & data
    assert any(TEXTS["id"]["limitation_box"] in c.value for c in app.caption)
    assert LIMITATION_ID in all_markdown(app)
    # Detail teknis segmen ada di ikon bantuan kalimat segmen
    assert any(m.help == TEXTS["id"]["segment_help"] for m in app.markdown)


def test_segment_matrix_puts_high_value_on_the_left():
    # Urutan baca matriks: Prioritas I kiri atas, II kiri bawah, III kanan atas, IV kanan bawah
    from src import charts
    t = TEXTS["id"]
    spec = charts.segment_matrix("II", t).to_dict()
    encoding = spec["layer"][0]["encoding"]
    assert encoding["x"]["sort"] == [t["segment_high"], t["segment_low"]]
    assert encoding["y"]["sort"] == [t["segment_high"], t["segment_low"]]


def test_ratio_lives_in_sidebar_and_changes_decision(app):
    # Rasio biaya ada di sidebar, di kotak Pengaturan keputusan antara grup isian dan tombol hitung, bukan di tab
    # hasil, dan langsung mengubah keputusan tanpa menekan tombol
    assert app.sidebar.radio(key="ratio").value == f"1:{config.DEFAULT_RATIO}"
    assert any(TEXTS["id"]["decision_title"] in m.value for m in app.sidebar.markdown)
    app.segmented_control(key="example").set_value("high").run()
    app.sidebar.radio(key="ratio").set_value("1:2").run()
    assert not app.exception
    labels = [m.label for m in app.metric]
    assert TEXTS["id"]["metric_threshold"].format(ratio="1:2") in labels


def test_business_tab_follows_what_so_what_now_what(app):
    # Tab pertama untuk pembaca bisnis: satu judul, lalu alur angka, arti, dan rekomendasi tanpa judul per bagian
    t = TEXTS["id"]
    business = app.tabs[0]
    assert [h.value for h in business.subheader] == [t["business_title"]]
    # Kartu hanya angka keputusan. Segmen dijelaskan di kalimat bersama matriksnya, jadi tidak dibuat kartu
    assert [m.label for m in business.metric] == [
        t["metric_decision"], t["metric_score"], t["metric_threshold"].format(ratio=f"1:{config.DEFAULT_RATIO}"),
    ]
    assert t["insight_no_contact"] in text_of(business)
    assert "Prioritas II" in text_of(business)
    text = " ".join(m.value for m in business.markdown)
    segment = t["segments"]["II"]  # nilai median: tidak dihubungi, nilai terhitung = nilai tengah
    assert segment["summary"] in text and segment["caution"] in text
    assert all(step in text for step in segment["steps"])
    assert t["now_intro"] in text
    # Pelanggan yang tidak dihubungi tidak mendapat saran yang disesuaikan
    assert t["personal_title"] not in text


def test_technical_tab_holds_score_explanation(app):
    # Tab Detail teknis: satu judul, lalu posisi skor dan waterfall sebagai bagian kecil. Cara kerja model
    # ada di tab ketiga sendiri
    t = TEXTS["id"]
    technical, model = app.tabs[1], app.tabs[2]
    assert [h.value for h in technical.subheader] == [t["tech_customer_title"]]
    assert len(technical.header) == 0
    assert f"**{t['why_title']}**" in [m.value for m in technical.markdown]
    assert t["flow_title"] in [h.value for h in model.subheader]
    assert t["flow_title"] not in [h.value for h in technical.subheader]


def test_insight_compares_with_typical_customer(app):
    # Insight bisnis memakai bahasa awam dan pembanding dengan pelanggan pada umumnya, tanpa mengulang angka skor
    app.segmented_control(key="example").set_value("high").run()
    insight = text_of(app.tabs[0])
    assert TEXTS["id"]["insight_contact"] in insight
    assert "ia pernah komplain (kebanyakan pelanggan tidak pernah komplain)" in insight
    assert "kegagalan panggilannya 12 kali (di atas umumnya, 6)" in insight


def test_contacted_customer_gets_tailored_hints(app):
    # Contoh risiko tinggi pernah komplain dan kegagalan panggilannya di atas umumnya, jadi mendapat dua saran khusus
    t = TEXTS["id"]
    app.segmented_control(key="example").set_value("high").run()
    text = text_of(app.tabs[0])
    assert t["personal_title"] in text
    assert t["hints"]["Complains"] in text and t["hints"]["Call_Failure"] in text
    assert t["hints"]["Status"] not in text
