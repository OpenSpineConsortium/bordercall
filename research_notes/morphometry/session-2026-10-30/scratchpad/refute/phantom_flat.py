"""One straight phantom whose layers lie 3 degrees off the pedicle's surfaces about x alone
(no turn, no tilt about y), so each surface crosses at most one layer boundary over the
isthmus span: print each side's top and bottom LP slopes, margins and the mean climb."""
import math, sys, time
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

t0 = time.time()
LUMBAR = ["L2", "L3", "L4"]
tilt_deg = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0
v = P.Vert()
placed = P.straight(LUMBAR, v, tilt=((1.0, 0.0, 0.0), tilt_deg))
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
grid = G.VoxelGrid(aff, lab.shape)
truth = P.truth(v)
vox = V.vertebra_voxels(lab, names)
for lv in list(vox):
    vox[lv], _ = M.main_piece(vox[lv])
order = [lv for lv in LEVELS if lv in vox]
spine = [lv for lv in order if lv != "sacrum"]
cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in spine]
whole = M.whole_levels(vox, spine, lab.shape)
axes = dict(zip(spine, M.column_line(cents, whole, lab.shape and grid.superior())))
lv = "L3"
vert = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], lab.shape), M.neighbours_of(vox, order, lv))
zb = CANAL.body_span(vert)
zs = PED.anchors(vert, zb)
print("drawn in %.0fs; fz %.2f; truth sagittal %.1f; layers %.1f deg off the surfaces" % (time.time() - t0, vert.fz, truth["pedicle_angle_sagittal"], tilt_deg))
for side, name in PED.SIDES:
    m = PED.SideMap(vert, side)
    rows = PED.profile(m, zs)
    got = PED.isthmus(rows, vert, m)
    if got is None:
        print(name, "no isthmus"); continue
    k, near, walls0 = got
    sec = float(np.median([rows[i]["w"] for i in near])); hgt = float(np.median([rows[i]["h"] for i in near]))
    taken, walls = PED.axis_rows(m, rows, near, k, walls0)
    rise, why, parted = PED.climb(m, rows, near, walls, sec, hgt)
    line = "%s: %d columns span %.1f; climb %s %s" % (name, len(parted["columns"]), parted["span"],
            ("%.2f deg" % math.degrees(math.atan(rise))) if np.isfinite(rise) else "not read", why)
    for s in ("top", "bottom"):
        if s in parted and "margin" in parted[s]:
            r = parted[s]
            line += " | %s slope %.2f deg margin %.3f across %d" % (s, math.degrees(math.atan(r["coefficients"][1])), r["margin"], r["across"])
    print(line)
    out, note, info = PED.one_side(vert, side, zb)
    print("   pedicle_angle_sagittal %.2f (truth %.1f) note: %s" % (out.get("pedicle_angle_sagittal", float("nan")), truth["pedicle_angle_sagittal"], note))
print("total %.0fs" % (time.time() - t0))
