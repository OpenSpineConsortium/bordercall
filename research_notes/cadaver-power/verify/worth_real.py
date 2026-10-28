# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/worth_real.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below; it imports per_cell.py from its own folder;
# and, for the note's check of its rewrite, any further arguments name series to leave out.
#     python3 -I verify/worth_real.py SYNTHETIC_SPINE_DATA BORDERCALL [SERIES ...]
"""Part A's worth formula at the recorded series and counts, per pool cell.

worth = r / (f^2 + 1 / sum_i 1/(f^2 + 1/n_i)), r = 1 + e^2/sd^2; with equal n_i = m this is the
note's r / (f^2 (1 + 1/k) + 1/(k m)). A series with no recorded n is given 12. Each series counts
once and as exact, Bonczar 2024's pooled meta-analysis among them, though it takes in Panjabi 1992
and Tan's spines; name it after the two paths to leave it out.
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, sys.argv[2])
import numpy as np
import per_cell as P   # reuses its loading (prints its own table first)
from schwingcheck import LEVELS, measures as MS

pool = MS.pool()
mu, sd = MS.arrays(pool)
keys = [MS.archive_key(m) for m in pool]
e = MS.errors(pool)[:, None]
R = 1.0 + (e / sd) ** 2


def worth(r, f, ns):
    inv = sum(1.0 / (f * f + 1.0 / n) for n in ns)
    return r / (f * f + 1.0 / inv)


LEFT_OUT = set(sys.argv[3:])            # series named on the command line, as "Bonczar 2024"
if LEFT_OUT:
    print("series left out:", ", ".join(sorted(LEFT_OUT)))
for f in (0.0, 0.39, 0.87):
    table = np.zeros_like(R)
    table_cad = np.zeros_like(R)
    for i in range(R.shape[0]):
        for j in range(R.shape[1]):
            v = P.beyond.get((keys[i], LEVELS[j]))
            if v is None:
                ns_all = ns_cad = [12]
            else:
                by = collections.OrderedDict()
                for row in v:
                    by.setdefault(row["series"], row)
                kept = [row for s, row in by.items() if s not in LEFT_OUT]
                ns_all = [P.count(row["n"]) or 12 for row in kept]
                ns_cad = [P.count(row["n"]) or 12 for row in kept if P.CADAVERIC.search(row["cohort"])]
            table[i, j] = worth(R[i, j], f, ns_all)
            table_cad[i, j] = worth(R[i, j], f, ns_cad)
    beyond_idx = [(keys.index(m), LEVELS.index(lv)) for (m, lv) in P.beyond]
    b_all = np.array([table[ij] for ij in beyond_idx])
    b_cad = np.array([table_cad[ij] for ij in beyond_idx])
    only = np.ones(R.shape, bool)
    for ij in beyond_idx:
        only[ij] = False
    print("f %.2f: Panjabi alone at %d cells, worth median %.1f (range %.1f-%.1f)" % (
        f, only.sum(), np.median(table[only]), table[only].min(), table[only].max()))
    print("        29 cells, all series:      median %.1f, range %.1f-%.1f" % (np.median(b_all), b_all.min(), b_all.max()))
    print("        29 cells, cadaveric only:  median %.1f, range %.1f-%.1f" % (np.median(b_cad), b_cad.min(), b_cad.max()))
    print("        whole pool median, all series: %.1f; the note's 42 x 12: see part_a.json" % np.median(table))
