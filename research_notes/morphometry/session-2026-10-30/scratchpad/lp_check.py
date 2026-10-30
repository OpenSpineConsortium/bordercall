import sys; sys.path.insert(0, "/home/user/bordercall")
import math, numpy as np
from morphometry import pedicle as PED
rng = np.random.default_rng(0)
# a tilted lattice about a known surface: z = a + b*y + crown(x'), y in [-12,-4], x' in [-2.25,2.25]
b_true = -math.tan(math.radians(6.0))   # posterior end higher: z rises as y falls
pts = []
for y in np.arange(-12.0, -4.0, 0.4):
    for xp in np.arange(-2.0, 2.01, 0.8):
        phase = rng.uniform(0, 1.24)
        for z in np.arange(-9.0, 16.01, 1.24) + phase:
            pts.append((y, xp, z))
pts = np.array(pts)
y, xp, z = pts.T
crown = -0.1 * xp ** 2
top = 10.5 + b_true * y + crown
bot = -4.5 + b_true * y - crown
sel_t = np.abs(z - top) <= 1.5 * 1.24
sel_b = np.abs(z - bot) <= 1.5 * 1.24
gt = PED.parting(y[sel_t], xp[sel_t], z[sel_t], z[sel_t] < top[sel_t], True)
gb = PED.parting(y[sel_b], xp[sel_b], z[sel_b], z[sel_b] > bot[sel_b], False)
print("true b", round(b_true, 4), "top", gt["coefficients"].round(4), "margin", round(gt["margin"], 3), "across", gt["across"])
print("                bottom", gb["coefficients"].round(4), "margin", round(gb["margin"], 3), "across", gb["across"])
rise = 0.5 * (gt["coefficients"][1] + gb["coefficients"][1])
across = math.tan(math.radians(12.0))
d = -np.array([across, 1.0, rise]); d /= np.linalg.norm(d)
print("projection atan2(d2,-d1) =", round(math.degrees(math.atan2(d[2], -d[1])), 3),
      " elevation atan2(d2,hypot) =", round(math.degrees(math.atan2(d[2], math.hypot(d[0], d[1]))), 3))
for t, s in ((12, 6), (30, 10), (30, 15), (35, 15)):
    print("t=%d s=%d exact elevation = %.2f (bias %.2f)" % (t, s, math.degrees(math.atan(math.tan(math.radians(s)) * math.cos(math.radians(t)))),
          math.degrees(math.atan(math.tan(math.radians(s)) * math.cos(math.radians(t)))) - s))
# one class only: the margin program is unbounded
one = PED.parting(y[sel_t][:30], xp[sel_t][:30], z[sel_t][:30], np.ones(30, bool), True)
print("all bone ->", one)
# both classes, but separable in (y, x'): bone at the back rows, air at the front rows
yy = np.concatenate([np.full(6, -12.0), np.full(6, -5.0)]); xx = np.zeros(12); zz = np.zeros(12)
print("separable ->", PED.parting(yy, xx, zz, np.r_[np.ones(6, bool), np.zeros(6, bool)], True))
