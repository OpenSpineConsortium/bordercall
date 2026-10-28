# Copied for the cadaver-power note from the reviewers' verify-verify-published-tables/sampling_share.py, 2026-10-28.
# Unchanged: it already took its input as an argument.
#     python3 -I verify/sampling_share.py between_studies.json
"""How much sampling error the level-by-level mean square of shift_profile.py holds, under several
guesses at the earlier studies' specimen counts, and what the level-by-level and shift parts become.

Within each measure and region the means (in units of Panjabi's person SD) are fitted as level +
study by least squares. A study s with n_s specimens gives each level's mean a sampling variance
1/n_s; within one person the same measure correlates r across levels, so study s's block of the
sampling covariance is ((1 - r) I + r 11') / n_s. The common part lies in the study column and the
residual projector removes it, so E[sampling part of RSS] = (1 - r) * sum_i (1 - h_ii) / n_s(i).

    python -I sampling_share.py between_studies.json
"""
import json
import math
import sys
from collections import defaultdict

import numpy as np

FIVE = ("EPDl", "EPWl", "VBHp", "SCD", "SCW")


def groups(cells):
    by = defaultdict(list)
    for c in cells:
        by[(c["measure"], c["level"][0])].append(c)
    return by


def design(cells):
    levels = sorted({c["level"] for c in cells})
    studies = sorted({s for c in cells for s in c["means"]})
    X, y, who, lev = [], [], [], []
    for c in cells:
        for s, v in c["means"].items():
            x = np.zeros(len(levels) + len(studies))
            x[levels.index(c["level"])] = 1.0
            x[len(levels) + studies.index(s)] = 1.0
            X.append(x)
            y.append(v / c["sd"])
            who.append(s)
            lev.append(c["level"])
    return np.array(X), np.array(y), who, lev


def main(path):
    cells = [c for c in json.load(open(path))["cells"] if c["measure"] in FIVE]
    per = []
    for key, g in sorted(groups(cells).items()):
        X, y, who, lev = design(g)
        H = X @ np.linalg.pinv(X)
        df = len(y) - np.linalg.matrix_rank(X)
        if df <= 0:
            continue
        resid = y - H @ y
        per.append({"key": key, "rss": float(resid @ resid), "df": int(df),
                    "one_minus_h": 1.0 - np.diag(H), "who": who, "levels": len(set(lev)),
                    "studies": len(set(who)), "means": len(y)})
    rss = sum(p["rss"] for p in per)
    df = sum(p["df"] for p in per)
    ms = rss / df
    print("groups %d, pooled df %d, pooled MS %.5f, sqrt %.4f" % (len(per), df, ms, math.sqrt(ms)))
    # Check that the trace of (I - H) is df in every group.
    for p in per:
        assert abs(p["one_minus_h"].sum() - p["df"]) < 1e-8, p["key"]
    # Share of the present study's observations in the residual degrees of freedom.
    pres = sum(sum(l for l, s in zip(p["one_minus_h"], p["who"]) if s == "present") for p in per)
    print("present study's share of residual df: %.2f of %d (%.1f%%)" % (pres, df, 100 * pres / df))

    def share(n_earlier):
        tot = 0.0
        for p in per:
            for l, s in zip(p["one_minus_h"], p["who"]):
                n = 12.0 if s == "present" else n_earlier
                tot += l / n
        return tot / df

    print("\nexpected sampling share of the pooled MS at r = 0, and level-by-level part at each r")
    print("%-28s %8s %8s %8s %8s %8s" % ("earlier studies' n", "share", "r=0", "r=0.5", "r=0.8", "r=1"))
    for n in (6, 8, 12, 20, 30, 50, 100, float("inf")):
        sh = share(n)
        lbl = [math.sqrt(max(0.0, ms - (1 - r) * sh)) for r in (0.0, 0.5, 0.8, 1.0)]
        print("%-28s %8.4f %8.3f %8.3f %8.3f %8.3f" % (n, sh, *lbl))
    # Per-group view at r = 0: all at 12 versus earlier infinite.
    print("\nper group: MS, lbl (all 12, r=0), lbl (earlier inf, r=0)")
    for p in per:
        m = p["rss"] / p["df"]
        s_inf = sum(l / 12.0 for l, s in zip(p["one_minus_h"], p["who"]) if s == "present") / p["df"]
        print("%-8s df %2d MS %.4f  all12 %.3f  earlier-inf %.3f (share %.4f)" % (
            "%s %s" % p["key"], p["df"], m, math.sqrt(max(0, m - 1 / 12)), math.sqrt(max(0, m - s_inf)), s_inf))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
