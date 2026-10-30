"""The reading at a9f21fd (each layer's most posterior body point) beside the new one, on notch
phantoms, for context: whether the new reader's silent failures were there before.

  old_on_notch.py <thin|thick> <suite|x2> <w,h,d> [...]
"""
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from scanimport import geometry as G

from notches import GRIDS, SPACINGS
from storage_order import LUMBAR, build_from, reading


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
    sname, gname = sys.argv[1], sys.argv[2]
    tilt, turn = GRIDS[gname]
    for spec in sys.argv[3:]:
        w, h, d = (float(s) for s in spec.split(","))
        placed = P.straight(LUMBAR, P.lumbar(notch_w=w, notch_h=h, notch_d=d), tilt=tilt)
        lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
        v = build_from(lab, aff)
        err, info = reading(v, placed, 0.0)
        B = v.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        old = BODY.degrees_of(old_slope(v, B, xc))
        print("%s %s notch %s: new err %+.2f; old reading %+.2f (truth in frame %+.2f)"
              % (sname, gname, spec, err, old, BODY.degrees_of(BODY.posterior_wall(v, B, xc)[0]) - err))


if __name__ == "__main__":
    main()
