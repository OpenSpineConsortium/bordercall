import os
import numpy as np
from scipy import ndimage
from morphoview.tests import test_projection as T
from morphoview.tests import flexray_record as FR
L = T.Lines
L.setUpClass()
worst = []
for got in L.views:
    v = got["record"]
    shape = (v["view"]["height"], v["view"]["width"])
    far_all = []
    for row, line in zip(L.rows, got["lines"]):
        if row["status"] != "drawn":
            continue
        levels = row["level"].split("-")
        mask = np.logical_or.reduce([FR.unpack(v["masks"][lv], shape) for lv in levels])
        dist = ndimage.distance_transform_edt(~mask)
        for e in "ab":
            if float(line[e + "_off_px"]) > 0:
                continue
            u, vv = float(line[e + "u"]), float(line[e + "v"])
            far_all.append((float(dist[int(vv), int(u)]), row["level"], row["key"], row["part"], e))
    far_all.sort(reverse=True)
    print(got["name"], "ends on the shadow:", len(far_all), "off the 0.5 mask:", sum(f[0] > 0 for f in far_all),
          "max", far_all[0])
