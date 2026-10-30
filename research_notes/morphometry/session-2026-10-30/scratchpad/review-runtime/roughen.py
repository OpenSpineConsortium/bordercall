"""roughen.py IN OUT SHARE SEED: a phantom label volume with its surfaces made ragged, as a real
segmenter's are: SHARE of the surface voxels taken off and SHARE of the voxels just outside put on
(each taking the largest neighbouring id), so the engine's least-crossing programs are exercised
where a smooth phantom parts cleanly.
"""
import sys

import nibabel as nib
import numpy as np
from scipy import ndimage


def main(src, dst, share, seed):
    img = nib.load(src)
    lab = np.asarray(img.dataobj)
    rng = np.random.default_rng(seed)
    inside = lab > 0
    surface = inside & ~ndimage.binary_erosion(inside)
    near = ndimage.maximum_filter(lab, size=3)
    outside = ~inside & (near > 0)
    out = lab.copy()
    out[surface & (rng.random(lab.shape) < share)] = 0
    grow = outside & (rng.random(lab.shape) < share)
    out[grow] = near[grow]
    nib.save(nib.Nifti1Image(out.astype(lab.dtype), img.affine), dst)
    print("%s: %d surface voxels, %d taken off, %d put on" % (dst, int(surface.sum()), int((lab > 0).sum() - (out[inside] > 0).sum()), int(grow.sum())))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))
