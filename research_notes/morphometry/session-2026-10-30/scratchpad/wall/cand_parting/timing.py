"""Time the candidate and the current reader per config, the cached vertebra already loaded."""
import importlib.util, os, pickle, sys, time
import numpy as np
from morphometry import body as BODY
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cand", os.path.join(here, "cand.py"))
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
cache = sys.argv[1]
tc, tn = {"thin": [], "thick": []}, {"thin": [], "thick": []}
for f in sorted(os.listdir(cache)):
    rec = pickle.load(open(os.path.join(cache, f), "rb"))
    v, xc = rec["vert"], rec["xc"]
    B = v.body_pts
    sp = rec["cfg"][5]
    v.mask_box()
    t = time.perf_counter(); C.slope(v, B, xc); tc[sp].append(time.perf_counter() - t)
    t = time.perf_counter(); BODY.posterior_wall_slope(v, B, xc); tn[sp].append(time.perf_counter() - t)
for sp in tc:
    a, b = np.array(tc[sp]), np.array(tn[sp])
    print("%s: candidate median %.3f s max %.3f s; current median %.4f s max %.4f s over %d" % (sp, np.median(a), a.max(), np.median(b), b.max(), len(a)))
