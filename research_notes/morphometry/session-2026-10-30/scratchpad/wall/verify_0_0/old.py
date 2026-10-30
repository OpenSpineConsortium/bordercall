"""The reading at a9f21fd (each layer's most posterior body point, copied from git show
a9f21fd:morphometry/body.py) on a notch phantom built by the suite's helpers, against the truth in
the measured frame, beside the new reading.

  old.py <thin|thick> <suite|x2> <w,h,d>
"""
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T
from scanimport import geometry as G

from notch_check import GRIDS, SPACINGS


def old_slope(v, B, xc):
    mid = B[np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    if len(mid) < G.MIN_CHORD_POINTS:
        return 0.0
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    rows = []
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        if len(layer):
            rows.append((z, layer[:, 1].min()))
    if len(rows) < 3:
        return 0.0
    rows = np.array(rows)
    return float(np.polyfit(rows[:, 0], rows[:, 1], 1)[0])


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h, d = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    placed = P.straight(T.LUMBAR, P.lumbar(notch_w=w, notch_h=h, notch_d=d), tilt=tilt)
    v = T.built(placed, T.LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=turn)
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    err = T.wall_error(v, placed, 0.0)
    truth = BODY.degrees_of(BODY.posterior_wall(v, B, xc)[0]) - err
    print("%s %s notch %s: new err %+.2f; old err %+.2f" % (sname, gname, spec, err,
                                                           BODY.degrees_of(old_slope(v, B, xc)) - truth))


if __name__ == "__main__":
    main()
