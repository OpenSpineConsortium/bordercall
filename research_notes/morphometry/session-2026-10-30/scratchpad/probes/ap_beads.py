"""Beads on fresh views: nanoDRR's PA turn, and the AP turn from behind as SchwingNet poses its
posterior views; how many are seen and how far their centroids lie from the projected centres."""
import sys
import time

sys.path.insert(0, sys.argv[1])
import numpy as np  # noqa: E402
from morphoview import projection as PJ  # noqa: E402
from morphoview.tests import flexray_record as FR  # noqa: E402
from morphoview.tests.test_projection import RECORD  # noqa: E402

lab, aff = FR.phantom()
iso = tuple(RECORD["isocentre_mm"])
views = {
    "PA": PJ.View(rot_deg=(4.0, -6.0, 3.0), xyz_mm=(10.0, -700.0, -5.0), isocentre_mm=iso, sdd=1200.0, delx=1.0,
                  height=256, width=256, orientation="PA"),
    "AP behind": PJ.View(rot_deg=(184.0, -6.0, 3.0), xyz_mm=(10.0, 700.0, -5.0), isocentre_mm=iso, sdd=1200.0,
                         delx=1.0, height=256, width=256, orientation="AP"),
}
balls, centroids = FR.bead_labels(lab.shape, aff, np.array(RECORD["beads"]["centroids_mm"]))
for name, view in views.items():
    t0 = time.time()
    cam = PJ.Camera(view)
    rendered = FR.render(np.where(balls > 0, FR.BONE_HU, FR.AIR_HU), balls, aff, view, FR.BEAD_SAMPLES)
    seen = [FR.channel_centroid(rendered[k + 1]) for k in range(len(centroids))]
    ok = [s is not None for s in seen]
    err = np.linalg.norm(cam.project(centroids).uv[ok] - np.array([s for s in seen if s is not None]), axis=1)
    print("%-10s seen %d of %d, max %.4f median %.4f px, source %s, beam %s, %.0f s"
          % (name, sum(ok), len(ok), err.max(), np.median(err), cam.source.round(1), cam.beam.round(3), time.time() - t0))
