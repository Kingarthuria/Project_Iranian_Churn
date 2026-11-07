"""Grafik demo dengan Altair (ikut terpasang bersama Streamlit) dan diagram alur Graphviz.

Warna dipilih untuk tema terang (.streamlit/config.toml). Merah berarti menaikkan skor, biru menurunkan.
"""
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


def segment_matrix(segment_id: str, t: dict) -> alt.Chart:
    """Matriks 2×2 risiko × nilai, dengan segmen pelanggan ini ditandai."""
    cells = [
        ("III", t["segment_low"], t["segment_high"]),
        ("I", t["segment_high"], t["segment_high"]),
        ("IV", t["segment_low"], t["segment_low"]),
        ("II", t["segment_high"], t["segment_low"]),
    ]
    data = pd.DataFrame([
        {
            "id": seg,
            "value": value,
            "risk": risk,
            "name": t["segments"][seg]["name"],
            "you": f"● {t['segment_you']}" if seg == segment_id else "",
            "current": seg == segment_id,
        }
        for seg, value, risk in cells
    ])
    # Nilai tinggi di kiri (permintaan pengguna), jadi urutan baca: I kiri atas, II kiri bawah, III kanan atas, IV kanan
    # bawah
    x = alt.X("value:N", sort=[t["segment_high"], t["segment_low"]], title=t["segment_axis_value"],
              axis=alt.Axis(orient="top", labelAngle=0, labelColor=INK, titleColor=PRIMARY, ticks=False,
                            domain=False))
    y = alt.Y("risk:N", sort=[t["segment_high"], t["segment_low"]], title=t["segment_axis_risk"],
              axis=alt.Axis(labelColor=INK, titleColor=PRIMARY, ticks=False, domain=False))
    base = alt.Chart(data).encode(x=x, y=y)
    rect = base.mark_rect(stroke="white", strokeWidth=4, cornerRadius=6).encode(
        color=alt.condition("datum.current", alt.value(PRIMARY), alt.value(SURFACE))
    )
    name = base.mark_text(fontSize=15, fontWeight="bold", dy=-8).encode(
        text="name:N", color=alt.condition("datum.current", alt.value("white"), alt.value(PRIMARY))
    )
    you = base.mark_text(fontSize=12, dy=14, color="white").encode(text="you:N")
    return (rect + name + you).properties(height=230).configure_view(stroke=None)


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


def sigmoid(margin: float) -> float:
    return float(1 / (1 + np.exp(-margin)))
