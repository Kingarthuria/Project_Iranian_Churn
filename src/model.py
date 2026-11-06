"""Model terkunci, Pipeline, dan skor out-of-fold."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from src import config


def build_model() -> XGBClassifier:
    """XGBoost parameter default, tanpa pembobotan (keputusan 31)."""
    return XGBClassifier(random_state=config.SEED, eval_metric="logloss")


def build_pipeline() -> Pipeline:
    """Pipeline final: pilih 12 fitur sesuai nama, lalu XGBoost.

    Kolom lain dibuang, urutan kolom input tidak berpengaruh, dan kolom yang hilang memunculkan error.
    """
    select = ColumnTransformer(
        [("fitur", "passthrough", config.FEATURES)],
        remainder="drop",
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")
    return Pipeline([("pilih_fitur", select), ("model", build_model())])


def oof_scores(X: pd.DataFrame, y: np.ndarray, n_repeats: int = config.N_REPEATS) -> np.ndarray:
    """Skor out-of-fold berulang, sama dengan notebook Fase 3 (seed SEED + 1).

    Hasil berbentuk (n_repeats, jumlah baris). Setiap baris diberi skor oleh model yang tidak melihatnya.
    """
    y = np.asarray(y)
    splitter = RepeatedStratifiedKFold(
        n_splits=config.N_SPLITS, n_repeats=config.N_REPEATS, random_state=config.OOF_SEED
    )
    splits = list(splitter.split(X, y))
    scores = np.zeros((n_repeats, len(X)))
    for repeat in range(n_repeats):
        for fit_idx, val_idx in splits[repeat * config.N_SPLITS:(repeat + 1) * config.N_SPLITS]:
            model = build_model().fit(X.iloc[fit_idx], y[fit_idx])
            scores[repeat, val_idx] = model.predict_proba(X.iloc[val_idx])[:, 1]
    return scores
