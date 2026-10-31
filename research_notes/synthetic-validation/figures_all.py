"""The second part's figures, every measure of the reread, from the records run_all.py wrote.

figures.py draws them with the first part's: `python3 -I figures.py --records records --out figures`
reads records/all for these. Each is in the house format (synthval/house.py) and numbered on from
the first part's eight.

- fig9_tables: what became of the vocabulary's keys, and how many measures each table holds at each
  level, with the source of the papers' SDs;
- fig10_relations: the relations between the papers' measures and Panjabi's, flagged on table C at
  the generator and at its nearest point, and the unions by table;
- fig11_state_space_all: one axis at a time on the three tables, the spread, the neighbour
  correlation and the indicators, with each table's nearest point;
- fig12_naming_measures: exact naming against the number of measures the rule reads, over the whole
  column and over the lumbar run;
- fig13_spread_all: the spread between published series, tau over the cell's SD, by measure;
- fig14_strata: every paper its own population (synthval/strata.py, records/strata): the rule built on
  the others scored on each paper, the pooled loss and the interval for one more population, the
  promise at 0.99, and populations drawn from the random-effects model.
"""
from __future__ import annotations

import json
import math
import os
from typing import Dict, List, Sequence

import numpy as np

from synthval import house as H

LEVELS = ("C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12",
          "L1", "L2", "L3", "L4", "L5")
TABLE_LETTERS = {"Panjabi's, every measure": "A", "the papers'": "B", "Panjabi's and the papers'": "C"}
TABLE_LABEL = {"A": "A, Panjabi's every measure", "B": "B, the papers'", "C": "C, both"}
FATES = (("the generator's 32", lambda r: r["in_generator"] == "True"),
         ("Panjabi's others, with a spread", lambda r: r["panjabi"] == "True" and r["in_generator"] != "True"
          and "no spread" not in r["why_not_drawn"]),
         ("Panjabi's, a mean with no spread", lambda r: "no spread" in r["why_not_drawn"]),
         ("the papers' own, drawn", lambda r: r["panjabi"] != "True" and r["of_a_vertebra"] == "True" and not r["why_not_drawn"]),
         ("no paper prints a series", lambda r: r["why_not_drawn"].startswith("no paper")),
         ("rows, but no usable series", lambda r: r["why_not_drawn"].startswith("no series")),
         ("not a measure of one vertebra", lambda r: r["of_a_vertebra"] != "True"))


def _read_csv(path: str) -> List[dict]:
    import csv
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _read_json(path: str):
    import json
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def _median(xs: Sequence[float]) -> float:
    xs = sorted(x for x in xs if x == x)
    if not xs:
        return float("nan")
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def _letter(row: dict) -> str:
    return row.get("table_letter") or TABLE_LETTERS.get(row.get("table", ""), "")


def _rec(records: str, name: str) -> str:
    return os.path.join(records, "all", name)


# ----- figure 9: the tables -------------------------------------------------------------------------

def fig_tables(records: str, out: str) -> List[str]:
    plt = H.style()
    inv = _read_csv(_rec(records, "inventory.csv"))
    cells = _read_csv(_rec(records, "cells.csv"))
    tables = {k: _read_csv(_rec(records, "table_%s.csv" % k)) for k in ("panjabi", "papers", "both")}
    fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.6), gridspec_kw={"width_ratios": [1.1, 1.0, 1.0]})
    drawn = []
    a = axes[0]
    counts = []
    taken = set()
    for label, test in FATES:
        mine = [r["key"] for r in inv if test(r) and r["key"] not in taken]
        taken |= set(mine)
        counts.append((label, len(mine)))
    left = [r["key"] for r in inv if r["key"] not in taken]
    if left:
        counts.append(("other", len(left)))
    a.barh(range(len(counts)), [c for _, c in counts], color="white", edgecolor=H.INK)
    for i, (label, c) in enumerate(counts):
        a.text(c + 0.5, i, str(c), va="center", fontsize=7)
        drawn.append({"panel": "A", "fate": label, "keys": c})
    a.set_yticks(range(len(counts)))
    a.set_yticklabels([l for l, _ in counts], fontsize=7)
    a.invert_yaxis()
    a.set_xlabel("keys of the vocabulary (%d)" % len(inv))
    H.letter(a, "A", "what became of each key")
    b = axes[1]
    for j, (k, letter) in enumerate((("panjabi", "A"), ("papers", "B"), ("both", "C"))):
        rows = tables[k]
        ys = [sum(1 for r in rows if r["level"] == lv and r["mean"] not in ("", "nan") and _num(r["sd"]) > 0) for lv in LEVELS]
        b.plot(range(len(LEVELS)), ys, color=H.INK, label=TABLE_LABEL[letter], **H.SERIES_STYLE[j])
        drawn += [{"panel": "B", "table": letter, "level": lv, "measures": y} for lv, y in zip(LEVELS, ys)]
    b.set_xticks(range(len(LEVELS)))
    b.set_xticklabels(LEVELS, rotation=90)
    b.set_ylabel("measures with a cell")
    b.set_ylim(0, None)
    b.legend(loc="upper left", fontsize=6.5)
    H.letter(b, "B", "each table's measures, by level")
    c = axes[2]
    sources = ("pooled", "one series", "Tan 2004's among them, uncertain", "Tan 2004's alone, uncertain")
    short = {"pooled": "pooled from two or more", "one series": "one series",
             "Tan 2004's among them, uncertain": "Tan's among them", "Tan 2004's alone, uncertain": "Tan 2004 alone"}
    placed = [r for r in cells if r["placed_at"]]
    bottom = [0] * len(LEVELS)
    hatches = ("", "///", "...", "xx")
    for j, s in enumerate(sources):
        ys = [sum(1 for r in placed if r["placed_at"] == lv and r["sd_from"] == s) for lv in LEVELS]
        if not any(ys):
            continue
        c.bar(range(len(LEVELS)), ys, bottom=bottom, color="white", edgecolor=H.INK, hatch=hatches[j], label=short[s])
        drawn += [{"panel": "C", "sd_from": s, "level": lv, "cells": y} for lv, y in zip(LEVELS, ys)]
        bottom = [x + y for x, y in zip(bottom, ys)]
    c.set_xticks(range(len(LEVELS)))
    c.set_xticklabels(LEVELS, rotation=90)
    c.set_ylabel("the papers' placed cells")
    c.legend(loc="upper left", fontsize=6.5)
    H.letter(c, "C", "where the papers' SD comes from")
    fig.tight_layout()
    H.write_csv(out, "fig9_tables", drawn)
    return H.save(fig, out, "fig9_tables", (
        "Every measure of the reread. A, what became of each of the vocabulary's keys; B, the measures each "
        "table holds at each level of C3 to L5; C, the papers' placed cells by level and by where their SD "
        "comes from, Tan 2004's SDs being uncertain."))


# ----- figure 10: the relations -------------------------------------------------------------------

