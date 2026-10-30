import numpy as np
from scipy.optimize import linprog
rng = np.random.default_rng(3)
same_ds = same_ipm = 0
ipm_tiny = 0
for t in range(40):
    n = int(rng.integers(8, 60))
    y = rng.choice(np.arange(0, 3, 0.35), n); x = rng.choice(np.arange(-5, 5, 0.7), n)
    z = 1.24 * np.round((0.2 * y + 0.1 * x + rng.normal(0, 0.8, n)) / 1.24)
    bone = (z < 0.2 * y + 0.1 * x) ^ (rng.random(n) < 0.2)
    F = np.column_stack([np.ones(n), y, x, x ** 2])
    sign = np.where(bone, -1.0, 1.0)
    args = dict(c=np.concatenate([np.zeros(4), np.ones(n)]), A_ub=np.column_stack([sign[:, None] * F, -np.eye(n)]),
                b_ub=sign * z, bounds=[(None, None)] * 4 + [(0.0, None)] * n)
    r = linprog(method="highs", **args); d = linprog(method="highs-ds", **args); p = linprog(method="highs-ipm", **args)
    same_ds += bool(np.array_equal(r.x, d.x)); same_ipm += bool(np.array_equal(r.x, p.x))
    xi = p.x[4:]; ipm_tiny += int(((xi > 1e-9) & (xi < 1e-6)).sum())
print("highs == highs-ds bitwise:", same_ds, "of 40;  highs == highs-ipm bitwise:", same_ipm, "of 40")
print("ipm xi in (1e-9, 1e-6):", ipm_tiny)
