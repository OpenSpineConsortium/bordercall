"""Two tells a refusal could read, on the clean cache and on notch phantoms: the share of the
band's edges the fit leaves out (more than a step off it), and how far the fitted wall at the
midline strays from the canal's line the gate is centred on, over the window, against the reach.

  tells.py cache
  tells.py notch <thin|thick> <suite|x2> <w,h,d> [...]
"""
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

from morphometry import body as BODY  # noqa: E402


def tells(v, B, xc):
    place, why = BODY.wall_window(v, B, xc)
    if place is None:
        return None
    half, reach, lo, hi = place
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    e = bone + 0.5 * d
    if len(e) < 8:
        return None
    X = BODY.wall_design(e, xc)
    coef = BODY.biweight(X, e[:, 1], BODY.trimmed_start(X, e[:, 1], e[:, 2]), BODY.WALL_BIWEIGHT_STEPS * abs(d[1]))
    good = np.abs(e[:, 1] - X @ coef) <= abs(d[1])
    z = np.linspace(lo, hi, 50)
    wall = coef[0] + coef[1] * z - 0.5 * d[1]          # the fitted edge surface at the midline, as a bone centre
    line = v.wall_y0 + v.wall_slope * (z - v.wall_z0)
    return 1.0 - good.mean(), float(np.max(np.abs(wall - line))) / reach


def cache():
    import score
    for key, rec in score.records(os.path.join(WALL, "cache")):
        v = rec["vert"]
        t = tells(v, v.body_pts, rec["xc"])
        slope, info = BODY.posterior_wall(v, v.body_pts, rec["xc"])
        err = BODY.degrees_of(slope) - score.wall_truth_in_frame(rec)
        print("%-42s err %+6.2f dropped share %.2f stray/reach %.2f" % (key, err, t[0], t[1]), flush=True)


def notches(sname, gname, specs):
    from morphometry.tests import phantom as P
    from notches import GRIDS, SPACINGS
    from storage_order import LUMBAR, build_from, reading
    tilt, turn = GRIDS[gname]
    for spec in specs:
        w, h, dd = (float(s) for s in spec.split(","))
        placed = P.straight(LUMBAR, P.lumbar(notch_w=w, notch_h=h, notch_d=dd), tilt=tilt)
        lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
        v = build_from(lab, aff)
        B = v.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        err, info = reading(v, placed, 0.0)
        t = tells(v, B, xc)
        print("%s %s notch %-7s err %+6.2f dropped share %.2f stray/reach %.2f" % (sname, gname, spec, err, t[0], t[1]),
              flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "cache":
        cache()
    else:
        notches(sys.argv[2], sys.argv[3], sys.argv[4:])
