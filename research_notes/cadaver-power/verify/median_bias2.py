# Copied for the cadaver-power note from the reviewers' verify-published-tables/median_bias2.py, 2026-10-28.
# Unchanged: it already took its input as an argument.
#     python3 -I verify/median_bias2.py between_studies.json
"""Median of per-cell f_low over the 86 cells' study counts, Panjabi's study at 12 and the others at n_other."""
import json, math, sys
import numpy as np
ks = np.array([c["studies"] for c in json.load(open(sys.argv[1]))["cells"]])
rng = np.random.default_rng(7)
def run(t, n_other, reps=1500):
    meds = []
    for _ in range(reps):
        f = []
        for k in ks:
            n = np.array([12] + [n_other] * (k - 1), float)
            x = t * rng.normal(size=k) + rng.normal(size=k) / np.sqrt(n)
            f.append(math.sqrt(max(0.0, x.var(ddof=1) - 1 / 12)))
        meds.append(np.median(f))
    return np.mean(meds)
for n_other in (12, 50, 200):
    row = ["true %.2f -> %.3f" % (t, run(t, n_other)) for t in (0.39, 0.45, 0.5, 0.55, 0.6)]
    print("others at n=%d:" % n_other, "; ".join(row))
