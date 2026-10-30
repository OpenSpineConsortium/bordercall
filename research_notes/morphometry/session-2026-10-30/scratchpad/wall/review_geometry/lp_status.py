"""The linear programs' own answers where one speck behind the wall unparts the label: the
status scipy's linprog gives each end of wall_slope_range, and what the code makes of it."""
import math
import os
import sys

import numpy as np
import scipy
from scipy.optimize import linprog

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from one_voxel import altered, middle_edge  # noqa: E402


def lp_answers(bone, air, xc):
    F = BODY.wall_design(np.vstack([bone, air]), xc)
    sign = np.concatenate([np.ones(len(bone)), -np.ones(len(air))])
    y = np.concatenate([bone[:, 1], air[:, 1]])
    out = []
    for c in ([0.0, 1.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0]):
        res = linprog(c=c, A_ub=sign[:, None] * F, b_ub=sign * y - BODY.WALL_PART_MM, bounds=[(None, None)] * 4,
                      method="highs")
        out.append((res.status, res.message))
    # the margin program: the widest margin any surface of the family parts them by
    A = np.column_stack([sign[:, None] * F, np.ones(len(y))])
    res = linprog(c=[0, 0, 0, 0, -1.0], A_ub=A, b_ub=sign * y, bounds=[(None, None)] * 4 + [(None, 10.0)], method="highs")
    return out, (res.status, -res.fun if res.success else None)


def main():
    print("scipy", scipy.__version__)
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if key not in sys.argv[1:]:
            continue
        v = rec["vert"]
        j = middle_edge(v, v.body_pts, rec["xc"])
        w, step, d = BODY.scan_step_back(v)
        u = altered(v, add=v.idx[j] + step)
        for name, x in (("clean", v), ("speck", u)):
            B = x.body_pts
            half, reach, lo, hi = BODY.wall_window(x, B, rec["xc"])[0]
            bone, dd = BODY.wall_edges(x, rec["xc"], half, lo, hi, reach)
            e = bone + 0.5 * dd
            X = BODY.wall_design(e, rec["xc"])
            coef = BODY.biweight(X, e[:, 1], BODY.trimmed_start(X, e[:, 1], e[:, 2]), BODY.WALL_BIWEIGHT_STEPS * abs(dd[1]))
            good = np.abs(e[:, 1] - X @ coef) <= abs(dd[1])
            ends, margin = lp_answers(bone[good], bone[good] + dd, rec["xc"])
            print("%-36s %s: ends %s; widest margin %s; wall_slope_range gives %s"
                  % (key, name, ends, margin, BODY.wall_slope_range(bone[good], bone[good] + dd, rec["xc"])))


if __name__ == "__main__":
    main()
