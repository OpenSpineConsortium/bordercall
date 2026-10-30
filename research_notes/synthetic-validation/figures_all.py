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

import os
from typing import Dict, List, Sequence

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
    papers = sorted({r["paper"] for r in loo},
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


FIGURES_ALL = (fig_tables, fig_relations, fig_state_space_all, fig_naming_measures, fig_spread_all, fig_strata)
