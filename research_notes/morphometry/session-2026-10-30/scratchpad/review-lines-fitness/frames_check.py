"""The frames file against the plan's words and the oracle interface the plan puts it behind:
is the written frame the turned one, does x point to the patient's right, do the files pass
autoanatomist.oracle.check, and which way round are the ends."""
import csv
import math
import os
import sys

import nibabel as nib
import numpy as np

from autoanatomist import oracle as O
from autoanatomist import specs as S
from morphometry.tests import phantom as P
from scanimport import geometry as G

RUN = sys.argv[1]
MASKS = sys.argv[2]


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


lines = read(os.path.join(RUN, "lines.csv"))
frames = {(f["study"], f["level"]): f for f in read(os.path.join(RUN, "frames.csv"))}
rows = read(os.path.join(RUN, "rows.csv"))
offset = {(r["study"], r["level"]): r["value"] for r in rows if r["key"] == "axis_offset"}


def frame(study, level):
    f = frames[(study, level)]
    vec = lambda p: np.array([float(f[p + a]) for a in "xyz"])  # noqa: E731
    return O.Frame(vec("o"), vec("ex"), vec("ey"), vec("ez"))


def ends(r):
    return (np.array([float(r[k]) for k in ("ax", "ay", "az")]), np.array([float(r[k]) for k in ("bx", "by", "bz")]))


# 1. the written z against the line through the neighbours' centroids, beside axis_offset
lab = np.asarray(nib.load(os.path.join(MASKS, "0002.nii.gz")).dataobj)
aff = nib.load(os.path.join(MASKS, "0002.nii.gz")).affine
grid = G.VoxelGrid(aff, lab.shape)
cents = {lv: grid.world(np.argwhere(lab == P.LEVEL_IDS[lv]).astype(float)).mean(0) for lv in ("L3", "L4", "L5")}
column = G.unit(cents["L3"] - cents["L5"])
f = frame("0002", "L4")
print("0002 L4: written ez to the column line through L3 and L5's centroids %.3f deg; axis_offset row %s"
      % (math.degrees(math.acos(min(1, abs(float(f.ez @ column))))), offset[("0002", "L4")]))
print("0002 L4: origin minus the label's centroid %.2e mm" % np.abs(f.origin - cents["L4"]).max())
for key in ("h_mid", "h_ant"):
    r = next(r for r in lines if (r["study"], r["level"], r["key"], r["part"]) == ("0002", "L4", key, ""))
    a, b = ends(r)
    d = G.unit(b - a)
    print("  %s along the written ez %.5f, along the column line %.5f" % (key, abs(d @ f.ez), abs(d @ column)))
for study, level in sorted(frames):
    f = frame(study, level)
    print(study, level, "ex . world +x (patient's right) %.3f" % f.ex[0])

# 2. the files behind the oracle interface: a frame's orthonormality and a chord's value
f = frame("0001", "L3")
A = f.axes
print("0001 L3 frame: max |A'A - I| %.2e against oracle.FRAME_ATOL %.0e -> %s"
      % (np.abs(A.T @ A - np.eye(3)).max(), O.FRAME_ATOL,
         "passes" if np.allclose(A.T @ A, np.eye(3), rtol=0.0, atol=O.FRAME_ATOL) else "fails"))
reading = O.Reading(level="L3", label=22, frame=f, centre=f.origin)
for key in ("endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "tp_span", "spinous_length"):
    r = next(r for r in lines if (r["study"], r["level"], r["key"], r["part"]) == ("0001", "L3", key, ""))
    a, b = ends(r)
    names = S.SPECS[key].points
    reading.measurements[key] = O.Measurement(key, float(r["measured"]), {names[0]: a, names[1]: b}, "")
    la, lb = f.local(a[None])[0], f.local(b[None])[0]
    print("%-22s a local %s b local %s spec ends %s" % (key, np.round(la, 1), np.round(lb, 1), names))
problems = O.check(reading)
print("oracle.check on the six lines mapped a -> spec's first end:")
for p in problems:
    print("   ", p)
missing = [k for k in S.SEVEN if not any((r["study"], r["level"], r["key"]) == ("0001", "L3", k) for r in lines)]
print("of specs.SEVEN, no line in lines.csv at 0001 L3:", missing)
