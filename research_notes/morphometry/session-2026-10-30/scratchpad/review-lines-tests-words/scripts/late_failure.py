"""A test the module lacks: the measuring fails after measure_volume has filled `keep` (here in the
column's regional measures, which run after it, as the pelvis does), so the study's rows hold only its
error; its lines and frames should then be empty, as they are when the failure comes first."""
import csv
import os
import tempfile
from unittest import mock

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphometry.tests import test_lines_export as T


def main():
    top = tempfile.mkdtemp()
    for sub in ("rows", "lines", "frames"):
        os.makedirs(os.path.join(top, sub))
    lab, aff = P.draw(P.straight(T.LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
    path = T.save(lab, aff, top, "0001")
    out = os.path.join(top, "rows", "0001.csv")
    with mock.patch.object(M.COL, "regional", side_effect=RuntimeError("late")):
        RUN.one_study((path, "verse", "0001", out, RUN.code_stamp(True), True))
    lines_path, frames_path = RUN.side_paths(out)
    n_lines = len(list(csv.DictReader(open(lines_path))))
    n_frames = len(list(csv.DictReader(open(frames_path))))
    errors = [r["note"] for r in csv.DictReader(open(out)) if r["key"] == "flag:error"]
    print("rows' error:", errors, "| lines rows:", n_lines, "| frames rows:", n_frames)


if __name__ == "__main__":
    main()
