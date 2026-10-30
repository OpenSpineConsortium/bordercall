"""The band's half-width and the edges' spread across x on the suite's notch phantom, built as the
test builds it, and where the pedicles' medial walls stand from the midline."""
import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T


def main():
    v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0)
    placed = P.straight(T.LUMBAR, v)
    vert = T.built(placed, T.LUMBAR, "L3")
    B = vert.body_pts
    xc = vert.midline
    w = float(np.median([s.width for s in vert.full_rings()]))
    half, reach, lo, hi = BODY.wall_window(vert, B, xc)[0]
    bone, d = BODY.wall_edges(vert, xc, half, lo, hi, reach)
    xs = bone[:, 0] + 0.5 * d[0] - xc
    slope, info = BODY.posterior_wall(vert, B, xc)
    print("canal width %.2f mm, half %.2f mm, full band %.2f mm (%.3f of the width)" % (w, half, 2 * half, 2 * half / w))
    print("edges %d, x from midline %.2f to %.2f (span %.2f mm); info half_band_mm %.2f"
          % (len(xs), xs.min(), xs.max(), np.ptp(xs), info.get("half_band_mm", float("nan"))))
    print("canal's medial walls (pedicle roots) at about +-%.2f mm from the midline" % (0.5 * w))


if __name__ == "__main__":
    main()
