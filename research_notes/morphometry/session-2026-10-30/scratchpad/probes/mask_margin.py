import json
import numpy as np
from morphoview import projection as PJ, shapes as SH
from morphoview.tests import flexray_record as FR
rec = json.load(open(FR.FIXTURE))
lab, aff = FR.phantom()
mu = rec["uniform"]["mu_per_mm"]
for v in rec["views"]:
    cam = PJ.Camera(PJ.View(**v["view"]))
    shape = (cam.view.height, cam.view.width)
    src, det = cam.rays(cam.pixel_centres())
    step = (np.linalg.norm(det - src, axis=1) / (rec["n_samples"] - 1)).reshape(shape)
    for lv, i in rec["phantom"]["ids"].items():
        mask = FR.unpack(v["masks"][lv], shape)
        ours = SH.Volume.from_labels(lab, aff, i, largest=False).path_length(cam, n_samples=rec["n_samples"])
        margin = (mu * (ours + step) - 0.5)[mask]
        dropped = ((ours > 0) & ~mask)
        print(v["name"][:20], lv, "mask px", int(mask.sum()), "min margin %.4f" % margin.min(),
              "dropped", int(dropped.sum()), "longest dropped %.2f mm" % ours[dropped].max(),
              "shortest kept %.2f mm" % ours[mask].min(), "0.5/mu %.2f" % (0.5 / mu))
