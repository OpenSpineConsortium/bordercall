"""A pedicle turned 30 and pitched 15 (about an L5's), at the suite's tilt: what the code reads
for the sagittal angle, against the phantom's truth (a projection onto the sagittal plane) and
against the elevation of the same axis."""
import math, sys, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
t_deg, s_deg = float(sys.argv[1]), float(sys.argv[2])
v = P.lumbar(ped_t=t_deg, ped_s=s_deg)
t0 = time.time()
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
truth = P.truth(v)
wall = math.degrees(math.atan(PED.wall_slope(vert)))
for side, name in PED.SIDES:
    out, note, info = PED.one_side(vert, side, zb)
    d = info["axis"] if info else None
    proj = math.degrees(math.atan2(d[2], -d[1])) - wall if d is not None else float("nan")
    rec = info["parted"] if info else {}
    print("%-5s code %6.2f  projection of the same axis %6.2f  truth %5.2f  transverse %6.2f (truth %.0f)  h %.2f (truth %.0f)  cols %d span %.1f  %s" % (
        name, out.get("pedicle_angle_sagittal", float("nan")), proj, truth["pedicle_angle_sagittal"],
        out.get("pedicle_angle_transverse", float("nan")), truth["pedicle_angle_transverse"], out.get("pedicle_h", float("nan")), truth["pedicle_h"],
        len(rec.get("columns", [])), rec.get("span", 0.0), note))
print("exact elevation for t=%.0f s=%.0f: %.2f; %.0fs" % (t_deg, s_deg, math.degrees(math.atan(math.tan(math.radians(s_deg)) * math.cos(math.radians(t_deg)))), time.time() - t0))
