#!/usr/bin/env python3
"""How much of the spread between studies is a shift and how much is level by level.

between_studies.py measures how far the published means differ, cell by cell. For naming the two
kinds of difference act differently (cadaver_power.py, part B): a difference shared by every level
of a measure moves every candidate place nearly alike, while a difference that changes from level
to level changes which place fits best. This splits the first from the second.

Within each measure and region (cervical, thoracic, lumbar), every study's means are put in units
of Panjabi's person SD at their level and fitted by least squares as a level term plus a study
term. The study term is the study's shift; what is left is the level-by-level part. Its mean
square holds sampling error as well, at most 1/12 of a person's variance for a mean of 12 or more
specimens, so the level-by-level part lies between sqrt(MS - 1/12) and sqrt(MS) if Panjabi's
person SDs were exact; where within a person the same measure at neighbouring levels moves
together, as it does in real columns, less of the sampling error lands here and the true value is
nearer the upper end. Each person SD comes from 12 specimens, though, and scaling every level by
its own SD carries that error into the means: it adds to MS, most for the endplate area, whose
level-by-level part is 0.77 with each level's own SD and 0.32 with one SD per group
(verify/pooled_sd_split.py), so sqrt(MS) is not a strict upper bound.

The summary gives the study shift's SD two ways: the median over the groups, which the note's
part C readings use, and pooled over the groups by degrees of freedom (studies minus 1), as the
level-by-level part is pooled. A median of SDs from groups of 3 to 6 studies runs below the pooled
value.

Grouping by region gives each study its own shift in each region. Where one study gives a measure
in both the thoracic and the lumbar region, the correlation of its two shifts says how far a
study's shift is shared along the column.

--measures keeps only the measures named, such as the five of Panjabi's that the seven SPINEPS
measures read: the lower endplate's depth and width (EPDl, EPWl), the posterior body height (VBHp)
and the canal's depth and width (SCD, SCW).

    python3 shift_profile.py between_studies.json [--measures EPDl EPWl ...] [--out FILE]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict

import numpy as np

SAMPLING = 1.0 / 12.0


def groups(cells):
    by = defaultdict(list)
    for c in cells:
        by[(c["measure"], c["level"][0])].append(c)
    return by


def fit(cells):
    """Least squares of y = level + study on one measure and region; None when it has no residual."""
    levels = sorted({c["level"] for c in cells})
    studies = sorted({s for c in cells for s in c["means"]})
    rows, y = [], []
    for c in cells:
        for s, v in c["means"].items():
            x = np.zeros(len(levels) + len(studies) - 1)
            x[levels.index(c["level"])] = 1.0
            j = studies.index(s)
            if j > 0:
                x[len(levels) + j - 1] = 1.0
            rows.append(x)
            y.append(v / c["sd"])
    X, y = np.array(rows), np.array(y)
    df = len(y) - np.linalg.matrix_rank(X)
    if df <= 0:
        return None
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    shift = np.concatenate([[0.0], beta[len(levels):]])
    shift = shift - shift.mean()
    total = sum((v / c["sd"] - np.mean([w / c["sd"] for w in c["means"].values()])) ** 2
                for c in cells for v in c["means"].values())
    total_df = sum(len(c["means"]) - 1 for c in cells)
    return {"levels": len(levels), "studies": len(studies), "means": len(y), "df": int(df),
            "ms_level_by_level": float(resid @ resid / df),
            "ms_between_studies": float(total / total_df),
            "shift_sd": float(np.std(shift, ddof=1)),
            "shifts": dict(zip(studies, map(float, shift)))}


def thoracic_lumbar(out: dict) -> dict:
    """The correlation of a study's thoracic and lumbar shifts, over the studies that give both."""
    pairs = []
    for key, r in out.items():
        m, region = key.split()
        lumbar = out.get(m + " L")
        if region != "T" or lumbar is None:
            continue
        pairs += [(v, lumbar["shifts"][s]) for s, v in r["shifts"].items() if s in lumbar["shifts"] and s != "present"]
    if len(pairs) < 3:
        return {"pairs": len(pairs), "correlation": None}
    a = np.array(pairs)
    return {"pairs": len(pairs), "correlation": float(np.corrcoef(a.T)[0, 1])}


