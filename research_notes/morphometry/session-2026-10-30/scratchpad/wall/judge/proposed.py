"""The reader proposed to replace body.posterior_wall_slope, self-contained: candidate A's edges
on the scan's own lattice, a least-trimmed-squares start polished by a biweight in place of A's
one trimming round, A's clamp to the range of slopes the label leaves free where it parts, and the
lattice's own range for the fitted surface where it does not, so a freedom is reported on every
mask. Refuses (NAN and why) where no full ring gives the canal, where fewer than
G.MIN_CHORD_POINTS edges stand near the surface, where they span less than half the window, or
where the lattice leaves the slope free over more than FREEDOM_DEG.

Bounds, each from the geometry: the band's half-width a quarter of the canal's width at its full
rings, at most 6 mm (canal behind the wall, not a pedicle's root); the middle 60 per cent of the
midline body's height; edges within a quarter of the canal's median depth of the canal's line
(about 4 mm: past the line's own error, short of the lamina and of a basivertebral channel's
floor); an edge only at the back of 3 mm of solid bone (no speck in the canal); a quarter of the
edges trimmed at most (a notch, a hole's rim or a lip that holds more is not told from the wall);
the biweight's scale two lattice steps along y (a clean digitisation's edges stand within half a
step of the wall, so a point two steps off is not the wall); an edge more than one step off the
final surface is left out of the programs; FREEDOM_DEG pedicle's own.
"""
import math

import numpy as np
from scipy.optimize import linprog

from morphometry import anatomy as A
from scanimport import geometry as G

NAN = float("nan")
HEIGHT_SHARE = 0.6
BAND_MAX_MM = 6.0
BAND_CANAL_SHARE = 0.25
GATE_CANAL_SHARE = 0.25
RUN_MM = 3.0
TRIM_KEEP = 0.75
BIWEIGHT_STEPS = 2.0
PART_MM = 1e-6
FREEDOM_DEG = 9.0          # pedicle.FREEDOM_DEG
FREE_FLAG_DEG = 3.0        # the caller flags a wall whose freedom's half-width passes 1.5 degrees


def walking_axis(v):
    axes, spacing, f = v.grid.axes, v.grid.spacing, v.frame
    w = int(np.argmax(np.abs(axes.T @ f.ey)))
    sign = -1 if axes[:, w] @ f.ey > 0 else 1
    step = np.zeros(3, int)
    step[w] = sign
    d = sign * spacing[w] * axes[:, w]
    return w, step, np.array([d @ f.ex, d @ f.ey, d @ f.ez])


def wall_edges(v, xc, half, lo, hi, reach):
    """Per scan line along the axis nearest y, the last centre of a solid run of bone and the
    step back to the first centre of air: (bone centres, step in the frame)."""
    w, step, d = walking_axis(v)
    loc = v.loc
    near = ((np.abs(A.square_to_wall(v, loc)[:, 1] - v.wall_y0) <= reach) & (np.abs(loc[:, 0] - xc) <= half + v.pixel)
            & (loc[:, 2] >= lo - v.fz) & (loc[:, 2] <= hi + v.fz))
    P, q = v.idx[near], loc[near]
    keep = ~v.is_bone(P + step)
    for m in range(1, int(math.ceil(RUN_MM / v.grid.spacing[w])) + 1):
        keep &= v.is_bone(P - m * step)
    bone, line = q[keep], np.delete(P[keep], w, axis=1)
    e = bone + 0.5 * d
    inside = (np.abs(e[:, 0] - xc) <= half) & (e[:, 2] >= lo) & (e[:, 2] <= hi)
    bone, line = bone[inside], line[inside]
    order = np.lexsort((bone[:, 1], line[:, 1], line[:, 0]))
    bone, line = bone[order], line[order]
    first = np.ones(len(bone), bool)
    first[1:] = (line[1:] != line[:-1]).any(1)
    return bone[first], d


def design(p, xc):
    x = p[:, 0] - xc
    return np.column_stack([np.ones(len(p)), p[:, 2], x, x * x])


