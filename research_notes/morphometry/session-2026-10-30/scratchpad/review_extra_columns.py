"""On the straight phantom's L3 at the suite's tilt: with the HEIGHT_SHARE admission off, which
columns are added, which lattice centres they bring, and does the parted surface honour them?"""
import math, sys, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
v = P.Vert()
placed = P.straight(LUMBAR, v)
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0), strict=False)
grid = G.VoxelGrid(aff, lab.shape)
names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
vox = V.vertebra_voxels(lab, names)
for lv in list(vox):
    vox[lv], _ = M.main_piece(vox[lv])
order = [lv for lv in LEVELS if lv in vox]
cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
whole = M.whole_levels(vox, order, lab.shape)
axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
vert = A.build("L3", vox["L3"], grid, axes["L3"], V.touching_edge(vox["L3"], lab.shape), M.neighbours_of(vox, order, "L3"))
zb = CANAL.body_span(vert)
for side, name in PED.SIDES:
    m = PED.SideMap(vert, side)
    rows = PED.profile(m, PED.anchors(vert, zb))
    k, near, walls0 = PED.isthmus(rows, vert, m)
    sec = float(np.median([rows[i]["w"] for i in near])); hgt = float(np.median([rows[i]["h"] for i in near]))
    taken, walls = PED.axis_rows(m, rows, near, k, walls0)
    line = PED.wall_line(rows, near, walls)
    PED.HEIGHT_SHARE = 1e9
    cols = PED.columns(m, rows, near, sec, hgt)
    PED.HEIGHT_SHARE = 0.35
    tall = (cols[:, 3] - cols[:, 2]) > 1.35 * hgt
    print("==", name, "near rows y %.2f..%.2f, %d columns, %d tall:" % (rows[near[0]]["y"], rows[near[-1]]["y"], len(cols), tall.sum()),
          [tuple(np.round(c, 2)) for c in cols[tall]])
    for top in (True, False):
        q, across, bone = PED.lattice_under(m, cols, line, sec, top)
        # which centres belong to a tall column: redo the assignment as lattice_under does
        apart = np.maximum(np.abs(q[:, :1] - cols[None, :, 0]) / (0.5 * vert.pixel), np.abs(q[:, 1:2] - cols[None, :, 1]) / (0.25 * vert.pixel + 1e-6))
        j = np.argmin(apart, axis=1)
        mine = tall[j]
        got = PED.parting(q[:, 1], across, q[:, 2], bone, top)
        F = np.column_stack([np.ones(len(q)), q[:, 1], across, across ** 2])
        surf = F @ got["coefficients"]
        signed = np.where(bone, surf - q[:, 2], q[:, 2] - surf) if top else np.where(bone, q[:, 2] - surf, surf - q[:, 2])
        print("  %s: %d centres, %d under the tall columns (z %s bone %s); margin %.3f across %d; least signed margin over all %.3f, over the tall columns' %s" % (
            "top" if top else "bottom", len(q), mine.sum(), np.round(q[mine, 2], 1).tolist(), bone[mine].astype(int).tolist(),
            got["margin"], got["across"], signed.min(), "%.3f" % signed[mine].min() if mine.any() else "-"))
