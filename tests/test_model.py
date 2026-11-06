"""Pipeline final: pemilihan fitur dan kesamaan dengan XGBoost biasa."""
import numpy as np
import pytest

from src import config
from src.model import build_model, build_pipeline


@pytest.fixture(scope="module")
def fitted(split):
    train, _ = split
    pipeline = build_pipeline().fit(train, train[config.TARGET])
    plain = build_model().fit(train[config.FEATURES], train[config.TARGET])
    return train, pipeline, plain


def test_pipeline_matches_plain_xgboost(fitted):
    train, pipeline, plain = fitted
    sample = train.head(200)
    np.testing.assert_allclose(
        pipeline.predict_proba(sample)[:, 1], plain.predict_proba(sample[config.FEATURES])[:, 1]
    )


def test_pipeline_drops_extra_columns_and_ignores_order(fitted):
    train, pipeline, _ = fitted
    sample = train.head(50)
    # Data bersih memuat Churn dan Age_Binning, dan urutan kolom dibalik
    shuffled = sample[list(reversed(sample.columns))]
    np.testing.assert_allclose(pipeline.predict_proba(shuffled), pipeline.predict_proba(sample))
    np.testing.assert_allclose(
        pipeline.predict_proba(sample[config.FEATURES]), pipeline.predict_proba(sample)
    )


def test_pipeline_rejects_missing_feature(fitted):
    train, pipeline, _ = fitted
    with pytest.raises(ValueError):
        pipeline.predict_proba(train.head(5).drop(columns=["Complains"]))