def trimmed_start(X, y, z):
    """Least trimmed squares (the TRIM_KEEP share with the least squared residuals) by
    concentration steps from the whole set and the window's lower, middle and upper halves."""
    n = len(y)
    h = max(int(TRIM_KEEP * n), 8)
    order = np.argsort(z)
    best = None
    for sub in [order] + [order[i * n // 4:(i + 2) * n // 4] for i in range(3)]:
        coef = np.linalg.lstsq(X[sub], y[sub], rcond=None)[0]
        for _ in range(30):
            idx = np.argsort((y - X @ coef) ** 2)[:h]
            new = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
            done = np.allclose(new, coef, atol=1e-10)
            coef = new
            if done:
                break
        cost = np.sort((y - X @ coef) ** 2)[:h].sum()
        if best is None or cost < best[0]:
            best = (cost, coef)
    return best[1]


def biweight(X, y, coef, scale, rounds=50):
    for _ in range(rounds):
        u = (y - X @ coef) / scale
        w = np.where(np.abs(u) < 1.0, (1.0 - u * u) ** 2, 0.0)
        if (w > 0).sum() < X.shape[1]:
            break
        sw = np.sqrt(w)
        new = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        done = np.allclose(new, coef, atol=1e-9)
        coef = new
        if done:
            break
    return coef


def slope_range(bone, air, xc):
    """The least and greatest b of a surface of the family keeping every bone centre in front of
    it and every air centre behind, by more than PART_MM; NAN, NAN where none parts them."""
    F = design(np.vstack([bone, air]), xc)
    sign = np.concatenate([np.ones(len(bone)), -np.ones(len(air))])
    y = np.concatenate([bone[:, 1], air[:, 1]])
    ends = []
    for c, unbounded in (([0.0, 1.0, 0.0, 0.0], -math.inf), ([0.0, -1.0, 0.0, 0.0], math.inf)):
        res = linprog(c=c, A_ub=sign[:, None] * F, b_ub=sign * y - PART_MM, bounds=[(None, None)] * 4, method="highs")
        if res.status == 2:
            return NAN, NAN
        ends.append(float(res.x[1]) if res.success else unbounded)
    return ends[0], ends[1]


def clean_digitisation(bone, d, coef, xc):
    """The centres either side of where the fitted surface crosses each edge's scan line: the
    label a clean digitisation of that surface would give on the same lines."""
    a, b, c, dd = coef
    x = bone[:, 0] - xc
    t = np.zeros(len(bone))
    for _ in range(6):
        px, pz = x + t * d[0], bone[:, 2] + t * d[2]
        g = bone[:, 1] + t * d[1] - (a + b * pz + c * px + dd * px * px)
        dg = d[1] - (b * d[2] + c * d[0] + 2.0 * dd * px * d[0])
        t = t - g / dg
    k = np.floor(t)[:, None]
    return bone + k * d, bone + (k + 1.0) * d


def posterior_wall(v, B, xc):
    """dy/dz of the body's posterior wall at the midline and a record of the reading, or NAN and
    why."""
    deg = lambda t: math.degrees(math.atan(t))
    rings = v.full_rings()
    if not rings:
        return NAN, {"why": "no full ring of the canal gives the wall's place"}
    half = min(BAND_MAX_MM, BAND_CANAL_SHARE * float(np.median([s.width for s in rings])))
    reach = GATE_CANAL_SHARE * float(np.median([s.ap for s in rings]))
    mid = B[np.abs(B[:, 0] - xc) <= half]
    if len(mid) < G.MIN_CHORD_POINTS:
        return NAN, {"why": "too few body points at the midline"}
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    trim = 0.5 * (1.0 - HEIGHT_SHARE) * (z1 - z0)
    lo, hi = z0 + trim, z1 - trim
    bone, d = wall_edges(v, xc, half, lo, hi, reach)
    ystep = abs(d[1])
    e = bone + 0.5 * d
    if len(e) < G.MIN_CHORD_POINTS:
        return NAN, {"why": "%d edges of the wall in the band" % len(e)}
    X = design(e, xc)
    coef = biweight(X, e[:, 1], trimmed_start(X, e[:, 1], e[:, 2]), BIWEIGHT_STEPS * ystep)
    r = e[:, 1] - X @ coef
    good = np.abs(r) <= ystep
    if good.sum() < G.MIN_CHORD_POINTS:
        return NAN, {"why": "%d edges near the wall's surface" % good.sum()}
    span = float(np.ptp(e[good, 2]))
    if span < 0.5 * (hi - lo):
        return NAN, {"why": "the wall's edges span %.1f mm of a %.1f mm window" % (span, hi - lo)}
    b = float(coef[1])
    b_lo, b_hi = slope_range(bone[good], bone[good] + d, xc)
    parted = not math.isnan(b_lo)
    if parted:
        b = min(max(b, b_lo), b_hi)
    else:
        b_lo, b_hi = slope_range(*clean_digitisation(bone[good], d, coef, xc), xc)
    free = deg(b_hi) - deg(b_lo) if not math.isnan(b_lo) else math.inf
    info = {"edges": int(good.sum()), "dropped": int((~good).sum()), "half_band_mm": half, "span_mm": span,
            "parted": parted, "fitted_deg": deg(coef[1]), "free_lo_deg": deg(b_lo), "free_hi_deg": deg(b_hi),
            "free_deg": free, "rms_over_step": float(np.sqrt(np.mean(r[good] ** 2)) / ystep)}
    if not free <= FREEDOM_DEG:
        return NAN, dict(info, why="the lattice leaves the wall's slope free over %.1f degrees, more than %.0f"
                         % (free, FREEDOM_DEG))
    return b, info


def posterior_wall_slope(v, B, xc):
    return posterior_wall(v, B, xc)[0]
