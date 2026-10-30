import math
import numpy as np
from scipy import ndimage
from morphoview.tests import test_projection as T
from morphoview.tests import flexray_record as FR
from morphoview import shapes as SH
lab, aff, same = T.phantom()
R = T.RECORD
tmp, mask, lines, frames, rows = T.exported()
mu = R["uniform"]["mu_per_mm"]
for name, cam, v in T.recorded_views():
    shape = (cam.view.height, cam.view.width)
    src, det = cam.rays(cam.pixel_centres())
    step = (np.linalg.norm(det - src, axis=1) / (R["n_samples"] - 1)).reshape(shape)
    diffs, kept_min, dropped, dropped_max = [], [], [], []
    for level, i in R["phantom"]["ids"].items():
        vol = SH.Volume.from_labels(lab, aff, i, largest=False)
        ours = vol.silhouette(cam, n_samples=R["n_samples"])
        theirs = T.support(v, [level])
        diffs.append(int((ours ^ theirs).sum()))
        pl = vol.path_length(cam, n_samples=R["n_samples"])
        m = FR.unpack(v["masks"][level], shape)
        kept_min.append(float(pl[m].min()))
        d = (pl > 0) & ~m
        dropped.append(int(d.sum()))
        dropped_max.append(float(pl[d].max()))
    # line ends against the 0.5 masks
    far_mask = 0.0
    far_support = 0.0
    for row in rows:
        lv = row["level"].split("-")
        sh = np.logical_or.reduce([FR.unpack(v["masks"][x], shape) for x in lv])
        su = T.support(v, lv)
        dm = ndimage.distance_transform_edt(~sh)
        ds = ndimage.distance_transform_edt(~su)
        for e in "ab":
            if T.construction(row, e) and name != T.LATERAL:
                continue
            uv = cam.project(T.point(row, e)[None]).uv[0]
            r, c = int(math.floor(uv[1])), int(math.floor(uv[0]))
            far_mask = max(far_mask, float(dm[r, c]))
            far_support = max(far_support, float(ds[r, c]))
    print(name[:14], "shadow differs", diffs, "kept min %.2f" % min(kept_min), "dropped", dropped, "dropped max %.2f" % max(dropped_max),
          "ends off mask %.1f off support %.2f" % (far_mask, far_support))
print("0.5/mu", 0.5 / mu)
