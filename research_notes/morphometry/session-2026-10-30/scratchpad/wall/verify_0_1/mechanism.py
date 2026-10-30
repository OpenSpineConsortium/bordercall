"""Where the edges the wall is fitted to lie on the notch phantom, in the phantom's own frame:
on the notch's floor (y near notch_d inside the notch's x and z), on the wall (y near 0), or
elsewhere; how many of each the fit keeps; and what the same fit reads on the wall's edges alone.

  mechanism.py <thin|thick> <suite|x2> <w,h,d> [...]
"""
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
GRIDS = {"suite": (((1.0, 0.3, 0.0), 18.0), 7.0), "x2": (((1.0, 0.0, 0.0), 2.0), 0.0)}


def fit(e, xc, step_y):
    X = BODY.wall_design(e, xc)
    coef = BODY.biweight(X, e[:, 1], BODY.trimmed_start(X, e[:, 1], e[:, 2]), BODY.WALL_BIWEIGHT_STEPS * step_y)
    return coef, np.abs(e[:, 1] - X @ coef) <= step_y


def one(sname, gname, w, h, dn):
    tilt, turn = GRIDS[gname]
    placed = P.straight(LUMBAR, P.lumbar(notch_w=w, notch_h=h, notch_d=dn), tilt=tilt)
    v = built(placed, LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn))
    pl = [p for p in placed if p.level == "L3"][0]
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    half, reach, lo, hi = BODY.wall_window(v, B, xc)[0]
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    step_y = abs(d[1])
    e = bone + 0.5 * d
    q = (v.points_world(e) - pl.c) @ pl.R
    in_notch = (np.abs(q[:, 0]) <= w / 2 + 0.6) & (np.abs(q[:, 2]) <= h / 2 + 0.6)
    floor = in_notch & (np.abs(q[:, 1] - dn) <= 1.0)
    wall = np.abs(q[:, 1]) <= 1.0
    other = ~floor & ~wall
    coef, good = fit(e, xc, step_y)
    print("%s %s notch %g,%g,%g: window %.1f mm (lo %.1f hi %.1f), half band %.2f, reach %.2f, canal line %+.2f deg"
          % (sname, gname, w, h, dn, hi - lo, lo, hi, half, reach, BODY.degrees_of(v.wall_slope)))
    print("   edges %d: floor %d (%.2f), wall %d (%.2f), other %d; kept: floor %d wall %d other %d; fit %+.2f deg"
          % (len(e), floor.sum(), floor.mean(), wall.sum(), wall.mean(), other.sum(),
             (good & floor).sum(), (good & wall).sum(), (good & other).sum(), BODY.degrees_of(coef[1])))
    zf = q[good & floor, 2]
    zw = q[good & wall, 2]
    print("   kept floor edges' phantom z %s; kept wall edges' phantom z %s" % (
        "none" if not len(zf) else "%.1f..%.1f" % (zf.min(), zf.max()),
        "none" if not len(zw) else "%.1f..%.1f" % (zw.min(), zw.max())))
    if wall.sum() >= 8:
        cw, _ = fit(e[wall], xc, step_y)
        print("   the same fit on the wall's edges alone: %+.2f deg" % BODY.degrees_of(cw[1]))
    print("   wall edges' phantom z %.1f..%.1f" % (q[wall, 2].min(), q[wall, 2].max()) if wall.any() else "", flush=True)


def main():
    sname, gname = sys.argv[1], sys.argv[2]
    for spec in sys.argv[3:]:
        w, h, dn = (float(s) for s in spec.split(","))
        one(sname, gname, w, h, dn)


if __name__ == "__main__":
    main()
