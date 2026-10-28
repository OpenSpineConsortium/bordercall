# Copied for the cadaver-power note from the reviewers' verify-simulation/ct_people.py, 2026-10-28.
# Changed: it imports the note's cadaver_power.py from the folder above (it used a copy
# identical to it before part A was rewritten; tables(), job() and the seeds are as they were)
# and takes bordercall's checkout as an argument, where it read a snapshot of schwingcheck at
# bordercall d20b78b. Not rerun for the note: its output is ct58_w3.log and ct58size_w3.log, read by summarise_runs.py.
#     python3 -I -B verify/ct_people.py BORDERCALL ct58_w3.npz 3 58 6 0.0 5150
#     python3 -I -B verify/ct_people.py BORDERCALL ct58size_w3.npz 3 58 6 0.07 5151
"""A table from P CTs: people drawn with the measures' CT errors (and, optionally, the size spread),
each level's mean the sample mean and its SD the sample SD with the CT error's variance taken out,
scored like cadaver_power's people-P tables at one width against the same 300 columns.

    python3 -I -B ct_people.py BORDERCALL OUT.npz WIDTH P N_TABLES SCALE_SD SEED
"""
import math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cadaver_power as cp

def main(argv):
    bordercall, out, width, P, n_tables, scale_sd, seed = argv[0], argv[1], int(argv[2]), int(argv[3]), int(argv[4]), float(argv[5]), int(argv[6])
    LEVELS, C, MS, R, S = cp.load(bordercall)
    pool = MS.select(MS.SPINEPS_7)
    keys = [MS.archive_key(m) for m in pool]
    cols = C.draw_columns(MS.reference(pool), ["typical"], cp.COLUMN_SEED, 300, keys,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))
    e = MS.errors(pool)[:, None]
    rng = np.random.default_rng(seed)
    tabs = []
    for t in range(n_tables):
        spec = C.draw_columns(MS.reference(pool), ["typical"], int(rng.integers(1 << 30)), P, keys,
                              noise_mm=MS.errors(pool), scale_sd=scale_sd, power=MS.powers(pool))
        vals = spec.values[:, :len(LEVELS), :]
        emu = vals.mean(0).T.copy()
        var = vals.var(0, ddof=1).T
        esd = np.sqrt(np.maximum(var - e ** 2, 0.05 * var))
        tabs.append(("ct-%d" % P, "nominal", t, emu, esd, {}))
    cp._STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
    res = {}
    t0 = time.time()
    for i in range(len(tabs)):
        _, n, hit, top, col = cp.job((i, width))
        res["%s|%d" % (tabs[i][0], tabs[i][2])] = (hit, top)
        said = top >= 0.99
        print("%s %d exact %.4f ans %.4f prec %.4f (%.0f s)" % (tabs[i][0], i, hit.mean(), said.mean(), hit[said].mean(), time.time() - t0), flush=True)
    np.savez_compressed(out, col=col, **{k + "|hit": v[0] for k, v in res.items()}, **{k + "|top": v[1] for k, v in res.items()})

main(sys.argv[1:])
