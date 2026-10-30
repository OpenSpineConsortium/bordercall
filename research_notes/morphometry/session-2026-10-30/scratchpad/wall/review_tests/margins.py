"""The numbers behind each new test on the tree it is run against: the wall's error, the
inclinations' errors, and the wall reading's record (parted, fitted against clamped slope, freedom),
so that each tolerance can be set beside what the test actually reads."""
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T


def record(vert):
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    if hasattr(BODY, "read_wall"):
        vert.__dict__.pop("_posterior_wall", None)
        slope, info = BODY.read_wall(vert, B, xc)
        return BODY.degrees_of(slope), info
    return math.degrees(math.atan(BODY.posterior_wall_slope(vert, B, xc))), {}


def show(name, vert, placed, lean, truth=None):
    deg, info = record(vert)
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    R = [pl for pl in placed if pl.level == vert.level][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    want = math.degrees(math.atan(float(vert.frame.ey @ w) / float(vert.frame.ez @ w)))
    print("%s: wall %.3f deg, truth %.3f, error %+.3f" % (name, deg, want, deg - want))
    keys = ("parted", "fitted_deg", "free_lo_deg", "free_hi_deg", "free_deg", "edges", "dropped", "why")
    print("   " + ", ".join("%s=%s" % (k, info[k]) for k in keys if k in info))
    if "fitted_deg" in info:
        print("   clamp moved the slope by %+.4f deg" % (deg - info["fitted_deg"]))
    if truth is not None:
        got, flags = BODY.measures(vert)
        for k in ("endplate_incl", "endplate_lower_incl", "wedge"):
            print("   %s %.3f against %.3f: error %+.3f" % (k, got[k], truth[k], got[k] - truth[k]))
        print("   body flags: %s" % sorted(flags))


def main():
    which = sys.argv[1:] or ["leaned", "notch", "thick", "straight"]
    if "leaned" in which:
        placed = P.straight(T.LUMBAR, P.lumbar(lean=5.0), tilt=((1.0, 0.0, 0.0), 2.0))
        vert = T.built(placed, T.LUMBAR, "L3", grid_turn=((0.0, 0.0, 1.0), 0.0))
        show("LeanedWall L3", vert, placed, 5.0)
    if "notch" in which:
        v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)
        placed = P.straight(T.LUMBAR, v)
        vert = T.built(placed, T.LUMBAR, "L3")
        show("Notch L3", vert, placed, 0.0, P.truth(v))
        print("   canal line slope %.4f (%.2f deg), wall_y0 %.3f" % (vert.wall_slope, math.degrees(math.atan(vert.wall_slope)), vert.wall_y0))
    if "thick" in which:
        v = P.Vert()
        placed = P.straight(T.LUMBAR, v, tilt=((1.0, 0.0, 0.0), 20.0))
        vert = T.built(placed, T.LUMBAR, "L3", spacing=(0.86, 0.86, 2.5), grid_turn=((0.0, 0.0, 1.0), 0.0))
        show("ThickSlices L3", vert, placed, 0.0, P.truth(v))
    if "straight" in which:
        v = P.Vert()
        placed = P.straight(T.LUMBAR, v)
        vert = T.built(placed, T.LUMBAR, "L3")
        show("Straight L3", vert, placed, 0.0, P.truth(v))


if __name__ == "__main__":
    main()
