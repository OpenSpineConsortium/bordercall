import sys, time; sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import measured, LUMBAR
kw = eval("dict(%s)" % sys.argv[1])
v = P.lumbar(**kw)
t0 = time.time()
rows = measured(P.straight(LUMBAR, v), LUMBAR, strict=False)
truth = P.truth(v)
r = rows["L3"]
for k in ("pedicle_angle_sagittal", "pedicle_angle_transverse", "pedicle_w", "pedicle_h", "pedicle_chord"):
    print("%-26s %8.3f  truth %8.3f" % (k, r.get(k, float("nan")), truth[k]))
print({k: r[k] for k in r if k.startswith("flag")}, "%.0fs" % (time.time() - t0))
