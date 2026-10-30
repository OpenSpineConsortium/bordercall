"""Time the measuring and the drawing on the test module's phantoms: the drawing as one_study
runs it (the measure's own pedicle reading), the drawing with pedicle.one_side read again, and
the measuring alone, so the commit's "8 of 11 s" and "about 5 per cent" can be set beside them."""
import os
import sys
import tempfile
import time

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import test_lines_export as T
from morphoview import lines as LN


def draw_again(kept):
    """The drawing as it was before the commit: every vertebra's lines with one_side read again."""
    out = []
    for lv, v in kept["verts"].items():
        out += LN.checked(LN.vertebra_lines(v, kept["peds"][lv]), kept["values"][lv])
    for (a, b), vals in kept["discs"].items():
        out += LN.checked(LN.discs(kept["verts"][a], kept["verts"][b]), vals)
    return out


def main():
    folder = tempfile.mkdtemp()
    T.masks(folder)
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    for study in ("0001", "0002"):
        path = os.path.join(folder, study + ".nii.gz")
        for rep in range(reps):
            t0 = time.perf_counter()
            M.measure_file(path, "verse", study)
            t_plain = time.perf_counter() - t0
            kept = {}
            t0 = time.perf_counter()
            M.measure_file(path, "verse", study, keep=kept)
            t_keep = time.perf_counter() - t0
            t0 = time.perf_counter()
            RUN.study_lines(study, kept)
            t_new = time.perf_counter() - t0
            t0 = time.perf_counter()
            draw_again(kept)
            t_old = time.perf_counter() - t0
            print("%s rep %d: measure %.2f s, measure with keep %.2f s, drawing now %.2f s, drawing with one_side "
                  "again %.2f s; drawing now / measuring = %.1f%%; saved %.2f of %.2f s" %
                  (study, rep, t_plain, t_keep, t_new, t_old, 100 * t_new / t_plain, t_old - t_new, t_old), flush=True)


if __name__ == "__main__":
    main()
