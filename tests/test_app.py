"""Uji asap aplikasi demo dengan alat uji bawaan Streamlit."""
import pytest
from streamlit.testing.v1 import AppTest

from src import config


@pytest.fixture(scope="module")
def app(clean_df):
    at = AppTest.from_file(str(config.ROOT / "streamlit_app.py"), default_timeout=120)
    return at.run()


def test_app_runs_without_error(app):
    assert not app.exception
    assert app.title[0].value.startswith("Demo Prediksi Churn")


def test_limitation_always_visible(app):
    text = " ".join(w.value for w in app.warning)
    assert "pola berulang per 50 baris" in text
    assert "bukan peluang" in text
    assert "bukan uang" in text


def test_default_ratio_is_1_5(app):
    assert app.radio[0].value == f"1:{config.DEFAULT_RATIO}"


def test_submit_shows_result(app):
    app.button[0].click().run()  # Contoh pelanggan berisiko
    app.button[-1].click().run()  # Tombol kirim formulir
    assert not app.exception
    labels = [m.label for m in app.metric]
    assert "Skor risiko" in labels
    assert any(m.value == "Hubungi" for m in app.metric)
