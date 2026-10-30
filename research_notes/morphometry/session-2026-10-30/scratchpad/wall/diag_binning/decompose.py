"""Split posterior_wall_slope's error on every cached phantom into what the z bins do, what the
body cut does and what the lattice staircase of the wall does. Each variant reads the wall's
dy/dz over the same window (the middle 60 per cent of the strip's height in B) and is scored
against the truth taken into the measured frame (score.wall_truth_in_frame), in degrees.

  cur        body.posterior_wall_slope as it stands
  cur_zp     the same bins, each row's abscissa the least-y point's own z, not the bin's centre
  phase      the bins' grid shifted by 1/4, 1/2 and 3/4 of a step: the largest and smallest error
  step_half  bins half as wide (step max(fz,0.5)/2), so no bin can hold two layers' wall
  layer      no bins: the least y of each lattice layer (the scan's k), at that point's own z
  uncut      the current bins over B plus the mask's voxels the body cut left out, within 3 mm
             behind the cut line in the strip (only body wall lies there: the canal is air)
  uncut_lay  per-layer over the uncut points
  oracle     the current bins with each least y moved back onto the true wall (minus its excess
             over the wall's pole line): what is left once staircase and cut are taken away
  canal      anatomy.wall_slope's line (v.wall_slope), the canal's wall that sets the cut

  decompose.py <cache_dir> <out.json>
"""
import json
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


def deg(s):
    return math.degrees(math.atan(s)) if np.isfinite(s) else float("nan")


def fit(z, y):
    return float(np.polyfit(z, y, 1)[0]) if len(z) >= 3 else float("nan")


def strip(v, pts, idx, xc):
    m = np.abs(pts[:, 0] - xc) <= BODY.ACROSS_HALF_MM
    return pts[m], idx[m]


def window(mid):
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    return z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)


def binned(pts, lo, hi, step, offset=0.0):
    """(bin z, point z, least y, row index into pts) of each non-empty bin."""
    rows = []
    for z in np.arange(lo + offset, hi + 1e-9, step):
        m = np.flatnonzero(np.abs(pts[:, 2] - z) <= 0.5 * step)
        if len(m):
            a = m[np.argmin(pts[m, 1])]
            rows.append((z, pts[a, 2], pts[a, 1], a))
    return rows


def per_layer(pts, idx, lo, hi):
    rows = []
    for k in np.unique(idx[:, 2]):
        m = np.flatnonzero(idx[:, 2] == k)
        a = m[np.argmin(pts[m, 1])]
        if lo <= pts[a, 2] <= hi:
            rows.append((pts[a, 2], pts[a, 2], pts[a, 1], a))
    return rows


def slope_of(rows, use_point_z=False):
    if len(rows) < 3:
        return float("nan")
    r = np.array([x[:3] for x in rows])
    return fit(r[:, 1] if use_point_z else r[:, 0], r[:, 2])


def placed_of(rec):
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    pv = P.lumbar(**BC.PHANTOMS[name])
    placed = P.straight(BC.LUMBAR, pv, tilt=tilt)
    return [p for p in placed if p.level == "L3"][0]


def pole_excess(rec, pts):
    pl = placed_of(rec)
    q = (rec["vert"].points_world(pts) - pl.c) @ pl.R
    return q[:, 1] - math.tan(math.radians(rec["cfg"][1])) * q[:, 2]


def uncut_points(v, xc):
    """B's strip plus the voxels the cut left out up to 3 mm behind the cut line."""
    rel = A.square_to_wall(v, v.loc)[:, 1] - v.wall_y0
    keep = v.body | ((rel > -3.0) & (np.abs(v.loc[:, 0] - xc) <= BODY.ACROSS_HALF_MM))
    return v.loc[keep], v.idx[keep]


def relative_angle(rec):
    """The angle between the true wall and the nearest lattice plane, degrees."""
    pl = placed_of(rec)
    v = rec["vert"]
    t = math.tan(math.radians(rec["cfg"][1]))
    n = pl.R @ np.array([0.0, 1.0, -t])
    n /= np.linalg.norm(n)
    c = np.abs(v.grid.axes.T @ n)
    return math.degrees(math.acos(min(1.0, c.max())))


def analyse(rec):
    v, xc = rec["vert"], rec["xc"]
    truth = SC.wall_truth_in_frame(rec)
    mid, kid = strip(v, v.body_pts, v.idx[v.body], xc)
    lo, hi = window(mid)
    step = max(v.fz, 0.5)
    out = {"truth": truth, "frame_err": rec["frame_err_deg"], "rel_angle": relative_angle(rec),
           "period_mm": float("nan")}
    rows = binned(mid, lo, hi, step)
    out["cur"] = deg(slope_of(rows))
    out["cur_check"] = deg(BODY.posterior_wall_slope(v, v.body_pts, xc))
    out["cur_zp"] = deg(slope_of(rows, True))
    ph = [deg(slope_of(binned(mid, lo, hi, step, f * step))) for f in (0.0, 0.25, 0.5, 0.75)]
    out["phase_min"], out["phase_max"] = min(ph, key=lambda a: abs(a - truth)), max(ph, key=lambda a: abs(a - truth))
    out["phase_spread"] = max(ph) - min(ph)
    out["step_half"] = deg(slope_of(binned(mid, lo, hi, 0.5 * step)))
    out["layer"] = deg(slope_of(per_layer(mid, kid, lo, hi)))
    U, UI = strip(v, *uncut_points(v, xc), xc)
    out["uncut"] = deg(slope_of(binned(U, lo, hi, step)))
    out["uncut_lay"] = deg(slope_of(per_layer(U, UI, lo, hi)))
    ex = pole_excess(rec, mid[[r[3] for r in rows]])
    r = np.array([x[:3] for x in rows])
    out["oracle"] = deg(fit(r[:, 0], r[:, 2] - ex))
    out["excess_fit"] = deg(fit(r[:, 0], ex))
    bs = np.zeros(3, int)
    c = v.grid.axes.T @ v.frame.ey
    a = int(np.argmax(np.abs(c)))
    bs[a] = -1 if c[a] > 0 else 1
    out["cut_binds"] = int(sum(bool(v.is_bone((kid[x[3]] + bs)[None, :])[0]) for x in rows))
    out["bins"] = len(rows)
    out["canal"] = deg(v.wall_slope)
    return out


def main():
    cache, js = sys.argv[1], sys.argv[2]
    res = {}
    for key, rec in SC.records(cache):
        res[key] = analyse(rec)
        o = res[key]
        print("%-38s rel %4.1f  err: cur %+5.2f zp %+5.2f phase[%+5.2f..%+5.2f] half %+5.2f layer %+5.2f "
              "uncut %+5.2f uncut_lay %+5.2f oracle %+5.2f | excess %+5.2f | cut binds %d/%d | canal %+5.2f" % (
                  key, o["rel_angle"], o["cur"] - o["truth"], o["cur_zp"] - o["truth"], o["phase_min"] - o["truth"],
                  o["phase_max"] - o["truth"], o["step_half"] - o["truth"], o["layer"] - o["truth"],
                  o["uncut"] - o["truth"], o["uncut_lay"] - o["truth"], o["oracle"] - o["truth"], o["excess_fit"],
                  o["cut_binds"], o["bins"], o["canal"] - o["truth"]), flush=True)
    with open(js, "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
