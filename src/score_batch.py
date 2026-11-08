"""Menilai satu batch pelanggan dan mencatat log prediksi (Fase 6, keputusan 44).

Jalankan dari root project:
    python -X utf8 -m src.score_batch path/ke/batch.csv

File batch berisi 12 fitur model (nama kolom seperti data bersih). Setiap baris divalidasi dengan skema demo
(src/schema.py), lalu dinilai dengan model yang sama seperti demo (src/predict.py). Hasilnya ditambahkan ke
monitoring/prediction_log.csv, yang tidak dilacak Git. Demo publik tidak menyimpan input (keputusan 38),
jadi log hanya dibuat oleh script ini.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src import config
from src.predict import SEGMENT_IDS, Bundle, load_bundle
from src.schema import CustomerInput
from src.train import display_path, file_hash

LOG_FILE = "prediction_log.csv"
LOG_COLUMNS = ["waktu_utc", "batch", "data_latih_sha256", "rasio", "skor_minimal", "skor", "hubungi", "segmen"]


def score_batch(bundle: Bundle, batch: pd.DataFrame, name: str, log_path: Path,
                ratio: str = f"1:{config.DEFAULT_RATIO}") -> pd.DataFrame:
    """Nilai semua baris batch dan tambahkan hasilnya ke log. Mengembalikan baris log batch ini."""
    rows = [CustomerInput(**row).model_dump() for row in batch[config.FEATURES].to_dict("records")]
    features = pd.DataFrame(rows)[config.FEATURES]
    scores = bundle.pipeline.predict_proba(features)[:, 1]
    threshold = float(bundle.thresholds.loc[ratio, "threshold"])
    contact = scores >= threshold
    high_value = features["Customer_Value"].to_numpy() >= bundle.value_cutoff
    log = pd.DataFrame({
        "waktu_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "batch": name,
        "data_latih_sha256": file_hash(config.CLEAN_PATH),
        "rasio": ratio,
        "skor_minimal": threshold,
        "skor": scores.round(6),
        "hubungi": contact,
        "segmen": [SEGMENT_IDS[(bool(c), bool(v))] for c, v in zip(contact, high_value)],
    })
    log = pd.concat([log, features.reset_index(drop=True)], axis=1)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log.to_csv(log_path, mode="a", header=not log_path.exists(), index=False)
    return log


def main(batch_path: Path, log_path: Path = config.MONITOR_DIR / LOG_FILE) -> pd.DataFrame:
    batch = pd.read_csv(batch_path)
    log = score_batch(load_bundle(), batch, batch_path.stem, log_path)
    print(f"Batch          : {batch_path.name}, {len(log):,} pelanggan")
    print(f"Disarankan hub.: {int(log['hubungi'].sum()):,} pelanggan ({log['hubungi'].mean():.1%})")
    print(f"Log prediksi   : {display_path(log_path)}")
    return log


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Pakai: python -X utf8 -m src.score_batch path/ke/batch.csv")
    main(Path(sys.argv[1]))
