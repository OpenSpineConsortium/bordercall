"""Our shadows against FleXray's supports, pixel by pixel, and the masks' drop."""
import json, time
import numpy as np
from morphoview import projection as PJ
from morphoview import shapes as SH
from morphoview.tests import flexray_record as FR

R = json.load(open(FR.FIXTURE))
lab, aff = FR.phantom()
print("phantom same:", FR.digest(lab, aff) == R["phantom"]["sha256"], lab.shape)
for v in R["views"]:
    cam = PJ.Camera(PJ.View(**v["view"]))
    shape = (v["view"]["height"], v["view"]["width"])
    for level, i in R["phantom"]["ids"].items():
        t = time.time()
        ours = SH.Volume.from_labels(lab, aff, i, largest=False).silhouette(cam, n_samples=R["n_samples"])
        dt = time.time() - t
        theirs = FR.unpack(v["supports"][level], shape)
        mask = FR.unpack(v["masks"][level], shape)
        print("%-45s %s differ %d support %d mask %d dropped %d (%.2f s)" % (
            v["name"], level, int((ours ^ theirs).sum()), int(theirs.sum()), int(mask.sum()),
            int((theirs & ~mask).sum()), dt))
