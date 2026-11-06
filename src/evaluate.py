"""Penilaian model dengan CV acak dan CV grup, sama dengan program/Modeling_Project_Churn.ipynb.

Skor dihitung per fold lalu dirata-ratakan per ulangan, dan fold tanpa churn dilewati (keputusan 22).
"""
from collections.abc import Callable

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedGroupKFold

from src import config


def random_cv_repeats(X: pd.DataFrame, y) -> list:
    """CV acak berstrata berulang, pemilih model di Fase 2."""
    splitter = RepeatedStratifiedKFold(
        n_splits=config.N_SPLITS, n_repeats=config.N_REPEATS, random_state=config.MODEL_SELECTION_SEED
    )
    splits = list(splitter.split(X, np.asarray(y)))
    return [splits[i:i + config.N_SPLITS] for i in range(0, len(splits), config.N_SPLITS)]


def group_cv_repeats(X: pd.DataFrame, y, groups) -> list:
    """CV grup per kelompok audit, hanya untuk cek internal (keputusan 22)."""
    y, groups = np.asarray(y), np.asarray(groups)
    repeats = []
    for repeat in range(config.N_REPEATS):
        splitter = StratifiedGroupKFold(
            n_splits=config.N_SPLITS, shuffle=True, random_state=config.MODEL_SELECTION_SEED + repeat
        )
        splits = list(splitter.split(X, y, groups))
        for fit_idx, val_idx in splits:
            # Satu kelompok tidak boleh berada di data latih dan validasi sekaligus
            if set(groups[fit_idx]) & set(groups[val_idx]):
                raise ValueError("Kelompok audit bocor ke data latih dan validasi")
        repeats.append(splits)
    return repeats


def evaluate(make_model: Callable, X: pd.DataFrame, y, repeats: list) -> pd.DataFrame:
    """PR-AUC dan ROC-AUC per ulangan, masing-masing rata-rata dari fold yang bisa dinilai."""
    y = np.asarray(y)
    rows = []
    for splits in repeats:
        fold_pr, fold_roc = [], []
        for fit_idx, val_idx in splits:
            # Fold tanpa churn dilewati, karena metrik tidak bisa dihitung
            if y[val_idx].min() == y[val_idx].max():
                continue
            model = make_model().fit(X.iloc[fit_idx], y[fit_idx])
            scores = model.predict_proba(X.iloc[val_idx])[:, 1]
            fold_pr.append(average_precision_score(y[val_idx], scores))
            fold_roc.append(roc_auc_score(y[val_idx], scores))
        rows.append({
            "pr_auc": np.mean(fold_pr),
            "roc_auc": np.mean(fold_roc),
            "folds_skipped": config.N_SPLITS - len(fold_pr),
        })
    return pd.DataFrame(rows)
