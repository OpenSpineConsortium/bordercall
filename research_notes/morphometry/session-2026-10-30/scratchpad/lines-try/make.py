import os, sys
import numpy as np, nibabel as nib
from morphometry.tests import phantom as P
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
levels = ["L1", "L2", "L3", "L4", "L5"]
lab, aff = P.draw(P.straight(levels, P.Vert()), spacing=(0.8, 0.8, 1.0))
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(out, "0001.nii.gz"))
lab2, aff2 = P.draw(P.straight(["L2", "L3", "L4"], P.Vert()), spacing=(0.86, 0.86, 2.5))
nib.save(nib.Nifti1Image(lab2.astype(np.int16), aff2), os.path.join(out, "0002.nii.gz"))
print(lab.shape, lab2.shape)
