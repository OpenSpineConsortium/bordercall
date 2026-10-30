"""Run the new tests against the base commit's reader (a9f21fd), the tree under base/ with the
new phantom.py and the new test module copied in. With --shim, the names the new tests reach
for (body.posterior_wall, read_wall, degrees_of) are given the old reading, so an accuracy test
fails on its number and not on a missing name, and the old posterior_wall_slope goes through
read_wall, so the refusal test's patch reaches every angle as it does on the new tree.

    base_run.py [--shim] CLASS[.METHOD] ..."""
import math
import sys
import unittest

from morphometry import body as BODY


def shim():
    old = BODY.posterior_wall_slope

    def read_wall(v, B, xc):
        return old(v, B, xc), {}

    BODY.read_wall = read_wall
    BODY.posterior_wall = lambda v, B, xc: BODY.read_wall(v, B, xc)
    BODY.posterior_wall_slope = lambda v, B, xc: BODY.read_wall(v, B, xc)[0]
    BODY.degrees_of = lambda s: math.degrees(math.atan(s))


def main():
    args = sys.argv[1:]
    if args and args[0] == "--shim":
        shim()
        args = args[1:]
    from morphometry.tests import test_morphometry as T
    suite = unittest.TestSuite()
    for name in args:
        if "." in name:
            cls, meth = name.split(".")
            suite.addTest(getattr(T, cls)(meth))
        else:
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(getattr(T, name)))
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
