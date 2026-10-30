"""Does the count at pedicle.py:448 ever differ between 1e-9 and a tolerance in mm, on
lattice-like sets run through parting itself; and what does HiGHS return as the margin
where bone and air exactly touch (the second half of the proposed fix)."""
import sys, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, "/home/user/bordercall")
from morphometry.pedicle import parting, VIOLATED_SHARE

def crossing_raw(y, x, z, bone, top):
    F = np.column_stack([np.ones_like(y), y, x, x ** 2])
    sign = np.where(bone, -1.0, 1.0) if top else np.where(bone, 1.0, -1.0)
    n = len(y)
    res = linprog(c=np.concatenate([np.zeros(4), np.ones(n)]),
                  A_ub=np.column_stack([sign[:, None] * F, -np.eye(n)]), b_ub=sign * z,
                  bounds=[(None, None)] * 4 + [(0.0, None)] * n, method="highs")
    return np.asarray(res.x[4:], float), np.asarray(res.x[:4], float), F, sign

rng = np.random.default_rng(7)
t0 = time.time()
stats = dict(trials=0, fallbacks=0, sets_le_10=0, noisy_xi=0, gate_differs=0, zero_basic_max=0.0,
             exact_zero_xi_on_surface=0, on_surface=0, margin_tiny_neg=0)
while time.time() - t0 < 35:
    small = rng.random() < 0.5
    fx = float(rng.choice([0.5, 0.7, 0.8, 1.0]))
    fz = float(rng.choice([0.625, 1.0, 1.24, 2.5, 5.0]))
    ncols = 6 if small else int(rng.integers(6, 40))
    y_off, z_off = rng.uniform(-40, 40), rng.uniform(-60, 60)
    ys = y_off + rng.choice(np.arange(0.0, float(rng.choice([0.4, 2.0, 7.5])), 0.5 * fx), size=ncols)
    xs = rng.choice(np.arange(-6.0, 6.0, fx), size=ncols) + rng.normal(0, 0.01)
    a, b, c, d = z_off + rng.normal(0, 2), np.tan(np.radians(rng.uniform(-40, 40))), rng.normal(0, 0.4), rng.normal(0, 0.1)
    layers = 0 if small else 1
    q, acr, z, bone = [], [], [], []
    z0 = rng.uniform(0, fz)
    for x, y in zip(xs, ys):
        zs = a + b * (y - y_off) + c * x + d * x * x
        for k in ([0, 1] if small and rng.random() < 0.5 else range(-layers, layers + 1)):
            zc = z0 + fz * np.round((zs - z0) / fz) + k * fz
            q.append(y); acr.append(x); z.append(zc)
            is_bone = zc < zs
            if rng.random() < 0.12:
                is_bone = not is_bone
            bone.append(bool(is_bone))
    y_, x_, z_, b_ = map(np.array, (q, acr, z, bone))
    if min(b_.sum(), (~b_).sum()) < 4:
        continue
    stats["trials"] += 1
    if len(y_) <= 10:
        stats["sets_le_10"] += 1
    top = bool(rng.random() < 0.5)
    got = parting(y_, x_, z_, b_, top)
    if got is None:
        continue
    if -1e-6 < got["margin"] < 0:
        stats["margin_tiny_neg"] += 1
    if got["margin"] >= 0:
        continue
    stats["fallbacks"] += 1
    xi, coef, F, sign = crossing_raw(y_, x_, z_, b_, top)
    resid = sign * (F @ coef - z_)              # the true crossing of each centre under this surface
    on = np.abs(resid) <= 1e-7
    stats["on_surface"] += int(on.sum())
    stats["exact_zero_xi_on_surface"] += int((xi[on] == 0.0).sum())
    if on.any():
        stats["zero_basic_max"] = max(stats["zero_basic_max"], float(np.abs(xi[on]).max()))
    noisy = (xi > 1e-9) & (xi <= 1e-6)
    stats["noisy_xi"] += int(noisy.sum())
    a9 = int((xi > 1e-9).sum()); a6 = int((xi > 1e-6 * 1.0).sum())
    if (a9 > VIOLATED_SHARE * len(y_)) != (a6 > VIOLATED_SHARE * len(y_)):
        stats["gate_differs"] += 1
print("random lattice sets:", stats)

# Exactly touching classes: a top surface climbing one layer per row, bone at (y=0,z=0) and
# (y=2,z=2), air at (y=1,z=1) on the same x', so no surface strictly parts them (margin 0),
# plus the rest of the lattice cleanly parted.
fz = 1.0
pts = []
for yy in range(0, 3):
    for k in range(-1, 3):
        zc = float(yy + k)
        pts.append((float(yy), 0.0, zc, zc < yy))          # bone below z = y
pts.append((1.0, 0.0, 1.0, False))                            # the air centre ON the surface
pts = [p for p in pts if not (p[0] == 1.0 and p[2] == 1.0 and p[3])]
y_, x_, z_, b_ = (np.array([p[i] for p in pts]) for i in range(4))
b_ = b_.astype(bool)
for off in (0.0, 13.7, -29.3):
    got = parting(y_ + off, x_, z_ + 0.37, b_, True)
    print("touching: y offset %6.1f -> margin %r across %r n %d" % (off, got["margin"], got["across"], len(y_)))
