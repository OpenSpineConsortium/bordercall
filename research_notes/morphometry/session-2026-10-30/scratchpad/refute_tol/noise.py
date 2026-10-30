"""Does HiGHS hand parting() a crossing of solver-noise size for a centre the L1-optimal
surface passes through?  Lattice centres under a few columns, a surface that no quadratic
parts (a step or label noise), the fallback program run through pedicle.parting itself,
and every xi in (0, 1e-6] counted."""
import sys, time
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0, "/home/user/bordercall")
from morphometry.pedicle import parting

rng = np.random.default_rng(0)
t0 = time.time()
tiny = []          # (trial, xi) for xi in (0, 1e-6]
smallest_pos = np.inf
fallbacks = 0
neg_margin_tiny = 0
n_trials = 0
lens = []
for trial in range(1500):
    if time.time() - t0 > 40:
        break
    fx = float(rng.choice([0.5, 0.7, 0.8, 1.0]))
    fz = float(rng.choice([0.625, 1.0, 1.24, 2.5, 3.0]))
    ncols = int(rng.integers(6, 14))
    # columns across one to three isthmus rows, a half pixel apart front to back
    ys = rng.choice(np.arange(-3.0, 3.0, 0.5 * fx), size=ncols) + rng.normal(0, 1e-3)
    xs = rng.choice(np.arange(-4.0, 4.0, fx), size=ncols)
    # true surface: a + b y + c x + d x^2, plus a step so it is not parted
    a, b, c, d = rng.normal(0, 2), np.tan(np.radians(rng.uniform(-20, 20))), rng.normal(0, 0.2), rng.normal(0, 0.05)
    layers = int(rng.integers(1, 4))      # SURFACE_LAYERS-like window in layers
    q, acr, z, bone = [], [], [], []
    z0 = rng.uniform(0, fz)                # the lattice's phase
    for x, y in zip(xs, ys):
        zs = a + b * y + c * x + d * x * x
        step = rng.choice([0.0, 0.0, fz]) if rng.random() < 0.5 else 0.0
        for k in range(-layers, layers + 1):
            zc = z0 + fz * np.round((zs - z0) / fz) + k * fz
            q.append(y); acr.append(x); z.append(zc)
            is_bone = zc < zs + step
            if rng.random() < 0.08:
                is_bone = not is_bone
            bone.append(bool(is_bone))
    y_, x_, z_, b_ = map(np.array, (q, acr, z, bone))
    if min(b_.sum(), (~b_).sum()) < 4:
        continue
    n_trials += 1
    lens.append(len(y_))
    top = bool(rng.random() < 0.5)
    got = parting(y_, x_, z_, b_, top)
    if got is None:
        continue
    if got["margin"] < 0.0:
        fallbacks += 1
        if got["margin"] > -1e-6:
            neg_margin_tiny += 1
        # re-run the crossing program as parting does, to look at the raw xi
        F = np.column_stack([np.ones_like(y_), y_, x_, x_ ** 2])
        sign = np.where(b_, -1.0, 1.0) if top else np.where(b_, 1.0, -1.0)
        n = len(y_)
        res = linprog(c=np.concatenate([np.zeros(4), np.ones(n)]),
                      A_ub=np.column_stack([sign[:, None] * F, -np.eye(n)]), b_ub=sign * z_,
                      bounds=[(None, None)] * 4 + [(0.0, None)] * n, method="highs")
        xi = np.asarray(res.x[4:], float)
        pos = xi[xi > 0]
        if len(pos):
            smallest_pos = min(smallest_pos, pos.min())
        for v in xi[(xi > 0) & (xi <= 1e-6)]:
            tiny.append((trial, float(v)))
        # how many xi are exactly 0.0, and how many centres lie exactly on the surface
        on = np.abs(F @ res.x[:4] - z_) < 1e-9
        exact0 = (xi == 0.0).sum()
        if trial < 5:
            print("trial", trial, "n", n, "across", got["across"], "xi exactly 0:", exact0,
                  "on surface:", on.sum(), "min positive xi:", pos.min() if len(pos) else None)
print("trials", n_trials, "fallbacks", fallbacks, "len(q) min/median/max", min(lens), int(np.median(lens)), max(lens))
print("xi in (0, 1e-6]:", len(tiny), tiny[:10])
print("smallest positive xi over all fallbacks:", smallest_pos)
print("margins in (-1e-6, 0):", neg_margin_tiny)
print("seconds", round(time.time() - t0, 1))
