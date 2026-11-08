"""Pelatihan ulang model final dengan satu perintah (keputusan 36).

Jalankan dari root project:
    python -X utf8 -m src.train

Langkahnya:
1. Membuat data bersih jika belum ada.
2. Menghitung ulang threshold dari skor out-of-fold data latih, lalu memastikannya sama dengan
   docs/threshold_skenario.csv. Threshold sudah dikunci (keputusan 32), jadi file itu tidak ditimpa.
3. Melatih Pipeline final pada 2.280 baris latih. Data uji tidak dipakai.
4. Menyimpan Pipeline dan metadata ke models/, lalu memuat ulang untuk memastikan hasilnya sama.
"""
import hashlib
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost

from src import clean_data, config
from src.data import load_clean, split_train_test
from src.model import build_pipeline, oof_scores
from src.threshold import select_thresholds

MODEL_FILE = "churn_pipeline.joblib"
METADATA_FILE = "metadata.json"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_thresholds(y_train: np.ndarray, X_train: pd.DataFrame) -> pd.DataFrame:
    """Hitung ulang threshold dan hentikan proses jika berbeda dari file yang sudah dikunci."""
    recomputed = select_thresholds(y_train, oof_scores(X_train, y_train))
    locked = pd.read_csv(config.THRESHOLD_PATH)
    try:
        pd.testing.assert_frame_equal(recomputed, locked)
    except AssertionError as error:
        raise ValueError(
            "Threshold hasil hitung ulang berbeda dari docs/threshold_skenario.csv. "
            "Periksa data atau versi library sebelum melanjutkan."
        ) from error
    return locked


def build_metadata(train: pd.DataFrame, thresholds: pd.DataFrame, model_path: Path) -> dict:
    return {
        "model_file": MODEL_FILE,
        "model_sha256": file_hash(model_path),
        "keputusan": "Model terkunci: XGBoost default, tanpa pembobotan, 12 fitur (keputusan 31 dan 36)",
        "target": config.TARGET,
        "features": config.FEATURES,
        "seed": config.SEED,
        "data_latih": {
            "baris": len(train),
            "churn": int(train[config.TARGET].sum()),
            "sumber": "dataset_clean/customer_churn_clean.csv",
            "sumber_sha256": file_hash(config.CLEAN_PATH),
        },
        "threshold": {
            "sumber": "docs/threshold_skenario.csv",
            "sumber_sha256": file_hash(config.THRESHOLD_PATH),
            "default_rasio": f"1:{config.DEFAULT_RATIO}",
            "per_rasio": dict(zip(thresholds["rasio"], thresholds["threshold"].astype(float))),
        },
        "versi": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit-learn": sklearn.__version__,
            "xgboost": xgboost.__version__,
            "joblib": joblib.__version__,
        },
        "keterbatasan": (
            "Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. "
            "Namun audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin "
            "dan skor model bisa terlalu optimistis."
        ),
    }


def main(output_dir: Path = config.MODEL_DIR) -> Path:
    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        print("Data bersih belum ada, dibuat dulu dari data mentah.")
        clean_data.main()

    train, _ = split_train_test(load_clean())
    X_train, y_train = train[config.FEATURES], train[config.TARGET].to_numpy()
    print(f"Data latih     : {len(train):,} baris, {y_train.sum():,} churn")

    thresholds = check_thresholds(y_train, X_train)
    print("Threshold      : sama dengan docs/threshold_skenario.csv")

    pipeline = build_pipeline().fit(train, train[config.TARGET])

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / MODEL_FILE
    joblib.dump(pipeline, model_path)

    # Muat ulang untuk memastikan file yang disimpan memberi skor yang sama
    loaded = joblib.load(model_path)
    if not np.allclose(loaded.predict_proba(train)[:, 1], pipeline.predict_proba(train)[:, 1]):
        raise ValueError("Model yang dimuat ulang memberi skor berbeda")

    metadata = build_metadata(train, thresholds, model_path)
    metadata_path = output_dir / METADATA_FILE
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Model          : {display_path(model_path)}")
    print(f"SHA-256 model  : {metadata['model_sha256']}")
    print(f"Metadata       : {display_path(metadata_path)}")
    return model_path


def display_path(path: Path) -> str:
    # Path di dalam project ditampilkan relatif, supaya output tidak memuat path absolut
    return path.relative_to(config.ROOT).as_posix() if path.is_relative_to(config.ROOT) else path.name


if __name__ == "__main__":
    main()
