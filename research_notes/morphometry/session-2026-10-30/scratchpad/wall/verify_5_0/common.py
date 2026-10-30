"""Shared helpers for checking the claim that, on cervical bodies, the wall's 6 mm band reaches the
pedicles' roots and biases body.posterior_wall: one phantom level built as measure_volume builds
it, the wall's truth in the measured frame, the reading at a given band cap, and a phantom whose
pedicles are clipped where they stand outside the body inside the band's reach."""
import math

import numpy as np

from morphometry import anatomy as A, body as BODY, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

# the reviewer's C5 (probe_cervical.py), kept as it was so the claim is read on its own phantom
CERVICAL = dict(W=17.0, D=16.0, Hp=14.0, Ha=14.0, canal_w=24.0, ped_w=5.5, ped_h=7.0, ped_z=2.0, ped_back=4.0,
                ped_t=45.0, mass_w=7.0, mass_h=10.0, foramen_d=5.5, pil_x=17.0, pil_y=-10.0, lam_t=4.0,
                lam_ap_top=14.0, lam_slope=10.0, lam_top=6.0, lam_bot=-8.0, sap_x=18.0, sap_y=-11.0, sap_len=8.0,
                sap_thk=4.0, sap_top=13.0, iap_x=17.0, iap_y=-13.0, iap_len=8.0, iap_thk=4.0, iap_bot=-13.0,
                facet=80.0, TP=50.0, tp_y=-6.0, tp_thk=5.0, tp_z=1.0, tp_h=6.0, LS=18.0, sp_angle=20.0, sp_hw=2.5,
                sp_hh=3.0)
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5), "fine": (0.4, 0.4, 0.6)}
TILTS = {"x0": ((1.0, 0.0, 0.0), 0.0), "x2": ((1.0, 0.0, 0.0), 2.0), "x5": ((1.0, 0.0, 0.0), 5.0),
         "suite18": ((1.0, 0.3, 0.0), 18.0)}

ORIGINAL_PEDICLE = P.pedicle_inside
CLIP_X_MM = 7.0   # the band's 6 mm and a pixel's margin: pedicle bone outside the body nearer the midline goes


def clipped_pedicle(q, v, side):
    """The pedicle less what stands outside the body within CLIP_X_MM of the midline: its root's
    medial lip behind the body's surface, which is all the band can see of it."""
    keep = ORIGINAL_PEDICLE(q, v, side)
    return keep & ~((np.abs(q[:, 0]) < CLIP_X_MM) & ~P.body_inside(q, v))


def build(levels, level, vert, spacing, tilt, clip=False):
    P.pedicle_inside = clipped_pedicle if clip else ORIGINAL_PEDICLE
    try:
        placed = P.straight(levels, vert, tilt=tilt)
        lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
    finally:
        P.pedicle_inside = ORIGINAL_PEDICLE
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in levels})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    v = A.build(level, vox[level], grid, axes[level], V.touching_edge(vox[level], lab.shape),
                M.neighbours_of(vox, order, level))
    return v, placed


def truth_deg(v, placed, lean):
    R = [pl for pl in placed if pl.level == v.level][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    return math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))


def read_at(v, placed, lean, cap):
    """The wall's error in degrees with the band capped at cap mm, and the reading's record."""
    old = BODY.WALL_BAND_MAX_MM
    BODY.WALL_BAND_MAX_MM = cap
    try:
        B = v.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        v.__dict__.pop("_posterior_wall", None)
        slope, info = BODY.posterior_wall(v, B, xc)
    finally:
        BODY.WALL_BAND_MAX_MM = old
        v.__dict__.pop("_posterior_wall", None)
    err = BODY.degrees_of(slope) - truth_deg(v, placed, lean) if math.isfinite(slope) else float("nan")
    return err, info


def root_edges(v, cap=6.0, outer=5.0):
    """The edges the band holds beyond `outer` mm of the midline, split at mid-window, with their
    mean residual from the fitted surface in mm (negative: behind it), and the whole set's count."""
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    old = BODY.WALL_BAND_MAX_MM
    BODY.WALL_BAND_MAX_MM = cap
    try:
        place, why = BODY.wall_window(v, B, xc)
    finally:
        BODY.WALL_BAND_MAX_MM = old
    if place is None:
        return None
    half, reach, lo, hi = place
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    e = bone + 0.5 * d
    X = BODY.wall_design(e, xc)
    coef = BODY.biweight(X, e[:, 1], BODY.trimmed_start(X, e[:, 1], e[:, 2]), BODY.WALL_BIWEIGHT_STEPS * abs(d[1]))
    r = e[:, 1] - X @ coef
    zm = 0.5 * (lo + hi)
    out = np.abs(e[:, 0] - xc) > outer
    up, down = out & (e[:, 2] > zm), out & (e[:, 2] <= zm)
    inner = ~out
    return dict(n=len(e), n_up=int(up.sum()), n_down=int(down.sum()),
                r_up=float(r[up].mean()) if up.any() else float("nan"),
                r_down=float(r[down].mean()) if down.any() else float("nan"),
                r_inner=float(r[inner].mean()), y_out_up=float(e[up, 1].mean()) if up.any() else float("nan"),
                y_out_down=float(e[down, 1].mean()) if down.any() else float("nan"))
