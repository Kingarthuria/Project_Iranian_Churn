"""Pelatihan ulang satu perintah: file model, metadata, dan hasil muat ulang."""
import json

import joblib
import numpy as np
import pandas as pd
import pytest

from src import config, train


@pytest.fixture(scope="module")
def trained(tmp_path_factory, clean_df):
    output_dir = tmp_path_factory.mktemp("models")
    model_path = train.main(output_dir=output_dir)
    return output_dir, model_path


def test_files_are_written(trained):
    output_dir, model_path = trained
    assert model_path.exists()
    assert (output_dir / train.METADATA_FILE).exists()


def test_metadata_matches_locked_choices(trained):
    output_dir, model_path = trained
    metadata = json.loads((output_dir / train.METADATA_FILE).read_text(encoding="utf-8"))
    assert metadata["features"] == config.FEATURES
    assert metadata["data_latih"]["baris"] == config.EXPECTED_TRAIN_ROWS
    assert metadata["data_latih"]["churn"] == config.EXPECTED_TRAIN_CHURN
    assert metadata["threshold"]["per_rasio"] == {"1:2": 0.23, "1:5": 0.06, "1:10": 0.045}
    assert metadata["model_sha256"] == train.file_hash(model_path)


def test_stops_when_thresholds_differ(tmp_path, monkeypatch, train_xy):
    # Threshold sudah dikunci (keputusan 32): file yang berbeda harus menghentikan proses, bukan ditimpa
    altered = tmp_path / "threshold_skenario.csv"
    table = pd.read_csv(config.THRESHOLD_PATH)
    table.loc[table["rasio"] == "1:5", "threshold"] = 0.07
    table.to_csv(altered, index=False)
    monkeypatch.setattr(config, "THRESHOLD_PATH", altered)
    X, y = train_xy
    with pytest.raises(ValueError):
        train.check_thresholds(y, X)


def test_loaded_pipeline_matches_fresh_fit(trained, split):
    _, model_path = trained
    train_df, _ = split
    loaded = joblib.load(model_path)
    fresh = train.build_pipeline().fit(train_df, train_df[config.TARGET])
    sample = train_df.head(200)
    np.testing.assert_allclose(loaded.predict_proba(sample), fresh.predict_proba(sample))
