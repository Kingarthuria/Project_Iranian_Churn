"""Batch simulasi untuk monitoring Fase 6 (keputusan 44).

Dataset UCI hanya punya satu periode, jadi tidak ada data bulan berikutnya yang asli. Batch dibuat dari data
latih dengan seed tetap:
- normal          : sampel acak tanpa perubahan, seharusnya tidak menunjukkan drift
- komplain_naik   : 30% pelanggan yang belum pernah komplain diubah menjadi pernah komplain
- pemakaian_turun : kolom pemakaian dan nilai terhitung dikali 0,6
- nonaktif_naik   : 40% pelanggan aktif diubah menjadi non-aktif

Batch tidak memuat label Churn, karena label baru diketahui sekitar 3 bulan kemudian. Data uji tidak dipakai
(keputusan 24). Semua batch adalah simulasi, bukan data pelanggan nyata.
"""
import numpy as np
import pandas as pd

from src import config

BATCH_SIZE = 500
SCENARIOS = ("normal", "komplain_naik", "pemakaian_turun", "nonaktif_naik")
COMPLAINT_SHARE = 0.30
INACTIVE_SHARE = 0.40
USAGE_FACTOR = 0.6
USAGE_COUNTS = ["Seconds_of_Use", "Frequency_of_use", "Frequency_of_SMS", "Distinct_Called_Numbers"]


def _flip(batch: pd.DataFrame, column: str, old: int, new: int, share: float, rng: np.random.Generator) -> None:
    candidates = batch.index[batch[column] == old]
    chosen = rng.choice(candidates, size=round(share * len(candidates)), replace=False)
    batch.loc[chosen, column] = new


def make_batch(train: pd.DataFrame, scenario: str, seed: int) -> pd.DataFrame:
    """Satu batch berisi 12 fitur, diambil acak dari data latih lalu diubah sesuai skenario."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Skenario {scenario} tidak dikenal. Pilihan: {SCENARIOS}")
    batch = train[config.FEATURES].sample(n=BATCH_SIZE, random_state=seed).reset_index(drop=True)
    rng = np.random.default_rng(seed)
    if scenario == "komplain_naik":
        _flip(batch, "Complains", 0, 1, COMPLAINT_SHARE, rng)
    elif scenario == "nonaktif_naik":
        _flip(batch, "Status", 1, 2, INACTIVE_SHARE, rng)
    elif scenario == "pemakaian_turun":
        # Nilai terhitung ikut turun karena sangat bisa dijelaskan oleh pemakaian telepon dan SMS (temuan 8)
        batch[USAGE_COUNTS] = (batch[USAGE_COUNTS] * USAGE_FACTOR).round().astype(int)
        batch["Customer_Value"] = (batch["Customer_Value"] * USAGE_FACTOR).round(2)
    return batch


def make_batches(train: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Semua skenario, masing-masing dengan seed berbeda supaya sampelnya tidak sama."""
    return {name: make_batch(train, name, config.SEED + i) for i, name in enumerate(SCENARIOS, start=1)}
