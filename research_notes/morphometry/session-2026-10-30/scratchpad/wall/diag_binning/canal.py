"""anatomy.wall_slope's canal line on cached phantoms: each full ring's anterior edge (s.anterior,
frame y) against the true wall's pole line in the frame, which is taken from posterior_wall_slope's
bins with each least y moved back by its excess (the oracle of decompose.py, fitted as a line).
Prints each slab's z, its edge, its excess over the pole line, and the line's error.

  canal.py <cache_dir> <key> [<key> ...]
"""
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import decompose as D  # noqa: E402
import score as SC  # noqa: E402


def main():
    cache = sys.argv[1]
    for key in sys.argv[2:]:
        with open(os.path.join(cache, key + ".pkl"), "rb") as fh:
            rec = pickle.load(fh)
        v, xc = rec["vert"], rec["xc"]
        truth = SC.wall_truth_in_frame(rec)
        mid, kid = D.strip(v, v.body_pts, v.idx[v.body], xc)
        lo, hi = D.window(mid)
        rows = D.binned(mid, lo, hi, max(v.fz, 0.5))
        pts = mid[[r[3] for r in rows]]
        pole = pts[:, 1] - D.pole_excess(rec, pts)
        c1, c0 = np.polyfit(pts[:, 2], pole, 1)
        rings = v.full_rings()
        z = np.array([s.z for s in rings])
        y = np.array([s.anterior for s in rings])
        ex = y - (c0 + c1 * z)
        print("== %s: canal line %+.2f deg, truth %+.2f, error %+.2f; pole line from the oracle %+.2f deg" % (
            key, math.degrees(math.atan(v.wall_slope)), truth, math.degrees(math.atan(v.wall_slope)) - truth,
            math.degrees(math.atan(c1))))
        print("   " + "  ".join("z %+5.1f ex %+5.2f" % (a, b) for a, b in zip(z, ex)))


if __name__ == "__main__":
    main()
