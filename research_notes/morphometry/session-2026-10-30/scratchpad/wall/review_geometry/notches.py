"""The wall past basivertebral notches of other sizes than the suite's 5 x 6 x 4 mm, with the
canal line it is gated about: the notch phantom's width, height and depth, on the suite's grid
(the column tilted 18 degrees, the grid turned 7) or the near-aligned one (tilted 2 about x).

  notches.py <thin|thick> <suite|x2> <w,h,d> [<w,h,d> ...]
"""
import math
import sys

import numpy as np

from morphometry import anatomy as A, body as BODY
from morphometry.tests import phantom as P

from storage_order import LUMBAR, build_from, reading

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
GRIDS = {"suite": (((1.0, 0.3, 0.0), 18.0), 7.0), "x2": (((1.0, 0.0, 0.0), 2.0), 0.0)}


def main():
    sname, gname = sys.argv[1], sys.argv[2]
    tilt, turn = GRIDS[gname]
    for spec in sys.argv[3:]:
        w, h, d = (float(s) for s in spec.split(","))
        placed = P.straight(LUMBAR, P.lumbar(notch_w=w, notch_h=h, notch_d=d), tilt=tilt)
        lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
        v = build_from(lab, aff)
        err, info = reading(v, placed, 0.0)
        reach = BODY.WALL_GATE_SHARE * float(np.median([s.ap for s in v.full_rings()]))
        print("%s %s notch %s: err %+6.2f edges %s dropped %s span %s free %5.2f parted %s fit %+.2f "
              "canal line %+.2f deg reach %.2f why %s"
              % (sname, gname, spec, err, info.get("edges"), info.get("dropped"),
                 None if info.get("span_mm") is None else round(info["span_mm"], 1),
                 info.get("free_deg", float("nan")), info.get("parted"), info.get("fitted_deg", float("nan")),
                 math.degrees(math.atan(v.wall_slope)), reach, info.get("why", "")), flush=True)


if __name__ == "__main__":
    main()
