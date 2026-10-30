"""The information limit of a binary mask on the posterior wall's slope, per cached phantom L3.

  PYTHONPATH=<bordercall> python limit.py <cache_dir> <out.json>

For each cached vertebra the scan's own voxel centres are taken in the vertebra's frame over the
region body.posterior_wall_slope reads: within ACROSS_HALF_MM of the midline xc, over the middle
60 per cent of the midline body's height, and within BAND_MM of a rough wall line front to back.
Bone is the vertebra's label (v.is_bone); air is every centre the label does not hold, which over
that region is the canal. A surface y = a + b z (line), + c x (plane), + d x^2 (curved) parts
them when every bone centre lies on or in front of it and every air centre on or behind it.
Linear programs (HiGHS) give the widest margin, the least and greatest slope b of any parting
surface, and the range of b among surfaces at the widest margin. Two other readings of "bone"
are scored beside the label: the body's own points (v.body) against air, the vertebra's bone
outside the body left out; and the body against everything else, which is what the reader sees.
"""
import json
import math
import os
import pickle
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # score.py and build_cache.py

ACROSS_HALF_MM = 3.0
BAND_MM = 4.0
FAMILIES = {"line": 2, "plane": 3, "curved": 4}


def region(v, B, xc, across=ACROSS_HALF_MM, cut=0.2):
    """The middle (1 - 2 cut) of the midline body's height and a rough wall line through it, as
    posterior_wall_slope bins it."""
    mid = B[np.abs(B[:, 0] - xc) <= across]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + cut * (z1 - z0), z1 - cut * (z1 - z0)
    step = max(v.fz, 0.5)
    rows = []
    for z in np.arange(lo, hi + 1e-9, step):
        layer = mid[np.abs(mid[:, 2] - z) <= 0.5 * step]
        if len(layer):
            rows.append((z, layer[:, 1].min()))
    rows = np.array(rows)
    s, i = np.polyfit(rows[:, 0], rows[:, 1], 1)
    return lo, hi, s, i


def lattice(v, xc, lo, hi, s, i, across=ACROSS_HALF_MM):
    """The scan's voxel centres over the region: frame coordinates and voxel indices."""
    ys = [i + s * lo, i + s * hi]
    corners = np.array([[x, y, z] for x in (xc - across - 2, xc + across + 2)
                        for y in (min(ys) - BAND_MM - 2, max(ys) + BAND_MM + 2) for z in (lo - 2, hi + 2)])
    inv = np.linalg.inv(np.asarray(v.grid.affine, float))
    cijk = v.points_world(corners) @ inv[:3, :3].T + inv[:3, 3]
    a, b = np.floor(cijk.min(0)).astype(int) - 1, np.ceil(cijk.max(0)).astype(int) + 1
    ijk = np.stack(np.meshgrid(*[np.arange(a[k], b[k] + 1) for k in range(3)], indexing="ij"), -1).reshape(-1, 3)
    q = v.frame.local(v.grid.world(ijk.astype(float)))
    keep = ((np.abs(q[:, 0] - xc) <= across) & (q[:, 2] >= lo) & (q[:, 2] <= hi)
            & (np.abs(q[:, 1] - (i + s * q[:, 2])) <= BAND_MM))
    return q[keep], ijk[keep]


def design(q, xc, k):
    X = q[:, 0] - xc
    cols = [np.ones(len(q)), q[:, 2], X, X ** 2][:k]
    return np.column_stack(cols)


def lp(c, A, b):
    r = linprog(c=c, A_ub=A, b_ub=b, bounds=[(None, None)] * len(c), method="highs")
    return r


STRICT_MM = 1e-6        # a surface parts only when no centre lies on it
TOL_MM = 0.02           # the slack of the tolerant range where a family parts nothing


