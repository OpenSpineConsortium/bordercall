"""Prototype 3 (prototype 2 with the lattice points admitted window by window): the pedicle's top and bottom surfaces as the surfaces that part the lattice's
bone centres from its air centres over the isthmus rows (a linear program: the widest margin),
each z = a + b y + c x' + d x'^2 with x' across the section from its middle, so the ellipse's
crown is the quadratic and the climb is b along the pedicle's centre line. Beside it the LS
plane of the per-window surfaces (prototype 1)."""
import math
import sys
import time

import numpy as np
from scipy.optimize import linprog

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


def build_l3(v, tilt, turn, spacing=(0.8, 0.8, 1.0)):
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
    lv = "L3"
    return A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], lab.shape), M.neighbours_of(vox, order, lv))


def windows(v, m, rows, chosen, sec, hgt):
    """The columns across the middle half of each chosen row's section whose run is the
    pedicle's (within HEIGHT_SHARE of the isthmus's height): (x0, y0, bottom, top)."""
    out = []
    for i in chosen:
        r = rows[i]
        for u in np.arange(r["u0"] + 0.25 * sec, r["u0"] + 0.75 * sec + 1e-9, v.fx):
            x0 = m.x_of(float(u))
            run = PED.height_run(v, x0, r["y"], r["z"])
            if run is not None and abs((run[1] - run[0]) - hgt) <= PED.HEIGHT_SHARE * hgt:
                out.append((x0, r["y"], run[0], run[1]))
    return np.array(out)


def lattice_in(v, m, win, u_of_y, sec, top, layers=1.5):
    """The lattice's points under the admitted windows, within `layers` of each window's own
    surface: (q, across, bone)."""
    xs, ys = win[:, 0], win[:, 1]
    zs = win[:, 3] if top else win[:, 2]
    corners = np.array([[x, y, z] for x in (xs.min() - v.pixel, xs.max() + v.pixel) for y in (ys.min() - v.pixel, ys.max() + v.pixel)
                        for z in (zs.min() - layers * v.fz - v.fz, zs.max() + layers * v.fz + v.fz)])
    inv = np.linalg.inv(np.asarray(v.grid.affine, float))
    cijk = v.points_world(corners) @ inv[:3, :3].T + inv[:3, 3]
    a, b = np.floor(cijk.min(0)).astype(int) - 1, np.ceil(cijk.max(0)).astype(int) + 1
    ijk = np.stack(np.meshgrid(*[np.arange(a[k], b[k] + 1) for k in range(3)], indexing="ij"), -1).reshape(-1, 3)
    q = v.frame.local(v.grid.world(ijk.astype(float)))
    dx = np.abs(q[:, 0][:, None] - xs[None, :])
    dy = np.abs(q[:, 1][:, None] - ys[None, :])
    dist = np.maximum(dx / (0.5 * v.pixel), dy / (0.25 * v.pixel + 1e-6))
    j = np.argmin(dist, axis=1)
    near_enough = dist[np.arange(len(q)), j] <= 1.0
    zsurf = zs[j]
    keep = near_enough & (np.abs(q[:, 2] - zsurf) <= layers * v.fz)
    q, ijk = q[keep], ijk[keep]
    u = m.side * (q[:, 0] - v.midline)
    uc = np.array([u_of_y(y) for y in q[:, 1]]) + 0.5 * sec
    return q, u - uc, v.is_bone(ijk)


def parting(y, xr, z, bone, top):
    """The surface z = a + b y + c xr + d xr^2 that parts bone from air with the widest margin:
    for the top surface bone lies below it and air above; for the bottom the other way. Returns
    (a, b, c, d, margin)."""
    F = np.column_stack([np.ones_like(y), y, xr, xr ** 2])
    # bone below (top): F w - z >= m  ->  -F w + m <= -z ; air above: z - F w >= m -> F w + m <= z
    sign = np.where(bone, -1.0, 1.0) if top else np.where(bone, 1.0, -1.0)
    A_ub = np.column_stack([sign[:, None] * F, np.ones(len(y))])
    b_ub = sign * z
    res = linprog(c=[0, 0, 0, 0, -1.0], A_ub=A_ub, b_ub=b_ub, bounds=[(None, None)] * 5, method="highs")
    if not res.success:
        return None
    return res.x


