"""Same question at the sizes a band can take: near MIN_PARTED and a few thousand centres."""
import numpy as np, sys
sys.path.insert(0, "/home/user/bordercall")
from scipy.optimize import linprog

def run(n_x, n_y, fz, pixel, seed, flips, tilt):
    rng = np.random.default_rng(seed)
    xs = np.arange(n_x) * pixel - 0.5 * n_x * pixel
    ys = np.arange(n_y) * pixel
    zs = np.arange(-6.0, 6.0 + 1e-9, fz)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    p = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    t = np.radians(tilt)
    R = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    p = p @ R.T + np.array([1.3, 27.0, -9.0])
    zsurf = -8.7 + 0.15 * (p[:, 1] - 27.0) + 0.05 * p[:, 0] - 0.04 * p[:, 0] ** 2 + 0.03 * (p[:, 1] - 27.0) * p[:, 0]
    keep = np.abs(p[:, 2] - zsurf) <= 1.5 * fz
    p = p[keep]; zsurf = zsurf[keep]
    bone = p[:, 2] < zsurf
    k = rng.choice(len(p), min(flips, len(p)), replace=False)
    bone[k] = ~bone[k]
    y, x, z = p[:, 1], p[:, 0], p[:, 2]
    F = np.column_stack([np.ones_like(y), y, x, x ** 2])
    sign = np.where(bone, -1.0, 1.0)
    n = len(y)
    res = linprog(c=np.concatenate([np.zeros(4), np.ones(n)]),
                  A_ub=np.column_stack([sign[:, None] * F, -np.eye(n)]), b_ub=sign * z,
                  bounds=[(None, None)] * 4 + [(0.0, None)] * n, method="highs")
    s = res.x[4:]
    resid = sign * (F @ res.x[:4] - z)
    on = np.abs(resid) <= 1e-6
    print("n=%5d across(1e-9)=%4d across(1e-3)=%4d on-surface=%3d exactly-zero slacks=%4d max slack among on-surface=%.2e noise(1e-12..1e-6)=%d"
          % (n, (s > 1e-9).sum(), (s > 1e-3).sum(), on.sum(), (s == 0.0).sum(), float(np.abs(s[on]).max()) if on.any() else 0.0, ((s > 1e-12) & (s <= 1e-6)).sum()))

for seed in range(3):
    run(3, 4, 1.24, 0.6, seed, 1, 0.0)      # a band near MIN_PARTED
    run(3, 4, 1.24, 0.6, seed, 1, 5.0)
    run(30, 40, 0.8, 0.4, seed, 8, 0.0)     # a few thousand centres
    run(30, 40, 0.8, 0.4, seed, 8, 4.0)
