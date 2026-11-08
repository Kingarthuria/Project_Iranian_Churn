"""Laporan drift dengan satu perintah (Fase 6, keputusan 44).

Jalankan dari root project:
    python -X utf8 -m src.monitor

Langkahnya:
1. Membuat batch simulasi dari data latih (src/simulate.py) dan menyimpannya ke monitoring/batches/.
2. Menilai tiap batch dan mencatat log prediksi baru di monitoring/prediction_log.csv (src/score_batch.py).
3. Membandingkan tiap batch dengan 2.280 baris data latih sebagai acuan: PSI per fitur, uji KS untuk kolom
   angka, chi-kuadrat untuk kolom berkode, dan porsi pelanggan yang disarankan dihubungi.
4. Menulis monitoring/laporan_drift.md dan monitoring/drift_per_fitur.csv.

Data uji tidak dipakai (keputusan 24). Semua batch adalah simulasi, dan drift data tidak sama dengan turunnya
performa model, karena label churn baru diketahui sekitar 3 bulan kemudian.
"""
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from src import clean_data, config
from src.data import load_clean, split_train_test
from src.predict import load_bundle
from src.score_batch import LOG_FILE, score_batch
from src.simulate import make_batches
from src.train import display_path, file_hash

PSI_BINS = 10
# Batas bawah proporsi supaya log tidak bernilai tak hingga saat satu kelompok kosong
PSI_EPSILON = 1e-4
REPORT_FILE = "laporan_drift.md"
DRIFT_FILE = "drift_per_fitur.csv"
STATUS_LABELS = {"stabil": "Stabil", "perlu_dicek": "Perlu dicek", "bergeser": "Bergeser"}
LIMITATION = (
    "Analisis mengikuti dokumentasi UCI yang menyatakan tiap baris mewakili satu pelanggan. Namun audit menemukan pola "
    "berulang per 50 baris, sehingga independensi antarbaris tidak terjamin dan skor model bisa terlalu optimistis."
)


def _shares(reference: pd.Series, current: pd.Series, categorical: bool) -> tuple[np.ndarray, np.ndarray]:
    """Proporsi tiap kelompok pada data acuan dan data baru. Batas kelompok selalu dari data acuan."""
    if categorical:
        categories = sorted(set(reference) | set(current))
        ref = reference.value_counts().reindex(categories, fill_value=0).to_numpy()
        cur = current.value_counts().reindex(categories, fill_value=0).to_numpy()
    else:
        # Kuantil data acuan. Kolom diskret bisa punya kuantil kembar, jadi batasnya dibuat unik
        edges = np.unique(np.quantile(reference, np.linspace(0, 1, PSI_BINS + 1)))
        edges[0], edges[-1] = -np.inf, np.inf
        ref = np.histogram(reference, bins=edges)[0]
        cur = np.histogram(current, bins=edges)[0]
    return ref / ref.sum(), cur / cur.sum()


def psi(reference: pd.Series, current: pd.Series, categorical: bool = False) -> float:
    """Population Stability Index: jumlah (baru - acuan) x ln(baru / acuan) di semua kelompok."""
    ref, cur = _shares(reference, current, categorical)
    ref, cur = np.clip(ref, PSI_EPSILON, None), np.clip(cur, PSI_EPSILON, None)
    return float(np.sum((cur - ref) * np.log(cur / ref)))


def p_value(reference: pd.Series, current: pd.Series, categorical: bool) -> float:
    """Uji KS untuk kolom angka, chi-kuadrat untuk kolom berkode."""
    if not categorical:
        return float(stats.ks_2samp(reference, current).pvalue)
    categories = sorted(set(reference) | set(current))
    table = np.array([
        reference.value_counts().reindex(categories, fill_value=0).to_numpy(),
        current.value_counts().reindex(categories, fill_value=0).to_numpy(),
    ])
    return float(stats.chi2_contingency(table).pvalue)


