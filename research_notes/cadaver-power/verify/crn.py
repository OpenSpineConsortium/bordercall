# Copied for the cadaver-power note from the reviewers' verify-simulation/crn.py, 2026-10-28.
# Changed: it imports the note's cadaver_power.py from the folder above (it used a copy
# identical to it before part A was rewritten; tables(), job() and the seeds are as they were)
# and takes bordercall's checkout as an argument, where it read a snapshot of schwingcheck at
# bordercall d20b78b. Not rerun for the note: its output is crn_a_w3.log, read by summarise_runs.py.
#     python3 -I -B verify/crn.py BORDERCALL crn_a_w3.npz 3 8 r0=0.57,0.7,0.0 r0.5=0.54,0.7,0.19
"""The disagreement arms again with common random numbers: every arm uses the same standard-normal
draws for its region shifts and its level-by-level part, scaled by the arm's sizes, so differences
between arms come from the sizes alone. Same 300 typical columns and same rule as cadaver_power.

    python3 -I -B crn.py BORDERCALL OUT.npz WIDTH N_TABLES ARM ...

ARM is name=shift,thoracic_lumbar,level (thoracic_lumbar 'none' for every region apart).
"""
import math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cadaver_power as cp

SEED = 99001

def main(argv):
    bordercall, out, width, n_tables, specs = argv[0], argv[1], int(argv[2]), int(argv[3]), argv[4:]
    LEVELS, C, MS, R, S = cp.load(bordercall)
    pool = MS.select(MS.SPINEPS_7)
    keys = [MS.archive_key(m) for m in pool]
    cols = C.draw_columns(MS.reference(pool), ["typical"], cp.COLUMN_SEED, 300, keys,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))
    mu, sd = MS.arrays(pool)
    region = np.array(["CTL".index(name[0]) for name in LEVELS])
    rng = np.random.default_rng(SEED)
    draws = [(rng.normal(size=(mu.shape[0], 3)), rng.normal(size=mu.shape)) for _ in range(n_tables)]
    tabs = []
    for spec in specs:
        name, vals = spec.split("=")
        shift_sd, tl, level_sd = vals.split(",")
        shift_sd, level_sd = float(shift_sd), float(level_sd)
        tl = None if tl == "none" else float(tl)
        for t, (z0, e) in enumerate(draws):
            z = z0.copy()
            if tl is not None:
                z[:, 2] = tl * z[:, 1] + math.sqrt(1.0 - tl ** 2) * z[:, 2]
            tmu = mu + sd * (shift_sd * z[:, region] + level_sd * e)
            tabs.append((name, "nominal", t, tmu, sd, {}))
    cp._STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
    res = {}
    t0 = time.time()
    for i in range(len(tabs)):
        _, n, hit, top, col = cp.job((i, width))
        res["%s|%d" % (tabs[i][0], tabs[i][2])] = (hit, top)
        said = top >= 0.99
        print("%-14s %d exact %.4f ans %.4f prec %.4f (%.0f s)" % (tabs[i][0], tabs[i][2], hit.mean(), said.mean(),
              hit[said].mean() if said.any() else float("nan"), time.time() - t0), flush=True)
    np.savez_compressed(out, col=col, **{k + "|hit": v[0] for k, v in res.items()}, **{k + "|top": v[1] for k, v in res.items()})

main(sys.argv[1:])
