"""Draw the thick-slice phantom (0.86 x 0.86 x dz) with the column tilted about x and read L3's
pedicles through pedicle.one_side, the real code path: the sagittal angle, each surface's margin
and slope, and the interval of slopes that still part bone from air under the same columns.

  refute_thick_pedicle.py <tilt about x, degrees> [dz=2.5] [ped_s=0]
"""
import math
import sys
import time

import numpy as np
from scipy.optimize import linprog

from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
tilt_deg = float(sys.argv[1])
dz = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
ped_s = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0

t0 = time.time()
v = P.lumbar(ped_s=ped_s)
placed = P.straight(LUMBAR, v, tilt=((1.0, 0.0, 0.0), tilt_deg))
lab, aff = P.draw(placed, spacing=(0.86, 0.86, dz), grid_turn=((0.0, 0.0, 1.0), 0.0))
grid = G.VoxelGrid(aff, lab.shape)
names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
vox = V.vertebra_voxels(lab, names)
for lv in list(vox):
    vox[lv], _ = M.main_piece(vox[lv])
order = [lv for lv in LEVELS if lv in vox]
spine = [lv for lv in order if lv != "sacrum"]
cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in spine]
whole = M.whole_levels(vox, spine, lab.shape)
axes = dict(zip(spine, M.column_line(cents, whole, grid.superior())))
lv = "L3"
vert = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], lab.shape), M.neighbours_of(vox, order, lv))
print("tilt %.1f dz %.2f truth sagittal %.1f: drawn and built in %.1fs, flags %s, fz %.2f"
      % (tilt_deg, dz, ped_s, time.time() - t0, vert.flags, vert.fz))

# the scan's layers in the frame: slope dz/dy of the plane the voxel centres of one layer lie on
n_world = np.asarray(aff, float)[:3, 2]
n_world = n_world / np.linalg.norm(n_world)
o = vert.frame.local(vert.points_world(np.zeros((1, 3))))[0]
n_frame = vert.frame.local(vert.points_world(np.zeros((1, 3))) + n_world[None, :])[0] - o
layer_slope = -n_frame[1] / n_frame[2]
print("the scan's layers climb %.4f per mm along the frame's y: %.1f degrees" % (layer_slope, math.degrees(math.atan(layer_slope))))
print("the body's wall slope correction: %.2f degrees" % math.degrees(math.atan(PED.wall_slope(vert))))

zb = CANAL.body_span(vert)
for side, name in PED.SIDES:
    out, note, info = PED.one_side(vert, side, zb)
    print("== %s: sagittal %.2f, transverse %.2f, h %.2f, chord %.2f%s" % (
        name, out.get("pedicle_angle_sagittal", float("nan")), out.get("pedicle_angle_transverse", float("nan")),
        out.get("pedicle_h", float("nan")), out.get("pedicle_chord", float("nan")), ("; note: " + note) if note else ""))
    parted = info["parted"] if info else None
    if not parted:
        continue
    print("   span %.1f mm under %d columns" % (parted["span"], len(parted["columns"])))
    for s in ("top", "bottom"):
        if s in parted and "margin" in parted[s]:
            r = parted[s]
            print("   %s: bone %d air %d, margin %.3f, %d across, slope %.4f per mm = %.1f degrees" % (
                s, r["bone"], r["air"], r["margin"], r["across"], r["coefficients"][1],
                math.degrees(math.atan(r["coefficients"][1]))))
    m, rows, near, walls = info["map"], info["rows"], info["near"], info["walls"]
    sec = float(np.median([rows[i]["w"] for i in near]))
    hgt = float(np.median([rows[i]["h"] for i in near]))
    cols = PED.columns(m, rows, near, sec, hgt)
    line = PED.wall_line(rows, near, walls)
    for top, s in ((True, "top"), (False, "bottom")):
        q, across, bone = PED.lattice_under(m, cols, line, sec, top)
        F = np.column_stack([np.ones(len(q)), q[:, 1], across, across ** 2])
        sign = np.where(bone, -1.0, 1.0) if top else np.where(bone, 1.0, -1.0)
        lo = linprog(c=[0, 1, 0, 0], A_ub=sign[:, None] * F, b_ub=sign * q[:, 2], bounds=[(None, None)] * 4, method="highs")
        hi = linprog(c=[0, -1, 0, 0], A_ub=sign[:, None] * F, b_ub=sign * q[:, 2], bounds=[(None, None)] * 4, method="highs")
        if lo.success and hi.success:
            print("   %s: every slope in [%.1f, %.1f] degrees parts bone from air" % (
                s, math.degrees(math.atan(lo.x[1])), math.degrees(math.atan(hi.x[1]))))
        else:
            print("   %s: no slope parts them (margin negative)" % s)
print("total %.1fs" % (time.time() - t0))
