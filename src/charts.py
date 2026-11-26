"""Grafik demo dengan Altair (ikut terpasang bersama Streamlit) dan diagram alur Graphviz.

Warna dipilih untuk tema terang (.streamlit/config.toml). Merah berarti menaikkan skor, biru menurunkan.
Skala keputusan di tab hasil berupa HTML (decision_scale), bukan Altair, supaya label jalur dan gerak penanda bisa
diatur dengan CSS.
"""
import re
from html import escape

import altair as alt
import numpy as np
import pandas as pd

INK = "#0F172A"
PRIMARY = "#334155"
MUTED = "#94A3B8"
SURFACE = "#F1F5F9"
GRID = "#E2E8F0"
UP = "#D1495B"
DOWN = "#2A78D6"
ZONE = "#FBE3E6"
# Batas bawah sumbu log. Skor yang lebih kecil ditampilkan di batas ini
SCORE_FLOOR = 1e-4


def score_position(score: float, threshold: float, contact: bool, t: dict, ratio: str) -> alt.Chart:
    """Posisi skor pelanggan terhadap batas hubungi pada sumbu log."""
    x_scale = alt.Scale(type="log", domain=[SCORE_FLOOR, 1])
    axis = alt.Axis(
        values=[0.0001, 0.001, 0.01, 0.1, 1], title=t["position_axis"], grid=False,
        labelExpr="datum.value >= 0.01 ? format(datum.value, '.2') : format(datum.value, '.4')",
        labelColor=PRIMARY, titleColor=PRIMARY,
    )
    track = alt.Chart(pd.DataFrame({"x": [SCORE_FLOOR], "x2": [1.0]})).mark_rect(
        color=SURFACE, height=18, cornerRadius=9
    ).encode(x=alt.X("x:Q", scale=x_scale, axis=axis), x2="x2:Q")
    zone = alt.Chart(pd.DataFrame({"x": [threshold], "x2": [1.0], "label": [t["position_zone"]]})).mark_rect(
        color=ZONE, height=18
    ).encode(x=alt.X("x:Q", scale=x_scale), x2="x2:Q", tooltip=["label:N"])
    rule = alt.Chart(pd.DataFrame({"x": [threshold]})).mark_rule(color=INK, strokeWidth=2, strokeDash=[4, 3]).encode(
        x=alt.X("x:Q", scale=x_scale)
    )
    rule_label = alt.Chart(pd.DataFrame({"x": [threshold], "label": [t["position_threshold"].format(ratio=ratio)]}))
    rule_label = rule_label.mark_text(dy=-22, color=INK, fontSize=12).encode(
        x=alt.X("x:Q", scale=x_scale), text="label:N"
    )
    point = alt.Chart(pd.DataFrame({"x": [max(score, SCORE_FLOOR)]})).mark_point(
        filled=True, size=320, color=UP if contact else DOWN, stroke="white", strokeWidth=2, opacity=1
    ).encode(x=alt.X("x:Q", scale=x_scale))
    return (track + zone + rule + rule_label + point).properties(height=90).configure_view(stroke=None)


def waterfall(base: float, contributions: list, t: dict, value_text) -> alt.Chart:
    """Dorongan ke-12 fitur dari skor dasar sampai skor akhir (log-odds), urut dari yang terbesar."""
    rows = [{"step": t["waterfall_base"], "start": 0.0, "end": base, "kind": "total", "text": f"{base:+.2f}"}]
    position = base
    for c in contributions:
        label = f"{t['features_short'][c.feature]} = {value_text(c.feature, c.value)}"
        rows.append({
            "step": label, "start": position, "end": position + c.shap,
            "kind": "up" if c.shap > 0 else "down", "text": f"{c.shap:+.2f}",
        })
        position += c.shap
    rows.append({"step": t["waterfall_final"], "start": 0.0, "end": position, "kind": "total",
                 "text": f"{position:+.2f}"})
    data = pd.DataFrame(rows)
    data["low"] = data[["start", "end"]].min(axis=1)
    data["high"] = data[["start", "end"]].max(axis=1)
    order = list(data["step"])
    color = alt.Color(
        "kind:N",
        scale=alt.Scale(domain=["up", "down", "total"], range=[UP, DOWN, PRIMARY]),
        legend=None,
    )
    y = alt.Y("step:N", sort=order, title=None, axis=alt.Axis(labelLimit=260, labelColor=INK))
    bars = alt.Chart(data).mark_bar(height=16, cornerRadius=2).encode(
        y=y,
        x=alt.X("low:Q", title=t["waterfall_axis"], axis=alt.Axis(gridColor=GRID, titleColor=PRIMARY)),
        x2="high:Q",
        color=color,
        tooltip=[alt.Tooltip("step:N", title=t["table_feature"]), alt.Tooltip("text:N", title=t["table_shap"])],
    )
    labels = alt.Chart(data).mark_text(align="left", dx=4, color=PRIMARY, fontSize=11).encode(
        y=alt.Y("step:N", sort=order), x="high:Q", text="text:N"
    )
    zero = alt.Chart(pd.DataFrame({"x": [0.0]})).mark_rule(color=MUTED).encode(x="x:Q")
    return (bars + labels + zero).properties(height=34 * len(data)).configure_view(stroke=None)


