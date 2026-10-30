import math, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import noise as N, score as S, cand as C
cache, p, seed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(seed)
deg = lambda t: math.degrees(math.atan(t)) if np.isfinite(t) else float("nan")
for f in sorted(os.listdir(cache)):
    if not f.endswith(".pkl"): continue
    rec = pickle.load(open(os.path.join(cache, f), "rb"))
    w = N.ragged(rec["vert"], p, rng)
    if rec["cfg"][5] != "thick": continue
    B = w.body_pts; Bc = rec["vert"].body_pts
    t = S.wall_truth_in_frame(rec)
    a, info = C.slope(w, B, rec["xc"])
    a2, info2 = C.slope(w, Bc, rec["xc"])
    if not (abs(deg(a) - t) < 2.0):
        mid = B[np.abs(B[:, 0] - rec["xc"]) <= 5.8]; midc = Bc[np.abs(Bc[:, 0] - rec["xc"]) <= 5.8]
        print(f[:-4], "err %+.2f" % (deg(a) - t), "| with the clean B for the window: %+.2f" % (deg(a2) - t),
              "| z extent noisy %.1f..%.1f clean %.1f..%.1f" % (mid[:, 2].min(), mid[:, 2].max(), midc[:, 2].min(), midc[:, 2].max()),
              {k: info[k] for k in ("why", "edges", "dropped", "rms", "span") if k in info})
