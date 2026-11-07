"""Skema input dan output demo, divalidasi dengan pydantic (keputusan 38).

Rentang angka mengikuti nilai terkecil dan terbesar di data latih. Nilai di luar rentang ditolak, karena
model tidak pernah melihat pelanggan seperti itu. Kode kategori mengikuti dokumentasi UCI
(PROJECT_GUIDE.md bagian 2), dan Charge_Amount boleh 10 sesuai keputusan 6.
"""
from pydantic import BaseModel, ConfigDict, Field

# Rentang per fitur: (minimum, maksimum), sama dengan data latih (diperiksa di tests/test_schema.py)
BOUNDS = {
    "Call_Failure": (0, 36),
    "Complains": (0, 1),
    "Subscription_Length": (3, 47),
    "Charge_Amount": (0, 10),
    "Seconds_of_Use": (0, 17090),
    "Frequency_of_use": (0, 255),
    "Frequency_of_SMS": (0, 522),
    "Distinct_Called_Numbers": (0, 97),
    "Age_Group": (1, 5),
    "Tariff_Plan": (1, 2),
    "Status": (1, 2),
    "Customer_Value": (0.0, 2165.28),
}

# Label Bahasa Indonesia untuk formulir demo
LABELS = {
    "Call_Failure": "Jumlah kegagalan panggilan",
    "Complains": "Pernah komplain (0 = tidak, 1 = ya)",
    "Subscription_Length": "Lama berlangganan (bulan)",
    "Charge_Amount": "Tingkat tagihan (0 = terendah, 10 = tertinggi)",
    "Seconds_of_Use": "Total detik panggilan",
    "Frequency_of_use": "Total jumlah panggilan",
    "Frequency_of_SMS": "Total jumlah SMS",
    "Distinct_Called_Numbers": "Jumlah panggilan berbeda (Distinct Called Numbers)",
    "Age_Group": "Kelompok usia (1 = lebih muda, 5 = lebih tua)",
    "Tariff_Plan": "Paket tarif (1 = pay as you go, 2 = kontrak)",
    "Status": "Status (1 = aktif, 2 = non-aktif)",
    "Customer_Value": "Nilai terhitung (Customer_Value, tanpa satuan)",
}


def _field(name: str, kind):
    low, high = BOUNDS[name]
    return Field(ge=kind(low), le=kind(high), description=LABELS[name])


class CustomerInput(BaseModel):
    """Data satu pelanggan: 12 fitur model, dengan nilai dari 9 bulan pertama menurut UCI."""

    model_config = ConfigDict(extra="forbid")

    Call_Failure: int = _field("Call_Failure", int)
    Complains: int = _field("Complains", int)
    Subscription_Length: int = _field("Subscription_Length", int)
    Charge_Amount: int = _field("Charge_Amount", int)
    Seconds_of_Use: int = _field("Seconds_of_Use", int)
    Frequency_of_use: int = _field("Frequency_of_use", int)
    Frequency_of_SMS: int = _field("Frequency_of_SMS", int)
    Distinct_Called_Numbers: int = _field("Distinct_Called_Numbers", int)
    Age_Group: int = _field("Age_Group", int)
    Tariff_Plan: int = _field("Tariff_Plan", int)
    Status: int = _field("Status", int)
    Customer_Value: float = _field("Customer_Value", float)


class Contribution(BaseModel):
    feature: str
    value: float
    shap: float


class PredictionOutput(BaseModel):
    """Hasil demo untuk satu pelanggan. Skor adalah skor risiko model, bukan peluang yang terkalibrasi."""

    score: float = Field(ge=0.0, le=1.0)
    ratio: str
    threshold: float
    contact: bool
    segment: str
    top_contributions: list[Contribution]