def fig_relations(records: str, out: str) -> List[str]:
    plt = H.style()
    qi = _read_json(_rec(records, "qi_all.json"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.0, 3.8), gridspec_kw={"width_ratios": [1.3, 1.0]})
    drawn = []
    on_c = [e for e in qi if TABLE_LETTERS.get(e["table"]) == "C"]
    gen = next(e for e in on_c if e["setting"] == "generator")
    near = next(e for e in on_c if e["setting"].startswith("nearest the papers (C)"))
    rel = [(x, y) for x, y in zip(gen["relations"], near["relations"]) if x["tested"]]
    for j, (label, pick) in enumerate((("generator", 0), ("C's nearest point", 1))):
        ys = [100 * pair[pick]["flagged"] for pair in rel]
        st = H.SERIES_STYLE[j]
        a.plot(range(len(rel)), ys, color=H.INK, linestyle="none", marker=st["marker"], markerfacecolor=st["markerfacecolor"],
               label=label)
        drawn += [{"panel": "A", "setting": label, "relation": pair[0]["relation"], "indicator": pair[0]["indicator"],
                   "tested": pair[0]["tested"], "flagged": y / 100} for pair, y in zip(rel, ys)]
    a.set_xticks(range(len(rel)))
    a.set_xticklabels([pair[0]["relation"].replace(" (convex bound)", ", convex") for pair in rel], rotation=30, ha="right", fontsize=6.5)
    a.set_ylabel("vertebrae flagged (%)")
    a.set_ylim(0, None)
    a.legend(loc="upper left", fontsize=6.5)
    H.letter(a, "A", "each relation on table C")
    unions = ("sign or inside", "necessary", "any but floor", "any")
    for j, letter in enumerate(("A", "B", "C")):
        mine = [e for e in qi if TABLE_LETTERS.get(e["table"]) == letter]
        g = next(e for e in mine if e["setting"] == "generator")
        n = next(e for e in mine if e["setting"].startswith("nearest the papers (%s)" % letter))
        for k, (e, mark) in enumerate(((g, "generator"), (n, "nearest"))):
            ys = [100 * e["vertebra"][u] for u in unions]
            st = dict(H.SERIES_STYLE[j])
            st["linestyle"] = "-" if k == 0 else ":"
            b.plot(range(len(unions)), ys, color=H.INK, label="%s, %s" % (letter, mark), **st)
            drawn += [{"panel": "B", "table": letter, "setting": mark, "union": u, "vertebrae": y / 100,
                       "persons": e["person"][u]} for u, y in zip(unions, ys)]
    b.set_xticks(range(len(unions)))
    b.set_xticklabels(unions, rotation=20, ha="right", fontsize=7)
    b.set_ylabel("vertebrae flagged (%)")
    b.set_ylim(0, 100)
    b.legend(loc="upper left", fontsize=6, ncol=2)
    H.letter(b, "B", "the unions, by table")
    fig.tight_layout()
    H.write_csv(out, "fig10_relations", drawn)
    return H.save(fig, out, "fig10_relations", (
        "Quality indicators on every measure. A, each relation between the papers' measures and Panjabi's, "
        "the share of synthetic vertebrae of table C that fail it at the generator and at C's nearest point; "
        "B, the unions on each table at both points, necessary being the relations no anatomy can fail."))


# ----- figure 11: the state space of the three tables ------------------------------------------------

def _axis(rows: List[dict], letter: str, axis: str) -> List[dict]:
    mine = [r for r in rows if _letter(r) == letter]
    gen = [r for r in mine if r["name"] == "generator"]
    pts = gen + [r for r in mine if r["name"].startswith(axis + "=")]
    return sorted(pts, key=lambda r: _num(r[axis]))


def fig_state_space_all(records: str, out: str) -> List[str]:
    plt = H.style()
    rows = _read_csv(_rec(records, "state_space_all.csv"))
    grid = _read_csv(_rec(records, "grid_all.csv"))
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.4))
    drawn = []
    panels = ((axes[0, 0], "A", "sd_scale", "sd_ratio_true", "SD of the true anatomy over the table's", "the SDs' scale"),
              (axes[0, 1], "B", "sd_scale", "qi vertebra necessary", "vertebrae failing a necessary relation (%)", "the SDs' scale"),
              (axes[1, 0], "C", "rho", "neighbour_r", "correlation of neighbouring levels", "rho"),
              (axes[1, 1], "D", "scale_sd", "qi vertebra any but floor", "vertebrae flagged, any but floor (%)", "the size's spread"))
    for ax, letter, axis, field, ylabel, xlabel in panels:
        for j, t in enumerate(("A", "B", "C")):
            pts = _axis(rows, t, axis)
            xs = [_num(p[axis]) for p in pts]
            ys = [_num(p[field]) * (100 if field.startswith("qi") else 1) for p in pts]
            ax.plot(xs, ys, color=H.INK, label=TABLE_LABEL[t], **H.SERIES_STYLE[j])
            drawn += [{"panel": letter, "table": t, axis: x, field: y / (100 if field.startswith("qi") else 1)} for x, y in zip(xs, ys)]
            near = [g for g in grid if _letter(g) == t]
            if near:
                n = min(near, key=lambda g: _num(g["distance"]))
                st = H.SERIES_STYLE[j]
                ax.plot([_num(n[axis])], [_num(n[field]) * (100 if field.startswith("qi") else 1)], color=H.INK, linestyle="none",
                        marker=st["marker"], markerfacecolor=H.GREY, markersize=9)
                drawn.append({"panel": letter, "table": t, "point": "nearest", axis: _num(n[axis]),
                              field: _num(n[field]), "distance": _num(n["distance"])})
        if field == "sd_ratio_true":
            ax.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        if letter == "A":
            ax.legend(loc="upper left", fontsize=6.5)
        H.letter(ax, letter, "%s moved alone; grey, each table's nearest point" % axis)
    fig.tight_layout()
    H.write_csv(out, "fig11_state_space_all", drawn)
    return H.save(fig, out, "fig11_state_space_all", (
        "The state space read on the three tables, one axis moved alone from the generator's point, with each "
        "table's nearest grid point in grey. A, the spread over the table's own SDs; B, the relations no anatomy "
        "can fail; C, the correlation between neighbouring levels; D, every indicator but the floor."))


# ----- figure 12: naming against the number of measures ------------------------------------------------

def fig_naming_measures(records: str, out: str) -> List[str]:
    plt = H.style()
    rows = _read_csv(_rec(records, "naming_all.csv"))
    runs = ("C3-L5", "L1-L5")
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.8))
    drawn = []
    settings = []
    for r in rows:
        if r["setting"] not in settings:
            settings.append(r["setting"])
    for ax, run, letter in zip(axes, runs, ("A", "B")):
        widths = sorted({int(_num(r["width"])) for r in rows if r["run"] == run})
        k = 0
        for si, st in enumerate(settings):
            for w in widths:
                mine = sorted([r for r in rows if r["run"] == run and r["setting"] == st and int(_num(r["width"])) == w],
                              key=lambda r: int(_num(r["n_measures"])))
                xs = [int(_num(r["n_measures"])) for r in mine]
                ys = [100 * _num(r["exact"]) for r in mine]
                style = dict(H.WIDTH_STYLE.get(w, H.SERIES_STYLE[k % len(H.SERIES_STYLE)]))
                style["linestyle"] = "-" if si == 0 else ":"
                ax.plot(xs, ys, color=H.INK, label="%d bod%s, %s" % (w, "y" if w == 1 else "ies", st), **style)
                drawn += [{"panel": letter, "run": run, "setting": st, "width": w, "measures": r["measures"], "n_measures": x,
                           "exact": y / 100, "exact_se": _num(r["exact_se"])} for r, x, y in zip(mine, xs, ys)]
                k += 1
        ax.set_xlabel("measures the rule reads")
        ax.set_ylabel("fields named exactly (%)")
        ax.set_ylim(0, 100)
        ax.legend(loc="lower right", fontsize=6)
        H.letter(ax, letter, "over %s" % run.replace("-", " to "))
    fig.tight_layout()
    H.write_csv(out, "fig12_naming_measures", drawn)
    return H.save(fig, out, "fig12_naming_measures", (
        "Exact naming by the rule built on more and more measures of table C, on columns drawn from it at the "
        "generator's point (solid) and at C's nearest point (dotted): over the whole column, the seven, the "
        "32 and every complete measure; over the lumbar run, those of A, B and C too."))


# ----- figure 13: the spread between series on every measure --------------------------------------------

def fig_spread_all(records: str, out: str) -> List[str]:
    plt = H.style()
    rows = _read_csv(_rec(records, "spread_all.csv"))
    fig, ax = plt.subplots(1, 1, figsize=(10.0, 3.6))
    drawn = []
    measures = sorted({r["measure"] for r in rows},
                      key=lambda m: -_median([_num(r["f"]) for r in rows if r["measure"] == m]))
    for mi, m in enumerate(measures):
        mine = [r for r in rows if r["measure"] == m]
        panjabi = mine[0]["panjabi"] == "True"
        st = H.SERIES_STYLE[0 if panjabi else 1]
        fs = [_num(r["f"]) for r in mine]
        ax.plot([mi] * len(fs), fs, color=H.GREY, linestyle="none", marker=".", markersize=3)
        ax.plot([mi], [_median(fs)], color=H.INK, linestyle="none", marker=st["marker"], markerfacecolor=st["markerfacecolor"],
                label=("Panjabi's measures" if panjabi else "the papers' own") if mi in (
                    next(i for i, x in enumerate(measures) if (rows and [r for r in rows if r["measure"] == x][0]["panjabi"] == "True")),
                    next((i for i, x in enumerate(measures) if [r for r in rows if r["measure"] == x][0]["panjabi"] != "True"), -1)) else None)
        drawn.append({"measure": m, "panjabi": panjabi, "cells": len(fs), "median_f": _median(fs),
                      "median_worth_scans": _median([_num(r["worth_scans"]) for r in mine])})
    ax.axhline(1.0, color=H.INK, linewidth=0.6, linestyle=":")
    ax.set_xticks(range(len(measures)))
    ax.set_xticklabels(measures, rotation=30, ha="right", fontsize=6.5)
    ax.set_ylabel("spread between series over the cell's SD")
    ax.set_ylim(0, None)
    ax.legend(loc="upper right", fontsize=6.5)
    H.letter(ax, "A", "every pooled cell with three series or more; the marker is the measure's median")
    fig.tight_layout()
    H.write_csv(out, "fig13_spread_all", drawn)
    return H.save(fig, out, "fig13_spread_all", (
        "The spread between published series on every measure the papers pool from three series or more: "
        "the REML tau over the cell's SD, one grey point a cell, the marker the measure's median. One means "
        "the series differ among themselves by a person's SD."))


