"""Cervical uncinate processes and the wall's window. The window is the middle WALL_HEIGHT_SHARE of
the height the body's points span within the band (|x| up to 6 mm on a cervical canal), where the
reading it replaced took the span within 3 mm (ACROSS_HALF_MM); an uncinate process rising from
the upper plate's lateral rim inside the band lifts that span's top. The C5 phantom's body outline
is carried up from the upper plate by `rise` mm wherever it lies `from_x` mm or more off the
midline, and the wall is read with and without it.

  probe_uncinate.py <thin|thick>"""
import sys

import numpy as np

from common import draw_and_build, read
from morphometry import body as BODY
from morphometry.tests import phantom as P
from probe_cervical import CERVICAL, SPACINGS
from probe_label_edits import local_coords, old_slope
from common import wall_truth_deg


def add_uncinates(level, v, from_x, rise):
    def edit(lab, aff, placed):
        idx, q = local_coords(lab, aff, placed, level)
        a, b, top = v.W / 2, v.D / 2, v.Hp / 2
        inside = (((q[:, 0] / a) ** 2 + ((q[:, 1] - b) / b) ** 2 <= 1.0) & (np.abs(q[:, 0]) >= from_x)
                  & (q[:, 2] >= top - 0.5) & (q[:, 2] <= top + rise))
        sel = tuple(idx[inside & (lab[tuple(idx.T)] == 0)].T)
        lab = lab.copy()
        lab[sel] = P.LEVEL_IDS[level]
        return lab
    return edit


sname = sys.argv[1] if len(sys.argv) > 1 else "thin"
kw = dict(CERVICAL)
vert = P.lumbar(**kw)
for tname, tilt in (("x2", ((1.0, 0.0, 0.0), 2.0)), ("suite18", ((1.0, 0.3, 0.0), 18.0))):
    for case in (None, (5.5, 4.0), (5.0, 5.0), (4.5, 5.0)):
        edit = None if case is None else add_uncinates("C5", vert, *case)
        v, placed, _, _ = draw_and_build(["C4", "C5", "C6"], "C5", vert, spacing=SPACINGS[sname], tilt=tilt, edit=edit)
        tag = "none" if case is None else "from %.1f mm, %.0f mm tall" % case
        if "all" in v.flags:
            print(tname, tag, "NOT BUILT", v.flags["all"])
            continue
        B = v.body_pts
        xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
        old = BODY.degrees_of(old_slope(v, B, xc)) - wall_truth_deg(v, placed, 0.0)
        err, info, _, _ = read(v, placed, 0.0)
        place, _ = BODY.wall_window(v, B, xc)
        print("%s %-8s uncinates %-22s new %+.2f old %+.2f free %.2f window %.1f to %.1f mm" % (
            sname, tname, tag, err, old, info.get("free_deg", float("nan")), place[2], place[3]), flush=True)
