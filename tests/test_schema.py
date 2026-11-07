"""Skema input demo: nilai valid lolos, nilai tidak valid ditolak, dan batas sama dengan data latih."""
import pytest
from pydantic import ValidationError

from src import config
from src.schema import BOUNDS, LABELS, CustomerInput


@pytest.fixture
def valid_row(split):
    train, _ = split
    return train[config.FEATURES].iloc[0].to_dict()


def test_valid_customer_passes(valid_row):
    customer = CustomerInput(**valid_row)
    assert list(customer.model_dump()) == config.FEATURES


def test_bounds_match_training_data(split):
    train, _ = split
    for feature in config.FEATURES:
        low, high = BOUNDS[feature]
        assert train[feature].min() == pytest.approx(low), feature
        assert train[feature].max() == pytest.approx(high), feature
    assert set(LABELS) == set(config.FEATURES)


@pytest.mark.parametrize("feature, bad_value", [
    ("Seconds_of_Use", -1),
    ("Complains", 2),
    ("Status", 0),
    ("Tariff_Plan", 3),
    ("Age_Group", 6),
    ("Charge_Amount", 11),
    ("Frequency_of_use", 10_000),
])
def test_invalid_values_rejected(valid_row, feature, bad_value):
    with pytest.raises(ValidationError):
        CustomerInput(**{**valid_row, feature: bad_value})


def test_missing_and_extra_fields_rejected(valid_row):
    missing = {k: v for k, v in valid_row.items() if k != "Complains"}
    with pytest.raises(ValidationError):
        CustomerInput(**missing)
    with pytest.raises(ValidationError):
        CustomerInput(**valid_row, Churn=1)