# ----- figure 14: every paper its own population ------------------------------------------------------

MERGED, PREDICTED, OWN = "merged: the others pooled", "predicted: the others pooled, SD widened by tau", "own table"
SD_ONLY = "own means, the others' SD"
ARM_LABEL = {MERGED: "merged: the others pooled", PREDICTED: "predicted: widened by tau", SD_ONLY: "own means, the others' SD"}


def _strata(records: str, name: str) -> str:
    return os.path.join(records, "strata", name)


def fig_strata(records: str, out: str) -> List[str]:
    plt = H.style()
    loo = _read_csv(_strata(records, "loo.csv"))
    drawn_pop = _read_csv(_strata(records, "new_populations.csv"))
    j = _read_json(_strata(records, "strata.json"))
    pooled = j["pooled"]
    widths = [int(w) for w in j["sizes"]["widths"]]
    w_main = max(widths)
    readings = list(dict.fromkeys(r["reading"] for r in pooled))
    fig, axes = plt.subplots(2, 2, figsize=(10.0, 7.4), gridspec_kw={"height_ratios": [1.5, 1.0]})
    drawn = []

    def pooled_row(reading, arm, w):
        return next(r for r in pooled if r["reading"] == reading and r["arm"] == arm and r["width"] == w)

    # A: every paper left out, at the widest field: its loss under each rule, and the pooled loss with the interval for one more.
    a = axes[0, 0]
    # sorted by name first, so two papers with one loss keep one order whatever the set's order was
    papers = sorted(sorted({r["paper"] for r in loo}),
                    key=lambda p: _num(next(r["loss"] for r in loo if r["paper"] == p and r["arm"] == MERGED and int(r["width"]) == w_main)))
    for j_, arm in enumerate((MERGED, PREDICTED, SD_ONLY)):
        st = H.SERIES_STYLE[j_]
        ys = list(range(len(papers)))
        xs = [_num(next(r["loss"] for r in loo if r["paper"] == p and r["arm"] == arm and int(r["width"]) == w_main)) for p in papers]
        es = [1.96 * _num(next(r["loss_se"] for r in loo if r["paper"] == p and r["arm"] == arm and int(r["width"]) == w_main)) for p in papers]
        a.errorbar(xs, [y + (-0.24, 0.24, 0.0)[j_] for y in ys], xerr=es, color=H.INK, linestyle="none", marker=st["marker"],
                   markerfacecolor=st["markerfacecolor"], markersize=4 if j_ < 2 else 3, elinewidth=0.6, label=ARM_LABEL[arm])
        pr = pooled_row(readings[0], arm, w_main)
        y0 = len(papers) + 0.5 + 0.3 * j_
        lo, hi = _num(pr["pi_low"]), _num(pr["pi_high"])
        a.plot([lo, hi], [y0, y0], color=H.INK, linewidth=0.6, linestyle=st["linestyle"])
        a.plot([pr["loss_pooled"]], [y0], color=H.INK, linestyle="none", marker="D", markerfacecolor=st["markerfacecolor"], markersize=5)
        drawn += [{"panel": "A", "paper": p, "arm": arm, "width": w_main, "loss": x, "half_width_95": e} for p, x, e in zip(papers, xs, es)]
        drawn.append({"panel": "A", "paper": "pooled, one more population", "arm": arm, "width": w_main,
                      "loss": pr["loss_pooled"], "pi_low": lo, "pi_high": hi})
    labels = ["%s (%s)" % (p, next(r["n_measures"] for r in loo if r["paper"] == p)) for p in papers] + ["one more population"]
    a.set_yticks(list(range(len(papers))) + [len(papers) + 0.8])
    a.set_yticklabels(labels, fontsize=6.5)
    a.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")
    a.set_xlabel("loss against the paper's own table (points named exactly, %d bodies)" % w_main)
    a.legend(loc="lower right", fontsize=6.5)
    H.letter(a, "A", "each paper left out, on its own measures (count); the diamond is the pooled loss")

    # B: the pooled loss by width, the two leave-one-out readings and each rule (the model's is D).
    b = axes[0, 1]
    k = 0
    for ri, reading in enumerate(readings[:2]):
        for j_, arm in enumerate((MERGED, PREDICTED)):
            rows = [pooled_row(reading, arm, w) for w in widths]
            st = dict(H.SERIES_STYLE[k % len(H.SERIES_STYLE)])
            xs = [w + (k - 2.5) * 0.05 for w in widths]
            b.errorbar(xs, [r["loss_pooled"] for r in rows], yerr=[1.96 * (r["loss_se"] or 0.0) for r in rows], color=H.INK,
                       elinewidth=0.6, label="%s, %s" % (reading, ARM_LABEL[arm].split(":")[0]), **st)
            drawn += [{"panel": "B", "reading": reading, "arm": arm, "width": w, "loss_pooled": r["loss_pooled"], "loss_se": r["loss_se"],
                       "populations": r["populations"]} for w, r in zip(widths, rows)]
            k += 1
    b.set_xticks(widths)
    b.set_xlabel("bodies in the field (L1 to L5)")
    b.set_ylabel("pooled loss (points named exactly)")
    b.set_ylim(0, None)
    b.legend(loc="lower right", fontsize=6)
    H.letter(b, "B", "the pooled loss over the papers left out, bars 95% of its SE")

    # C: the promise at 0.99 on the papers and on the model's populations: how often right, the mean over the
    # populations, the least as a whisker.
    c = axes[1, 0]
    k = 0
    for ri, reading in enumerate((readings[0], readings[-1])):
        for j_, arm in enumerate((MERGED, PREDICTED)):
            rows = [pooled_row(reading, arm, w) for w in widths]
            st = dict(H.SERIES_STYLE[k % len(H.SERIES_STYLE)])
            xs = [w + (k - 2.5) * 0.05 for w in widths]
            ys = [100 * (r["precision_mean"] if r["precision_mean"] is not None else float("nan")) for r in rows]
            lows = [100 * (r["precision_min"] if r["precision_min"] is not None else float("nan")) for r in rows]
            c.errorbar(xs, ys, yerr=[[y - l for y, l in zip(ys, lows)], [0] * len(ys)], color=H.INK, elinewidth=0.6,
                       label="%s, %s" % (reading, ARM_LABEL[arm].split(":")[0]), **st)
            drawn += [{"panel": "C", "reading": reading, "arm": arm, "width": w, "precision_mean": r["precision_mean"],
                       "precision_min": r["precision_min"], "answered_mean": r["answered_mean"]} for w, r in zip(widths, rows)]
            k += 1
    c.axhline(99, color=H.INK, linewidth=0.6, linestyle=":")
    c.set_xticks(widths)
    c.set_xlabel("bodies in the field (L1 to L5)")
    c.set_ylabel("answers at 0.99 that are right (%)")
    c.set_ylim(40, 101)
    c.legend(loc="lower right", fontsize=6)
    H.letter(c, "C", "the promise at 0.99: the mean over the populations, the whisker down to the least")

    # D: populations drawn from the random-effects model itself: each one's loss, and the two rules.
    d = axes[1, 1]
    pops = list(dict.fromkeys(r["paper"] for r in drawn_pop))
    for j_, arm in enumerate((MERGED, PREDICTED)):
        st = dict(H.SERIES_STYLE[j_])
        for pi, p in enumerate(pops):
            ys = [_num(next(r["loss"] for r in drawn_pop if r["paper"] == p and r["arm"] == arm and int(r["width"]) == w)) for w in widths]
            d.plot([w + (j_ - 0.5) * 0.06 for w in widths], ys, color=H.GREY, linewidth=0.5, linestyle=st["linestyle"], marker=st["marker"],
                   markerfacecolor=st["markerfacecolor"], markersize=2.5, markeredgecolor=H.GREY)
            drawn += [{"panel": "D", "population": p, "arm": arm, "width": w, "loss": y} for w, y in zip(widths, ys)]
        rows = [pooled_row(readings[-1], arm, w) for w in widths]
        d.plot([w + (j_ - 0.5) * 0.06 for w in widths], [r["loss_pooled"] for r in rows], color=H.INK, label=ARM_LABEL[arm], **st)
    d.set_xticks(widths)
    d.set_xlabel("bodies in the field (L1 to L5)")
    d.set_ylabel("loss (points named exactly)")
    d.legend(loc="upper left", fontsize=6.5)
    H.letter(d, "D", "%d populations drawn from the model on the seven (grey), and the pooled loss" % len(pops))
    fig.tight_layout()
    H.write_csv(out, "fig14_strata", drawn)
    return H.save(fig, out, "fig14_strata", (
        "Every paper its own population. A, the rule built on the other papers, pooled, scored on each paper's "
        "population at three bodies, the small triangles the SD difference alone, the diamond's line the interval for "
        "one more population; B, the pooled loss by field width and reading; C, whether answers at 0.99 stay right; "
        "D, populations drawn from the model."))


