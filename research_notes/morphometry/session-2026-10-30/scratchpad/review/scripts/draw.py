"""Draw phantom label volumes (ENHANCE.PET ids) into a masks folder, with the new engine's phantom."""
import sys, time
import numpy as np
import nibabel as nib
from morphometry.tests import phantom as P

out = sys.argv[1]
t0 = time.time()
cases = {
    "0001": dict(levels=["L2", "L3", "L4"], v=P.Vert()),
    "0002": dict(levels=["L3", "L4", "L5"], v=P.lumbar(canal_w=20.0, ped_w=7.0)),
}
for study, c in cases.items():
    placed = P.straight(c["levels"], c["v"])
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0))
    img = nib.Nifti1Image(lab.astype(np.int16), aff)
    nib.save(img, "%s/%s.nii.gz" % (out, study))
    print(study, lab.shape, sorted(set(np.unique(lab)) - {0}), "%.1f s" % (time.time() - t0), flush=True)