def consistent(shift_sd: float, ms_level: float, levels: float) -> dict:
    """The two parts with the sampling error of 12 specimens split between them, not taken out of
    both. Within a person the same measure at its several levels correlates r: a study's shift, the
    mean of its levels, then carries (r + (1 - r)/L)/12 of sampling variance, and the level-by-level
    part the rest, (1 - r)/12. r is not known here; real columns put it high."""
    out = {}
    for r in (0.0, 0.5, 0.8, 1.0):
        out["%g" % r] = {
            "shift": math.sqrt(max(0.0, shift_sd ** 2 - (r + (1.0 - r) / levels) * SAMPLING)),
            "level_by_level": math.sqrt(max(0.0, ms_level - (1.0 - r) * SAMPLING))}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cells")
    ap.add_argument("--measures", nargs="*")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    cells = json.load(open(a.cells))["cells"]
    if a.measures:
        cells = [c for c in cells if c["measure"] in a.measures]
    out, pooled = {}, defaultdict(float)
    print("%-10s %6s %7s %5s %3s %10s %10s %10s %10s" % (
        "measure", "levels", "studies", "means", "df", "between", "shift sd", "lbl high", "lbl low"))
    for (m, region), cs in sorted(groups(cells).items()):
        r = fit(cs)
        if r is None:
            continue
        r["level_by_level_high"] = math.sqrt(r["ms_level_by_level"])
        r["level_by_level_low"] = math.sqrt(max(0.0, r["ms_level_by_level"] - SAMPLING))
        out["%s %s" % (m, region)] = r
        pooled["ss"] += r["ms_level_by_level"] * r["df"]
        pooled["df"] += r["df"]
        pooled["bss"] += r["ms_between_studies"] * sum(len(c["means"]) - 1 for c in cs)
        pooled["bdf"] += sum(len(c["means"]) - 1 for c in cs)
        print("%-10s %6d %7d %5d %3d %10.2f %10.2f %10.2f %10.2f" % (
            "%s %s" % (m, region), r["levels"], r["studies"], r["means"], r["df"],
            math.sqrt(r["ms_between_studies"]), r["shift_sd"], r["level_by_level_high"], r["level_by_level_low"]))
    ms = pooled["ss"] / pooled["df"]
    summary = {"groups": len(out), "df": pooled["df"],
               "between_studies_rms": math.sqrt(pooled["bss"] / pooled["bdf"]),
               "level_by_level_high": math.sqrt(ms), "level_by_level_low": math.sqrt(max(0.0, ms - SAMPLING)),
               "median_level_by_level_high": float(np.median([r["level_by_level_high"] for r in out.values()])),
               "median_level_by_level_low": float(np.median([r["level_by_level_low"] for r in out.values()])),
               "median_shift_sd": float(np.median([r["shift_sd"] for r in out.values()]))}
    summary["median_shift_sd_sampling_out"] = math.sqrt(max(0.0, summary["median_shift_sd"] ** 2 - SAMPLING))
    summary["thoracic_lumbar"] = thoracic_lumbar(out)
    summary["consistent"] = consistent(summary["median_shift_sd"], ms,
                                       float(np.mean([r["levels"] for r in out.values()])))
    shift_df = [(r["studies"] - 1, r["shift_sd"]) for r in out.values()]
    summary["pooled_shift_df"] = sum(d for d, _ in shift_df)
    summary["pooled_shift_sd"] = math.sqrt(sum(d * s * s for d, s in shift_df) / summary["pooled_shift_df"])
    summary["consistent_pooled_shift"] = consistent(summary["pooled_shift_sd"], ms,
                                                    float(np.mean([r["levels"] for r in out.values()])))
    print(json.dumps(summary, indent=1))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"summary": summary, "groups": out}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
