# Copied for the cadaver-power note from the reviewers' verify-verify-simulation/run.py, 2026-10-28.
# Changed: it imports the note's cadaver_power.py from the folder above (it used a copy
# identical to it before part A was rewritten; tables(), job() and the seeds are as they were)
# and takes bordercall's checkout as an argument, where it read a copy of the live schwingcheck
# (bordercall d20b78b's code). Not rerun for the note: its output is fresh_w1.log, fresh_w3.log, fresh_w9.log and orig_w3.log, read by summarise_runs.py.
#     python3 -I -B verify/run.py BORDERCALL fresh_w3.npz 3 seven-r0 7001 7002 7003 7004   (and widths 1 and 9;
#     orig_w3.log is the same with the seed 4102 alone)
"""Score the nominal tables of one arm, drawn by cadaver_power.tables() itself at one or more
TABLE_SEEDs, on the same 300 typical columns and with the same rule as cadaver_power's part B, in
one process. Prints each table's share named exactly, its loss against the 2,000-person table of
the original run (draw 0, TABLE_SEED 4102, the README's reference), the share answered at 0.99 and
the precision of those answers.

    python3 -I -B run.py BORDERCALL OUT.npz WIDTH ARM SEED [SEED ...]
"""
import math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cadaver_power as cp

bordercall, out, width, arm, seeds = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], [int(s) for s in sys.argv[5:]]
LEVELS, C, MS, R, S = cp.load(bordercall)
pool = MS.select(MS.SPINEPS_7)
keys = [MS.archive_key(m) for m in pool]
cols = C.draw_columns(MS.reference(pool), ["typical"], cp.COLUMN_SEED, 300, keys,
                      noise_mm=MS.errors(pool), power=MS.powers(pool))
cp.TABLE_SEED = 4102
ref_tab = [t for t in cp.tables(MS, C, LEVELS, pool, False) if t[0] == "people-2000" and t[1] == "nominal"][0]
tabs = [ref_tab]
for seed in seeds:
    cp.TABLE_SEED = seed
    tabs += [t for t in cp.tables(MS, C, LEVELS, pool, False) if t[0] == arm and t[1] == "nominal"]
cp._STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
t0 = time.time()
saved = {}
_, _, ref_hit, ref_top, col = cp.job((0, width))
print("reference people-2000/nominal/0 (seed 4102): exact %.5f  answered %.4f  precision %.5f" % (
    ref_hit.mean(), (ref_top >= 0.99).mean(), ref_hit[ref_top >= 0.99].mean()), flush=True)
saved["ref|hit"], saved["ref|top"] = ref_hit, ref_top
k = 0
for i in range(1, len(tabs)):
    seed = seeds[(i - 1) // cp.OFFSET_TABLES]
    _, _, hit, top, col = cp.job((i, width))
    said = top >= 0.99
    print("%s seed %d draw %d: exact %.4f  loss %+.2f  answered %.4f  n_ans %d  wrong %d  precision %.4f  (%.0f s)" % (
        arm, seed, tabs[i][2], hit.mean(), 100 * (hit.mean() - ref_hit.mean()), said.mean(), said.sum(),
        (said & ~hit).sum(), hit[said].mean() if said.any() else float("nan"), time.time() - t0), flush=True)
    saved["%d|%d|hit" % (seed, tabs[i][2])], saved["%d|%d|top" % (seed, tabs[i][2])] = hit, top
np.savez_compressed(out, col=col, **saved)
