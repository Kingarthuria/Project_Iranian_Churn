"""Prediksi satu pelanggan untuk demo: skor, keputusan hubungi, segmen, dan penjelasan.

Model dilatih ulang dari data latih saat dipanggil (keputusan 38), jadi tidak ada file model di Git.
"""
from dataclasses import dataclass, field

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
# Kode segmen untuk teks dua bahasa di demo (src/texts.py)
SEGMENT_IDS = {(True, True): "I", (False, True): "II", (True, False): "III", (False, False): "IV"}
N_CONTRIBUTIONS = 5


@dataclass
class Bundle:
    pipeline: Pipeline
    thresholds: pd.DataFrame
    value_cutoff: float
    examples: dict
    defaults: CustomerInput
    # Per fitur: (median, minimum, maksimum) di data latih, untuk petunjuk formulir
    hints: dict = field(default_factory=dict)
    # Jumlah baris di tiap tahap, untuk diagram alur
    counts: dict = field(default_factory=dict)
    # Age_Group -> nilai kolom Age (Age_Binning) yang selalu berpasangan dengannya. Hanya untuk tampilan formulir,
    # bukan fitur model (keputusan 10). Arti Age tidak dijelaskan UCI, jadi dibaca sebagai perkiraan umur
    age_by_group: dict = field(default_factory=dict)


def _age_by_group(train: pd.DataFrame) -> dict:
    pairs = train.groupby("Age_Group")["Age_Binning"].unique()
    if any(len(values) != 1 for values in pairs):
        raise ValueError("Age_Group dan Age_Binning tidak lagi berpasangan satu-satu")
    return {int(group): int(values[0]) for group, values in pairs.items()}


def load_bundle() -> Bundle:
    """Latih Pipeline final pada data latih dan siapkan threshold, batas nilai, serta contoh pelanggan."""
    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        clean_data.main()
    clean = load_clean()
    train, test = split_train_test(clean)
    pipeline = build_pipeline().fit(train, train[config.TARGET])
    thresholds = pd.read_csv(config.THRESHOLD_PATH).set_index("rasio")

    # Contoh dari data latih: churn dengan skor tertinggi dan tidak churn dengan skor terendah
    scores = pipeline.predict_proba(train)[:, 1]
    churn, stay = train[config.TARGET] == 1, train[config.TARGET] == 0
    examples = {
        "high": train.loc[churn].iloc[int(np.argmax(scores[churn.to_numpy()]))],
        "low": train.loc[stay].iloc[int(np.argmin(scores[stay.to_numpy()]))],
    }
    examples = {name: CustomerInput(**row[config.FEATURES].to_dict()) for name, row in examples.items()}
    # Nilai awal formulir: median data latih per fitur
    medians = train[config.FEATURES].median()
    defaults = CustomerInput(**{
        feature: float(medians[feature]) if feature == "Customer_Value" else int(np.rint(medians[feature]))
        for feature in config.FEATURES
    })
    hints = {
        feature: (float(medians[feature]), float(train[feature].min()), float(train[feature].max()))
        for feature in config.FEATURES
    }
    raw_rows = len(pd.read_csv(clean_data.RAW_PATH))
    counts = {
        "raw": raw_rows,
        "duplicates": raw_rows - len(clean),
        "clean": len(clean),
        "train": len(train),
        "train_churn": int(train[config.TARGET].sum()),
        "test": len(test),
        "test_churn": int(test[config.TARGET].sum()),
    }
    return Bundle(
        pipeline=pipeline,
        thresholds=thresholds,
        value_cutoff=float(train["Customer_Value"].median()),
        examples=examples,
        defaults=defaults,
        hints=hints,
        counts=counts,
        age_by_group=_age_by_group(train),
    )


def to_frame(customer: CustomerInput) -> pd.DataFrame:
    return pd.DataFrame([customer.model_dump()])[config.FEATURES]


def explain_all(bundle: Bundle, customer: CustomerInput) -> tuple[float, list[Contribution]]:
    """Nilai dasar dan sumbangan SHAP ke-12 fitur (log-odds) dari fungsi bawaan XGBoost, tanpa library shap.

    Nilai dasar ditambah semua sumbangan sama dengan skor model dalam log-odds. Urutan dari sumbangan terbesar.
    """
    row = to_frame(customer)
    booster = bundle.pipeline.named_steps["model"].get_booster()
    contribs = booster.predict(xgb.DMatrix(row), pred_contribs=True)[0]
    base, features = float(contribs[-1]), contribs[:-1]
    order = np.argsort(-np.abs(features), kind="stable")
    return base, [
        Contribution(feature=config.FEATURES[i], value=float(row.iloc[0, i]), shap=float(features[i]))
        for i in order
    ]


def explain(bundle: Bundle, customer: CustomerInput) -> list[Contribution]:
    """Sumbangan SHAP terbesar (log-odds)."""
    return explain_all(bundle, customer)[1][:N_CONTRIBUTIONS]


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
