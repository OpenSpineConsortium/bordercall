"""The reviewer's notch claim measured independently: the notch phantom built by the suite's own
helpers (test_morphometry.built and wall_error, strict drawing), the wall's reading and record,
then measure_volume's rows for L3 (the pipeline's own output) with every flag.

  notch_check.py <thin|thick> <suite|x2> <w,h,d> [rows]
"""
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
GRIDS = {"suite": (((1.0, 0.3, 0.0), 18.0), ((0.0, 0.0, 1.0), 7.0)),
         "x2": (((1.0, 0.0, 0.0), 2.0), ((0.0, 0.0, 1.0), 0.0))}
KEYS = ("endplate_incl", "endplate_lower_incl", "wedge", "pedicle_angle_sagittal", "spinous_angle")


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h, d = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    vp = P.lumbar(notch_w=w, notch_h=h, notch_d=d)
    placed = P.straight(T.LUMBAR, vp, tilt=tilt)
    vert = T.built(placed, T.LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=turn)
    err = T.wall_error(vert, placed, 0.0)
    B = vert.body_pts
    _, info = BODY.posterior_wall(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
    n = info.get("edges", 0) + info.get("dropped", 0)
    share = info.get("dropped", 0) / n if n else float("nan")
    print("%s %s notch %s: wall err %+.2f edges %s dropped %s share %.2f free %.2f parted %s fitted %+.2f span %s why %r"
          % (sname, gname, spec, err, info.get("edges"), info.get("dropped"), share,
             info.get("free_deg", float("nan")), info.get("parted"), info.get("fitted_deg", float("nan")),
             info.get("span_mm"), info.get("why", "")), flush=True)
    if len(sys.argv) > 4:
        rows = T.measured(placed, T.LUMBAR, spacing=SPACINGS[sname], grid_turn=turn)["L3"]
        truth = P.truth(vp)
        for k in KEYS:
            for kk in sorted(r for r in rows if r == k or r.startswith(k + "_")):
                if kk.startswith(k) and not kk.startswith("flag"):
                    print("  %-32s %+8.2f truth %+7.2f" % (kk, rows[kk], truth.get(k, float("nan"))))
        for kk in sorted(r for r in rows if r.startswith("flag")):
            print("  %-32s %s" % (kk, str(rows[kk])[:110]))


if __name__ == "__main__":
    main()
