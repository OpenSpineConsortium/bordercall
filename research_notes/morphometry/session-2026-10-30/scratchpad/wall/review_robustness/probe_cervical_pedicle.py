"""Whether the cervical phantom's low reading comes from the pedicles' roots inside the band: the
same C5 on the fine grid with its pedicles at the body's upper half (ped_z 2, the default here) and
moved to its lower half (ped_z -2), each read with the band capped at 6, 4 and 3 mm."""
import sys

from common import draw_and_build, read
from morphometry import body as BODY
from morphometry.tests import phantom as P
from probe_cervical import CERVICAL, SPACINGS, TILTS

sname = sys.argv[1] if len(sys.argv) > 1 else "fine"
for ped_z in (2.0, -2.0):
    for tname in ("x2", "suite18"):
        lean = 0.0
        v, placed, _, _ = draw_and_build(["C4", "C5", "C6"], "C5", P.lumbar(lean=lean, **dict(CERVICAL, ped_z=ped_z)),
                                         spacing=SPACINGS[sname], tilt=TILTS[tname])
        if "all" in v.flags:
            print(ped_z, tname, "NOT BUILT", v.flags["all"])
            continue
        cells = []
        for cap in (6.0, 4.0, 3.0):
            BODY.WALL_BAND_MAX_MM = cap
            err, info, _, _ = read(v, placed, lean)
            cells.append("cap %.0f: %+.2f (free %.2f, %s)" % (cap, err, info.get("free_deg", float("nan")),
                                                             "parted" if info.get("parted") else "not parted"))
        BODY.WALL_BAND_MAX_MM = 6.0
        print("ped_z %+.0f %s %-8s | %s" % (ped_z, sname, tname, " | ".join(cells)), flush=True)
