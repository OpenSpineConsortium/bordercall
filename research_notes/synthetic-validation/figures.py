"""The figures of this note, drawn from the records run.py wrote.

    python3 -I figures.py --records records --out figures

Line graphs in the house format (schwingcheck/figures.py, the build-up study's, which
synthval/house.py takes and adds to): lettered panels, black ink, serif type, a series told apart
by line and marker. Each figure is written as PDF and PNG,
with the CSV of every number drawn and its caption, and FIGURES.md lists them with the sha256 of
each file and the records they were drawn from. Nothing here computes a result: every number is
read from a record, so a figure and the README's tables cannot disagree. The three renders of
render.py, drawings of synthetic vertebrae in Benzel's manner, are drawn in the same call and listed
in the same index.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from typing import Dict, List, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]

import render as R  # noqa: E402
import figures_all as FA  # noqa: E402  (after render, which puts the repository on sys.path)
from synthval import house as H  # noqa: E402

LUMBAR = ("L1", "L2", "L3", "L4", "L5")
NAMES = {
    "endplate": "upper end-plate width", "endplate_depth": "upper end-plate depth",
    "endplate_lower": "lower end-plate width", "endplate_lower_depth": "lower end-plate depth",
    "endplate_area": "upper end-plate area", "endplate_lower_area": "lower end-plate area",
    "h_post": "posterior body height", "h_ant": "anterior body height",
    "canal_w": "canal width", "canal_ap": "canal depth", "canal_area": "canal area",
    "pedicle_w": "pedicle width", "pedicle_h": "pedicle height", "pedicle_area": "pedicle area",
    "pedicle_incl_sag": "pedicle angle, sagittal", "pedicle_incl_trans": "pedicle angle, transverse",
    "spinous_length": "spinous process length", "transverse_width": "transverse process span",
    "facet_w_sup": "upper facet width", "facet_area_sup": "upper facet area", "facet_area_inf": "lower facet area",
}
SHORT = {
    "endplate": "EPW", "endplate_depth": "EPD", "endplate_lower": "EPWl", "endplate_lower_depth": "EPDl",
    "endplate_area": "EPA", "endplate_lower_area": "EPAl", "h_post": "VBHp", "canal_w": "SCW", "canal_ap": "SCD",
    "canal_area": "SCA", "pedicle_w": "PDW", "pedicle_h": "PDH", "pedicle_area": "PDA", "pedicle_incl_sag": "PDIs",
    "pedicle_incl_trans": "PDIt", "spinous_length": "SPL", "transverse_width": "TPW", "facet_w_sup": "FW",
}
UNITS = {"length": "mm", "area": "mm$^2$", "angle": "degrees"}
SETTINGS = ("generator", "size_removed", "nearest the papers")
SETTING_LABEL = {"generator": "generator as it stands", "size_removed": "SDs with size taken out",
                 "nearest the papers": "nearest point to the papers"}
MEANS_MEASURES = ("endplate", "endplate_depth", "h_post", "canal_w", "canal_ap", "canal_area", "pedicle_w", "pedicle_h")
INDICATORS = ("sign", "inside", "sign or inside", "box", "convex", "any but floor", "floor", "any")
LEAST_MEASURES = 4


def read_csv(records: str, name: str) -> List[dict]:
    with open(os.path.join(records, name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def read_json(records: str, name: str):
    with open(os.path.join(records, name), encoding="utf-8") as fh:
        return json.load(fh)


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def finite(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


def median(xs: Sequence[float]) -> float:
    xs = sorted(x for x in xs if finite(x))
    if not xs:
        return float("nan")
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def quantile(xs: Sequence[float], q: float) -> float:
    xs = sorted(x for x in xs if finite(x))
    if not xs:
        return float("nan")
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def dodge(i: int, count: int, step: float = 0.16) -> float:
    return (i - (count - 1) / 2) * step


# ----- figure 1: the means against the papers --------------------------------------------------

def fig_means(records: str, out: str) -> List[str]:
    plt = H.style()
    cells = [r for r in read_csv(records, "validation_cells.csv")
             if r["setting"] == "generator" and r["which"] == "measured" and r["modalities"] == "bone_ct"]
    by = {(r["measure"], r["level"]): r for r in cells}
    series = [r for r in read_csv(records, "series.csv") if r["usable"] == "True" and r["modality"] in ("bone", "ct")]
    fig, axes = plt.subplots(2, 4, figsize=(10.0, 5.0))
    rows = []
    x = list(range(len(LUMBAR)))
    for p, (ax, key) in enumerate(zip(axes.flat, MEANS_MEASURES)):
        got = [by.get((key, lv)) for lv in LUMBAR]
        pan = [num(g["panjabi_mean"]) if g else float("nan") for g in got]
        syn = [num(g["syn_mean"]) if g else float("nan") for g in got]
        sd = [num(g["syn_sd"]) if g else float("nan") for g in got]
        ax.fill_between(x, [m - s for m, s in zip(syn, sd)], [m + s for m, s in zip(syn, sd)], color="#d9d9d9", linewidth=0)
        ax.plot(x, pan, color=H.INK, **H.SERIES_STYLE[0])
        for i, lv in enumerate(LUMBAR):
            here = [s for s in series if s["key"] == key and s["level"] == lv]
            for j, s in enumerate(here):
                ax.plot([i - 0.22 + dodge(j % 4, 4, 0.04)], [num(s["mean"])], linestyle="none", marker="o", markersize=2.6,
                        markerfacecolor="white", markeredgecolor=H.GREY, markeredgewidth=0.7)
                rows.append({"measure": key, "level": lv, "what": "series", "paper": s["paper"], "cohort": s["cohort"],
                             "mean": num(s["mean"]), "sd": num(s["sd"]), "n": num(s["n"])})
            g = got[i]
            if not g or not finite(num(g["lit_mean"])):
                continue
            k, mean, se = int(num(g["k"])), num(g["lit_mean"]), num(g["lit_se"])
            if k >= 3 and finite(se):
                ax.errorbar([i + 0.18], [mean], yerr=[1.959964 * se], color=H.INK, linestyle="none", marker="s",
                            markerfacecolor="white")
            else:
                ax.plot([i + 0.18], [mean], linestyle="none", marker="^", markerfacecolor="white", color=H.INK)
            rows.append({"measure": key, "level": lv, "what": "pooled", "series": k, "panjabi_mean": pan[i],
                         "synthetic_mean": syn[i], "synthetic_sd": sd[i], "mean": mean,
                         "ci_low": mean - 1.959964 * se if k >= 3 else float("nan"),
                         "ci_high": mean + 1.959964 * se if k >= 3 else float("nan"),
                         "pi_low": num(g["pi_low"]), "pi_high": num(g["pi_high"])})
        kind = got[2]["kind"] if got[2] else "length"
        ax.set_xticks(x)
        ax.set_xticklabels(LUMBAR)
        ax.set_xlim(-0.5, len(LUMBAR) - 0.5)
        ax.set_ylabel("%s (%s)" % (SHORT[key], UNITS.get(kind, "")))
        H.letter(ax, chr(65 + p), NAMES[key])
    handles = [plt.Line2D([], [], color=H.INK, **H.SERIES_STYLE[0]),
               plt.Line2D([], [], color=H.INK, linestyle="none", marker="s", markerfacecolor="white"),
               plt.Line2D([], [], color=H.INK, linestyle="none", marker="^", markerfacecolor="white"),
               plt.Line2D([], [], linestyle="none", marker="o", markersize=3, markerfacecolor="white",
                          markeredgecolor=H.GREY),
               plt.matplotlib.patches.Patch(facecolor="#d9d9d9", edgecolor="none")]
    fig.legend(handles, ["Panjabi, the generator's mean", "papers pooled, 95% CI", "papers, one or two series",
                         "one published series", "synthetic mean $\\pm$ 1 SD"],
               loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.04))
    fig.tight_layout(rect=(0, 0.05, 1, 1), h_pad=1.6)
    H.write_csv(out, "fig1_means", rows)
    return H.save(fig, out, "fig1_means", (
        "Lumbar means of eight measures. The generator draws around Panjabi's means; each grey circle "
        "is one published series of the 39 papers (bone and CT, adults, Panjabi's definitions or close "
        "ones), pooled "
        "by REML where three or more exist. The grey band is the synthetic population's measured spread."))


# ----- figure 2: the spread --------------------------------------------------------------------

def spread_rows(records: str) -> List[dict]:
    cells = [r for r in read_csv(records, "validation_cells.csv")
             if r["which"] == "measured" and r["modalities"] == "bone_ct" and finite(num(r["sd_ratio"]))]
    out = []
    for r in cells:
        out.append({"setting": r["setting"], "measure": r["measure"], "level": r["level"], "ratio": num(r["sd_ratio"]),
                    "panjabi": num(r["panjabi_sd_ratio"])})
    return out


def log_ticks(ax, ticks=(0.5, 0.75, 1, 1.5, 2, 3, 5)):
    from matplotlib.ticker import NullFormatter
    ax.set_yscale("log")
    ax.set_yticks(list(ticks))
    ax.set_yticklabels(["%g" % t for t in ticks])
    ax.yaxis.set_minor_formatter(NullFormatter())


def fig_spread(records: str, out: str) -> List[str]:
    plt = H.style()
    rows = spread_rows(records)
    measures = sorted({r["measure"] for r in rows}, key=lambda k: (-sum(1 for r in rows if r["measure"] == k), k))
    measures = [m for m in measures if sum(1 for r in rows if r["measure"] == m and r["setting"] == "generator") >= 3]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 3.8), gridspec_kw={"width_ratios": [1.6, 1.0]})
    drawn = []
    series = [(s, SETTING_LABEL[s], "ratio") for s in SETTINGS] + [("generator", "Panjabi's own SDs", "panjabi")]
    for si, (setting, label, field) in enumerate(series):
        st = H.SERIES_STYLE[si]
        for mi, m in enumerate(measures):
            vals = [r[field] for r in rows if r["setting"] == setting and r["measure"] == m]
            med, q1, q3 = median(vals), quantile(vals, 0.25), quantile(vals, 0.75)
            a.errorbar([mi + dodge(si, len(series))], [med], yerr=[[med - q1], [q3 - med]], color=H.INK,
                       linestyle="none", marker=st["marker"], markerfacecolor=st["markerfacecolor"],
                       label=label if mi == 0 else None)
            drawn.append({"panel": "A", "series": label, "measure": m, "cells": len(vals), "median": med, "q1": q1, "q3": q3})
    a.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
    log_ticks(a)
    a.set_xticks(range(len(measures)))
    a.set_xticklabels([SHORT.get(m, m) for m in measures], rotation=0)
    a.set_ylabel("SD over the papers' pooled SD")
    a.legend(loc="upper right", ncol=2)
    H.letter(a, "A", "by measure, median and quartiles over levels")
    levels = [lv for lv in ("C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10",
                            "T11", "T12", "L1", "L2", "L3", "L4", "L5")
              if len({r["measure"] for r in rows if r["level"] == lv and r["setting"] == "generator"}) >= LEAST_MEASURES]
    for si, (setting, label, field) in enumerate(series):
        meds = [median([r[field] for r in rows if r["setting"] == setting and r["level"] == lv]) for lv in levels]
        b.plot(range(len(levels)), meds, color=H.INK, **H.SERIES_STYLE[si], label=label)
        drawn += [{"panel": "B", "series": label, "level": lv, "median": v} for lv, v in zip(levels, meds)]
    b.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
    log_ticks(b)
    b.set_xticks(range(len(levels)))
    b.set_xticklabels(levels, rotation=90)
    b.set_ylabel("median SD ratio over measures")
    H.letter(b, "B", "by level, %d measures or more" % LEAST_MEASURES)
    fig.tight_layout()
    H.write_csv(out, "fig2_spread", drawn)
    return H.save(fig, out, "fig2_spread", (
        "The spread of the synthetic population against the published series: each cell's measured "
        "SD over the pooled published SD (bone and CT, Tan's SDs left out). One means the papers' "
        "spread; Panjabi's own SDs are shown beside the three settings of the generator. B keeps the "
        "levels that four measures or more reach."))


# ----- figure 3: structure ---------------------------------------------------------------------

def fig_structure(records: str, out: str) -> List[str]:
    plt = H.style()
    st = read_json(records, "structure.json")
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.6))
    drawn = []
    a = axes[0, 0]
    pairs = [g["pair"] for g in st["griffith"]]
    corr = st["correlations"]
    together = {g["pair"]: g["sexes_together"] for g in st["griffith"]}
    for pi, pair in enumerate(pairs):
        ref = next(r for r in corr["generator"] if r["pair"] == pair)
        for j, (sex, lo_hi) in enumerate((("men", ref["griffith_ci_men"]), ("women", ref["griffith_ci_women"]))):
            v = ref["griffith_" + sex]
            a.errorbar([pi + dodge(j, 6)], [v], yerr=[[v - lo_hi[0]], [lo_hi[1] - v]], color=H.INK, linestyle="none",
                       marker="D" if sex == "men" else "v", markerfacecolor="white",
                       label="Griffith 2016, %s (95%% CI)" % sex if pi == 0 else None)
            drawn.append({"panel": "A", "pair": pair, "series": "griffith " + sex, "r": v, "low": lo_hi[0], "high": lo_hi[1]})
        a.plot([pi + dodge(2, 6)], [together[pair]], linestyle="none", color=H.INK, marker="x",
               label="Griffith, the sexes together (the target)" if pi == 0 else None)
        drawn.append({"panel": "A", "pair": pair, "series": "griffith, sexes together", "r": together[pair]})
        for j, s in enumerate(SETTINGS):
            r = next(x for x in corr[s] if x["pair"] == pair)["synthetic"]
            sty = H.SERIES_STYLE[j]
            a.plot([pi + dodge(j + 3, 6)], [r], linestyle="none", color=H.INK, marker=sty["marker"],
                   markerfacecolor=sty["markerfacecolor"], label=SETTING_LABEL[s] if pi == 0 else None)
            drawn.append({"panel": "A", "pair": pair, "series": s, "r": r})
    a.set_xticks(range(len(pairs)))
    a.set_xticklabels([p.replace(" with ", "\nwith ").replace("_", " ") for p in pairs], fontsize=7)
    a.set_ylim(0, 1.35)
    a.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    a.set_ylabel("correlation of subject means, L1-L5")
    a.legend(loc="upper left", fontsize=6.2, ncol=2)
    H.letter(a, "A", "the canal against the body")
    b = axes[0, 1]
    iso = st["isometry"]
    first = {True: True, False: True}
    for i, r in enumerate(iso):
        unit = bool(r.get("is_unit"))
        b.errorbar([i], [r["loading"]], yerr=[[r["loading"] - r["q1"] / r["body_unit"]], [r["q3"] / r["body_unit"] - r["loading"]]],
                   color=H.INK, linestyle="none", marker="s" if unit else "o", markerfacecolor=H.GREY if unit else "white",
                   label=("the unit's own measures (their median is the unit)" if unit else
                          "papers: log(men/women) over the body's; bars: quartiles over cells") if first[unit] else None)
        first[unit] = False
        drawn.append({"panel": "B", "measure": r["measure"], "loading": r["loading"], "q1": r["q1"] / r["body_unit"],
                      "q3": r["q3"] / r["body_unit"], "cells": r["cells"], "generator": r["generator_loading"],
                      "is_unit": unit})
    b.axhline(1.0, color=H.INK, linestyle="--", linewidth=0.9, label="generator: every measure 1")
    b.set_xticks(range(len(iso)))
    b.set_xticklabels([SHORT.get(r["measure"], r["measure"]) for r in iso])
    b.set_ylabel("share of the body's sex difference")
    b.set_ylim(-0.6, 2.2)
    b.legend(loc="upper left", fontsize=6.2)
    H.letter(b, "B", "how the measures scale with size")
    for p, (ax, ratio) in enumerate(zip(axes[1], ("canal depth / body depth", "canal width / canal depth"))):
        rr = [r for r in st["ratios"] if r["ratio"] == ratio]
        x = [LUMBAR.index(r["level"]) for r in rr]
        m = [r["synthetic_mean"] for r in rr]
        s = [r["synthetic_sd"] for r in rr]
        ax.fill_between(x, [u - v for u, v in zip(m, s)], [u + v for u, v in zip(m, s)], color="#d9d9d9", linewidth=0,
                        label="synthetic, mean $\\pm$ 1 SD")
        ax.plot(x, [r["panjabi_ratio_of_means"] for r in rr], color=H.INK, **H.SERIES_STYLE[0], label="Panjabi, ratio of means")
        papers = [k for k in rr[0] if k not in ("level", "panjabi_ratio_of_means", "ratio", "source", "synthetic_mean", "synthetic_sd")]
        for j, k in enumerate(sorted(papers)):
            ax.plot(x, [r[k] for r in rr], color=H.INK, **H.SERIES_STYLE[j + 1], label=k)
        for r in rr:
            drawn.append(dict({"panel": "CD"[p]}, **{k: v for k, v in r.items() if k != "source"}))
        ax.set_xticks(range(len(LUMBAR)))
        ax.set_xticklabels(LUMBAR)
        ax.set_ylabel(ratio)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.55 * (hi - lo))
        ax.legend(loc="upper left", fontsize=6.2, ncol=2)
        H.letter(ax, "CD"[p], "the canal over the body" if p == 0 else "the canal's shape")
    fig.tight_layout(h_pad=2.0)
    H.write_csv(out, "fig3_structure", drawn)
    return H.save(fig, out, "fig3_structure", (
        "What the means and SDs do not test. A, the canal's correlations with the body, synthetic "
        "against Griffith's 1,080 CTs, his sexes apart and together; B, the share of the body's sex "
        "difference each measure carries (the generator scales all alike); C and D, two ratios by "
        "level against the papers that print them."))


# ----- figure 4: the state space -----------------------------------------------------------------

def axis_points(rows: List[dict], axis: str) -> List[dict]:
    """The generator's own point and every point that moves `axis` alone, in order of the axis."""
    gen = next(r for r in rows if r["name"] == "generator")
    pts = [gen] + [r for r in rows if r["name"].startswith(axis + "=")]
    return sorted(pts, key=lambda r: num(r[axis]))


