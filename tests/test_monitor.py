"""Monitoring Fase 6: PSI, batch simulasi, log prediksi, dan laporan drift dengan satu perintah."""
import numpy as np
import pandas as pd
import pytest

from src import config
from src.monitor import feature_drift, psi, psi_status, run
from src.predict import load_bundle
from src.score_batch import LOG_COLUMNS, score_batch
from src.simulate import BATCH_SIZE, SCENARIOS, make_batch, make_batches


@pytest.fixture(scope="module")
def train(split):
    return split[0]


@pytest.fixture(scope="module")
def batches(train):
    return make_batches(train)


def test_psi_zero_for_identical_and_high_for_shifted():
    rng = np.random.default_rng(0)
    values = pd.Series(rng.normal(size=2000))
    assert psi(values, values) == pytest.approx(0.0, abs=1e-12)
    assert psi(values, values + 1.0) >= config.PSI_ALERT
    codes = pd.Series([0] * 900 + [1] * 100)
    assert psi(codes, codes, categorical=True) == pytest.approx(0.0, abs=1e-12)
    assert psi(codes, pd.Series([0] * 600 + [1] * 400), categorical=True) >= config.PSI_ALERT


def test_psi_status_thresholds():
    assert psi_status(0.05) == "stabil"
    assert psi_status(config.PSI_WARN) == "perlu_dicek"
    assert psi_status(config.PSI_ALERT) == "bergeser"


def test_batches_are_reproducible_and_valid(train, batches):
    assert tuple(batches) == SCENARIOS
    for batch in batches.values():
        assert list(batch.columns) == config.FEATURES and len(batch) == BATCH_SIZE
        assert config.TARGET not in batch.columns  # label belum diketahui saat batch dinilai
    pd.testing.assert_frame_equal(make_batch(train, "normal", config.SEED + 1), batches["normal"])


def test_normal_batch_is_stable_and_scenarios_are_caught(train, batches):
    reference = train[config.FEATURES]
    drifted = {name: set(feature_drift(reference, batch).query("status == 'bergeser'")["fitur"])
               for name, batch in batches.items()}
    assert drifted["normal"] == set()
    assert "Complains" in drifted["komplain_naik"]
    assert "Status" in drifted["nonaktif_naik"]
    assert {"Seconds_of_Use", "Frequency_of_use"} <= drifted["pemakaian_turun"]


def test_score_batch_appends_log(tmp_path, batches):
    bundle = load_bundle()
    log_path = tmp_path / "log.csv"
    first = score_batch(bundle, batches["normal"], "normal", log_path)
    score_batch(bundle, batches["komplain_naik"], "komplain_naik", log_path)
    log = pd.read_csv(log_path)
    assert list(log.columns) == LOG_COLUMNS + config.FEATURES
    assert len(log) == 2 * BATCH_SIZE and set(log["batch"]) == {"normal", "komplain_naik"}
    # Skor di log sama dengan model demo, dan keputusan mengikuti skor minimal rasio 1:5
    expected = bundle.pipeline.predict_proba(batches["normal"])[:, 1]
    np.testing.assert_allclose(first["skor"], expected, atol=1e-6)
    assert (first["hubungi"] == (first["skor"] >= first["skor_minimal"])).all()


def test_one_command_writes_report(tmp_path):
    result = run(tmp_path)
    summary = result["summary"].set_index("batch")["status"]
    assert summary["normal"] == "stabil"
    assert (summary.drop("normal") == "bergeser").all()
    report = (tmp_path / "laporan_drift.md").read_text(encoding="utf-8")
    assert "simulasi" in report and "independensi antarbaris tidak terjamin" in report
    detail = pd.read_csv(tmp_path / "drift_per_fitur.csv")
    assert len(detail) == len(SCENARIOS) * len(config.FEATURES)
    assert len(pd.read_csv(tmp_path / "prediction_log.csv")) == len(SCENARIOS) * BATCH_SIZE
