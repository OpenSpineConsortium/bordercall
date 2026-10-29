"""The benchmark figures, in the house format for line graphs (schwingcheck.figures): black ink,
serif type, lettered panels, each series told apart by its marker and never by a hue.

Each figure is drawn from a records file beside it and is skipped, with a line saying so, where
that file is not there yet; FIGURES.md names every record and every file of code by sha256."""
from __future__ import annotations

import csv
import glob
import math
import os
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import numpy as np

from schwingcheck import figures as FIG

GRID_STYLE = {"1.0 mm": dict(marker="o", markerfacecolor=FIG.INK), "1.25 mm": dict(marker="o", markerfacecolor="white"),
              "2.5 mm": dict(marker="s", markerfacecolor="white"), "5.0 mm": dict(marker="^", markerfacecolor="white")}
EDGE_STYLE = {"exact": dict(marker="o", markerfacecolor=FIG.INK), "grown one voxel": dict(marker="^", markerfacecolor="white"),
              "shrunk one voxel": dict(marker="v", markerfacecolor="white"), "0004": dict(marker="s", markerfacecolor="white"),
              "0006": dict(marker="D", markerfacecolor="white"), "0010": dict(marker="s", markerfacecolor=FIG.INK)}
REGION_NAMES = {"upper_plate": "upper end-plate", "lower_plate": "lower end-plate", "lateral_wall": "lateral wall",
                "anterior_wall": "anterior wall", "posterior_wall": "posterior wall", "arch": "arch"}
BODY = ("h_ant", "h_mid", "h_post_inset", "h_post", "body_w_mid", "body_d_mid", "endplate", "endplate_depth",
        "endplate_lower", "endplate_lower_depth", "endplate_concavity", "disc_h_ant", "disc_h_mid", "disc_h_post")
POSTERIOR = ("canal_ap_min", "canal_ap_lateral", "canal_ap_lateral_film", "interpedicular", "interpedicular_max",
             "pedicle_w", "pedicle_h", "pedicle_chord", "transverse_width", "lamina_thickness", "interfacet_w_sup",
             "interfacet_w_inf")
ANGLES = ("endplate_incl", "endplate_lower_incl", "wedge", "pedicle_angle_transverse", "pedicle_angle_sagittal",
          "lamina_angle", "spinous_angle", "facet_angle_axial")
PAPER_KEYS = ("h_ant", "h_post", "body_d_mid", "body_w_mid", "endplate", "endplate_depth", "canal_ap_min",
              "interpedicular", "pedicle_w", "disc_h_mid")
PAPER_MARKERS = (dict(marker="s", markerfacecolor="white"), dict(marker="^", markerfacecolor="white"),
                 dict(marker="D", markerfacecolor="white"), dict(marker="v", markerfacecolor="white"))
LEVEL_ORDER = ["C%d" % i for i in range(2, 8)] + ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)]


def read(path: str) -> List[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return math.nan


# ---- the phantom against its truth ---------------------------------------------------------------

def error_rows(rows: List[dict], keys: Sequence[str]) -> List[Tuple[str, str, float, float, float, int]]:
    """Per measure and grid: the median error over tilts and turns, the least and the largest, how many."""
    by = defaultdict(list)
    for r in rows:
        e = num(r["error"])
        if r["key"] in keys and math.isfinite(e):
            by[(r["key"], r["grid"])].append(e)
    return [(k, g, float(np.median(v)), float(min(v)), float(max(v)), len(v)) for (k, g), v in by.items()]


def strip(ax, stats, keys: Sequence[str], styles: Dict[str, dict], unit: str) -> List[str]:
    """One row a measure, one marker a series, a bar from the least to the largest."""
    shown = [k for k in keys if any(s[0] == k for s in stats)]
    names = list(styles)
    for i, k in enumerate(shown):
        for j, g in enumerate(names):
            got = [s for s in stats if s[0] == k and s[1] == g]
            if not got:
                continue
            _, _, med, lo, hi, _ = got[0]
            y = i + (j - (len(names) - 1) / 2) * 0.16
            ax.plot([lo, hi], [y, y], color=FIG.INK, lw=0.7)
            ax.plot([med], [y], linestyle="none", color=FIG.INK, label=g if i == 0 else None, **styles[g])
    ax.axvline(0.0, color=FIG.INK, lw=0.6, linestyle=":")
    ax.set_yticks(range(len(shown)))
    ax.set_yticklabels(shown, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("error, %s (value less truth)" % unit)
    return shown


def fig_phantom(records: str, out: str) -> List[dict]:
    rows = read(os.path.join(records, "phantom-truth.csv"))
    plt = FIG.style()
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 5.2), gridspec_kw=dict(wspace=0.75))
    csv_rows = []
    for ax, (letter, title, keys, unit) in zip(axes, (("A", "Body and discs", BODY, "mm"),
                                                      ("B", "Canal, pedicles, arch", POSTERIOR, "mm"),
                                                      ("C", "Angles", ANGLES, "degrees"))):
        stats = error_rows(rows, keys)
        strip(ax, stats, keys, GRID_STYLE, unit)
        FIG.letter(ax, letter, title)
        csv_rows += [{"panel": letter, "key": k, "grid": g, "median_error": m, "least": lo, "largest": hi, "n": n}
                     for k, g, m, lo, hi, n in stats]
    axes[0].legend(title="slice", loc="lower right")
    cap = ("Each measure on the phantom, L2 to L4 drawn from shapes whose measures are known, less its truth: the "
           "median over three tilts and two grid turns, and a bar from the least to the largest, by slice thickness.")
    FIG.save(fig, out, "phantom-truth", cap)
    FIG.write_csv(out, "phantom-truth", csv_rows)
    return csv_rows


