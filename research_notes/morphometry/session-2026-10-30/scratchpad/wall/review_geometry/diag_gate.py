"""Why a notch 8 wide, 8 tall and 5 deep reads the wall off: where the gate about the canal's
line sits against the wall and the notch's floor, and the reading with the gate about a level
line at the canal's median front instead (v.wall_slope 0, v.wall_y0 v.wall).

  diag_gate.py <thin|thick> <suite|x2> <w,h,d>
"""
import copy
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P

from notches import GRIDS, SPACINGS
from storage_order import LUMBAR, build_from, reading


def edges_unGated(v, B, xc):
    """The reader's edges with the gate opened wide, so where the wall and the notch lie shows."""
    place, _ = BODY.wall_window(v, B, xc)
    half, reach, lo, hi = place
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, 1e3)
    return bone + 0.5 * d, (lo, hi, reach)


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h, dep = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    placed = P.straight(LUMBAR, P.lumbar(notch_w=w, notch_h=h, notch_d=dep), tilt=tilt)
    lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
    v = build_from(lab, aff)
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    err, info = reading(v, placed, 0.0)
    print("as read: err %+.2f edges %s dropped %s span %.1f free %.2f parted %s; canal line %+.2f deg, y0 %.2f at z0 %.2f"
          % (err, info.get("edges"), info.get("dropped"), info.get("span_mm", float("nan")), info.get("free_deg", float("nan")),
             info.get("parted"), math.degrees(math.atan(v.wall_slope)), v.wall_y0, v.wall_z0))
    e, (lo, hi, reach) = edges_unGated(v, B, xc)
    line = v.wall_y0 + v.wall_slope * (e[:, 2] - v.wall_z0)
    gated = np.abs(e[:, 1] - 0.5 * BODY.scan_step_back(v)[2][1] - line) <= reach
    print("window %.1f to %.1f mm, reach %.2f; edges with the gate open %d, inside the gate %d" % (lo, hi, reach, len(e), gated.sum()))
    for z0 in np.arange(lo, hi + 1e-9, 2.0):
        sel = (e[:, 2] >= z0) & (e[:, 2] < z0 + 2.0)
        if sel.any():
            print("  z %+5.1f..%+5.1f: edges y median %+6.2f (min %+6.2f max %+6.2f), line %+6.2f, in gate %d of %d"
                  % (z0, z0 + 2.0, np.median(e[sel, 1]), e[sel, 1].min(), e[sel, 1].max(),
                     v.wall_y0 + v.wall_slope * (z0 + 1.0 - v.wall_z0), gated[sel].sum(), sel.sum()))
    level = copy.copy(v)
    level.__dict__.pop("_posterior_wall", None)
    level.wall_slope, level.wall_y0 = 0.0, v.wall
    err2, info2 = reading(level, placed, 0.0)
    print("gate about a level line at the canal's median front (%.2f): err %+.2f edges %s dropped %s free %.2f parted %s"
          % (v.wall, err2, info2.get("edges"), info2.get("dropped"), info2.get("free_deg", float("nan")), info2.get("parted")))


if __name__ == "__main__":
    main()