def fig_state_space(records: str, out: str) -> List[str]:
    plt = H.style()
    rows = read_csv(records, "state_space.csv")
    grid = read_csv(records, "grid.csv")
    fig, axes = plt.subplots(2, 3, figsize=(10.0, 6.2))
    drawn = []

    def line(ax, axis, field, label, si, scale=1.0):
        pts = axis_points(rows, axis)
        x = [num(p[axis]) for p in pts]
        y = [num(p[field]) * scale for p in pts]
        ax.plot(x, y, color=H.INK, **H.SERIES_STYLE[si], label=label)
        g = next(p for p in pts if p["name"] == "generator")
        ax.plot([num(g[axis])], [num(g[field]) * scale], marker="o", markersize=8, markerfacecolor="none",
                markeredgecolor=H.INK, linestyle="none")
        drawn.extend({"axis": axis, "value": xi, "series": label, "y": yi} for xi, yi in zip(x, y))

    a = axes[0, 0]
    line(a, "scale_sd", "sd_ratio_true", "true values", 0)
    line(a, "scale_sd", "sd_ratio_measured", "as a CT reads them", 1)
    a.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
    a.set_xlabel("SD of the shared size, scale_sd")
    a.set_ylabel("median SD over the papers'")
    a.legend(loc="upper left")
    H.letter(a, "A", "the shared size")
    b = axes[0, 1]
    line(b, "sd_scale", "sd_ratio_true", "true values", 0)
    line(b, "sd_scale", "sd_ratio_measured", "as a CT reads them", 1)
    b.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
    b.set_xlabel("Panjabi's SDs multiplied by, sd_scale")
    b.set_ylabel("median SD over the papers'")
    H.letter(b, "B", "the SDs' scale")
    c = axes[0, 2]
    line(c, "rho", "neighbour_r", "rho, between levels", 0)
    line(c, "phi", "neighbour_r", "phi, along the column", 1)
    c.set_xlabel("correlation set in the generator")
    c.set_ylabel("correlation of neighbouring levels")
    c.set_ylim(0, 1)
    c.legend(loc="upper left")
    H.letter(c, "C", "neighbouring levels")
    d = axes[1, 0]
    pairs = [k for k in rows[0] if k.startswith("griffith ")]
    for j, k in enumerate(pairs):
        line(d, "r_between", k, k.replace("griffith ", "").replace("~", " with ").replace("_", " "), j)
    d.set_xlabel("correlation between measures, r_between")
    d.set_ylabel("correlation of subject means")
    d.set_ylim(0, 1)
    d.legend(loc="lower right", fontsize=6.5)
    H.letter(d, "D", "between measures")
    e = axes[1, 1]
    for j, ind in enumerate(("any", "box", "convex", "sign")):
        line(e, "sd_scale", "qi vertebra " + ind, ind, j, 100.0)
    e.set_xlabel("Panjabi's SDs multiplied by, sd_scale")
    e.set_ylabel("vertebrae flagged (%)")
    e.legend(loc="upper left")
    H.letter(e, "E", "quality against the SDs' scale")
    f = axes[1, 2]
    best_rho = num(grid[0]["rho"])
    for j, sc in enumerate(sorted({num(g["scale_sd"]) for g in grid})):
        pts = sorted([g for g in grid if num(g["scale_sd"]) == sc and num(g["rho"]) == best_rho
                      and num(g["r_between"]) == num(grid[0]["r_between"])], key=lambda g: num(g["sd_scale"]))
        if not pts:
            continue
        x = [num(g["sd_scale"]) for g in pts]
        y = [num(g["distance"]) for g in pts]
        f.plot(x, y, color=H.INK, **H.SERIES_STYLE[j], label="scale_sd %g" % sc)
        drawn.extend({"axis": "grid", "scale_sd": sc, "sd_scale": xi, "distance": yi, "rho": best_rho,
                      "r_between": num(grid[0]["r_between"])} for xi, yi in zip(x, y))
    f.plot([num(grid[0]["sd_scale"])], [num(grid[0]["distance"])], marker="*", markersize=10, color=H.INK, linestyle="none",
           label="nearest point", zorder=5)
    past = sorted((e for e in read_csv(records, "grid_edges.csv") if e["axis"] == "sd_scale"), key=lambda e: num(e["sd_scale"]))
    if past:
        x = [num(e["sd_scale"]) for e in past] + [num(grid[0]["sd_scale"])]
        y = [num(e["distance"]) for e in past] + [num(grid[0]["distance"])]
        f.plot(x, y, color=H.GREY, linestyle=":", marker="o", markerfacecolor="white", markeredgecolor=H.GREY,
               label="past the grid's edge")
        drawn.extend({"axis": "past the grid", "scale_sd": num(e["scale_sd"]), "sd_scale": num(e["sd_scale"]),
                      "distance": num(e["distance"]), "rho": num(e["rho"]), "r_between": num(e["r_between"])} for e in past)
    f.set_xlabel("sd_scale (rho %g, r_between %g)" % (best_rho, num(grid[0]["r_between"])))
    f.set_ylabel("distance from the papers")
    f.legend(loc="upper left", fontsize=6.5)
    H.letter(f, "F", "the grid")
    fig.tight_layout(h_pad=2.0)
    H.write_csv(out, "fig4_state_space", drawn)
    return H.save(fig, out, "fig4_state_space", (
        "The generator's state space, one axis at a time from its own point (circled), and the grid "
        "searched for the point nearest the papers: the squared log SD ratio plus the mean squared "
        "distance from Griffith's four correlations; in F, grey, past the grid's lowest sd_scale."))


