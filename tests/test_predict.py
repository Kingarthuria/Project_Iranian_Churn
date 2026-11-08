"""Prediksi demo: skor sama dengan Pipeline, threshold sesuai CSV, dan penjelasan konsisten dengan skor."""
import numpy as np
import pandas as pd
import pytest
import xgboost as xgb

from src import config
from src.model import build_pipeline
from src.predict import SEGMENTS, explain_all, load_bundle, predict, to_frame
from src.schema import CustomerInput


@pytest.fixture(scope="module")
def bundle(clean_df):
    return load_bundle()


@pytest.fixture(scope="module")
def customers(split):
    train, _ = split
    return [CustomerInput(**row) for row in train[config.FEATURES].head(30).to_dict("records")]


def test_score_matches_pipeline(bundle, customers, split):
    train, _ = split
    fresh = build_pipeline().fit(train, train[config.TARGET])
    for customer in customers:
        expected = fresh.predict_proba(to_frame(customer))[0, 1]
        assert predict(bundle, customer).score == pytest.approx(expected)


def test_thresholds_follow_csv_and_decision(bundle, customers):
    locked = pd.read_csv(config.THRESHOLD_PATH).set_index("rasio")["threshold"]
    for ratio, threshold in locked.items():
        for customer in customers:
            result = predict(bundle, customer, ratio)
            assert result.threshold == threshold
            assert result.contact == (result.score >= threshold)


def test_segment_uses_risk_and_median_value(bundle, customers):
    assert bundle.value_cutoff == pytest.approx(232.68)
    for customer in customers:
        result = predict(bundle, customer)
        assert result.segment == SEGMENTS[(result.contact, customer.Customer_Value >= bundle.value_cutoff)]


def test_unknown_ratio_rejected(bundle, customers):
    with pytest.raises(ValueError):
        predict(bundle, customers[0], "1:3")


def test_explanation_consistent_with_score(bundle, customers):
    booster = bundle.pipeline.named_steps["model"].get_booster()
    for customer in customers[:5]:
        row = to_frame(customer)
        contribs = booster.predict(xgb.DMatrix(row), pred_contribs=True)[0]
        margin = booster.predict(xgb.DMatrix(row), output_margin=True)[0]
        # Jumlah sumbangan semua fitur ditambah nilai dasar sama dengan skor model (log-odds)
        assert np.isclose(contribs.sum(), margin, atol=1e-4)
        result = predict(bundle, customer)
        top = [c.shap for c in result.top_contributions]
        assert len(top) == 5 and top == sorted(top, key=abs, reverse=True)


def test_examples_are_valid_and_separated(bundle):
    risky = predict(bundle, bundle.examples["high"])
    safe = predict(bundle, bundle.examples["low"])
    assert risky.contact and not safe.contact
    assert predict(bundle, bundle.defaults).score >= 0


def test_explain_all_adds_up_to_score(bundle, customers):
    for customer in customers[:5]:
        base, contributions = explain_all(bundle, customer)
        assert len(contributions) == len(config.FEATURES)
        assert {c.feature for c in contributions} == set(config.FEATURES)
        margin = base + sum(c.shap for c in contributions)
        score = predict(bundle, customer).score
        assert 1 / (1 + np.exp(-margin)) == pytest.approx(score, abs=1e-5)


def test_hints_and_counts_from_training_data(bundle, split):
    train, _ = split
    for feature in config.FEATURES:
        median, low, high = bundle.hints[feature]
        assert median == pytest.approx(train[feature].median())
        assert (low, high) == (train[feature].min(), train[feature].max())
    assert bundle.counts == {
        "raw": 3150, "duplicates": 300, "clean": config.EXPECTED_CLEAN_ROWS,
        "train": config.EXPECTED_TRAIN_ROWS, "train_churn": config.EXPECTED_TRAIN_CHURN,
        "test": config.EXPECTED_TEST_ROWS, "test_churn": config.EXPECTED_TEST_CHURN,
    }


def test_age_by_group_is_one_to_one_from_training_data(bundle, split):
    # Pasangan kelompok usia dan kolom Age hanya untuk tampilan formulir. Harus satu-satu dan berasal dari data latih
    train, _ = split
    expected = train.groupby("Age_Group")["Age_Binning"].agg(lambda s: s.unique().tolist())
    assert all(len(values) == 1 for values in expected)
    assert bundle.age_by_group == {int(g): int(v[0]) for g, v in expected.items()}
    assert list(bundle.age_by_group) == sorted(bundle.age_by_group)


def test_demo_uses_one_thread_with_identical_scores(bundle, split):
    # Demo membatasi XGBoost ke satu thread untuk server Streamlit Cloud. Skornya harus persis sama dengan model
    # bawaan yang memakai semua thread, jadi model yang dikunci (keputusan 31) tidak berubah
    from src.predict import DEMO_N_JOBS
    train, _ = split
    assert bundle.pipeline.named_steps["model"].get_params()["n_jobs"] == DEMO_N_JOBS == 1
    default = build_pipeline().fit(train, train[config.TARGET])
    np.testing.assert_array_equal(
        bundle.pipeline.predict_proba(train)[:, 1], default.predict_proba(train)[:, 1]
    )
