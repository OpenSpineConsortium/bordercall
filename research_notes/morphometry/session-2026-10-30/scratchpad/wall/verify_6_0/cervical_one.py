"""One cervical-sized phantom (the robustness reviewer's C5) read by body.posterior_wall, to see
whether the truth lies in the range the freedom reports where the label does not part.

  cervical_one.py <spacing name> <tilt name> <lean>"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REV = os.path.join(os.path.dirname(HERE), "review_robustness")
sys.path.insert(0, REV)

from common import draw_and_build, show  # noqa: E402
from probe_cervical import CERVICAL, SPACINGS, TILTS  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402

sname, tname, lean = sys.argv[1], sys.argv[2], float(sys.argv[3])
v, placed, _, _ = draw_and_build(["C4", "C5", "C6"], "C5", P.lumbar(lean=lean, **CERVICAL), spacing=SPACINGS[sname],
                                 tilt=TILTS[tname])
show("C5 %s %s lean%+.0f" % (sname, tname, lean), v, placed, lean)
