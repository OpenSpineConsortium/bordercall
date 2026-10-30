"""On the export test's own phantom (and on a chain whose vertebrae lean against the column's
line), how far the column line's frame lies from the frame the export writes, whether the origin
is the label's voxel centroid, and how the three test lines sit in the written frame, with sign."""
import math
import sys

import numpy as np

from morphometry import measure as M
from morphometry.tests import phantom as P
from morphoview import lines as LN
from scanimport import geometry as G
from scanimport import volume as V

LEVELS = ["L2", "L3", "L4"]


def deg(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(a, b))))))


def report(name, lab, aff):
    grid = G.VoxelGrid(aff, lab.shape)
    kept = {}
    M.measure_volume(lab, grid, {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, name, pelvis=False, keep=kept)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in LEVELS})
    print("==", name)
    for lv, v in kept["verts"].items():
        f = v.frame
        col = v.column_ez if v.column_ez is not None else f.ez
        f0 = G.frame_from(f.origin, col, grid.anterior())
        cen = grid.world(vox[lv].astype(float)).mean(0)
        main_cen = grid.world(v.idx.astype(float)).mean(0)
        print("%s axis_turn %.2f deg | column frame vs written: ex %.2f ey %.2f ez %.2f deg | origin - label centroid %.4f mm,"
              " - main piece centroid %.4f mm | flags %s" % (
                  lv, v.axis_turn, deg(f0.ex, f.ex), deg(f0.ey, f.ey), deg(f0.ez, f.ez),
                  float(np.linalg.norm(f.origin - cen)), float(np.linalg.norm(f.origin - main_cen)),
                  sorted(k for k in v.flags if k.startswith("axis"))))
        vals = kept["values"][lv]
        lines = {ln.key: ln for ln in LN.checked(LN.vertebra_lines(v, kept["peds"][lv], vals), vals)}
        for key, axis in (("h_mid", "ez"), ("body_w_mid", "ex"), ("body_d_mid", "ey")):
            ln = lines[key]
            d = (ln.b - ln.a) / np.linalg.norm(ln.b - ln.a)
            loc_a, loc_b = f.local(np.stack([ln.a, ln.b]))
            print("   %-10s signed cosine with %s %.6f (col frame %.6f) | local a %s b %s" % (
                key, axis, float(d @ getattr(f, axis)), float(d @ getattr(f0, axis)),
                np.round(loc_a, 3), np.round(loc_b, 3)))


def main():
    which = sys.argv[1:] or ["test", "joints"]
    if "test" in which:
        lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
        report("the export test's phantom", lab, aff)
    if "joints" in which:
        v = P.Vert()
        joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
        placed = P.chain(LEVELS, {lv: v for lv in LEVELS}, {lv: joint for lv in LEVELS[1:]},
                         R0=P.rotation((1.0, 0.3, 0.0), 12.0))
        lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), strict=False)
        report("the Joints chain", lab, aff)
    if "wedge" in which:
        v = P.Vert(Ha=21.0)
        lab, aff = P.draw(P.straight(LEVELS, v), spacing=(0.8, 0.8, 1.0))
        report("a column of wedged bodies", lab, aff)


if __name__ == "__main__":
    main()
