"""Experiment tracking dan registry, dijalankan ke folder sementara supaya mlflow.db asli tidak tersentuh."""
import os

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

import mlflow
import numpy as np
import pytest
from mlflow.tracking import MlflowClient

from src import config, track
from src.model import build_pipeline


@pytest.fixture(scope="module")
def tracked(tmp_path_factory, clean_df):
    base = tmp_path_factory.mktemp("mlflow")
    result = track.main(
        tracking_uri=track.sqlite_uri(base / "mlflow.db"),
        artifact_dir=base / "mlartifacts",
        model_dir=base / "models",
    )
    client = MlflowClient(tracking_uri=result["tracking_uri"], registry_uri=result["tracking_uri"])
    experiment = client.get_experiment_by_name(config.EXPERIMENT_NAME)
    runs = {run.info.run_name: run for run in client.search_runs([experiment.experiment_id])}
    return result, client, runs


def test_four_runs_finished(tracked):
    _, _, runs = tracked
    assert set(runs) == set(track.CANDIDATES)
    assert all(run.info.status == "FINISHED" for run in runs.values())


@pytest.mark.parametrize("name, pr_mean, pr_min, pr_max, group_mean", [
    # Angka dari program/Modeling_Project_Churn.ipynb (temuan 13–15)
    ("xgboost_12_fitur", 0.931, 0.920, 0.939, 0.474),
    ("xgboost_10_fitur", 0.887, 0.878, 0.896, 0.231),
    ("logreg_12_fitur", 0.773, 0.768, 0.776, 0.625),
    ("dummy", 0.157, 0.157, 0.157, 0.161),
])
def test_metrics_match_phase2(tracked, name, pr_mean, pr_min, pr_max, group_mean):
    _, _, runs = tracked
    metrics = runs[name].data.metrics
    assert round(metrics["pr_auc_mean"], 3) == pr_mean
    assert round(metrics["pr_auc_min"], 3) == pr_min
    assert round(metrics["pr_auc_max"], 3) == pr_max
    assert round(metrics["cek_grup_pr_auc_mean"], 3) == group_mean


def test_test_data_not_used(tracked):
    _, _, runs = tracked
    assert all(run.data.tags["data_uji"].startswith("tidak dipakai") for run in runs.values())


def test_champion_model_loads_and_matches(tracked, split):
    result, client, runs = tracked
    version = client.get_model_version_by_alias(config.REGISTERED_MODEL_NAME, config.MODEL_ALIAS)
    assert version.run_id == runs["xgboost_12_fitur"].info.run_id

    mlflow.set_registry_uri(result["tracking_uri"])
    loaded = mlflow.sklearn.load_model(f"models:/{config.REGISTERED_MODEL_NAME}@{config.MODEL_ALIAS}")
    train_df, _ = split
    fresh = build_pipeline().fit(train_df, train_df[config.TARGET])
    sample = train_df.head(200)
    np.testing.assert_allclose(loaded.predict_proba(sample), fresh.predict_proba(sample))
