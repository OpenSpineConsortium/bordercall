"""What sets the width: the angle between the true wall and the nearest family of lattice planes
(constant i, j or k), and how many of that family's planes the wall crosses over the span read.

  PYTHONPATH=<bordercall> python phase.py <cache_dir> limit.json
"""
import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def wall_normal_world(rec):
    from morphometry.tests import phantom as P
    import build_cache as BC
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    placed = P.straight(BC.LUMBAR, P.lumbar(**BC.PHANTOMS[name]), tilt=tilt)
    pl = [p for p in placed if p.level == "L3"][0]
    n = np.array([0.0, 1.0, -math.tan(math.radians(lean))])
    n = pl.R @ (n / np.linalg.norm(n))
    return n


def main():
    cache, js = sys.argv[1], sys.argv[2]
    rows = {r["key"]: r for r in json.load(open(js))}
    out = []
    for key, r in sorted(rows.items()):
        with open(os.path.join(cache, key + ".pkl"), "rb") as fh:
            rec = pickle.load(fh)
        v = rec["vert"]
        n = wall_normal_world(rec)
        ax, sp = v.grid.axes, v.grid.spacing
        best = None
        for k in range(3):
            th = math.degrees(math.acos(min(1.0, abs(float(n @ ax[:, k])))))
            # the wall's own direction up the frame's z crosses planes of this family at the rate
            # tan(angle between the wall and the plane) per mm of height
            cross = r["span_mm"] * math.tan(math.radians(th)) / sp[k]
            if best is None or th < best[0]:
                best = (th, k, sp[k], cross)
        f = r["fits"]["mask_curved"]
        out.append((best[3], best[0], f["width_deg"], key))
    out.sort()
    print("%-38s %7s %9s %8s" % ("config", "angle", "crossings", "width"))
    for cross, th, w, key in out:
        print("%-38s %7.2f %9.2f %8.2f" % (key, th, cross, w))
    c = np.array([o[0] for o in out])
    w = np.array([o[2] for o in out])
    for lo, hi in ((0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 2.5), (2.5, 4), (4, 100)):
        sel = (c >= lo) & (c < hi)
        if sel.any():
            print("crossings in [%.1f, %.1f): %2d configs, width median %.2f max %.2f" % (lo, hi, sel.sum(), np.median(w[sel]), w[sel].max()))


if __name__ == "__main__":
    main()
