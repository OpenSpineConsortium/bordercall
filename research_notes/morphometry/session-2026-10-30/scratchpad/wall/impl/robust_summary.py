"""The alteration harness's rows for the reader in body.py ("current") beside the judge's
("proposed"): whether they agree, and per alteration and spacing the largest and median error and
the refusals; with the rank correlation of the error with the freedom over the altered rows.

  python robust_summary.py robust_0.json robust_1.json
"""
import json
import math
import sys

import numpy as np

rows = [r for p in sys.argv[1:] for r in json.load(open(p))]
diff = [abs(r["current"] - r["proposed"]) for r in rows if math.isfinite(r["current"]) and math.isfinite(r["proposed"])]
told = sum(math.isfinite(r["current"]) != math.isfinite(r["proposed"]) for r in rows)
print("rows %d, largest difference %.2g, refusals told apart %d" % (len(rows), max(diff), told))
for sp in ("thin", "thick"):
    print("==", sp)
    for alt in sorted({r["alt"] for r in rows}, key=lambda a: [r["alt"] for r in rows].index(a)):
        sel = [r for r in rows if r["alt"] == alt and r["spacing"] == sp]
        e = np.array([abs(r["current"]) for r in sel if math.isfinite(r["current"])])
        print("  %-18s max %5.2f median %4.2f refused %d of %d" % (alt, e.max(), np.median(e), len(sel) - len(e), len(sel)))


def ranks(x):
    return np.argsort(np.argsort(x)).astype(float)


for sp in ("thin", "thick"):
    sel = [r for r in rows if r["spacing"] == sp and r["alt"] not in ("clean", "lip_top_1.5") and not r["alt"].startswith("ragged")
           and math.isfinite(r["current"]) and math.isfinite(r.get("proposed_free_deg", math.nan))]
    e = np.array([abs(r["current"]) for r in sel])
    f = np.array([r["proposed_free_deg"] for r in sel])
    print("%s: rank correlation of |error| with the freedom over %d altered readings %.2f" % (sp, len(sel), np.corrcoef(ranks(e), ranks(f))[0, 1]))
