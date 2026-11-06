"""Fungsi biaya dan threshold, serta kecocokan dengan docs/threshold_skenario.csv."""
import numpy as np
import pandas as pd
import pytest

from src import config
from src.threshold import best_threshold, confusion, cost, high_risk_by_vote, select_thresholds


def test_confusion_small_example():
    y = np.array([1, 1, 0, 0, 1])
    scores = np.array([0.9, 0.2, 0.7, 0.1, 0.5])
    # Threshold 0,5: dihubungi baris 0, 2, dan 4
    assert confusion(y, scores, 0.5) == (2, 1, 1)


def test_cost_formula():
    assert cost(wrong=10, missed=3, ratio=5) == 25


def test_best_threshold_prefers_lowest_cost_and_smallest_tie():
    y = np.array([1, 0, 0])
    scores = np.array([0.30, 0.20, 0.05])
    # Threshold 0,21 sampai 0,30 sama-sama sempurna. Yang terkecil dipilih
    assert best_threshold(y, scores, ratio=5) == pytest.approx(0.21)


def test_high_risk_by_vote_needs_more_than_half():
    oof = np.array([[0.1, 0.9], [0.1, 0.9], [0.9, 0.1], [0.9, 0.1]])
    # Baris pertama melewati threshold di 2 dari 4 ulangan: belum lebih dari separuh
    assert list(high_risk_by_vote(oof, 0.5)) == [False, False]


def test_oof_scores_match_notebooks(train_xy, oof):
    from sklearn.metrics import average_precision_score

    _, y = train_xy
    repeat_pr = [average_precision_score(y, scores) for scores in oof]
    # PR-AUC gabungan per ulangan di Threshold_Biaya.ipynb dan Risiko_Nilai.ipynb: 0,923 sampai 0,938
    assert round(min(repeat_pr), 3) == 0.923 and round(max(repeat_pr), 3) == 0.938


def test_thresholds_reproduce_csv(train_xy, oof):
    _, y = train_xy
    expected = pd.read_csv(config.THRESHOLD_PATH)
    pd.testing.assert_frame_equal(select_thresholds(y, oof), expected)


def test_majority_vote_matches_risk_value_notebook(oof):
    # Risiko_Nilai.ipynb dan Analisis_Error.ipynb: 464 pelanggan berisiko tinggi pada threshold 1:5
    assert high_risk_by_vote(oof, 0.06).sum() == 464
