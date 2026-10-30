"""What other range bounds would refuse: per spacing, refused count and the read ones' max |error|.
Read off the score file's info; no rerun."""
import json, sys, math
import numpy as np
rows = json.load(open(sys.argv[1]))
for sp in ("thin", "thick"):
    sel = [r for r in rows if r["spacing"] == sp]
    w = np.array([r["info"]["width_deg"] for r in sel]); e = np.array([abs(r["wall_err"]) for r in sel])
    print("%s: width min %.2f median %.2f max %.2f" % (sp, w.min(), np.median(w), w.max()))
    for W in (2.0, 3.0, 4.0, 5.0, 6.0, 9.0):
        read = w <= W
        print("   bound %.0f: refuses %2d of %d; read max |err| %.2f; refused max |err| %.2f" % (
            W, (~read).sum(), len(sel), e[read].max() if read.any() else float("nan"), e[~read].max() if (~read).any() else float("nan")))
    print("   |err| / width max %.2f; |err| <= width/2 in %d of %d" % ((e / w).max(), (e <= w / 2).sum(), len(sel)))
