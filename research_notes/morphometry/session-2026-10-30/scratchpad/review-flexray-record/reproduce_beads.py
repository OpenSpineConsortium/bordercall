"""The recorded bead centroids rendered again like for like: the balls built around the line ends
the recorder picked (pick_beads(line_ends(...))), as record() builds them."""
import json
import sys

import numpy as np
import torch

torch.set_num_threads(2)
sys.path.insert(0, sys.argv[1])
from morphoview import projection as PJ  # noqa: E402
from morphoview.tests import flexray_record as FR  # noqa: E402

RECORD = json.load(open(FR.FIXTURE))
lab, aff = FR.phantom()
centres = FR.pick_beads(FR.line_ends(lab, aff))
balls, bead_mm = FR.bead_labels(lab.shape, aff, centres)
print("bead truth vs record, mm:", float(np.abs(bead_mm - np.array(RECORD["beads"]["centroids_mm"])).max()))
hu = np.where(balls > 0, FR.BONE_HU, FR.AIR_HU)
for v in RECORD["views"]:
    view = PJ.View(**v["view"])
    rendered = FR.render(hu, balls, aff, view, FR.BEAD_SAMPLES)
    seen = [FR.channel_centroid(rendered[k + 1]) for k in range(len(bead_mm))]
    d = [float(np.linalg.norm(np.array(a) - np.array(b))) for a, b in zip(seen, v["bead_centroids_uv"])]
    print(v["name"], "again vs record: max %.2e px" % max(d))
