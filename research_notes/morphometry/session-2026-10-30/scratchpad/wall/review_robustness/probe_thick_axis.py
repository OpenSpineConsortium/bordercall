"""The wall on slices whose thick axis is not the scan's z: sagittal (thick along x) and coronal
(thick along y, the wall's own step direction) stacks, against the axial baseline."""
import sys

from common import draw_and_build, show
from morphometry.tests import phantom as P

LUMBAR = ["L2", "L3", "L4"]
SPACINGS = {
    "axial2.5": (0.86, 0.86, 2.5),
    "sag2.5": (2.5, 0.86, 0.86),
    "sag4": (4.0, 0.86, 0.86),
    "cor2.5": (0.86, 2.5, 0.86),
    "cor4": (0.86, 4.0, 0.86),
}
TILTS = {"x0": ((1.0, 0.0, 0.0), 0.0), "x2": ((1.0, 0.0, 0.0), 2.0), "x5": ((1.0, 0.0, 0.0), 5.0),
         "suite18": ((1.0, 0.3, 0.0), 18.0)}

which = sys.argv[1:] or list(SPACINGS)
for sname in which:
    for tname, tilt in TILTS.items():
        for lean in (0.0, 5.0):
            v, placed, _, _ = draw_and_build(LUMBAR, "L3", P.lumbar(lean=lean), spacing=SPACINGS[sname], tilt=tilt)
            show("%s %s lean%+.0f" % (sname, tname, lean), v, placed, lean)