# Urutan sel matriks: nilai tinggi di kiri dan risiko tinggi di atas, jadi I kiri atas, III kanan atas, II kiri
# bawah, IV kanan bawah
MATRIX_LAYOUT = (("high", ("I", "III")), ("low", ("II", "IV")))


def segment_matrix(segment_id: str, t: dict) -> str:
    """Matriks prioritas 2×2 risiko × nilai terhitung (keputusan 48), HTML untuk st.html.

    Lebar sel tetap, jadi matriks tidak ikut melebar saat sidebar ditutup. Gaya ada di LAYOUT_CSS streamlit_app.py.
    """
    name = t["segments"][segment_id]["name"]
    cells = [
        '<div></div>',
        f'<div class="col">{escape(t["matrix_cols"]["high"])}</div>',
        f'<div class="col">{escape(t["matrix_cols"]["low"])}</div>',
    ]
    for risk, row in MATRIX_LAYOUT:
        cells.append(f'<div class="row">{escape(t["matrix_rows"][risk])}</div>')
        for seg in row:
            if seg == segment_id:
                cells.append(
                    f'<div class="cell on"><span>{escape(t["segments"][seg]["name"])}</span>'
                    f'<small>{escape(t["segment_you"])}</small></div>'
                )
            else:
                cells.append(f'<div class="cell"><span>{escape(t["segments"][seg]["name"])}</span></div>')
    label = escape(t["matrix_aria"].format(segment=name))
    return f'<div class="segment-matrix" role="img" aria-label="{label}">{"".join(cells)}</div>'


def importance(table: pd.DataFrame, t: dict) -> alt.Chart:
    """Permutation importance dengan rentang 10 ulangan. Kelompok pemakaian diberi warna utama."""
    data = table.copy()
    data["label"] = [
        t["importance_group"] if item == "usage_group" else t["features_short"][item] for item in data["item"]
    ]
    data["group"] = data["item"] == "usage_group"
    # Nilai -0,000 dari pembulatan ditampilkan sebagai 0
    for col in ("drop_mean", "drop_min", "drop_max"):
        data[col] = data[col].where(data[col].abs() >= 0.0005, 0.0)
    data["text"] = data["drop_mean"].map(lambda v: f"{v:.3f}")
    order = list(data.sort_values("drop_mean", ascending=False)["label"])
    y = alt.Y("label:N", sort=order, title=None, axis=alt.Axis(labelLimit=240, labelColor=INK))
    bars = alt.Chart(data).mark_bar(height=16, cornerRadius=2).encode(
        y=y,
        x=alt.X("drop_mean:Q", title=t["importance_axis"], axis=alt.Axis(gridColor=GRID, titleColor=PRIMARY)),
        color=alt.condition("datum.group", alt.value(PRIMARY), alt.value(DOWN)),
        tooltip=[alt.Tooltip("label:N", title=t["table_feature"]), alt.Tooltip("text:N", title="PR-AUC")],
    )
    ranges = alt.Chart(data).mark_rule(color=INK, strokeWidth=1.5).encode(
        y=alt.Y("label:N", sort=order), x="drop_min:Q", x2="drop_max:Q"
    )
    labels = alt.Chart(data).mark_text(align="left", dx=6, color=PRIMARY, fontSize=11).encode(
        y=alt.Y("label:N", sort=order), x="drop_max:Q", text="text:N"
    )
    return (bars + ranges + labels).properties(height=30 * len(data)).configure_view(stroke=None)


