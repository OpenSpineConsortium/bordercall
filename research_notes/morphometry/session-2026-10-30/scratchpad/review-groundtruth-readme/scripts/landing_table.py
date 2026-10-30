"""Every drawn line's ends and midpoint against FleXray's recorded shadow of its level, in the
three recorded views, as the tests set them up (morphoview/tests/test_projection.py, Lines)."""
import contextlib
import csv
import io
import json
import math
import os
import sys
import tempfile

import nibabel as nib
import numpy as np
from scipy import ndimage

from morphometry import __main__ as RUN
from morphoview import __main__ as MV
from morphoview import projection as PJ
from morphoview.tests import flexray_record as FR

OUT = sys.argv[1]
with open(FR.FIXTURE, encoding="ascii") as fh:
    RECORD = json.load(fh)


def support(v, levels):
    shape = (v["view"]["height"], v["view"]["width"])
    return np.logical_or.reduce([FR.unpack(v["supports"][lv], shape) for lv in levels])


def off_px(shadow, u, v):
    r, c = int(math.floor(v)), int(math.floor(u))
    return float(ndimage.distance_transform_edt(~shadow)[r, c])


def quiet(run, argv):
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        run(argv)
    return said.getvalue()


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


lab, aff = FR.phantom()
print("phantom is the recorded one:", FR.digest(lab, aff) == RECORD["phantom"]["sha256"])
os.makedirs(OUT, exist_ok=True)
masks = os.path.join(OUT, "masks")
os.makedirs(masks, exist_ok=True)
mask = os.path.join(masks, "0001.nii.gz")
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), mask)
run = os.path.join(OUT, "run")
quiet(RUN.main, ["run", "--masks", masks, "--scheme", "verse", "--out", run, "--workers", "1", "--lines"])
lines = os.path.join(run, "lines.csv")
frames = os.path.join(run, "frames.csv")
rows = read_csv(lines)
table = []
for k, v in enumerate(RECORD["views"]):
    path = os.path.join(OUT, "view%d.json" % k)
    with open(path, "w", encoding="ascii") as fh:
        json.dump(dict(v["view"], n_samples=RECORD["n_samples"]), fh)
    out = os.path.join(OUT, "projected%d" % k)
    quiet(MV.main, ["project", "--lines", lines, "--frames", frames, "--view", path,
                    "--labels", mask, "--scheme", "verse", "--out", out])
    got = read_csv(os.path.join(out, "lines2d.csv"))
    for row, line in zip(rows, got):
        shadow = support(v, row["level"].split("-"))
        a = np.array([float(line["au"]), float(line["av"])])
        b = np.array([float(line["bu"]), float(line["bv"])])
        mid2d = 0.5 * (a + b)
        table.append({"view": v["name"], "level": row["level"], "key": row["key"], "part": row["part"],
                      "a_end": row["a_end"], "b_end": row["b_end"],
                      "a_off": off_px(shadow, *a), "b_off": off_px(shadow, *b),
                      "mid2d_off": off_px(shadow, *mid2d),
                      "cmd_a": line["a_off_px"], "cmd_b": line["b_off_px"], "cmd_mid": line["mid_off_px"]})
with open(os.path.join(OUT, "landing.json"), "w") as fh:
    json.dump(table, fh, indent=1)
print("rows", len(rows), "table", len(table))
for t in table:
    if t["key"] == "canal_ap_lateral_film" or max(t["a_off"], t["b_off"]) > 1.0 or float(t["cmd_mid"] or 0) > 1.0 \
            or t["mid2d_off"] > 1.0:
        print("%-45s %-6s %-22s %-14s a=%-10s b=%-10s a_off=%5.2f b_off=%5.2f mid2d=%5.2f cmd_mid=%s" % (
            t["view"][:45], t["level"], t["key"], t["part"], t["a_end"], t["b_end"], t["a_off"], t["b_off"],
            t["mid2d_off"], t["cmd_mid"]))
