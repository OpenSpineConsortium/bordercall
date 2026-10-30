"""The export end to end through `python -m morphometry run --lines` on a phantom written as a label
file: which of specs.SEVEN and EXTRA the joined lines.csv holds a line for, level by level, beside
the rows' values."""
import csv
import os
import sys
import tempfile

import nibabel as nib
import numpy as np

sys.path.insert(0, "/home/user/bordercall")

from autoanatomist import specs as S             # noqa: E402
from morphometry import __main__ as RUN          # noqa: E402
from morphometry.tests import phantom as P       # noqa: E402

LEVELS = ["L2", "L3", "L4"]
top = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))
masks, out = os.path.join(top, "masks"), os.path.join(top, "out")
os.makedirs(masks)
lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(masks, "0001.nii.gz"))
RUN.main(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"])


def read(name):
    with open(os.path.join(out, name), newline="") as fh:
        return list(csv.DictReader(fh))


rows, lines = read("rows.csv"), read("lines.csv")
for lv in LEVELS:
    have = {r["key"] for r in lines if r["level"] == lv and r["part"] == ""}
    vals = {r["key"]: r["value"] for r in rows if r["level"] == lv}
    print(lv, "lines:", len(have), "row keys with a value:", sum(1 for k, x in vals.items() if x and not k.startswith("flag:")))
    for k in S.SEVEN + S.EXTRA:
        print("   %-22s row %-10s line %s" % (k, vals.get(k, "-"), "yes" if k in have else "NO"))
print("files:", out)
