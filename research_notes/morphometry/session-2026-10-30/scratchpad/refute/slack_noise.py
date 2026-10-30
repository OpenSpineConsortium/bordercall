"""Does the L1 parting program return slacks of ~1e-8 for centres lying on the surface?
Build bands as lattice_under would (axis-aligned and tilted lattices), label bone/air by a
surface the quadratic model cannot part (a y*x' term plus flipped labels), run pedicle.parting's
second program verbatim and look at the slack values in the noise band (1e-12, 1e-6)."""
import numpy as np, sys
sys.path.insert(0, "/home/user/bordercall")
from morphometry.pedicle import parting
from scipy.optimize import linprog

def band(seed, tilt_deg, offset, fz=1.24, pixel=0.6, flips=3):
    rng = np.random.default_rng(seed)
    # lattice centres in a box, then rotated by tilt about x, offset in the frame
    xs = np.arange(-4.0, 4.0 + 1e-9, pixel)
    ys = np.arange(0.0, 9.0 + 1e-9, pixel)
    zs = np.arange(-6.0, 6.0 + 1e-9, fz)
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    p = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    t = np.radians(tilt_deg)
    R = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    p = p @ R.T + np.array(offset)
    a, b, c, d, e = offset[2] + 0.3, 0.15, 0.05, -0.04, 0.03
    zsurf = a + b * (p[:, 1] - offset[1]) + c * p[:, 0] + d * p[:, 0] ** 2 + e * (p[:, 1] - offset[1]) * p[:, 0]
    keep = np.abs(p[:, 2] - zsurf) <= 1.5 * fz
    p = p[keep]; zsurf = zsurf[keep]
    bone = p[:, 2] < zsurf
    k = rng.choice(len(p), flips, replace=False)
    bone[k] = ~bone[k]
    return p[:, 1], p[:, 0], p[:, 2], bone

worst = 0.0
for seed in range(6):
    for tilt in (0.0, 3.0, 7.0, 12.0):
        for off in ((0.0, 0.0, 0.0), (3.7, 21.3, -14.9), (-2.1, 35.0, 42.2)):
            y, x, z, bone = band(seed, tilt, off)
            got = parting(y, x, z, bone, top=True)
            if got is None:
                print("seed", seed, "tilt", tilt, "off", off, "-> None"); continue
            if got["margin"] >= 0:
                print("seed", seed, "tilt", tilt, "off", off, "parted, margin", got["margin"]); continue
            # recompute the slack vector the way parting does, to inspect it
            F = np.column_stack([np.ones_like(y), y, x, x ** 2])
            sign = np.where(bone, -1.0, 1.0)
            n = len(y)
            res = linprog(c=np.concatenate([np.zeros(4), np.ones(n)]),
                          A_ub=np.column_stack([sign[:, None] * F, -np.eye(n)]), b_ub=sign * z,
                          bounds=[(None, None)] * 4 + [(0.0, None)] * n, method="highs")
            s = res.x[4:]
            resid = sign * (F @ res.x[:4] - z)   # the true crossing distance, positive when across
            on = np.abs(resid) <= 1e-6            # centres lying on the surface
            noise = (s > 1e-12) & (s <= 1e-6)
            worst = max(worst, float(s[s <= 1e-6].max()) if (s <= 1e-6).any() else 0.0)
            print("seed %d tilt %4.1f off %-18s n=%4d across(1e-9)=%3d across(1e-3)=%3d on-surface=%2d  slack-noise(1e-12..1e-6)=%d  max slack of on-surface=%.2e  min slack of across=%.3e"
                  % (seed, tilt, off, n, int((s > 1e-9).sum()), int((s > 1e-3).sum()), int(on.sum()), int(noise.sum()),
                     float(np.abs(s[on]).max()) if on.any() else 0.0, float(s[s > 1e-9].min()) if (s > 1e-9).any() else 0.0))
print("worst sub-1e-6 slack over all runs: %.3e" % worst)
