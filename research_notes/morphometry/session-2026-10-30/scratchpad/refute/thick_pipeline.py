"""The real pipeline on the thick-slice phantom: 0.86 x 0.86 x 2.5 mm, the column tilted
THETA about x, no grid turn, L2 to L4 with the pedicles pitched PED_S; L3's sagittal angle
beside the truth, with each surface's slope and margin as parting() returned them."""
import math, sys, time
import numpy as np
from morphometry import measure as M, pedicle as PED
from morphometry.tests import phantom as P
from scanimport import geometry as G

theta, ped_s = float(sys.argv[1]), float(sys.argv[2])
dz = float(sys.argv[3]) if len(sys.argv) > 3 else 2.5
px = 0.86 if dz > 1.5 else 0.8
log = []
real = PED.parting
def logged(y, across, z, bone, top):
    got = real(y, across, z, bone, top)
    if got is not None:
        log.append((top, math.degrees(math.atan(got["coefficients"][1])), got["margin"], got["across"], len(y), float(np.ptp(y))))
    return got
PED.parting = logged
real_side = PED.one_side
def side_logged(v, side, zb):
    log.append(("%s %s" % (v.level, "right" if side > 0 else "left"), float("nan"), float("nan"), 0, 0, 0.0))
    return real_side(v, side, zb)
PED.one_side = side_logged
real_wall = PED.wall_slope
def wall_logged(v):
    w = real_wall(v)
    log.append(("wall_slope %.2f deg" % math.degrees(math.atan(w)), float("nan"), float("nan"), 0, 0, 0.0))
    return w
PED.wall_slope = wall_logged

t0 = time.time()
v = P.lumbar(ped_s=ped_s)
lab, aff = P.draw(P.straight(["L2", "L3", "L4"], v, tilt=((1.0, 0.0, 0.0), theta)), spacing=(px, px, dz),
                  grid_turn=((0.0, 0.0, 1.0), 0.0))
grid = G.VoxelGrid(aff, lab.shape)
names = {P.LEVEL_IDS[lv]: lv for lv in ["L2", "L3", "L4"]}
rows = {}
for r in M.measure_volume(lab, grid, names, "phantom", pelvis=False):
    rows.setdefault(r["level"], {})[r["key"]] = r["value"] if not r["key"].startswith("flag") else r["note"]
print("tilt %.0f about x, ped_s %.0f, slices %.1f mm, %.0fs" % (theta, ped_s, dz, time.time() - t0))
for lv in ("L2", "L3", "L4"):
    row = rows.get(lv, {})
    print("  %s sagittal right %6.2f left %6.2f mean %6.2f | transverse %6.2f | h %5.2f (truth h %.1f)" % (
        lv, row.get("pedicle_angle_sagittal_right", float("nan")), row.get("pedicle_angle_sagittal_left", float("nan")),
        row.get("pedicle_angle_sagittal", float("nan")), row.get("pedicle_angle_transverse", float("nan")),
        row.get("pedicle_h", float("nan")), v.ped_h))
    for k, val in row.items():
        if k.startswith("flag") and "pedicle" in k:
            print("    ", k, val)
print("  parting calls (top?, slope deg, margin, across, n, y span):")
for e in log:
    print(("    %5s %6.1f m %.2f x %d n %d span %.1f" % e) if isinstance(e[0], bool) else "   " + e[0])
