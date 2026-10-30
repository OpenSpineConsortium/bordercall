import math, itertools
import numpy as np
from morphoview.tests import test_projection as T
from morphoview.tests import flexray_record as FR
from morphoview import shapes as SH
placed = FR.placed()
best = []
for co in itertools.product((-1, 0, 1), repeat=3):
    if not any(co):
        continue
    worst = 90.0
    for name, cam, v in T.recorded_views():
        for pl in placed:
            n = SH.unit(pl.R @ np.array(co, float))
            worst = min(worst, math.degrees(math.asin(abs(float(cam.ray_direction(pl.c)[0] @ n)))))
    best.append((worst, co))
for w, co in sorted(best, reverse=True)[:6]:
    print(co, round(w, 1))
