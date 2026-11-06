"""Data bersih, kelompok audit, dan pembagian data latih dan uji."""
from src import config


def test_clean_data_shape_and_no_duplicates(clean_df):
    assert clean_df.shape == (config.EXPECTED_CLEAN_ROWS, 14)
    assert not clean_df.duplicated().any()


def test_groups_aligned_with_clean_data(clean_df, groups):
    assert len(groups) == len(clean_df)
    assert groups.nunique() == 50


def test_features_match_notebooks(clean_df):
    # Notebook memakai semua kolom kecuali target dan Age_Binning, dengan urutan kolom data bersih
    notebook_features = [col for col in clean_df.columns if col not in (config.TARGET, "Age_Binning")]
    assert config.FEATURES == notebook_features
    assert config.TARGET not in config.FEATURES
    assert not set(config.EXCLUDED_COLUMNS) & set(config.FEATURES)


def test_split_sizes_and_no_overlap(split):
    train, test = split
    assert len(train) == config.EXPECTED_TRAIN_ROWS and train[config.TARGET].sum() == config.EXPECTED_TRAIN_CHURN
    assert len(test) == config.EXPECTED_TEST_ROWS and test[config.TARGET].sum() == config.EXPECTED_TEST_CHURN
    assert not set(train.index) & set(test.index)


def test_split_is_reproducible(clean_df, split):
    from src.data import split_train_test

    train_again, _ = split_train_test(clean_df)
    assert list(train_again.index) == list(split[0].index)
