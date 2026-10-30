"""Where the canal's full rings stand against the body's height at the midline and the wall's
window, on the cervical C2 with and without its dens and on the lumbar phantom's L3.

  rings.py <thin|thick>
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import SPACINGS, GRIDS, build, read, line  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402

sys.path.insert(0, "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall/review_robustness")
from probe_cervical import CERVICAL  # noqa: E402
from probe_label_edits import add_dens  # noqa: E402


def show(tag, v):
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    place, why = BODY.wall_window(v, B, xc)
    rings = v.full_rings()
    zs = [s.z for s in rings]
    mid = B[np.abs(B[:, 0] - xc) <= 3.0]
    print("%-30s body z %+6.1f..%+6.1f  rings %2d z %+6.1f..%+6.1f  window %s" % (
        tag, mid[:, 2].min(), mid[:, 2].max(), len(rings), min(zs), max(zs),
        None if place is None else "%+.1f..%+.1f" % (place[2], place[3])))


def main():
    sname = sys.argv[1]
    tilt, turn = GRIDS["x2"]
    kw = dict(CERVICAL)
    for dens in (False, True):
        edit = add_dens("C2", kw["Hp"] / 2, back_y=1.5, lean_back_deg=12.0) if dens else None
        v, placed = build(["C2", "C3", "C4"], "C2", P.lumbar(**kw), SPACINGS[sname], tilt, turn, edit)
        show("C2 %s" % ("dens" if dens else "no dens"), v)
    v, placed = build(["L2", "L3", "L4"], "L3", P.lumbar(), SPACINGS[sname], tilt, turn)
    show("L3", v)
    v, placed = build(["C4", "C5", "C6"], "C5", P.lumbar(**kw), SPACINGS[sname], tilt, turn)
    show("C5", v)


if __name__ == "__main__":
    main()
