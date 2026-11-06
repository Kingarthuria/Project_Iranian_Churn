"""Threshold berbasis rasio biaya (keputusan 32) dan suara mayoritas (keputusan 33)."""
import numpy as np
import pandas as pd

from src import config


def confusion(y_true, scores, threshold: float) -> tuple[int, int, int]:
    """Kembalikan (tertangkap, salah hubungi, terlewat) untuk satu threshold."""
    y_true, scores = np.asarray(y_true), np.asarray(scores)
    contacted = scores >= threshold
    caught = int((contacted & (y_true == 1)).sum())
    wrong = int((contacted & (y_true == 0)).sum())
    missed = int((~contacted & (y_true == 1)).sum())
    return caught, wrong, missed


def cost(wrong: float, missed: float, ratio: float) -> float:
    """Biaya dalam satuan "kali salah hubungi": salah hubungi + rasio × churn terlewat."""
    return wrong + ratio * missed


def best_threshold(y_true, scores, ratio: float, grid=config.THRESHOLD_GRID) -> float:
    """Threshold dengan biaya terendah. Kalau seri, threshold terkecil yang dipakai."""
    costs = [cost(*confusion(y_true, scores, th)[1:], ratio) for th in grid]
    return float(grid[int(np.argmin(costs))])


def select_thresholds(y_true, oof: np.ndarray) -> pd.DataFrame:
    """Threshold tiap rasio dari skor out-of-fold berulang, berformat sama dengan threshold_skenario.csv.

    Threshold akhir adalah median threshold terbaik dari tiap ulangan, dibulatkan 3 desimal.
    """
    rows = []
    for ratio in config.COST_RATIOS:
        chosen = [best_threshold(y_true, scores, ratio) for scores in oof]
        rows.append({
            "rasio": f"1:{ratio}",
            "threshold": round(float(np.median(chosen)), 3),
            "threshold_min": float(min(chosen)),
            "threshold_max": float(max(chosen)),
            "is_default": ratio == config.DEFAULT_RATIO,
            "penjelasan": config.RATIO_EXPLANATIONS[ratio],
        })
    return pd.DataFrame(rows)


def high_risk_by_vote(oof: np.ndarray, threshold: float) -> np.ndarray:
    """Berisiko tinggi jika skor mencapai threshold di lebih dari separuh ulangan."""
    return (np.asarray(oof) >= threshold).mean(axis=0) > 0.5
