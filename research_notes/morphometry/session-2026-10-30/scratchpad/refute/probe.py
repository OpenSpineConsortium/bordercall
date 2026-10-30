"""probe.py <variant> <sx> <sy> <sz> <tilt axis x,y,z> <tilt deg> <turn deg>: run climb on a phantom's L3
and record every linprog status inside pedicle.parting."""
import sys, time
import numpy as np
from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

variant = sys.argv[1]
spacing = tuple(float(s) for s in sys.argv[2:5])
axis = tuple(float(s) for s in sys.argv[5].split(","))
tilt = float(sys.argv[6]); turn = float(sys.argv[7])
LUMBAR = ["L2", "L3", "L4"]
if variant == "small":
    v = P.lumbar(ped_w=6.0, ped_h=7.0, ped_back=3.0)
elif variant == "shapes":
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
print("drawn in %.0fs shape %s" % (time.time() - t0, lab.shape), flush=True)

statuses = []
real = PED.linprog
def spy(*a, **k):
    res = real(*a, **k)
    statuses.append((res.status, bool(res.success)))
    return res
PED.linprog = spy

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
print("fx fy fz %.2f %.2f %.2f pixel %.2f" % (vert.fx, vert.fy, vert.fz, vert.pixel))
zb = CANAL.body_span(vert)
zs = PED.anchors(vert, zb)
for side, name in PED.SIDES:
    m = PED.SideMap(vert, side)
    rows = PED.profile(m, zs)
    got = PED.isthmus(rows, vert, m)
    if got is None:
        print(name, "no isthmus"); continue
    k, near, walls0 = got
    sec = float(np.median([rows[i]["w"] for i in near]))
    hgt = float(np.median([rows[i]["h"] for i in near]))
    taken, walls = PED.axis_rows(m, rows, near, k, walls0)
    statuses.clear()
    rise, why, rec = PED.climb(m, rows, near, walls, sec, hgt)
    print("%s: %d columns span %.1f rise %s note %r statuses %s" % (name, len(rec["columns"]), rec["span"], rise, why, statuses))
    for s in ("top", "bottom"):
        if s in rec:
            print("   ", s, {kk: vv for kk, vv in rec[s].items() if kk != "coefficients"},
                  "slope %.4f" % rec[s]["coefficients"][1] if "coefficients" in rec[s] else "")
    # how the kept centres sit: per column, bone and air counts
    line = PED.wall_line(rows, near, walls)
    cols = rec["columns"]
    if len(cols):
        for top in (True, False):
            q, across, bone = PED.lattice_under(m, cols, line, sec, top)
            xs, ys = cols[:, 0], cols[:, 1]
            apart = np.maximum(np.abs(q[:, :1] - xs[None, :]) / (0.5 * vert.pixel), np.abs(q[:, 1:2] - ys[None, :]) / (0.25 * vert.pixel + 1e-6))
            j = np.argmin(apart, axis=1)
            both = sum(1 for c in range(len(cols)) if bone[j == c].any() and (~bone[j == c]).any())
            only_b = sum(1 for c in range(len(cols)) if bone[j == c].any() and not (~bone[j == c]).any())
            only_a = sum(1 for c in range(len(cols)) if (~bone[j == c]).any() and not bone[j == c].any())
            print("    %s: centres %d (bone %d) columns with both %d, bone only %d, air only %d" % ("top" if top else "bottom", len(q), bone.sum(), both, only_b, only_a))
print("total %.0fs" % (time.time() - t0))
