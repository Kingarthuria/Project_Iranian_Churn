"""Memuat data bersih dan membaginya menjadi data latih dan uji."""
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from src import config


def load_clean(path: Path = config.CLEAN_PATH) -> pd.DataFrame:
    """Muat data bersih hasil `src/clean_data.py`."""
    if not path.exists():
        raise FileNotFoundError(f"{path.name} belum ada. Jalankan dulu: python -X utf8 src/clean_data.py")
    df = pd.read_csv(path)
    if len(df) != config.EXPECTED_CLEAN_ROWS:
        raise ValueError(f"Data bersih {len(df)} baris, seharusnya {config.EXPECTED_CLEAN_ROWS}")
    missing = [col for col in config.FEATURES + [config.TARGET] if col not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan di data bersih: {missing}")
    return df


def load_groups(path: Path = config.GROUPS_PATH) -> pd.Series:
    """Muat kelompok audit. Hanya untuk cek CV grup, bukan fitur model (keputusan 22)."""
    groups = pd.read_csv(path)["audit_group"]
    if len(groups) != config.EXPECTED_CLEAN_ROWS:
        raise ValueError(f"Kelompok {len(groups)} baris, seharusnya {config.EXPECTED_CLEAN_ROWS}")
    return groups


def split_train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bagi data sama persis dengan notebook (keputusan 24).

    Indeks asli dipertahankan supaya baris tetap sejajar dengan kelompok audit.
    """
    train_idx, test_idx = train_test_split(
        df.index, test_size=config.TEST_SIZE, stratify=df[config.TARGET], random_state=config.SEED
    )
    train, test = df.loc[train_idx], df.loc[test_idx]
    checks = [
        (len(train), config.EXPECTED_TRAIN_ROWS, "Baris latih"),
        (int(train[config.TARGET].sum()), config.EXPECTED_TRAIN_CHURN, "Churn latih"),
        (len(test), config.EXPECTED_TEST_ROWS, "Baris uji"),
        (int(test[config.TARGET].sum()), config.EXPECTED_TEST_CHURN, "Churn uji"),
    ]
    for actual, expected, name in checks:
        if actual != expected:
            raise ValueError(f"{name} {actual}, seharusnya {expected}")
    return train, test
