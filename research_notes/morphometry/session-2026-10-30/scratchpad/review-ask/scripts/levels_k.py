"""Which slices (the last voxel axis, the axis FleXray's crops cut) each level of the recorded phantom fills."""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from morphoview.tests import flexray_record as FR
lab, aff = FR.phantom()
print("shape", lab.shape)
print("affine\n", np.round(aff, 4))
for lv, i in FR.level_ids().items():
    ks = np.argwhere(lab == i)[:, 2]
    print(lv, "k from", ks.min(), "to", ks.max(), "voxels", len(ks))