def part(q, bone, xc, k):
    """For the family with k coefficients: the widest margin m* (mm along y); where m* > 0, the
    least and greatest slope b of any surface that parts bone from air and the range of b among
    surfaces at the widest margin; where m* <= 0, nothing in the family parts them, and the range
    is that of surfaces within -m* + TOL_MM of parting (tolerant), so the misfit is on record."""
    F = design(q, xc, k)
    y = q[:, 1]
    sgn = np.where(bone, 1.0, -1.0)          # bone: F.c + t <= y ; air: -F.c + t <= -y
    A = np.column_stack([sgn[:, None] * F, np.ones(len(q))])
    rhs = sgn * y
    obj = np.zeros(k + 1)
    obj[-1] = -1.0
    r = lp(obj, np.vstack([A, np.r_[np.zeros(k), 1.0]]), np.r_[rhs, 10.0])
    if not r.success:
        return {"ok": False, "why": str(r.message)}
    margin = float(r.x[-1])
    parts = margin > STRICT_MM
    floor = 0.0 if parts else margin - TOL_MM
    out = {"ok": True, "parts": bool(parts), "margin": margin, "n_bone": int(bone.sum()), "n_air": int((~bone).sum())}

    def b_range(t_min):
        ends = []
        for sense in (1.0, -1.0):
            c = np.zeros(k + 1)
            c[1] = sense
            rr = lp(c, np.vstack([A, np.r_[np.zeros(k), -1.0]]), np.r_[rhs, -t_min])
            ends.append(float(rr.x[1]) if rr.success else (-math.inf if sense > 0 else math.inf))
        return ends
    out["b_lo"], out["b_hi"] = b_range(floor)
    out["b_mm_lo"], out["b_mm_hi"] = b_range(margin - 1e-7)
    out["b_mm"] = 0.5 * (out["b_mm_lo"] + out["b_mm_hi"])
    return out


def truth_plane(rec):
    """The true wall plane in the measured frame, y = a + b z + c x (x from the frame's origin):
    the phantom's wall plane n.q = 0, n = (0, 1, -tan lean), mapped through the placement."""
    from morphometry.tests import phantom as P
    import build_cache as BC
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    placed = P.straight(BC.LUMBAR, P.lumbar(**BC.PHANTOMS[name]), tilt=tilt)
    pl = [p for p in placed if p.level == "L3"][0]
    f = rec["vert"].frame
    M = np.column_stack([f.ex, f.ey, f.ez])
    Q = pl.R.T @ M
    d = pl.R.T @ (f.origin - pl.c)
    n = np.array([0.0, 1.0, -math.tan(math.radians(lean))])
    m = Q.T @ n
    return {"a": float(-(n @ d) / m[1]), "b": float(-m[2] / m[1]), "c": float(-m[0] / m[1])}


def true_inside(rec, q):
    """Whether each frame point lies inside the phantom's body as drawn (sheared for the lean)."""
    from morphometry.tests import phantom as P
    import build_cache as BC
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    vv = P.lumbar(**BC.PHANTOMS[name])
    placed = P.straight(BC.LUMBAR, vv, tilt=tilt)
    pl = [p for p in placed if p.level == "L3"][0]
    world = rec["vert"].points_world(q)
    ql = (world - pl.c) @ pl.R
    inside = BC.sheared(lean) if lean else P.body_inside
    return inside(ql, vv)


def deg(b):
    return math.degrees(math.atan(b)) if math.isfinite(b) else (90.0 if b > 0 else -90.0)


def scored(got, t):
    """The parting's slopes in degrees, and where the truth t (degrees) and the widest-margin
    surface fall in the range."""
    if not got.get("ok"):
        return got
    for k in ("lo", "hi", "mm", "mm_lo", "mm_hi"):
        got[k + "_deg"] = deg(got["b_" + k] if k != "mm" else got["b_mm"])
    w = got["hi_deg"] - got["lo_deg"]
    got["width_deg"] = w
    got["truth_inside"] = bool(got["lo_deg"] - 1e-6 <= t <= got["hi_deg"] + 1e-6)
    got["truth_pos"] = (t - got["lo_deg"]) / w if w > 1e-9 else float("nan")
    got["mm_pos"] = (got["mm_deg"] - got["lo_deg"]) / w if w > 1e-9 else float("nan")
    got["mm_err"] = got["mm_deg"] - t
    got["mid_err"] = 0.5 * (got["lo_deg"] + got["hi_deg"]) - t
    got["worst_any_reader"] = max(t - got["lo_deg"], got["hi_deg"] - t)
    return got


EXTRA_REGIONS = {"x3_h80": (3.0, 0.1), "x6_h60": (6.0, 0.2), "x6_h80": (6.0, 0.1)}


