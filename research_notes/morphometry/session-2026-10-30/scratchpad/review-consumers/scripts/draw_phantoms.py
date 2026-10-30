"""Draw phantom columns with bordercall's morphometry/tests/phantom.py and write them as NIfTI
label maps, one folder per scheme, for both engines to measure."""
import sys
import nibabel as nib
import numpy as np

sys.path.insert(0, sys.argv[1])            # bordercall main, for morphometry.tests.phantom
from morphometry.tests import phantom as P

out = sys.argv[2]


def save(lab, aff, path):
    nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), path)
    print(path, lab.shape, np.unique(lab).tolist())


# enhance: L2 to L5 on a sacrum and two hips, 1 mm voxels, and the same at 2.5 mm slices
levels = ["L2", "L3", "L4", "L5"]
placed = P.straight(levels)
lab, aff = P.draw(placed, spacing=(1.0, 1.0, 1.0), pelvis=P.Pelvis(), strict=False)
save(lab, aff, out + "/enhance/e001.nii.gz")
lab, aff = P.draw(placed, spacing=(0.86, 0.86, 2.5), pelvis=P.Pelvis(), strict=False)
save(lab, aff, out + "/enhance/e002.nii.gz")
# enhance: a slipped, opened column, L1 to L3
joint = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
lv3 = ["L1", "L2", "L3"]
placed = P.chain(lv3, {lv: P.Vert() for lv in lv3}, {lv: joint for lv in lv3[1:]}, R0=P.rotation((1.0, 0.3, 0.0), 12.0))
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), strict=False)
save(lab, aff, out + "/enhance/e003.nii.gz")
# verse: C2 to C4 with a dens, and T12 to L2
lvc = ["C2", "C3", "C4"]
verts = {"C2": P.cervical(dens_r=4.5, dens_h=14.0, dens_y=1.5), "C3": P.cervical(), "C4": P.cervical()}
placed = P.chain(lvc, verts, {lv: P.Joint() for lv in lvc[1:]}, R0=P.rotation((1.0, 0.0, 0.0), 2.0))
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
save(lab, aff, out + "/verse/v001.nii.gz")
lvt = ["T12", "L1", "L2"]
placed = P.straight(lvt)
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), strict=False)
save(lab, aff, out + "/verse/v002.nii.gz")
