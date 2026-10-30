"""Tables of robust.py's rows: per alteration and spacing, each reader's max and median |error|
and its refusals; for the ragged edges, the error less the field's own lean as well."""
import collections
import json
import math
import sys

import numpy as np

rows = []
for p in sys.argv[1:]:
    rows += json.load(open(p))
import os
READERS = os.environ.get("TABLE", "current,A,A_plain,B,C").split(",")
alts = list(dict.fromkeys(r["alt"] for r in rows))
for sp in ("thin", "thick"):
    print("== %s" % sp)
    print("%-18s " % "alteration" + " ".join("%-22s" % r for r in READERS))
    for alt in alts:
        sel = [r for r in rows if r["alt"] == alt and r["spacing"] == sp]
        cells = []
        for rn in READERS:
            e = np.array([abs(r[rn]) for r in sel])
            fin = e[np.isfinite(e)]
            n_ref = int((~np.isfinite(e)).sum())
            cells.append("%5.2f/%4.2f r%-2d" % (fin.max() if len(fin) else np.nan, np.median(fin) if len(fin) else np.nan, n_ref))
        print("%-18s " % alt + " ".join("%-22s" % c for c in cells))
        if alt.startswith("ragged"):
            cells = []
            for rn in READERS:
                band = "tilt6" if rn.startswith("A") or rn == "proposed" else "tilt3"
                e = np.array([abs(r[rn] + r[band]) for r in sel])  # the stored lean was taken of -f, the wall moves by +f
                fin = e[np.isfinite(e)]
                cells.append("%5.2f/%4.2f     " % (fin.max() if len(fin) else np.nan, np.median(fin) if len(fin) else np.nan))
            tl = np.array([abs(r["tilt3"]) for r in sel]), np.array([abs(r["tilt6"]) for r in sel])
            print("%-18s " % "  less own lean" + " ".join("%-22s" % c for c in cells)
                  + "  field lean 3mm max/med %.2f/%.2f, 6mm %.2f/%.2f" % (tl[0].max(), np.median(tl[0]), tl[1].max(), np.median(tl[1])))
print()
if "B" not in READERS:
    sys.exit(0)
print("Why B refused, by alteration:")
for alt in alts:
    why = collections.Counter(r["B_why"].split(" ")[0:4].__str__() for r in rows if r["alt"] == alt and not math.isfinite(r["B"]))
    if why:
        print("  %-18s %s" % (alt, dict(why)))
for rn in ("A", "C"):
    print("Why %s refused:" % rn)
    for alt in alts:
        why = collections.Counter(r[rn + "_why"][:40] for r in rows if r["alt"] == alt and not math.isfinite(r[rn]))
        if why:
            print("  %-18s %s" % (alt, dict(why)))
print()
print("Seconds per call, median (max), thin / thick:")
for rn in READERS:
    t = [np.array([r[rn + "_s"] for r in rows if r["spacing"] == sp]) for sp in ("thin", "thick")]
    print("  %-8s %.4f (%.4f) / %.4f (%.4f)" % (rn, np.median(t[0]), t[0].max(), np.median(t[1]), t[1].max()))
