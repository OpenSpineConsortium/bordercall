# Copied for the cadaver-power note from the reviewers' verify-verify-simulation/median-shift-check/median_bias.py,
# 2026-10-28. It imported a copy of shift_profile.py (sp_orig.py) from a folder named on the command line; it now
# imports this folder's parent's shift_profile.py, whose groups() and fit() are that copy's unchanged (the file
# gained only the pooled-shift summary since), and takes the cells file and the two SDs as arguments. It scores
# no rule and draws no table: it refits the split many times, so it runs in seconds.
#     python3 -I -B verify/median_shift.py between_studies.json 0.753 0.279 > verify/median_shift.log
"""Under one common shift SD, where does the median of the five measures' 11 group shift SDs fall
against their df-pooled value? Uses shift_profile.py's own fit() on the real cell layout (levels,
studies, which study gives which level), replacing the means with a study shift and level-by-level
noise, both in units of each level's person SD."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import shift_profile as SP

cells = json.load(open(sys.argv[1]))["cells"]
keep = ("EPDl", "EPWl", "VBHp", "SCD", "SCW")
cells = [c for c in cells if c["measure"] in keep]
grp = {k: v for k, v in SP.groups(cells).items() if SP.fit(v) is not None}
rng = np.random.default_rng(11)
SIG_SHIFT, SIG_LBL = float(sys.argv[2]), float(sys.argv[3])
OBSERVED = (0.5898, 0.7526)  # shift_profile_seven.json: the median and the df-pooled shift SD
med, pool, ratio = [], [], []
for it in range(2000):
    sds, dfs = [], []
    for key, cs in grp.items():
        studies = sorted({s for c in cs for s in c["means"]})
        sh = dict(zip(studies, rng.normal(0, SIG_SHIFT, len(studies))))
        new = []
        for c in cs:
            m = {s: (c["sd"] * (sh[s] + rng.normal(0, SIG_LBL))) for s in c["means"]}
            new.append({"measure": c["measure"], "level": c["level"], "sd": c["sd"], "means": m})
        r = SP.fit(new)
        sds.append(r["shift_sd"]); dfs.append(r["studies"] - 1)
    sds, dfs = np.array(sds), np.array(dfs)
    med.append(np.median(sds)); p = math.sqrt((dfs * sds ** 2).sum() / dfs.sum()); pool.append(p)
    ratio.append(np.median(sds) / p)
med, pool, ratio = map(np.array, (med, pool, ratio))
print("groups %d, studies per group %d to %d" % (len(grp), min(SP.fit(v)["studies"] for v in grp.values()),
                                                max(SP.fit(v)["studies"] for v in grp.values())))
print("true shift %.3f, lbl %.3f: mean median-of-SDs %.4f, mean pooled %.4f, median/pooled mean %.3f, P(median<pooled) %.3f"
      % (SIG_SHIFT, SIG_LBL, med.mean(), pool.mean(), ratio.mean(), (med < pool).mean()))
print("  observed median/pooled = %.3f; share of simulated ratios at or below it: %.3f"
      % (OBSERVED[0] / OBSERVED[1], (ratio <= OBSERVED[0] / OBSERVED[1]).mean()))
