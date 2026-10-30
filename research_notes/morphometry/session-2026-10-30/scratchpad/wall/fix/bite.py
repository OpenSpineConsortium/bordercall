"""Whether the new wall tests bite: each runs under one undoing of this pass's fixes, and should
fail there.

  bite.py <plain_fit|no_clamp|no_c2|no_set_aside|no_share|old_range|old_range_margin>
"""
import math
import sys
import unittest
from unittest import mock

import numpy as np

from morphometry import body as BODY
from morphometry.tests import test_morphometry as T

NAN = math.nan
ORIGINAL_READ = BODY.read_wall


def plain_fit(e, d, xc):
    return np.linalg.lstsq(BODY.wall_design(e, xc), e[:, 1], rcond=None)[0]


def unclamped(v, B, xc):
    """read_wall with the reading left at the fit's slope, its record as it was."""
    slope, info = ORIGINAL_READ(v, B, xc)
    if math.isfinite(slope):
        slope = math.tan(math.radians(info["fitted_deg"]))
    return slope, info


def window_unbounded(v, B, xc):
    """wall_window with no bound at C2."""
    level = v.level
    try:
        v.level = "C3" if level == "C2" else level
        return ORIGINAL_WINDOW(v, B, xc)
    finally:
        v.level = level


ORIGINAL_WINDOW = BODY.wall_window


def old_range(bone, air, xc):
    """wall_slope_range as it stood before this pass: no widest margin, and HiGHS's status 4 read
    as an unbounded end."""
    A, b = BODY.wall_programme(bone, air, xc)
    from scipy.optimize import linprog
    ends = []
    for c, unbounded in (([0.0, 1.0, 0.0, 0.0], -math.inf), ([0.0, -1.0, 0.0, 0.0], math.inf)):
        res = linprog(c=c, A_ub=A, b_ub=b - BODY.WALL_PART_MM, bounds=[(None, None)] * 4, method="highs")
        if res.status == 2:
            return NAN, NAN
        ends.append(float(res.x[1]) if res.success else unbounded)
    return ends[0], ends[1]


WALL = ["LeanedWall", "SpeckOnTheMargin", "BasivertebralNotch", "DeepNotch", "FreeWall", "DensAtC2"]
CASES = {
    "plain_fit": (mock.patch.object(BODY, "fitted_wall", plain_fit), ["BasivertebralNotch"]),
    "no_clamp": (mock.patch.object(BODY, "read_wall", unclamped), ["LeanedWall"]),
    "no_c2": (mock.patch.object(BODY, "wall_window", window_unbounded), ["DensAtC2"]),
    "no_set_aside": (mock.patch.object(BODY, "WALL_ACROSS_MAX", 0), ["LeanedWall"]),
    "no_share": (mock.patch.object(BODY, "WALL_DROPPED_SHARE", 1.0), ["DeepNotch"]),
    "old_range": (mock.patch.object(BODY, "wall_slope_range", old_range), WALL),
    "old_range_margin": (mock.patch.object(BODY, "wall_slope_range", old_range), ["SpeckOnTheMargin"]),
}


def main():
    patch, classes = CASES[sys.argv[1]]
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(
        "morphometry.tests.test_morphometry." + c) for c in classes)
    with patch:
        result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    print("%s: %d run, %d failed, %d errors" % (sys.argv[1], result.testsRun, len(result.failures),
                                                len(result.errors)))


if __name__ == "__main__":
    main()
