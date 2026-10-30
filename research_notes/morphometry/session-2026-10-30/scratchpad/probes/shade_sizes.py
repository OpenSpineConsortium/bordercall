import math
import numpy as np
from morphoview.tests import test_projection as T
from morphoview import shapes as SH
t = T.Shapes()
T.Shapes.setUpClass()
for name, cam, v in T.recorded_views():
    for pl in t.placed:
        shadow = T.support(v, [pl.level])
        curves, surfaces = t.inside(pl)
        out = []
        for kind, s in surfaces.items():
            shade = s.silhouette(cam)
            out.append((kind, int(shade.sum()), int((shade & ~shadow).sum())))
        tilted_n = SH.unit(pl.R[:, 0] - pl.R[:, 1])
        seen = math.degrees(math.asin(abs(float(cam.ray_direction(pl.c)[0] @ tilted_n))))
        print(name[:12], pl.level, out, "cap seen at %.1f" % seen, "shadow", int(shadow.sum()))
