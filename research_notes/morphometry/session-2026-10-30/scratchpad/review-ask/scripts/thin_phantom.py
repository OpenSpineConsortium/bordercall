"""The recorded L2 to L4 phantom drawn at 0.5 mm slices (a thin-slice CT of the same column), saved
as a mask, its levels' slice ranges printed, then the morphometry lines export run on it."""
import os
import sys
import numpy as np
import nibabel as nib
bc, out = sys.argv[1], sys.argv[2]
sys.path.insert(0, bc)
from morphometry.tests import phantom as P
from morphometry import __main__ as RUN
lab, aff = P.draw(P.straight(["L2", "L3", "L4"], P.Vert()), spacing=(0.8, 0.8, 0.5))
masks = os.path.join(out, "masks")
os.makedirs(masks, exist_ok=True)
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(masks, "0001.nii.gz"))
np.save(os.path.join(out, "lab.npy"), lab)
np.save(os.path.join(out, "aff.npy"), aff)
print("shape", lab.shape)
for lv in ("L2", "L3", "L4"):
    ks = np.argwhere(lab == P.LEVEL_IDS[lv])[:, 2]
    print(lv, "k from", ks.min(), "to", ks.max())
RUN.main(["run", "--masks", masks, "--scheme", "verse", "--out", os.path.join(out, "run"), "--workers", "1", "--lines"])
