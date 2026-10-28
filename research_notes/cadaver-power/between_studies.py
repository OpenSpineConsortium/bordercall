#!/usr/bin/env python3
"""How far the published cadaver studies' means differ from one another, from Panjabi's own
comparison tables.

Each of the four Panjabi papers prints a table that sets its present-study means beside earlier
studies' (cervical Table 7, thoracic Tables 8A and 8B, lumbar Table 6, facets Tables 9 and 10),
read cell by cell into bordercall's archive/bordercall/reference/provenance/provenance.csv. For
every measure and level with three or more studies this gives the SD of the studies' means, s_b,
beside the person-to-person SD of Panjabi's 12 spines at that level, sd (the dimension table's
standard error times the square root of 12; for a measure the comparison restates as the mean of
right and left, the mean of the two sides' SDs).

f_obs = s_b / sd is the spread between studies in units of one person's spread. It holds sampling
error as well as real differences, so it overstates tau / sd. f_low, the square root of
s_b^2 - sd^2 / 12 over sd, takes out the sampling error a study of 12 specimens would carry. The
comparison tables do not print the earlier studies' counts; if those studies held more than 12,
less sampling error is in s_b than is taken out, so f_low is the low side. It runs low for the
paired measures too (PDH, PDW, PDIs, Ss, 44 of the 86 cells): the SD of a left-right mean is
s * sqrt((1 + rho)/2), at most the mean of the two sides' SDs, so the error taken out is too large
there. And a median of per-cell figures that rest on 2 to 5 degrees of freedom sits below the
spread they share, which is why the summary also gives pooled moment estimates: the mean over
cells of f_obs^2, weighted by each cell's degrees of freedom (studies minus 1) or not, with 1/12
taken out or kept.

The summary also gives the measures in groups (the five that the seven SPINEPS measures read, and
the pedicles, which no SPINEPS measurer reads), and the cells again with the rows the papers' own
text attributes to another definition left out, one rule after another (DEFINITIONS), each in the
same groups too. Those summaries leave the list of cells, which shift_profile.py reads, as it was.

    python3 between_studies.py --bordercall PATH [--out FILE]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import statistics
import sys
from collections import defaultdict

COMPARISONS = ("cervical-t7", "thoracic-t8a", "thoracic-t8b", "lumbar-t6", "facets-t9", "facets-t10")
SPECIMENS = 12
# Left out whole: a comparison row whose earlier studies measured something else under the name.
LEFT_OUT = {
    # Thoracic Table 8B. Without Berry no level of the row has the three studies a cell needs.
    "PDIt": "Berry's transverse pedicle angles, which the thoracic paper (p900) says 'appeared to be "
            "grossly incorrect (eg, at T2, Berry: 137.0, Zindrick: 17.5, present study: 17.9)'",
    # Cervical Table 7. Its present column restates Panjabi's VBHp to the digit. It would also drop
    # for want of a person SD, since no dimension table of his prints a VBH, but that is an accident
    # of naming; this entry says why it is out.
    "VBH": "the earlier body heights, which the cervical paper (p868) says were 'the posterior wall "
           "height as observed from the lateral direction', 2 to 2.5 mm above Panjabi's posterior "
           "height in the midsagittal plane",
}
# Rows the papers' own text attributes to another definition: (rule, measure, region or None for
# every region, the studies left out or None for every study, where the paper says so).
DEFINITIONS = (
    ("EPAl", "EPAl", None, None,
     "cervical p868: Liu's areas 'probably' include the uncovertebral area; Francis's equal the ellipse "
     "of his own depth and width, and p868 finds the ellipse overestimates the area by 10%"),
    ("Liu's depths", "EPDl", "C", ("Liu (1986)",),
     "cervical p868: 'probably measured at the centrum midheight instead of the lower end-plate'"),
    ("midheight depths", "EPDl", "T", ("Scoles (1988)", "Cotterill (1986)"),
     "thoracic p898: the depth 'may be at the body mid-height'"),
    ("Ss", "Ss", None, None,
     "facets p1309: earlier angles are taken on the transverse plane, which 'could account for the "
     "differences in the angle comparisons of Table 10'"),
)
GROUPS = {"five": ("EPDl", "EPWl", "VBHp", "SCD", "SCW"), "pedicles": ("PDH", "PDIs", "PDW")}


def number(text: str):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def person_sd(dimension: dict, measure: str, level: str):
    """Panjabi's person SD at a level: one measure's, or the mean of its right and left sides'."""
    m = measure
    if (m, level) in dimension:
        return dimension[(m, level)]
    sides = [dimension.get((m + s, level)) for s in ("r", "l")]
    sides = [s for s in sides if s is not None]
    return sum(sides) / len(sides) if sides else None


