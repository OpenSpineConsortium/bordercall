"""Which keys the rows hold a finite value for, and which of them the export draws a line for, on
the straight lumbar phantom the export's tests use (L2 to L4 at 0.8 by 0.8 by 1 mm)."""
import math
import sys

import numpy as np

sys.path.insert(0, "/home/user/bordercall")

from autoanatomist import specs as S          # noqa: E402
from morphometry import measure as M          # noqa: E402
from morphometry.tests import phantom as P    # noqa: E402
from morphoview import lines as LN            # noqa: E402
from scanimport import geometry as G          # noqa: E402

LEVELS = ["L2", "L3", "L4"]
lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
kept = {}
rows = M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, "probe",
                        pelvis=False, keep=kept)
for lv in LEVELS:
    vals = kept["values"][lv]
    finite = sorted(k for k, x in vals.items() if isinstance(x, float) and math.isfinite(x))
    lines = LN.checked(LN.vertebra_lines(kept["verts"][lv], kept["peds"][lv], vals), vals)
    drawn = sorted({ln.key for ln in lines})
    print(lv, "keys with a finite value:", len(finite), "keys with a line:", len(drawn))
    print(lv, "status of lines:", sorted({ln.status for ln in lines}))
    print(lv, "SEVEN without a line:", [k for k in S.SEVEN if k not in drawn])
    print(lv, "EXTRA without a line:", [k for k in S.EXTRA if k not in drawn])
    print(lv, "SEVEN values:", {k: round(vals[k], 3) for k in S.SEVEN})
    print(lv, "near:", {k: round(vals.get(k, float("nan")), 3) for k in
                         ("h_post", "h_post_inset", "canal_w", "interpedicular", "interpedicular_max", "canal_ap",
                          "canal_ap_min", "canal_ap_lateral_film")})
    if lv == "L3":
        print("drawn keys:", drawn)
        print("finite keys without a line:", [k for k in finite if k not in drawn])
