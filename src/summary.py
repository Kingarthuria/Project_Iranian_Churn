"""Ringkasan angka untuk tab "Cara kerja model" di demo.

Jalankan dari root project:
    python -X utf8 -m src.summary

Hasilnya dua file kecil di docs/, supaya demo tidak menghitung ulang saat menyala:
- ringkasan_model.csv: PR-AUC dan ROC-AUC CV acak XGBoost final dan DummyClassifier (temuan 13)
- kepentingan_fitur.csv: permutation importance pada CV acak data latih (temuan 22)

Cara hitungnya sama dengan program/Modeling_Project_Churn.ipynb dan program/Interpretasi_Model.ipynb.
Data uji tidak dipakai, dan CV grup tidak dicatat di sini (keputusan 2 dan 22).
"""
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import average_precision_score
from sklearn.model_selection import RepeatedStratifiedKFold

from src import clean_data, config
from src.data import load_clean, split_train_test
from src.evaluate import evaluate, random_cv_repeats
from src.model import build_model

METRICS_PATH = config.ROOT / "docs" / "ringkasan_model.csv"
IMPORTANCE_PATH = config.ROOT / "docs" / "kepentingan_fitur.csv"

# Kelompok pemakaian dinilai bersama, sama dengan notebook interpretasi (keputusan 34)
USAGE_GROUP = ["Seconds_of_Use", "Frequency_of_use", "Frequency_of_SMS", "Distinct_Called_Numbers", "Customer_Value"]
USAGE_GROUP_NAME = "usage_group"
N_PERMUTATIONS = 5
MODELS = {
    "xgboost_12_fitur": build_model,
    "dummy": lambda: DummyClassifier(strategy="prior"),
}


def model_metrics(X: pd.DataFrame, y) -> pd.DataFrame:
    repeats = random_cv_repeats(X, y)
    rows = []
    for name, make_model in MODELS.items():
        table = evaluate(make_model, X, y, repeats)
        row = {"model": name}
        for metric in ("pr_auc", "roc_auc"):
            row[f"{metric}_mean"] = table[metric].mean()
            row[f"{metric}_min"] = table[metric].min()
            row[f"{metric}_max"] = table[metric].max()
        rows.append(row)
    return pd.DataFrame(rows).round(3)


def permutation_importance(X: pd.DataFrame, y) -> pd.DataFrame:
    """Turunnya PR-AUC saat satu fitur (atau kelompok pemakaian) diacak di fold validasi."""
    y = np.asarray(y)
    items = {**{feature: [feature] for feature in config.FEATURES}, USAGE_GROUP_NAME: USAGE_GROUP}
    splitter = RepeatedStratifiedKFold(
        n_splits=config.N_SPLITS, n_repeats=config.N_REPEATS, random_state=config.OOF_SEED
    )
    splits = list(splitter.split(X, y))
    rng = np.random.default_rng(config.SEED)
    per_repeat = []
    for start in range(0, len(splits), config.N_SPLITS):
        fold_drops = []
        for fit_idx, val_idx in splits[start:start + config.N_SPLITS]:
            if y[val_idx].max() == 0:
                continue
            model = build_model().fit(X.iloc[fit_idx], y[fit_idx])
            X_val, y_val = X.iloc[val_idx], y[val_idx]
            base = average_precision_score(y_val, model.predict_proba(X_val)[:, 1])
            drops = {}
            for name, columns in items.items():
                values = []
                for _ in range(N_PERMUTATIONS):
                    shuffled = X_val.copy()
                    # Baris diacak bersama untuk semua kolom dalam satu item
                    shuffled[columns] = X_val[columns].to_numpy()[rng.permutation(len(X_val))]
                    values.append(base - average_precision_score(y_val, model.predict_proba(shuffled)[:, 1]))
                drops[name] = np.mean(values)
            fold_drops.append(drops)
        per_repeat.append(pd.DataFrame(fold_drops).mean())
    table = pd.DataFrame(per_repeat)
    return (
        pd.DataFrame({
            "item": table.columns,
            "drop_mean": table.mean().to_numpy(),
            "drop_min": table.min().to_numpy(),
            "drop_max": table.max().to_numpy(),
        })
        .sort_values("drop_mean", ascending=False, kind="stable")
        .round(3)
        .reset_index(drop=True)
    )


def build(X: pd.DataFrame, y) -> tuple[pd.DataFrame, pd.DataFrame]:
    return model_metrics(X, y), permutation_importance(X, y)


def main() -> None:
    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        clean_data.main()
    train, _ = split_train_test(load_clean())
    metrics, importance = build(train[config.FEATURES], train[config.TARGET].to_numpy())
    # Akhir baris LF, sama dengan .gitattributes untuk docs/*.csv
    metrics.to_csv(METRICS_PATH, index=False, lineterminator="\n")
    importance.to_csv(IMPORTANCE_PATH, index=False, lineterminator="\n")
    print(metrics.to_string(index=False))
    print()
    print(importance.to_string(index=False))


if __name__ == "__main__":
    main()
