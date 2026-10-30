"""Downstream |error| (max / median) of each reading, per spacing, for the scored candidates, with
the reading the true wall would give beside them (what the raw readings err by on their own)."""
import json, sys
import numpy as np
runs = {"current": "score_current.json", "C": "score_final.json", "C+risers": "score_crack.json"}
data = {k: json.load(open(f)) for k, f in runs.items()}
truth_rows = data["current"]
keys = ["sag_right", "sag_left", "endplate_incl", "endplate_lower_incl", "spinous"]
for sp in ("thin", "thick"):
    print("== %s" % sp)
    for k in keys:
        line = "  %-20s" % k
        for name, rows in data.items():
            e = [abs(r["down"].get(k, np.nan)) for r in rows if r["spacing"] == sp]
            e = np.array([x for x in e if np.isfinite(x)])
            line += " %s %5.2f/%4.2f (n %2d)" % (name, e.max() if len(e) else np.nan, np.median(e) if len(e) else np.nan, len(e))
        # the true wall: the current's downstream minus the current's wall error, by the sign each reading takes it
        sign = {"sag_right": -1, "sag_left": -1, "endplate_incl": -1, "endplate_lower_incl": -1, "spinous": +1}[k]
        e = [abs(r["down"][k] - sign * r["wall_err"]) for r in truth_rows if r["spacing"] == sp and np.isfinite(r["down"].get(k, np.nan))]
        line += " | true wall %5.2f/%4.2f" % (max(e) if e else np.nan, np.median(e) if e else np.nan)
        print(line)
