# Copied for the cadaver-power note from the reviewers' verify-verify-published-tables/r0_large.py,
# 2026-10-28. Changed: it imports the note's cadaver_power.py from the folder above, where it used a
# byte-for-byte copy made before part A was rewritten (tables(), job() and the seeds are as they were).
# Not rerun for the note: its outputs are run1_base_lbl0.233.json and run2_lbl0.174_lbl0.135.json,
# read by summarise_runs.py.
"""The seven-r0 row of part C again, on the very same draws, with the level-by-level part that r = 0
gives when the earlier studies had more than 12 specimens.

cadaver_power.py draws every table from one generator in a fixed order. This replays that order
(the people tables' seeds, the profile and shift draws, then every DISAGREEMENTS arm's z and
level-by-level normals) without building the tables it does not need, keeps the draws of seven-r0,
and builds from them seven-r0 as published and the same tables with another shift and
level-by-level SD, so a difference between them is the size of the level-by-level part alone.
Nominal rules only; the reference is the generator's own table (the published minus_true).

    python3 -I verify/r0_large.py --bordercall BORDERCALL --columns 300 --base --arm lbl0.233:0.57:0.233 --out run1_base_lbl0.233.json
    python3 -I verify/r0_large.py --bordercall BORDERCALL --columns 300 --arm lbl0.174:0.57:0.174 --arm lbl0.135:0.57:0.135 --out run2_lbl0.174_lbl0.135.json
"""
import argparse
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402

import cadaver_power as CP  # noqa: E402  (the note's; tables(), job() and the seeds are as they were)


def replay(MS, LEVELS, pool):
    mu, sd = MS.arrays(pool)
    rng = np.random.default_rng(CP.TABLE_SEED)
    for P, n_tables in CP.PEOPLE.items():
        for _ in range(n_tables):
            rng.integers(1 << 30)
    for kind in ("profile", "shift"):
        for _ in CP.FRACTIONS:
            for _ in range(CP.OFFSET_TABLES):
                if kind == "profile":
                    rng.normal(size=mu.shape)
                else:
                    rng.normal(size=(mu.shape[0], 1))
    draws = {}
    for name, shift_sd, tl, level_sd in CP.DISAGREEMENTS:
        for _ in range(CP.OFFSET_TABLES):
            z = rng.normal(size=(mu.shape[0], 3))
            if tl is not None:
                z[:, 2] = tl * z[:, 1] + math.sqrt(1.0 - tl ** 2) * z[:, 2]
            e = rng.normal(size=mu.shape)
            draws.setdefault(name, []).append((z, e))
    return mu, sd, draws


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bordercall", required=True)
    ap.add_argument("--columns", type=int, default=300)
    ap.add_argument("--base", action="store_true", help="also run seven-r0 as published")
    ap.add_argument("--arm", action="append", default=[], help="name:shift:level_by_level on seven-r0's draws")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    LEVELS, C, MS, R, S = CP.load(a.bordercall)
    pool = MS.select(MS.SPINEPS_7)
    mu, sd, draws = replay(MS, LEVELS, pool)
    region = np.array(["CTL".index(name[0]) for name in LEVELS])
    tabs = [("true", "nominal", 0, mu, sd, {})]
    specs = ([("seven-r0", 0.57, 0.0)] if a.base else []) + [
        (s.split(":")[0], float(s.split(":")[1]), float(s.split(":")[2])) for s in a.arm]
    for name, shift_sd, level_sd in specs:
        for t, (z, e) in enumerate(draws["seven-r0"]):
            tabs.append((name, "nominal", t, mu + sd * (shift_sd * z[:, region] + level_sd * e), sd,
                         {"shift": shift_sd, "level_by_level": level_sd}))
    keys = [MS.archive_key(m) for m in pool]
    cols = C.draw_columns(MS.reference(pool), ["typical"], CP.COLUMN_SEED, a.columns, keys,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))
    CP._STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
    t0 = time.time()
    res = {}
    for n in sorted(CP.WIDTHS, reverse=True):
        for i in range(len(tabs)):
            _, _, hit, top, col = CP.job((i, n))
            res[(i, n)] = (hit, top, col)
            print("  table %d width %d done, %.0f s" % (i, n, time.time() - t0), flush=True)
    out = {}
    for n in CP.WIDTHS:
        ref = res[(0, n)][0]
        by = {}
        for i, (arm, rule, draw, *_rest) in enumerate(tabs):
            hit, top, col = res[(i, n)]
            row = CP.rates(hit, top, col, S)
            row["minus_true"] = CP.paired(hit, ref, col, S)
            by.setdefault(arm, []).append(row)
        for arm, rows in by.items():
            out.setdefault(arm, {})[str(n)] = {
                "exact": float(np.mean([r["exact"] for r in rows])),
                "minus_true": float(np.mean([r["minus_true"]["minus_ref"] for r in rows])),
                "minus_true_each": [r["minus_true"]["minus_ref"] for r in rows],
                "precision": float(np.mean([r["precision"] for r in rows])),
                "precision_each": [r["precision"] for r in rows],
                "answered": float(np.mean([r["answered"] for r in rows])),
                "errors_at_claim": int(sum(r["errors_at_claim"] for r in rows)),
                "n_answered": int(sum(r["n_answered"] for r in rows)),
                "tables": len(rows)}
    print("%-14s %s" % ("arm", "  ".join("%d bod: exact  -true  prec@.99 (errors/answered)" % n for n in CP.WIDTHS)))
    for arm, byn in out.items():
        cells = []
        for n in CP.WIDTHS:
            s = byn[str(n)]
            cells.append("%12.1f%% %+6.1f %8.2f%% (%d/%d)" % (100 * s["exact"], 100 * s["minus_true"],
                                                          100 * s["precision"], s["errors_at_claim"], s["n_answered"]))
        print("%-14s %s" % (arm, "  ".join(cells)))
    print("seconds %.0f" % (time.time() - t0))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"columns": a.columns, "specs": specs, "arms": out}, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
