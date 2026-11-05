"""Membuat data bersih dari data mentah dengan satu perintah.

Jalankan dari root project:
    python -X utf8 src/clean_data.py

Script hanya menjalankan keputusan yang tercatat di PROJECT_GUIDE.md bagian 4.
Data mentah di dataset/ tidak diubah.
"""
import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "dataset" / "Customer Churn.csv"
CLEAN_PATH = ROOT / "dataset_clean" / "customer_churn_clean.csv"
GROUPS_PATH = ROOT / "dataset_clean" / "validation_groups.csv"

EXPECTED_ROWS = 2850
EXPECTED_COLUMNS = 14
GROUP_SIZE = 50


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Hapus duplikat persis, lalu rapikan nama kolom."""
    # Keputusan 4: baris pertama dari tiap duplikat persis dipertahankan
    clean = raw.drop_duplicates(keep="first").reset_index(drop=True)

    # Spasi pada nama kolom diganti satu underscore, misalnya "Call  Failure"
    clean.columns = ["_".join(column.split()) for column in clean.columns]

    # Kolom ini hanya punya 5 nilai yang berpasangan dengan Age_Group
    return clean.rename(columns={"Age": "Age_Binning"})


def build_validation_groups(raw: pd.DataFrame) -> pd.DataFrame:
    """Buat kelompok validasi yang sejajar per baris dengan data bersih.

    Keputusan 22: kelompok hanya untuk cek CV grup, bukan fitur model.
    """
    groups = pd.DataFrame({"audit_group": raw.index % GROUP_SIZE})
    return groups[~raw.duplicated(keep="first")].reset_index(drop=True)


def validate(clean: pd.DataFrame, groups: pd.DataFrame) -> None:
    """Hentikan script jika hasilnya tidak sesuai keputusan pembersihan."""
    if clean.shape != (EXPECTED_ROWS, EXPECTED_COLUMNS):
        raise ValueError(
            f"Bentuk data {clean.shape}, seharusnya ({EXPECTED_ROWS}, {EXPECTED_COLUMNS})"
        )
    if clean.duplicated().any():
        raise ValueError("Data bersih masih memuat duplikat persis")
    if len(groups) != len(clean):
        raise ValueError(f"Baris kelompok {len(groups)}, seharusnya {len(clean)}")
    if groups["audit_group"].nunique() != GROUP_SIZE:
        raise ValueError(f"Jumlah kelompok seharusnya {GROUP_SIZE}")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    raw = pd.read_csv(RAW_PATH)
    clean = clean_data(raw)
    groups = build_validation_groups(raw)
    validate(clean, groups)

    CLEAN_PATH.parent.mkdir(exist_ok=True)
    # Akhir baris dipatok supaya isi file sama di semua sistem operasi
    clean.to_csv(CLEAN_PATH, index=False, lineterminator="\n")
    groups.to_csv(GROUPS_PATH, index=False, lineterminator="\n")

    churn_counts = clean["Churn"].value_counts().sort_index()
    churn_rates = clean["Churn"].value_counts(normalize=True).sort_index()

    print(f"Baris mentah      : {len(raw):,}")
    print(f"Duplikat dihapus  : {len(raw) - len(clean):,}")
    print(f"Baris bersih      : {len(clean):,}")
    print(f"Bentuk data       : {clean.shape}")
    print(f"Churn = 0         : {churn_counts[0]:,} ({churn_rates[0]:.2%})")
    print(f"Churn = 1         : {churn_counts[1]:,} ({churn_rates[1]:.2%})")
    print(f"Jumlah kelompok   : {groups['audit_group'].nunique()}")
    print(f"File bersih       : {CLEAN_PATH.relative_to(ROOT).as_posix()}")
    print(f"SHA-256 bersih    : {file_hash(CLEAN_PATH)}")
    print(f"File kelompok     : {GROUPS_PATH.relative_to(ROOT).as_posix()}")
    print(f"SHA-256 kelompok  : {file_hash(GROUPS_PATH)}")


if __name__ == "__main__":
    main()
