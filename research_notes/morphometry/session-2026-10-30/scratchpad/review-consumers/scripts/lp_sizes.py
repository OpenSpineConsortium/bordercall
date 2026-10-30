"""The largest linear programme the new engine builds over one phantom study, by constraint count,
and whether the least-crossing programme (with its dense n by n identity) ran."""
import sys
sys.path.insert(0, sys.argv[1])
import numpy as np
from morphometry import pedicle as PED, body as BODY, measure as M
sizes = {"parting": [], "dense": [], "wall": []}
real_parting, real_range = PED.parting, BODY.wall_slope_range
def parting(y, across, z, bone, top):
    sizes["parting"].append(len(y))
    got = real_parting(y, across, z, bone, top)
    if got is not None and got["margin"] < 0:
        sizes["dense"].append(len(y))
    return got
def wall_range(bone, air, xc):
    sizes["wall"].append(len(bone) + len(air))
    return real_range(bone, air, xc)
PED.parting, BODY.wall_slope_range = parting, wall_range
M.measure_file(sys.argv[2], "enhance", "x")
for k, v in sizes.items():
    print(k, "calls", len(v), "largest", max(v) if v else 0)