# ---- choosing the rule by held-out prediction -----------------------------------------------------------

CANDIDATE_LABEL = {"own table": "own table (oracle)", "plain": "plain", "widened by tau": "widened by tau", "scaled SD": "scaled SD (k inner)",
                   "tempered": "tempered (T inner)", "mixture": "mixture"}
CANDIDATE_TICK = {"own table": "own\n(oracle)", "plain": "plain", "widened by tau": "widened\nby tau", "scaled SD": "scaled\nSD (k)",
                  "tempered": "tempered\n(T)", "mixture": "mixture"}


def _select(records: str, name: str) -> str:
    return os.path.join(records, "select", name)


def fig_select(records: str, out: str) -> List[str]:
    plt = H.style()
    j = _read_json(_select(records, "select.json"))
    summary = j["summary"]
    scores = _read_csv(_select(records, "scores.csv"))
    calibration = _read_csv(_select(records, "calibration.csv"))
    k_curve = _read_csv(_select(records, "k_curve.csv"))
    t_curve = _read_csv(_select(records, "t_curve.csv"))
    choices = _read_csv(_select(records, "choices.csv"))
    widths = [int(w) for w in j["sizes"]["widths"]]
    w_main = max(widths)
    candidates = ["own table"] + list(j.get("core", j["candidates"]))
    won = j["winner"]["by_log_score"]
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 7.6))
    drawn = []

    def srow(candidate, w):
        return next(r for r in summary if r["candidate"] == candidate and r["width"] == w)

    # A and B: every candidate's held-out log loss and accuracy, the mean over the populations, bars its SE.
    for ax, key, se_key, label, letter, note in ((axes[0, 0], "log_loss_mean", "log_score_se", "held-out log loss (nats, lower is better)", "A",
                                                   "mean over the %d held-out populations, bars one SE" % j["sizes"]["populations"]),
                                                  (axes[0, 1], "exact_mean", "exact_se", "held-out accuracy (top-1, exact level)", "B",
                                                   "the same populations; the oracle is the paper's own table")):
        for wi, w in enumerate(widths):
            st = dict(H.SERIES_STYLE[wi])
            xs = list(range(len(candidates)))
            ys = [srow(c, w)[key] for c in candidates]
            es = [srow(c, w)[se_key] or 0.0 for c in candidates]
            if key == "exact_mean":
                ys, es = [100 * y for y in ys], [100 * e for e in es]
            ax.errorbar([x + (wi - 1) * 0.12 for x in xs], ys, yerr=es, color=H.INK, elinewidth=0.6, label="%d bod%s" % (w, "y" if w == 1 else "ies"), **st)
            drawn += [{"panel": letter, "candidate": c, "width": w, key: y, se_key: e} for c, y, e in zip(candidates, ys, es)]
        ax.set_xticks(list(range(len(candidates))))
        ax.set_xticklabels([CANDIDATE_TICK[c] for c in candidates], fontsize=6.5)
        ax.set_ylabel(label)
        ax.legend(loc="upper right" if key == "log_loss_mean" else "lower right", fontsize=6.5)
        H.letter(ax, letter, note)

    # C: the reliability diagram at the widest field, pooled over the populations.
    c = axes[0, 2]
    for ci, cand in enumerate(candidates):
        rows = [r for r in calibration if r["candidate"] == cand and int(r["width"]) == w_main]
        st = dict(H.SERIES_STYLE[ci % len(H.SERIES_STYLE)])
        c.plot([_num(r["confidence"]) for r in rows], [_num(r["accuracy"]) for r in rows], color=H.INK, linewidth=0.8, markersize=3.5,
               label="%s, ECE %.3f" % (CANDIDATE_LABEL[cand].split(" (")[0], srow(cand, w_main)["ece_pooled"]), **st)
        drawn += [{"panel": "C", "candidate": cand, "width": w_main, "bin": r["bin"], "confidence": _num(r["confidence"]), "accuracy": _num(r["accuracy"]),
                   "fields": r["fields"]} for r in rows]
    c.plot([0, 1], [0, 1], color=H.INK, linewidth=0.6, linestyle=":")
    c.set_xlim(0, 1)
    c.set_ylim(0, 1)
    c.set_xlabel("posterior probability of the named level (bin mean)")
    c.set_ylabel("share of those fields named right")
    c.legend(loc="upper left", fontsize=6)
    H.letter(c, "C", "calibration at %d bodies, all populations pooled; the dotted line is perfect" % w_main)

    # D and E: the held-out log loss along the two knobs, the inner choices as a rug.
    for ax, rows, key, chosen_key, label, letter in ((axes[1, 0], k_curve, "k", "k", "SD factor k (1 is plain)", "D"),
                                                     (axes[1, 1], t_curve, "temperature", "t_%d", "temperature T (1 is the exact posterior)", "E")):
        grid = sorted({_num(r[key]) for r in rows})
        for wi, w in enumerate(widths):
            st = dict(H.SERIES_STYLE[wi])
            ys, es = [], []
            for g in grid:
                ls = [-_num(r["log_score"]) for r in rows if int(r["width"]) == w and abs(_num(r[key]) - g) < 1e-9]
                ys.append(float(np.mean(ls)))
                es.append(float(np.std(ls, ddof=1) / math.sqrt(len(ls))) if len(ls) > 1 else 0.0)
            ax.errorbar(grid, ys, yerr=es, color=H.INK, elinewidth=0.6, label="%d bod%s" % (w, "y" if w == 1 else "ies"), **st)
            drawn += [{"panel": letter, "width": w, key: g, "log_loss_mean": y, "log_loss_se": e} for g, y, e in zip(grid, ys, es)]
        for wi, w in enumerate(widths):
            picks = [_num(ch[chosen_key % w if "%" in chosen_key else chosen_key]) for ch in choices]
            if wi == 0 or "%" in chosen_key:
                ax.plot(picks, [0.02 + 0.03 * wi] * len(picks), color=H.INK, marker="|", markersize=5, linestyle="none", alpha=0.7,
                        transform=ax.get_xaxis_transform())
                drawn += [{"panel": letter, "width": w, "chosen_" + key: pk} for pk in picks]
        ax.set_xscale("log")
        ax.set_xticks(grid)
        ax.set_xticklabels(["%g" % g for g in grid], fontsize=6.5)
        ax.minorticks_off()
        ax.set_xlabel(label)
        ax.set_ylabel("held-out log loss (nats)")
        ax.legend(loc="upper right", fontsize=6.5)
        H.letter(ax, letter, "the knob swept on the held-out populations; the ticks are the inner choices")

    # F: the winner by log score against plain, population by population, paired, at the widest field.
    f = axes[1, 2]
    rows = sorted([r for r in scores if r["candidate"] == won and int(r["width"]) == w_main], key=lambda r: _num(r["log_score_vs_plain"]))
    ys = list(range(len(rows)))
    xs = [_num(r["log_score_vs_plain"]) for r in rows]
    es = [1.96 * _num(r["log_score_vs_plain_se"]) for r in rows]
    f.errorbar(xs, ys, xerr=es, color=H.INK, linestyle="none", marker="o", markerfacecolor=H.INK, markersize=3.5, elinewidth=0.6)
    f.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")
    f.set_yticks(ys)
    f.set_yticklabels([r["paper"] for r in rows], fontsize=6.5)
    f.set_xlabel("log score, %s minus plain (nats, right is better)" % won)
    drawn += [{"panel": "F", "candidate": won, "width": w_main, "paper": r["paper"], "log_score_vs_plain": x, "half_width_95": e}
              for r, x, e in zip(rows, xs, es)]
    H.letter(f, "F", "the winner against plain on each held-out population, %d bodies, bars 95%%" % w_main)
    fig.tight_layout()
    H.write_csv(out, "fig15_select", drawn)
    return H.save(fig, out, "fig15_select", (
        "Choosing the rule by held-out prediction, every paper held out in turn. A and B, each candidate's log loss and "
        "accuracy on the held-out populations; C, calibration; D and E, the SD factor and the temperature swept, the inner "
        "choices as ticks; F, the winner against the plain rule, population by population."))


