"""Check a reviewer's claim that C2's posterior wall is read on the dens.

A C2 phantom is the package's lumbar-shaped vertebra at cervical sizes with a dens drawn on top:
an elliptic cylinder, its back a set distance in front of the body's wall at its base (negative
stands proud), leaning back a set angle as it rises. The C2 level is built as measure_volume
builds it, and its wall read by body.posterior_wall (the change) and by the reading of a9f21fd
(copied), each against the phantom's wall taken into the measured frame. The window and the
share of the window and of the kept edges that lie above the body's top are printed, and so are
C2's rows from measure_volume: endplate_lower_incl, both sagittal pedicle angles, spinous_angle
and the flags.

  dens_probe.py <thin|thick> <grid name> <case name>[,<case name>...]
"""
import math
import sys

import numpy as np

from morphometry import anatomy as A, body as BODY, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LEVELS_DRAWN = ["C2", "C3", "C4"]
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
GRIDS = {"x2": (((1.0, 0.0, 0.0), 2.0), ((0.0, 0.0, 1.0), 0.0)),
         "suite18": (((1.0, 0.3, 0.0), 18.0), ((0.0, 0.0, 1.0), 7.0)),
         "x0": (((1.0, 0.0, 0.0), 0.0), ((0.0, 0.0, 1.0), 0.0))}
# A C5-sized body as the reviewer's, and a taller one closer to C2's own body under its dens.
SMALL = dict(W=17.0, D=16.0, Hp=14.0, Ha=14.0, canal_w=24.0, ped_w=5.5, ped_h=7.0, ped_z=2.0, ped_back=4.0,
             ped_t=45.0, ped_s=0.0, mass_w=7.0, mass_h=10.0, foramen_d=5.5, pil_x=17.0, pil_y=-10.0, lam_t=4.0,
             lam_ap_top=14.0, lam_slope=10.0, lam_top=6.0, lam_bot=-8.0, sap_x=18.0, sap_y=-11.0, sap_len=8.0,
             sap_thk=4.0, sap_top=13.0, iap_x=17.0, iap_y=-13.0, iap_len=8.0, iap_thk=4.0, iap_bot=-13.0,
             facet=80.0, TP=50.0, tp_y=-6.0, tp_thk=5.0, tp_z=1.0, tp_h=6.0, LS=18.0, sp_angle=20.0, sp_hw=2.5,
             sp_hh=3.0)
# case: (body overrides, dens depth, dens width, dens height, back offset at base, lean back degrees)
CASES = {
    "none": ({}, None, None, None, None, None),
    "flush0": ({}, 9.0, 9.0, 14.0, 0.0, 0.0),
    "rec1.5_0": ({}, 9.0, 9.0, 14.0, 1.5, 0.0),
    "rec1.5_12": ({}, 9.0, 9.0, 14.0, 1.5, 12.0),
    "flush10": ({}, 9.0, 9.0, 14.0, 0.0, 10.0),
    "tall_none": ({"Hp": 20.0, "Ha": 20.0}, None, None, None, None, None),
    "tall_flush10": ({"Hp": 20.0, "Ha": 20.0}, 10.0, 9.0, 15.0, 0.0, 10.0),
    "tall_rec2_10": ({"Hp": 20.0, "Ha": 20.0}, 10.0, 9.0, 15.0, 2.0, 10.0),
}


def dens_edit(placed, vert, depth, width, height, back0, lean_back):
    """Draw C2's dens onto the label: from 1 mm under the body's top to `height` above it."""
    pl = [p for p in placed if p.level == "C2"][0]
    top = vert.Hp / 2

    def edit(lab, aff):
        idx = np.argwhere(np.ones(lab.shape, bool))
        q = (idx @ aff[:3, :3].T + aff[:3, 3] - pl.c) @ pl.R
        rise = q[:, 2] - top
        back = back0 - rise * math.tan(math.radians(lean_back))
        yc = back + depth / 2
        inside = ((rise >= -1.0) & (rise <= height)
                  & ((q[:, 0] / (width / 2)) ** 2 + ((q[:, 1] - yc) / (depth / 2)) ** 2 <= 1.0))
        out = lab.copy()
        free = inside & (lab[tuple(idx.T)] == 0)
        out[tuple(idx[free].T)] = P.LEVEL_IDS["C2"]
        return out
    return edit


def old_slope(v, B, xc):
    """body.posterior_wall_slope as it stood at a9f21fd."""
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


