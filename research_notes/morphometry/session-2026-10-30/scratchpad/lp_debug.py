import sys; sys.path.insert(0, "/home/user/bordercall")
import math, numpy as np
from scipy.optimize import linprog
rng = np.random.default_rng(0)
b_true = -math.tan(math.radians(6.0))
pts = []
for y in np.arange(-12.0, -4.0, 0.4):
    for xp in np.arange(-2.0, 2.01, 0.8):
        phase = rng.uniform(0, 1.24)
        for z in np.arange(-3.0, 3.01, 1.24) + phase:
            pts.append((y, xp, z))
pts = np.array(pts); y, xp, z = pts.T
top = 10.5 + b_true * y - 0.1 * xp ** 2
sel = np.abs(z - top) <= 1.5 * 1.24
y, xp, z, bone = y[sel], xp[sel], z[sel], z[sel] < top[sel]
print("n", len(y), "bone", bone.sum(), "air", (~bone).sum())
F = np.column_stack([np.ones_like(y), y, xp, xp ** 2])
sign = np.where(bone, -1.0, 1.0)
n = len(y)
res = linprog(c=[0.0, 0.0, 0.0, 0.0, -1.0], A_ub=np.column_stack([sign[:, None] * F, np.ones(n)]),
              b_ub=sign * z, bounds=[(None, None)] * 5, method="highs")
print("status", res.status, res.message, "x", None if res.x is None else res.x.round(4))
