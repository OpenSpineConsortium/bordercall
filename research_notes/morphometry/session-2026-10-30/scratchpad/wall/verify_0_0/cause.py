"""Why the notch reading goes wrong: the band's edges sorted into the wall's and the notch's (by
where they lie in the phantom's own frame), the canal line's lean, and the trimmed cost of the fit
the reader found against that of the wall's own surface fitted to the wall's edges alone.

  cause.py <thin|thick> <suite|x2> <w,h,d>
"""
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T
from scanimport import geometry as G

from notch_check import GRIDS, SPACINGS


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h, d = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    vp = P.lumbar(notch_w=w, notch_h=h, notch_d=d)
    placed = P.straight(T.LUMBAR, vp, tilt=tilt)
    v = T.built(placed, T.LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=turn)
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    half, reach, lo, hi = BODY.wall_window(v, B, xc)[0]
    bone, dv = BODY.wall_edges(v, xc, half, lo, hi, reach)
    e = bone + 0.5 * dv
    step_y = abs(dv[1])
    # the edges in the phantom's own frame: world = frame origin + local coords; phantom frame via R, c
    pl = [p for p in placed if p.level == "L3"][0]
    world = v.frame.origin + e @ np.vstack([v.frame.ex, v.frame.ey, v.frame.ez])
    ph = (world - pl.c) @ pl.R
    in_notch = (np.abs(ph[:, 0]) <= w / 2 + 0.5) & (np.abs(ph[:, 2]) <= h / 2 + 0.5) & (ph[:, 1] > 1.0)
    print("edges in the phantom frame: wall %d (y %.2f..%.2f), notch floor %d (y %.2f..%.2f), share %.2f"
          % ((~in_notch).sum(), ph[~in_notch, 1].min(), ph[~in_notch, 1].max(), in_notch.sum(),
             ph[in_notch, 1].min() if in_notch.any() else np.nan, ph[in_notch, 1].max() if in_notch.any() else np.nan,
             in_notch.mean()))
    print("half %.2f reach %.2f window %.2f..%.2f (%.1f mm) edges %d canal line %+.2f deg"
          % (half, reach, lo, hi, hi - lo, len(e), math.degrees(math.atan(v.wall_slope))))
    X = BODY.wall_design(e, xc)
    start = BODY.trimmed_start(X, e[:, 1], e[:, 2])
    coef = BODY.biweight(X, e[:, 1], start, BODY.WALL_BIWEIGHT_STEPS * step_y)
    hkeep = max(int(BODY.WALL_TRIM_KEEP * len(e)), G.MIN_CHORD_POINTS)

    def tcost(c):
        return float(np.sort((e[:, 1] - X @ c) ** 2)[:hkeep].sum())

    print("start slope %+.2f deg tcost %.3f; biweight slope %+.2f deg tcost %.3f"
          % (BODY.degrees_of(start[1]), tcost(start), BODY.degrees_of(coef[1]), tcost(coef)))
    wall_fit = np.linalg.lstsq(X[~in_notch], e[~in_notch, 1], rcond=None)[0]
    print("wall's own edges fitted alone: slope %+.2f deg, tcost over all %.3f (kept h %d of %d)"
          % (BODY.degrees_of(wall_fit[1]), tcost(wall_fit), hkeep, len(e)))
    polished = BODY.biweight(X, e[:, 1], wall_fit, BODY.WALL_BIWEIGHT_STEPS * step_y)
    print("biweight from the wall's fit: slope %+.2f deg tcost %.3f" % (BODY.degrees_of(polished[1]), tcost(polished)))
    r = np.abs(e[:, 1] - X @ coef)
    print("found fit: within a step %d (wall %d, notch %d)"
          % ((r <= step_y).sum(), ((r <= step_y) & ~in_notch).sum(), ((r <= step_y) & in_notch).sum()))


if __name__ == "__main__":
    main()
