"""Which of the measures the rows hold a value for get a line, on the test module's phantoms."""
import math
import os
import tempfile

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import test_lines_export as T


def main():
    folder = tempfile.mkdtemp()
    T.masks(folder)
    for study in ("0001", "0002"):
        kept = {}
        rows = M.measure_file(os.path.join(folder, study + ".nii.gz"), "verse", study, keep=kept)
        lines, frames, flags = RUN.study_lines(study, kept)
        drawn = {(r["level"], r["key"]) for r in lines if r["part"] == ""}
        by_level = {}
        for r in rows:
            v = r["value"]
            if r["key"].startswith("flag") or not isinstance(v, float) or not math.isfinite(v):
                continue
            by_level.setdefault(r["level"], set()).add(r["key"])
        for level in sorted(by_level):
            keys = by_level[level]
            with_line = {k for k in keys if (level, k) in drawn}
            print("%s %s: %d keys with a value, %d with a line; e.g. without: %s" % (
                study, level, len(keys), len(with_line), sorted(keys - with_line)[:8]))
        cut = [r for r in rows if r["level"] == "L4"]
        if study == "0002":
            filled = sorted(r["key"] for r in cut if isinstance(r["value"], float) and math.isfinite(r["value"])
                            and not r["key"].startswith("flag"))
            print("0002 L4 keys the rows fill:", len(filled), filled[:20])


if __name__ == "__main__":
    main()
