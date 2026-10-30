"""Draw phantom label volumes for timing the morphometry engines: a lumbar column on a pelvis and a
cervical-to-sacrum column on a pelvis, each at two spacings, written as ENHANCE.PET-id NIfTIs.

Run with PYTHONPATH at the bordercall main checkout, whose morphometry/tests/phantom.py draws them:
    python make_phantoms.py OUTDIR
"""
import os
import sys
import time

import nibabel as nib
import numpy as np

from morphometry.tests import phantom as P

LUMBAR = ["L1", "L2", "L3", "L4", "L5"]
CERV = ["C3", "C4", "C5", "C6", "C7"]
THOR = ["T%d" % i for i in range(1, 13)]
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}


def thoracic():
    """A vertebra halfway between the cervical preset and the lumbar default in every field the
    cervical preset sets, a stand-in for a mid-thoracic level."""
    lum = P.Vert()
    mid = {k: 0.5 * (val + getattr(lum, k)) for k, val in P.CERVICAL.items()}
    return P.Vert(**mid)


def lumbar_column():
    return P.chain(LUMBAR, {lv: P.Vert() for lv in LUMBAR},
                   {lv: P.Joint(gap=10.0, sagittal=4.0) for lv in LUMBAR[1:]},
                   R0=P.rotation((1.0, 0.3, 0.0), 12.0))


def full_column():
    levels = CERV + THOR + LUMBAR
    verts = {**{lv: P.cervical() for lv in CERV}, **{lv: thoracic() for lv in THOR},
             **{lv: P.Vert() for lv in LUMBAR}}
    gaps = {**{lv: 5.0 for lv in CERV}, **{lv: 6.0 for lv in THOR}, **{lv: 10.0 for lv in LUMBAR}}
    joints = {lv: P.Joint(gap=gaps[lv]) for lv in levels[1:]}
    return P.chain(levels, verts, joints, R0=P.rotation((1.0, 0.3, 0.0), 8.0)), levels


def write(out, name, placed, spacing):
    t0 = time.time()
    lab, aff = P.draw(placed, spacing=spacing, pelvis=P.Pelvis(), strict=False)
    nib.save(nib.Nifti1Image(lab, aff), os.path.join(out, name + ".nii.gz"))
    present = sorted(int(x) for x in np.unique(lab) if x)
    print("%s shape %s ids %s drawn in %.1f s" % (name, lab.shape, present, time.time() - t0), flush=True)


def main(out):
    os.makedirs(out, exist_ok=True)
    full, _ = full_column()
    for tag, spacing in SPACINGS.items():
        write(out, "lumbar_" + tag, lumbar_column(), spacing)
        write(out, "full_" + tag, full, spacing)


if __name__ == "__main__":
    main(sys.argv[1])
