"""Every figure the docstrings quote for body.posterior_wall, from the final robustness rows.

  final_stats.py rob_f_0.json,rob_f_1.json
"""
import json
import math
import sys

import numpy as np

rows = [r for p in sys.argv[1].split(",") for r in json.load(open(p))]


def fin(x):
    return x is not None and math.isfinite(x)


def ranks(x):
    return np.argsort(np.argsort(x)).astype(float)


for sp in ("thin", "thick"):
    print("==", sp)
    clean = [r for r in rows if r["alt"] == "clean" and r["spacing"] == sp]
    e = [abs(r["current"]) for r in clean if fin(r["current"])]
    fit = [abs(r["current_fitted_deg"] - r["truth"]) for r in clean if fin(r.get("current_fitted_deg", math.nan))]
    print("clean: read %d of %d, max %.2f median %.2f; parted %d; fit alone max %.2f median %.2f; flagged %d" % (
        len(e), len(clean), max(e), float(np.median(e)), sum(r.get("current_parted") == 1.0 for r in clean),
        max(fit), float(np.median(fit)), sum(r.get("current_free_deg", 0) > 3.0 for r in clean)))
    for alt in sorted({r["alt"] for r in rows}):
        sel = [r for r in rows if r["alt"] == alt and r["spacing"] == sp]
        e = [abs(r["current"]) for r in sel if fin(r["current"])]
        extra = ""
        if alt.startswith("ragged"):
            less = [abs(r["current"] + r["tilt6"]) for r in sel if fin(r["current"])]
            extra = " less the lean max %.2f" % max(less)
        parted = [r for r in sel if r.get("current_parted") == 1.0 and fin(r["current"])]
        unparted = [r for r in sel if r.get("current_parted") == 0.0 and fin(r["current"])]

        def inside(rs):
            return sum(r["current_free_lo_deg"] - 1e-9 <= r["truth"] <= r["current_free_hi_deg"] + 1e-9 for r in rs)
        print("  %-18s max %5.2f median %4.2f refused %d of %d; parted %d (truth inside %d), not parted %d "
              "(truth inside %d); flagged %d, unflagged past 1.5 %d%s" % (
                  alt, max(e), float(np.median(e)), len(sel) - len(e), len(sel), len(parted), inside(parted),
                  len(unparted), inside(unparted), sum(r.get("current_free_deg", 0) > 3.0 for r in sel if fin(r["current"])),
                  sum(abs(r["current"]) > 1.5 and r.get("current_free_deg", 0) <= 3.0 for r in sel if fin(r["current"])),
                  extra))
    sel = [r for r in rows if r["spacing"] == sp and r["alt"] not in ("clean", "lip_top_1.5")
           and not r["alt"].startswith("ragged") and fin(r["current"]) and fin(r.get("current_free_deg"))]
    e = np.array([abs(r["current"]) for r in sel])
    f = np.array([r["current_free_deg"] for r in sel])
    print("rank correlation of |error| with the freedom over %d altered readings %.2f" % (
        len(sel), np.corrcoef(ranks(e), ranks(f))[0, 1]))
    alt = [r for r in rows if r["spacing"] == sp and r["alt"] not in ("clean", "lip_top_1.5")
           and not r["alt"].startswith("ragged") and fin(r["current"])]
    print("altered but the ragged and the lip: max %.2f (%s)" % (
        max(abs(r["current"]) for r in alt), max(alt, key=lambda r: abs(r["current"]))["alt"]))
    sh = [r.get("current_dropped", 0) / (r.get("current_dropped", 0) + r.get("current_edges", 1)) for r in rows
          if r["spacing"] == sp and fin(r["current"])]
    print("largest dropped share of a reading: %.2f" % max(sh))