EXCLUSION_TICK = {"tempered": "tempered", "without yadav2020": "without Yadav", "without yadav2020, tempered": "without Yadav,\ntempered",
                  "without frontphys2026": "without Front.\nPhys. 2026", "without frontphys2026, tempered": "without Front. Phys.\n2026, tempered",
                  "one vote per population": "one vote per\npopulation", "one vote per population, tempered": "one vote,\ntempered"}


def fig_exclusion(records: str, out: str) -> List[str]:
    """Whether leaving a paper out of the prior predicts the other populations better (the owner's
    choice of 2026-10-30, "Score exclusion held out"): each exclusion candidate against plain,
    paired by population, and population by population where the drops differ from plain."""
    plt = H.style()
    j = _read_json(_select(records, "select.json"))
    if "exclusion" not in j:
        return []
    summary = j["summary"]
    scores = _read_csv(_select(records, "scores.csv"))
    widths = [int(w) for w in j["sizes"]["widths"]]
    w_main = max(widths)
    names = ["tempered"] + list(j["exclusion"])
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.2))
    drawn = []

    def srow(candidate, w):
        return next(r for r in summary if r["candidate"] == candidate and r["width"] == w)

    ys = list(range(len(names)))[::-1]
    for ax, key, se_key, scale, label, letter, note in (
            (axes[0, 0], "log_score_vs_plain", "log_score_vs_plain_se", 1.0, "log score minus plain (nats, right is better)", "A",
             "mean over the %d held-out populations, paired, bars one SE" % j["sizes"]["populations"]),
            (axes[0, 1], "exact_vs_plain", "exact_vs_plain_se", 100.0, "accuracy minus plain (points, right is better)", "B",
             "the same populations; a temperature never moves the named level")):
        for wi, w in enumerate(widths):
            st = dict(H.SERIES_STYLE[wi])
            st["linestyle"] = "none"
            xs = [scale * srow(n, w)[key] for n in names]
            es = [scale * (srow(n, w)[se_key] or 0.0) for n in names]
            ax.errorbar(xs, [y + (1 - wi) * 0.18 for y in ys], xerr=es, color=H.INK, elinewidth=0.6, markersize=4,
                        label="%d bod%s" % (w, "y" if w == 1 else "ies"), **st)
            drawn += [{"panel": letter, "candidate": n, "width": w, key: x, se_key: e} for n, x, e in zip(names, xs, es)]
        ax.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")
        ax.set_yticks(ys)
        ax.set_yticklabels([EXCLUSION_TICK[n] for n in names], fontsize=6.5)
        ax.set_xlabel(label)
        ax.legend(loc="upper left", fontsize=6.5)
        H.letter(ax, letter, note)

    # C: population by population, each untempered drop against plain at the widest field.
    c = axes[1, 0]
    drops = [n for n in j["exclusion"] if not n.endswith(", tempered")]
    papers = sorted({r["paper"] for r in scores})
    per = {(r["candidate"], r["paper"]): r for r in scores if int(r["width"]) == w_main}
    order = sorted(papers, key=lambda p: min(_num(per[d, p]["log_score_vs_plain"]) for d in drops))[::-1]
    for di, d in enumerate(drops):
        st = dict(H.SERIES_STYLE[di])
        st["linestyle"] = "none"
        xs = [_num(per[d, p]["log_score_vs_plain"]) for p in order]
        c.plot(xs, [i + (1 - di) * 0.22 for i in range(len(order))], color=H.INK, markersize=3.5,
               label=EXCLUSION_TICK[d].replace("\n", " "), **st)
        drawn += [{"panel": "C", "candidate": d, "width": w_main, "paper": p, "log_score_vs_plain": x} for p, x in zip(order, xs)]
    c.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")
    c.set_yticks(list(range(len(order))))
    c.set_yticklabels(order, fontsize=6)
    c.set_xlabel("log score minus plain at %d bodies (nats, right is better)" % w_main)
    c.legend(loc="lower left", fontsize=6.5)
    H.letter(c, "C", "each held-out population; a drop changes nothing on a population whose measures it does not reach")

    # D: calibration of every candidate, the pooled ECE.
    d = axes[1, 1]
    every = ["plain"] + names
    for wi, w in enumerate(widths):
        st = dict(H.SERIES_STYLE[wi])
        st["linestyle"] = "none"
        xs = [srow(n, w)["ece_pooled"] for n in every]
        d.plot(xs, [y + (1 - wi) * 0.18 for y in range(len(every))[::-1]], color=H.INK, markersize=4,
               label="%d bod%s" % (w, "y" if w == 1 else "ies"), **st)
        drawn += [{"panel": "D", "candidate": n, "width": w, "ece_pooled": x} for n, x in zip(every, xs)]
    d.set_yticks(list(range(len(every)))[::-1])
    d.set_yticklabels([EXCLUSION_TICK.get(n, n) for n in every], fontsize=6.5)
    d.set_xlim(left=0)
    d.set_xlabel("expected calibration error, all populations pooled (lower is better)")
    d.legend(loc="lower right", fontsize=6.5)
    H.letter(d, "D", "how far the stated probability sits from the hit rate")
    fig.tight_layout()
    H.write_csv(out, "fig16_exclusion", drawn)
    return H.save(fig, out, "fig16_exclusion", (
        "Leaving a paper out, scored held out. A and B, each exclusion candidate against the plain rule, paired over the "
        "held-out populations; C, population by population at three bodies; D, calibration. Dropping either end-plate "
        "paper costs the populations that share its measures; the temperature carries the gain."))


def _covariates(records: str, name: str) -> str:
    return os.path.join(records, "covariates", name)


