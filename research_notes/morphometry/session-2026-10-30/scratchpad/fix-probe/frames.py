"""The written frame against the line ends on the leaning chain, with the worktree's code."""
import csv, os, sys, tempfile, io, contextlib
import numpy as np
import nibabel as nib
from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
L = ["L2", "L3", "L4"]
j = P.Joint(gap=10.0, sagittal=8.0, coronal=4.0, axial=5.0, slip=4.0)
placed = P.chain(L, {lv: P.Vert() for lv in L}, {lv: j for lv in L[1:]}, R0=P.rotation((1.0, 0.3, 0.0), 12.0))
lab, aff = P.draw(placed, spacing=(0.8, 0.8, 1.0), strict=False)
tmp = tempfile.mkdtemp(); os.makedirs(tmp + "/m")
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), tmp + "/m/0001.nii.gz")
with contextlib.redirect_stdout(io.StringIO()):
    RUN.main(["run", "--masks", tmp + "/m", "--scheme", "verse", "--out", tmp + "/o", "--workers", "1", "--lines"])
lines = list(csv.DictReader(open(tmp + "/o/lines.csv")))
frames = {r["level"]: r for r in csv.DictReader(open(tmp + "/o/frames.csv"))}
img = nib.load(tmp + "/m/0001.nii.gz"); data = np.asarray(img.dataobj)
for lv, f in frames.items():
    o = np.array([float(f["o" + a]) for a in "xyz"])
    R = np.array([[float(f[e + a]) for a in "xyz"] for e in ("ex", "ey", "ez")])
    idx = np.argwhere(data == P.LEVEL_IDS[lv])
    main, dropped = M.main_piece(idx)
    c_all = (idx @ img.affine[:3, :3].T + img.affine[:3, 3]).mean(0)
    c_main = (main @ img.affine[:3, :3].T + img.affine[:3, 3]).mean(0)
    print(lv, "origin - main centroid", np.abs(o - c_main).max().round(5), "- all centroid", np.abs(o - c_all).max().round(5), "dropped", dropped)
    for r in lines:
        if r["level"] != lv or r["part"]:
            continue
        a = R @ (np.array([float(r["a" + x]) for x in "xyz"]) - o)
        b = R @ (np.array([float(r["b" + x]) for x in "xyz"]) - o)
        print("  %-22s a %s b %s" % (r["key"], np.round(a, 3), np.round(b, 3)))
