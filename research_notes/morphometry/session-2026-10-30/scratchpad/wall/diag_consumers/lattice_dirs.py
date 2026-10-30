"""On the joint phantom's L3 in the column's-line frame: the dy/dz, in that frame, of the lattice
directions a voxel-centre column can follow at the midline (a3 + i a1 + j a2 for small i, j whose
step across x stays inside the canal reader's band), beside the canal line and the wall's truth,
to see whether the canal line reads a lattice direction rather than the wall.

  lattice_dirs.py
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import joints as J  # noqa: E402
from morphometry import anatomy as A, measure as M  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402
from scanimport import geometry as G, volume as V, LEVELS  # noqa: E402


def main():
    v0 = P.Vert()
    joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
    placed = P.chain(J.LUMBAR, {lv: v0 for lv in J.LUMBAR}, {lv: joint for lv in J.LUMBAR[1:]},
                     R0=P.rotation((1.0, 0.3, 0.0), 12.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0), strict=False)
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in J.LUMBAR}
    vox = V.vertebra_voxels(lab, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    whole = M.whole_levels(vox, order, lab.shape)
    axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
    pl = [p for p in placed if p.level == "L3"][0]
    v = A.build("L3", vox["L3"], grid, axes["L3"], V.touching_edge(vox["L3"], lab.shape), {})
    f = v.frame
    Acol = np.asarray(aff, float)[:3, :3]
    print("wall truth %+.2f, canal line %+.2f" % (J.lean_in(v, pl.R), math.degrees(math.atan(v.wall_slope))))
    out = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            d = Acol @ np.array([i, j, 1.0])
            q = np.array([d @ f.ex, d @ f.ey, d @ f.ez])
            if abs(q[0]) <= 1.2 and q[2] > 0.5:
                out.append((abs(q[0]), i, j, q))
    for ax, i, j, q in sorted(out, key=lambda t: t[0]):
        print("i %+d j %+d k 1 (i a1 + j a2 + a3): step x %+.2f y %+.2f z %+.2f mm, dy/dz %+.2f deg" % (
            i, j, q[0], q[1], q[2], math.degrees(math.atan(q[1] / q[2]))))


if __name__ == "__main__":
    main()
