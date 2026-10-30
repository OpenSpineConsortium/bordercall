import numpy as np
from morphoview.tests import test_projection as T
from morphoview import shapes as SH
lab, aff, same = T.phantom()
print("phantom is the recorded one:", same)
for name, cam, v in T.recorded_views():
    for level, i in T.RECORD["phantom"]["ids"].items():
        ours = SH.Volume.from_labels(lab, aff, i, largest=False).silhouette(cam, n_samples=T.RECORD["n_samples"])
        theirs = T.support(v, [level])
        print("%-46s %s: differ %d px (ours %d, FleXray %d)" % (name, level, int((ours ^ theirs).sum()), int(ours.sum()), int(theirs.sum())))
