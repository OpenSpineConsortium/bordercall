"""(a) Bone and air that exactly touch: bone centres ON the top surface at y0 and y0+2h, an
air centre ON it at y0+h, the rest a layer clear; the true margin is 0.  What does parting
return, and is the climb then refused?  (b) Over random fallbacks, does across (the 1e-9
count) ever exceed the count of centres truly across the returned surface by 1e-6 mm?"""
import sys, time
import numpy as np
sys.path.insert(0, "/home/user/bordercall")
from morphometry.pedicle import parting, VIOLATED_SHARE

def touching(y0, z0, h, fz, xoff):
    pts = []
    for j, yy in enumerate((y0, y0 + h, y0 + 2 * h)):
        s = z0 + j * fz                         # the surface z = z0 + (fz/h)(y - y0) at this row
        for k in range(-2, 3):
            zc = s + k * fz
            pts.append((yy, xoff, zc, zc <= s + 1e-12))   # bone up to and on the surface
    # the middle row's centre on the surface is air instead: the hulls touch
    pts = [(y, x, z, (False if (abs(y - (y0 + h)) < 1e-9 and abs(z - (z0 + fz)) < 1e-9) else b)) for y, x, z, b in pts]
    # a few cleanly parted centres at other x', so the quadratic terms have columns
    for xx in (xoff + 1.3, xoff - 1.3):
        for j, yy in enumerate((y0, y0 + 2 * h)):
            s = z0 + j * fz
            pts.append((yy, xx, s - 0.5 * fz, True)); pts.append((yy, xx, s + 0.5 * fz, False))
    y, x, z, b = (np.array([p[i] for p in pts]) for i in range(4))
    return y, x, z, b.astype(bool)

for (y0, z0, h, fz, xoff) in [(0.0, 0.0, 1.0, 1.0, 0.0), (13.7, -22.31, 0.4, 1.24, 0.0), (-7.3, 41.9, 0.35, 0.625, 2.1),
                              (0.4, 0.37, 0.4, 1.24, -1.7), (25.55, 3.3, 0.5, 2.5, 0.0)]:
    y, x, z, b = touching(y0, z0, h, fz, xoff)
    got = parting(y, x, z, b, True)
    n = len(y)
    verdict = "REFUSED" if got is None or got["across"] > VIOLATED_SHARE * n else "read"
    print("touching y0=%6.2f z0=%7.2f h=%.2f fz=%.3f: margin %+.3e across %d of %d -> %s, b=%.4f (true %.4f)"
          % (y0, z0, h, fz, got["margin"], got["across"], n, verdict, got["coefficients"][1], fz / h))

# (b) independent count over random fallbacks
from scipy.optimize import linprog
rng = np.random.default_rng(11)
t0 = time.time(); over = under = fallbacks = 0; worst = 0.0
while time.time() - t0 < 22:
    fx = float(rng.choice([0.5, 0.8, 1.0])); fz = float(rng.choice([0.625, 1.24, 3.0]))
    ncols = int(rng.integers(6, 30)); y_off, z_off = rng.uniform(-40, 40), rng.uniform(-60, 60)
    ys = y_off + rng.choice(np.arange(0.0, float(rng.choice([0.4, 7.5])), 0.5 * fx), size=ncols)
    xs = rng.choice(np.arange(-6.0, 6.0, fx), size=ncols)
    a, b_, c, d = z_off + rng.normal(0, 2), np.tan(np.radians(rng.uniform(-40, 40))), rng.normal(0, 0.4), rng.normal(0, 0.1)
    q, acr, z, bone = [], [], [], []
    z0 = rng.uniform(0, fz)
    for x, yy in zip(xs, ys):
        zs = a + b_ * (yy - y_off) + c * x + d * x * x
        for k in range(-1, 2):
            zc = z0 + fz * np.round((zs - z0) / fz) + k * fz
            q.append(yy); acr.append(x); z.append(zc)
            bone.append(bool((zc < zs) != (rng.random() < 0.12)))
    y_, x_, z_, bb = map(np.array, (q, acr, z, bone))
    if min(bb.sum(), (~bb).sum()) < 4:
        continue
    top = bool(rng.random() < 0.5)
    got = parting(y_, x_, z_, bb, top)
    if got is None or got["margin"] >= 0:
        continue
    fallbacks += 1
    F = np.column_stack([np.ones_like(y_), y_, x_, x_ ** 2])
    sign = np.where(bb, -1.0, 1.0) if top else np.where(bb, 1.0, -1.0)
    resid = sign * (F @ got["coefficients"] - z_)
    truly = int((resid > 1e-6).sum())
    if got["across"] > truly: over += 1
    if got["across"] < truly: under += 1
    near = np.abs(resid[(np.abs(resid) > 1e-12) & (np.abs(resid) < 1e-6)])
    if len(near): worst = max(worst, float(near.max()))
print("random fallbacks %d: across overcounts %d, undercounts %d, largest |residual| in (1e-12,1e-6): %.2e" % (fallbacks, over, under, worst))
