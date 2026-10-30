"""ThickSlices' L3 (straight phantom, tilt 20 degrees about x, grid turn 0, 0.86 x 0.86 x 2.5 mm):
the lattice directions a voxel-centre column can follow at the midline, in the vertebra's frame,
beside the wall's truth, the canal line and body.posterior_wall_slope, and the canal rings' and the
posterior bins' excess over the true wall.

  lattice_x20.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import build_cache as BC  # noqa: E402
import canal_line as CL  # noqa: E402
import score as SC  # noqa: E402

rec = BC.build(("straight", 0.0, "x20", ((1.0, 0.0, 0.0), 20.0), 0.0, "thick"))
v = rec["vert"]
f = v.frame
print("wall truth %+.2f canal %+.2f posterior %+.2f fz %.2f fy %.2f" % (
    SC.wall_truth_in_frame(rec), math.degrees(math.atan(v.wall_slope)), rec["raw"]["wall_now"], v.fz, v.fy))
Acol = np.asarray(v.grid.affine, float)[:3, :3]
rows = []
for i in range(-3, 4):
    for j in range(-3, 4):
        for k in range(1, 3):
            d = Acol @ np.array([i, j, k], float)
            q = np.array([d @ f.ex, d @ f.ey, d @ f.ez])
            if abs(q[0]) <= 1.0 and q[2] > 0.5 and abs(math.degrees(math.atan(q[1] / q[2]))) < 15:
                rows.append((i, j, k, q))
for i, j, k, q in rows:
    print("  %+d a_i %+d a_j %+d a_k: step x %+.2f y %+.2f z %+.2f, dy/dz %+.2f deg" % (
        i, j, k, q[0], q[1], q[2], math.degrees(math.atan(q[1] / q[2]))))
rings = v.full_rings()
print("rings:", " ".join("%+.1f:%+.2f" % (s.z, s.anterior - CL.wall_y(rec, s.midline, s.z)) for s in rings))
pb, _ = CL.post_bins(v, rec["xc"])
print("bins :", " ".join("%+.1f:%+.2f" % (z, y - CL.wall_y(rec, x, z)) for z, y, x in pb))
