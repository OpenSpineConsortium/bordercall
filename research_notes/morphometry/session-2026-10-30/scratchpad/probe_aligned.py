"""Why a pitched pedicle reads high on a grid aligned with its frame: for the top and bottom
bands under the columns, which centres a surface at the phantom's true slope would put on the
wrong side, and which part of the phantom each such centre belongs to."""
import math
import sys

import numpy as np

from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
kw = dict(ped_s=float(sys.argv[1]))
tilt = float(sys.argv[2])
v = P.lumbar(**kw)
placed = P.straight(LUMBAR, v, tilt=((1.0, 0.0, 0.0), tilt))
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
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
pl = [p for p in placed if p.level == "L3"][0]
print("wall_slope deg %.2f  axis_turn %.2f" % (math.degrees(math.atan(PED.wall_slope(vert))), vert.axis_turn))
# frame axes in the phantom's local frame
for nm, e in (("ex", vert.frame.ex), ("ey", vert.frame.ey), ("ez", vert.frame.ez)):
    print(nm, np.round(e @ pl.R, 4))
zb = CANAL.body_span(vert)
for side, sname in PED.SIDES:
    m = PED.SideMap(vert, side)
    rows = PED.profile(m, PED.anchors(vert, zb))
    k, near, walls = PED.isthmus(rows, vert, m)
    sec = float(np.median([rows[i]["w"] for i in near])); hgt = float(np.median([rows[i]["h"] for i in near]))
    cols = PED.columns(m, rows, near, sec, hgt)
    line = PED.wall_line(rows, near, walls)
    print("==", sname, "rows y", round(rows[min(near)]["y"], 2), "..", round(rows[max(near)]["y"], 2), "columns", len(cols))
    for top in (True, False):
        q, xr, bone = PED.lattice_under(m, cols, line, sec, top)
        wpts = vert.points_world(q)
        loc = (wpts - pl.c) @ pl.R
        parts = P.parts_inside(loc, v)
        ped = parts["pedicle_" + ("right" if side == 1 else "left")]
        other = np.zeros(len(q), bool)
        for kname, msk in parts.items():
            if not kname.startswith("pedicle"):
                other |= msk
        mism = bone != (ped | other)
        print("  %s: %d centres, %d bone; labelled bone but in no part %d; in another part only %d; label vs parts mismatch %d"
              % ("top" if top else "bottom", len(q), bone.sum(), int((bone & ~(ped | other)).sum()), int((bone & other & ~ped).sum()), int(mism.sum())))
        if (bone & other & ~ped).any():
            names_hit = {}
            for kname, msk in parts.items():
                c = int((bone & msk & ~ped).sum())
                if c and not kname.startswith("pedicle"):
                    names_hit[kname] = c
            print("    other parts:", names_hit)
        got = PED.parting(q[:, 1], xr, q[:, 2], bone, top)
        print("    reading %.2f  freedom %s  margin %.3f across %d" % (
            -math.degrees(math.atan(got["coefficients"][1])) - math.degrees(math.atan(PED.wall_slope(vert))),
            tuple(round(-math.degrees(math.atan(b)), 1) for b in got["freedom"]), got["margin"], got["across"]))
        # the same with only the pedicle's own label
        got2 = PED.parting(q[:, 1], xr, q[:, 2], ped, top)
        if got2:
            print("    pedicle-only labels: %.2f freedom %s" % (
                -math.degrees(math.atan(got2["coefficients"][1])) - math.degrees(math.atan(PED.wall_slope(vert))),
                tuple(round(-math.degrees(math.atan(b)), 1) for b in got2["freedom"])))
