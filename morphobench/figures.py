"""The benchmark figures, in the house format for line graphs (schwingcheck.figures): black ink,
serif type, lettered panels, each series told apart by its marker and never by a hue.

Each figure is drawn from a records file beside it and is skipped, with a line saying so, where
that file is not there yet; FIGURES.md names every record and every file of code by sha256."""
from __future__ import annotations

import csv
import glob
import math
import os
import re
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
PAPER_KEYS = ("h_ant", "h_post", "body_d_mid", "body_w_mid", "endplate", "endplate_depth", "canal_ap",
              "interpedicular", "pedicle_w", "disc_h_mid")
NAMES = {"h_ant": "anterior height", "h_mid": "middle height", "h_post_inset": "posterior height, inset",
         "h_post": "posterior height", "body_w_mid": "waist width", "body_d_mid": "waist depth",
         "endplate": "upper end-plate width", "endplate_depth": "upper end-plate depth",
         "endplate_lower": "lower end-plate width", "endplate_lower_depth": "lower end-plate depth",
         "endplate_concavity": "end-plate concavity", "disc_h_ant": "disc height, anterior",
         "disc_h_mid": "disc height, middle", "disc_h_post": "disc height, posterior",
         "canal_ap_min": "least canal depth", "canal_ap": "canal depth at the pedicles",
         "canal_ap_lateral": "lateral canal depth", "canal_ap_lateral_film": "canal depth to the film line",
         "interpedicular": "interpedicular distance", "interpedicular_max": "greatest interpedicular",
         "pedicle_w": "pedicle width", "pedicle_h": "pedicle height", "pedicle_chord": "pedicle chord",
         "transverse_width": "transverse span", "lamina_thickness": "lamina thickness",
         "interfacet_w_sup": "interfacet width, superior", "interfacet_w_inf": "interfacet width, inferior",
         "endplate_incl": "upper end-plate inclination", "endplate_lower_incl": "lower end-plate inclination",
         "wedge": "wedge angle", "pedicle_angle_transverse": "pedicle transverse angle",
         "pedicle_angle_sagittal": "pedicle sagittal angle", "lamina_angle": "lamina angle",
         "spinous_angle": "spinous angle", "facet_angle_axial": "facet axial angle"}
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
            first = not any(s[1] == g for s in stats if s[0] in shown[:i])
            ax.plot([med], [y], linestyle="none", color=FIG.INK, label=g if first else None, **styles[g])
    ax.axvline(0.0, color=FIG.INK, lw=0.6, linestyle=":")
    ax.set_yticks(range(len(shown)))
    ax.set_yticklabels([NAMES.get(k, k) for k in shown], fontsize=7)
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


# ---- the disc in the CT --------------------------------------------------------------------------

DISC_REGIONS = ("L2-L3", "L3-L4", "cervical", "thoracic", "lumbar")
DISC_NAMES = {"L2-L3": "phantom L2-L3", "L3-L4": "phantom L3-L4", "cervical": "cervical discs",
              "thoracic": "thoracic discs", "lumbar": "lumbar discs"}