def psi_status(value: float) -> str:
    if value >= config.PSI_ALERT:
        return "bergeser"
    if value >= config.PSI_WARN:
        return "perlu_dicek"
    return "stabil"


def feature_drift(reference: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per fitur: PSI, p-value, status, dan apakah termasuk fitur penting (temuan 22)."""
    rows = []
    for feature in config.FEATURES:
        categorical = feature in config.CATEGORICAL_FEATURES
        value = psi(reference[feature], current[feature], categorical)
        rows.append({
            "fitur": feature,
            "jenis": "kode" if categorical else "angka",
            "uji": "chi-kuadrat" if categorical else "KS",
            "psi": round(value, 4),
            "p_value": p_value(reference[feature], current[feature], categorical),
            "status": psi_status(value),
            "fitur_penting": feature in config.KEY_FEATURES,
        })
    return pd.DataFrame(rows)


def batch_status(drift: pd.DataFrame, contact_shift: float) -> str:
    """Bergeser jika ada fitur penting dengan PSI di atas batas, atau porsi dihubungi bergeser jauh."""
    key = drift[drift["fitur_penting"]]
    if (key["status"] == "bergeser").any() or abs(contact_shift) >= config.CONTACT_SHARE_ALERT:
        return "bergeser"
    if (drift["status"] != "stabil").any():
        return "perlu_dicek"
    return "stabil"


def run(output_dir: Path = config.MONITOR_DIR) -> dict:
    if not config.CLEAN_PATH.exists() or not config.GROUPS_PATH.exists():
        clean_data.main()
    train, _ = split_train_test(load_clean())
    reference = train[config.FEATURES]
    bundle = load_bundle()
    ratio = f"1:{config.DEFAULT_RATIO}"
    threshold = float(bundle.thresholds.loc[ratio, "threshold"])
    reference_share = float((bundle.pipeline.predict_proba(reference)[:, 1] >= threshold).mean())

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "batches").mkdir(exist_ok=True)
    # Log simulasi dibuat ulang setiap kali perintah ini dijalankan, supaya hasilnya bisa diulang
    log_path = output_dir / LOG_FILE
    log_path.unlink(missing_ok=True)

    summary, details = [], []
    for name, batch in make_batches(train).items():
        batch.to_csv(output_dir / "batches" / f"{name}.csv", index=False)
        log = score_batch(bundle, batch, name, log_path, ratio)
        drift = feature_drift(reference, batch)
        share = float(log["hubungi"].mean())
        status = batch_status(drift, share - reference_share)
        summary.append({
            "batch": name,
            "status": status,
            "fitur_bergeser": ", ".join(drift.loc[drift["status"] == "bergeser", "fitur"]) or "-",
            "porsi_dihubungi": round(share, 4),
            "porsi_acuan": round(reference_share, 4),
        })
        details.append(drift.assign(batch=name))

    detail = pd.concat(details, ignore_index=True)
    detail = detail[["batch"] + [col for col in detail.columns if col != "batch"]]
    detail.to_csv(output_dir / DRIFT_FILE, index=False)
    summary = pd.DataFrame(summary)
    report = build_report(summary, detail, len(reference), threshold, ratio)
    (output_dir / REPORT_FILE).write_text(report, encoding="utf-8")
    return {"summary": summary, "detail": detail, "report": output_dir / REPORT_FILE}


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%".replace(".", ",")


def _num(value: float, decimals: int = 3) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def build_report(summary: pd.DataFrame, detail: pd.DataFrame, n_reference: int, threshold: float,
                 ratio: str) -> str:
    """Laporan Markdown berbahasa Indonesia. Semua angka berasal dari tabel hasil hitungan."""
    lines = [
        "# Laporan drift (simulasi)",
        "",
        f"Dibuat: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, dengan `python -X utf8 -m src.monitor`.",
        "",
        f"- **Acuan:** {n_reference:,} baris data latih".replace(",", "."),
        f"- **Hash data latih (SHA-256):** `{file_hash(config.CLEAN_PATH)[:16]}…`",
        f"- **Skor minimal untuk dihubungi:** {_num(threshold)} (rasio {ratio})",
        (f"- **Batas PSI:** di bawah {_num(config.PSI_WARN, 2)} stabil, {_num(config.PSI_WARN, 2)} sampai "
         f"{_num(config.PSI_ALERT, 2)} perlu dicek, {_num(config.PSI_ALERT, 2)} ke atas bergeser. Ini aturan "
         "praktis yang umum dipakai, bukan hasil hitungan dari data ini."),
        (f"- **Status batch bergeser** jika ada fitur penting (temuan 22) dengan PSI {_num(config.PSI_ALERT, 2)} "
         f"ke atas, atau porsi pelanggan yang disarankan dihubungi bergeser {100 * config.CONTACT_SHARE_ALERT:.0f} "
         "poin persen atau lebih dari acuan. Batas porsi ini juga asumsi."),
        "",
        "## Ringkasan per batch",
        "",
        "| Batch | Status | Fitur bergeser | Porsi dihubungi | Porsi acuan |",
        "|---|---|---|---|---|",
    ]
    for row in summary.itertuples():
        lines.append(
            f"| `{row.batch}` | {STATUS_LABELS[row.status]} | {row.fitur_bergeser} | {_pct(row.porsi_dihubungi)} "
            f"| {_pct(row.porsi_acuan)} |"
        )
    lines += ["", "## PSI per fitur", "", "Tanda * berarti fitur penting.", ""]
    batches = list(summary["batch"])
    lines.append("| Fitur | " + " | ".join(f"`{b}`" for b in batches) + " |")
    lines.append("|---|" + "---|" * len(batches))
    pivot = detail.pivot(index="fitur", columns="batch", values="psi").reindex(config.FEATURES)
    for feature, values in pivot.iterrows():
        mark = " *" if feature in config.KEY_FEATURES else ""
        lines.append(f"| `{feature}`{mark} | " + " | ".join(_num(values[b]) for b in batches) + " |")
    lines += [
        "",
        "## Tindak lanjut",
        "",
        ("Aturan retraining dan rollback ada di `docs/monitoring.md`. Status bergeser adalah pemicu untuk "
         "memeriksa data, bukan bukti bahwa performa model turun."),
        "",
        "## Keterbatasan",
        "",
        ("- Semua batch adalah **simulasi** dari data latih, bukan data pelanggan baru. Skenario pergeseran dibuat "
         "sengaja untuk menguji laporan ini."),
        ("- Batch diambil dari data latih model itu sendiri, jadi skornya lebih yakin daripada skor untuk "
         "pelanggan yang benar-benar baru, dan porsi dihubungi bisa berbeda dari kenyataan."),
        ("- Drift data tidak sama dengan turunnya performa. Label churn baru diketahui sekitar 3 bulan setelah "
         "data 9 bulan terkumpul, jadi performa baru bisa dinilai setelah label tiba."),
        ("- Dengan sampel besar, uji KS dan chi-kuadrat bisa memberi p-value kecil untuk perbedaan yang tidak "
         "berarti. Karena itu status memakai PSI, dan p-value hanya ada di `drift_per_fitur.csv`."),
        f"- {LIMITATION}",
        "",
    ]
    return "\n".join(lines)


def main(output_dir: Path = config.MONITOR_DIR) -> dict:
    result = run(output_dir)
    for row in result["summary"].itertuples():
        print(f"{row.batch:<16}: {STATUS_LABELS[row.status]:<12} fitur bergeser: {row.fitur_bergeser}")
    print(f"Laporan        : {display_path(result['report'])}")
    print(f"Tabel per fitur: {display_path(output_dir / DRIFT_FILE)}")
    return result


if __name__ == "__main__":
    main()
