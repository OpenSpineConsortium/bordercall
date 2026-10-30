"""Tan 2004's population apart from the rest: the spread between populations, part A's worth, the
prediction for one more population (merged, the rest alone, the two strata as a mixture, with
leave-one-out coverage) and part C's naming loss, before (pooled) and after (two strata).
synthval/tan.py says what each is.

    python3 -I tan_strata.py --out records/tan-strata --quick    # the record in place: few columns, about a minute
    python3 -I tan_strata.py --out records/tan-strata            # about ten minutes on 4 CPUs

Everything is synthetic but the papers' own numbers, read from the snapshot run.py reads.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

from synthval import literature as L  # noqa: E402
from synthval import power as PW  # noqa: E402
from synthval import tan as T  # noqa: E402

from run import write_csv, write_json  # noqa: E402


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--columns", type=int, default=300)
    ap.add_argument("--tables", type=int, default=4)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    if args.quick:
        args.columns, args.tables = 40, 2
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    started = time.time()
    series, _ = L.select(L.load_rows())
    rest, tan = T.split(series)

    matched = T.matched_spread(series)
    write_csv(out, "matched_cells.csv", matched)
    prediction = T.prediction_by_stratum(series)
    write_csv(out, "prediction_cells.csv", prediction)
    splits = {"pooled": PW.shift_split(series), "rest": PW.shift_split(rest)}
    calibrated = {name: {"panjabi": PW.calibrated_median_f(v, "panjabi"), "literature": PW.calibrated_median_f(v, "literature")}
                  for name, v in (("pooled", series), ("rest", rest))}
    seven = [m for m in T.MS.select(T.MS.SPINEPS_7)]
    _, _, filled = T.tan_table(series, seven)

    rows = T.naming_by_stratum(series, splits, columns=args.columns, tables=args.tables)
    write_csv(out, "naming.csv", rows)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    write_json(out, "tan_strata.json", {
        "command": "python3 -I tan_strata.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit, "columns": args.columns, "tables": args.tables,
        "series": {"all": len(series), "rest": len(rest), "tan": len(tan)},
        "matched_spread": T.spread_summary(matched), "prediction": T.prediction_summary(prediction),
        "split": splits, "calibrated_median_f": calibrated,
        "tan_table_filled": filled, "naming": T.naming_summary(rows), "gold_against_tan": T.gold_against_tan(matched),
        "seconds": round(time.time() - started, 1)})


if __name__ == "__main__":
    main()
