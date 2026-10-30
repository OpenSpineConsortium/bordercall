"""The current reader's per-bin most posterior bone point against the true wall, for one config:
how far in front of the wall each bin's extreme lies (the lattice's phase), and the slope a line
through those extremes takes."""
import math
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import limit as L  # noqa: E402

rec = pickle.load(open(sys.argv[1], "rb"))
v, xc = rec["vert"], rec["xc"]
tp = L.truth_plane(rec)
from morphometry import anatomy as A  # noqa: E402
sq = A.square_to_wall(v, v.loc)
for name, B in (("B (cut)", v.body_pts), ("uncut", v.loc[sq[:, 1] > v.wall_y0 - 3.0])):
    mid = B[np.abs(B[:, 0] - xc) <= 3.0]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    rows = []
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        if len(layer):
            k = np.argmin(layer[:, 1])
            p = layer[k]
            rows.append((z, p[1], p[1] - (tp["a"] + tp["b"] * p[2] + tp["c"] * p[0]), p[0], p[2]))
    rows = np.array(rows)
    s = np.polyfit(rows[:, 0], rows[:, 1], 1)[0]
    print("%s: slope %+.2f deg against truth %+.2f; ahead of the true wall per bin (mm):" % (
        name, math.degrees(math.atan(s)), math.degrees(math.atan(tp["b"]))))
    print("   " + " ".join("%.2f" % r[2] for r in rows))
    print("   at x " + " ".join("%+.1f" % r[3] for r in rows))
