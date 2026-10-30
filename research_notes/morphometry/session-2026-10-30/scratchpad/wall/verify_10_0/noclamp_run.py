"""Run test modules with the posterior wall's clamp taken out of body.read_wall, and nothing else.

    noclamp_run.py MODE LOG MODULE [MODULE ...]

MODE is clamp (the tree as it stands) or noclamp. The noclamp mutant rewrites the one line of
read_wall that clamps the fitted slope into the parted range, so that b is the fitted slope
whatever the range; the record (parted, free_lo_deg, free_hi_deg, free_deg) is left as the tree
writes it, so the refusal by freedom and the flag are untouched. Every wall reading the run makes
is logged with the fitted and the returned slope."""
import inspect
import json
import math
import sys
import textwrap
import unittest

from morphometry import body as BODY

CLAMP = "b = min(max(float(coef[1]), b_lo), b_hi) if parted else float(coef[1])"
READINGS = []


def without_clamp():
    """read_wall rebuilt from its own source with the clamp's line made the fitted slope."""
    src = textwrap.dedent(inspect.getsource(BODY.read_wall))
    if src.count(CLAMP) != 1:
        raise SystemExit("the clamp's line is not in read_wall once")
    ns = {}
    exec(compile(src.replace(CLAMP, "b = float(coef[1])"), "read_wall_noclamp", "exec"), BODY.__dict__, ns)
    return ns["read_wall"]


def logged(reader):
    def read_wall(v, B, xc):
        slope, info = reader(v, B, xc)
        row = {"level": v.level, "slope_deg": BODY.degrees_of(slope) if math.isfinite(slope) else None}
        for k in ("parted", "fitted_deg", "free_lo_deg", "free_hi_deg", "free_deg", "why"):
            if k in info:
                val = info[k]
                row[k] = val if isinstance(val, (str, bool)) else float(val)
        READINGS.append(row)
        return slope, info
    return read_wall


def main():
    mode, log, modules = sys.argv[1], sys.argv[2], sys.argv[3:]
    if mode not in ("clamp", "noclamp"):
        raise SystemExit("mode is clamp or noclamp")
    reader = without_clamp() if mode == "noclamp" else BODY.read_wall
    BODY.read_wall = logged(reader)
    suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    with open(log, "w") as f:
        json.dump({"mode": mode, "run": result.testsRun, "failures": [str(t) for t, _ in result.failures],
                   "errors": [str(t) for t, _ in result.errors], "readings": READINGS}, f, indent=1)
    print("%s: %d run, %d failed, %d errors, %d wall readings" % (
        mode, result.testsRun, len(result.failures), len(result.errors), len(READINGS)))


if __name__ == "__main__":
    main()
