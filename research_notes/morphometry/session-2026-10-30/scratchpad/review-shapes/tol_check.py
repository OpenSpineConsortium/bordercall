import sys, math
sys.path.insert(0, sys.argv[1])
import numpy as np
from scipy.spatial import cKDTree
from morphoview import shapes as SH

def dist_to_polyline(q, pts, closed):
    ring = np.vstack([pts, pts[:1]]) if closed else pts
    a, ab = ring[:-1], np.diff(ring, axis=0)
    best = np.full(len(q), np.inf)
    for i in range(0, len(a), 2000):
        aa, bb = a[i:i+2000], ab[i:i+2000]
        t = np.clip(((q[:, None, :] - aa[None]) * bb[None]).sum(-1) / np.maximum((bb * bb).sum(-1)[None], 1e-300), 0, 1)
        d = np.linalg.norm(q[:, None, :] - (aa[None] + t[..., None] * bb[None]), axis=-1).min(axis=1)
        best = np.minimum(best, d)
    return best

TOL = SH.TOLERANCE_MM
rng = np.random.default_rng(7)
# ellipses: tilted axes, high eccentricity
for la, lb in ((50.0, 0.5), (200.0, 0.05), (5.0, 4.9), (0.04, 0.03), (300.0, 2.0)):
    n = SH.unit(rng.normal(size=3)); e1, e2 = SH.across(n)
    c = rng.normal(size=3) * 10
    e = SH.ellipse(c, la * e1, lb * e2)
    t = np.linspace(0, 2 * math.pi, 400001)
    true = c + np.cos(t)[:, None] * la * e1 + np.sin(t)[:, None] * lb * e2
    print("ellipse %7.2f x %5.2f: %6d points, max off %.4f mm (tol %.2f)" % (la, lb, len(e.points), dist_to_polyline(true, e.points, True).max(), TOL))
# arcs and circles, tiny and large
for r, ang in ((0.03, 300.0), (0.05, 200.0), (0.06, 359.0), (500.0, 90.0), (10.0, -270.0), (10.0, 720.0)):
    c = np.zeros(3); nrm = np.array([0.0, 0.0, 1.0])
    a = SH.arc(c, nrm, [r, 0, 0], ang)
    t = np.linspace(0, math.radians(ang), 200001)
    true = np.stack([r * np.cos(t), r * np.sin(t), 0 * t], 1)
    print("arc r=%g angle=%g: %d points, max off %.4f" % (r, ang, len(a.points), dist_to_polyline(true, a.points, False).max()))
for r in (0.03, 0.05, 0.2, 400.0, -12.0):
    circ = SH.circle(np.zeros(3), [0, 0, 1], r)
    e1, e2 = SH.across([0, 0, 1])
    t = np.linspace(0, 2 * math.pi, 200001)
    true = abs(r) * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
    print("circle r=%g: %d points, max off %.4f" % (r, len(circ.points), dist_to_polyline(true, circ.points, True).max()))
