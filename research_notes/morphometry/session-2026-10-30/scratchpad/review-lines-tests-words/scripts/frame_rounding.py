"""How far the frames as frames.csv writes them (four places) are from orthonormal, against the 1e-6
autoanatomist.oracle.FRAME_ATOL allows, and how far a 50 mm end moves when taken into the written frame."""
import os
import tempfile

import numpy as np

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import test_lines_export as T


def main():
    folder = tempfile.mkdtemp()
    T.masks(folder)
    kept = {}
    M.measure_file(os.path.join(folder, "0001.nii.gz"), "verse", "0001", keep=kept)
    for lv, v in kept["verts"].items():
        row = RUN.frame_row("0001", lv, v.frame)
        written = {k: float(RUN.number(x)) for k, x in row.items() if k not in ("study", "level")}
        R = np.array([[written[p + a] for a in "xyz"] for p in ("ex", "ey", "ez")])
        exact = np.stack([v.frame.ex, v.frame.ey, v.frame.ez])
        p = v.frame.origin + 50.0 * v.frame.ez
        moved = np.linalg.norm(R @ (p - v.frame.origin) - exact @ (p - v.frame.origin))
        print("%s: max |R R^T - I| = %.2e, |det - 1| = %.2e, a point 50 mm up the axis moves %.4f mm in the written frame"
              % (lv, np.abs(R @ R.T - np.eye(3)).max(), abs(np.linalg.det(R) - 1), moved))


if __name__ == "__main__":
    main()
