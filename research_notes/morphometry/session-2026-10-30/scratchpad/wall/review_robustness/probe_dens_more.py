"""C2's wall with its dens over a few shapes of dens and both slice thicknesses, and what C2's rows
then carry: endplate_lower_incl (kept at C2, measure.no_dens_plate drops only the upper plate)
against the phantom's truth, and the wall flags.

  probe_dens_more.py <thin|thick>"""
import sys

from common import draw_and_build, read
from morphometry import body as BODY
from morphometry.tests import phantom as P
from probe_cervical import CERVICAL, SPACINGS
from probe_label_edits import add_dens

sname = sys.argv[1] if len(sys.argv) > 1 else "thin"
tilt = ((1.0, 0.0, 0.0), 2.0)
kw = dict(CERVICAL)
truth = P.truth(P.lumbar(**kw))["endplate_lower_incl"]
for back_y, lean_back in ((None, None), (0.0, 0.0), (1.5, 0.0), (1.5, 12.0), (3.0, 12.0)):
    edit = None if back_y is None else add_dens("C2", kw["Hp"] / 2, back_y=back_y, lean_back_deg=lean_back)
    v, placed, _, _ = draw_and_build(["C2", "C3", "C4"], "C2", P.lumbar(**kw), spacing=SPACINGS[sname], tilt=tilt,
                                     edit=edit)
    tag = "no dens" if back_y is None else "dens back %+.1f mm, leaning back %.0f" % (back_y, lean_back)
    if "all" in v.flags:
        print("%-38s NOT BUILT %s" % (tag, v.flags["all"]))
        continue
    err, info, _, _ = read(v, placed, 0.0)
    got, flags = BODY.measures(v)
    wall_flags = {k: x[:40] for k, x in flags.items() if k.startswith("posterior_wall")}
    print("%-38s %s wall %+.2f (free %.2f) endplate_lower_incl err %+.2f flags %s" % (
        tag, sname, err, info.get("free_deg", float("nan")), got["endplate_lower_incl"] - truth, wall_flags), flush=True)
