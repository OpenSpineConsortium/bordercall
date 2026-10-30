"""For chosen configs: candidate A's edges against the phantom's true wall crossing on each line.
Reports the slope from the midpoints, from the true crossings (no lattice error), and the edge
errors' spread, so the remaining error is split into lattice staircase and anything else."""
import math, os, pickle, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cand as C
import build_cache as BC
import score as S
from morphometry.tests import phantom as P

def placed_L3(cfg):
    name, lean, gname, tilt, turn, sname = cfg
    placed = P.straight(BC.LUMBAR, P.lumbar(**BC.PHANTOMS[name]), tilt=tilt)
    return [p for p in placed if p.level == "L3"][0]

def true_crossing(v, pl, lean, e, d):
    """Bisect along the line through edge e (frame) with step d (frame, posterior) for the
    phantom body's boundary."""
    inside = BC.sheared(lean) if lean else P.body_inside
    f = v.frame
    def body(pt_frame):
        w = f.origin + pt_frame[0] * f.ex + pt_frame[1] * f.ey + pt_frame[2] * f.ez
        q = (w - pl.c) @ pl.R
        return bool(inside(q[None, :], pl.v)[0])
    a, b = e - 0.5 * d, e + 0.5 * d     # a bone side, b air side
    if not body(a) or body(b):
        return None
    for _ in range(40):
        m = 0.5 * (a + b)
        if body(m): a = m
        else: b = m
    return 0.5 * (a + b)

def run(key, rec):
    v, B, xc = rec["vert"], rec["vert"].body_pts, rec["xc"]
    got, info = C.slope(v, B, xc)
    tf = S.wall_truth_in_frame(rec)
    rings = v.full_rings()
    width = float(np.median([s.width for s in rings])); ap = float(np.median([s.ap for s in rings]))
    half = min(C.HALF_BAND_MAX_MM, C.CANAL_SHARE * width)
    mid = B[np.abs(B[:, 0] - xc) <= half]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max(); m = 0.5 * (1 - C.HEIGHT_SHARE) * (z1 - z0)
    e, ystep = C.edges(v, xc, half, z0 + m, z1 - m, v.wall_y0 - 0.5 * ap)
    w, step, d = C.walking_axis(v)
    pl = placed_L3(rec["cfg"])
    T = np.array([true_crossing(v, pl, rec["cfg"][1], p, d) for p in e])
    coef_m, r_m = C.fit(e, xc)
    coef_t, r_t = C.fit(T, xc)
    err = (e - T) @ d / np.linalg.norm(d)   # along the line, mm, + = posterior of truth
    print("%-40s truth %+6.2f cand %+6.2f (err %+5.2f) | midpts %+6.2f truecross %+6.2f | n %d half %.1f |d| %.2f d_frame %s err along line [%+.2f %+.2f] mean %+.3f" % (
        key, tf, math.degrees(math.atan(got)), math.degrees(math.atan(got)) - tf,
        math.degrees(math.atan(coef_m[1])), math.degrees(math.atan(coef_t[1])), len(e), half,
        np.linalg.norm(d), np.round(d, 2), err.min(), err.max(), err.mean()))
    return e, T, err

if __name__ == "__main__":
    cache = sys.argv[1]
    for key in sys.argv[2:]:
        rec = pickle.load(open(os.path.join(cache, key + ".pkl"), "rb"))
        run(key, rec)