def fig_covariates(records: str, out: str) -> List[str]:
    """Covariates both ways from what the papers print apart (records/covariates): the effects of sex,
    age and body size on each measure, pooled within papers first; how well one measure tells the
    sexes apart; and how much of a measure sex or age explains, in the population and held out."""
    if not os.path.exists(_covariates(records, "effects.csv")):
        return []
    plt = H.style()
    effects = _read_csv(_covariates(records, "effects.csv"))
    held = _read_csv(_covariates(records, "held_out.csv"))
    contrasts = _read_csv(_covariates(records, "contrasts.csv"))
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.4))
    drawn = []

    def forest(ax, rows, label_of, style_of):
        rows = sorted(rows, key=lambda r: _num(r["mean"]))
        for i, r in enumerate(rows):
            m, lo, hi = _num(r["mean"]), _num(r["ci_low"]), _num(r["ci_high"])
            st = dict(style_of(r), linestyle="none")
            ax.errorbar([m], [i], xerr=[[m - lo], [hi - m]], color=H.INK, elinewidth=0.7, markersize=4, **st)
            drawn.append({"panel": ax.get_label(), "variable": r["variable"], "measure": r["measure"], "mean": m, "ci_low": lo,
                          "ci_high": hi, "papers": int(_num(r["papers"]))})
        ax.set_yticks(list(range(len(rows))))
        ax.set_yticklabels([label_of(r) for r in rows], fontsize=6.5)
        ax.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")

    a = axes[0, 0]
    a.set_label("A")
    forest(a, [r for r in effects if r["variable"] == "sex"],
           lambda r: "%s (%s)" % (r["measure"], r["papers_named"] if int(_num(r["papers"])) == 1 else "%d papers" % int(_num(r["papers"]))),
           lambda r: dict(H.SERIES_STYLE[0]))
    a.set_xlabel("men minus women, in within-sex SDs (Hedges' g), 95% interval")
    H.letter(a, "A", "sex, each paper's own men against its own women, papers pooled")

    b = axes[0, 1]
    b.set_label("B")
    order = ("age", "body height", "body weight")
    style = {v: dict(H.SERIES_STYLE[i]) for i, v in enumerate(order)}
    unit = {"age": "per decade", "body height": "per 100 mm", "body weight": "per 10 kg"}
    forest(b, [r for r in effects if r["variable"] in order],
           lambda r: "%s, %s (%s)" % (r["measure"], r["variable"], r["papers_named"].replace(";", ", ")), lambda r: style[r["variable"]])
    b.set_xlabel("change in within-band SDs (%s), 95%% interval" % ", ".join("%s %s" % (v, unit[v]) for v in order))
    H.letter(b, "B", "age and body size, each paper's own bands, papers pooled")

    c = axes[1, 0]
    measures = sorted({r["measure"] for r in contrasts})
    for i, m in enumerate(measures):
        own = [r for r in contrasts if r["measure"] == m]
        aucs = [_auc(_num(r["mean_male"]), _num(r["sd_male"]), _num(r["mean_female"]), _num(r["sd_female"])) for r in own]
        c.plot(aucs, [i + 0.12] * len(aucs), color=H.INK, marker="o", markersize=3, linestyle="none", alpha=0.6,
               label="in the population" if i == 0 else None)
        ho = [_num(r["auc_transfer"]) for r in held if r["variable"] == "sex" and r["measure"] == m]
        c.plot(ho, [i - 0.12] * len(ho), color=H.INK, marker="s", markerfacecolor="white", markersize=3, linestyle="none",
               label="held out, effect from other papers" if i == 0 else None)
        drawn += [{"panel": "C", "measure": m, "auc_own": x} for x in aucs] + [{"panel": "C", "measure": m, "auc_held_out": x} for x in ho]
    c.axvline(0.5, color=H.INK, linewidth=0.6, linestyle=":")
    c.set_yticks(list(range(len(measures))))
    c.set_yticklabels(measures, fontsize=6.5)
    c.set_xlim(0.3, 1.0)
    c.set_xlabel("AUC of telling men from women by this one measure at one level (0.5 is chance)")
    c.legend(loc="lower left", fontsize=6.5)
    H.letter(c, "C", "shape to sex: one point a printed stratum")

    d = axes[1, 1]
    keys = sorted({(r["variable"], r["measure"]) for r in held})
    for i, (v, m) in enumerate(keys):
        rs = [r for r in held if r["variable"] == v and r["measure"] == m]
        own = [_num(r["r2_own"]) for r in rs]
        tr = [_num(r["r2_transfer"]) for r in rs]
        d.plot(own, [i + 0.12] * len(own), color=H.INK, marker="o", markersize=3, linestyle="none", alpha=0.6,
               label="the population's own split" if i == 0 else None)
        d.plot(tr, [i - 0.12] * len(tr), color=H.INK, marker="s", markerfacecolor="white", markersize=3, linestyle="none",
               label="held out, effect from other papers" if i == 0 else None)
        drawn += [{"panel": "D", "variable": v, "measure": m, "r2_own": o, "r2_held_out": t} for o, t in zip(own, tr)]
    d.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")
    d.set_yticks(list(range(len(keys))))
    d.set_yticklabels(["%s from %s" % (m, v) for v, m in keys], fontsize=6.5)
    d.set_xlabel("share of the measure's variance explained (R^2; below 0 is worse than ignoring it)")
    d.legend(loc="lower right", fontsize=6.5)
    H.letter(d, "D", "covariate to shape, where another paper prints the same measure")
    fig.tight_layout()
    H.write_csv(out, "fig17_covariates", drawn)
    return H.save(fig, out, "fig17_covariates", (
        "Covariates read from what the papers print apart. A, sex; B, age and body size, each within its paper and the "
        "papers pooled; C, how well one measure tells men from women; D, how much of a measure sex or age explains, in "
        "the population and held out by paper."))


LUMBAR = ("L1", "L2", "L3", "L4", "L5")
BOUNDS_MEASURE = "h_ant"
COHORTS = (("the papers' ideal spine", "centre"), ("SchwingCheck's generator, true", "generator, true"),
           ("SchwingCheck's generator, measured", "generator, measured"), ("nearest the papers, true", "nearest the papers, true"),
           ("lumbar gradient flattened", "flattened lumbar"), ("lumbar gradient reversed", "reversed lumbar"))


def fig_bounds(records: str, out: str) -> List[str]:
    """The bounds card (records/bounds): one measure's interval for a new population's mean along the
    column, with the ideal spine's lumbar gradient flattened and reversed beside it; and each test's
    pass rate for real papers held out, populations the card draws and the generators, against the
    bar the held-out papers set."""
    folder = os.path.join(records, "bounds")
    if not os.path.exists(os.path.join(folder, "bounds.json")):
        return []
    plt = H.style()
    j = _read_json(os.path.join(folder, "bounds.json"))
    cells = {r["level"]: r for r in _read_csv(os.path.join(folder, "bounds.csv"))
             if r["kind"] == "all" and r["measure"] == BOUNDS_MEASURE}
    cal = [r for r in _read_csv(os.path.join(folder, "calibration.csv")) if (r.get("kind") or "all") == "all"]
    bar = j["calibration"]["bar"]
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))
    drawn = []

    a = axes[0]
    levels = [lv for lv in LEVELS if lv in cells]
    x = np.arange(len(levels))
    mean = np.array([_num(cells[lv]["mean"]) for lv in levels])
    low = np.array([_num(cells[lv]["mean_low"]) for lv in levels])
    high = np.array([_num(cells[lv]["mean_high"]) for lv in levels])
    a.fill_between(x, low, high, color=H.INK, alpha=0.12, linewidth=0, label="95% interval for a new population's mean")
    a.plot(x, mean, color=H.INK, linewidth=1.2, label="pooled mean")
    lumbar = [i for i, lv in enumerate(levels) if lv in LUMBAR]
    flat = float(np.mean(mean[lumbar]))
    a.plot(lumbar, [flat] * len(lumbar), color=H.INK, marker="s", markerfacecolor="white", markersize=4, linestyle="--",
           linewidth=0.8, label="lumbar gradient flattened")
    a.plot(lumbar, mean[lumbar][::-1], color=H.INK, marker="^", markersize=4, linestyle=":", linewidth=0.8,
           label="lumbar gradient reversed")
    a.set_xticks(x)
    a.set_xticklabels(levels, fontsize=6.5, rotation=90)
    a.set_ylabel("%s, mm" % BOUNDS_MEASURE)
    a.legend(loc="upper left", fontsize=6.5)
    H.letter(a, "A", "one measure along the column: wide on means, so a broken gradient stays inside")
    drawn += [{"panel": "A", "level": lv, "mean": m, "mean_low": lo, "mean_high": hi} for lv, m, lo, hi in zip(levels, mean, low, high)]

    b = axes[1]
    tests = ("mean", "sd", "step")
    rows = []
    for test in tests:
        papers = [r for r in cal if r["test"] == test and int(_num(r["made"])) >= 20]
        rows.append(("real papers held out", test, [_num(r["rate"]) for r in papers]))
        for label, key in COHORTS:
            got = j["checks"][key]["summary"]["tests"].get(test)
            if got:
                rows.append((label, test, [_num(got["rate"])]))
    labels = ["real papers held out", "populations the card draws"] + [label for label, _ in COHORTS]
    quartiles = [_num(v) for v in j["checks"]["drawn"]["population_rate_quartiles"]]
    b.plot(quartiles, [1] * len(quartiles), marker="x", markersize=4, linestyle="-", linewidth=0.6, color=H.INK,
           label="every test together (quartiles)")
    drawn += [{"panel": "B", "cohort": "populations the card draws", "test": "every test, quartile", "rate": v} for v in quartiles]
    for k, test in enumerate(tests):
        for i, label in enumerate(labels):
            got = [v for (lb, t, v) in rows if lb == label and t == test]
            if not got:
                continue
            y = i + (k - 1) * 0.25
            b.plot(got[0], [y] * len(got[0]), marker=("o", "s", "^")[k], markersize=3.5, linestyle="none", color=H.INK,
                   markerfacecolor=("white", H.INK, "white")[k], alpha=0.8, label=test if i == 0 else None)
            drawn += [{"panel": "B", "cohort": label, "test": test, "rate": v} for v in got[0]]
    step_bar = bar.get("step", {})
    if "low" in step_bar:
        b.axvline(step_bar["low"], color=H.INK, linewidth=0.8, linestyle="--")
        b.text(step_bar["low"], len(labels) - 0.4, " step bar %.2f" % step_bar["low"], fontsize=6.5, va="bottom")
    b.set_yticks(range(len(labels)))
    b.set_yticklabels(labels, fontsize=6.5)
    b.invert_yaxis()
    b.set_xlim(0.0, 1.02)
    b.set_xlabel("share of a cohort's cells or steps inside the card's interval (scored at %d people a cell)"
                 % int(j["reference_n_measured"]["reference_n"]))
    b.legend(loc="lower left", fontsize=6.5, title="test", title_fontsize=6.5)
    H.letter(b, "B", "pass rates against the bar real papers set; naming lives on the steps")
    fig.tight_layout()
    H.write_csv(out, "fig19_bounds", drawn)
    return H.save(fig, out, "fig19_bounds", (
        "The bounds card. A, one measure's interval for a new population's mean; a flattened or reversed lumbar "
        "gradient stays inside it. B, pass rates by test; the step test separates the broken gradients from real "
        "populations."))