def flow_dot(counts: dict, t: dict, fmt) -> str:
    """Diagram alur data dan model dalam bahasa DOT, digambar oleh st.graphviz_chart."""
    values = {key: fmt(value) for key, value in counts.items()}
    labels = {key: text.format(**values).replace("\n", "\\n") for key, text in t["flow"].items()}
    node = f'node [shape=box, style="rounded,filled", fillcolor="{SURFACE}", color="{PRIMARY}", ' \
           f'fontname="Helvetica", fontsize=11, fontcolor="{INK}", margin="0.15,0.08"];'
    lines = [
        "digraph {",
        'rankdir=LR; bgcolor="transparent"; nodesep=0.3; ranksep=0.35;',
        node,
        f'edge [color="{MUTED}", arrowsize=0.7];',
    ]
    for key, label in labels.items():
        extra = f', fillcolor="{GRID}", fontcolor="{PRIMARY}", style="rounded,filled,dashed"' if key == "test" else ""
        lines.append(f'{key} [label="{label}"{extra}];')
    lines += [
        "raw -> clean; clean -> train; clean -> test;",
        "train -> model; model -> threshold; threshold -> decision;",
        "}",
    ]
    return "\n".join(lines)


def log_position(value: float) -> float:
    """Posisi nilai pada sumbu log SCORE_FLOOR–1, dalam persen lebar (0–100)."""
    return float((np.log10(max(value, SCORE_FLOOR)) - np.log10(SCORE_FLOOR)) / -np.log10(SCORE_FLOOR) * 100)


# Ujung kanan sumbu: penanda skor 1 tetap terlihat di dalam batang
SCALE_MAX_POSITION = 99.6
# Label penanda rata kiri/kanan jika terlalu dekat dengan tepi batang
SCALE_EDGE = 15


def decision_scale(score: float, threshold: float, contact: bool, t: dict, ratio: str,
                   score_text: str, threshold_text: str, fmt) -> str:
    """Skala keputusan (keputusan 48): batang dua jalur, batasnya skor minimal untuk dihubungi.

    Jalur tempat pelanggan berada diberi warna penuh, dan penanda menunjukkan skor pelanggan pada sumbu log.
    Hasilnya HTML untuk st.html. Gaya ada di LAYOUT_CSS streamlit_app.py. Skor dan skor minimal datang sudah
    diformat sesuai bahasa, dan `fmt(nilai, desimal)` memformat angka sumbu.
    """
    to = min(log_position(score), SCALE_MAX_POSITION)
    cut = log_position(threshold)
    edge = " edge-r" if to > 100 - SCALE_EDGE else " edge-l" if to < SCALE_EDGE else ""
    decision = t["scale_go"] if contact else t["scale_stay"]
    label = escape(t["scale_aria"].format(decision=decision, score=score_text, threshold=threshold_text))
    ticks = "".join(
        f'<span class="tick{" last" if v == 1 else ""}" style="left:{log_position(v):.2f}%">{fmt(v, digits)}</span>'
        for v, digits in ((0.0001, 4), (0.001, 3), (0.01, 2), (1, 0))
    )
    return (
        f'<div class="decision-scale" role="img" aria-label="{label}" style="--to:{to:.2f}%">'
        f'<div class="tag{edge}">{escape(t["scale_marker"].format(score=score_text))}</div>'
        '<div class="lanes">'
        f'<div class="lane stay{" on" if not contact else ""}" style="width:{cut:.2f}%">{escape(t["scale_stay"])}</div>'
        f'<div class="lane go{" on" if contact else ""}">{escape(t["scale_go"])}</div>'
        '<div class="marker"></div></div>'
        f'<div class="ticks">{ticks}</div>'
        f'<div class="thr" style="left:{cut:.2f}%">'
        f'{escape(t["scale_threshold"].format(ratio=ratio, threshold=threshold_text))}</div>'
        "</div>"
    )


def plan_timeline(steps: list[str]) -> str:
    """Linimasa langkah rencana per segmen (keputusan 48 langkah 2), HTML untuk st.html.

    Tiap langkah di src/texts.py ditulis "**waktu:** tindakan". Gaya ada di LAYOUT_CSS streamlit_app.py.
    """
    items = []
    for step in steps:
        match = re.fullmatch(r"\*\*(.+?):\*\*\s*(.+)", step, flags=re.DOTALL)
        if match is None:
            raise ValueError(f"Format langkah tidak dikenal: {step!r}")
        when, what = match.groups()
        items.append(
            f'<div class="step"><div class="mark"></div><p class="when">{escape(when)}</p>'
            f'<p class="what">{escape(what[0].upper() + what[1:])}</p></div>'
        )
    return f'<div class="plan-timeline">{"".join(items)}</div>'


def sigmoid(margin: float) -> float:
    return float(1 / (1 + np.exp(-margin)))
