"""C2 with a dens, read by body.posterior_wall and by the reading it replaced, to test the claim
that C2's wall is read largely on the dens and is off by degrees with no flag.

The dens here is drawn independently of the reviewer's probe: an elliptic cylinder, half-widths
rx across and ry front to back, standing on the body's top from 1 mm inside it, its back at
back_y in front of the body's wall plane (y = 0) at its base, leaning back by lean_deg as it
rises. The body's wall is upright (lean 0), so the truth is the frame's view of the local z axis.

  probe_c2.py <thin|thick> <Hp> [tilts]
"""
import math
import sys

import numpy as np

from morphometry import anatomy as A, body as BODY, measure as M, pedicle as PED, posterior as POST
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

CERV = dict(W=17.0, D=16.0, canal_w=24.0, ped_w=5.5, ped_h=7.0, ped_z=2.0, ped_back=4.0,
            ped_t=45.0, mass_w=7.0, mass_h=10.0, foramen_d=5.5, pil_x=17.0, pil_y=-10.0, lam_t=4.0,
            lam_ap_top=14.0, lam_slope=10.0, lam_top=6.0, lam_bot=-8.0, sap_x=18.0, sap_y=-11.0, sap_len=8.0,
            sap_thk=4.0, sap_top=13.0, iap_x=17.0, iap_y=-13.0, iap_len=8.0, iap_thk=4.0, iap_bot=-13.0,
            facet=80.0, TP=50.0, tp_y=-6.0, tp_thk=5.0, tp_z=1.0, tp_h=6.0, LS=18.0, sp_angle=20.0, sp_hw=2.5,
            sp_hh=3.0)
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
TILTS = {"x0": ((1.0, 0.0, 0.0), 0.0), "x2": ((1.0, 0.0, 0.0), 2.0), "suite18": ((1.0, 0.3, 0.0), 18.0)}


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


def dens_edit(top_z, back_y, lean_deg, rx=4.5, ry=5.0, height=14.0):
    def edit(lab, aff, placed):
        pl = [p for p in placed if p.level == "C2"][0]
        idx = np.argwhere(np.ones(lab.shape, bool))
        q = (idx @ aff[:3, :3].T + aff[:3, 3] - pl.c) @ pl.R
        rise = q[:, 2] - top_z
        yc = back_y + ry - rise * math.tan(math.radians(lean_deg))
        inside = ((rise >= -1.0) & (rise <= height)
                  & ((q[:, 0] / rx) ** 2 + ((q[:, 1] - yc) / ry) ** 2 <= 1.0))
        sel = tuple(idx[inside & (lab[tuple(idx.T)] == 0)].T)
        lab = lab.copy()
        lab[sel] = P.LEVEL_IDS["C2"]
        return lab
    return edit


def build(vert, spacing, tilt, edit):
    levels = ["C2", "C3", "C4"]
    placed = P.straight(levels, vert, tilt=tilt)
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
    if edit is not None:
        lab = edit(lab, aff, placed)
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in levels})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    v = A.build("C2", vox["C2"], grid, axes["C2"], V.touching_edge(vox["C2"], lab.shape),
                M.neighbours_of(vox, order, "C2"))
    return v, placed


def truth_deg(v, placed):
    R = [pl for pl in placed if pl.level == "C2"][0].R
    w = R[:, 2]
    return math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))


def frame_z(v, world):
    """A world point's z in v's frame."""
    return float((world - v.frame.origin) @ v.frame.ez)


def report(tag, v, placed, vert):
    if "all" in v.flags:
        print("%-44s NOT BUILT %s" % (tag, v.flags["all"]), flush=True)
        return
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    v.__dict__.pop("_posterior_wall", None)
    place, why = BODY.wall_window(v, B, xc)
    slope, info = BODY.posterior_wall(v, B, xc)
    t = truth_deg(v, placed)
    new = BODY.degrees_of(slope) - t if math.isfinite(slope) else float("nan")
    old = BODY.degrees_of(old_slope(v, B, xc)) - t
    # the body's own top and bottom at the wall, local (0, 0, +-Hp/2), in v's frame
    pl = [p for p in placed if p.level == "C2"][0]
    loc_top = pl.c + pl.R @ np.array([0.0, 0.0, vert.Hp / 2])
    loc_bot = pl.c + pl.R @ np.array([0.0, 0.0, -vert.Hp / 2])
    zt, zb = frame_z(v, loc_top), frame_z(v, loc_bot)
    share = float("nan")
    if place:
        lo, hi = place[2], place[3]
        share = max(0.0, hi - max(lo, zt)) / (hi - lo)
    got, flags = BODY.measures(v)
    wf = sorted(k for k in flags if k.startswith("posterior_wall"))
    print("%-44s new %+6.2f old %+6.2f free %5.2f edges %s span %s window %.1f..%.1f body z %.1f..%.1f "
          "dens share of window %.2f flags %s" % (
              tag, new, old, info.get("free_deg", float("nan")), info.get("edges"), round(info.get("span_mm", float("nan")), 1),
              place[2] if place else float("nan"), place[3] if place else float("nan"), zb, zt, share, wf), flush=True)


def main():
    sname = sys.argv[1]
    Hp = float(sys.argv[2])
    tilts = sys.argv[3].split(",") if len(sys.argv) > 3 else list(TILTS)
    vert = P.lumbar(Hp=Hp, Ha=Hp, **CERV)
    cases = [("no dens", None)]
    for back_y, lean in ((0.0, 0.0), (0.0, 12.0), (1.0, 0.0), (1.0, 12.0), (-1.0, 12.0)):
        cases.append(("dens back %+.1f lean %.0f" % (back_y, lean), dens_edit(Hp / 2, back_y, lean)))
    for tname in tilts:
        for cname, edit in cases:
            v, placed = build(vert, SPACINGS[sname], TILTS[tname], edit)
            report("H%.0f %s %s %s" % (Hp, sname, tname, cname), v, placed, vert)


if __name__ == "__main__":
    main()
