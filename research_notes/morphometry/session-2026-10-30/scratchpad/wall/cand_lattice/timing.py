import os, pickle, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cand as C
from morphometry import body as BODY
cache = sys.argv[1]
recs = [pickle.load(open(os.path.join(cache, f), "rb")) for f in sorted(os.listdir(cache)) if f.endswith(".pkl")]
for name, fn in (("candidate", C.slope), ("candidate, no clamp", C.slope_plain), ("current", BODY.posterior_wall_slope)):
    t = []
    for rec in recs:
        v = rec["vert"]; B = v.body_pts
        t0 = time.perf_counter(); fn(v, B, rec["xc"]); t.append(time.perf_counter() - t0)
    t = np.array(t)
    print("%-22s %d configs: mean %.1f ms, median %.1f, max %.1f" % (name, len(t), 1e3 * t.mean(), 1e3 * np.median(t), 1e3 * t.max()))
