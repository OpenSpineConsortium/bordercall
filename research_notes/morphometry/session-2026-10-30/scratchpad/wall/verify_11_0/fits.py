"""Whether BasivertebralNotch tells the robust wall fit from plain least squares: the suite's
notch (5 wide, 6 tall, 4 deep) drawn with its centre SHIFT mm from mid-height, its wall and both
end-plate inclinations read with the fit as it stands and with three replacements, and where the
notch floor's edges fall against the window.

    fits.py SHIFT [SHIFT ...]"""
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T

ORIG_INSIDE = P.body_inside
ORIG_START, ORIG_BIWEIGHT = BODY.trimmed_start, BODY.biweight


def plain_start(X, y, z):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def no_biweight(X, y, coef, scale):
    return coef


VARIANTS = {
    "as it stands": (ORIG_START, ORIG_BIWEIGHT),
    "plain fit": (plain_start, no_biweight),
    "plain start, biweight": (plain_start, ORIG_BIWEIGHT),
    "trimmed start alone": (ORIG_START, no_biweight),
}


def shifted(dz):
    """body_inside with the notch's centre moved dz mm up; the phantom's own notch is turned off
    and the shifted one cut instead."""
    def inside(q, v):
        plain = P.replace(v, notch_w=0.0, notch_h=0.0, notch_d=0.0)
        x, y, z = q[:, 0], q[:, 1], q[:, 2] - dz
        hole = (np.abs(x) <= v.notch_w / 2) & (np.abs(z) <= v.notch_h / 2) & (y <= v.notch_d)
        return ORIG_INSIDE(q, plain) & ~hole
    return inside


def notch_edges(vert):
    """The window and the edges in the band, split into the wall's and the notch floor's by y."""
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    place, _ = BODY.wall_window(vert, B, xc)
    half, reach, lo, hi = place
    bone, d = BODY.wall_edges(vert, xc, half, lo, hi, reach)
    e = bone + 0.5 * d
    wall_y = np.median(e[:, 1])
    floor = e[:, 1] > wall_y + 2.0
    return xc, lo, hi, e, floor


def read_with(vert, variant):
    BODY.trimmed_start, BODY.biweight = VARIANTS[variant]
    try:
        vert.__dict__.pop("_posterior_wall", None)
        B = vert.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        slope, info = BODY.read_wall(vert, B, xc)
        vert.__dict__.pop("_posterior_wall", None)
        body, flags = BODY.measures(vert)
    finally:
        BODY.trimmed_start, BODY.biweight = ORIG_START, ORIG_BIWEIGHT
        vert.__dict__.pop("_posterior_wall", None)
    return slope, info, body, flags


def wall_truth(vert, placed):
    R = [pl for pl in placed if pl.level == vert.level][0].R
    w = R @ np.array([0.0, 0.0, 1.0])
    return math.degrees(math.atan(float(vert.frame.ey @ w) / float(vert.frame.ez @ w)))


def main():
    for dz in map(float, sys.argv[1:]):
        v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)
        P.body_inside = shifted(dz)
        try:
            placed = P.straight(T.LUMBAR, v)
            vert = T.built(placed, T.LUMBAR, "L3")
        finally:
            P.body_inside = ORIG_INSIDE
        truth = P.truth(v)
        xc, lo, hi, e, floor = notch_edges(vert)
        mid = 0.5 * (lo + hi)
        print("shift %+.1f mm: window %.2f to %.2f (centre %+.2f); %d edges, %d on the notch floor, "
              "their z from the window's centre %+.2f to %+.2f, mean %+.2f"
              % (dz, lo, hi, mid, len(e), floor.sum(), (e[floor, 2] - mid).min(), (e[floor, 2] - mid).max(),
                 (e[floor, 2] - mid).mean()))
        t = wall_truth(vert, placed)
        for variant in VARIANTS:
            slope, info, body, flags = read_with(vert, variant)
            err = BODY.degrees_of(slope) - t if math.isfinite(slope) else float("nan")
            e1 = body["endplate_incl"] - truth["endplate_incl"]
            e2 = body["endplate_lower_incl"] - truth["endplate_lower_incl"]
            wall_ok = abs(err) <= T.WALL_TOL_DEG
            incl_ok = abs(e1) <= T.TOL_DEG and abs(e2) <= T.TOL_DEG and "posterior_wall" not in flags
            print("  %-22s wall %+7.3f (%s)  incl %+6.2f %+6.2f (%s)  parted %s edges %s dropped %s %s"
                  % (variant, err, "pass" if wall_ok else "FAIL", e1, e2, "pass" if incl_ok else "FAIL",
                     info.get("parted"), info.get("edges"), info.get("dropped"), info.get("why", "")))


if __name__ == "__main__":
    main()
