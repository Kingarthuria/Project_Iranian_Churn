"""Prediksi satu pelanggan untuk demo: skor, keputusan hubungi, segmen, dan penjelasan.

Model dilatih ulang dari data latih saat dipanggil (keputusan 38), jadi tidak ada file model di Git.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.pipeline import Pipeline

from src import clean_data, config
from src.data import load_clean, split_train_test
from src.model import build_pipeline
from src.schema import Contribution, CustomerInput, PredictionOutput

# Penomoran segmen sama dengan program/Risiko_Nilai.ipynb (keputusan 33)
SEGMENTS = {
    (True, True): "Prioritas I (risiko tinggi, nilai tinggi)",
    (False, True): "Prioritas II (risiko rendah, nilai tinggi)",
    (True, False): "Prioritas III (risiko tinggi, nilai rendah)",
    (False, False): "Prioritas IV (risiko rendah, nilai rendah)",
}
N_CONTRIBUTIONS = 5


@dataclass
class Bundle:
    pipeline: Pipeline
    thresholds: pd.DataFrame
    value_cutoff: float
    examples: dict
    defaults: CustomerInput


def load_bundle() -> Bundle:
    """Latih Pipeline final pada data latih dan siapkan threshold, batas nilai, serta contoh pelanggan."""
    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        clean_data.main()
    train, _ = split_train_test(load_clean())
    pipeline = build_pipeline().fit(train, train[config.TARGET])
    thresholds = pd.read_csv(config.THRESHOLD_PATH).set_index("rasio")

    # Contoh dari data latih: churn dengan skor tertinggi dan tidak churn dengan skor terendah
    scores = pipeline.predict_proba(train)[:, 1]
    churn, stay = train[config.TARGET] == 1, train[config.TARGET] == 0
    examples = {
        "Contoh pelanggan berisiko": train.loc[churn].iloc[int(np.argmax(scores[churn.to_numpy()]))],
        "Contoh pelanggan aman": train.loc[stay].iloc[int(np.argmin(scores[stay.to_numpy()]))],
    }
    examples = {name: CustomerInput(**row[config.FEATURES].to_dict()) for name, row in examples.items()}
    # Nilai awal formulir: median data latih per fitur
    medians = train[config.FEATURES].median()
    defaults = CustomerInput(**{
        feature: float(medians[feature]) if feature == "Customer_Value" else int(np.rint(medians[feature]))
        for feature in config.FEATURES
    })
    return Bundle(
        pipeline=pipeline,
        thresholds=thresholds,
        value_cutoff=float(train["Customer_Value"].median()),
        examples=examples,
        defaults=defaults,
    )


def to_frame(customer: CustomerInput) -> pd.DataFrame:
    return pd.DataFrame([customer.model_dump()])[config.FEATURES]


def explain(bundle: Bundle, customer: CustomerInput) -> list[Contribution]:
    """Sumbangan SHAP terbesar (log-odds) dari fungsi bawaan XGBoost, tanpa library shap."""
    row = to_frame(customer)
    booster = bundle.pipeline.named_steps["model"].get_booster()
    contribs = booster.predict(xgb.DMatrix(row), pred_contribs=True)[0][:-1]
    order = np.argsort(-np.abs(contribs), kind="stable")[:N_CONTRIBUTIONS]
    return [
        Contribution(feature=config.FEATURES[i], value=float(row.iloc[0, i]), shap=float(contribs[i]))
        for i in order
    ]


def predict(bundle: Bundle, customer: CustomerInput, ratio: str = f"1:{config.DEFAULT_RATIO}") -> PredictionOutput:
    if ratio not in bundle.thresholds.index:
        raise ValueError(f"Rasio {ratio} tidak tersedia. Pilihan: {list(bundle.thresholds.index)}")
    score = float(bundle.pipeline.predict_proba(to_frame(customer))[0, 1])
    threshold = float(bundle.thresholds.loc[ratio, "threshold"])
    contact = score >= threshold
    high_value = customer.Customer_Value >= bundle.value_cutoff
    return PredictionOutput(
        score=score,
        ratio=ratio,
        threshold=threshold,
        contact=contact,
        segment=SEGMENTS[(contact, high_value)],
        top_contributions=explain(bundle, customer),
    )
