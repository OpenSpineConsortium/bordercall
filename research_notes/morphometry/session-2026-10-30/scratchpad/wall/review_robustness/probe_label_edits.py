"""The wall on two labels a real mask gives that the cache does not hold.

dens: C2, whose body carries the dens above it in front of the canal, so the body's points at the
midline run from the lower plate to the dens's tip and the window (the middle 60 per cent of
that height) stands mostly on the dens. A cervical-sized C2 phantom with a dens 9 mm across, its
back 1.5 mm in front of the body's wall, 14 mm tall and leaning back 12 degrees.

shell: a body labelled as its cortex alone, a shell 2 mm thick round a hollow, as a mask made by
thresholding bone gives; the wall's edge must stand at the back of WALL_RUN_MM of bone.

Each is read by body.posterior_wall and, for comparison, by the reading it replaced (old_slope,
copied from a9f21fd)."""
import math
import sys

import numpy as np
from scipy import ndimage

from common import draw_and_build, read, wall_truth_deg
from morphometry import body as BODY
from morphometry.tests import phantom as P
from probe_cervical import CERVICAL

LUMBAR = ["L2", "L3", "L4"]


def old_slope(v, B, xc):
    mid = B[np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    if len(mid) < 8:
        return 0.0
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    rows = []
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        if len(layer):
            rows.append((z, layer[:, 1].min()))
    if len(rows) < 3:
        return 0.0
    rows = np.array(rows)
    return float(np.polyfit(rows[:, 0], rows[:, 1], 1)[0])


def local_coords(lab, aff, placed, level):
    pl = [p for p in placed if p.level == level][0]
    idx = np.argwhere(np.ones(lab.shape, bool))
    world = idx @ aff[:3, :3].T + aff[:3, 3]
    return idx, (world - pl.c) @ pl.R


def add_dens(level, top_z, back_y=1.5, radius=4.5, height=14.0, lean_back_deg=12.0):
    def edit(lab, aff, placed):
        idx, q = local_coords(lab, aff, placed, level)
        rise = q[:, 2] - top_z
        yc = back_y + radius - rise * math.tan(math.radians(lean_back_deg))
        inside = (rise >= -1.0) & (rise <= height) & (q[:, 0] ** 2 + (q[:, 1] - yc) ** 2 <= radius ** 2)
        sel = tuple(idx[inside & (lab[tuple(idx.T)] == 0)].T)
        lab = lab.copy()
        lab[sel] = P.LEVEL_IDS[level]
        return lab
    return edit


def hollow(level, shell_mm):
    def edit(lab, aff, placed):
        spacing = np.linalg.norm(aff[:3, :3], axis=0)
        mine = lab == P.LEVEL_IDS[level]
        depth = ndimage.distance_transform_edt(mine, sampling=spacing)
        lab = lab.copy()
        lab[mine & (depth > shell_mm)] = 0
        return lab
    return edit


def report(tag, v, placed, lean):
    if "all" in v.flags:
        print("%-36s NOT BUILT: %s" % (tag, v.flags["all"]), flush=True)
        return
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    old = BODY.degrees_of(old_slope(v, B, xc)) - wall_truth_deg(v, placed, lean)
    err, info, _, _ = read(v, placed, lean)
    keep = {k: (round(x, 2) if isinstance(x, float) else x) for k, x in info.items()
            if k in ("edges", "span_mm", "parted", "free_deg", "why")}
    print("%-36s new %+.2f  old %+.2f  %s" % (tag, err, old, keep), flush=True)


which = sys.argv[1] if len(sys.argv) > 1 else "both"
tilts = {"x2": ((1.0, 0.0, 0.0), 2.0), "suite18": ((1.0, 0.3, 0.0), 18.0)}
if which in ("dens", "both"):
    for tname, tilt in tilts.items():
        kw = dict(CERVICAL)
        v0, pl0, _, _ = draw_and_build(["C2", "C3", "C4"], "C2", P.lumbar(**kw), tilt=tilt)
        report("C2 no dens %s" % tname, v0, pl0, 0.0)
        v1, pl1, _, _ = draw_and_build(["C2", "C3", "C4"], "C2", P.lumbar(**kw), tilt=tilt,
                                       edit=add_dens("C2", kw["Hp"] / 2))
        report("C2 with dens %s" % tname, v1, pl1, 0.0)
if which in ("shell", "both"):
    for tname, tilt in tilts.items():
        for shell in (1.5, 2.5, 4.0):
            v, pl, _, _ = draw_and_build(LUMBAR, "L3", P.lumbar(), tilt=tilt, edit=hollow("L3", shell))
            report("L3 shell %.1f mm %s" % (shell, tname), v, pl, 0.0)
