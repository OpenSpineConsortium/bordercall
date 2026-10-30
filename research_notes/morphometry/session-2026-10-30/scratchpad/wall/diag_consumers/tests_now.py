"""How much of each tested angle in morphometry/tests/test_morphometry.py is the wall reader's.

The cache's suite18 thin configs are the L3s of the test classes Straight (straight), Shapes
(shapes) and PitchedDown (pitched_down): P.straight's default tilt ((1, 0.3, 0), 18 degrees),
P.draw's default grid turn (7 degrees about z), 0.8 x 0.8 x 1 mm, the same parameters. Overhang
and ThickSlices are built here the way build_cache.build builds a config. For each: the tested
angles' errors with the wall as read now, with the same reader on the uncut voxels in front of the
canal's middle (coupling.uncut), and with the true wall in the frame, beside the test's tolerance.

  tests_now.py <cache_dir>
"""
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build_cache as BC  # noqa: E402
import score as SC  # noqa: E402
import coupling as CP  # noqa: E402
from morphometry import body as BODY  # noqa: E402

TOL = {"sag_right": 1.5, "sag_left": 1.5, "endplate_incl": 1.5, "endplate_lower_incl": 1.5, "spinous": 3.0}
TESTS = {"straight": "Straight (test_pedicles, test_end_plate_angles_and_areas, test_posterior_elements)",
         "shapes": "Shapes (test_pedicle_angles, test_processes)",
         "pitched_down": "PitchedDown (test_pedicle_angles_and_size)",
         "overhang": "Overhang (test_pedicle_under_the_process)",
         "straight_x20": "ThickSlices (test_pedicle_sagittal_angle_is_refused_or_right)"}


def show(tag, rec):
    v = rec["vert"]
    truth = SC.wall_truth_in_frame(rec)
    now = rec["raw"]["wall_now"]
    unc = math.degrees(math.atan(BODY.posterior_wall_slope(v, CP.uncut(v), rec["xc"])))
    canal = math.degrees(math.atan(v.wall_slope))
    print("== %s: wall truth %+.2f, read %+.2f (err %+.2f), uncut %+.2f (err %+.2f), canal line err %+.2f" % (
        TESTS[tag], truth, now, now - truth, unc, unc - truth, canal - truth))
    for name, cand in (("now", now), ("uncut", unc), ("true wall", truth)):
        d = SC.downstream(rec, cand)
        print("   %-9s %s" % (name, "  ".join("%s %+.2f (tol %.1f)" % (k, x, TOL[k]) for k, x in d.items()
                                             if k in TOL and np.isfinite(x))))
    nan = [k for k in ("sag_raw_right", "sag_raw_left") if not np.isfinite(rec["raw"].get(k, float("nan")))]
    if nan:
        print("   not read: %s" % ", ".join(nan))


def main():
    cache = sys.argv[1]
    for tag in ("straight", "shapes", "pitched_down"):
        with open(os.path.join(cache, "%s_lean+0_suite18_thin.pkl" % tag), "rb") as f:
            show(tag, pickle.load(f))
    BC.PHANTOMS["overhang"] = dict(sap_x=19.0, sap_y=-10.0, facet=0.0, sap_thk=3.5, sap_len=14.0)
    show("overhang", BC.build(("overhang", 0.0, "suite18", ((1.0, 0.3, 0.0), 18.0), 7.0, "thin")))
    BC.GRIDS.append(("x20", ((1.0, 0.0, 0.0), 20.0), 0.0))
    show("straight_x20", BC.build(("straight", 0.0, "x20", ((1.0, 0.0, 0.0), 20.0), 0.0, "thick")))


if __name__ == "__main__":
    main()
