"""The same timing on the Resuming and Failing phantom (L2 to L4 at 0.86 by 0.86 by 2.5 mm)."""
import os
import sys
import tempfile
import time

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
from morphometry.tests import test_lines_export as T

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import draw_again  # noqa: E402


def main():
    folder = tempfile.mkdtemp()
    lab, aff = P.draw(P.straight(T.LEVELS, P.Vert()), spacing=(0.86, 0.86, 2.5))
    path = T.save(lab, aff, folder, "0001")
    for rep in range(2):
        t0 = time.perf_counter()
        M.measure_file(path, "verse", "0001")
        t_plain = time.perf_counter() - t0
        kept = {}
        M.measure_file(path, "verse", "0001", keep=kept)
        t0 = time.perf_counter()
        RUN.study_lines("0001", kept)
        t_new = time.perf_counter() - t0
        t0 = time.perf_counter()
        draw_again(kept)
        t_old = time.perf_counter() - t0
        print("thick rep %d: measure %.2f s, drawing now %.2f s, drawing with one_side again %.2f s; now/measure %.1f%%"
              % (rep, t_plain, t_new, t_old, 100 * t_new / t_plain), flush=True)


if __name__ == "__main__":
    main()
