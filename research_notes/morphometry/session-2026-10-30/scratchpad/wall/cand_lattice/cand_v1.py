"""Candidate A: the body's posterior wall read on the scan's own lattice.

The wall is read from the vertebra's label, not from the body as the canal's line cut it, and
not on bins of the frame's z. The scan's lines along the axis that runs most nearly front to
back each cross the wall once; on each, the wall lies between the last centre of solid bone and
the first centre of air behind it, and the midpoint of the two, at its own place in the frame,
is that line's edge. One edge per line, so no layer is missed or caught twice. A surface
y = a + b z + c x + d x^2 is fitted to the edges by least squares, x measured from the midline,
and b is the wall's dy/dz: the x terms take the frame's roll and the wall's curve across the
midline, so that a band wider than 3 mm can be read.

Bounds, each from the geometry and none from the phantoms' truths:
- the band's half-width is a quarter of the canal's width at its full rings, at most 6 mm:
  behind the wall there is then canal and not a pedicle's root, so every line's air is the
  canal's, and the inner half of the canal is where the wall runs nearly flat across;
- the middle 60 per cent of the wall's height, as body.posterior_wall_slope reads it, clear of
  the end-plates' rims;
- an edge counts only in front of the canal's middle (the canal's line, less half the canal's
  median depth, as column.wall_corner takes the wall) and only at the back of a solid run of at
  least RUN_MM of bone along its line, so the lamina, the spinous process and a speck of bone in
  the canal give no edge;
- after the first fit an edge more than one lattice step (along y) off the surface is dropped
  and the surface fitted again: a plane wall's edges stand at most half a step off it, so
  anything further is not the wall.
It refuses (NAN) where no full ring gives the canal, where fewer than G.MIN_CHORD_POINTS edges
remain, or where the edges span less than half the window's height.
"""
import math

import numpy as np

from morphometry import anatomy as A
from scanimport import geometry as G

NAN = float("nan")
HEIGHT_SHARE = 0.6
HALF_BAND_MAX_MM = 6.0
CANAL_SHARE = 0.25
RUN_MM = 3.0


def walking_axis(v):
    """The scan axis that runs most nearly along the frame's y, the index step along it that
    moves posteriorly, and that step's displacement in the frame."""
    axes, spacing = v.grid.axes, v.grid.spacing
    f = v.frame
    w = int(np.argmax(np.abs(axes.T @ f.ey)))
    sign = -1 if axes[:, w] @ f.ey > 0 else 1
    step = np.zeros(3, int)
    step[w] = sign
    d = sign * spacing[w] * axes[:, w]
    return w, step, np.array([d @ f.ex, d @ f.ey, d @ f.ez])


def edges(v, xc, half, lo, hi, gate):
    """One edge per scan line across the band: the midpoint between the last centre of a solid
    run of bone and the first centre of air behind it, in frame coordinates, with each line's key."""
    w, step, d = walking_axis(v)
    loc = v.loc
    near = ((A.square_to_wall(v, loc)[:, 1] > gate) & (np.abs(loc[:, 0] - xc) <= half + v.pixel)
            & (loc[:, 2] >= lo - v.fz) & (loc[:, 2] <= hi + v.fz))
    P, q = v.idx[near], loc[near]
    back = ~v.is_bone(P + step)
    run = np.ones(len(P), bool)
    for m in range(1, int(math.ceil(RUN_MM / v.grid.spacing[w])) + 1):
        run &= v.is_bone(P - m * step)
    keep = back & run
    e = q[keep] + 0.5 * d
    key = np.delete(P[keep], w, axis=1)
    inside = (np.abs(e[:, 0] - xc) <= half) & (e[:, 2] >= lo) & (e[:, 2] <= hi)
    e, key = e[inside], key[inside]
    order = np.lexsort((e[:, 1], key[:, 1], key[:, 0]))      # per line, the most posterior first
    e, key = e[order], key[order]
    first = np.ones(len(e), bool)
    first[1:] = (key[1:] != key[:-1]).any(1)
    return e[first], abs(d[1])


def fit(e, xc):
    x = e[:, 0] - xc
    X = np.column_stack([np.ones(len(e)), e[:, 2], x, x * x])
    coef = np.linalg.lstsq(X, e[:, 1], rcond=None)[0]
    return coef, e[:, 1] - X @ coef


def slope(v, B, xc):
    rings = v.full_rings()
    if not rings:
        return NAN, {"why": "no full ring gives the canal"}
    width = float(np.median([s.width for s in rings]))
    ap = float(np.median([s.ap for s in rings]))
    half = min(HALF_BAND_MAX_MM, CANAL_SHARE * width)
    mid = B[np.abs(B[:, 0] - xc) <= half]
    if len(mid) < G.MIN_CHORD_POINTS:
        return NAN, {"why": "too few body points at the midline"}
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    margin = 0.5 * (1.0 - HEIGHT_SHARE) * (z1 - z0)
    lo, hi = z0 + margin, z1 - margin
    e, ystep = edges(v, xc, half, lo, hi, v.wall_y0 - 0.5 * ap)
    if len(e) < G.MIN_CHORD_POINTS:
        return NAN, {"why": "%d edges" % len(e)}
    coef, r = fit(e, xc)
    good = np.abs(r) <= ystep
    if good.sum() < G.MIN_CHORD_POINTS:
        return NAN, {"why": "%d edges near the surface" % good.sum()}
    coef, r = fit(e[good], xc)
    span = float(np.ptp(e[good, 2]))
    if span < 0.5 * (hi - lo):
        return NAN, {"why": "the edges span %.1f mm of %.1f" % (span, hi - lo)}
    info = {"edges": int(good.sum()), "dropped": int((~good).sum()), "half_band": half, "span": span,
            "ystep": ystep, "rms": float(np.sqrt(np.mean(r * r))), "roll": float(coef[2]), "curve": float(coef[3])}
    return float(coef[1]), info

