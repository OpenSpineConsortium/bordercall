"""The BasivertebralNotch test's vertebra with the notch 4 mm below mid-height: the reading, the
fit alone, a plain least-squares fit through the same edges, the gate's reach, and whether the
cervical C2 draws strict.

  notch_low.py
"""
import math
from unittest import mock

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T


def plain_fit(e, d, xc):
    X = BODY.wall_design(e, xc)
    return np.linalg.lstsq(X, e[:, 1], rcond=None)[0]


def main():
    v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0, notch_z=-4.0)
    placed = P.straight(T.LUMBAR, v)
    vert = T.built(placed, T.LUMBAR, "L3")
    slope, info = T.wall_reading(vert)
    err = T.wall_error(vert, placed, 0.0)
    truth = BODY.degrees_of(slope) - err
    B = vert.body_pts
    place = BODY.wall_window(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))[0]
    print("reading %+.3f fit alone %+.3f gate reach %.2f mm parted %s across %s" % (
        err, info["fitted_deg"] - truth, place[1], info["parted"], info["across"]))
    vert.__dict__.pop("_posterior_wall", None)
    with mock.patch.object(BODY, "fitted_wall", plain_fit):
        s2, i2 = T.wall_reading(vert)
    print("plain fit: reading %+.3f fit %+.3f parted %s why %s" % (
        BODY.degrees_of(s2) - truth if math.isfinite(s2) else math.nan, i2.get("fitted_deg", math.nan) - truth,
        i2.get("parted"), i2.get("why", "")))
    verts = {"C2": P.cervical(dens_r=4.5, dens_h=14.0, dens_y=1.5), "C3": P.cervical(), "C4": P.cervical()}
    levels = ["C2", "C3", "C4"]
    placed = P.chain(levels, verts, {lv: P.Joint() for lv in levels[1:]}, R0=P.rotation((1.0, 0.0, 0.0), 2.0))
    try:
        P.draw(placed, grid_turn=((0.0, 0.0, 1.0), 0.0), strict=True)
        print("C2 draws strict")
    except Exception as exc:  # noqa: BLE001 - the probe reports whatever draw raises
        print("C2 strict raises %s: %s" % (type(exc).__name__, str(exc)[:200]))
    P2 = {"C2": P.cervical(), "C3": P.cervical(), "C4": P.cervical()}
    try:
        P.draw(P.chain(levels, P2, {lv: P.Joint() for lv in levels[1:]}, R0=P.rotation((1.0, 0.0, 0.0), 2.0)),
               grid_turn=((0.0, 0.0, 1.0), 0.0), strict=True)
        print("C2 without the dens draws strict")
    except Exception as exc:  # noqa: BLE001
        print("C2 without the dens strict raises %s: %s" % (type(exc).__name__, str(exc)[:200]))


if __name__ == "__main__":
    main()
