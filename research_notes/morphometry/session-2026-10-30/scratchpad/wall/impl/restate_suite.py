"""Restate the research note's line on the suite: its phantoms, its bounds and its count."""
import sys

PATH = sys.argv[1] + "/research_notes/morphometry/README.md"
OLD = ("a pelvis, thick slices, and two masks a segmenter gets wrong (two labels swapped, a column cropped). The 20 "
       "tests require linear measures within 0.75 mm, angles within 1.5 degrees (3 for the spinous and facet angles), "
       "areas within 4 per cent and the slip within 1.5 mm; all 20 pass (`python -m unittest "
       "morphometry.tests.test_morphometry`, 281 s).")
NEW = ("a pelvis, thick slices, a posterior wall leaned 5 degrees on a grid 2 degrees off the vertebra's frame, a "
       "basivertebral notch, and two masks a segmenter gets wrong (two labels swapped, a column cropped). The 31 "
       "tests require linear measures within 0.75 mm, angles within 1.5 degrees (3 for the spinous and facet angles), "
       "areas within 4 per cent, the slip within 1.5 mm and the posterior wall's slope within 0.5 degrees; all 31 "
       "pass (`python -m unittest morphometry.tests.test_morphometry`, 448 s on 30 October 2026, beside other runs).")
t = open(PATH).read()
assert t.count(OLD) == 1
open(PATH, "w").write(t.replace(OLD, NEW))
print("done")