# ----- figure 5: naming ------------------------------------------------------------------------

def fig_naming(records: str, out: str) -> List[str]:
    plt = H.style()
    rows = read_csv(records, "naming.csv")
    settings = []
    for r in rows:
        if r["setting"] not in settings:
            settings.append(r["setting"])
    widths = sorted({int(num(r["width"])) for r in rows})
    fig, axes = plt.subplots(1, len(widths), figsize=(10.0, 3.6), sharey=False)
    drawn = []
    for p, (ax, w) in enumerate(zip(axes, widths)):
        for j, rule in enumerate(("generator's rule", "rule matched")):
            xs, ys, es = [], [], []
            for i, s in enumerate(settings):
                got = [r for r in rows if r["setting"] == s and r["rule"] == rule and int(num(r["width"])) == w]
                if rule == "rule matched" and got and got[0].get("rule_ignores"):
                    continue    # no rule holds phi or r_between: the matched rule is the generator's, drawn once
                if not got:
                    continue
                xs.append(i + dodge(j, 2, 0.24))
                ys.append(100 * num(got[0]["exact"]))
                es.append(100 * 1.96 * num(got[0]["exact_se"]))
                drawn.append({"width": w, "setting": s, "rule": rule, "exact": num(got[0]["exact"]),
                              "exact_se": num(got[0]["exact_se"]), "columns": int(num(got[0]["columns"]))})
            sty = H.SERIES_STYLE[j]
            ax.errorbar(xs, ys, yerr=es, color=H.INK, linestyle="none", marker=sty["marker"],
                        markerfacecolor=sty["markerfacecolor"],
                        label="the generator's rule" if j == 0 else "a rule that knows the setting")
        ax.set_xticks(range(len(settings)))
        ax.set_xticklabels(settings, rotation=90, fontsize=6.5)
        ax.set_ylabel("named exactly (%)")
        H.letter(ax, chr(65 + p), "%d bod%s seen" % (w, "y" if w == 1 else "ies"))
        if p == 0:
            ax.legend(loc="lower left", fontsize=6.5)
    fig.tight_layout()
    H.write_csv(out, "fig5_naming", drawn)
    return H.save(fig, out, "fig5_naming", (
        "Naming by the exact rule on the seven SPINEPS measures, with the CT's errors, at points of the "
        "state space: the rule built for the generator against one that knows the setting, left out "
        "where no rule holds the setting whole (the generator, phi, r_between, the nearest point, "
        "whose rule ignores r_between). Bars are 95% intervals over the columns."))


