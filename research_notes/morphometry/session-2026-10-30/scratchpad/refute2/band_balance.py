"""band_balance.py <variant> <sx> <sy> <sz> <tilt axis x,y,z> <tilt deg> <turn deg>: build a phantom's
L3, run the pedicle reading, and tally the bone and air centres of each surface's band as a whole
and per column, to see how far one class can dominate what lattice_under keeps."""
import sys, time
from collections import Counter
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

variant = sys.argv[1]
spacing = tuple(float(s) for s in sys.argv[2:5])
axis = tuple(float(s) for s in sys.argv[5].split(","))
tilt = float(sys.argv[6]); turn = float(sys.argv[7])
LUMBAR = ["L2", "L3", "L4"]
if variant == "shapes":
    v = P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0)
elif variant == "pitched":
    v = P.lumbar(ped_s=10.0)
else:
    v = P.Vert()
t0 = time.time()
placed = P.straight(LUMBAR, v, tilt=(axis, tilt))
lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
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
print("%s %s tilt %s %.0f turn %.0f: built in %.0fs; fz %.2f pixel %.2f" % (variant, spacing, axis, tilt, turn, time.time() - t0, vert.fz, vert.pixel), flush=True)
zb = CANAL.body_span(vert)
for side, name in PED.SIDES:
    out, note, info = PED.one_side(vert, side, zb)
    if info is None:
        print(name, "not read:", note); continue
    rows, near, walls = info["rows"], info["near"], info["walls"]
    sec = float(np.median([rows[i]["w"] for i in near]))
    hgt = float(np.median([rows[i]["h"] for i in near]))
    cols = PED.columns(SM := PED.SideMap(vert, side), rows, near, sec, hgt)
    line = PED.wall_line(rows, near, walls)
    print("%s: sag %.2f (%s) columns %d" % (name, out.get("pedicle_angle_sagittal", float("nan")), note or "ok", len(cols)))
    for top, sname in ((True, "top"), (False, "bottom")):
        q, across, bone = PED.lattice_under(SM, cols, line, sec, top)
        xs, ys = cols[:, 0], cols[:, 1]
        apart = np.maximum(np.abs(q[:, :1] - xs[None, :]) / (0.5 * vert.pixel),
                           np.abs(q[:, 1:2] - ys[None, :]) / (0.25 * vert.pixel + 1e-6))
        j = np.argmin(apart, axis=1)
        per = Counter()
        for c in np.unique(j):
            b = int(bone[j == c].sum()); a = int((~bone[j == c]).sum())
            per[(b, a)] += 1
        nb, na = int(bone.sum()), int((~bone).sum())
        got = PED.parting(q[:, 1], across, q[:, 2], bone, top)
        print("  %-6s bone %3d air %3d  minority share %.2f  VIOLATED_SHARE*len(q) = %.1f = %.0f%% of the minority; across %d margin %.3f"
              % (sname, nb, na, min(nb, na) / len(q), PED.VIOLATED_SHARE * len(q), 100 * PED.VIOLATED_SHARE * len(q) / min(nb, na), got["across"], got["margin"]))
        print("         per-column (bone, air) -> columns: %s" % sorted(per.items()))
