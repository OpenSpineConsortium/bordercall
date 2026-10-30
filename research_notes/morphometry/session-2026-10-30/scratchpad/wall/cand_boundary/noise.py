"""How C and its riser variant hold up when the wall's boundary voxels are jittered by one voxel.

  PYTHONPATH=<bordercall> python noise.py ../cache <p> <seeds>

Each bone voxel on the posterior wall (its neighbour behind it along the axis nearest y is not
bone) is dropped with probability p, and each canal voxel just behind the wall is added with
probability p, independently, near the midline band and within half the canal's depth of
the canal's wall line (so the arch's own back is left alone); the label's box, idx and loc are made
again, B keeps the body's voxels that remain plus those added. A phantom-only stand-in for a
segmentation's ragged edge, which is correlated in a real mask and is not here.
"""
import copy
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S          # noqa: E402
import cand as C           # noqa: E402
import cand_crack as K     # noqa: E402
from morphometry import body as BODY  # noqa: E402


def jittered(v, xc, p, rng):
    step, _, step_f = C.nearest_step(v)
    off_line = v.loc[:, 1] - (v.wall_y0 + v.wall_slope * (v.loc[:, 2] - v.wall_z0))
    near = (np.abs(v.loc[:, 0] - xc) <= C.ACROSS_HALF_MM + 2.0) & (np.abs(off_line) <= C.canal_half_depth(v))
    edge = near & ~v.is_bone(v.idx + step)
    drop = edge & (rng.random(len(v.idx)) < p)
    behind = v.idx[edge] + step
    add = behind[rng.random(len(behind)) < p]
    w = copy.copy(v)
    w.idx = np.concatenate([v.idx[~drop], add])
    w.loc = w.frame.local(w.grid.world(w.idx.astype(float)))
    w.body = np.concatenate([v.body[~drop], np.ones(len(add), bool)])
    w._box = None
    return w


def main():
    cache, p, seeds = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
    fns = {"C": C.slope, "C+risers": K.slope, "current": BODY.posterior_wall_slope}
    errs = {k: {"thin": [], "thick": []} for k in fns}
    for key, rec in S.records(cache):
        truth = S.wall_truth_in_frame(rec)
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            w = jittered(rec["vert"], rec["xc"], p, rng)
            B = w.body_pts
            for name, fn in fns.items():
                got = fn(w, B, rec["xc"])
                got = got[0] if isinstance(got, tuple) else got
                errs[name][rec["cfg"][5]].append(abs(math.degrees(math.atan(got)) - truth) if np.isfinite(got) else np.nan)
    for name in fns:
        for sp in ("thin", "thick"):
            e = np.array(errs[name][sp])
            print("p %.2f %-9s %-5s |err| max %5.2f  95th %5.2f  median %4.2f  refused %d of %d" % (
                p, name, sp, np.nanmax(e), np.nanpercentile(e, 95), np.nanmedian(e), np.isnan(e).sum(), len(e)))


if __name__ == "__main__":
    main()
