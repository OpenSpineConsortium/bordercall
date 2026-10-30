import sys, math, time; sys.path.insert(0, "/home/user/bordercall")
import numpy as np
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import measured
t0 = time.time()
v = P.lumbar(ped_t=25.0, ped_s=12.0)
rows = measured(P.straight(["L2", "L3", "L4"], v), ["L3"])
r = rows["L3"]
for side in ("", "_right", "_left"):
    if "pedicle_angle_sagittal" + side not in r: print("L3%s: not read" % side); continue
    s, t = r["pedicle_angle_sagittal" + side], r["pedicle_angle_transverse" + side]
    proj = math.degrees(math.atan(math.tan(math.radians(s)) / math.cos(math.radians(t)))) if np.isfinite(s) else float("nan")
    print("L3%-7s code (elevation) %6.2f  transverse %6.2f  -> projection from the same axis %6.2f  truth 12.00" % (side, s, t, proj))
print("pedicle_h %.2f (truth 12.00)  %.0fs" % (r["pedicle_h"], time.time() - t0))
