"""The wall where the vertebra turns about its own axis against the scan, as a scoliotic vertebra
does (20 to 45 degrees): the scan's axis nearest the frame's y then lies that far off it, and the
scan lines cross the curved wall obliquely. Lumbar phantom, 1 mm and 2.5 mm slices."""
import sys

from common import draw_and_build, show
from morphometry.tests import phantom as P

LUMBAR = ["L2", "L3", "L4"]
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
which = sys.argv[1:] or list(SPACINGS)
for sname in which:
    for turn in (20.0, 30.0, 40.0, 45.0):
        for lean in (0.0, 5.0):
            v, placed, _, _ = draw_and_build(LUMBAR, "L3", P.lumbar(lean=lean), spacing=SPACINGS[sname],
                                             tilt=((1.0, 0.0, 0.0), 2.0), grid_turn=((0.0, 0.0, 1.0), turn))
            show("%s turn%.0f lean%+.0f" % (sname, turn, lean), v, placed, lean)
