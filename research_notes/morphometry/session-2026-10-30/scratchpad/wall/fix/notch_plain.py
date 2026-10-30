"""The slope a plain least-squares fit gives through the wall's edges on the BasivertebralNotch
test's vertebra, the notch at mid-height and 4 mm below it, against the truth.

  notch_plain.py
"""
import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T


def main():
    for z in (0.0, -4.0):
        v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0, notch_z=z)
        placed = P.straight(T.LUMBAR, v)
        vert = T.built(placed, T.LUMBAR, "L3")
        slope, info = T.wall_reading(vert)
        truth = BODY.degrees_of(slope) - T.wall_error(vert, placed, 0.0)
        B = vert.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        half, reach, lo, hi = BODY.wall_window(vert, B, xc)[0]
        bone, d = BODY.wall_edges(vert, xc, half, lo, hi, reach)
        e = bone + 0.5 * d
        coef = np.linalg.lstsq(BODY.wall_design(e, xc), e[:, 1], rcond=None)[0]
        print("notch at %+.0f: plain fit %+.2f degrees off, robust fit %+.2f, reading %+.2f, gate %.2f mm" % (
            z, BODY.degrees_of(coef[1]) - truth, info["fitted_deg"] - truth, BODY.degrees_of(slope) - truth, reach))


if __name__ == "__main__":
    main()
