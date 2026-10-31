"""Choosing the rule by held-out prediction: the records of synthval/select.py.

    python3 -I run_select.py --out records/select            # about ten minutes on 4 CPUs
    python3 -I run_select.py --out /tmp/x --quick             # the same path on few columns

Run from this folder with the Python that holds bordercall's pinned packages, after run_strata.py's
snapshot check passes (the same snapshot, the same cells, the same populations on the same seeds).
Every paper of the strata's leave-one-out is held out in turn; the candidates (select.CANDIDATES: the
five of select.CORE, and the rule without each paper of select.EXCLUDABLE and with one vote per
population, each plain and tempered) are built on the other papers, the SD factor and the
temperatures set by a second leave-one-out inside them, and all
are scored on the held-out population at one, two and three bodies on the same fields: scores.csv
(one row a paper, width and candidate, the own table beside them), bins.csv (the calibration curve's
bins per paper), k_curve.csv and t_curve.csv (the held-out scores at every factor and temperature,
drawn to show where the inner choice fell, never to choose by), choices.csv (each paper's knobs and
the inner curves they came from), summary.csv (each candidate over the populations), calibration.csv
(the curves pooled over the populations) and select.json (the winner, the sizes, the grids, the seeds,
the commit, the snapshot's digest and the code).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

import numpy as np  # noqa: E402

from synthval import papers_table as PT  # noqa: E402
from synthval import select as SEL  # noqa: E402
from synthval import strata as ST  # noqa: E402
from run import code_digests, log, write_csv, write_json  # noqa: E402

WIDTHS = (1, 2, 3)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--columns", type=int, default=1000)
    ap.add_argument("--inner-columns", type=int, default=SEL.INNER_COLUMNS)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    if args.quick:
        args.columns, args.inner_columns = 40, 20
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    started = time.time()
    code = code_digests()
    problems = PT.check_snapshot_all()
    if problems:
        raise SystemExit("; ".join(problems))
    rows = PT.load_rows_all()
    series, _ = PT.select_all(rows)
    voc = PT.load_vocabulary()
    cells = ST.strata_of(series)
    ST.set_between(cells)

    got = SEL.select(cells, voc, args.columns, WIDTHS, args.inner_columns, log=log)
    write_csv(out, "scores.csv", got["scores"])
    write_csv(out, "bins.csv", got["bins"])
    write_csv(out, "k_curve.csv", got["k_curve"])
    write_csv(out, "t_curve.csv", got["t_curve"])
    write_csv(out, "choices.csv", got["choices"])
    summary = SEL.summarise(got["scores"], got["bins"], WIDTHS)
    write_csv(out, "summary.csv", summary)
    calibration = []
    for name in (SEL.OWN,) + SEL.CANDIDATES:
        for w in WIDTHS:
            calibration += SEL.pooled_bins(got["bins"], name, w)
    write_csv(out, "calibration.csv", calibration)
    won = SEL.winner(summary, WIDTHS)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    papers = sorted({r["paper"] for r in got["scores"]})
    write_json(out, "select.json", {
        "command": "python3 -I run_select.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "sizes": {"columns": args.columns, "inner_columns": args.inner_columns, "widths": list(WIDTHS), "populations": len(papers)},
        "seeds": {"columns": ST.SEED_COLUMNS,
                  "rule": "a paper's columns on SEED_COLUMNS + its index among the papers sorted by name, as the strata draw them; "
                          "an inner fold's on that + 1000 + the fold's index"},
        "grids": {"k": list(SEL.K_GRID), "temperature": list(SEL.T_GRID)},
        "candidates": list(SEL.CANDIDATES), "core": list(SEL.CORE), "exclusion": list(SEL.EXCLUSION),
        "excludable": list(SEL.EXCLUDABLE), "bases": list(SEL.BASES), "papers": papers,
        "choices": {c["paper"]: {"k": c["k"], "t": {str(w): c["t_%d" % w] for w in WIDTHS},
                                 "t_by": {b: {str(w): c["t_%s_%d" % (SEL.slug(b), w)] for w in WIDTHS} for b in SEL.BASES[1:]},
                                 "inner_folds": c["inner_folds"]} for c in got["choices"]},
        "summary": summary, "winner": won,
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "code": code})
    log("done in %d s; by log score %s, by accuracy %s" % (round(time.time() - started), won["by_log_score"], won["by_accuracy"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
