"""Print posterior_wall_slope's z bins on cached phantoms: each bin's z, count, least y, the scan's
k layers its points come from, and, for the least-y point, its k, j and its excess over the true
wall (the point's distance in front of the phantom's wall surface at its own x and z).

  bins.py <cache_dir> <key> [<key> ...]
"""
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from morphometry import body as BODY  # noqa: E402
from scanimport import geometry as G  # noqa: E402
import build_cache as BC  # noqa: E402
import score as SC  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402


def placed_of(rec):
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    pv = P.lumbar(**BC.PHANTOMS[name])
    placed = P.straight(BC.LUMBAR, pv, tilt=tilt)
    return [p for p in placed if p.level == "L3"][0], pv


def excess_over_wall(rec, pts_local):
    """Each frame-local point's distance in front of the true wall, along the phantom's y."""
    pl, pv = placed_of(rec)
    v = rec["vert"]
    w = v.points_world(pts_local)
    q = (w - pl.c) @ pl.R           # phantom coordinates: R's columns are the phantom axes
    lean = rec["cfg"][1]
    t = math.tan(math.radians(lean))
    x, y, z = q[:, 0], q[:, 1] - t * q[:, 2], q[:, 2]
    f = 1.0 - (1.0 - pv.waist) * np.clip(1.0 - (2.0 * z / pv.Hp) ** 2, 0.0, 1.0)
    a, b = pv.W * f / 2, pv.D * f / 2
    ywall = b - b * np.sqrt(np.clip(1.0 - (x / a) ** 2, 0.0, 1.0))
    return y - ywall


def bins(rec):
    v, xc = rec["vert"], rec["xc"]
    B = v.body_pts
    K = v.idx[v.body]
    sel = np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM
    mid, kid = B[sel], K[sel]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    out = []
    for z in np.arange(lo, hi + 1e-9, step):
        m = np.abs(mid[:, 2] - z) <= 0.5 * step
        if not m.any():
            out.append(dict(z=z, n=0))
            continue
        L, KL = mid[m], kid[m]
        a = int(np.argmin(L[:, 1]))
        ymin = L[a, 1]
        ks, cnt = np.unique(KL[:, 2], return_counts=True)
        near = L[:, 1] <= ymin + 0.5 * v.fy        # the wall's own points in the bin
        kn = np.unique(KL[near, 2])
        ex = excess_over_wall(rec, L[a:a + 1])[0]
        out.append(dict(z=z, n=int(m.sum()), ymin=ymin, ks=dict(zip(ks.tolist(), cnt.tolist())),
                        kwall=kn.tolist(), kmin=int(KL[a, 2]), jmin=int(KL[a, 1]), imin=int(KL[a, 0]),
                        zmin=L[a, 2], excess=ex))
    return out, step, (lo, hi)


def main():
    cache = sys.argv[1]
    for key in sys.argv[2:]:
        with open(os.path.join(cache, key + ".pkl"), "rb") as fh:
            rec = pickle.load(fh)
        v = rec["vert"]
        truth = SC.wall_truth_in_frame(rec)
        now = math.degrees(math.atan(BODY.posterior_wall_slope(v, v.body_pts, rec["xc"])))
        rows, step, (lo, hi) = bins(rec)
        print("== %s: step %.3f, window z %.2f..%.2f (%.1f mm), fy %.3f, frame err %.2f deg" % (
            key, step, lo, hi, hi - lo, v.fy, rec["frame_err_deg"]))
        print("   wall now %+.2f deg, truth in frame %+.2f, error %+.2f" % (now, truth, now - truth))
        print("   %7s %5s %7s %7s %5s %4s %4s  %-28s %s" % ("z", "n", "ymin", "excess", "zmin", "k*", "j*", "layers k:count", "wall layers"))
        for r in rows:
            if r["n"] == 0:
                print("   %+7.2f %5d   (empty bin)" % (r["z"], 0))
                continue
            ks = " ".join("%d:%d" % kv for kv in r["ks"].items())
            print("   %+7.2f %5d %+7.3f %+7.3f %+5.2f %4d %4d  %-28s %s" % (
                r["z"], r["n"], r["ymin"], r["excess"], r["zmin"] - r["z"], r["kmin"], r["jmin"], ks, r["kwall"]))
        zz = np.array([r["z"] for r in rows if r["n"]])
        ex = np.array([r["excess"] for r in rows if r["n"]])
        if len(zz) >= 2:
            s = np.polyfit(zz, ex, 1)[0]
            print("   slope of the excess over the window: %+.4f mm/mm = %+.2f deg" % (s, math.degrees(math.atan(s))))


if __name__ == "__main__":
    main()
