"""Prototype: the pedicle's sagittal angle from its top and bottom surfaces fitted as planes
over the axis rows and the columns across the middle half of the isthmus's section, beside the
current reading (the middles' slope over one column a row). Run with PYTHONPATH=bordercall."""
import math
import sys
import time

import numpy as np

from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]


def vert_of(which):
    if which == "mass":
        return P.lumbar(ped_waist=0.02, mass_w=8.0, mass_h=24.0, foramen_d=6.5)
    if which == "shapes":
        return P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0)
    if which == "pitched":
        return P.lumbar(ped_s=10.0)
    if which == "pitched_down":
        return P.lumbar(ped_s=-8.0, ped_t=8.0)
    return P.Vert()


def build_l3(v, tilt, turn):
    placed = P.straight(LUMBAR, v, tilt=tilt)
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
    vox = V.vertebra_voxels(lab, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    whole = M.whole_levels(vox, order, lab.shape)
    axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
    lv = "L3"
    return A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], lab.shape), M.neighbours_of(vox, order, lv))


def planes(m, rows, taken, near, k, sec, hgt):
    """(x, y, bottom, top) over the taken rows and the columns across the middle half of the
    isthmus's section out from each row's wall."""
    v = m.v
    pts = []
    for i in taken:
        r = rows[i]
        wall = r["u0"]
        us = np.arange(wall + 0.25 * sec, wall + 0.75 * sec + 1e-9, v.fx)
        for u in us:
            run = PED.height_run(v, m.x_of(float(u)), r["y"], rows[k]["z"] if i not in near else r["z"])
            if run is None:
                continue
            if abs((run[1] - run[0]) - hgt) > PED.HEIGHT_SHARE * hgt:
                continue
            pts.append((m.x_of(float(u)), r["y"], run[0], run[1]))
    return np.array(pts)


def fit_plane(x, y, z):
    Amat = np.column_stack([np.ones_like(x), y, x])
    coef, *_ = np.linalg.lstsq(Amat, z, rcond=None)
    return coef  # a, b (dz/dy), c (dz/dx)


def sagittal_from_planes(pts, across, side, v, mids_only=False):
    x, y, zb, zt = pts.T
    if mids_only:
        zm = 0.5 * (zb + zt)
        a, b, c = fit_plane(x, y, zm)
    else:
        ab, bb, cb = fit_plane(x, y, zb)
        at, bt, ct = fit_plane(x, y, zt)
        b, c = 0.5 * (bb + bt), 0.5 * (cb + ct)
    f = np.array([across, 1.0]) / math.hypot(across, 1.0)   # the level axis, forward, in (x, y)
    # across was fitted on side*walls against y, so in x terms dz/dx must be taken with side
    s_f = c * (side * f[0]) + b * f[1]
    return -math.degrees(math.atan(s_f)) - math.degrees(math.atan(PED.wall_slope(v))), len(pts), np.ptp(y)


def one(which, tilt, turn):
    v = vert_of(which)
    t0 = time.time()
    vert = build_l3(v, tilt, turn)
    truth = P.truth(v)
    zb = CANAL.body_span(vert)
    zs = PED.anchors(vert, zb)
    out = []
    for side, name in PED.SIDES:
        m = PED.SideMap(vert, side)
        rows = PED.profile(m, zs)
        got = PED.isthmus(rows, vert, m)
        if got is None:
            out.append((name, "no isthmus"))
            continue
        k, near, walls0 = got
        sec = float(np.median([rows[i]["w"] for i in near]))
        hgt = float(np.median([rows[i]["h"] for i in near]))
        taken, walls, mids = PED.axis_rows(m, rows, near, k, sec, hgt, walls0)
        d, note, reads = PED.axis_from(rows, taken, walls, mids, side)
        cur = math.degrees(math.atan2(d[2], -d[1])) - math.degrees(math.atan(PED.wall_slope(vert)))
        if reads != "both":
            cur = float("nan")
        across = np.polyfit(np.array([rows[i]["y"] for i in taken]), side * np.array([walls[i] for i in taken]), 1)[0] \
            if len(taken) >= 3 else 0.0
        pts = planes(m, rows, taken, near, k, sec, hgt)
        pl, n, span = sagittal_from_planes(pts, across, side, vert)
        pm, _, _ = sagittal_from_planes(pts, across, side, vert, mids_only=True)
        # the near rows alone
        pts_n = planes(m, rows, [i for i in taken if i in near], near, k, sec, hgt)
        pn, nn, spn = sagittal_from_planes(pts_n, across, side, vert) if len(pts_n) >= 3 else (float("nan"), len(pts_n), 0.0)
        out.append("%-5s current %6.2f  planes %6.2f (n=%d span %.1f)  mids-plane %6.2f  near-only %6.2f (n=%d span %.1f)  truth %5.2f  taken %d near %d fz %.2f" % (
            name, cur, pl, n, span, pm, pn, nn, spn, truth["pedicle_angle_sagittal"], len(taken), len(near), vert.fz))
    print("== %s tilt %s turn %s (%.0fs)" % (which, tilt, turn, time.time() - t0))
    for o in out:
        print("  ", o)
    sys.stdout.flush()


if __name__ == "__main__":
    which = sys.argv[1].split(",")
    configs = [(((1.0, 0.3, 0.0), 18.0), 7.0), (((1.0, 0.0, 0.0), 10.0), 0.0), (((1.0, 0.3, 0.0), 25.0), 15.0),
               (((0.3, 1.0, 0.0), 12.0), 4.0), (((1.0, -0.5, 0.2), 20.0), -9.0)]
    if len(sys.argv) > 2 and sys.argv[2] == "one":
        configs = configs[:1]
    for w in which:
        for tilt, turn in configs:
            one(w, tilt, turn)