# ----- figure 6: power -------------------------------------------------------------------------

def fig_power(records: str, out: str) -> List[str]:
    plt = H.style()
    cells = read_csv(records, "power_cells.csv")
    pw = read_json(records, "power.json")
    pn = read_csv(records, "power_naming.csv")
    fig, axes = plt.subplots(2, 3, figsize=(10.0, 6.8))
    drawn = []
    a = axes[0, 0]
    measures = sorted({c["measure"] for c in cells}, key=lambda m: (-sum(1 for c in cells if c["measure"] == m), m))
    for i, m in enumerate(measures):
        fs = [num(c["f_panjabi"]) for c in cells if c["measure"] == m]
        a.plot([i + dodge(j % 5, 5, 0.08) for j in range(len(fs))], fs, linestyle="none", marker="o", markersize=3,
               markerfacecolor="white", color=H.INK)
        drawn.extend({"panel": "A", "measure": m, "f_panjabi": f} for f in fs)
    new = pw["spread"]["main"]["all"]["f_panjabi"]["median"]
    old = pw["old_part_b"]["median_f"]
    cal = pw["calibrated_median_f"]["main"]["panjabi"]["calibrated_median"]
    a.axhline(new, color=H.INK, linestyle="-", linewidth=0.9, label="39 papers, median %.2f" % new)
    a.axhline(cal, color=H.INK, linestyle="-.", linewidth=0.9, label="the same, calibrated for few series, %.2f" % cal)
    a.axhline(old, color=H.INK, linestyle="--", linewidth=0.9, label="part B before, median %.2f" % old)
    a.set_xticks(range(len(measures)))
    a.set_xticklabels([SHORT.get(m, m) for m in measures], rotation=90)
    a.set_ylabel("spread between series / Panjabi's SD")
    a.set_ylim(0, 1.55 * max(num(c["f_panjabi"]) for c in cells))
    a.legend(loc="upper right", fontsize=6.5)
    H.letter(a, "A", "part B again")
    arms = []
    for r in pn:
        if r["arm"] not in arms:
            arms.append(r["arm"])
    widths = sorted({int(num(r["width"])) for r in pn})
    for p, (ax, field, ylabel) in enumerate(((axes[0, 1], "loss", "points lost against its own table"),
                                             (axes[0, 2], "precision", "right when it answers (%)"))):
        for j, arm in enumerate(arms):
            ys, lo, hi = [], [], []
            for w in widths:
                v = [num(r[field]) for r in pn if r["arm"] == arm and int(num(r["width"])) == w]
                v = [x * (100 if field == "precision" else 1) for x in v if finite(x)]
                mean = sum(v) / len(v) if v else float("nan")
                ys.append(mean)
                lo.append(mean - min(v) if v else float("nan"))
                hi.append(max(v) - mean if v else float("nan"))
                drawn.append({"panel": "BC"[p], "arm": arm, "width": w, field: mean, "tables": len(v),
                              "min": min(v) if v else float("nan"), "max": max(v) if v else float("nan")})
            sty = H.SERIES_STYLE[j % len(H.SERIES_STYLE)]
            ax.errorbar([w * math.exp(dodge(j, len(arms), 0.05)) for w in widths], ys, yerr=[lo, hi], color=H.INK,
                        label=arm, **sty)
        ax.set_xscale("log")
        ax.set_xticks(widths)
        ax.set_xticklabels([str(w) for w in widths])
        ax.set_xlabel("bodies seen")
        ax.set_ylabel(ylabel)
        H.letter(ax, "BC"[p], "part C again" if p == 0 else "what it says, when it says it")
    handles, labels = axes[0, 1].get_legend_handles_labels()
    tables = max(int(num(r["table"])) for r in pn) + 1
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=6.5, bbox_to_anchor=(0.5, -0.01),
               title="B and C: the rule's table (bars: the range over its %d tables)" % tables, title_fontsize=6.5)
    gold = pw["gold"]
    n = [g["persons"] for g in gold]
    d = axes[1, 0]
    d.plot(n, [g["least_mean_shift_one_cell"] for g in gold], color=H.INK, **H.SERIES_STYLE[0], label="one cell")
    d.plot(n, [g["least_mean_shift_154_cells"] for g in gold], color=H.INK, **H.SERIES_STYLE[1],
           label="one of the seven's 154 cells, Bonferroni")
    d.plot(n, [g["against_panjabi_12_least_mean_shift"] for g in gold], color=H.INK, **H.SERIES_STYLE[2],
           label="against Panjabi's 12 as a sample (Welch)")
    e = axes[1, 1]
    e.plot(n, [g["least_sd_ratio"] for g in gold], color=H.INK, **H.SERIES_STYLE[0], label="least SD ratio found")
    e.plot(n, [g["against_panjabi_12_least_sd_ratio"] for g in gold], color=H.INK, **H.SERIES_STYLE[1],
           label="against Panjabi's 12 as a sample (F)")
    e.plot(n, [1 + g["neighbour_r_half_width"] for g in gold], color=H.INK, **H.SERIES_STYLE[2],
           label="1 + half-width of a neighbour r of 0.5")
    for ax, ticks, where in ((d, (0.05, 0.1, 0.2, 0.5, 1, 2), "lower left"), (e, (1, 1.25, 1.5, 2, 2.5), "upper right")):
        ax.axvline(159, color=H.GREY, linewidth=0.8, linestyle=":")
        ax.set_xscale("log")
        log_ticks(ax, ticks)
        ax.set_xlabel("persons with whole spines")
        ax.legend(loc=where, fontsize=6.5)
    d.set_ylabel("least mean shift found (person SDs)")
    e.set_ylabel("ratio, or 1 + half-width")
    H.letter(d, "D", "what the gold tier can test")
    H.letter(e, "E", "spread and correlation")
    f = axes[1, 2]
    order = [p["state"] for p in read_json(records, "references.json")["prevalence"]]
    keys = sorted((k for k in gold[0] if k.startswith("expected: ")), key=lambda k: order.index(k[len("expected: "):]))
    for j, k in enumerate(keys):
        f.plot(n, [g[k] for g in gold], color=H.INK, **H.SERIES_STYLE[j], label=k.replace("expected: ", ""))
    f.axvline(159, color=H.GREY, linewidth=0.8, linestyle=":")
    f.set_xscale("log")
    f.set_yscale("log")
    f.set_xlabel("persons with whole spines")
    f.set_ylabel("columns expected")
    f.set_ylim(top=1000)
    f.legend(loc="upper left", fontsize=5.5)
    H.letter(f, "F", "anomalies to expect")
    for g in gold:
        drawn.append(dict({"panel": "DEF"}, **g))
    fig.tight_layout(rect=(0, 0.07, 1, 1), h_pad=2.0)
    H.write_csv(out, "fig6_power", drawn)
    return H.save(fig, out, "fig6_power", (
        "The power calculations rerun. A, the REML spread between published series over Panjabi's SD, "
        "cell by cell; B and C, the exact rule built on tables moved as the papers disagree; D to F, "
        "what whole spines can test against the table taken as exact, and against Panjabi's twelve "
        "as a sample (two-sided, 5%, 80% power; 159 marked)."))


