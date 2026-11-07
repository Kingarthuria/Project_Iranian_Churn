"""Teks demo: kedua bahasa lengkap, dan kalimat keterbatasan wajib tidak berubah (keputusan 2)."""
import re

from src import config
from src.texts import FORM_GROUPS, LIMITATION_ID, TEXTS, fmt_number, fmt_score


def keys(value, prefix=""):
    if isinstance(value, dict):
        return {k for key, item in value.items() for k in keys(item, f"{prefix}{key}.")} | {prefix}
    if isinstance(value, list):
        return {f"{prefix}len={len(value)}"}
    return {prefix}


def test_both_languages_have_same_keys():
    assert keys(TEXTS["id"]) == keys(TEXTS["en"])


def test_limitation_sentence_matches_guide():
    guide = (config.ROOT / "PROJECT_GUIDE.md").read_text(encoding="utf-8")
    match = re.search(r"^> (Analisis mengikuti dokumentasi UCI.+)$", guide, flags=re.MULTILINE)
    assert match and match.group(1) == LIMITATION_ID
    assert TEXTS["id"]["limitation"] == LIMITATION_ID


def test_every_feature_has_labels_and_a_form_group():
    grouped = [feature for features in FORM_GROUPS.values() for feature in features]
    assert sorted(grouped) == sorted(config.FEATURES)
    for t in TEXTS.values():
        assert set(t["features"]) == set(t["features_short"]) == set(config.FEATURES)


def test_number_format_per_language():
    assert fmt_number("id", 2165.28, 2) == "2.165,28"
    assert fmt_number("en", 2165.28, 2) == "2,165.28"
    assert fmt_score("id", 0.0004) == "< 0,001"
    assert fmt_score("en", 0.912) == "0.912"


def test_no_forbidden_wording():
    # Skor tidak disebut peluang churn, dan nilai terhitung tidak disebut uang atau pendapatan
    text = str(TEXTS).lower()
    for phrase in ("peluang churn", "probability of churn", "pendapatan", "revenue", "rupiah"):
        assert phrase not in text
