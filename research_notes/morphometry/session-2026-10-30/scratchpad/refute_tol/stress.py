"""The same question under worse numbers: frame coordinates offset by tens of mm, columns
crowded in y (the slope ill-determined), x' up to 10 mm so x'^2 reaches 100, and the
smallest sets (len(q) near 8).  The largest noise-size xi is what matters against 1e-9."""
import sys, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, "/home/user/bordercall")
from morphometry.pedicle import parting

rng = np.random.default_rng(1)
t0 = time.time()
largest_noise = 0.0
counts = {"trials": 0, "fallbacks": 0, "noise_xi": 0, "small_sets": 0, "small_fallbacks": 0, "flipped": 0}
margins_tiny = []
while time.time() - t0 < 40:
    small = rng.random() < 0.5
    fx = float(rng.choice([0.5, 0.7, 1.0]))
    fz = float(rng.choice([0.625, 1.24, 3.0, 5.0]))
    ncols = 6 if small else int(rng.integers(6, 40))
    yspread = float(rng.choice([0.3, 1.0, 6.0]))
    y_off, z_off, x_off = rng.uniform(-40, 40), rng.uniform(-60, 60), rng.uniform(-10, 10)
    ys = y_off + rng.choice(np.arange(0.0, yspread, 0.5 * fx), size=ncols)
    xs = rng.choice(np.arange(-10.0, 10.0, fx), size=ncols)
    a, b, c, d = z_off + rng.normal(0, 2), np.tan(np.radians(rng.uniform(-45, 45))), rng.normal(0, 0.5), rng.normal(0, 0.1)
    layers = 0 if small else int(rng.integers(1, 3))
    q, acr, z, bone = [], [], [], []
    z0 = rng.uniform(0, fz)
    for x, y in zip(xs, ys):
        zs = a + b * (y - y_off) + c * x + d * x * x
        ks = [0] if layers == 0 else range(-layers, layers + 1)
        if small and rng.random() < 0.4:
            ks = [0, 1]
        for k in ks:
            zc = z0 + fz * np.round((zs - z0) / fz) + k * fz
            q.append(y); acr.append(x); z.append(zc)
            is_bone = zc < zs
            if rng.random() < 0.15:
                is_bone = not is_bone
            bone.append(bool(is_bone))
    y_, x_, z_, b_ = map(np.array, (q, acr, z, bone))
    if min(b_.sum(), (~b_).sum()) < 4:
        continue
    counts["trials"] += 1
    if len(y_) <= 10:
        counts["small_sets"] += 1
    top = bool(rng.random() < 0.5)
    got = parting(y_, x_, z_, b_, top)
    if got is None:
        continue
    if -1e-6 < got["margin"] < 0:
        margins_tiny.append(got["margin"])
    if got["margin"] >= 0.0:
        continue
    counts["fallbacks"] += 1
    if len(y_) <= 10:
        counts["small_fallbacks"] += 1
    F = np.column_stack([np.ones_like(y_), y_, x_, x_ ** 2])
    sign = np.where(b_, -1.0, 1.0) if top else np.where(b_, 1.0, -1.0)
    n = len(y_)
    res = linprog(c=np.concatenate([np.zeros(4), np.ones(n)]),
                  A_ub=np.column_stack([sign[:, None] * F, -np.eye(n)]), b_ub=sign * z_,
                  bounds=[(None, None)] * 4 + [(0.0, None)] * n, method="highs")
    xi = np.asarray(res.x[4:], float)
    noise = xi[(xi > 0) & (xi < 1e-4)]
    if len(noise):
        counts["noise_xi"] += len(noise)
        largest_noise = max(largest_noise, noise.max())
    # would a count at a tolerance of 1e-6 differ from the code's 1e-9?
    if int((xi > 1e-9).sum()) != int((xi > 1e-6).sum()):
        counts["flipped"] += 1
print(counts)
print("largest noise-size xi (0 < xi < 1e-4):", largest_noise)
print("margins in (-1e-6, 0):", margins_tiny[:5], len(margins_tiny))
print("seconds", round(time.time() - t0, 1))
