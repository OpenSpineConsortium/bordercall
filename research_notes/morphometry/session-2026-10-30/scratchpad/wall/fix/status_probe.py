"""The statuses HiGHS gives the range's programs, asked as before this pass (no widest margin
first), on the speck labels of speck6.py: one voxel a step behind one of six edges, in turn, on
each cached vertebra of the named thickness; with the widest margin each time.

  status_probe.py <thin|thick>
"""
import collections
import os
import sys

import numpy as np
from scipy.optimize import linprog

FIX = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FIX)
import speck6  # noqa: E402
from speck6 import score, WALL  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def kept_pairs(u, B, xc):
    half, reach, lo, hi = BODY.wall_window(u, B, xc)[0]
    bone, d = BODY.wall_edges(u, xc, half, lo, hi, reach)
    e = bone + 0.5 * d
    coef = BODY.fitted_wall(e, d, xc)
    good = np.abs(e[:, 1] - BODY.wall_design(e, xc) @ coef) <= abs(d[1])
    return bone[good], bone[good] + d


def statuses(bone, air, xc):
    A, b = BODY.wall_programme(bone, air, xc)
    widest = linprog(c=[0.0, 0.0, 0.0, 0.0, -1.0], A_ub=np.column_stack([A, np.ones(len(b))]), b_ub=b,
                     bounds=[(None, None)] * 5, method="highs")
    ends = [linprog(c=c, A_ub=A, b_ub=b - BODY.WALL_PART_MM, bounds=[(None, None)] * 4, method="highs").status
            for c in ([0.0, 1.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0])]
    margin = widest.x[4] if widest.status == 0 else np.nan
    return tuple(ends), widest.status, margin


def main():
    counts = collections.Counter()
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if not key.endswith("_" + sys.argv[1]):
            continue
        v = rec["vert"]
        v.__dict__.pop("_posterior_wall", None)
        B, xc = v.body_pts, rec["xc"]
        _, step, _ = BODY.scan_step_back(v)
        for j in speck6.edge_voxels(v, B, xc):
            u = speck6.with_voxel(v, v.idx[j] + step)
            ends, wstat, margin = statuses(*kept_pairs(u, B, xc), xc)
            counts[(ends, wstat, "margin<=part" if not margin > BODY.WALL_PART_MM else "margin>part")] += 1
            if 4 in ends:
                print("%s: ends %s widest %s margin %.3g" % (key, ends, wstat, margin), flush=True)
    for k, n in sorted(counts.items()):
        print(k, n)


if __name__ == "__main__":
    main()
