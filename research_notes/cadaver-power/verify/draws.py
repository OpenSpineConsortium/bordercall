# Copied for the cadaver-power note from the reviewers' verify-verify-simulation/draws.py, 2026-10-28.
# Changed: it imports the note's cadaver_power.py from the folder above (tables() and the seeds are as
# they were) and takes bordercall's checkout as an argument. It scores nothing, so it runs in seconds.
#     python3 -I -B verify/draws.py BORDERCALL seven-r0 4102
"""The disagreement arms' table draws, as cadaver_power.tables() makes them, at one TABLE_SEED or
several: for each table, the realized region shifts (in person SDs), their RMS about 0 and SD,
the C-T and T-L steps they make, and the level-by-level residual.

    python3 -I -B draws.py BORDERCALL ARM SEED [SEED ...]
"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cadaver_power as cp

LEVELS, C, MS, R, S = cp.load(sys.argv[1])
pool = MS.select(MS.SPINEPS_7)
keys = [MS.archive_key(m) for m in pool]
mu, sd = MS.arrays(pool)
region = np.array(["CTL".index(n[0]) for n in LEVELS])
arm = sys.argv[2]
print("measures", keys)
allrms = []
for seed in [int(s) for s in sys.argv[3:]]:
    cp.TABLE_SEED = seed
    tabs = cp.tables(MS, C, LEVELS, pool, False)
    rows = [t for t in tabs if t[0] == arm and t[1] == "nominal"]
    for t in rows:
        d = (t[3] - mu) / sd                                          # (7, 22)
        sh = np.stack([d[:, region == r].mean(1) for r in range(3)], 1)   # (7, 3)
        resid = d - sh[:, region]
        rms = math.sqrt((sh ** 2).mean())
        allrms.append(rms)
        ct, tl = sh[:, 1] - sh[:, 0], sh[:, 2] - sh[:, 1]
        print("seed %d table %d: shift RMS %.3f (arm %.2f), SD %.3f; |C-T step| RMS %.3f, |T-L step| RMS %.3f; "
              "T-L corr %.2f; resid SD %.3f" % (seed, t[2], rms, t[5]["shift"], sh.std(), math.sqrt((ct ** 2).mean()),
                                                math.sqrt((tl ** 2).mean()), np.corrcoef(sh[:, 1], sh[:, 2])[0, 1], resid.std()))
        print("    C shifts", np.round(sh[:, 0], 2), " T", np.round(sh[:, 1], 2), " L", np.round(sh[:, 2], 2))
print("all tables: shift RMS mean %.3f, pooled RMS %.3f over %d tables" % (np.mean(allrms), math.sqrt(np.mean(np.square(allrms))), len(allrms)))