def build_c2(lab, aff):
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in LEVELS_DRAWN})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    return A.build("C2", vox["C2"], grid, axes["C2"], V.touching_edge(vox["C2"], lab.shape),
                   M.neighbours_of(vox, order, "C2")), grid


def in_frame(v, pl, local_pt):
    """A point of the phantom's own frame in the measured frame."""
    world = pl.c + pl.R @ np.asarray(local_pt, float)
    return v.frame.local(world[None, :])[0]


def wall_truth_deg(v, pl):
    w = pl.R @ np.array([0.0, 0.0, 1.0])
    return math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))


def window_and_edges(v, B, xc):
    place, why = BODY.wall_window(v, B, xc)
    if place is None:
        return None, None, why
    half, reach, lo, hi = place
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    return (lo, hi), bone, ""


def run(sname, gname, cname):
    over, depth, width, height, back0, lean_back = CASES[cname]
    vert = P.lumbar(**dict(SMALL, **over))
    tilt, turn = GRIDS[gname]
    placed = P.straight(LEVELS_DRAWN, vert, tilt=tilt)
    lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=turn, strict=False)
    if depth is not None:
        lab = dens_edit(placed, vert, depth, width, height, back0, lean_back)(lab, aff)
    v, grid = build_c2(lab, aff)
    tag = "%-5s %-7s %-13s" % (sname, gname, cname)
    if "all" in v.flags:
        print(tag, "NOT BUILT", v.flags["all"], flush=True)
        return
    pl = [p for p in placed if p.level == "C2"][0]
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    truth = wall_truth_deg(v, pl)
    v.__dict__.pop("_posterior_wall", None)
    slope, info = BODY.posterior_wall(v, B, xc)
    new_err = BODY.degrees_of(slope) - truth if math.isfinite(slope) else float("nan")
    old_err = BODY.degrees_of(old_slope(v, B, xc)) - truth
    body_top = in_frame(v, pl, (0.0, 0.0, vert.Hp / 2))[2]
    body_bot = in_frame(v, pl, (0.0, 0.0, -vert.Hp / 2))[2]
    win, bone, why = window_and_edges(v, B, xc)
    if win is not None:
        lo, hi = win
        share_win = max(0.0, hi - max(lo, body_top)) / (hi - lo)
        share_edges = float((bone[:, 2] > body_top).mean()) if len(bone) else float("nan")
        wtxt = "window %.1f..%.1f (body %.1f..%.1f) on dens %.0f%% edges on dens %.0f%%" % (
            lo, hi, body_bot, body_top, 100 * share_win, 100 * share_edges)
    else:
        wtxt = "no window: " + why
    keep = {k: (round(x, 2) if isinstance(x, float) else x) for k, x in info.items()
            if k in ("edges", "span_mm", "parted", "free_deg", "why")}
    print("%s wall new %+.2f old %+.2f  %s  %s" % (tag, new_err, old_err, wtxt, keep), flush=True)
    names = {P.LEVEL_IDS[lv]: lv for lv in LEVELS_DRAWN}
    rows = {}
    for r in M.measure_volume(lab, grid, names, "phantom", pelvis=False):
        if r["level"] == "C2":
            rows[r["key"]] = r["value"] if not r["key"].startswith("flag") else r["note"]
    t = P.truth(vert)
    def err(k):
        x = rows.get(k, float("nan"))
        return x - t[k] if isinstance(x, float) and math.isfinite(x) else float("nan")
    flags = sorted(k for k in rows if k.startswith("flag:"))
    wall_flags = {k: rows[k][:60] for k in flags if "wall" in k or "spinous" in k}
    print("%s rows: endplate_lower_incl %+.2f  ped_sag R %+.2f L %+.2f  spinous %+.2f  flags %s %s" % (
        tag, err("endplate_lower_incl"), err_side(rows, t, "right"), err_side(rows, t, "left"), err("spinous_angle"),
        flags, wall_flags), flush=True)


def err_side(rows, t, side):
    for k in ("pedicle_angle_sagittal_" + side, "pedicle_%s_angle_sagittal" % side):
        if k in rows:
            x = rows[k]
            return x - t["pedicle_angle_sagittal"] if isinstance(x, float) and math.isfinite(x) else float("nan")
    return float("nan")


if __name__ == "__main__":
    sname, gname = sys.argv[1], sys.argv[2]
    for cname in sys.argv[3].split(","):
        run(sname, gname, cname)
