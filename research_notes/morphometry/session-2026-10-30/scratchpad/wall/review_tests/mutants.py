"""Run named test classes of morphometry.tests.test_morphometry with one part of the new wall
reader taken out (a mutant), to see which test, if any, notices; and log every wall reading the
run makes, to see which of the reader's paths the run reaches.

    mutants.py MUTANT LOG CLASS [CLASS ...]

MUTANT is one of none, noclamp, nolts, nobiweight, noflag, norefuse, stalecache, nodigit, or
several joined by +."""
import json
import math
import sys
import unittest

import numpy as np

from morphometry import body as BODY

ORIG = {k: getattr(BODY, k) for k in ("wall_freedom", "trimmed_start", "biweight", "kept_wall", "read_wall")}
READINGS = []


def no_clamp(bone, d, coef, xc):
    b_lo, b_hi, _ = ORIG["wall_freedom"](bone, d, coef, xc)
    return b_lo, b_hi, False


def plain_start(X, y, z):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def no_reweight(X, y, coef, scale):
    return coef


def stale(v, B, xc):
    kept = getattr(v, "_posterior_wall", None)
    return None if kept is None else kept[4]


def logged_read_wall(v, B, xc):
    slope, info = ORIG["read_wall"](v, B, xc)
    row = {"level": v.level, "slope_deg": BODY.degrees_of(slope) if math.isfinite(slope) else None}
    for k, val in info.items():
        row[k] = val if isinstance(val, (str, bool, int)) else (float(val) if math.isfinite(float(val)) else str(val))
    if "fitted_deg" in info and math.isfinite(slope):
        row["clamp_moved_deg"] = BODY.degrees_of(slope) - info["fitted_deg"]
    READINGS.append(row)
    return slope, info


def apply(mutants):
    for mutant in mutants.split("+"):
        apply_one(mutant)
    BODY.read_wall = logged_read_wall


def no_digitisation(bone, d, coef, xc):
    raise RuntimeError("clean_digitisation reached")


def apply_one(mutant):
    if mutant == "nodigit":
        BODY.clean_digitisation = no_digitisation
    elif mutant == "noclamp":
        BODY.wall_freedom = no_clamp
    elif mutant == "nolts":
        BODY.trimmed_start = plain_start
        BODY.biweight = no_reweight
    elif mutant == "nobiweight":
        BODY.biweight = no_reweight
    elif mutant == "noflag":
        BODY.WALL_FREE_FLAG_DEG = math.inf
    elif mutant == "norefuse":
        BODY.WALL_FREEDOM_DEG = math.inf
    elif mutant == "stalecache":
        BODY.kept_wall = stale
    elif mutant != "none":
        raise SystemExit("no such mutant: " + mutant)


def main():
    mutant, log, classes = sys.argv[1], sys.argv[2], sys.argv[3:]
    apply(mutant)
    from morphometry.tests import test_morphometry as T
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in classes:
        if "." in name:
            cls, meth = name.split(".")
            suite.addTest(getattr(T, cls)(meth))
        else:
            suite.addTests(loader.loadTestsFromTestCase(getattr(T, name)))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    with open(log, "w") as f:
        json.dump({"mutant": mutant, "failures": [str(t) for t, _ in result.failures],
                   "errors": [str(t) for t, _ in result.errors], "readings": READINGS}, f, indent=1)
    print("mutant %s: %d run, %d failed, %d errors, %d wall readings" % (
        mutant, result.testsRun, len(result.failures), len(result.errors), len(READINGS)))


if __name__ == "__main__":
    main()
