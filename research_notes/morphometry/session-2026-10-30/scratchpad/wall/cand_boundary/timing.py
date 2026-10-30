"""Wall-clock seconds per call of C, the riser variant and the current reader, per cached config:
the median of five calls, one thread."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import score as S
import cand as C
import cand_crack as K
from morphometry import body as BODY
fns = {"C": C.slope, "C+risers": K.slope, "current": BODY.posterior_wall_slope}
out = {k: {"thin": [], "thick": []} for k in fns}
for key, rec in S.records("../cache"):
    v, B, xc = rec["vert"], rec["vert"].body_pts, rec["xc"]
    for name, fn in fns.items():
        ts = []
        for _ in range(5):
            t0 = time.perf_counter()
            fn(v, B, xc)
            ts.append(time.perf_counter() - t0)
        out[name][rec["cfg"][5]].append(np.median(ts))
for name in fns:
    for sp in ("thin", "thick"):
        t = np.array(out[name][sp]) * 1000
        print("%-9s %-5s median %.2f ms  max %.2f ms over %d configs" % (name, sp, np.median(t), t.max(), len(t)))