SEX_RULES = (("B: the person's sex's table", "A: the sexless table"),)


SEX_HELD_B = "B: A moved by the others' g, P's inner T"
SEX_HELD_A = "A: the others' plain table, P's inner T"
SEX_SYNTHETIC = "synthetic, every measure the selection uses"
SEX_HEADLINE = "the headline"


def _gain_reads(rows: List[dict]) -> str:
    """What the headline's 95% intervals say across the field widths, in words for a panel title."""
    lows = [_num(r["d_log_score"]) - 1.96 * _num(r["d_log_score_se"]) for r in rows]
    highs = [_num(r["d_log_score"]) + 1.96 * _num(r["d_log_score_se"]) for r in rows]
    if rows and all(lo > 0 for lo in lows):
        return "told the sex names better at every width"
    if rows and all(hi < 0 for hi in highs):
        return "told the sex names worse at every width"
    return "no width's gain is clear of zero" if all(lo <= 0 <= hi for lo, hi in zip(lows, highs)) else "the gain is clear at some widths only"


def fig_sex_naming(records: str, out: str) -> List[str]:
    """Naming told the person's sex (records/sex_naming): the gain over the sexless table on synthetic
    populations whose sexes differ by a known shift, and held out by paper on the papers' own men and
    women, at one to three bodies in the field. Held out, the rule told the sex is the others' table
    moved by the others' pooled g and the rule not told is the others' plain table, both at the held-out
    paper's own inner temperature, so the two differ only in the sex."""
    folder = os.path.join(records, "sex_naming")
    if not os.path.exists(os.path.join(folder, "summary.csv")):
        return []
    plt = H.style()
    summary = _read_csv(os.path.join(folder, "summary.csv"))
    with open(os.path.join(folder, "sex_naming.json"), encoding="ascii") as fh:
        borrowed = set(json.load(fh)["headline"]["papers_with_borrowed_sd"])
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))
    drawn = []
    widths = ("1", "2", "3")
    marks = ("o", "s", "^")
    fills = ("white", H.INK, "white")

    def bodies(width: str) -> str:
        return "%s bod%s" % (width, "y" if width == "1" else "ies")

    a = axes[0]
    syn = [r for r in summary if r["reading"] == SEX_SYNTHETIC and r["rule"].startswith("B:")
           and r["against"] == "A: the sexless table" and r["arm"] == "the same shift at every cell"]
    for k, width in enumerate(widths):
        rs = sorted((r for r in syn if r["width"] == width), key=lambda r: _num(r["d"]))
        d = [_num(r["d"]) for r in rs]
        gain = [_num(r["d_log_score"]) for r in rs]
        se = [_num(r["d_log_score_se"]) for r in rs]
        a.errorbar(d, gain, yerr=[1.96 * v for v in se], marker=marks[k], markersize=3.5, linewidth=0.8,
                   color=H.INK, markerfacecolor=fills[k], label=bodies(width))
        drawn += [{"panel": "A", "width": int(width), "d": x, "d_log_score": g, "se": e} for x, g, e in zip(d, gain, se)]
    a.axhline(0, color=H.INK, linewidth=0.6, linestyle=":")
    a.set_xlabel("men minus women in the synthetic populations, within-sex SDs at every cell")
    a.set_ylabel("log score per field, told the sex minus not told (nats)")
    a.legend(loc="upper left", fontsize=6.5)
    H.letter(a, "A", "synthetic: the gain grows with the sexes' difference")

    b = axes[1]
    held = [r for r in summary if r["reading"] == "held out" and r["rule"] == SEX_HELD_B and r["against"] == SEX_HELD_A]
    headline = [r for r in held if r["paper"].startswith(SEX_HEADLINE)]
    papers = sorted({r["paper"] for r in held if not r["paper"].startswith(("pooled", SEX_HEADLINE))})
    rows = papers + [SEX_HEADLINE]
    for k, width in enumerate(widths):
        for i, paper in enumerate(rows):
            got = [r for r in (headline if paper == SEX_HEADLINE else held) if r["width"] == width
                   and (paper == SEX_HEADLINE or r["paper"] == paper)]
            if not got:
                continue
            g, e = _num(got[0]["d_log_score"]), _num(got[0]["d_log_score_se"])
            y = i + (0.5 if paper == SEX_HEADLINE else 0) + (k - 1) * 0.25
            b.errorbar([g], [y], xerr=[[1.96 * e], [1.96 * e]], marker="D" if paper == SEX_HEADLINE else marks[k],
                       markersize=4 if paper == SEX_HEADLINE else 3, linewidth=1.0 if paper == SEX_HEADLINE else 0.6,
                       color=H.INK if paper not in borrowed else H.GREY, markerfacecolor=fills[k],
                       label=bodies(width) if i == 0 else None)
            drawn.append({"panel": "B", "paper": got[0]["paper"], "width": int(width), "d_log_score": g, "se": e,
                          "persons_sd_borrowed": paper in borrowed})
    b.axvline(0, color=H.INK, linewidth=0.6, linestyle=":")
    b.set_yticks([i + (0.5 if p == SEX_HEADLINE else 0) for i, p in enumerate(rows)])
    b.set_yticklabels([("%s (SD borrowed)" % p) if p in borrowed else p for p in papers]
                      + ["pooled, papers with printed SDs"], fontsize=6.5)
    b.invert_yaxis()
    b.set_xlabel("log score per field, told the sex minus not told (nats), 95% interval")
    b.legend(loc="upper left", fontsize=6.5)
    reads = _gain_reads(headline)
    H.letter(b, "B", "held out by paper: " + reads)
    fig.tight_layout()
    H.write_csv(out, "fig18_sex_naming", drawn)
    return H.save(fig, out, "fig18_sex_naming", (
        "Naming a short field told the person's sex. A, synthetic populations: the gain in log score grows with the "
        "sexes' difference. B, each paper held out on its own men and women, scored at its own temperature: %s." % reads))


GOLD3_MEMBERS = (("autopet", "autoPET", "o", None), ("totalseg", "TotalSegmentator", "s", "white"))
GOLD3_FAMILIES = ("every family", "body and end plate", "disc and foramen", "pedicle and canal", "posterior elements")
GOLD3_PROFILE = ("pedicle", "pedicle_w")


GOLD3_COLUMNS = {"sex_g": ("card_sex_g", "sex_g_new_low", "sex_g_new_high"),
                 "age_slope": ("card_age_slope", "age_new_low", "age_new_high")}


