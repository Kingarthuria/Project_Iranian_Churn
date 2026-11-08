"""Experiment tracking dan registry dengan MLflow lokal (keputusan 37).

Jalankan dari root project:
    python -X utf8 -m src.track

Lalu buka tampilan web dengan:
    mlflow ui --backend-store-uri sqlite:///mlflow.db

Yang dicatat: 4 run inti (XGBoost 12 fitur, XGBoost 10 fitur, Logistic Regression 12 fitur, dan
DummyClassifier) dengan CV acak dan cek CV grup pada data latih. Data uji tidak dipakai. Pipeline final
dari src.train didaftarkan di registry dengan alias champion. Setiap kali dijalankan, run baru dan versi
model baru akan bertambah.
"""
import os

# Matikan pesan petunjuk bawaan MLflow tentang fitur tracing, yang tidak dipakai di project ini
os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

import subprocess
from pathlib import Path

import joblib
import mlflow
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src import clean_data, config, train
from src.data import load_clean, load_groups, split_train_test
from src.evaluate import evaluate, group_cv_repeats, random_cv_repeats
from src.model import build_model

# Definisi model sama dengan program/Modeling_Project_Churn.ipynb
CANDIDATES = {
    "xgboost_12_fitur": {
        "make_model": build_model,
        "features": config.FEATURES,
        "deskripsi": "Model final: XGBoost default, tanpa pembobotan, 12 fitur (keputusan 31)",
        "final": True,
    },
    "xgboost_10_fitur": {
        "make_model": build_model,
        "features": config.REDUCED_FEATURES,
        "deskripsi": "Pembanding: XGBoost tanpa Status dan Complains (keputusan 29)",
        "final": False,
    },
    "logreg_12_fitur": {
        "make_model": lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "features": config.FEATURES,
        "deskripsi": "Pembanding: Logistic Regression, tertinggi pada cek CV grup (temuan 14)",
        "final": False,
    },
    "dummy": {
        "make_model": lambda: DummyClassifier(strategy="prior"),
        "features": config.FEATURES,
        "deskripsi": "Batas bawah: DummyClassifier (keputusan 25)",
        "final": False,
    },
}

TRUSTED_TYPES = ["xgboost.core.Booster", "xgboost.sklearn.XGBClassifier"]

LIMITATION = (
    "Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. "
    "Namun audit menemukan pola berulang per 50 baris, sehingga independensi antarbaris tidak terjamin "
    "dan skor model bisa terlalu optimistis."
)


def sqlite_uri(db_path: Path) -> str:
    return "sqlite:///" + db_path.resolve().as_posix()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=config.ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "tidak diketahui"


def summarize(table, prefix: str = "") -> dict:
    """Rata-rata, minimum, dan maksimum per ulangan sebagai metrik MLflow."""
    metrics = {}
    for col in ("pr_auc", "roc_auc"):
        metrics[f"{prefix}{col}_mean"] = float(table[col].mean())
        metrics[f"{prefix}{col}_min"] = float(table[col].min())
        metrics[f"{prefix}{col}_max"] = float(table[col].max())
    metrics[f"{prefix}folds_skipped"] = float(table["folds_skipped"].sum())
    return metrics


def prepare_experiment(artifact_dir: Path) -> None:
    client = MlflowClient()
    if client.get_experiment_by_name(config.EXPERIMENT_NAME) is None:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        client.create_experiment(config.EXPERIMENT_NAME, artifact_location=artifact_dir.resolve().as_uri())
    mlflow.set_experiment(config.EXPERIMENT_NAME)


def log_final_model(model_dir: Path, X_train) -> str:
    """Latih ulang dengan src.train, lampirkan file pendukung, lalu daftarkan Pipeline final."""
    model_path = train.main(output_dir=model_dir)
    pipeline = joblib.load(model_path)
    mlflow.log_artifact(str(config.THRESHOLD_PATH), artifact_path="pendukung")
    mlflow.log_artifact(str(model_dir / train.METADATA_FILE), artifact_path="pendukung")

    example = X_train.head(5)
    signature = infer_signature(example, pipeline.predict_proba(example))
    info = mlflow.sklearn.log_model(
        sk_model=pipeline,
        name="model",
        signature=signature,
        input_example=example,
        registered_model_name=config.REGISTERED_MODEL_NAME,
        # MLflow 3 menyimpan model dengan skops. Hanya dua tipe XGBoost ini yang dipercaya
        skops_trusted_types=TRUSTED_TYPES,
    )
    version = str(info.registered_model_version)
    MlflowClient().set_registered_model_alias(config.REGISTERED_MODEL_NAME, config.MODEL_ALIAS, version)
    return version


def main(tracking_uri: str | None = None, artifact_dir: Path = config.MLFLOW_ARTIFACT_DIR,
         model_dir: Path = config.MODEL_DIR) -> dict:
    tracking_uri = tracking_uri or sqlite_uri(config.MLFLOW_DB_PATH)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_registry_uri(tracking_uri)
    prepare_experiment(artifact_dir)

    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        clean_data.main()
    df = load_clean()
    train_df, _ = split_train_test(df)
    y = train_df[config.TARGET].to_numpy()
    groups = load_groups().loc[train_df.index].to_numpy()

    X_all = train_df[config.FEATURES]
    random_repeats = random_cv_repeats(X_all, y)
    group_repeats = group_cv_repeats(X_all, y, groups)

    common_tags = {
        "data_sha256": train.file_hash(config.CLEAN_PATH),
        "git_commit": git_commit(),
        "data_latih": f"{len(train_df)} baris, {int(y.sum())} churn",
        "data_uji": "tidak dipakai (catatan keputusan 24)",
        "keterbatasan": LIMITATION,
    }

    run_ids, model_version = {}, None
    for name, spec in CANDIDATES.items():
        X = train_df[spec["features"]]
        with mlflow.start_run(run_name=name) as run:
            mlflow.log_params({
                "model": repr(spec["make_model"]()),
                "jumlah_fitur": len(spec["features"]),
                "fitur": ", ".join(spec["features"]),
                "seed": config.SEED,
                "cv_acak": f"RepeatedStratifiedKFold({config.N_SPLITS}, {config.N_REPEATS}), seed {config.MODEL_SELECTION_SEED}",
                "cv_grup": f"StratifiedGroupKFold({config.N_SPLITS}) per audit_group, {config.N_REPEATS} seed",
            })
            mlflow.log_metrics(summarize(evaluate(spec["make_model"], X, y, random_repeats)))
            mlflow.log_metrics(summarize(evaluate(spec["make_model"], X, y, group_repeats), prefix="cek_grup_"))
            mlflow.set_tags({**common_tags, "deskripsi": spec["deskripsi"], "model_final": str(spec["final"])})
            if spec["final"]:
                mlflow.set_tags({
                    "keputusan": "31, 32, 36, 37",
                    "skor_data_uji": "lihat temuan 18 di PROJECT_GUIDE.md (tidak dihitung ulang)",
                })
                model_version = log_final_model(model_dir, X)
            run_ids[name] = run.info.run_id
        print(f"Run tercatat   : {name}")

    print(f"Model terdaftar: {config.REGISTERED_MODEL_NAME} versi {model_version}, alias {config.MODEL_ALIAS}")
    print("Buka UI dengan : mlflow ui --backend-store-uri sqlite:///mlflow.db")
    return {"run_ids": run_ids, "model_version": model_version, "tracking_uri": tracking_uri}


if __name__ == "__main__":
    main()
