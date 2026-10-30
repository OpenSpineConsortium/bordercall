"""A test the module lacks: a study written by an older code is measured again with the lines, and the
job dies after the first file of the new set lands. With the lines written before the rows the study
stays not current; with the rows first (mutant M01) it reads as current over the older lines."""
import os
import tempfile
from unittest import mock

from morphometry import __main__ as RUN
from morphometry.tests import phantom as P
from morphometry.tests import test_lines_export as T


def main():
    top = tempfile.mkdtemp()
    for sub in ("rows", "lines", "frames"):
        os.makedirs(os.path.join(top, sub))
    lab, aff = P.draw(P.straight(T.LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
    path = T.save(lab, aff, top, "0001")
    out = os.path.join(top, "rows", "0001.csv")
    RUN.one_study((path, "verse", "0001", out, "older-code", True))
    lines_path = RUN.side_paths(out)[0]
    with open(lines_path, "a") as fh:            # what the older code drew, told apart by a marker
        fh.write("0001,L3,stale,,,,,,,,,,,,,\n")
    real = RUN.write_atomic
    calls = []

    def dies_after_first(rows, p, fields=RUN.FIELDS):
        calls.append(os.path.relpath(p, top))
        if len(calls) > 1:
            raise KeyboardInterrupt("the job is killed")   # the worker dies after the first file lands
        return real(rows, p, fields)

    with mock.patch.object(RUN, "write_atomic", dies_after_first):
        try:
            RUN.one_study((path, "verse", "0001", out, "newer-code", True))
        except KeyboardInterrupt:
            pass
    stale = "stale" in open(lines_path).read()
    print("files written before the kill:", calls[:1], "| lines still the older code's:", stale,
          "| current for the newer code:", RUN.current(out, "newer-code", True))


if __name__ == "__main__":
    main()
