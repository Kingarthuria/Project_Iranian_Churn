"""Angka tab "Cara kerja model" sama dengan notebook, dan file di docs/ sama dengan hasil hitung ulang."""
import pandas as pd
import pytest

from src import summary


@pytest.fixture(scope="module")
def rebuilt(train_xy):
    X, y = train_xy
    return summary.build(X, y)


def test_metrics_match_phase2():
    metrics = pd.read_csv(summary.METRICS_PATH).set_index("model")
    # Temuan 13: PR-AUC CV acak XGBoost 0,931 (0,920–0,939), DummyClassifier 0,157
    xgb_row = metrics.loc["xgboost_12_fitur"]
    assert (xgb_row["pr_auc_mean"], xgb_row["pr_auc_min"], xgb_row["pr_auc_max"]) == (0.931, 0.92, 0.939)
    assert metrics.loc["dummy", "pr_auc_mean"] == 0.157


def test_importance_matches_interpretation_notebook():
    table = pd.read_csv(summary.IMPORTANCE_PATH).set_index("item")
    # Temuan 22: kelompok pemakaian 0,446 (0,427–0,463), Complains 0,224, Frequency_of_use 0,167
    group = table.loc["usage_group"]
    assert (group["drop_mean"], group["drop_min"], group["drop_max"]) == (0.446, 0.427, 0.463)
    assert table.loc["Complains", "drop_mean"] == 0.224
    assert table.loc["Frequency_of_use", "drop_mean"] == 0.167
    assert list(table.index[:3]) == ["usage_group", "Complains", "Frequency_of_use"]


def test_files_equal_recomputation(rebuilt):
    metrics, importance = rebuilt
    pd.testing.assert_frame_equal(metrics, pd.read_csv(summary.METRICS_PATH))
    pd.testing.assert_frame_equal(importance, pd.read_csv(summary.IMPORTANCE_PATH))