# ----- figure 7: quality -----------------------------------------------------------------------

def fig_quality(records: str, out: str) -> List[str]:
    plt = H.style()
    qi = read_json(records, "qi.json")
    levels = qi["levels"]
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.4))
    drawn = []
    a = axes[0, 0]
    typ = [t for t in qi["typical"] if t["measures"] == "pool"]
    for j, s in enumerate(SETTINGS):
        t = next(x for x in typ if x["setting"] == s)
        ys = [100 * t["vertebra " + k] for k in INDICATORS]
        sty = H.SERIES_STYLE[j]
        a.plot(range(len(INDICATORS)), ys, color=H.INK, label=SETTING_LABEL[s], **sty)
        drawn.extend({"panel": "A", "setting": s, "indicator": k, "vertebrae": y / 100, "persons": t["person " + k]}
                     for k, y in zip(INDICATORS, ys))
    a.set_xticks(range(len(INDICATORS)))
    a.set_xticklabels(INDICATORS, rotation=30, ha="right", fontsize=7)
    a.set_ylabel("vertebrae flagged (%)")
    a.set_ylim(0, 100)
    a.legend(loc="upper left", fontsize=6.5)
    H.letter(a, "A", "each indicator, by setting")
    b = axes[0, 1]
    box = qi["box"]["generator"]
    for j, (area, v) in enumerate(sorted((k, v) for k, v in box.items() if not k.startswith("facet"))):
        ys = [100 * x for x in v["over_box"]]
        b.plot(range(len(levels)), ys, color=H.INK, label=NAMES.get(area.split(":")[0], area), **H.SERIES_STYLE[j])
        drawn.extend({"panel": "B", "area": area, "level": lv, "over_box": y / 100, "k_mean": k, "k_sd": s}
                     for lv, y, k, s in zip(levels, ys, v["k_mean"], v["k_sd"]))
    b.set_xticks(range(len(levels)))
    b.set_xticklabels(levels, rotation=90)
    b.set_ylabel("area over its own box (%)")
    b.set_ylim(0, 1.5 * max(100 * x for k, v in box.items() if not k.startswith("facet") for x in v["over_box"]))
    b.legend(loc="upper center", fontsize=6.5, ncol=2)
    H.letter(b, "B", "the box, by level (generator; facets in the CSV)")
    drawn.extend({"panel": "B", "area": area, "level": lv, "over_box": o, "k_mean": k, "k_sd": s}
                 for area, v in sorted(box.items()) if area.startswith("facet")
                 for lv, o, k, s in zip(levels, v["over_box"], v["k_mean"], v["k_sd"]))
    c = axes[1, 0]
    tan = [r for r in read_json(records, "structure.json")["ratios"] if r["ratio"] == "canal area / (width x depth)"]
    tan_x = [levels.index(r["level"]) for r in tan]
    c.plot(tan_x, [r["tan2004"] for r in tan], color=H.INK, linestyle="none", marker="D", markerfacecolor="white",
           label="Tan 2004, his ratio of means")
    drawn.extend({"panel": "C", "setting": "tan2004, ratio of means", "level": r["level"], "k_mean": r["tan2004"]} for r in tan)
    g = qi["box"]["generator"]["canal_area"]
    c.fill_between(range(len(levels)), [m - s for m, s in zip(g["k_mean"], g["k_sd"])],
                   [m + s for m, s in zip(g["k_mean"], g["k_sd"])], color="#bdbdbd", alpha=0.6, linewidth=0,
                   label="generator, $\\pm$ 1 SD")
    for j, s in enumerate(SETTINGS):
        v = qi["box"][s]["canal_area"]
        c.plot(range(len(levels)), v["k_mean"], color=H.INK, label=SETTING_LABEL[s], **H.SERIES_STYLE[j])
        drawn.extend({"panel": "C", "setting": s, "level": lv, "k_mean": m, "k_sd": sd}
                     for lv, m, sd in zip(levels, v["k_mean"], v["k_sd"]))
    c.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
    c.set_xticks(range(len(levels)))
    c.set_xticklabels(levels, rotation=90)
    c.set_ylabel("canal area / (width x depth)")
    c.set_ylim(0.4, 1.35)
    c.legend(loc="upper left", fontsize=6.5, ncol=2)
    H.letter(c, "C", "the canal's shape factor")
    d = axes[1, 1]
    ph = qi["phenotypes"]
    for j, k in enumerate(("any", "any but floor", "box", "convex", "sign or inside")):
        d.plot(range(len(ph)), [100 * p["vertebra " + k] for p in ph], color=H.INK, label=k, **H.SERIES_STYLE[j])
    drawn.extend(dict({"panel": "D"}, **p) for p in ph)
    d.set_xticks(range(len(ph)))
    d.set_xticklabels([p["phenotype"].replace("_", " ") for p in ph], rotation=90, fontsize=7)
    d.set_ylabel("vertebrae flagged (%)")
    d.set_ylim(0, 100)
    d.legend(loc="upper center", fontsize=6.5, ncol=3)
    H.letter(d, "D", "the six phenotypes (generator)")
    fig.tight_layout(h_pad=2.0)
    H.write_csv(out, "fig7_quality", drawn)
    return H.save(fig, out, "fig7_quality", (
        "Quality indicators of synthetic vertebrae: a length or area at or below zero (sign), a measured value "
        "at the floor, an area larger than its own width times depth (box), an end-plate under half of "
        "it (convex), a canal wider than its transverse processes (inside). Sign and inside no anatomy "
        "can fail; box and convex hold under allowances."))


