"""Probe: the whole `run --lines` path on the pelvis phantom under scheme enhance, written as a
label file: the pelvis rows are there, every vertebra's and disc's line is drawn and holds the
row's value, and every measured vertebra has a frame. Phantoms only."""
import collections
import contextlib
import csv
import io
import os
import sys
import tempfile

import nibabel as nib
import numpy as np

from morphometry import __main__ as RUN
from morphometry.tests import phantom as P


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


tmp = tempfile.mkdtemp(dir=sys.argv[1])
masks, out = os.path.join(tmp, "masks"), os.path.join(tmp, "out")
os.makedirs(masks)
placed = P.straight(["L4", "L5"])
lab, aff = P.draw(placed, spacing=(1.0, 1.0, 1.0), pelvis=P.Pelvis())
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(masks, "0001.nii.gz"))
said = io.StringIO()
with contextlib.redirect_stdout(said):
    RUN.main(["run", "--masks", masks, "--scheme", "enhance", "--out", out, "--workers", "1", "--lines"])
print(said.getvalue().strip())
rows = read(os.path.join(out, "rows.csv"))
lines = read(os.path.join(out, "lines.csv"))
frames = read(os.path.join(out, "frames.csv"))
value = {(r["level"], r["key"]): r["value"] for r in rows}
print("pelvis rows:", {k: value.get(("pelvis", k)) for k in ("pelvic_incidence", "lowest_lumbar", "sacral_slope_supine")})
print("column rows:", {r["key"]: r["value"] for r in rows if r["level"] == "column"})
print("flags:", [(r["level"], r["key"], r["note"][:60]) for r in rows if r["key"].startswith("flag")])
status = collections.Counter((r["level"], r["status"].split(":")[0]) for r in lines if r["part"] == "")
print("statuses:", dict(status))
bad = [(r["level"], r["key"], r["measured"], value.get((r["level"], r["key"]))) for r in lines
       if r["part"] == "" and r["measured"] != value.get((r["level"], r["key"]), "")]
print("measured not the row's value:", bad)
print("frames:", [(f["level"], f["ox"], f["oy"], f["oz"]) for f in frames])
