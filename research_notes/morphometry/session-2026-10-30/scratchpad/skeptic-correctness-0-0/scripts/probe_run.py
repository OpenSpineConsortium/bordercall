"""Run the export on the straight phantom as the grid would (run --lines) and list, per level,
which keys hold a finite value in the rows and which have a line in lines.csv."""
import csv
import math
import os
import sys
import tempfile

import nibabel as nib
import numpy as np

from morphometry import __main__ as RUN
from morphometry.tests import phantom as P
from autoanatomist import specs

LEVELS = ["L2", "L3", "L4"]
tmp = tempfile.mkdtemp(dir=sys.argv[1])
masks, out = os.path.join(tmp, "masks"), os.path.join(tmp, "out")
os.makedirs(masks)
lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(masks, "0001.nii.gz"))
RUN.main(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"])
rows = list(csv.DictReader(open(os.path.join(out, "rows.csv"))))
lines = list(csv.DictReader(open(os.path.join(out, "lines.csv"))))
for lv in LEVELS:
    finite = {r["key"] for r in rows if r["level"] == lv and r["value"] not in ("",) and not r["key"].startswith("flag:")
              and math.isfinite(float(r["value"]))}
    drawn = {r["key"] for r in lines if r["level"] == lv and r["part"] == ""}
    print(lv, "finite keys:", len(finite), "keys with a line:", len(drawn))
    print("  SEVEN without a line:", [k for k in specs.SEVEN if k not in drawn])
    print("  SEVEN finite in rows:", {k: next(r["value"] for r in rows if r["level"] == lv and r["key"] == k) for k in specs.SEVEN})
    print("  EXTRA without a line:", [k for k in specs.EXTRA if k not in drawn])
    print("  line keys:", sorted(drawn))
print("tmp", tmp)
