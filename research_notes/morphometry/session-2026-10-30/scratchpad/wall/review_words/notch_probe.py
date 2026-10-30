"""The notch and leaned-wall phantoms of the suite: the gate's reach, the canal line's lean, the
wall's error and its record, so the numbers the docstrings quote are checked."""
import math
import sys

import numpy as np

from morphometry import anatomy as A, body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T


def report(name, vert, placed, lean):
    rings = vert.full_rings()
    reach = BODY.WALL_GATE_SHARE * float(np.median([s.ap for s in rings]))
    half = min(BODY.WALL_BAND_MAX_MM, BODY.WALL_BAND_SHARE * float(np.median([s.width for s in rings])))
    err = T.wall_error(vert, placed, lean)
    B = vert.body_pts
    slope, info = BODY.posterior_wall(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
    print(name, "reach %.2f half %.2f canal line slope %.4f (%.2f deg) wall err %.3f" % (
        reach, half, vert.wall_slope, math.degrees(math.atan(vert.wall_slope)), err), info, flush=True)


which = sys.argv[1]
if which == "notch":
    v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)
    placed = P.straight(T.LUMBAR, v)
    report("notch", T.built(placed, T.LUMBAR, "L3"), placed, 0.0)
    placed = P.straight(T.LUMBAR, P.lumbar())
    report("plain", T.built(placed, T.LUMBAR, "L3"), placed, 0.0)
else:
    placed = P.straight(T.LUMBAR, P.lumbar(lean=5.0), tilt=((1.0, 0.0, 0.0), 2.0))
    report("leaned", T.built(placed, T.LUMBAR, "L3", grid_turn=((0.0, 0.0, 1.0), 0.0)), placed, 5.0)