# ---- the mask's edge ---------------------------------------------------------------------------

def fig_maskedge(records: str, out: str) -> None:
    rows = read(os.path.join(records, "maskedge-phantom.csv")) + read(os.path.join(records, "maskedge-ct.csv"))
    plt = FIG.style()
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    regions = list(REGION_NAMES)
    cases = [c for c in EDGE_STYLE if any(r["case"] == c for r in rows)]
    for j, case in enumerate(cases):
        for i, reg in enumerate(regions):
            got = [r for r in rows if r["case"] == case and r["region"] == reg]
            if not got:
                continue
            r = got[0]
            y = i + (j - (len(cases) - 1) / 2) * 0.12
            ax.plot([num(r["q25"]), num(r["q75"])], [y, y], color=FIG.INK, lw=0.7)
            label = ("phantom, " + case) if r["source"] == "phantom" else ("CT " + case)
            ax.plot([num(r["median"])], [y], linestyle="none", color=FIG.INK, label=label if i == 0 else None,
                    **EDGE_STYLE[case])
    ax.axvline(0.0, color=FIG.INK, lw=0.6, linestyle=":")
    ax.set_yticks(range(len(regions)))
    ax.set_yticklabels([REGION_NAMES[r] for r in regions])
    ax.invert_yaxis()
    ax.set_xlabel("bone's half-maximum edge less the mask's surface, mm (positive: the mask stops short)")
    ax.legend(loc="lower right", fontsize=6.5)
    FIG.letter(ax, "A", "Where the mask's surface lies against the bone")
    cap = ("How far the bone's edge in the CT lies beyond the mask's surface, along its normal: the phantom's exact "
           "mask and the mask grown or shrunk by a voxel (median and quartiles over points), and three ENHANCE.PET "
           "studies (over vertebrae).")
    FIG.save(fig, out, "maskedge", cap)
    FIG.write_csv(out, "maskedge", rows)


# ---- thick slices --------------------------------------------------------------------------------

def fig_thicken(records: str, out: str) -> None:
    paths = sorted(glob.glob(os.path.join(records, "thicken-*.csv")))
    rows = [r for p in paths for r in read(p)]
    by = defaultdict(list)
    for r in rows:
        mm = r["note"].split("(")[1].split(" mm")[0] if "(" in r["note"] else ""
        v = num(r["value"])
        if r["key"] in PAPER_KEYS + ("h_mid", "disc_h_ant", "disc_h_post") and math.isfinite(v):
            by[(r["key"], mm)].append(v)
    keys = [k for k in PAPER_KEYS + ("h_mid", "disc_h_ant", "disc_h_post") if any(kk == k for kk, _ in by)]
    styles = {}
    for mm in sorted({m for _, m in by}, key=float):
        styles[mm] = GRID_STYLE["2.5 mm" if float(mm) < 4 else "5.0 mm"]
    stats = [(k, mm, float(np.median(v)), float(np.percentile(v, 25)), float(np.percentile(v, 75)), len(v))
             for (k, mm), v in by.items()]
    plt = FIG.style()
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    strip(ax, stats, keys, styles, "mm")
    ax.set_xlabel("change from the thin scan, mm (median and quartiles over vertebrae)")
    ax.legend(title="slices", loc="lower right", labels=["%s mm" % m for m in styles])
    FIG.letter(ax, "A", "The same studies on thicker slices")
    cap = ("Each measure read again on every second and every fourth slice of three thin ENHANCE.PET studies, as a "
           "clinical 2.5 or 5 mm scan would hold them: the change from the thin scan, median and quartiles over vertebrae.")
    FIG.save(fig, out, "thicken", cap)
    FIG.write_csv(out, "thicken", [dict(zip(("key", "slice", "median", "q25", "q75", "n"), s)) for s in stats])


