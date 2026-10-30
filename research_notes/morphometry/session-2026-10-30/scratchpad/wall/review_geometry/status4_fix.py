"""The six specks that leave the wall unread, read again with wall_slope_range taking HiGHS's
status 4 (no verdict, primal infeasible) as no parting, as it takes status 2."""
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from one_voxel import altered, err_of, middle_edge  # noqa: E402


def range_status4_unparted(bone, air, xc):
    F = BODY.wall_design(np.vstack([bone, air]), xc)
    sign = np.concatenate([np.ones(len(bone)), -np.ones(len(air))])
    y = np.concatenate([bone[:, 1], air[:, 1]])
    ends = []
    for c, unbounded in (([0.0, 1.0, 0.0, 0.0], -math.inf), ([0.0, -1.0, 0.0, 0.0], math.inf)):
        res = linprog(c=c, A_ub=sign[:, None] * F, b_ub=sign * y - BODY.WALL_PART_MM, bounds=[(None, None)] * 4,
                      method="highs")
        if res.status in (2, 4):
            return BODY.NAN, BODY.NAN
        ends.append(float(res.x[1]) if res.success else unbounded)
    return ends[0], ends[1]


def main():
    keys = sys.argv[1:]
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if key not in keys:
            continue
        v = rec["vert"]
        j = middle_edge(v, v.body_pts, rec["xc"])
        w, step, d = BODY.scan_step_back(v)
        u = altered(v, add=v.idx[j] + step)
        e_now, i_now = err_of(u, rec)
        original = BODY.wall_slope_range
        BODY.wall_slope_range = range_status4_unparted
        try:
            u2 = altered(v, add=v.idx[j] + step)
            e_fix, i_fix = err_of(u2, rec)
        finally:
            BODY.wall_slope_range = original
        e0, _ = err_of(altered(v), rec)
        print("%-38s clean %+5.2f | speck as written %+5.2f (%s) | speck, status 4 as unparted %+5.2f (parted %s, free %.2f)"
              % (key, e0, e_now, i_now.get("why", "")[:40], e_fix, i_fix.get("parted"), i_fix.get("free_deg", float("nan"))))


if __name__ == "__main__":
    main()
