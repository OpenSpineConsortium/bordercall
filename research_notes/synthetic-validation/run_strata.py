"""Every paper its own population: the records of synthval/strata.py, the rule predicted for a
population it has not seen.

    python3 -I run_strata.py --out records/strata            # about two minutes on 4 CPUs
    python3 -I run_strata.py --out /tmp/x --quick             # the same path on few columns

Run from this folder with the Python that holds bordercall's pinned packages, after run.py, whose
records/power.json gives the calibrated split a drawn population's shift takes its share from.
Three readings, each on the lumbar run L1 to L5 and each paired on the same fields: every paper
scored on the measures it prints at every lumbar level (loo.csv), every paper that prints the
pedicle's width and height scored on those two (common.csv), and populations drawn from the
random-effects model itself (new_populations.csv); strata_cells.csv is every placed cell with its
strata, its tau and where the tau came from; strata.json the pooled readings, the sizes, the seeds,
the commit, the snapshot's digest and the code. The quick lumbar run is not the second part's grid
search, which stays as it is (the owner's word of 2026-10-29: no large rerun while the populations
move).
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

from schwingcheck import measures as MS  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import strata as ST  # noqa: E402
from run import code_digests, log, write_csv, write_json  # noqa: E402

# 1, 2 and 3 bodies over L1 to L5: five places, four and three; five bodies would leave one place, so nothing to name.
WIDTHS = (1, 2, 3)
COMMON_READING = "the pedicle's width and height"
MODEL_READING = "a population drawn from the model"


def seven_keys() -> list:
    to_panjabi = PT._reread_to_panjabi()
    return [to_panjabi[k] for k in MS.SPINEPS_7]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--records", default=os.path.join(HERE, "records"), help="the first part's records, for the split's share")
    ap.add_argument("--columns", type=int, default=1000)
    ap.add_argument("--tables", type=int, default=8)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    if args.quick:
        args.columns, args.tables = 40, 2
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
    borrowed = ST.set_between(cells)
    write_csv(out, "strata_cells.csv", ST.cell_rows(cells))
    with open(os.path.join(args.records, "power.json"), encoding="utf-8") as fh:
        split = json.load(fh)["split"]["all"]
    share = ST.shift_share(split)

    log("leave one paper out, every measure the paper prints")
    loo = ST.leave_one_out(cells, voc, args.columns, WIDTHS)
    write_csv(out, "loo.csv", loo)
    log("leave one paper out, %s" % COMMON_READING)
    common = ST.leave_one_out(cells, voc, args.columns, WIDTHS, keys=ST.COMMON, reading=COMMON_READING)
    write_csv(out, "common.csv", common)
    log("populations drawn from the model, the seven")
    drawn = ST.new_populations(cells, voc, seven_keys(), share, args.columns, args.tables, WIDTHS, reading=MODEL_READING)
    write_csv(out, "new_populations.csv", drawn)

    pooled = ST.pooled_losses(loo + common + drawn, WIDTHS)
    ratio = [c.predictive_sd / c.pool.sd for c in cells if c.pool.sd > 0]
    tau_from = {}
    for c in cells:
        tau_from[c.tau_from] = tau_from.get(c.tau_from, 0) + 1
    papers = {}
    for r in loo:
        papers.setdefault(r["paper"], {"n_measures": r["n_measures"], "measures": r["measures"].split(";"),
                                       "cells_with_own_sd": r["cells_with_own_sd"], "cells": r["cells"], "people": r["people"]})
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    write_json(out, "strata.json", {
        "command": "python3 -I run_strata.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "sizes": {"columns": args.columns, "tables": args.tables, "widths": list(WIDTHS)},
        "seeds": {"columns": ST.SEED_COLUMNS, "tables": ST.SEED_TABLES},
        "cells": {"placed": len(cells), "tau_from": tau_from,
                  "predictive_over_sd_quartiles": [float(q) for q in np.quantile(ratio, [0.25, 0.5, 0.75])],
                  "borrowed_f_by_measure": borrowed[0], "borrowed_f_overall": borrowed[1],
                  "min_series_for_tau": ST.MIN_SERIES_FOR_TAU},
        "share_of_spread_as_one_shift": share, "split": split,
        "papers": papers, "common": {"keys": list(ST.COMMON), "papers": sorted({r["paper"] for r in common})},
        "model_keys": seven_keys(), "pooled": pooled, "arms": list(ST.ARMS), "loss_se_floor": ST.LOSS_SE_FLOOR,
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "code": code})
    log("done in %d s" % round(time.time() - started))
    return 0


if __name__ == "__main__":
    sys.exit(main())
