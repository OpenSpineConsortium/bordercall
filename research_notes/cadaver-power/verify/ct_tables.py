# Copied for the cadaver-power note from the reviewers' verify-verify-simulation/ct-table-check/ct_tables.py, 2026-10-28.
# Changed: it imports the note's cadaver_power.py from the folder above (it used a copy
# identical to it before part A was rewritten; tables(), job() and the seeds are as they were)
# and takes bordercall's checkout as an argument, where it read a snapshot of schwingcheck at
# bordercall d20b78b. Not rerun for the note: its output is ct_run1_w3.log to ct_run4_w1.log (run1_w3.log to run4_w1.log there), read by summarise_runs.py.
#     python3 -I -B verify/ct_tables.py BORDERCALL run1_w3.npz 3 9001 err:58:6 errsize:58:6
#     python3 -I -B verify/ct_tables.py BORDERCALL run2_w3.npz 3 9002 plain:50:4 errsize:50:4 oracle:58:6
#     python3 -I -B verify/ct_tables.py BORDERCALL run3_w9.npz 9 9003 err:58:3 errsize:58:3 plain:50:3 oracle:58:3
#     python3 -I -B verify/ct_tables.py BORDERCALL run4_w1.npz 1 9004 err:58:3 errsize:58:3 plain:50:3 oracle:58:3
"""Tables a CT set would give, scored like cadaver_power's people-P tables against the same 300
typical columns at one width, beside the people-2000 nominal table of draw 0 (the README's
reference), each in one process.

Kinds (P people each, drawn by columns.draw_columns from a seed of their own):
  exact    noise 0, size spread 0: the note's people-P table (a fresh draw)
  err      the CT error, no size spread; SD with the error's variance taken out
  errsize  the CT error and the generator's size spread; SD with the error's variance taken out
  plain    the CT error and the size spread; the plain sample mean and SD, nothing taken out
  oracle   the CT error and the size spread; each person's values divided by the person's own
           size (known here, never in a real CT set) before the mean, and the SD with the
           error's variance over s^2 taken out: the best an estimator that takes the size out
           could do

    python3 -I -B ct_tables.py BORDERCALL OUT.npz WIDTH SEED KIND:P:N [KIND:P:N ...]
"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cadaver_power as cp  # noqa: E402


def ct_table(C, MS, pool, LEVELS, kind, P, seed):
    keys = [MS.archive_key(m) for m in pool]
    e = MS.errors(pool)[:, None]
    noise = 0.0 if kind == "exact" else MS.errors(pool)
    scale_sd = 0.0 if kind in ("exact", "err") else C.SYNTH["scale_sd"]
    spec = C.draw_columns(MS.reference(pool), ["typical"], seed, P, keys,
                          noise_mm=noise, scale_sd=scale_sd, power=MS.powers(pool))
    vals = spec.values[:, :len(LEVELS), :]                  # (people, levels, measures)
    if kind == "oracle":
        s = spec.scale[:, None, None]
        vals = vals / s                                     # every one of the seven has power 1
        emu = vals.mean(0).T.copy()
        var = vals.var(0, ddof=1).T
        e2 = (e ** 2) * np.mean(1.0 / spec.scale ** 2)
        esd = np.sqrt(np.maximum(var - e2, 0.05 * var))
        return emu, esd
    emu = vals.mean(0).T.copy()
    var = vals.var(0, ddof=1).T
    if kind in ("exact", "plain"):
        return emu, np.sqrt(var)
    return emu, np.sqrt(np.maximum(var - e ** 2, 0.05 * var))


def main(argv):
    bordercall, out, width, seed, specs = argv[0], argv[1], int(argv[2]), int(argv[3]), argv[4:]
    LEVELS, C, MS, R, S = cp.load(bordercall)
    pool = MS.select(MS.SPINEPS_7)
    keys = [MS.archive_key(m) for m in pool]
    cols = C.draw_columns(MS.reference(pool), ["typical"], cp.COLUMN_SEED, 300, keys,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))
    all_tabs = cp.tables(MS, C, LEVELS, pool, False)
    ref = [t for t in all_tabs if t[0] == "people-2000" and t[1] == "nominal" and t[2] == 0]
    tabs = list(ref)
    rng = np.random.default_rng(seed)
    for spec in specs:
        kind, P, n = spec.split(":")
        for t in range(int(n)):
            mu, sd = ct_table(C, MS, pool, LEVELS, kind, int(P), int(rng.integers(1 << 30)))
            tabs.append(("%s-%s" % (kind, P), "nominal", t, mu, sd, {}))
    cp._STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
    res = {}
    t0 = time.time()
    for i in range(len(tabs)):
        _, n, hit, top, col = cp.job((i, width))
        key = "%s|%d" % (tabs[i][0], tabs[i][2])
        res[key] = (hit, top)
        said = top >= 0.99
        print("%-16s exact %.4f ans %.4f prec %.4f (%.0f s)" % (
            key, hit.mean(), said.mean(), hit[said].mean() if said.any() else float("nan"), time.time() - t0), flush=True)
    np.savez_compressed(out, col=col, **{k + "|hit": v[0] for k, v in res.items()},
                        **{k + "|top": v[1] for k, v in res.items()})


main(sys.argv[1:])
