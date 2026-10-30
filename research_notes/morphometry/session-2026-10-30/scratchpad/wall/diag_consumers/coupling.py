"""Whether body.posterior_wall_slope reads the canal line's cut instead of the wall.

The body B is cut from the arch along the canal's wall line (anatomy.body_in_front: voxels with y
measured from the line beyond wall_y0). Where that line leans off the true wall the cut can pass
in front of the wall's outermost voxel centres over part of the height, and the least y of a bin
is then the cut's, not the wall's. Here the reader is run on the cut body as it stands and on the
same vertebra's voxels in front of the canal's middle, uncut (as column.wall_corner takes them),
and each bin's least y is counted as on the cut where it lies within a quarter of a pixel of the
cut plane while the uncut voxels hold a point further back in that bin.

  coupling.py <cache_dir> <out.json>
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import score as SC  # noqa: E402
from morphometry import anatomy as A  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def uncut(v):
    ap = float(np.median([s.ap for s in v.full_rings()]))
    near = A.square_to_wall(v, v.loc)[:, 1] > v.wall_y0 - 0.5 * ap
    return v.loc[near]


def cut_bins(v, B, U, xc):
    mid = B[np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    umid = U[np.abs(U[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    n, on_cut = 0, 0
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        ul = umid[np.abs(umid[:, 2] - z) <= 0.5 * step]
        if not len(layer):
            continue
        n += 1
        if ul[:, 1].min() < layer[:, 1].min() - 1e-9:
            on_cut += 1
    return n, on_cut


def main():
    cache, out = sys.argv[1], sys.argv[2]
    rows = []
    for key, rec in SC.records(cache):
        v = rec["vert"]
        truth = SC.wall_truth_in_frame(rec)
        B, xc = v.body_pts, rec["xc"]
        U = uncut(v)
        cut = math.degrees(math.atan(BODY.posterior_wall_slope(v, B, xc)))
        unc = math.degrees(math.atan(BODY.posterior_wall_slope(v, U, xc)))
        n, on_cut = cut_bins(v, B, U, xc)
        canal = math.degrees(math.atan(v.wall_slope))
        rows.append({"key": key, "grid": rec["cfg"][2], "spacing": rec["cfg"][5], "lean": rec["cfg"][1],
                     "truth": truth, "canal_err": canal - truth, "post_cut_err": cut - truth,
                     "post_uncut_err": unc - truth, "bins": n, "bins_on_cut": on_cut})
        print("%-40s canal err %+6.2f | post on cut body %+6.2f, uncut %+6.2f | bins %2d, %2d set by the cut" % (
            key, canal - truth, cut - truth, unc - truth, n, on_cut), flush=True)
    for sp in ("thin", "thick"):
        sel = [r for r in rows if r["spacing"] == sp]
        print("== %s: |post err| max on cut body %.2f, uncut %.2f; configs with a bin set by the cut %d of %d" % (
            sp, max(abs(r["post_cut_err"]) for r in sel), max(abs(r["post_uncut_err"]) for r in sel),
            sum(r["bins_on_cut"] > 0 for r in sel), len(sel)))
        for g in sorted({r["grid"] for r in sel}):
            gs = [r for r in sel if r["grid"] == g]
            print("   %-8s cut %5.2f uncut %5.2f canal %5.2f" % (
                g, max(abs(r["post_cut_err"]) for r in gs), max(abs(r["post_uncut_err"]) for r in gs),
                max(abs(r["canal_err"]) for r in gs)))
    with open(out, "w") as f:
        json.dump(rows, f, indent=1, default=float)


if __name__ == "__main__":
    main()