def fig_disc(records: str, out: str) -> None:
    rows = read(os.path.join(records, "disc-phantom.csv")) + read(os.path.join(records, "disc-ct.csv"))
    plt = FIG.style()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.5, 3.9), gridspec_kw=dict(wspace=0.55))
    regions = [r for r in DISC_REGIONS if any(x["region"] == r for x in rows)]
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
            ax.plot([num(r["median"])], [y], linestyle="none", color=FIG.INK, label=label if label not in
                    ax.get_legend_handles_labels()[1] else None, **EDGE_STYLE[case])
    ax.axvline(0.0, color=FIG.INK, lw=0.6, linestyle=":")
    ax.set_yticks(range(len(regions)))
    ax.set_yticklabels([DISC_NAMES[r] for r in regions])
    ax.invert_yaxis()
    ax.set_xlabel("masks' gap less the CT's disc, mm (negative: the masks take in disc)")
    ax.set_xlim(right=max(ax.get_xlim()[1], 3.2))
    ax.legend(loc="lower right", fontsize=6.5)
    FIG.letter(ax, "A", "The gap the masks leave against the disc in the CT")
    real = [r for r in rows if r["source"] != "phantom"]
    studies = sorted({r["case"] for r in real})
    ct_regions = [r for r in ("cervical", "thoracic", "lumbar") if any(x["region"] == r for x in real)]
    for j, study in enumerate(studies):
        for i, reg in enumerate(ct_regions):
            got = [r for r in real if r["case"] == study and r["region"] == reg]
            if not got:
                continue
            y = i + (j - (len(studies) - 1) / 2) * 0.16
            gap, ct = num(got[0]["masks_gap"]), num(got[0]["ct_height"])
            bx.plot([gap, ct], [y, y], color=FIG.INK, lw=0.7)
            bx.plot([ct], [y], linestyle="none", color=FIG.INK, marker="o", markerfacecolor=FIG.INK,
                    label="the CT's disc" if (i, j) == (0, 0) else None)
            bx.plot([gap], [y], linestyle="none", color=FIG.INK, marker="o", markerfacecolor="white",
                    label="the masks' gap" if (i, j) == (0, 0) else None)
    bx.set_yticks(range(len(ct_regions)))
    bx.set_yticklabels(["%s discs" % r for r in ct_regions])
    bx.invert_yaxis()
    bx.set_xlabel("height at the disc's middle, mm (one row a study)")
    bx.legend(loc="upper right", fontsize=6.5)
    FIG.letter(bx, "B", "Each study's discs, the CT and the masks")
    cap = ("Each disc read along 25 lines through the middle of the body below: the CT's disc between the two "
           "cortices' half-maximum edges against the gap the masks leave, on the phantom's exact, grown and "
           "shrunk masks and three ENHANCE.PET studies (medians over discs read on eight lines or more).")
    FIG.save(fig, out, "disc", cap)
    FIG.write_csv(out, "disc", rows)


# ---- thick slices --------------------------------------------------------------------------------

THICK_KEYS = PAPER_KEYS + ("h_mid", "disc_h_ant", "disc_h_post")


def asked_of(note: str) -> str:
    """The thickness a thicken row was asked for, from its note ('every 2 slices (2.50 mm, asked
    2.50) ...'): the slices a study's own spacing gives differ from study to study, the ask does not."""
    got = re.search(r"asked ([0-9.]+)", note)
    return "%.1f mm" % float(got.group(1)) if got else "?"


def thicken_summary(rows: List[dict]) -> List[dict]:
    """morphometry thicken's per-vertebra rows as aggregates: per measure and thickness asked, the
    median change from the thin scan and its quartiles over vertebrae, and how many studies."""
    by = defaultdict(list)
    studies = defaultdict(set)
    for r in rows:
        v = num(r["value"])
        if r["key"] in THICK_KEYS and math.isfinite(v):
            key = (r["key"], asked_of(r["note"]))
            by[key].append(v)
            studies[key].add(r["study"])
    return [{"key": k, "slice": mm, "median": float(np.median(v)), "q25": float(np.percentile(v, 25)),
             "q75": float(np.percentile(v, 75)), "vertebrae": len(v), "studies": len(studies[(k, mm)])}
            for (k, mm), v in sorted(by.items(), key=lambda kv: (THICK_KEYS.index(kv[0][0]), kv[0][1]))]


def fig_thicken(records: str, out: str) -> None:
    rows = read(os.path.join(records, "thicken.csv"))
    keys = [k for k in THICK_KEYS if any(r["key"] == k for r in rows)]
    slices = sorted({r["slice"] for r in rows}, key=lambda m: float(m.split()[0]))
    styles = {mm: GRID_STYLE["2.5 mm" if float(mm.split()[0]) < 4 else "5.0 mm"] for mm in slices}
    stats = [(r["key"], r["slice"], num(r["median"]), num(r["q25"]), num(r["q75"]), int(r["vertebrae"])) for r in rows]
    plt = FIG.style()
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    strip(ax, stats, keys, styles, "mm")
    ax.set_xlabel("change from the thin scan, mm (median and quartiles over vertebrae)")
    ax.legend(title="slices asked", loc="lower right")
    FIG.letter(ax, "A", "The same studies on thicker slices")
    cap = ("Each measure read again on three thin ENHANCE.PET studies keeping one slice in three or four (2.8 to "
           "3.0 mm apart, asked 2.5) or in five or seven (4.9 to 5.0 mm), as a clinical scan would hold them: the "
           "change from the thin scan, median and quartiles over vertebrae.")
    FIG.save(fig, out, "thicken", cap)
    FIG.write_csv(out, "thicken", rows)