# ----- figure 8: what the generator assumes ------------------------------------------------------

def fig_assumptions(records: str, out: str) -> List[str]:
    plt = H.style()
    ref = read_json(records, "references.json")
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 3.8), gridspec_kw={"width_ratios": [1.3, 1.0]})
    drawn = []
    errs = [e for e in ref["errors"] if e["unit"] == "mm"]
    for i, e in enumerate(errs):
        a.plot([i, i], [e["low"], e["high"]], color=H.INK, linewidth=2.2)
        a.plot([i], [(e["low"] + e["high"]) / 2], marker="o", markerfacecolor="white", color=H.INK, linestyle="none")
        drawn.append(dict({"panel": "A"}, **e))
    a.axhline(1.0, color=H.INK, linestyle="--", linewidth=0.9, label="the generator's error for a length, 1 mm")
    a.set_xticks(range(len(errs)))
    a.set_xticklabels(["%s\n(%s)" % (e["what"], e["modality"]) for e in errs], rotation=90, fontsize=6.5)
    a.set_ylabel("error SD of one reading (mm)")
    a.set_ylim(0, 1.4)
    a.legend(loc="upper right", fontsize=6.5)
    H.letter(a, "A", "measurement error, papers' range")
    prev = ref["prevalence"]
    for i, p in enumerate(prev):
        if p["papers"] is not None and "ceiling" in p["state"]:
            b.plot([i], [100 * p["papers"]], marker="v", markerfacecolor="white", color=H.INK, linestyle="none",
                   label="papers, a ceiling")
        elif p["papers"] is not None:
            pt = p["papers"]
            b.errorbar([i], [100 * pt], yerr=[[100 * (pt - p["low"])], [100 * (p["high"] - pt)]], color=H.INK,
                       linestyle="none", marker="o", markerfacecolor="white",
                       label="papers, Wilson 95% interval" if i == 0 else None)
        elif p["high"] is not None:
            b.plot([i], [100 * p["high"]], marker="v", markerfacecolor="white", color=H.INK, linestyle="none")
        else:
            b.text(i, 0.3, "no count", rotation=90, ha="center", va="bottom", fontsize=6.5, style="italic")
        if p["generator_share"] is not None:
            b.plot([i - 0.2], [100 * p["generator_share"]], marker="s", color=H.INK, linestyle="none",
                   label="model.py's equal shares" if i == 0 else None)
        if p["chain_weight"] is not None:
            b.plot([i + 0.2], [100 * p["chain_weight"]], marker="D", markerfacecolor="white", color=H.INK, linestyle="none",
                   label="the chain's stated weight" if i == 0 else None)
        drawn.append(dict({"panel": "B"}, **p))
    b.set_yscale("log")
    b.set_xticks(range(len(prev)))
    b.set_xticklabels([re.sub(r" \([^)]*\)", "", p["state"]) for p in prev], rotation=90, fontsize=6.5)
    b.set_ylabel("columns (%)")
    b.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=6)
    H.letter(b, "B", "how often a column is not typical")
    fig.tight_layout()
    H.write_csv(out, "fig8_assumptions", drawn)
    return H.save(fig, out, "fig8_assumptions", (
        "Two things the generator assumes, set beside the papers. A, the error of one reading as the "
        "reread's checked error part gives it, two figures from pig bone; B, how often a column carries "
        "each anomaly, from Eisenstein's 443 skeletons and Duman's 517 CTs (the reread's checked priors)."))


