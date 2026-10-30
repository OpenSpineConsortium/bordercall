"""Max and median |error| of each downstream reading, per spacing, for each score file given."""
import json, sys, math
import numpy as np
for path in sys.argv[1:]:
    rows = json.load(open(path))
    print("##", path)
    for sp in ("thin", "thick"):
        sel = [r for r in rows if r["spacing"] == sp]
        out = []
        for k in ("sag", "endplate_incl", "endplate_lower_incl", "spinous"):
            e = [abs(x) for r in sel for kk, x in r["down"].items() if (kk.startswith(k) if k == "sag" else kk == k) and math.isfinite(x)]
            out.append("%s max %.2f med %.2f n %d" % (k, max(e) if e else float("nan"), np.median(e) if e else float("nan"), len(e)))
        print("  %-5s " % sp + "; ".join(out))
