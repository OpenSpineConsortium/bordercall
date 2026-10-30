"""Grafts onto candidate A, measured beside it: a robust fit in place of its one trimming round,
and the lattice's own freedom for the fitted surface (the range a clean digitisation of that
surface on the same scan lines would leave), which exists on any mask, ragged or not.

Phantoms only. Nothing here is set from the cache's truths: the biweight's scale is two lattice
steps along y (a plane wall's edge midpoints stand within half a step of it and a fit within the
lattice's range within another half; a structure two steps proud is not the wall), and the
trimmed share of the least-trimmed fit is a quarter."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "cand_lattice"))
import cand as A  # noqa: E402
from scanimport import geometry as G  # noqa: E402

NAN = float("nan")
BIWEIGHT_STEPS = 2.0
LTS_KEEP = 0.75


def biweight(e, xc, ystep, start=None, rounds=50):
    X = A.design(e, xc)
    coef = np.linalg.lstsq(X, e[:, 1], rcond=None)[0] if start is None else start
    s = BIWEIGHT_STEPS * ystep
    for _ in range(rounds):
        u = (e[:, 1] - X @ coef) / s
        w = np.where(np.abs(u) < 1.0, (1.0 - u * u) ** 2, 0.0)
        if (w > 0).sum() < 4:
            break
        sw = np.sqrt(w)
        new = np.linalg.lstsq(X * sw[:, None], e[:, 1] * sw, rcond=None)[0]
        if np.allclose(new, coef, atol=1e-9):
            coef = new
            break
        coef = new
    return coef, e[:, 1] - X @ coef


def lts(e, xc, ystep, keep=LTS_KEEP, starts=12, seed=0):
    """Least trimmed squares by concentration steps from fits over the window's quarters and
    random halves: the fit of the share keep of the edges with the least squared residuals."""
    X = A.design(e, xc)
    n = len(e)
    h = max(int(keep * n), 8)
    z = e[:, 2]
    order = np.argsort(z)
    subsets = [order[i * n // 4:(i + 2) * n // 4] for i in range(3)]
    rng = np.random.default_rng(seed)
    subsets += [order] + [rng.choice(n, size=max(n // 2, 8), replace=False) for _ in range(starts)]
    best = None
    for sub in subsets:
        coef = np.linalg.lstsq(X[sub], e[sub, 1], rcond=None)[0]
        for _ in range(30):
            r = e[:, 1] - X @ coef
            idx = np.argsort(r * r)[:h]
            new = np.linalg.lstsq(X[idx], e[idx, 1], rcond=None)[0]
            if np.allclose(new, coef, atol=1e-10):
                break
            coef = new
        r = e[:, 1] - X @ coef
        cost = np.sort(r * r)[:h].sum()
        if best is None or cost < best[0]:
            best = (cost, coef)
    coef = best[1]
    return coef, e[:, 1] - X @ coef


def synthetic_freedom(bone, d, coef, xc):
    """The range of b a clean digitisation of the fitted surface leaves on the same scan lines:
    on each line (through the edge's bone centre, step d back along it) the centres on either
    side of where the fitted surface crosses, parted by A.freedom's programs."""
    a, b, c, dd = coef
    sb, sa = [], []
    for p in bone:
        def g(t):
            q = p + t * d
            x = q[0] - xc
            return q[1] - (a + b * q[2] + c * x + dd * x * x)
        t = 0.0
        for _ in range(8):                       # g is nearly linear in t: Newton from the bone centre
            h = 1e-3
            slope = (g(t + h) - g(t - h)) / (2 * h)
            if abs(slope) < 1e-12:
                break
            t -= g(t) / slope
        k = math.floor(t)                         # centres at t <= k lie in front (bone), k + 1 behind
        sb.append(p + k * d)
        sa.append(p + (k + 1) * d)
    return A.freedom(np.array(sb), np.array(sa), xc)


def read(v, B, xc, fit="trim", clamp=True, band_max=None):
    rings = v.full_rings()
    if not rings:
        return NAN, {"why": "no full ring gives the canal"}
    width = float(np.median([s.width for s in rings]))
    ap = float(np.median([s.ap for s in rings]))
    half = min(A.HALF_BAND_MAX_MM if band_max is None else band_max, A.CANAL_SHARE * width)
    mid = B[np.abs(B[:, 0] - xc) <= half]
    if len(mid) < G.MIN_CHORD_POINTS:
        return NAN, {"why": "too few body points at the midline"}
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    margin = 0.5 * (1.0 - A.HEIGHT_SHARE) * (z1 - z0)
    lo, hi = z0 + margin, z1 - margin
    bone, air, ystep = A.edges(v, xc, half, lo, hi, A.GATE_SHARE * ap)
    e = 0.5 * (bone + air)
    if len(e) < G.MIN_CHORD_POINTS:
        return NAN, {"why": "%d edges" % len(e)}
    if fit == "trim":
        coef, r = A.fit(e, xc)
        good = np.abs(r) <= ystep
        if good.sum() < G.MIN_CHORD_POINTS:
            return NAN, {"why": "%d edges near the surface" % good.sum()}
        coef, r = A.fit(e[good], xc)
        r = e[:, 1] - A.design(e, xc) @ coef
    elif fit == "biweight":
        coef, r = biweight(e, xc, ystep)
    elif fit == "lts_biweight":
        c0, _ = lts(e, xc, ystep)
        coef, r = biweight(e, xc, ystep, start=c0)
    else:
        raise KeyError(fit)
    good = np.abs(r) <= ystep
    if good.sum() < G.MIN_CHORD_POINTS:
        return NAN, {"why": "%d edges near the surface" % good.sum()}
    span = float(np.ptp(e[good, 2]))
    if span < 0.5 * (hi - lo):
        return NAN, {"why": "the edges span %.1f mm of %.1f" % (span, hi - lo)}
    b = float(coef[1])
    b_lo, b_hi = A.freedom(bone[good], air[good], xc)
    parted = not math.isnan(b_lo)
    if clamp and parted:
        b = min(max(b, b_lo), b_hi)
    _, _, d = A.walking_axis(v)
    s_lo, s_hi = synthetic_freedom(bone[good], d, coef, xc)
    deg = lambda t: math.degrees(math.atan(t))
    info = {"edges": int(good.sum()), "dropped": int((~good).sum()), "half_band": half, "span": span,
            "parted": float(parted), "fitted_deg": deg(coef[1]),
            "rms_over_step": float(np.sqrt(np.mean(r[good] ** 2)) / ystep),
            "free_deg": (deg(b_hi) - deg(b_lo)) if parted else NAN,
            "synth_free_deg": (deg(s_hi) - deg(s_lo)) if not math.isnan(s_lo) else NAN,
            "synth_lo_deg": deg(s_lo), "synth_hi_deg": deg(s_hi)}
    return b, info


def A_trim(v, B, xc):
    return read(v, B, xc, fit="trim")


def A_bw(v, B, xc):
    return read(v, B, xc, fit="biweight")


def A_lts(v, B, xc):
    return read(v, B, xc, fit="lts_biweight")


def A_lts_plain(v, B, xc):
    return read(v, B, xc, fit="lts_biweight", clamp=False)


def read_det(v, B, xc, clamp=True):
    """A_lts with deterministic starts only: the window's lower, middle and upper halves and the
    whole set, no random subsets."""
    saved = lts.__defaults__
    lts.__defaults__ = (LTS_KEEP, 0, 0)
    try:
        return read(v, B, xc, fit="lts_biweight", clamp=clamp)
    finally:
        lts.__defaults__ = saved


def A_lts_det(v, B, xc):
    return read_det(v, B, xc)
