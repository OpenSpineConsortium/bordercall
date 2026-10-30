"""Probe: which of a vertebra's measured keys get a line in the export, on the straight phantom,
and whether the seven chords of autoanatomist.specs.SEVEN are among them. Phantoms only."""
import math

import numpy as np

from autoanatomist.specs import SEVEN
from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]

lab, aff = P.draw(P.straight(LEVELS, P.Vert()), spacing=(0.8, 0.8, 1.0))
kept = {}
M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, "keys", pelvis=False,
                 keep=kept)
lines, frames, flags = RUN.study_lines("keys", kept)
vals = kept["values"]["L3"]
finite = sorted(k for k, x in vals.items() if isinstance(x, float) and math.isfinite(x))
drawn = sorted({r["key"] for r in lines if r["level"] == "L3" and r["part"] == ""})
print("L3 keys with a finite value:", len(finite))
print("L3 keys with a line:", len(drawn), drawn)
print("SEVEN:", SEVEN)
print("SEVEN without a line:", [k for k in SEVEN if k not in drawn])
print("SEVEN values at L3:", {k: round(vals[k], 3) for k in SEVEN})
print("finite keys without a line:", [k for k in finite if k not in drawn])
print("flags:", flags)
