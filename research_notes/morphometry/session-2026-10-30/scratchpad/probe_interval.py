"""Calibration probe for the climb's gates, on the committed pedicle.py: per side the climb's
two surfaces' slopes (degrees), margins, crossings, and the interval of slopes b that still part
the bone from the air once the least-crossing surface's crossed centres are set aside; with the
projection angle each would give. Run with PYTHONPATH=bordercall."""
import math
import sys
import time

import numpy as np
from scipy.optimize import linprog

from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
PHANTOMS = {
    "straight": {}, "shapes": dict(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0),
    "pitched": dict(ped_s=10.0), "pitched_down": dict(ped_s=-8.0, ped_t=8.0),
    "overhang": dict(sap_x=19.0, sap_y=-10.0, facet=0.0, sap_thk=3.5, sap_len=14.0),
    "steep": dict(ped_t=25.0, ped_s=12.0),
}


def build_l3(v, tilt, turn, spacing):
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
    return A.build("L3", vox["L3"], grid, axes["L3"], V.touching_edge(vox["L3"], lab.shape), M.neighbours_of(vox, order, "L3"))


def interval(y, across, z, bone, top, keep):
    F = np.column_stack([np.ones_like(y), y, across, across ** 2])[keep]
    sign = (np.where(bone, -1.0, 1.0) if top else np.where(bone, 1.0, -1.0))[keep]
    zz = z[keep]
    out = []
    for c in ([0, 1, 0, 0], [0, -1, 0, 0]):
        res = linprog(c=c, A_ub=sign[:, None] * F, b_ub=sign * zz, bounds=[(None, None)] * 4, method="highs")
        out.append(res.x[1] if res.success else (float("-inf") if c[1] > 0 else float("inf")))
    return out


def one(name, tilt, turn, spacing):
    v = P.lumbar(**PHANTOMS[name])
    vert = build_l3(v, tilt, turn, spacing)
    truth = P.truth(v)["pedicle_angle_sagittal"]
    zb = CANAL.body_span(vert)
    lines = []
    wall_deg = math.degrees(math.atan(PED.wall_slope(vert)))
    for side, sname in PED.SIDES:
        m = PED.SideMap(vert, side)
        rows = PED.profile(m, PED.anchors(vert, zb))
        got = PED.isthmus(rows, vert, m)
        if got is None:
            lines.append("%-5s no isthmus" % sname)
            continue
        k, near, walls = got
        sec = float(np.median([rows[i]["w"] for i in near]))
        hgt = float(np.median([rows[i]["h"] for i in near]))
        taken, walls = PED.axis_rows(m, rows, near, k, walls)
        cols = PED.columns(m, rows, near, sec, hgt)
        span = float(np.ptp(cols[:, 1])) + 0.5 * vert.pixel if len(cols) else 0.0
        if len(cols) < PED.MIN_COLUMNS:
            lines.append("%-5s %d columns" % (sname, len(cols)))
            continue
        line = PED.wall_line(rows, near, walls)
        y_t = np.array([rows[i]["y"] for i in taken])
        across_t = np.polyfit(y_t, side * np.array([walls[i] for i in taken]), 1)[0] if len(taken) >= 3 else 0.0
        parts = []
        bs = []
        for top in (True, False):
            q, xr, bone = PED.lattice_under(m, cols, line, sec, top)
            got2 = PED.parting(q[:, 1], xr, q[:, 2], bone, top)
            if got2 is None:
                parts.append("none"); bs.append(float("nan")); continue
            b = float(got2["coefficients"][1])
            F = np.column_stack([np.ones_like(q[:, 1]), q[:, 1], xr, xr ** 2])
            sign = np.where(bone, -1.0, 1.0) if top else np.where(bone, 1.0, -1.0)
            slack = sign * (F @ got2["coefficients"]) - sign * q[:, 2]
            keep = slack <= 1e-9
            lo, hi = interval(q[:, 1], xr, q[:, 2], bone, top, keep)
            ang = lambda bb: -math.degrees(math.atan(bb)) - wall_deg  # noqa: E731
            parts.append("%s %6.2f [%6.1f %6.1f] m %5.2f x %d/%d" % ("T" if top else "B", ang(b), ang(hi), ang(lo), got2["margin"], got2["across"], len(q)))
            bs.append(b)
        rise = 0.5 * (bs[0] + bs[1])
        proj = -math.degrees(math.atan(rise)) - wall_deg
        lines.append("%-5s span %4.1f n %3d | %s | %s | proj %6.2f truth %5.1f" % (sname, span, len(cols), parts[0], parts[1], proj, truth))
    print("== %s tilt %s turn %s spacing %s fz %.2f" % (name, tilt, turn, spacing, vert.fz))
    for ln in lines:
        print("   ", ln)
    sys.stdout.flush()


if __name__ == "__main__":
    names = sys.argv[1].split(",")
    spacing = tuple(float(x) for x in sys.argv[2].split(","))
    which = sys.argv[3] if len(sys.argv) > 3 else "thin"
    if which == "thick":
        configs = [(((1.0, 0.0, 0.0), 20.0), 0.0), (((1.0, 0.0, 0.0), 5.0), 0.0), (((1.0, 0.0, 0.0), 0.0), 0.0),
                   (((1.0, 0.3, 0.0), 12.0), 9.0), (((1.0, 0.0, 0.0), 30.0), 0.0)]
    else:
        configs = [(((1.0, 0.3, 0.0), 18.0), 7.0), (((1.0, 0.0, 0.0), 10.0), 0.0), (((1.0, 0.3, 0.0), 25.0), 15.0),
                   (((0.3, 1.0, 0.0), 12.0), 4.0), (((1.0, -0.5, 0.2), 20.0), -9.0), (((1.0, 0.0, 0.0), 2.0), 0.0)]
    for n in names:
        for tilt, turn in configs:
            t0 = time.time()
            one(n, tilt, turn, spacing)
