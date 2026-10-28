# Copied for the cadaver-power note from the reviewers' verify-simulation/run_jobs.py, 2026-10-28.
# Changed: it imports the note's cadaver_power.py from the folder above (it used a copy
# identical to it before part A was rewritten; tables(), job() and the seeds are as they were)
# and takes bordercall's checkout as an argument, where it read a snapshot of schwingcheck at
# bordercall d20b78b. Not rerun for the note: its output is r_arms_w3.log, read by summarise_runs.py.
#     python3 -I -B verify/run_jobs.py BORDERCALL r_arms_w3.npz 3 seven-r0 seven-r0.5 seven-r0.8 seven-r1 observed-0.28
"""Run chosen tables of cadaver_power at chosen widths, one process, and save per-table hit vectors.

    python3 -I -B run_jobs.py BORDERCALL OUT.npz WIDTH ARM[:RULE[:DRAW]] ...
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cadaver_power as cp

def main(argv):
    bordercall, out, width, specs = argv[0], argv[1], int(argv[2]), argv[3:]
    LEVELS, C, MS, R, S = cp.load(bordercall)
    pool = MS.select(MS.SPINEPS_7)
    keys = [MS.archive_key(m) for m in pool]
    cols = C.draw_columns(MS.reference(pool), ["typical"], cp.COLUMN_SEED, 300, keys,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))
    tabs = cp.tables(MS, C, LEVELS, pool, False)
    cp._STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
    chosen = []
    for spec in specs:
        parts = spec.split(":")
        arm = parts[0]
        rule = parts[1] if len(parts) > 1 else "nominal"
        draw = int(parts[2]) if len(parts) > 2 else None
        for i, t in enumerate(tabs):
            if t[0] == arm and t[1] == rule and (draw is None or t[2] == draw):
                chosen.append(i)
    res = {}
    t0 = time.time()
    for i in chosen:
        _, n, hit, top, col = cp.job((i, width))
        res["%s|%s|%d" % (tabs[i][0], tabs[i][1], tabs[i][2])] = (hit, top)
        print("%-28s exact %.4f  ans %.4f  prec %.4f  (%.0f s)" % ("%s/%s/%d" % tabs[i][:3], hit.mean(), (top >= .99).mean(),
              hit[top >= .99].mean() if (top >= .99).any() else float('nan'), time.time() - t0), flush=True)
    np.savez_compressed(out, col=col, **{k + "|hit": v[0] for k, v in res.items()}, **{k + "|top": v[1] for k, v in res.items()})

main(sys.argv[1:])
