"""Reproduce the landing of the lines export on the three recorded views, as the test's
Lines.setUpClass builds it, and print every place off its level's shadow by more than a pixel,
with the canal line's rows in full."""
import contextlib
import csv
import io
import json
import math
import os
import sys

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


def quiet(run, argv):
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        run(argv)
    return said.getvalue()


def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def support(v, levels):
    shape = (v["view"]["height"], v["view"]["width"])
    return np.logical_or.reduce([FR.unpack(v["supports"][lv], shape) for lv in levels])


def off_px(shadow, u, v):
    r, c = int(math.floor(v)), int(math.floor(u))
    return float(ndimage.distance_transform_edt(~shadow)[r, c])


lab, aff = FR.phantom()
print("phantom is the recorded one:", FR.digest(lab, aff) == RECORD["phantom"]["sha256"])
masks = os.path.join(OUT, "masks")
os.makedirs(masks, exist_ok=True)
mask = os.path.join(masks, "0001.nii.gz")
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), mask)
run = os.path.join(OUT, "run")
quiet(RUN.main, ["run", "--masks", masks, "--scheme", "verse", "--out", run, "--workers", "1", "--lines"])
lines, frames = os.path.join(run, "lines.csv"), os.path.join(run, "frames.csv")
rows = read_csv(lines)
print("rows:", len(rows), "drawn:", sum(r["status"] == "drawn" for r in rows))
for k, v in enumerate(RECORD["views"]):
    path = os.path.join(OUT, "view%d.json" % k)
    with open(path, "w", encoding="ascii") as fh:
        json.dump(dict(v["view"], n_samples=RECORD["n_samples"]), fh)
    out = os.path.join(OUT, "projected%d" % k)
    said = quiet(MV.main, ["project", "--lines", lines, "--frames", frames, "--view", path,
                           "--labels", mask, "--scheme", "verse", "--out", out])
    print("\n== view %d: %s" % (k, v["name"]))
    print("  said:", said.strip())
    got = read_csv(os.path.join(out, "lines2d.csv"))
    for row, line in zip(rows, got):
        assert (row["level"], row["key"], row["part"]) == (line["level"], line["key"], line["part"])
        shadow = support(v, row["level"].split("-"))
        # the test's midpoint: the middle of the two projected ends; the command's: the projected middle
        mid2d = 0.5 * (np.array([float(line["au"]), float(line["av"])]) + np.array([float(line["bu"]), float(line["bv"])]))
        fx = {"a": off_px(shadow, float(line["au"]), float(line["av"])),
              "b": off_px(shadow, float(line["bu"]), float(line["bv"])),
              "mid2d": off_px(shadow, *mid2d)}
        cmd = {e: line[e + "_off_px"] for e in ("a", "b", "mid")}
        far = any(float(x) > 1.0 for x in cmd.values() if x != "") or any(x > 1.0 for x in fx.values())
        if row["key"] == "canal_ap_lateral_film" or far:
            print("  %-6s %-24s %-14s a=%-8s(%s) b=%-8s(%s) mid=%-8s mid2d_on_flexray=%.2f  [a_end=%s b_end=%s]" % (
                row["level"], row["key"], row["part"] or "-", cmd["a"], line["a_end"], cmd["b"], line["b_end"],
                cmd["mid"], fx["mid2d"], line["a_end"], line["b_end"]))
            # the command's numbers against FleXray's own support
            for e in "ab":
                if cmd[e] != "" and float(cmd[e]) != fx[e]:
                    print("    MISMATCH command vs FleXray support at", e, cmd[e], fx[e])
