"""A variant of candidate C, measured beside it: the midpoints of every bone-to-canal pair along all
three lattice axes, not only the axis nearest y, fitted by least squares weighted by how tightly
each pair pins the wall. A pair straddles the wall, so the wall's y at its midpoint lies within
half the pair's own extent across the wall, h = |d_y - b d_z - c d_x| / 2 for the step d in the
frame; the weight is 1 / h^2. The pairs along the axis nearest y (the treads of the staircase)
pin the wall to half a row; the pairs along the axes nearest z and x cross the wall only where it
steps from one row to the next (the risers), and pin it there to a fraction of that, which is the
information below one voxel that the treads alone lack.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cand as C  # noqa: E402

NAN = float("nan")
H_FLOOR_MM = 0.05          # a pair is never trusted to pin the wall closer than this
FIT_ROUNDS = 4


def crack_pairs(v, xc, z_lo, z_hi):
    """Midpoints and frame steps of the bone-to-canal pairs along every lattice axis near the wall."""
    tread, axis, tread_f = C.nearest_step(v)
    A = np.asarray(v.grid.affine, float)[:3, :3]
    in_frame = np.stack([v.frame.ex, v.frame.ey, v.frame.ez]) @ A
    half = C.canal_half_depth(v)
    q = v.loc
    off_line = q[:, 1] - (v.wall_y0 + v.wall_slope * (q[:, 2] - v.wall_z0))
    near_wall = np.abs(off_line) <= half
    steps = [tread] + [s * np.eye(3, dtype=int)[a] for a in range(3) if a != axis for s in (1, -1)]
    mids, ds = [], []
    for step in steps:
        d = in_frame @ step
        mid = q + 0.5 * d
        near = (near_wall & (np.abs(mid[:, 0] - xc) <= C.ACROSS_HALF_MM) & (mid[:, 2] >= z_lo)
                & (mid[:, 2] <= z_hi))
        entry = ~v.is_bone(v.idx[near] + step)
        mids.append(mid[near][entry])
        ds.append(np.repeat(d[None, :], entry.sum(), axis=0))
    return np.concatenate(mids), np.concatenate(ds)


def weighted_fit(m, d, xc):
    x = m[:, 0] - xc
    X = np.column_stack([np.ones(len(m)), m[:, 2], x, x ** 2])
    coef = np.zeros(4)
    for _ in range(FIT_ROUNDS):
        h = np.maximum(0.5 * np.abs(d[:, 1] - coef[1] * d[:, 2] - (coef[2] + 2 * coef[3] * x) * d[:, 0]), H_FLOOR_MM)
        w = 1.0 / h
        coef = np.linalg.lstsq(X * w[:, None], m[:, 1] * w, rcond=None)[0]
    return coef, h


def slope(v, B, xc):
    t0 = time.perf_counter()
    band = B[np.abs(B[:, 0] - xc) <= C.ACROSS_HALF_MM]
    if len(band) < C.MIN_PAIRS or not v.full_rings():
        return NAN, {"why": "no midline body or no canal ring"}
    z0, z1 = band[:, 2].min(), band[:, 2].max()
    z_lo, z_hi = z0 + C.MIDDLE[0] * (z1 - z0), z0 + C.MIDDLE[1] * (z1 - z0)
    m, d = crack_pairs(v, xc, z_lo, z_hi)
    if len(m) < C.MIN_PAIRS:
        return NAN, {"why": "too few wall pairs"}
    coef, h = weighted_fit(m, d, xc)
    return float(coef[1]), {"pairs": len(m), "tight": int((h < 0.2).sum()), "seconds": time.perf_counter() - t0}
