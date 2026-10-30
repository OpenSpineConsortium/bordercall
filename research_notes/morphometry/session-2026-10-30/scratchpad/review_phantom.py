"""Build a phantom's L3 at the suite's tilt from keyword parameters and read both pedicles as the
code does, then with the HEIGHT_SHARE admission off."""
import math, sys, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
kw = eval("dict(%s)" % sys.argv[1])
v = P.lumbar(**kw)
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
print("%s built in %.0fs; truth sag %.2f trans %.2f h %.2f w %.2f" % (kw, time.time() - t0, truth["pedicle_angle_sagittal"], truth["pedicle_angle_transverse"], truth["pedicle_h"], truth["pedicle_w"]))
for share in (0.35, 1e9):
    PED.HEIGHT_SHARE = share
    sags = []
    for side, name in PED.SIDES:
        out, note, info = PED.one_side(vert, side, zb)
        rec = info["parted"] if info else {}
        cols = rec.get("columns", np.zeros((0, 4)))
        hs = cols[:, 3] - cols[:, 2] if len(cols) else np.array([0.0])
        extra = "".join(" %s m %.3f across %d/%d;" % (s, rec[s]["margin"], rec[s]["across"], rec[s]["bone"] + rec[s]["air"]) for s in ("top", "bottom") if s in rec and "margin" in rec[s])
        sags.append(out.get("pedicle_angle_sagittal", float("nan")))
        print("  share %-5s %-5s cols %3d span %.1f heights %.1f..%.1f  sag %6.2f trans %6.2f h %.2f w %.2f%s %s" % (
            share, name, len(cols), rec.get("span", 0.0), hs.min(), hs.max(), sags[-1],
            out.get("pedicle_angle_transverse", float("nan")), out.get("pedicle_h", float("nan")), out.get("pedicle_w", float("nan")), extra, note))
    print("  share %-5s mean sagittal %.2f" % (share, np.mean(sags)))