def one(rec):
    import score as S
    from morphometry import body as BODY
    from morphometry import anatomy as A
    v, xc = rec["vert"], rec["xc"]
    B = v.body_pts
    lo, hi, s, i = region(v, B, xc)
    q, ijk = lattice(v, xc, lo, hi, s, i)
    bone = v.is_bone(ijk)
    body_set = {tuple(t) for t in v.idx[v.body]}
    isbody = np.array([tuple(t) in body_set for t in ijk])
    tp = truth_plane(rec)
    t = S.wall_truth_in_frame(rec)
    inside = true_inside(rec, q)
    resid = q[:, 1] - (tp["a"] + tp["b"] * q[:, 2] + tp["c"] * q[:, 0])
    # the reader on the vertebra's points in front of the canal, the body's cut undone: what
    # lies within 3 mm of the canal's wall line behind it is the sliver the cut took off the body
    sq = A.square_to_wall(v, v.loc)
    uncut = v.loc[sq[:, 1] > v.wall_y0 - 3.0]
    out = {"cfg": list(rec["cfg"]), "frame_err": rec["frame_err_deg"],
           "truth_dir_deg": t, "truth_plane": tp, "truth_plane_deg": deg(tp["b"]),
           "reader_deg": rec["raw"]["wall_now"], "reader_check_deg": deg(BODY.posterior_wall_slope(v, B, xc)),
           "reader_uncut_deg": deg(BODY.posterior_wall_slope(v, uncut, xc)),
           "canal_line_deg": deg(v.wall_slope), "fz": v.fz, "fy": v.fy, "fx": v.fx, "span_mm": hi - lo,
           "n": int(len(q)), "bone": int(bone.sum()), "body": int(isbody.sum()),
           "bone_not_body": int((bone & ~isbody).sum()), "body_not_bone": int((isbody & ~bone).sum()),
           "label_vs_true_inside": int((bone != inside).sum()),
           "true_plane_bone_behind_mm": float(max(0.0, -resid[bone].min())),
           "true_plane_air_ahead_mm": float(max(0.0, resid[~bone].max())),
           "fits": {}}
    variants = {"mask": (q, bone), "body": (q[~(bone & ~isbody)], isbody[~(bone & ~isbody)]), "cut": (q, isbody)}
    for vname, (qq, bb) in variants.items():
        for fam, k in FAMILIES.items():
            if vname != "mask" and fam == "line":
                continue
            out["fits"]["%s_%s" % (vname, fam)] = scored(part(qq, bb, xc, k), t)
    for name, (across, cut) in EXTRA_REGIONS.items():
        lo2, hi2, _, _ = region(v, B, xc, across, cut)
        q2, ijk2 = lattice(v, xc, lo2, hi2, s, i, across)
        out["fits"]["mask_curved_" + name] = scored(part(q2, v.is_bone(ijk2), xc, 4), t)
    return out


def main():
    cache, js = sys.argv[1], sys.argv[2]
    only = sys.argv[3] if len(sys.argv) > 3 else None
    rows = []
    for f in sorted(os.listdir(cache)):
        if not f.endswith(".pkl") or (only and only not in f):
            continue
        with open(os.path.join(cache, f), "rb") as fh:
            rec = pickle.load(fh)
        r = {"key": f[:-4]}
        r.update(one(rec))
        rows.append(r)
        cells = []
        for k in ("mask_line", "mask_plane", "mask_curved", "cut_plane"):
            g = r["fits"][k]
            cells.append("%s %s[%+6.2f %+6.2f] in %d mm %+6.2f" % (
                k.split("_")[1][:2] if k.startswith("mask") else "cut", "" if g["parts"] else "~",
                g["lo_deg"], g["hi_deg"], g["truth_inside"], g["mm_deg"]))
        print("%-38s t %+6.2f rd %+6.2f unc %+6.2f can %+6.2f bnb %3d | %s" % (
            r["key"], r["truth_dir_deg"], r["reader_deg"], r["reader_uncut_deg"], r["canal_line_deg"],
            r["bone_not_body"], " | ".join(cells)), flush=True)
    with open(js, "w") as fh:
        json.dump(rows, fh, indent=1, default=float)


if __name__ == "__main__":
    main()
