"""Whether the committed phantom's lean draws the scratch cache's sheared body voxel for voxel,
on one grid near the frame and on the suite's grid; and whether the repository alone names the
cache's configurations."""
import math
import sys

import numpy as np

sys.path.insert(0, "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall")
import build_cache as BC
from morphometry.tests import phantom as P

for gname, tilt, turn in [g for g in BC.GRIDS if g[0] in ("x2", "suite18")]:
    for lean in (5.0, -5.0):
        for sname in ("thin", "thick"):
            P.body_inside = BC.sheared(lean)
            try:
                v0 = P.lumbar()
                lab0, aff0 = P.draw(P.straight(BC.LUMBAR, v0, tilt=tilt), spacing=BC.SPACINGS[sname],
                                    grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
            finally:
                P.body_inside = BC._BODY_INSIDE
            v1 = P.lumbar(lean=lean)
            lab1, aff1 = P.draw(P.straight(BC.LUMBAR, v1, tilt=tilt), spacing=BC.SPACINGS[sname],
                                grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
            same_shape = lab0.shape == lab1.shape
            diff = int((lab0 != lab1).sum()) if same_shape else -1
            print("%-8s lean %+.0f %-5s shape equal %s, voxels differing %d of %d, affine equal %s"
                  % (gname, lean, sname, same_shape, diff, lab0.size, np.allclose(aff0, aff1)))
