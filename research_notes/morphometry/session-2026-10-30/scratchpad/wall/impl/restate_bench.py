"""Put the 2.5 mm bench as it now reads into the research note's table, and restate the line on
the inclinations' scatter."""
import sys

PATH = sys.argv[1] + "/research_notes/morphometry/README.md"

OLD_TABLE = """| h_ant | +0.72 mm | 0.87 | 2.25 | 22 |
| h_mid | +0.60 mm | 1.18 | 2.38 | 22 |
| h_post_inset | +0.61 mm | 0.85 | 2.21 | 22 |
| endplate_incl | -0.07 degrees | 1.27 | 3.22 | 22 |
| endplate_lower_incl | +0.15 degrees | 1.50 | 3.52 | 22 |
| disc_h_ant | -0.82 mm | 1.03 | 2.52 | 44 |
| disc_h_mid | -0.58 mm | 0.95 | 2.45 | 44 |
| disc_h_post | -0.59 mm | 0.85 | 2.40 | 44 |
"""
NEW_TABLE = """| h_ant | +0.63 mm | 0.82 | 2.24 | 22 |
| h_mid | +0.50 mm | 1.15 | 2.40 | 22 |
| h_post_inset | +0.54 mm | 0.82 | 2.25 | 22 |
| endplate_incl | -0.21 degrees | 1.38 | 3.05 | 22 |
| endplate_lower_incl | -0.02 degrees | 1.49 | 3.04 | 22 |
| disc_h_ant | -0.37 mm | 0.76 | 2.09 | 44 |
| disc_h_mid | -0.29 mm | 0.79 | 2.30 | 44 |
| disc_h_post | -0.30 mm | 0.80 | 2.20 | 44 |
"""
OLD_LEAD = "On 2.5 mm slices, as most of ENHANCE.PET is cut, `bench --slice 2.5` over 22 tilts and turns of the straight phantom gives:"
NEW_LEAD = ("On 2.5 mm slices, as most of ENHANCE.PET is cut, `bench --slice 2.5` over 22 tilts and turns of the straight "
            "phantom gives, as run on 30 October 2026 with the posterior wall read on the lattice:")
OLD_SCATTER = ("Drawn rim to rim, an end-plate's inclination scatters by 1.3 to 1.5 degrees on these slices, where the "
               "plane through the plate's middle had scattered by 3.2 to 3.5 (largest 9.5).")
NEW_SCATTER = ("Drawn rim to rim and taken against the wall read on the lattice, an end-plate's inclination scatters by "
               "1.4 to 1.5 degrees on these slices (largest 3.05), where against the wall read as each layer's hindmost "
               "voxel it scattered by 1.65 to 1.76 (largest 5.10, the heights and discs as above), and the plane "
               "through the plate's middle had scattered by 3.2 to 3.5 (largest 9.5).")

t = open(PATH).read()
for old, new in ((OLD_TABLE, NEW_TABLE), (OLD_LEAD, NEW_LEAD), (OLD_SCATTER, NEW_SCATTER)):
    assert t.count(old) == 1, old[:50]
    t = t.replace(old, new)
open(PATH, "w").write(t)
print("done")
