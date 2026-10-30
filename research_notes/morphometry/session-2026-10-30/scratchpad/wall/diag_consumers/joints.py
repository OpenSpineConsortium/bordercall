"""The joint phantom of test_morphometry.Joints (L2 to L4, each joint opened 8 degrees in front,
tilted 4 sideways, turned 5, slipped 4 mm; R0 12 degrees about (1, 0.3, 0); 0.8 x 0.8 x 1 mm; grid
turned 7), where column.wall_corner's docstring says the canal's line "leans half as far as the
wall does". L3 is built twice: in the column's line through its neighbours (no neighbours given,
so own_axis keeps the line, as before own_axis was written) and in its own axis (as the run does).
In each frame the wall's true lean (the phantom's wall direction taken into the frame), the canal
line (v.wall_slope), body.posterior_wall_slope on the cut body and on the uncut voxels in front of
the canal's middle, and each ring's excess over the true wall.

  joints.py [<extra grid turn in degrees> ...]
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from morphometry import anatomy as A, measure as M, body as BODY  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402
from scanimport import geometry as G, volume as V, LEVELS  # noqa: E402
import coupling as CP  # noqa: E402

LUMBAR = ["L2", "L3", "L4"]


def lean_in(v, R):
    w = R @ np.array([0.0, 0.0, 1.0])
    f = v.frame
    return math.degrees(math.atan((f.ey @ w) / (f.ez @ w)))


def wall_y(v, pl, x, z):
    N = pl.R @ np.array([0.0, 1.0, 0.0])
    f = v.frame
    return -(N @ (f.origin - pl.c) + x * (N @ f.ex) + z * (N @ f.ez)) / (N @ f.ey)


def report(tag, v, pl):
    truth = lean_in(v, pl.R)
    canal = math.degrees(math.atan(v.wall_slope))
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    cut = math.degrees(math.atan(BODY.posterior_wall_slope(v, B, xc)))
    unc = math.degrees(math.atan(BODY.posterior_wall_slope(v, CP.uncut(v), xc)))
    rings = v.full_rings()
    ex = [(s.z, s.anterior - wall_y(v, pl, s.midline, s.z)) for s in rings]
    print("== %s: wall truth %+.2f | canal line %+.2f (ratio %.2f, err %+.2f) | posterior on cut body %+.2f "
          "(err %+.2f), uncut %+.2f (err %+.2f) | axis_turn %.2f, rings %d span %.1f" % (
              tag, truth, canal, canal / truth if abs(truth) > 0.5 else float("nan"), canal - truth, cut,
              cut - truth, unc, unc - truth, v.axis_turn, len(rings),
              max(s.z for s in rings) - min(s.z for s in rings)), flush=True)
    print("   ring excess: " + " ".join("%+.1f:%+.2f" % e for e in ex), flush=True)


def run(turn):
    v0 = P.Vert()
    joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
    placed = P.chain(LUMBAR, {lv: v0 for lv in LUMBAR}, {lv: joint for lv in LUMBAR[1:]},
                     R0=P.rotation((1.0, 0.3, 0.0), 12.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
    vox = V.vertebra_voxels(lab, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    whole = M.whole_levels(vox, order, lab.shape)
    axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
    pl = [p for p in placed if p.level == "L3"][0]
    touch = V.touching_edge(vox["L3"], lab.shape)
    col = A.build("L3", vox["L3"], grid, axes["L3"], touch, {})
    report("turn %.0f, the column's line (no own_axis)" % turn, col, pl)
    own = A.build("L3", vox["L3"], grid, axes["L3"], touch, M.neighbours_of(vox, order, "L3"))
    report("turn %.0f, the vertebra's own axis (as the run reads it)" % turn, own, pl)


def main():
    turns = [float(t) for t in sys.argv[1:]] or [7.0]
    for t in turns:
        run(t)


if __name__ == "__main__":
    main()
