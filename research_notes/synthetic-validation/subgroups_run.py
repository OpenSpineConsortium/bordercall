"""The subgroup meta-analysis of the published series by every population variable, cell by
cell: the test for subgroup differences and the share of the spread each variable accounts for,
every value of the main variables against the rest as Tan 2004 was read, and the within-paper
contrasts a paper prints apart (synthval/subgroups.py says what each is; synthval/register.py
and data/populations.csv hold the variables).

    python3 -I subgroups_run.py --out records/subgroups       # a few seconds

Everything is the papers' own numbers, read from the snapshot run.py reads, with no draw.
"""
from __future__ import annotations

import argparse
import collections
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

from synthval import literature as L  # noqa: E402
from synthval import register as RG  # noqa: E402
from synthval import subgroups as SG  # noqa: E402

from run import write_csv, write_json  # noqa: E402

# sex is read only as a within-paper contrast: under the main selection the series' sex says how a
# paper reported (all, pooled, not stated, one sex), not who its people were
ANALYSED = ("paper", "cohort", "modality", "country", "region", "ancestry", "specimen", "age_band", "decade")
AGAINST_REST = ("paper", "ancestry", "specimen", "region", "country", "modality", "age_band", "decade")
CONTRASTS = (("sex", ("male", "female")), ("ancestry", ("African American", "Caucasian")))
LEAST_CELLS = 3


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    started = time.time()
    rows = L.load_rows()
    series, _ = L.select(rows)
    apart, why_apart = L.select(rows, strata=L.STRATA_APART)
    register = RG.load()
    problems = RG.check(series, register) + RG.check(apart, register)
    if problems:
        raise SystemExit("the register does not hold together:\n" + "\n".join(problems))
    usable = [s for s in series if L.usable(s)]
    values = {v: dict(collections.Counter(RG.tag(s, register)[v] for s in usable).most_common()) for v in RG.VARIABLES}

    analysis = []
    for v in ANALYSED:
        analysis += SG.analysis(series, v, register)
    write_csv(out, "analysis.csv", analysis)
    against, against_summary = [], {}
    for v in AGAINST_REST:
        got, summary = SG.each_against_rest(series, v, register, least_cells=LEAST_CELLS)
        against += got
        against_summary[v] = summary
    write_csv(out, "against_rest.csv", against)
    contrasts, contrast_summary = [], {}
    for v, pair in CONTRASTS:
        got = SG.paired_contrast(apart, v, pair, register)
        contrasts += got
        contrast_summary["%s: %s - %s" % (v, pair[0], pair[1])] = SG.contrast_summary(got)
    write_csv(out, "contrasts.csv", contrasts)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    write_json(out, "subgroups.json", {
        "command": "python3 -I subgroups_run.py --out %s" % os.path.relpath(out, HERE), "bordercall_commit": commit,
        "register": {"cohorts": len(register), "series": len(series), "usable": len(usable),
                     "apart_series": len(apart), "apart_usable": sum(1 for s in apart if L.usable(s)),
                     "sex_apart_series": sum(1 for s in apart if s.flag.startswith("sex apart")), "values": values},
        "least_cells": LEAST_CELLS, "analysis": SG.analysis_summary(analysis), "against_rest": against_summary,
        "contrasts": contrast_summary, "seconds": round(time.time() - started, 1)})


if __name__ == "__main__":
    main()