# ---- ours against the papers -------------------------------------------------------------------

def fig_papers(records: str, out: str) -> None:
    rows = [r for r in read(os.path.join(records, "compare-229.csv")) if r["key"] == r["ours_key"]]
    plt = FIG.style()
    fig, axes = plt.subplots(2, 5, figsize=(12.0, 5.6), gridspec_kw=dict(wspace=0.38, hspace=0.55))
    drawn = []
    for ax, letter, key in zip(axes.ravel(), "ABCDEFGHIJ", PAPER_KEYS):
        mine = [r for r in rows if r["key"] == key and r["sex"] in ("pooled", "")]
        levels = [lv for lv in LEVEL_ORDER if any(r["level"] == lv for r in mine)]
        if not levels:
            ax.axis("off")
            continue
        x = {lv: i for i, lv in enumerate(levels)}
        ours = {}
        for r in mine:
            ours.setdefault(r["level"], (num(r["ours_mean"]), num(r["ours_sd"]), r["ours_n"]))
        xs = [x[lv] for lv in levels]
        ax.errorbar(xs, [ours[lv][0] for lv in levels], yerr=[ours[lv][1] for lv in levels], color=FIG.INK,
                    marker="o", markerfacecolor=FIG.INK, lw=1.0, label="ours")
        papers = sorted({r["paper"] for r in mine}, key=lambda p: -sum(r["paper"] == p for r in mine))[:len(PAPER_MARKERS)]
        for j, paper in enumerate(papers):
            pr = [r for r in mine if r["paper"] == paper]
            px = [x[r["level"]] + 0.15 * (j + 1) for r in pr]
            ax.errorbar(px, [num(r["paper_mean"]) for r in pr], yerr=[num(r["paper_sd"]) for r in pr], color=FIG.INK,
                        linestyle="none", lw=0.7, label=paper, **PAPER_MARKERS[j])
            drawn += [{"key": key, "level": r["level"], "paper": paper, "paper_mean": num(r["paper_mean"]),
                       "paper_sd": num(r["paper_sd"]), "ours_mean": ours[r["level"]][0], "ours_sd": ours[r["level"]][1],
                       "ours_n": ours[r["level"]][2]} for r in pr]
        step = max(1, len(levels) // 6)
        ax.set_xticks(xs[::step])
        ax.set_xticklabels(levels[::step], fontsize=7)
        ax.set_ylabel("mm", fontsize=7)
        ax.legend(fontsize=5.5, loc="best")
        FIG.letter(ax, letter, key)
    cap = ("Ours on the thin ENHANCE.PET studies (mean and standard deviation by level) beside each paper's mean and "
           "standard deviation, the papers with the most levels for each measure; pooled sexes only.")
    FIG.save(fig, out, "papers", cap)
    if drawn:
        FIG.write_csv(out, "papers", drawn)


# ---- all, and the index ------------------------------------------------------------------------

FIGURES = (("phantom-truth", fig_phantom, ("phantom-truth.csv",)),
           ("maskedge", fig_maskedge, ("maskedge-phantom.csv", "maskedge-ct.csv")),
           ("thicken", fig_thicken, ("thicken-*.csv",)),
           ("papers", fig_papers, ("compare-229.csv",)))


def all_figures(records: str, out: str) -> None:
    os.makedirs(out, exist_ok=True)
    used = []
    for name, draw, needs in FIGURES:
        paths = [p for n in needs for p in sorted(glob.glob(os.path.join(records, n)))]
        if len(paths) < len(needs):
            print("%s: skipped, %s not there yet" % (name, ", ".join(needs)))
            continue
        draw(records, out)
        used += paths
        print("%s: drawn" % name)
    index(sorted(set(used)), out)


def index(records: List[str], out: str) -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    code = sorted(glob.glob(os.path.join(here, "*.py"))) + [FIG.__file__]
    lines = ["# The morphometry benchmarks", "", "Drawn by `python -m morphobench figures`.", "", "## Records", ""]
    lines += ["- %s %s" % (os.path.basename(p), FIG.sha256(p)) for p in records]
    lines += ["", "## Code", ""]
    lines += ["- %s %s" % (os.path.relpath(p, os.path.dirname(here)), FIG.sha256(p)) for p in code]
    lines += ["", "## Figures", ""]
    lines += ["- %s" % os.path.basename(p) for p in sorted(glob.glob(os.path.join(out, "*.png")))]
    with open(os.path.join(out, "FIGURES.md"), "w", encoding="ascii", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
