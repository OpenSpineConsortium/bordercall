"""Which surface sets each bin's least y: the mask's own posterior wall, or the body cut of
anatomy.body_in_front (B is what lies in front of the canal's wall line)? For each bin of
posterior_wall_slope, the least-y point's

  ex    its distance in front of the true wall's pole line (phantom y, sheared by the lean),
  cut   its distance in front of the cut line (square_to_wall y minus v.wall_y0),
  back  whether the voxel one step behind it on the lattice (the grid axis nearest -ey) is bone,
        i.e. whether the mask goes on behind the point and only the cut stopped B.

  bins2.py <cache_dir> <key> [<key> ...]
"""
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from morphometry import body as BODY, anatomy as A  # noqa: E402
import build_cache as BC  # noqa: E402
import score as SC  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402


def placed_of(rec):
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    pv = P.lumbar(**BC.PHANTOMS[name])
    placed = P.straight(BC.LUMBAR, pv, tilt=tilt)
    return [p for p in placed if p.level == "L3"][0], pv


def pole_excess(rec, pts_local):
    pl, pv = placed_of(rec)
    v = rec["vert"]
    q = (v.points_world(pts_local) - pl.c) @ pl.R
    t = math.tan(math.radians(rec["cfg"][1]))
    return q[:, 1] - t * q[:, 2]


def back_step(v):
    """The lattice step (di, dj, dk) that moves most nearly along -ey."""
    c = v.grid.axes.T @ v.frame.ey
    a = int(np.argmax(np.abs(c)))
    s = np.zeros(3, int)
    s[a] = -1 if c[a] > 0 else 1
    return s


def describe(rec):
    v, xc = rec["vert"], rec["xc"]
    B = v.body_pts
    K = v.idx[v.body]
    sel = np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM
    mid, kid = B[sel], K[sel]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    bs = back_step(v)
    rows = []
    for z in np.arange(lo, hi + 1e-9, step):
        m = np.abs(mid[:, 2] - z) <= 0.5 * step
        if not m.any():
            continue
        L, KL = mid[m], kid[m]
        a = int(np.argmin(L[:, 1]))
        p = L[a:a + 1]
        cut = A.square_to_wall(v, p)[0, 1] - v.wall_y0
        back = bool(v.is_bone((KL[a] + bs)[None, :])[0])
        rows.append(dict(z=z, zp=p[0, 2], y=p[0, 1], ex=pole_excess(rec, p)[0], cut=cut, back=back,
                         k=int(KL[a, 2]), j=int(KL[a, 1])))
    return rows, (lo, hi), bs


def main():
    cache = sys.argv[1]
    for key in sys.argv[2:]:
        with open(os.path.join(cache, key + ".pkl"), "rb") as fh:
            rec = pickle.load(fh)
        v = rec["vert"]
        truth = SC.wall_truth_in_frame(rec)
        rows, (lo, hi), bs = describe(rec)
        now = math.degrees(math.atan(BODY.posterior_wall_slope(v, v.body_pts, rec["xc"])))
        print("== %s: error %+.2f (now %+.2f, truth %+.2f); cut line %+.2f deg, y0 %+.2f at z %+.2f; back step %s" % (
            key, now - truth, now, truth, math.degrees(math.atan(v.wall_slope)), v.wall_y0, v.wall_z0, bs.tolist()))
        nb = sum(r["back"] for r in rows)
        for r in rows:
            print("   z %+6.2f  y %+7.3f  ex %+6.3f  cut %+6.3f  k %3d j %3d  %s" % (
                r["z"], r["y"], r["ex"], r["cut"], r["k"], r["j"], "BONE BEHIND (cut binds)" if r["back"] else "air behind"))
        zz = np.array([r["z"] for r in rows])
        ex = np.array([r["ex"] for r in rows])
        print("   bins where the cut binds: %d of %d; fit of ex over bin z: %+.2f deg" % (
            nb, len(rows), math.degrees(math.atan(np.polyfit(zz, ex, 1)[0]))))


if __name__ == "__main__":
    main()
