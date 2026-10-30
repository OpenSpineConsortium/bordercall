"""Probe: a run with the lines, a code change measured by a run without them, then a run with the
lines whose pool breaks after one study. The joined lines.csv then carries the second study's lines
from the first code beside rows from the second, and nothing in lines.csv says so. Phantoms only;
the code change is made in this scratch copy alone."""
import concurrent.futures
import contextlib
import csv
import io
import os
import sys
import tempfile
from concurrent.futures.process import BrokenProcessPool

import nibabel as nib
import numpy as np

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P

LEVELS = ["L2", "L3", "L4"]


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        RUN.main(argv)
    return out.getvalue().strip().replace("\n", " | ")


class BreaksAfterOne:
    """A pool that measures the first study in this process and then dies, as a worker killed for
    memory leaves a ProcessPoolExecutor."""

    def __init__(self, n):
        self.done = 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def submit(self, fn, job):
        self.done += 1
        if self.done > 1:
            raise BrokenProcessPool("a worker died")
        fut = concurrent.futures.Future()
        fut.set_result(fn(job))
        return fut


tmp = tempfile.mkdtemp(dir=sys.argv[1])
masks, out = os.path.join(tmp, "masks"), os.path.join(tmp, "out")
os.makedirs(masks)
lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
for study in ("0001", "0002"):
    nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), os.path.join(masks, study + ".nii.gz"))
base = ["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1"]

print("1, code A with the lines:", run(base + ["--lines"]))
stamp_a = RUN.code_stamp(True)

# code B: the measure moves tp_span by a millimetre; the stamp follows the source files, so it is
# changed on disk too
measure_py = M.__file__
src = open(measure_py).read()
open(measure_py, "w").write(src + "\n# code B\n")
real = M.vertebra_values


def moved(v):
    vals, flags, ped = real(v)
    vals["tp_span"] = vals["tp_span"] + 1.0
    return vals, flags, ped


M.vertebra_values = moved
print("2, code B without the lines:", run(base))
print("3, code B with the lines, the pool breaking after one study:", end=" ")
RUN.ProcessPoolExecutor = BreaksAfterOne
print(run(base + ["--lines"]))
open(measure_py, "w").write(src)

rows = read(os.path.join(out, "rows.csv"))
lines = read(os.path.join(out, "lines.csv"))
code = {r["study"]: r["note"] for r in rows if r["key"] == "code"}
print("stamps in rows.csv:", code, "this run's:", RUN.code_stamp(True) if False else "(code B with the lines)")
for study in ("0001", "0002"):
    row = next(r["value"] for r in rows if (r["study"], r["level"], r["key"]) == (study, "L3", "tp_span"))
    ln = next(r for r in lines if (r["study"], r["level"], r["key"], r["part"]) == (study, "L3", "tp_span", ""))
    print("%s L3 tp_span: rows.csv %s; lines.csv value %s measured %s status %s" % (
        study, row, ln["value"], ln["measured"], ln["status"]))
print("lines.csv columns:", list(lines[0].keys()))
