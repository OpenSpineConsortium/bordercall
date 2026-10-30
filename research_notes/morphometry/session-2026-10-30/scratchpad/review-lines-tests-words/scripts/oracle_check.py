"""The export read as PR 45 means to read it: behind autoanatomist.oracle's interface in place of
ChordOracle, each line's a and b taken as the first and second point specs.py names, the frame from
frames.csv, then oracle.check over the seven chords and the two record-only ones."""
import contextlib
import csv
import io
import os
import tempfile

import numpy as np

from autoanatomist import oracle as O
from autoanatomist import specs
from morphometry import __main__ as RUN
from morphometry.tests import test_lines_export as T


def main():
    tmp = tempfile.mkdtemp()
    masks, out = os.path.join(tmp, "masks"), os.path.join(tmp, "out")
    os.makedirs(masks)
    T.masks(masks)
    with contextlib.redirect_stdout(io.StringIO()):
        RUN.main(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines",
                  "--studies", "0001"])
    lines = list(csv.DictReader(open(os.path.join(out, "lines.csv"))))
    frames = list(csv.DictReader(open(os.path.join(out, "frames.csv"))))
    f = next(r for r in frames if r["level"] == "L3")
    vec = lambda p: np.array([float(f[p + a]) for a in "xyz"])  # noqa: E731
    reading = O.Reading("L3", 22, O.Frame(vec("o"), vec("ex"), vec("ey"), vec("ez")), vec("o"))
    for r in lines:
        if r["level"] != "L3" or r["part"] or r["key"] not in specs.SPECS:
            continue
        first, second = specs.SPECS[r["key"]].points
        a = np.array([float(r[k]) for k in ("ax", "ay", "az")])
        b = np.array([float(r[k]) for k in ("bx", "by", "bz")])
        reading.measurements[r["key"]] = O.Measurement(r["key"], float(r["value"]), {first: a, second: b})
    keys = list(specs.SEVEN) + list(specs.EXTRA)
    for atol in (1e-6, 1e-3):
        print("oracle.check at atol %g:" % atol)
        for p in O.check(reading, atol=atol, keys=keys):
            print("  " + p)


if __name__ == "__main__":
    main()
