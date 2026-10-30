"""The canal's reading with and without the notch, on the suite's grid: the canal's anterior wall
(the slabs' median), the canal line's slope and place, and the full rings' depths.

  PYTHONPATH=<bordercall> python probe_canal.py
"""
import numpy as np

from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built

for name, kw in (("plain", {}), ("notch", dict(notch_w=5.0, notch_h=6.0, notch_d=4.0))):
    vert = built(P.straight(LUMBAR, P.lumbar(**kw)), LUMBAR, "L3")
    rings = vert.full_rings()
    print("%-6s wall %.2f wall_y0 %.2f wall_slope %+.4f rings %d ap median %.2f" % (
        name, vert.wall, vert.wall_y0, vert.wall_slope, len(rings), float(np.median([s.ap for s in rings]))))
