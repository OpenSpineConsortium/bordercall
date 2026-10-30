import sys, time
sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphoview import projection as PJ
from morphoview.tests import test_projection as T, flexray_record as FR
lab, aff, same = T.phantom()
view = PJ.View(rot_deg=(4.0, -6.0, 3.0), xyz_mm=(10.0, -700.0, -5.0), isocentre_mm=tuple(T.RECORD["isocentre_mm"]),
               sdd=1200.0, delx=1.0, height=256, width=256, orientation="PA")
cam = PJ.Camera(view)
balls, centroids = FR.bead_labels(lab.shape, aff, np.array(T.RECORD["beads"]["centroids_mm"]))
t0 = time.time()
rendered = FR.render(np.where(balls > 0, FR.BONE_HU, FR.AIR_HU), balls, aff, view, FR.BEAD_SAMPLES)
seen = np.array([FR.channel_centroid(rendered[k + 1]) for k in range(len(centroids))])
err = np.linalg.norm(cam.project(centroids).uv - seen, axis=1)
print("PA 256: %d beads, error px median %.3f max %.3f; render %.1f s" % (len(err), np.median(err), err.max(), time.time() - t0))
