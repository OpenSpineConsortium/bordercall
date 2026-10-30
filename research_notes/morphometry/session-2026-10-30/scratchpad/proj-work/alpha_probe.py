import sys
import numpy as np
sys.path.insert(0, "/home/user/bordercall")
from morphoview import shapes as SH


def hermite(p, alpha, s):
    t = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1) ** alpha)])
    h = t[2] - t[1]
    m1 = h * ((p[1] - p[0]) / (t[1] - t[0]) - (p[2] - p[0]) / (t[2] - t[0]) + (p[2] - p[1]) / (t[2] - t[1]))
    m2 = h * ((p[2] - p[1]) / (t[2] - t[1]) - (p[3] - p[1]) / (t[3] - t[1]) + (p[3] - p[2]) / (t[3] - t[2]))
    s = s[:, None]
    return ((2 * s**3 - 3 * s**2 + 1) * p[1] + (s**3 - 2 * s**2 + s) * m1
            + (-2 * s**3 + 3 * s**2) * p[2] + (s**3 - s**2) * m2)


def dense(pts, alpha, closed=False):
    if closed:
        ext = np.vstack([pts[-1:], pts, pts[:2]]); spans = len(pts)
    else:
        ext = np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]); spans = len(pts) - 1
    s = np.linspace(0.0, 1.0, 20001)
    return np.vstack([hermite(ext[i:i + 4], alpha, s) for i in range(spans)])


def worst(curve, ref):
    from scipy.spatial import cKDTree
    return float(cKDTree(ref).query(curve)[0].max())


pts = np.array([[0.0, 0.0, 0.0], [30.0, 4.0, 0.0], [31.0, 9.0, 2.0], [60.0, 10.0, -3.0], [62.0, 40.0, 1.0]])
for closed in (False, True):
    c = SH.spline(pts, closed=closed).points
    print("closed", closed, "n", len(c))
    for alpha in (0.5, 0.0, 1.0):
        print("  alpha", alpha, "worst %.6f" % worst(c, dense(pts, alpha, closed)))
# the pyramid against the Hermite form directly, at the same s
p = pts[:4]
s = np.linspace(0, 1, 101)
print("pyramid vs hermite", np.abs(SH.catmull_rom(p, s) - hermite(p, 0.5, s)).max())
