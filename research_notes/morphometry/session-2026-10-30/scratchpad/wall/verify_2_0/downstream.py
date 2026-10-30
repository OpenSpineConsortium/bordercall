"""What the speck's refusal does to the angles taken against the wall: measure.vertebra_values on
the clean vertebra, on the speck copy as the code stands, and on the speck copy with
wall_slope_range taking HiGHS's status 4 as no parting (the reviewer's first fix)."""
import copy
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)
sys.path.insert(0, HERE)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from morphometry import measure as MEASURE  # noqa: E402
from speck_status import with_speck  # noqa: E402

KEYS = ("endplate_incl", "endplate_lower_incl", "pedicle_angle_sagittal_right", "pedicle_angle_sagittal_left",
        "spinous_angle")
FLAGS = ("posterior_wall", "posterior_wall_free", "spinous", "pedicle_right", "pedicle_left")


def range_with_status4_unparted(bone, air, xc):
    F = BODY.wall_design(np.vstack([bone, air]), xc)
    sign = np.concatenate([np.ones(len(bone)), -np.ones(len(air))])
    y = np.concatenate([bone[:, 1], air[:, 1]])
    ends = []
    for c, unbounded in (([0.0, 1.0, 0.0, 0.0], -math.inf), ([0.0, -1.0, 0.0, 0.0], math.inf)):
        res = linprog(c=c, A_ub=sign[:, None] * F, b_ub=sign * y - BODY.WALL_PART_MM, bounds=[(None, None)] * 4,
                      method="highs")
        if res.status in (2, 4):
            return BODY.NAN, BODY.NAN
        ends.append(float(res.x[1]) if res.status == 0 else unbounded)
    return ends[0], ends[1]


def values(v):
    vals, flags, _ = MEASURE.vertebra_values(v)
    return vals, flags


def show(name, vals, flags):
    print("  %-22s %s" % (name, " ".join("%s %+.2f" % (k.replace("pedicle_angle_", "ped_"), vals.get(k, float("nan")))
                                         for k in KEYS)))
    for k in FLAGS:
        if k in flags:
            print("      flag %s: %s" % (k, flags[k][:110]))


def main():
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if key not in sys.argv[1:]:
            continue
        v = rec["vert"]
        print(key)
        show("clean", *values(copy.copy(v)))
        show("speck as written", *values(with_speck(v, v.body_pts, rec["xc"])))
        original = BODY.wall_slope_range
        BODY.wall_slope_range = range_with_status4_unparted
        try:
            show("speck, 4 as unparted", *values(with_speck(v, v.body_pts, rec["xc"])))
        finally:
            BODY.wall_slope_range = original


if __name__ == "__main__":
    main()
