"""On the notch phantom, how far the wall's edges lie from the canal's line, against the gate's
reach, and how many of the wall's last-bone voxels in the band and window the gate leaves out.

  PYTHONPATH=<bordercall> python probe_gate.py
"""
import math

import numpy as np

from morphometry import anatomy as A, body as BODY
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built

vert = built(P.straight(LUMBAR, P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)), LUMBAR, "L3")
B = vert.body_pts
xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
(half, reach, lo, hi), _ = BODY.wall_window(vert, B, xc)
print("canal line lean %.2f degrees, reach %.2f" % (math.degrees(math.atan(vert.wall_slope)), reach))
for name, r in (("gated", reach), ("ungated", 1e9)):
    bone, d = BODY.wall_edges(vert, xc, half, lo, hi, r)
    e = bone + 0.5 * d
    off = A.square_to_wall(vert, bone)[:, 1] - vert.wall_y0
    print("%-8s edges %d, their centres' distance from the line: min %+.2f max %+.2f" % (name, len(e), off.min(), off.max()))
