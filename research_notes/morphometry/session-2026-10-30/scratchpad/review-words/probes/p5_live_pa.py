"""The Live test's fresh PA render of the beads, with the numbers printed: max and median."""
import json, time
import numpy as np
import torch
torch.set_num_threads(2)
from morphoview import projection as PJ
from morphoview.tests import flexray_record as FR

R = json.load(open(FR.FIXTURE))
lab, aff = FR.phantom()
view = PJ.View(rot_deg=(4.0, -6.0, 3.0), xyz_mm=(10.0, -700.0, -5.0), isocentre_mm=tuple(R["isocentre_mm"]),
               sdd=1200.0, delx=1.0, height=256, width=256, orientation="PA")
cam = PJ.Camera(view)
balls, centroids = FR.bead_labels(lab.shape, aff, np.array(R["beads"]["centroids_mm"]))
t = time.time()
rendered = FR.render(np.where(balls > 0, FR.BONE_HU, FR.AIR_HU), balls, aff, view, FR.BEAD_SAMPLES)
print("render %.1f s" % (time.time() - t))
seen = [FR.channel_centroid(rendered[k + 1]) for k in range(len(centroids))]
print("seen", sum(c is not None for c in seen), "of", len(centroids))
ok = [k for k, c in enumerate(seen) if c is not None]
err = np.linalg.norm(cam.project(centroids[ok]).uv - np.array([seen[k] for k in ok]), axis=1)
print("max %.4f median %.4f mean %.4f" % (err.max(), np.median(err), err.mean()))
print("bead pixels (support) per bead: min %d" % min(int((rendered[k + 1] > 0).sum()) for k in range(len(centroids))))
