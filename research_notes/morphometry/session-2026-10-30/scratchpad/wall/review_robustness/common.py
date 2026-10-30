"""Shared helpers for the robustness probes of body.posterior_wall: build one phantom level as
measure_volume builds it, and read the wall's error against the phantom's truth."""
import math
import time

import numpy as np

from morphometry import anatomy as A, body as BODY, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS


def draw_and_build(levels, level, vert, spacing=(0.8, 0.8, 1.0), tilt=((1.0, 0.0, 0.0), 2.0),
                   grid_turn=((0.0, 0.0, 1.0), 0.0), edit=None):
    placed = P.straight(levels, vert, tilt=tilt)
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=grid_turn, strict=False)
    if edit is not None:
        lab = edit(lab, aff, placed)
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in levels})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    v = A.build(level, vox[level], grid, axes[level], V.touching_edge(vox[level], lab.shape),
                M.neighbours_of(vox, order, level))
    return v, placed, lab, aff


def wall_truth_deg(v, placed, lean):
    R = [pl for pl in placed if pl.level == v.level][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    return math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))


def read(v, placed, lean):
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    v.__dict__.pop("_posterior_wall", None)
    t0 = time.perf_counter()
    slope, info = BODY.posterior_wall(v, B, xc)
    dt = time.perf_counter() - t0
    truth = wall_truth_deg(v, placed, lean)
    err = BODY.degrees_of(slope) - truth if math.isfinite(slope) else float("nan")
    return err, info, dt, truth


def show(tag, v, placed, lean):
    if "all" in v.flags:
        print("%-40s NOT BUILT: %s" % (tag, v.flags["all"]))
        return None
    err, info, dt, truth = read(v, placed, lean)
    keep = {k: (round(x, 2) if isinstance(x, float) else x) for k, x in info.items()}
    print("%-40s err %+.2f truth %+.2f  %.3fs  %s" % (tag, err, truth, dt, keep), flush=True)
    return err, info