FIGURES = (fig_means, fig_spread, fig_structure, fig_state_space, fig_naming, fig_power, fig_quality, fig_assumptions) + FA.FIGURES_ALL


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


DRAWN_BY = ("figures.py", "figures_all.py", "render.py", "synthval/house.py", "../../schwingcheck/figures.py")


def write_index(records: str, out: str, written: Dict[str, List[str]]) -> str:
    """FIGURES.md: the command, the records and the code that drew the figures, each by sha256,
    the commit at drawing time, the abbreviations on the axes, then every figure's caption and
    files."""
    rec = read_json(records, "RECORD.json")
    commit = subprocess.run(["git", "-C", HERE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    lines = ["# Figures", "", "Drawn by `python3 -I figures.py --records %s --out %s` from the records of"
             % (os.path.basename(records.rstrip("/")), os.path.basename(out.rstrip("/"))),
             "`%s` (bordercall %s). Each figure's numbers are its CSV; its caption is its .caption.txt."
             % (rec.get("command", "run.py"), (rec.get("bordercall_commit") or "")[:7]),
             "The three renders are drawn by render.py from the generator itself, seed %d, %d people."
             % (R.SEED, R.PEOPLE), "",
             "Drawn at bordercall %s, from and by:" % commit[:7], "",
             "- %s/RECORD.json, sha256 %s" % (os.path.basename(records.rstrip("/")), sha(os.path.join(records, "RECORD.json")))]
    lines += ["- %s, sha256 %s" % (name.replace("../../", ""), sha(os.path.normpath(os.path.join(HERE, name))))
              for name in DRAWN_BY]
    lines += ["", "Abbreviations on the axes: " + "; ".join("%s %s" % (SHORT[k], NAMES.get(k, k)) for k in SHORT) + ".", ""]
    for name, paths in written.items():
        cap = open(os.path.join(out, name + ".caption.txt"), encoding="ascii").read().strip()
        lines += ["## %s" % name, "", cap, ""]
        for p in sorted(set(paths + [os.path.join(out, name + ".csv")])):
            lines.append("- %s, sha256 %s" % (os.path.basename(p), sha(p)))
        lines.append("")
    path = os.path.join(out, "FIGURES.md")
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write("\n".join(lines))
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--records", default=os.path.join(HERE, "records"))
    ap.add_argument("--out", default=os.path.join(HERE, "figures"))
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    written = {}
    for f in FIGURES:
        paths = f(args.records, args.out)
        written[os.path.splitext(os.path.basename(paths[0]))[0]] = paths
    written.update(R.render_all(args.out))
    print(write_index(args.records, args.out, written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
