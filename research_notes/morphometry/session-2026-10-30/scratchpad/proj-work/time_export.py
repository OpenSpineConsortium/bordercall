"""Time one lines export of the straight L2 to L4 phantom, as the export tests make it."""
import os, sys, time, tempfile, contextlib, io, csv
sys.path.insert(0, "/home/user/bordercall")
import nibabel as nib
import numpy as np
from morphometry import __main__ as RUN
from morphometry.tests import phantom as P

t0 = time.time()
lab, aff = P.draw(P.straight(["L2", "L3", "L4"], P.Vert()), spacing=(0.8, 0.8, 1.0))
t1 = time.time()
print("phantom", lab.shape, lab.dtype, np.unique(lab), "%.1f s" % (t1 - t0))
print(np.round(aff, 4))
tmp = tempfile.mkdtemp()
os.makedirs(os.path.join(tmp, "masks"))
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(tmp, "masks", "0001.nii.gz"))
out = io.StringIO()
with contextlib.redirect_stdout(out):
    RUN.main(["run", "--masks", os.path.join(tmp, "masks"), "--scheme", "verse", "--out", os.path.join(tmp, "out"),
              "--workers", "1", "--lines"])
t2 = time.time()
rows = list(csv.DictReader(open(os.path.join(tmp, "out", "lines.csv"))))
print("export %.1f s, %d line rows, %d drawn" % (t2 - t1, len(rows), sum(r["status"] == "drawn" for r in rows)))
print(tmp)
