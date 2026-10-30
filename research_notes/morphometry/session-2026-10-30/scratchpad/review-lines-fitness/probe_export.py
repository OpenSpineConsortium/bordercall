"""Run `morphometry run --lines` on a few phantoms and look at what lines.csv and frames.csv give
the latent shape prior's stage 1: counts per level, statuses, join keys, frames."""
import contextlib
import csv
import io
import math
import os
import sys
import tempfile
from collections import Counter, defaultdict

import nibabel as nib
import numpy as np

from morphometry import __main__ as RUN
from morphometry.tests import phantom as P

OUT = sys.argv[1]


def save(lab, aff, folder, study):
    nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(folder, study + ".nii.gz"))


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def build_masks(folder):
    os.makedirs(folder, exist_ok=True)
    lab, aff = P.draw(P.straight(["L1", "L2", "L3", "L4", "L5"], P.Vert()), spacing=(0.8, 0.8, 1.0))
    save(lab, aff, folder, "0001")
    # a lordotic, wedged lumbar column, so the own-axis turn is taken
    wedge = P.lumbar(Ha=31.0)
    placed = P.chain(["L3", "L4", "L5"], {lv: wedge for lv in ("L3", "L4", "L5")},
                     {lv: P.Joint(sagittal=10.0) for lv in ("L4", "L5")}, R0=P.rotation((1.0, 0.0, 0.0), 10.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), strict=False)
    save(lab, aff, folder, "0002")
    levels = ["C2", "C3", "C4", "C5"]
    verts = {"C2": P.cervical(dens_r=4.5, dens_h=14.0, dens_y=1.5), "C3": P.cervical(), "C4": P.cervical(),
             "C5": P.cervical()}
    placed = P.chain(levels, verts, {lv: P.Joint() for lv in levels[1:]}, R0=P.rotation((1.0, 0.0, 0.0), 2.0))
    lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
    save(lab, aff, folder, "0003")


def main():
    masks = os.path.join(OUT, "masks")
    if not os.path.isdir(masks):
        build_masks(masks)
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        RUN.main(["run", "--masks", masks, "--scheme", "verse", "--out", os.path.join(OUT, "run"), "--workers", "3",
                  "--lines"])
    print(said.getvalue())


if __name__ == "__main__":
    main()
