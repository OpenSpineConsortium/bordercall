import sys, math, time; sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import measured
t0 = time.time()
v = P.lumbar(ped_t=30.0, ped_s=15.0)
rows = measured(P.straight(["L2", "L3", "L4"], v), ["L3"])
r = rows["L3"]
for k in sorted(r):
    if k.startswith("pedicle") or k.startswith("flag"):
        print(k, r[k] if isinstance(r[k], str) else round(r[k], 2))
print("%.0fs" % (time.time() - t0))
