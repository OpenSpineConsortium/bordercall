# Copied for the cadaver-power note from the reviewers' verify-arithmetic/zeros_by_group.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below.
#     python3 -I verify/zeros_by_group.py between_studies.json
"""The zeros of f_low split by group: the pedicle measures (PDH, PDIs, PDW) and the rest. For each
group, the share of cells at exactly 0 and the median f_low a common true spread tau would give,
with the group's own study counts (every study 12 specimens, Panjabi's SD estimate in the ratio)."""
import json
import statistics
import sys

import numpy as np

BS = sys.argv[1]
cells = json.load(open(BS))["cells"]
PEDICLE = ("PDH", "PDIs", "PDW")
FIVE = ("EPDl", "EPWl", "VBHp", "SCD", "SCW")
groups = {"pedicle": [c for c in cells if c["measure"] in PEDICLE],
          "the five SPINEPS reads": [c for c in cells if c["measure"] in FIVE],
          "all but pedicle": [c for c in cells if c["measure"] not in PEDICLE]}
rng = np.random.default_rng(11)
N, REPS = 12, 2000
for name, cs in groups.items():
    ks = [c["studies"] for c in cs]
    fl = [c["f_low"] for c in cs]
    print("%s: %d cells, observed share at 0 %.2f, median %.2f" % (name, len(cs), np.mean([x == 0 for x in fl]), statistics.median(fl)))
    for tau in (0.0, 0.024, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        z, med = [], []
        for _ in range(REPS):
            f = []
            for k in ks:
                means = tau * rng.normal(size=k) + rng.normal(size=k) / np.sqrt(N)
                sb = np.std(means, ddof=1)
                sdh = np.sqrt(rng.chisquare(N - 1) / (N - 1))
                f.append(np.sqrt(max(0.0, sb * sb - sdh * sdh / N)) / sdh)
            z.append(np.mean(np.array(f) == 0)); med.append(np.median(f))
        print("   tau %.3f: share at 0 %.2f (5-95%% %.2f-%.2f), median %.2f (5-95%% %.2f-%.2f)" % (
            tau, np.mean(z), np.quantile(z, .05), np.quantile(z, .95), np.mean(med), np.quantile(med, .05), np.quantile(med, .95)))
