"""Whether a notch off the wall's mid-height tells the robust fit from plain least squares, where
the suite's notch, centred at mid-height and so symmetric in z, does not: the notch of
BasivertebralNotch (5 wide, 6 tall, 4 deep) drawn with its centre RAISE mm above mid-height,
read by the reader as it stands, with trimmed_start and biweight replaced by one plain fit, and
with the plain fit as the biweight's start.

    notch_up.py RAISE [RAISE ...]"""
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T

ORIG_INSIDE = P.body_inside
ORIG = (BODY.trimmed_start, BODY.biweight)


def raised(dz):
    def inside(q, v):
        q2 = np.array(q, float, copy=True)
        q2[:, 2] -= dz
        hole = (np.abs(q2[:, 0]) <= v.notch_w / 2) & (np.abs(q2[:, 2]) <= v.notch_h / 2) & (q2[:, 1] <= v.notch_d)
        plain = P.replace(v, notch_w=0.0, notch_h=0.0, notch_d=0.0)
        return ORIG_INSIDE(q, plain) & ~hole
    return inside


def read(vert, fit):
    if fit in ("plain fit", "plain start, biweight"):
        BODY.trimmed_start = lambda X, y, z: np.linalg.lstsq(X, y, rcond=None)[0]
    if fit == "plain fit":
        BODY.biweight = lambda X, y, coef, scale: coef
    try:
        vert.__dict__.pop("_posterior_wall", None)
        B = vert.body_pts
        slope, info = BODY.read_wall(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
    finally:
        BODY.trimmed_start, BODY.biweight = ORIG
    return slope, info


def main():
    for dz in map(float, sys.argv[1:]):
        v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)
        P.body_inside = raised(dz)
        try:
            placed = P.straight(T.LUMBAR, v)
            vert = T.built(placed, T.LUMBAR, "L3")
        finally:
            P.body_inside = ORIG_INSIDE
        for fit in ("robust fit", "plain fit", "plain start, biweight"):
            vert.__dict__.pop("_posterior_wall", None)
            slope, info = read(vert, fit)
            vert._posterior_wall = None
            vert.__dict__.pop("_posterior_wall", None)
            R = [pl for pl in placed if pl.level == "L3"][0].R
            w = R @ np.array([0.0, 0.0, 1.0])
            truth = math.degrees(math.atan(float(vert.frame.ey @ w) / float(vert.frame.ez @ w)))
            err = BODY.degrees_of(slope) - truth if math.isfinite(slope) else float("nan")
            print("notch raised %.1f mm, %s: error %+.3f deg, parted %s, free %s, edges %s, dropped %s, why %s" % (
                dz, fit, err, info.get("parted"), info.get("free_deg"), info.get("edges"),
                info.get("dropped"), info.get("why", "")))


if __name__ == "__main__":
    main()
