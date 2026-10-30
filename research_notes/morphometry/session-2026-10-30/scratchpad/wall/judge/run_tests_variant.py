"""morphometry's phantom tests with body.posterior_wall_slope swapped, in this process only, for
the judged reader (variants.A_lts); a refusal reads NAN or 0.0 as the first argument says.
Usage: run_tests_variant.py nan|zero|current Class [Class ...]"""
import math, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from morphometry import body as BODY
import variants as V
import proposed as PR

def swapped(v, B, xc):
    b, info = PR.posterior_wall(v, B, xc)
    if not math.isfinite(b):
        print("REFUSED", v.level, info.get("why"), flush=True)
        return b if sys.argv[1] == "nan" else 0.0
    return b

if sys.argv[1] != "current":
    BODY.posterior_wall_slope = swapped
from morphometry.tests import test_morphometry as T
suite = unittest.TestSuite()
for name in sys.argv[2:]:
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(getattr(T, name)))
unittest.TextTestRunner(verbosity=2).run(suite)
