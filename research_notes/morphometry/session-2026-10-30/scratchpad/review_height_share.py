"""Build the straight phantom's L3 at the suite's tilt and read the right and left pedicles as
the code does, then again with the HEIGHT_SHARE admission switched off, to see whether the
suite's phantoms carry columns under the articular process and what their admission changes."""
import math, sys, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

which = sys.argv[1] if len(sys.argv) > 1 else "straight"
LUMBAR = ["L2", "L3", "L4"]
v = P.Vert() if which == "straight" else P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0)
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
print("built in %.0fs" % (time.time() - t0))
truth = P.truth(v)["pedicle_angle_sagittal"]
for share in (PED.HEIGHT_SHARE, 1e9):
    PED.HEIGHT_SHARE = share
    for side, name in PED.SIDES:
        out, note, info = PED.one_side(vert, side, zb)
        rec = info["parted"] if info else {}
        cols = rec.get("columns", np.zeros((0, 4)))
        hs = cols[:, 3] - cols[:, 2] if len(cols) else np.array([])
        extra = ""
        for s in ("top", "bottom"):
            if s in rec and "margin" in rec[s]:
                extra += " %s m %.3f across %d/%d slope %.4f;" % (s, rec[s]["margin"], rec[s]["across"], rec[s]["bone"] + rec[s]["air"], rec[s]["coefficients"][1])
        print("share %-6s %-5s cols %3d span %.1f heights %.1f..%.1f  sag %6.2f (truth %.0f) h %.2f%s %s" % (
            share, name, len(cols), rec.get("span", 0.0), hs.min() if len(hs) else 0, hs.max() if len(hs) else 0,
            out.get("pedicle_angle_sagittal", float("nan")), truth, out.get("pedicle_h", float("nan")), extra, note))
print("%.0fs" % (time.time() - t0))