# ---- what the change of frame moved ----------------------------------------------------------------

REGION_STYLE = {"cervical": dict(marker="^", markerfacecolor="white"), "thoracic": dict(marker="s", markerfacecolor="white"),
                "lumbar": dict(marker="o", markerfacecolor=FIG.INK)}


def fig_axis(records: str, out: str) -> None:
    shift = read(os.path.join(records, "axis-shift.csv"))
    turn = read(os.path.join(records, "axis-turn.csv"))
    plt = FIG.style()
    fig, axes = plt.subplots(1, 4, figsize=(13.5, 5.2), gridspec_kw=dict(wspace=0.7, width_ratios=[1.15, 1, 1, 1]))
    ax = axes[0]
    levels = [r["level"] for r in turn if r["level"] in LEVEL_ORDER]
    x = np.arange(len(levels))
    med = [num(r["median_deg"]) for r in turn if r["level"] in levels]
    lo = [num(r["p10_deg"]) for r in turn if r["level"] in levels]
    hi = [num(r["p90_deg"]) for r in turn if r["level"] in levels]
    for xi, a, b in zip(x, lo, hi):
        ax.plot([xi, xi], [a, b], color=FIG.INK, lw=0.7)
    ax.plot(x, med, color=FIG.INK, marker="o", markerfacecolor="white", label="median, 10th to 90th percentile")
    ax.set_xticks(x)
    ax.set_xticklabels(levels, fontsize=6.5, rotation=90)
    ax.set_ylabel("turn from the column's line onto the vertebra's own axis, degrees")
    ax.legend(loc="upper center", fontsize=6.5)
    FIG.letter(ax, "A", "The turn, by level")
    stats = [(r["key"], r["region"], num(r["median_shift"]), num(r["p10_shift"]), num(r["p90_shift"]), int(r["n"]))
             for r in shift if r["region"] in REGION_STYLE]
    for ax, (letter, title, keys, unit) in zip(axes[1:], (("B", "Body and discs", BODY, "mm"),
                                                          ("C", "Canal, pedicles, arch", POSTERIOR, "mm"),
                                                          ("D", "Angles", ANGLES, "degrees"))):
        strip(ax, stats, keys, REGION_STYLE, unit)
        ax.set_xlabel("shift, %s (own axis less column's line)" % unit)
        FIG.letter(ax, letter, title)
    axes[1].legend(loc="lower right", fontsize=6.5)
    cap = ("What turning each vertebra's frame from the column's line onto its own axis moved, over the thin-slice "
           "ENHANCE.PET studies: the turn by level (A), and each measure's shift, median and 10th to 90th "
           "percentiles over vertebrae, by region (B to D).")
    FIG.save(fig, out, "axis-shift", cap)
    FIG.write_csv(out, "axis-shift", shift)


# ---- ours against the papers -------------------------------------------------------------------

def level_rank(level: str) -> float:
    """A level's place down the column, a disc's half way between its two vertebrae."""
    ends = level.split("-")
    if ends[0] not in LEVEL_ORDER:
        return math.inf
    return LEVEL_ORDER.index(ends[0]) + (0.5 if len(ends) == 2 else 0.0)


def combined(rows: List[dict]) -> Tuple[float, float, float]:
    """Several of one paper's rows for one level (its sexes, its decades) as one mean and standard
    deviation over all their people, the spread between the rows' means counted in."""
    ns = np.array([num(r["paper_n"]) if math.isfinite(num(r["paper_n"])) else 1.0 for r in rows])
    ms = np.array([num(r["paper_mean"]) for r in rows])
    sds = np.array([num(r["paper_sd"]) for r in rows])
    keep = np.isfinite(ms)
    ns, ms, sds = ns[keep], ms[keep], np.where(np.isfinite(sds[keep]), sds[keep], 0.0)
    if not len(ms):
        return math.nan, math.nan, 0.0
    mean = float(np.sum(ns * ms) / np.sum(ns))
    var = float(np.sum(ns * (sds ** 2 + (ms - mean) ** 2)) / np.sum(ns))
    return mean, math.sqrt(var), float(np.sum(ns))


