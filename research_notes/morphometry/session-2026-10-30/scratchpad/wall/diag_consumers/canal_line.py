"""anatomy's canal wall line (v.wall_slope, Theil-Sen over the full rings' anterior walls) against
the frame-relative truth of the body's posterior wall, which on these phantoms is also the canal's
anterior wall at the midline, beside body.posterior_wall_slope as it stands.

  canal_line.py <cache_dir> <out.json>

Per config: both readings and their errors against score.wall_truth_in_frame; the rings' z span
and count; and each ring's excess, its anterior wall minus the true wall's y at that ring's
midline x and z (the wall plane taken into the measured frame), with the excess of the raw
outermost voxel centre (no edge_gap half-step) beside it. A reader that errs by the staircase of
voxel centres shows an excess that climbs or falls steadily within a tooth and jumps by about one
lattice step between teeth, and its error is the slope of that excess.
"""
import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import build_cache as BC  # noqa: E402
import score as SC  # noqa: E402
from morphometry import anatomy as A  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402
from scanimport import geometry as G  # noqa: E402


def placed_L3(cfg):
    name, lean, gname, tilt, turn, sname = cfg
    placed = P.straight(BC.LUMBAR, P.lumbar(**BC.PHANTOMS[name]), tilt=tilt)
    return [p for p in placed if p.level == "L3"][0]


def wall_y(rec, x, z):
    """The true wall plane's y in the measured frame at frame (x, z)."""
    pl = placed_L3(rec["cfg"])
    t = math.tan(math.radians(rec["cfg"][1]))
    N = pl.R @ np.array([0.0, 1.0, -t])
    f = rec["vert"].frame
    return -(N @ (f.origin - pl.c) + x * (N @ f.ex) + z * (N @ f.ez)) / (N @ f.ey)


def plane_slope_deg(rec):
    pl = placed_L3(rec["cfg"])
    t = math.tan(math.radians(rec["cfg"][1]))
    N = pl.R @ np.array([0.0, 1.0, -t])
    f = rec["vert"].frame
    return math.degrees(math.atan(-(N @ f.ez) / (N @ f.ey)))


def raw_walls(v):
    """Each slab's anterior wall as canal_walls reads it and as the raw outermost centre."""
    out = {}
    for s in G.sections(v.loc, v.fz, v.pixel, as_hole=True):
        if s.canal is None:
            continue
        got = G.canal_walls(s, v.pixel, v.fx, v.fy)
        if got is None:
            continue
        c, p = s.canal, s.pts
        xm = 0.5 * (c[:, 0].min() + c[:, 0].max())
        ym = 0.5 * (c[:, 1].min() + c[:, 1].max())
        down = p[np.abs(p[:, 0] - xm) <= 0.75 * v.pixel]
        ant = down[down[:, 1] > ym, 1]
        out[round(s.w, 6)] = (got[2], float(ant.min()))
    return out


def theil_sen(z, y):
    i, j = np.triu_indices(len(z), 1)
    far = np.abs(z[j] - z[i]) >= A.WALL_PAIR_MM
    if len(z) < 3 or far.sum() < 3:
        return float("nan")
    return float(np.median((y[j] - y[i])[far] / (z[j] - z[i])[far]))


def jumps(e, step):
    d = np.diff(e)
    return int((np.abs(d) > 0.5 * step).sum())


def post_bins(v, xc):
    """posterior_wall_slope's bins: (z, least y) as it takes them."""
    B = v.body_pts
    mid = B[np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    rows = []
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        if len(layer):
            k = int(np.argmin(layer[:, 1]))
            rows.append((z, layer[k, 1], layer[k, 0]))
    return np.array(rows), (lo, hi)


def one(key, rec):
    v = rec["vert"]
    truth = SC.wall_truth_in_frame(rec)
    plane = plane_slope_deg(rec)
    rings = v.full_rings()
    z = np.array([s.z for s in rings])
    ya = np.array([s.anterior for s in rings])
    xm = np.array([s.midline for s in rings])
    yt = np.array([wall_y(rec, a, b) for a, b in zip(xm, z)])
    raw = raw_walls(v)
    yr = np.array([raw.get(round(s.z, 6), (np.nan, np.nan))[1] for s in rings])
    canal = math.degrees(math.atan(v.wall_slope))
    ts_now = theil_sen(z, ya)
    ts_raw = theil_sen(z, yr)
    e, er = ya - yt, yr - yt
    span = float(z.max() - z.min()) if len(z) else 0.0
    zero_fallback = (v.wall_slope == 0.0)
    pb, (lo, hi) = post_bins(v, rec["xc"])
    pe = pb[:, 1] - np.array([wall_y(rec, x, zz) for zz, x in zip(pb[:, 0], pb[:, 2])])
    post = rec["raw"]["wall_now"]
    return {"key": key, "phantom": rec["cfg"][0], "lean": rec["cfg"][1], "grid": rec["cfg"][2],
            "spacing": rec["cfg"][5], "truth": truth, "plane_truth": plane, "frame_err": rec["frame_err_deg"],
            "canal_deg": canal, "canal_err": canal - truth,
            "canal_raw_deg": math.degrees(math.atan(ts_raw)) if np.isfinite(ts_raw) else float("nan"),
            "post_deg": post, "post_err": post - truth,
            "rings": int(len(rings)), "ring_span": span, "zero_fallback": bool(zero_fallback),
            "ring_z": z.tolist(), "ring_excess": e.tolist(), "ring_excess_raw": er.tolist(),
            "ring_jumps": jumps(e, v.fy), "post_window": hi - lo, "post_bins": int(len(pb)),
            "post_excess": pe.tolist(), "post_jumps": jumps(pe, v.fy), "fy": v.fy, "fz": v.fz,
            "excess_slope_deg": math.degrees(math.atan(theil_sen(z, e))) if len(z) >= 3 else float("nan"),
            "check_reconstructed_deg": math.degrees(math.atan(ts_now)) if np.isfinite(ts_now) else float("nan")}


def main():
    cache, out = sys.argv[1], sys.argv[2]
    rows = []
    for key, rec in SC.records(cache):
        r = one(key, rec)
        rows.append(r)
        print("%-40s truth %+6.2f | canal %+6.2f err %+6.2f (raw %+6.2f) rings %2d span %5.1f jumps %d%s"
              " | post %+6.2f err %+6.2f jumps %d" % (
                  key, r["truth"], r["canal_deg"], r["canal_err"], r["canal_raw_deg"] - r["truth"], r["rings"],
                  r["ring_span"], r["ring_jumps"], " ZERO" if r["zero_fallback"] else "", r["post_deg"],
                  r["post_err"], r["post_jumps"]), flush=True)
    with open(out, "w") as f:
        json.dump(rows, f, indent=1, default=float)


if __name__ == "__main__":
    main()
