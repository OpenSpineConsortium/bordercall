import sys, math
sys.path.insert(0, sys.argv[1])
import numpy as np
from morphoview import shapes as SH
sys.path.insert(0, sys.argv[2])
from fastdist import dist_to_polyline

def hermite(p, alpha, s):
    t = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1) ** alpha)])
    h = t[2] - t[1]
    m1 = h * ((p[1] - p[0]) / (t[1] - t[0]) - (p[2] - p[0]) / (t[2] - t[0]) + (p[2] - p[1]) / (t[2] - t[1]))
    m2 = h * ((p[2] - p[1]) / (t[2] - t[1]) - (p[3] - p[1]) / (t[3] - t[1]) + (p[3] - p[2]) / (t[3] - t[2]))
    s = s[:, None]
    return ((2 * s ** 3 - 3 * s ** 2 + 1) * p[1] + (s ** 3 - 2 * s ** 2 + s) * m1 + (3 * s ** 2 - 2 * s ** 3) * p[2] + (s ** 3 - s ** 2) * m2)

def worst(pts, closed):
    sp = SH.spline(pts, closed=closed)
    ext = np.vstack([pts[-1:], pts, pts[:2]]) if closed else np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]])
    spans = len(pts) if closed else len(pts) - 1
    s = np.linspace(0, 1, 20001)
    dense = np.vstack([hermite(ext[i:i + 4], 0.5, s) for i in range(spans)])
    return len(sp.points), float(dist_to_polyline(dense, sp.points, closed).max())

rng = np.random.default_rng(11)
cases = {
    "hairpin": np.array([[0, 0, 0], [100, 0, 0], [100.5, 1.0, 0], [0, 2, 0.0]]),
    "uneven 1000:1": np.array([[0, 0, 0], [0.05, 0.02, 0], [80, 3, 1], [81, 40, 2], [81.02, 40.03, 2.01]]),
    "near collinear": np.array([[0, 0, 0], [10, 1e-6, 0], [20, 0, 1e-6], [30, 2e-6, 0]]),
    "zigzag": np.array([[i * 2.0, (-1) ** i * 30.0, 0] for i in range(9)]),
    "two points": np.array([[0, 0, 0], [10, 5, 2.0]]),
    "vertebra origins": np.array([[0, 0, 0], [1, 2, 32], [3, 5, 63], [4, 10, 95], [3, 18, 128.0]]),
}
for name, pts in cases.items():
    for closed in (False, True):
        if closed and len(pts) < 3:
            continue
        n, off = worst(pts.astype(float), closed)
        print("%-16s closed=%-5s %6d points, max off the true spline %.4f mm" % (name, closed, n, off))
for k in range(60):
    pts = np.cumsum(rng.normal(size=(6, 3)) * rng.uniform(0.1, 40, size=(6, 1)), axis=0)
    for closed in (False, True):
        n, off = worst(pts, closed)
        if off > SH.TOLERANCE_MM:
            print("random %d closed=%s: %d points, max off %.4f" % (k, closed, n, off))
print("random done")
