"""The phantoms the new tests draw, read with the new wall and the old one: the wall's error in the
measured frame and the end-plates' inclinations against their truths, with the time each build
takes. The old reader is body.posterior_wall_slope as it stood at a9f21fd, copied here.

  PYTHONPATH=<bordercall> python probe_tests.py [name ...]
"""
import math
import sys
import time

import numpy as np

from morphometry import anatomy as A, body as BODY, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]


def old_wall(v, B, xc):
    mid = B[np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    if len(mid) < G.MIN_CHORD_POINTS:
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


def built(placed, level, spacing, grid_turn, strict=True):
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=grid_turn, strict=strict)
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in LUMBAR})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    return A.build(level, vox[level], grid, axes[level], V.touching_edge(vox[level], lab.shape),
                   M.neighbours_of(vox, order, level))


def wall_truth(vert, placed, lean):
    R = [p for p in placed if p.level == "L3"][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    return math.degrees(math.atan((vert.frame.ey @ w) / (vert.frame.ez @ w)))


CASES = {
    "leaned_x2": dict(v=dict(lean=5.0), tilt=((1.0, 0.0, 0.0), 2.0), turn=0.0, spacing=(0.8, 0.8, 1.0)),
    "notch_up": dict(v=dict(notch_w=6.0, notch_h=4.0, notch_d=2.0, notch_z=4.0), tilt=((1.0, 0.3, 0.0), 18.0),
                     turn=7.0, spacing=(0.8, 0.8, 1.0)),
    "notch_deep": dict(v=dict(notch_w=5.0, notch_h=6.0, notch_d=4.0), tilt=((1.0, 0.3, 0.0), 18.0), turn=7.0,
                       spacing=(0.8, 0.8, 1.0)),
    "thickslices": dict(v=dict(), tilt=((1.0, 0.0, 0.0), 20.0), turn=0.0, spacing=(0.86, 0.86, 2.5)),
}


def main():
    for name in sys.argv[1:] or list(CASES):
        c = CASES[name]
        t0 = time.time()
        pv = P.lumbar(**c["v"])
        placed = P.straight(LUMBAR, pv, tilt=c["tilt"])
        vert = built(placed, "L3", c["spacing"], ((0.0, 0.0, 1.0), c["turn"]))
        t1 = time.time()
        B = vert.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        new, info = BODY.posterior_wall(vert, B, xc)
        old = old_wall(vert, B, xc)
        truth = wall_truth(vert, placed, pv.lean)
        got, flags = BODY.measures(vert)
        t = P.truth(pv)
        line = "%-12s build %.0f s; wall new %+.2f old %+.2f truth %+.2f (err new %+.2f old %+.2f) free %.2f parted %s" % (
            name, t1 - t0, BODY.degrees_of(new), BODY.degrees_of(old), truth, BODY.degrees_of(new) - truth,
            BODY.degrees_of(old) - truth, info.get("free_deg", float("nan")), info.get("parted"))
        print(line)
        for k in ("endplate_incl", "endplate_lower_incl"):
            rim = -math.radians(got[k]) - math.atan(new)
            old_incl = -math.degrees(rim + math.atan(old))
            want = t[k] - pv.lean           # both plates are taken against the leaned wall
            print("    %-20s new %+.2f old %+.2f truth %+.2f (err new %+.2f old %+.2f)" % (
                k, got[k], old_incl, want, got[k] - want, old_incl - want))
        print("    flags", flags, "info", {k: info[k] for k in info if k != "why"}, info.get("why", ""))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
