"""Phantom label files for the robustness review: written under OUT/<name>/masks/<id>.nii.gz.

    python make_phantoms.py OUT

lumbar5   L1 to L5 lumbar, 0.8 x 0.8 x 1 mm, tilted 18 degrees (phantom.straight)
long      C2 to L5: cervical C2 (with a dens) to C7, lumbar-sized T1 to L5, 0.8 x 0.8 x 1 mm
cervical  C2 (dens) to C7 alone, 0.8 x 0.8 x 1 mm, strict off as DensAtC2 draws it
"""
import os
import sys
import time

import nibabel as nib
import numpy as np

from morphometry.tests import phantom as P


def save(lab, aff, folder, study):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, study + ".nii.gz")
    nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), path)
    return path


def main(out):
    t = time.time()
    lab, aff = P.draw(P.straight(["L1", "L2", "L3", "L4", "L5"], P.Vert()), spacing=(0.8, 0.8, 1.0))
    save(lab, aff, os.path.join(out, "lumbar5", "masks"), "0001")
    print("lumbar5", lab.shape, "%.0f s" % (time.time() - t), flush=True)

    t = time.time()
    cerv = ["C2", "C3", "C4", "C5", "C6", "C7"]
    verts = {lv: P.cervical() for lv in cerv}
    verts["C2"] = P.cervical(dens_r=4.5, dens_h=14.0, dens_y=1.5)
    joints = {lv: P.Joint() for lv in cerv[1:]}
    placed = P.chain(cerv, verts, joints, R0=P.rotation((1.0, 0.0, 0.0), 2.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
    save(lab, aff, os.path.join(out, "cervical", "masks"), "0002")
    print("cervical", lab.shape, "%.0f s" % (time.time() - t), flush=True)

    t = time.time()
    levels = cerv + ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)]
    for lv in levels[6:]:
        verts[lv] = P.Vert()
    joints = {lv: P.Joint() for lv in levels[1:]}
    joints["T1"] = P.Joint(gap=12.0)
    placed = P.chain(levels, verts, joints, R0=P.rotation((1.0, 0.0, 0.0), 2.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 7.0), strict=False)
    save(lab, aff, os.path.join(out, "long", "masks"), "0003")
    print("long", lab.shape, "%.0f s" % (time.time() - t), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