def _gold3_rows(cells: List[dict], prefix: str) -> List[dict]:
    """One row a measure: the card's interval for a new population's effect and its centre, and each
    member's effect, each averaged over the levels both have."""
    centre, low, high = GOLD3_COLUMNS[prefix]
    out = []
    for key in sorted({c["key"] for c in cells if c.get(prefix)}):
        mine = [c for c in cells if c["key"] == key and c.get(prefix)]
        row = {"key": key, "centre": float(np.mean([_num(c[centre]) for c in mine])),
               "new_low": float(np.mean([_num(c[low]) for c in mine])),
               "new_high": float(np.mean([_num(c[high]) for c in mine]))}
        for member, *_ in GOLD3_MEMBERS:
            got = [_num(c[prefix]) for c in mine if c["member"] == member]
            row[member] = float(np.mean(got)) if got else float("nan")
        out.append(row)
    return sorted(out, key=lambda r: r["centre"])


def _gold3_forest(ax, rows: List[dict], prefix: str, xlabel: str) -> List[dict]:
    drawn = []
    for i, r in enumerate(rows):
        ax.plot([r["new_low"], r["new_high"]], [i, i], color=H.GREY, linewidth=3.0, solid_capstyle="butt",
                label="the card's 95% interval for a new population" if i == 0 else None)
        ax.plot([r["centre"]], [i], marker="|", markersize=7, color=H.INK, linestyle="none",
                label="the card's centre" if i == 0 else None)
        for member, name, marker, fill in GOLD3_MEMBERS:
            ax.plot([r[member]], [i], marker=marker, markersize=3.5, color=H.INK, linestyle="none",
                    markerfacecolor=fill or H.INK, label=name if i == 0 else None)
        drawn.append(dict(r, panel=prefix))
    ax.axvline(0, color=H.INK, linewidth=0.5, linestyle=":")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r["key"] for r in rows], fontsize=6.0)
    ax.set_xlabel(xlabel)
    return drawn


def fig_gold3(records: str, out: str) -> List[str]:
    """Gold tier 3's real CTs on the bounds card (records/gold3): each test's pass rate by family of
    measures against the bar of the papers held out, the sex contrast and the age slope by measure
    against the card's interval for a new population, and the pedicle width along the column, where
    the engine's values leave the papers'."""
    folder = os.path.join(records, "gold3")
    if not os.path.exists(os.path.join(folder, "gold3.json")):
        return []
    plt = H.style()
    j = _read_json(os.path.join(folder, "gold3.json"))
    cells = _read_csv(os.path.join(folder, "cells.csv"))
    bar = j["bar"]
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 9.0))
    drawn = []

    a = axes[0][0]
    labels = []
    for t, test in enumerate(("mean", "sd", "step")):
        for f, fam in enumerate(GOLD3_FAMILIES):
            y = len(labels)
            labels.append("%s, %s" % (test, fam))
            for member, name, marker, fill in GOLD3_MEMBERS:
                got = j["members"][member]["by_family"][fam].get(test)
                if got:
                    a.plot([got["rate"]], [y], marker=marker, markersize=4, color=H.INK, linestyle="none",
                           markerfacecolor=fill or H.INK, label=name if y == 0 else None)
                    drawn.append({"panel": "A", "member": member, "test": test, "family": fam, "made": got["made"],
                                  "passed": got["passed"], "rate": got["rate"]})
        ys = (t * len(GOLD3_FAMILIES) - 0.4, (t + 1) * len(GOLD3_FAMILIES) - 0.6)
        a.plot([bar[test]["low"]] * 2, ys, color=H.INK, linewidth=1.0, linestyle="--",
               label="the bar: 10th percentile of papers held out" if t == 0 else None)
        a.plot([bar[test]["median"]] * 2, ys, color=H.INK, linewidth=0.6, linestyle=":",
               label="their median" if t == 0 else None)
        drawn.append({"panel": "A", "test": test, "bar_low": bar[test]["low"], "bar_median": bar[test]["median"]})
    a.set_yticks(range(len(labels)))
    a.set_yticklabels(labels, fontsize=6.0)
    a.invert_yaxis()
    rates = [r["rate"] for r in drawn if "rate" in r]
    a.set_xlim(min(0.3, math.floor(10 * min(rates)) / 10 - 0.05), 1.02)
    a.set_xlabel("share of the cohort's cells or steps inside the card's interval (scored at %d people)" % j["reference_n"])
    a.legend(loc="lower left", fontsize=6.0)
    H.letter(a, "A", "real CTs pass the body and end-plate steps; the pedicle and canal steps near the bar, the discs' fail")

    b = axes[0][1]
    sex = _gold3_rows(cells, "sex_g")
    drawn += _gold3_forest(b, sex, "sex_g", "men minus women, Hedges' g (mean over levels)")
    b.legend(loc="lower right", fontsize=6.0)
    s = {m: j["members"][m]["sex"] for m, *_ in GOLD3_MEMBERS}
    H.letter(b, "B", "sex: inside the card's interval at %d of %d and %d of %d cells; the sign holds, the gaps smaller"
             % (s["autopet"]["inside_card"], s["autopet"]["cells"], s["totalseg"]["inside_card"], s["totalseg"]["cells"]))

    c = axes[1][0]
    card = {r["level"]: r for r in _read_csv(os.path.join(records, "bounds", "bounds.csv"))
            if r["kind"] == "all" and r["measure"] == GOLD3_PROFILE[0]}
    levels = [lv for lv in LEVELS if lv in card or any(x["key"] == GOLD3_PROFILE[1] and x["level"] == lv for x in cells)]
    x = np.arange(len(levels))
    low = [_num(card[lv]["mean_low"]) if lv in card else float("nan") for lv in levels]
    high = [_num(card[lv]["mean_high"]) if lv in card else float("nan") for lv in levels]
    c.fill_between(x, low, high, color=H.INK, alpha=0.12, linewidth=0, label="the card's 95% interval for a new population's mean")
    c.plot(x, [_num(card[lv]["mean"]) if lv in card else float("nan") for lv in levels], color=H.INK, linewidth=1.0,
           label="the card's pooled mean")
    for k, (member, name, marker, fill) in enumerate(GOLD3_MEMBERS):
        got = {r["level"]: r for r in cells if r["member"] == member and r["key"] == GOLD3_PROFILE[1]}
        ys = [_num(got[lv]["mean"]) if lv in got else float("nan") for lv in levels]
        c.plot(x, ys, color=H.INK, marker=marker, markersize=3.5, markerfacecolor=fill or H.INK,
               linestyle=("-", "--")[k], linewidth=0.8, label=name + ", the engine")
        drawn += [{"panel": "C", "member": member, "level": lv, "mean": v} for lv, v in zip(levels, ys)]
    drawn += [{"panel": "C", "level": lv, "card_low": lo, "card_high": hi} for lv, lo, hi in zip(levels, low, high)]
    c.set_xticks(x)
    c.set_xticklabels(levels, fontsize=6.5)
    c.set_ylabel("pedicle width, mm")
    c.legend(loc="upper left", fontsize=6.0)
    H.letter(c, "C", "the engine's pedicle width (PR 44): 1 to 2 mm wide at T10 to T12, inside the band from L1")

    d = axes[1][1]
    age = _gold3_rows(cells, "age_slope")
    drawn += _gold3_forest(d, age, "age_slope", "change per decade of age, in SDs")
    s = {m: j["members"][m]["age"] for m, *_ in GOLD3_MEMBERS}
    H.letter(d, "D", "age: inside the card's interval at %d of %d and %d of %d cells; its age spread is not identified"
             % (s["autopet"]["inside_card"], s["autopet"]["cells"], s["totalseg"]["inside_card"], s["totalseg"]["cells"]))
    fig.tight_layout()
    H.write_csv(out, "fig20_gold3", drawn)
    return H.save(fig, out, "fig20_gold3", (
        "Two real gold tier 3 cohorts, measured by the engine, on the bounds card. A, pass rates by family "
        "against the papers' bar. B, sex contrasts against the card's interval. C, the engine's pedicle width "
        "along the column. D, age slopes."))


def _auc(mu_a: float, sd_a: float, mu_b: float, sd_b: float) -> float:
    from scipy import stats
    z = stats.norm.cdf((mu_a - mu_b) / math.sqrt(sd_a ** 2 + sd_b ** 2))
    return float(max(z, 1.0 - z))


FIGURES_ALL = (fig_tables, fig_relations, fig_state_space_all, fig_naming_measures, fig_spread_all, fig_strata, fig_select,
               fig_exclusion, fig_covariates, fig_sex_naming, fig_bounds, fig_gold3)
