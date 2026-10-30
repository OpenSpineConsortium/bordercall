"""The wall's error, clamped and not, on the vertebrae the new tests assert on: LeanedWall's and
BasivertebralNotch's L3 on 1 mm slices, and ThickSlices' L3 on 2.5 mm; and the margin each
test's bound leaves. The unclamped slope is the record's fitted_deg, which read_wall computes
before the clamp, so one reading gives both."""
import math
import sys

import numpy as np

sys.path.insert(0, "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall/verify_10_0")

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T


def truth_deg(vert, placed, lean):
    R = [pl for pl in placed if pl.level == vert.level][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    return math.degrees(math.atan(float(vert.frame.ey @ w) / float(vert.frame.ez @ w)))


def report(name, vert, placed, lean, bound):
    B = vert.body_pts
    slope, info = BODY.posterior_wall(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
    t = truth_deg(vert, placed, lean)
    got, fit = BODY.degrees_of(slope), info["fitted_deg"]
    print("%-12s truth %.3f clamped %.3f (err %+.3f) fitted %.3f (err %+.3f) range [%.3f, %.3f] parted %s "
          "free %.3f bound %.2f" % (name, t, got, got - t, fit, fit - t, info["free_lo_deg"], info["free_hi_deg"],
                                    info["parted"], info["free_deg"], bound))
    print("   T.wall_error gives %+.3f" % T.wall_error(vert, placed, lean))


def main():
    lean = 5.0
    placed = P.straight(T.LUMBAR, P.lumbar(lean=lean), tilt=((1.0, 0.0, 0.0), 2.0))
    report("LeanedWall", T.built(placed, T.LUMBAR, "L3", grid_turn=((0.0, 0.0, 1.0), 0.0)), placed, lean,
           T.WALL_TOL_DEG)
    placed = P.straight(T.LUMBAR, P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0))
    report("Notch", T.built(placed, T.LUMBAR, "L3"), placed, 0.0, T.WALL_TOL_DEG)
    placed = P.straight(T.LUMBAR, P.Vert(), tilt=((1.0, 0.0, 0.0), 20.0))
    report("ThickSlices", T.built(placed, T.LUMBAR, "L3", spacing=(0.86, 0.86, 2.5),
                                  grid_turn=((0.0, 0.0, 1.0), 0.0)), placed, 0.0, T.TOL_DEG)


if __name__ == "__main__":
    main()
