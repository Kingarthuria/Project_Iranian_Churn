"""Satu tempat untuk seed, path, fitur, dan pengaturan yang dipakai di seluruh `src/`.

Nilai di sini sama dengan yang dipakai notebook di `program/` (keputusan 22–36 di PROJECT_GUIDE.md).
"""
from pathlib import Path

import numpy as np

# Path relatif terhadap root project
ROOT = Path(__file__).resolve().parents[1]
CLEAN_PATH = ROOT / "dataset_clean" / "customer_churn_clean.csv"
GROUPS_PATH = ROOT / "dataset_clean" / "validation_groups.csv"
THRESHOLD_PATH = ROOT / "docs" / "threshold_skenario.csv"
MODEL_DIR = ROOT / "models"

# Satu seed global. Skor out-of-fold memakai SEED + 1, sama dengan notebook Fase 3
SEED = 180915
OOF_SEED = SEED + 1

# Pembagian data uji (keputusan 24)
TEST_SIZE = 0.2

TARGET = "Churn"
# 12 fitur model terkunci (keputusan 29 dan 31), urutannya sama dengan kolom data bersih.
# Age_Binning tidak dipakai (keputusan 10), dan audit_group bukan fitur (keputusan 22)
FEATURES = [
    "Call_Failure",
    "Complains",
    "Subscription_Length",
    "Charge_Amount",
    "Seconds_of_Use",
    "Frequency_of_use",
    "Frequency_of_SMS",
    "Distinct_Called_Numbers",
    "Age_Group",
    "Tariff_Plan",
    "Status",
    "Customer_Value",
]
EXCLUDED_COLUMNS = ("Age_Binning", "audit_group")

# CV acak berulang untuk skor out-of-fold (keputusan 22 dan 32)
N_SPLITS = 5
N_REPEATS = 10

# Threshold berbasis rasio biaya (keputusan 32)
COST_RATIOS = (2, 5, 10)
DEFAULT_RATIO = 5
THRESHOLD_GRID = np.round(np.arange(0.01, 1.0, 0.01), 2)
RATIO_EXPLANATIONS = {
    2: "Churn terlewat dianggap 2 kali lebih merugikan daripada salah hubungi. "
       "Cocok jika biaya menghubungi cukup mahal.",
    5: "Churn terlewat dianggap 5 kali lebih merugikan daripada salah hubungi. "
       "Cocok jika biaya menghubungi sedang.",
    10: "Churn terlewat dianggap 10 kali lebih merugikan daripada salah hubungi. "
        "Cocok jika biaya menghubungi murah.",
}

# Jumlah baris yang diharapkan, untuk menghentikan proses jika data berubah
EXPECTED_CLEAN_ROWS = 2850
EXPECTED_TRAIN_ROWS = 2280
EXPECTED_TRAIN_CHURN = 357
EXPECTED_TEST_ROWS = 570
EXPECTED_TEST_CHURN = 89