def one(which, tilt, turn, spacing=(0.8, 0.8, 1.0)):
    v = vert_of(which)
    t0 = time.time()
    vert = build_l3(v, tilt, turn, spacing)
    truth = P.truth(v)
    zb = CANAL.body_span(vert)
    zs = PED.anchors(vert, zb)
    out = []
    for side, name in PED.SIDES:
        m = PED.SideMap(vert, side)
        rows = PED.profile(m, zs)
        got = PED.isthmus(rows, vert, m)
        if got is None:
            out.append("%-5s no isthmus" % name)
            continue
        k, near, walls0 = got
        sec = float(np.median([rows[i]["w"] for i in near]))
        hgt = float(np.median([rows[i]["h"] for i in near]))
        taken, walls, mids = PED.axis_rows(m, rows, near, k, sec, hgt, walls0)
        d, note, reads = PED.axis_from(rows, taken, walls, mids, side)
        cur = math.degrees(math.atan2(d[2], -d[1])) - math.degrees(math.atan(PED.wall_slope(vert)))
        if reads != "both":
            cur = float("nan")
        line = PED.wall_line(rows, near, walls0)
        u_of_y = lambda y: float(np.polyval(line, y))  # noqa: E731
        across = line[0]
        fy = 1.0 / math.hypot(across, 1.0)
        wall_deg = math.degrees(math.atan(PED.wall_slope(vert)))
        res = {}
        for label, chosen in (("near", near), ("taken", taken)):
            win = windows(vert, m, rows, chosen, sec, hgt)
            if len(win) < 6:
                res[label] = (float("nan"), [float("nan")] * 2, [0, 0], 0.0)
                continue
            span = np.ptp(win[:, 1]) + 0.5 * vert.pixel
            slopes, margins, ns = [], [], []
            for top in (True, False):
                q, xr, bone = lattice_in(vert, m, win, u_of_y, sec, top)
                if len(q) < 12 or bone.sum() < 4 or (~bone).sum() < 4:
                    slopes.append(float("nan")); margins.append(float("nan")); ns.append(len(q))
                    continue
                w = parting(q[:, 1], xr, q[:, 2], bone, top)
                if w is None:
                    slopes.append(float("nan")); margins.append(float("nan")); ns.append(len(q))
                    continue
                slopes.append(w[1]); margins.append(w[4]); ns.append(len(q))
            b = 0.5 * (slopes[0] + slopes[1])
            res[label] = (-math.degrees(math.atan(b * fy)) - wall_deg, margins, ns, span)
        out.append("%-5s current %6.2f | LP near %6.2f (m %.2f/%.2f n %d/%d span %.1f) | LP taken %6.2f (m %.2f/%.2f n %d/%d span %.1f) | truth %5.2f fz %.2f" % (
            name, cur, res["near"][0], res["near"][1][0], res["near"][1][1], res["near"][2][0], res["near"][2][1], res["near"][3],
            res["taken"][0], res["taken"][1][0], res["taken"][1][1], res["taken"][2][0], res["taken"][2][1], res["taken"][3],
            truth["pedicle_angle_sagittal"], vert.fz))
    print("== %s tilt %s turn %s spacing %s (%.0fs)" % (which, tilt, turn, spacing, time.time() - t0))
    for o in out:
        print("  ", o)
    sys.stdout.flush()


if __name__ == "__main__":
    which = sys.argv[1].split(",")
    configs = [(((1.0, 0.3, 0.0), 18.0), 7.0), (((1.0, 0.0, 0.0), 10.0), 0.0), (((1.0, 0.3, 0.0), 25.0), 15.0),
               (((0.3, 1.0, 0.0), 12.0), 4.0), (((1.0, -0.5, 0.2), 20.0), -9.0)]
    spacing = (0.8, 0.8, 1.0)
    if len(sys.argv) > 2:
        spacing = tuple(float(x) for x in sys.argv[2].split(","))
    for w in which:
        for tilt, turn in configs:
            one(w, tilt, turn, spacing)
