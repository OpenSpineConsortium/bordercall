"""Candidate A: the body's posterior wall read on the scan's own lattice.

The wall is read from the vertebra's label, not from the body as the canal's line cut it, and
not on bins of the frame's z. The scan's lines along the axis that runs most nearly front to
back each cross the wall once; on each, the wall lies between the last centre of solid bone and
the first centre of air behind it, and the midpoint of the two, at its own place in the frame,
is that line's edge. One edge per line, so no layer is missed or caught twice. A surface
y = a + b z + c x + d x^2 is fitted to the edges by least squares, x measured from the midline,
and b is the wall's dy/dz: the x terms take the frame's roll and the wall's curve across the
midline, so that a band wider than 3 mm can be read. The body as cut (B) gives only the wall's
height at the midline, from which the window is taken.

The least-squares surface follows the lattice's staircase where the window holds few of its
steps. The edges also bound the slope: every surface of the family that keeps each edge's bone
centre in front of it and its air centre behind it has a slope in a range (freedom, two linear
programs as pedicle.slope_range's), which holds the truth wherever the family fits the wall.
Where the least-squares slope lies outside that range it is brought to the range's nearer end;
where no surface of the family parts the centres, as a segmenter's ragged edge may leave it, the
least-squares slope stands. The range is returned in the info (free_lo_deg, free_hi_deg) so a
caller can refuse an angle the lattice leaves free; this reader refuses none on that ground.

Bounds, each from the geometry and none from the phantoms' truths:
- the band's half-width is a quarter of the canal's width at its full rings, at most 6 mm:
  behind the wall there is then canal and not a pedicle's root, so every line's air is the
  canal's, and the inner half of the canal is where the wall runs nearly flat across;
- the middle 60 per cent of the wall's height, as body.posterior_wall_slope reads it, clear of
  the end-plates' rims;
- an edge counts only within a quarter of the canal's median depth of the canal's line, in front
  of it or behind (the line errs by up to 7.7 degrees on these phantoms, about 1.1 mm at the ends
  of a 16 mm window, and a quarter of a lumbar canal's depth is near 4 mm), so the lamina, the
  spinous process and a line that leaves the body through an end-plate give no edge; and only at
  the back of a solid run of at least RUN_MM of bone along its line, so a speck of bone in the
  canal gives none;
- after the first fit an edge more than one lattice step (along y) off the surface is dropped
  and the surface fitted again: a plane wall's edges stand at most half a step off it, so
  anything further is not the wall.
It refuses (NAN) where no full ring gives the canal, where fewer than G.MIN_CHORD_POINTS edges
remain, or where the edges span less than half the window's height.
"""
import math

import numpy as np
from scipy.optimize import linprog

from morphometry import anatomy as A
from scanimport import geometry as G

NAN = float("nan")
HEIGHT_SHARE = 0.6
HALF_BAND_MAX_MM = 6.0
CANAL_SHARE = 0.25
RUN_MM = 3.0
GATE_SHARE = 0.25


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


def edges(v, xc, half, lo, hi, reach):
    """One edge per scan line across the band: the last centre of a solid run of bone and the
    first centre of air behind it, both in frame coordinates, and the run of one step along y."""
    w, step, d = walking_axis(v)
    loc = v.loc
    near = ((np.abs(A.square_to_wall(v, loc)[:, 1] - v.wall_y0) <= reach) & (np.abs(loc[:, 0] - xc) <= half + v.pixel)
            & (loc[:, 2] >= lo - v.fz) & (loc[:, 2] <= hi + v.fz))
    P, q = v.idx[near], loc[near]
    back = ~v.is_bone(P + step)
    run = np.ones(len(P), bool)
    for m in range(1, int(math.ceil(RUN_MM / v.grid.spacing[w])) + 1):
        run &= v.is_bone(P - m * step)
    bone, key = q[back & run], np.delete(P[back & run], w, axis=1)
    e = bone + 0.5 * d
    inside = (np.abs(e[:, 0] - xc) <= half) & (e[:, 2] >= lo) & (e[:, 2] <= hi)
    bone, key = bone[inside], key[inside]
    order = np.lexsort((bone[:, 1], key[:, 1], key[:, 0]))      # per line, the most posterior first
    bone, key = bone[order], key[order]
    first = np.ones(len(bone), bool)
    first[1:] = (key[1:] != key[:-1]).any(1)
    return bone[first], bone[first] + d, abs(d[1])


def design(p, xc):
    x = p[:, 0] - xc
    return np.column_stack([np.ones(len(p)), p[:, 2], x, x * x])


def fit(e, xc):
    X = design(e, xc)
    coef = np.linalg.lstsq(X, e[:, 1], rcond=None)[0]
    return coef, e[:, 1] - X @ coef


def freedom(bone, air, xc):
    """The least and greatest dy/dz of a surface of the fitted family that keeps every edge's
    bone centre in front of it and its air centre behind it, two linear programs over the same
    constraints as pedicle.slope_range's; an end the lattice does not bound is infinite, and
    both are nan where no surface of the family parts the centres."""
    F = design(np.vstack([bone, air]), xc)
    sign = np.concatenate([np.ones(len(bone)), -np.ones(len(air))])
    y = np.concatenate([bone[:, 1], air[:, 1]])
    ends = []
    for c, unbounded in (([0.0, 1.0, 0.0, 0.0], -math.inf), ([0.0, -1.0, 0.0, 0.0], math.inf)):
        res = linprog(c=c, A_ub=sign[:, None] * F, b_ub=sign * y, bounds=[(None, None)] * 4, method="highs")
        if res.status == 2:
            return NAN, NAN
        ends.append(float(res.x[1]) if res.success else unbounded)
    return ends[0], ends[1]


def read(v, B, xc, clamp):
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
    bone, air, ystep = edges(v, xc, half, lo, hi, GATE_SHARE * ap)
    e = 0.5 * (bone + air)
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
    b = float(coef[1])
    b_lo, b_hi = freedom(bone[good], air[good], xc)
    if clamp and not math.isnan(b_lo):
        b = min(max(b, b_lo), b_hi)
    deg = lambda t: math.degrees(math.atan(t))
    info = {"edges": int(good.sum()), "dropped": int((~good).sum()), "half_band": half, "span": span,
            "rms": float(np.sqrt(np.mean(r * r))), "fitted_deg": deg(coef[1]),
            "free_lo_deg": deg(b_lo), "free_hi_deg": deg(b_hi), "free_deg": deg(b_hi) - deg(b_lo)}
    return b, info


def slope(v, B, xc):
    """dy/dz of the posterior wall: the least-squares surface through the edges, its slope
    brought inside the range the lattice leaves free where it lies outside it."""
    return read(v, B, xc, clamp=True)


def slope_plain(v, B, xc):
    """The least-squares slope alone."""
    return read(v, B, xc, clamp=False)
