"""Candidate C: the posterior wall's dy/dz from the midpoints of the lattice pairs that cross it.

Every scan line along the lattice axis nearest the frame's y that runs through the midline band
and the middle 60 per cent of the body's height enters the vertebra's bone from the canal once at
the wall. The wall crosses the segment between that line's last air centre and first bone centre,
so the segment's midpoint lies within half a step of the wall whatever the lattice's phase there.
A least-squares plane through those midpoints, y = a + b z + c x + d x^2, gives the slope b.
The midpoints average the staircase only where the pairs take many phases, across columns or over
several row steps along z; where the wall runs within a degree or two of one family of lattice
planes over the whole window, every midpoint has nearly the same phase and the plane follows the
lattice, so info carries the range of slopes the pairs leave free (straddle_range); C reads such
a wall and does not refuse it.

The pairs are read on the vertebra's own label (v.is_bone over the scan's lattice), not on B,
since B is cut at the canal's wall line, which leans off the wall and cuts its posterior row away
at one end of the body. B gives only the band's centre and the body's height, as the reader in
body.posterior_wall_slope takes them.
"""
import math
import time

import numpy as np

NAN = float("nan")
ACROSS_HALF_MM = 3.0       # body.ACROSS_HALF_MM: the midline band
MIDDLE = (0.2, 0.8)        # the middle 60 per cent of the body's height, as the current reader
MIN_PAIRS = 12             # G.MIN_CHORD_POINTS is 12: fewer midpoints read no plane
MIN_LAYERS = 3             # the current reader's least number of rows
TRIM_ROUNDS = 3
TRIM_SHARE = 0.2           # at most a fifth of the points dropped in one round
X_TERMS = 2                # the plane carries c x and d x^2: the frame's roll and the wall's curve across


def nearest_step(v):
    """The index step along the lattice axis nearest the frame's y, pointing back (toward the
    canal), and that step in the frame."""
    A = np.asarray(v.grid.affine, float)[:3, :3]
    in_frame = np.stack([v.frame.ex, v.frame.ey, v.frame.ez]) @ A
    axis = int(np.argmax(np.abs(in_frame[1]) / np.linalg.norm(in_frame, axis=0)))
    step = np.zeros(3, int)
    step[axis] = -1 if in_frame[1, axis] > 0 else 1
    return step, axis, in_frame @ step


def canal_half_depth(v):
    """Half the canal's depth at the midline, the median over its full rings: a pair further than
    this from the canal's wall line lies on the arch's side of the canal, not on the body's wall."""
    rings = v.full_rings()
    return 0.5 * float(np.median([s.ap for s in rings])) if rings else NAN


def wall_pairs(v, xc, z_lo, z_hi):
    """Midpoints (x, y, z) of the bone-to-canal pairs along the nearest lattice axis, one per scan
    line, the most posterior entry into bone on it; and the step in the frame."""
    step, axis, step_f = nearest_step(v)
    half = canal_half_depth(v)
    q = v.loc
    off_line = q[:, 1] - (v.wall_y0 + v.wall_slope * (q[:, 2] - v.wall_z0))
    mid = q + 0.5 * step_f
    near = ((np.abs(mid[:, 0] - xc) <= ACROSS_HALF_MM) & (mid[:, 2] >= z_lo) & (mid[:, 2] <= z_hi)
            & (np.abs(off_line) <= half))
    idx = v.idx[near]
    entry = ~v.is_bone(idx + step)
    idx, mid = idx[entry], mid[near][entry]
    line = np.delete(idx, axis, axis=1)
    order = np.lexsort((mid[:, 1], line[:, 1], line[:, 0]))
    line, mid = line[order], mid[order]
    first = np.ones(len(line), bool)
    first[1:] = (line[1:] != line[:-1]).any(1)
    return mid[first], step_f


