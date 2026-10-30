"""Whether the pairs C reads pin the slope: the range of b of every line y = a + b z that keeps each
pair straddled once C's own fitted x terms are taken off, against the information limit's width."""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S
import cand as C


def slope_range(m, step_f, coef, xc, tol):
    x = m[:, 0] - xc
    curve = sum(coef[2 + p] * x ** (p + 1) for p in range(C.X_TERMS))
    bone, air = m - 0.5 * step_f, m + 0.5 * step_f
    yb, ya = bone[:, 1] - curve, air[:, 1] - curve
    dz = bone[:, 2][None, :] - air[:, 2][:, None]          # [air i, bone j]
    dy = yb[None, :] - ya[:, None] + tol
    up, down = dz > 1e-9, dz < -1e-9
    hi = np.min(dy[up] / dz[up]) if up.any() else np.inf
    lo = np.max(dy[down] / dz[down]) if down.any() else -np.inf
    flat_bad = ((np.abs(dz) <= 1e-9) & (dy < 0)).any()
    return lo, hi, flat_bad


limit = {r["key"]: r for r in json.load(open("../diag_limit/limit.json"))}
for tol in (0.0, 0.02, 0.05):
    feas, rows = 0, []
    for key, rec in S.records("../cache"):
        v, B, xc = rec["vert"], rec["vert"].body_pts, rec["xc"]
        band = B[np.abs(B[:, 0] - xc) <= 3]
        z0, z1 = band[:, 2].min(), band[:, 2].max()
        m, step_f = C.wall_pairs(v, xc, z0 + 0.2 * (z1 - z0), z0 + 0.8 * (z1 - z0))
        coef, res, keep = C.trimmed_fit(m, xc, step_f)
        lo, hi, bad = slope_range(m, step_f, coef, xc, tol)
        ok = lo <= hi and not bad
        feas += ok
        lw = limit[key]["fits"]["mask_curved"]["width_deg"]
        w = math.degrees(math.atan(hi) - math.atan(lo)) if ok else float("nan")
        err = math.degrees(math.atan(coef[1])) - S.wall_truth_in_frame(rec)
        rows.append((key, w, lw, err))
    print("tol %.2f mm: a straddling line exists in %d of 98" % (tol, feas))
    if tol == 0.02:
        for r in rows:
            print("  %-40s C range width %6.2f  limit (curved) width %5.2f  C err %+5.2f" % r)
