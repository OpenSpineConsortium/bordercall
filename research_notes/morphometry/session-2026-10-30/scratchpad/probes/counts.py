"""How FleXray's channels, divided by the bone's attenuation and each ray's step, compare with
the counts of samples morphoview.shapes reads, on the record's three views."""
import sys
import time

sys.path.insert(0, sys.argv[1])
import numpy as np  # noqa: E402
import torch  # noqa: E402
from nanodrr.data.preprocess import hu_to_mu  # noqa: E402

from morphoview import projection as PJ  # noqa: E402
from morphoview import shapes as SH  # noqa: E402
from morphoview.tests import flexray_record as FR  # noqa: E402
from morphoview.tests.test_projection import RECORD, recorded_views  # noqa: E402

lab, aff = FR.phantom()
mu = float(hu_to_mu(torch.full((1, 1, 1, 1, 1), float(FR.BONE_HU)))[0, 0, 0, 0, 0])
print("mu at %d HU: %.6f per mm" % (FR.BONE_HU, mu))
n = RECORD["n_samples"]
bone = np.full(lab.shape, FR.BONE_HU) if "--uniform" in sys.argv else np.where(lab > 0, FR.BONE_HU, FR.AIR_HU)
for name, cam, v in recorded_views():
    t0 = time.time()
    rendered = FR.render(bone, lab, aff, cam.view)
    src, det = cam.rays(cam.pixel_centres())
    step = (np.linalg.norm(det - src, axis=1) / (n - 1)).reshape(cam.view.height, cam.view.width)
    for level, i in RECORD["phantom"]["ids"].items():
        theirs = rendered[i] / (mu * step)
        frac = np.abs(theirs - np.rint(theirs))
        ours = SH.Volume.from_labels(lab, aff, i, largest=False).path_length(cam, n_samples=n) / step
        d = np.rint(theirs).astype(int) - np.rint(ours).astype(int)
        print("%-45s %s  max off an integer %.2e  pixels %5d  differ %d (by at most %d)  ours max off %.1e"
              % (name, level, frac.max(), int((theirs > 0.5).sum()), int((d != 0).sum()), int(np.abs(d).max()),
                 float(np.abs(ours - np.rint(ours)).max())))
    print("  %.1f s" % (time.time() - t0))
