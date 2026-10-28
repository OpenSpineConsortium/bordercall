# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/per_cell.py, 2026-10-28.
# Changed: the absolute paths became the command-line arguments below; worth_real.py imports it with the same arguments.
#     python3 -I verify/per_cell.py SYNTHETIC_SPINE_DATA BORDERCALL
"""Per pool cell: the series synthetic_spine records, their n, cadaveric or living, and the spread of their means.

Pool keys: endplate (EPWu), h_post, canal_w, canal_ap, pedicle (PDW, the mean of right and left).
"""
import csv
import collections
import os
import re
import sys

sys.path.insert(0, sys.argv[2])
import numpy as np
from schwingcheck import LEVELS, measures as MS

D = os.path.join(sys.argv[1], "")
CADAVERIC = re.compile(r"cadaver|dry bone|post-mortem", re.I)


def rows(name):
    with open(D + name, newline="") as fh:
        return list(csv.DictReader(l for l in fh if not l.startswith("#")))


def count(n):
    m = re.findall(r"\d+", n or "")
    if not m:
        return None
    v = [int(x) for x in m]
    return sum(v) / len(v)          # "26-56 per level" -> 41, "60 pedicles" -> 60


level = rows("level_references.csv")
ped = rows("pedicle_width_references.csv")
recs = []
for r in level:
    recs.append(dict(measure=r["measure"], level=r["level"], series=r["series"], sex=r["sex"], mean=float(r["mean"]),
                     sd=r["sd"], disp=r["dispersion"], cohort=r["cohort"], n=r["n"], modality=r["modality"]))
for r in ped:
    s = "Panjabi 1992" if r["series"] == "Panjabi" else r["series"]
    recs.append(dict(measure="pedicle", level=r["level"], series=s, sex="all", mean=float(r["mean"]),
                     sd=r["sd"], disp=r["dispersion"], cohort=r["cohort"], n=r["n"], modality=r["modality"]))

pool = MS.pool()
mu, sd = MS.arrays(pool)
keys = [MS.archive_key(m) for m in pool]
POOLMAP = {"endplate": "endplate", "h_post": "h_post", "canal_w": "canal_w", "canal_ap": "canal_ap", "pedicle": "pedicle"}

cells = collections.defaultdict(list)
for r in recs:
    if r["measure"] in POOLMAP and r["level"] in LEVELS:
        cells[(POOLMAP[r["measure"]], r["level"])].append(r)

print("pool cells holding any series:", len(cells))
beyond = {c: v for c, v in cells.items() if {r["series"] for r in v} != {"Panjabi 1992"}}
print("pool cells holding a series beside Panjabi's:", len(beyond), "of", mu.size)
print()
print("%-10s %-4s %3s %3s %8s %8s  %s" % ("measure", "lev", "k", "kc", "n_cad", "n_all", "f = SD(series means)/Panjabi SD"))
fs = []
for (m, lv), v in sorted(beyond.items(), key=lambda kv: (kv[0][0], LEVELS.index(kv[0][1]))):
    by_series = collections.defaultdict(list)
    for r in v:
        by_series[r["series"]].append(r)
    k = len(by_series)
    cad = {s: rr for s, rr in by_series.items() if CADAVERIC.search(rr[0]["cohort"])}
    n_cad = sum(count(rr[0]["n"]) or 0 for rr in cad.values())
    n_all = sum(count(rr[0]["n"]) or 0 for rr in by_series.values())
    # a series' mean: the mean of its rows (both sexes when split)
    means = np.array([np.mean([r["mean"] for r in rr]) for rr in by_series.values()])
    psd = sd[keys.index(m), LEVELS.index(lv)]
    f = np.std(means, ddof=1) / psd if k >= 3 else float("nan")
    if k >= 3:
        fs.append(f)
    print("%-10s %-4s %3d %3d %8.0f %8.0f  %.2f   cad: %s" % (m, lv, k, len(cad), n_cad, n_all, f,
          ", ".join("%s(%s)" % (s, rr[0]["n"]) for s, rr in cad.items())))
fs = np.array(fs)
print("\ncells with 3+ series:", len(fs), "median f %.2f, range %.2f to %.2f" % (np.median(fs), fs.min(), fs.max()))
