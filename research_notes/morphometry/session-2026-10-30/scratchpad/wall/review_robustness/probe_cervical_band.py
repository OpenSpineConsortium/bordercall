"""Why the cervical phantom's wall reads low with the wall leaned: the same vertebra read with the
band capped narrower (WALL_BAND_MAX_MM), and with the pedicles turned out of the band's reach."""
import sys

from common import draw_and_build, read
from morphometry import body as BODY
from morphometry.tests import phantom as P
from probe_cervical import CERVICAL, SPACINGS, TILTS

sname = sys.argv[1] if len(sys.argv) > 1 else "thin"
for label, kw in (("pedicles at 45", {}), ("pedicles at 0", dict(ped_t=0.0, ped_back=1.0))):
    for tname in ("x0", "suite18"):
        for lean in (5.0, -5.0):
            v, placed, _, _ = draw_and_build(["C4", "C5", "C6"], "C5", P.lumbar(lean=lean, **dict(CERVICAL, **kw)),
                                             spacing=SPACINGS[sname], tilt=TILTS[tname])
            if "all" in v.flags:
                print(label, tname, lean, "NOT BUILT", v.flags["all"])
                continue
            cells = []
            for cap in (6.0, 5.0, 4.0, 3.0):
                BODY.WALL_BAND_MAX_MM = cap
                err, info, _, _ = read(v, placed, lean)
                cells.append("cap %.0f: %+.2f (free %.2f, %s)" % (cap, err, info.get("free_deg", float("nan")),
                                                                 "parted" if info.get("parted") else "not parted"))
            BODY.WALL_BAND_MAX_MM = 6.0
            print("%-15s %s %-8s lean%+.0f | %s" % (label, sname, tname, lean, " | ".join(cells)), flush=True)
