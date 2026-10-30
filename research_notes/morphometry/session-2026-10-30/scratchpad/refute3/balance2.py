"""As balance.py, with the prototype's geometry: the column tilted, the grid turned about z."""
import sys, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
kw = eval("dict(%s)" % sys.argv[1])
tilt = eval(sys.argv[2])
turn = float(sys.argv[3])
spacing = eval(sys.argv[4]) if len(sys.argv) > 4 else (0.8, 0.8, 1.0)
v = P.lumbar(**kw)
t0 = time.time()
placed = P.straight(LUMBAR, v, tilt=tilt)
lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
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
print("%s tilt %s turn %s spacing %s fz %.2f built in %.0fs; truth sag %.2f" % (kw, tilt, turn, spacing, vert.fz, time.time() - t0, truth["pedicle_angle_sagittal"]))
for side, name in PED.SIDES:
    out, note, info = PED.one_side(vert, side, zb)
    rec = info["parted"] if info else {}
    for s in ("top", "bottom"):
        if s in rec:
            r = rec[s]
            n = r["bone"] + r["air"]
            print("  %-5s %-6s bone %3d air %3d (bone share %.2f) margin %s across %s  limit 0.1*n=%.1f  min-class=%d" % (
                name, s, r["bone"], r["air"], r["bone"] / n, "%.3f" % r["margin"] if "margin" in r else "-", r.get("across", "-"), 0.1 * n, min(r["bone"], r["air"])))
    print("  %-5s sag %6.2f  %s" % (name, out.get("pedicle_angle_sagittal", float("nan")), note))
