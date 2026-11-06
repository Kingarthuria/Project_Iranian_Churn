"""Prediksi demo: skor sama dengan Pipeline, threshold sesuai CSV, dan penjelasan konsisten dengan skor."""
import numpy as np
import pandas as pd
import pytest
import xgboost as xgb

from src import config
from src.model import build_pipeline
from src.predict import SEGMENTS, load_bundle, predict, to_frame
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
    risky = predict(bundle, bundle.examples["Contoh pelanggan berisiko"])
    safe = predict(bundle, bundle.examples["Contoh pelanggan aman"])
    assert risky.contact and not safe.contact
    assert predict(bundle, bundle.defaults).score >= 0
