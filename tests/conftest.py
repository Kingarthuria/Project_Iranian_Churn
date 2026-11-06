"""Data bersama untuk test. Skor out-of-fold dihitung sekali per sesi karena butuh beberapa detik."""
import pytest

from src import clean_data, config
from src.data import load_clean, load_groups, split_train_test
from src.model import oof_scores


@pytest.fixture(scope="session")
def clean_df():
    # Data bersih tidak dilacak Git, jadi dibuat dulu kalau belum ada (misalnya setelah clone baru)
    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        clean_data.main()
    return load_clean()


@pytest.fixture(scope="session")
def groups(clean_df):
    return load_groups()


@pytest.fixture(scope="session")
def split(clean_df):
    return split_train_test(clean_df)


@pytest.fixture(scope="session")
def train_xy(split):
    train, _ = split
    return train[config.FEATURES], train[config.TARGET].to_numpy()


@pytest.fixture(scope="session")
def oof(train_xy):
    X, y = train_xy
    return oof_scores(X, y)
