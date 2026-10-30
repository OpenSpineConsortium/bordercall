"""Per bin of body.posterior_wall_slope, the least y's excess over the true wall on the cut body and
on the uncut voxels, for the configs named.

  cut_bins.py <cache_dir> <key> [<key> ...]
"""
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import canal_line as CL  # noqa: E402
import coupling as CP  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def bins(v, P, xc, lo, hi):
    mid = P[np.abs(P[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    step = max(v.fz, 0.5)
    out = []
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        if len(layer):
            k = int(np.argmin(layer[:, 1]))
            out.append((z, layer[k, 1], layer[k, 0]))
    return out


for key in sys.argv[2:]:
    with open(os.path.join(sys.argv[1], key + ".pkl"), "rb") as f:
        rec = pickle.load(f)
    v, xc = rec["vert"], rec["xc"]
    B = v.body_pts
    mid = B[np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    cut, unc = bins(v, B, xc, lo, hi), bins(v, CP.uncut(v), xc, lo, hi)
    rings = v.full_rings()
    print("== %s: rings z %.1f to %.1f, posterior window %.1f to %.1f" % (key, rings[0].z, rings[-1].z, lo, hi))
    print("   z     cut   uncut   (excess over the true wall, mm)")
    for (z, y, x), (_, yu, xu) in zip(cut, unc):
        print("   %+5.1f %+5.2f %+5.2f%s" % (z, y - CL.wall_y(rec, x, z), yu - CL.wall_y(rec, xu, z),
                                         "  <- cut" if yu < y - 1e-9 else ""))
