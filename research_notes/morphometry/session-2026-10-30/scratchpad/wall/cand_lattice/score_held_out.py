"""Score candidate A on the held-out phantoms (held_out.py) as score.py scores the cache."""
import math, os, pickle, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import held_out  # registers the overhang phantom with build_cache
import score as S
import cand as C

deg = lambda t: math.degrees(math.atan(t)) if np.isfinite(t) else float("nan")
cache = sys.argv[1]
worst = {}
for f in sorted(os.listdir(cache)):
    if not f.endswith(".pkl"):
        continue
    rec = pickle.load(open(os.path.join(cache, f), "rb"))
    v = rec["vert"]; B = v.body_pts
    t = S.wall_truth_in_frame(rec)
    a, info = C.slope(v, B, rec["xc"])
    p, _ = C.slope_plain(v, B, rec["xc"])
    now = rec["raw"]["wall_now"]
    d = S.downstream(rec, deg(a)); dn = S.downstream(rec, now); dt = S.downstream(rec, t)
    print("%-42s frame %.2f truth %+6.2f | now %+6.2f  cand %+6.2f  plain %+6.2f | free %s" % (
        f[:-4], rec["frame_err_deg"], t, now - t, deg(a) - t, deg(p) - t, "%.2f" % float(info.get("free_deg", float("nan")))))
    print("   downstream now:  %s" % "  ".join("%s %+.2f" % (k, x) for k, x in dn.items() if np.isfinite(x)))
    print("   downstream cand: %s" % "  ".join("%s %+.2f" % (k, x) for k, x in d.items() if np.isfinite(x)))
    print("   with true wall:  %s" % "  ".join("%s %+.2f" % (k, x) for k, x in dt.items() if np.isfinite(x)))
