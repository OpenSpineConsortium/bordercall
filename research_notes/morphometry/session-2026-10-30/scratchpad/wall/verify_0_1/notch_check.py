"""Re-measure the reviewer's notch claim with the suite's own helpers (built, wall_error) and the
phantom's truth, not the reviewer's: the wall's error, its record, the flags measures sets and the
angles taken against it, for each notch named on the command line.

  notch_check.py <thin|thick> <suite|x2> <w,h,d> [...]
"""
import math
import sys

import numpy as np

from morphometry import body as BODY, canal as CANAL, pedicle as PED, posterior as POST
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built, wall_error

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
GRIDS = {"suite": (((1.0, 0.3, 0.0), 18.0), 7.0), "x2": (((1.0, 0.0, 0.0), 2.0), 0.0)}


def one(sname, gname, w, h, d):
    tilt, turn = GRIDS[gname]
    v = P.lumbar(notch_w=w, notch_h=h, notch_d=d)
    placed = P.straight(LUMBAR, v, tilt=tilt)
    vert = built(placed, LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn))
    err = wall_error(vert, placed, 0.0)
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    slope, info = BODY.posterior_wall(vert, B, xc)
    body, bflags = BODY.measures(vert)
    ped, pflags, _ = PED.measures(vert, CANAL.body_span(vert))
    post, sflags = POST.measures(vert)
    t = P.truth(v)
    n = info.get("edges", 0) + info.get("dropped", 0)
    share = info.get("dropped", 0) / n if n else float("nan")
    print("%s %s notch %g,%g,%g: wall err %+.2f edges %s dropped %s share %.2f span %s free %.2f parted %s why %r"
          % (sname, gname, w, h, d, err, info.get("edges"), info.get("dropped"), share,
             None if "span_mm" not in info else round(info["span_mm"], 1), info.get("free_deg", float("nan")),
             info.get("parted"), info.get("why", "")))
    for k in ("endplate_incl", "endplate_lower_incl", "wedge"):
        print("   %-28s %+7.2f truth %+6.2f" % (k, body.get(k, float("nan")), t.get(k, float("nan"))))
    for s in ("right", "left"):
        k = "pedicle_angle_sagittal_" + s
        print("   %-28s %+7.2f truth %+6.2f" % (k, ped.get(k, float("nan")), t.get("pedicle_angle_sagittal", float("nan"))))
    print("   %-28s %+7.2f truth %+6.2f" % ("spinous_angle", post.get("spinous_angle", float("nan")),
                                           t.get("spinous_angle", float("nan"))))
    print("   body flags %s; spinous flag %r; pedicle notes %s" % (
        {k: v[:60] for k, v in bflags.items()}, sflags.get("spinous"),
        {k: v[:60] for k, v in pflags.items() if k.startswith("pedicle_")}), flush=True)


def main():
    sname, gname = sys.argv[1], sys.argv[2]
    for spec in sys.argv[3:]:
        w, h, d = (float(s) for s in spec.split(","))
        one(sname, gname, w, h, d)


if __name__ == "__main__":
    main()
