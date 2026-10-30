"""Run morphometry's phantom tests with body.posterior_wall_slope swapped for candidate A in
this process only (no file of bordercall is changed). A refusal reads 0.0, as the reader does
now where it cannot read. Usage: run_tests.py candidate|current Class [Class ...]"""
import math, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from morphometry import body as BODY
import cand as C

def swapped(v, B, xc):
    b, info = C.slope(v, B, xc)
    return b if math.isfinite(b) else 0.0

if sys.argv[1] == "candidate":
    BODY.posterior_wall_slope = swapped
from morphometry.tests import test_morphometry as T
suite = unittest.TestSuite()
for name in sys.argv[2:]:
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(T, name)))
unittest.TextTestRunner(verbosity=2).run(suite)