def paper_points(rows: List[dict]) -> Dict[Tuple[str, str], Tuple[float, float, float]]:
    """Each paper's adult human mean at each level: its pooled row where compare made one, else its
    rows for both sexes together, else its rows by sex, combined; rows compare left out (children,
    another species, a disease, a sample chosen by size) never."""
    by = defaultdict(list)
    for r in rows:
        if not r["left_out"]:
            by[(r["paper"], r["level"])].append(r)
    out = {}
    for key, got in by.items():
        for sexes in (("pooled",), ("all", "not stated", ""), ("female", "male")):
            pick = [r for r in got if r["sex"] in sexes]
            if pick:
                out[key] = combined(pick)
                break
    return out


def fig_papers(records: str, out: str) -> None:
    rows = [r for r in read(os.path.join(records, "compare-229.csv")) if r["key"] == r["ours_key"]]
    shown = [k for k in PAPER_KEYS if any(r["key"] == k and not r["left_out"] for r in rows)]
    plt = FIG.style()
    ncol = 5
    nrow = max(1, math.ceil(len(shown) / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(12.0, 3.9 * nrow), gridspec_kw=dict(wspace=0.38, hspace=1.05),
                             squeeze=False)
    drawn = []
    for ax in axes.ravel()[len(shown):]:
        ax.axis("off")
    for ax, letter, key in zip(axes.ravel(), "ABCDEFGHIJKL", shown):
        mine = [r for r in rows if r["key"] == key]
        points = paper_points(mine)
        ours = {}
        for r in mine:
            ours.setdefault(r["level"], (num(r["ours_mean"]), num(r["ours_sd"]), r["ours_n"]))
        levels = sorted({lv for _, lv in points} & set(ours), key=level_rank)
        x = {lv: i for i, lv in enumerate(levels)}
        ax.errorbar([x[lv] for lv in levels], [ours[lv][0] for lv in levels], yerr=[ours[lv][1] for lv in levels],
                    color=FIG.INK, marker="o", markerfacecolor=FIG.INK, lw=1.0, label="ours")
        papers = sorted({p for p, lv in points if lv in x}, key=lambda p: (-sum(q == p for q, _ in points), p))
        for j, paper in enumerate(papers[:len(PAPER_MARKERS)]):
            pl = [lv for lv in levels if (paper, lv) in points]
            ax.errorbar([x[lv] + 0.15 * (j + 1) for lv in pl], [points[(paper, lv)][0] for lv in pl],
                        yerr=[points[(paper, lv)][1] for lv in pl], color=FIG.INK, linestyle="none", lw=0.7,
                        label=paper, **PAPER_MARKERS[j])
            drawn += [{"key": key, "level": lv, "paper": paper, "paper_mean": points[(paper, lv)][0],
                       "paper_sd": points[(paper, lv)][1], "paper_n": points[(paper, lv)][2],
                       "ours_mean": ours[lv][0], "ours_sd": ours[lv][1], "ours_n": ours[lv][2]} for lv in pl]
        discs = any("-" in lv for lv in levels)
        step = max(1, math.ceil(len(levels) / (4 if discs else 6)))
        ax.set_xticks(list(range(len(levels)))[::step])
        ax.set_xticklabels(levels[::step], fontsize=6.5 if discs else 7)
        ax.set_ylabel("mm", fontsize=7)
        ax.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
        FIG.letter(ax, letter, NAMES.get(key, key))
    cap = ("Ours on the thin ENHANCE.PET studies (mean and standard deviation by level) beside the adult human means "
           "and standard deviations of the papers with the most levels for each measure, each paper's sexes and age "
           "groups combined.")
    FIG.save(fig, out, "papers", cap)
    if drawn:
        FIG.write_csv(out, "papers", drawn)


# ---- all, and the index ------------------------------------------------------------------------

FIGURES = (("phantom-truth", fig_phantom, ("phantom-truth.csv",)),
           ("maskedge", fig_maskedge, ("maskedge-phantom.csv", "maskedge-ct.csv")),
           ("disc", fig_disc, ("disc-phantom.csv", "disc-ct.csv")),
           ("thicken", fig_thicken, ("thicken.csv",)),
           ("axis", fig_axis, ("axis-shift.csv", "axis-turn.csv")),
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