def plane_fit(m, xc, keep):
    x = m[:, 0] - xc
    X = np.column_stack([np.ones(len(m)), m[:, 2]] + [x ** p for p in range(1, X_TERMS + 1)])
    coef = np.linalg.lstsq(X[keep], m[keep, 1], rcond=None)[0]
    return coef, m[:, 1] - X @ coef


def trimmed_fit(m, xc, step_f):
    """Least squares, then up to TRIM_ROUNDS rounds dropping the midpoints more than one whole
    step off the plane (at most TRIM_SHARE of those kept each round). A midpoint of a pair that
    straddles a plane wall lies within half a step of it, and a fit within the feasible range
    lies within another half step of the wall over the window, so a point further off is not a
    crossing of this wall: a notch, a stray voxel, a hole's edge."""
    keep = np.ones(len(m), bool)
    coef, res = plane_fit(m, xc, keep)
    for _ in range(TRIM_ROUNDS):
        bound = abs(step_f[1] - coef[1] * step_f[2])
        far = keep & (np.abs(res) > bound)
        if not far.any():
            break
        cap = int(TRIM_SHARE * keep.sum())
        worst = np.argsort(-np.abs(np.where(far, res, 0.0)))[:max(cap, 1)]
        keep[worst[far[worst]]] = False
        coef, res = plane_fit(m, xc, keep)
    return coef, res, keep


def straddle_range(m, step_f, coef, xc, keep):
    """The least and greatest slope b of a line y = a + b z, beside the fitted x terms, that keeps
    every kept pair's bone end in front of it and its canal end behind it: how far the pairs leave
    the slope free. NAN, NAN where no such line exists. Where the wall runs along one family of
    lattice planes over the whole window, every pair has the same phase and the range is wide."""
    x = m[keep, 0] - xc
    curve = sum(coef[1 + p] * x ** p for p in range(1, X_TERMS + 1))
    bone, canal = m[keep] - 0.5 * step_f, m[keep] + 0.5 * step_f
    rise = bone[:, 2][None, :] - canal[:, 2][:, None]          # rows: canal end, columns: bone end
    room = (bone[:, 1] - curve)[None, :] - (canal[:, 1] - curve)[:, None]
    up, down, level = rise > 1e-9, rise < -1e-9, np.abs(rise) <= 1e-9
    hi = np.min(room[up] / rise[up]) if up.any() else math.inf
    lo = np.max(room[down] / rise[down]) if down.any() else -math.inf
    if lo > hi or (room[level] < 0).any():
        return NAN, NAN
    return lo, hi


def slope(v, B, xc):
    t0 = time.perf_counter()
    info = {}
    band = B[np.abs(B[:, 0] - xc) <= ACROSS_HALF_MM]
    if len(band) < MIN_PAIRS or not v.full_rings():
        return NAN, {"why": "no midline body or no canal ring"}
    z0, z1 = band[:, 2].min(), band[:, 2].max()
    z_lo, z_hi = z0 + MIDDLE[0] * (z1 - z0), z0 + MIDDLE[1] * (z1 - z0)
    m, step_f = wall_pairs(v, xc, z_lo, z_hi)
    layers = len(np.unique(np.round(m[:, 2] / max(v.fz, 0.5)))) if len(m) else 0
    info.update(pairs=len(m), layers=layers, step_off_y_deg=math.degrees(math.acos(abs(step_f[1]) / np.linalg.norm(step_f))))
    if len(m) < MIN_PAIRS or layers < MIN_LAYERS:
        info["why"] = "too few wall pairs"
        return NAN, info
    coef, res, keep = trimmed_fit(m, xc, step_f)
    lo, hi = straddle_range(m, step_f, coef, xc, keep)
    info.update(trimmed=int((~keep).sum()), rms_over_step=float(np.sqrt(np.mean(res[keep] ** 2)) / abs(step_f[1])),
                range_lo_deg=math.degrees(math.atan(lo)), range_hi_deg=math.degrees(math.atan(hi)),
                range_deg=math.degrees(math.atan(hi) - math.atan(lo)), seconds=time.perf_counter() - t0)
    return float(coef[1]), info
