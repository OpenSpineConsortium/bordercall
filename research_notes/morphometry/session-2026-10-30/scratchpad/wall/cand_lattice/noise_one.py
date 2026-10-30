import math, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import noise as N, score as S, cand as C
cache, p, seed, want = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rng = np.random.default_rng(seed)
for f in sorted(os.listdir(cache)):
    if not f.endswith(".pkl"): continue
    rec = pickle.load(open(os.path.join(cache, f), "rb"))
    w = N.ragged(rec["vert"], p, rng)
    if f[:-4] != want: continue
    xc = rec["xc"]; B = w.body_pts
    t = S.wall_truth_in_frame(rec)
    rings = w.full_rings(); half = min(6.0, 0.25 * float(np.median([s.width for s in rings]))); ap = float(np.median([s.ap for s in rings]))
    mid = B[np.abs(B[:, 0] - xc) <= half]; z0, z1 = mid[:, 2].min(), mid[:, 2].max(); m = 0.2 * (z1 - z0)
    bone, air, ys = C.edges(w, xc, half, z0 + m, z1 - m, w.wall_y0 - 0.5 * ap)
    e = 0.5 * (bone + air)
    true_y = math.tan(math.radians(t)) * e[:, 2]
    coef, r = C.fit(e, xc)
    print(want, "truth %+.2f, first fit %+.2f, window %.1f..%.1f, ystep %.2f" % (t, math.degrees(math.atan(coef[1])), z0 + m, z1 - m, ys))
    order = np.argsort(e[:, 2])
    zs = np.round(e[order, 2]).astype(int)
    for z in np.unique(zs):
        sel = order[zs == z]
        dev = e[sel, 1] - true_y[sel]
        print("  z %+3d  n %3d  y - (truth line) median %+.2f  min %+.2f max %+.2f   x %+.1f..%+.1f" % (z, len(sel), np.median(dev), dev.min(), dev.max(), e[sel, 0].min() - xc, e[sel, 0].max() - xc))