def cell(measure: str, level: str, sd: float, by_study: dict) -> dict:
    s_b = statistics.stdev(by_study.values())
    low = math.sqrt(max(0.0, s_b * s_b - sd * sd / SPECIMENS)) / sd
    return {"measure": measure, "level": level, "studies": len(by_study), "sd": sd, "s_b": s_b,
            "range": max(by_study.values()) - min(by_study.values()),
            "f_obs": s_b / sd, "f_low": low, "means": by_study}


def describe(cells: list) -> dict:
    """Medians, quartiles and pooled moment estimates of the spread over some cells."""
    f_obs = [c["f_obs"] for c in cells]
    f_low = [c["f_low"] for c in cells]
    q = lambda xs: statistics.quantiles(xs, n=4)
    df = [c["studies"] - 1 for c in cells]
    weighted = sum(d * f * f for d, f in zip(df, f_obs)) / sum(df)
    unweighted = statistics.mean(f * f for f in f_obs)
    return {"cells": len(cells), "measures": len({c["measure"] for c in cells}),
            "f_obs": {"median": statistics.median(f_obs), "quartiles": q(f_obs)},
            "f_low": {"median": statistics.median(f_low), "quartiles": q(f_low)},
            "cells_at_zero": sum(x == 0.0 for x in f_low),
            "share_f_low_above_0.1": sum(x > 0.1 for x in f_low) / len(f_low),
            "share_f_low_above_0.3": sum(x > 0.3 for x in f_low) / len(f_low),
            "pooled": {"weighted_by_df": math.sqrt(max(0.0, weighted - 1.0 / SPECIMENS)),
                       "weighted_by_df_sampling_error_kept": math.sqrt(weighted),
                       "unweighted": math.sqrt(max(0.0, unweighted - 1.0 / SPECIMENS)),
                       "unweighted_sampling_error_kept": math.sqrt(unweighted)}}


def groups(cells: list) -> dict:
    """describe() over each of GROUPS, so the measures the rule reads are read apart from the pedicles."""
    return {name: describe([c for c in cells if c["measure"] in ms]) for name, ms in GROUPS.items()}


def without(cells: list, rules: tuple) -> list:
    """The cells again with the studies each rule names taken out, kept where three studies remain."""
    out = []
    for c in cells:
        means = dict(c["means"])
        for _, measure, region, studies, _ in rules:
            if c["measure"] == measure and (region is None or c["level"][0] == region):
                means = {} if studies is None else {s: v for s, v in means.items() if s not in studies}
        if len(means) >= 3:
            out.append(cell(c["measure"], c["level"], c["sd"], means))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bordercall", default=os.getcwd())
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    path = os.path.join(a.bordercall, "archive", "bordercall", "reference", "provenance", "provenance.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    dimension = {}
    for r in rows:
        if r["table"] not in COMPARISONS and r["study"] == "present" and r["statistic"] == "sem":
            v = number(r["value"])
            if v is not None:
                dimension.setdefault((r["measure"], r["level"]), v * math.sqrt(SPECIMENS))
    means = defaultdict(dict)
    for r in rows:
        if r["table"] in COMPARISONS and r["statistic"] == "mean" and r["study"] != "Level":
            v = number(r["value"])
            if v is not None:
                means[(r["measure"], r["level"])][r["study"]] = v
    cells = []
    for (measure, level), by_study in sorted(means.items()):
        sd = person_sd(dimension, measure, level)
        if measure in LEFT_OUT:
            continue
        if len(by_study) < 3 or not sd:
            continue
        cells.append(cell(measure, level, sd, by_study))
    by_measure = defaultdict(list)
    for c in cells:
        by_measure[c["measure"]].append(c)
    print("%-6s %5s %7s %8s %8s %8s %8s" % ("measure", "cells", "studies", "sd mm", "s_b mm", "f_obs", "f_low"))
    for m, cs in sorted(by_measure.items()):
        print("%-6s %5d %7.1f %8.2f %8.2f %8.2f %8.2f" % (
            m, len(cs), statistics.median(c["studies"] for c in cs), statistics.median(c["sd"] for c in cs),
            statistics.median(c["s_b"] for c in cs), statistics.median(c["f_obs"] for c in cs),
            statistics.median(c["f_low"] for c in cs)))
    summary = describe(cells)
    summary["left_out"] = LEFT_OUT
    summary["groups"] = groups(cells)
    summary["definitions_left_out"] = []
    for k in range(1, len(DEFINITIONS) + 1):
        kept = without(cells, DEFINITIONS[:k])
        summary["definitions_left_out"].append(
            dict(describe(kept), rules=[d[0] for d in DEFINITIONS[:k]], groups=groups(kept)))
    summary["definitions"] = {d[0]: d[4] for d in DEFINITIONS}
    print(json.dumps(summary, indent=1))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"summary": summary, "cells": cells}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
