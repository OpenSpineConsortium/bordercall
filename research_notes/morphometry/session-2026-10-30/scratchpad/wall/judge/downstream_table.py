"""Max and median |error| of the four readings that take the wall, per reader and spacing, from
score.py's JSON rows; 'true wall' puts the frame-relative truth in the reader's place."""
import json, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)
import score as S
files = {"current": "score_current.json", "A": "score_A.json", "B": "score_B.json", "C": "score_C.json",
         "A_lts": "score_A_lts.json", "A_lts_plain": "score_A_lts_plain.json"}
rows = {k: json.load(open(os.path.join(HERE, f))) for k, f in files.items()}
true = []
for r in rows["A"]:
    rec = pickle.load(open(os.path.join(WALL, "cache", r["key"] + ".pkl"), "rb"))
    true.append({"spacing": r["spacing"], "down": S.downstream(rec, r["wall_truth_frame"])})
rows["true wall"] = true
keys = [("sag", ("sag_right", "sag_left")), ("endplate_incl", ("endplate_incl",)),
        ("endplate_lower_incl", ("endplate_lower_incl",)), ("spinous", ("spinous",))]
for sp in ("thin", "thick"):
    print("== %s   (max / median |error|, degrees)" % sp)
    print("%-12s" % "reader" + "".join("%-22s" % k for k, _ in keys))
    for name, rs in rows.items():
        cells = []
        for k, ks in keys:
            e = np.array([abs(r["down"].get(x, np.nan)) for r in rs if r["spacing"] == sp for x in ks])
            e = e[np.isfinite(e)]
            cells.append("%5.2f / %4.2f (n %3d)" % (e.max(), np.median(e), len(e)) if len(e) else "n/a")
        print("%-12s" % name + "".join("%-22s" % c for c in cells))
