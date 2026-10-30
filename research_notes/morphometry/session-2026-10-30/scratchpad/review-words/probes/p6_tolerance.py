"""Whether a sampled spline or ellipse keeps every point of the true curve within 0.05 mm."""
import numpy as np
from morphoview import shapes as SH

def distance_to_polyline(q, pts, closed):
    ring = np.vstack([pts, pts[:1]]) if closed else pts
    a, ab = ring[:-1], np.diff(ring, axis=0)
    out = np.empty(len(q))
    for i in range(0, len(q), 2000):
        qq = q[i:i + 2000]
        t = np.clip(((qq[:, None, :] - a[None]) * ab[None]).sum(-1) / (ab * ab).sum(-1)[None], 0.0, 1.0)
        out[i:i + 2000] = np.linalg.norm(qq[:, None, :] - (a[None] + t[..., None] * ab[None]), axis=-1).min(axis=1)
    return out

worst = (0.0, None)
for seed in range(60):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(3, 8))
    scale = rng.choice([1.0, 5.0, 30.0])
    pts = np.cumsum(rng.normal(size=(n, 3)) * scale, axis=0)
    # sometimes put a point very near another, to make a sharp, uneven span
    if seed % 3 == 0:
        pts[1] = pts[0] + rng.normal(size=3) * 0.3
    for closed in (False, True):
        try:
            sp = SH.spline(pts, closed=closed)
        except ValueError:
            continue
        ext = (np.vstack([pts[-1:], pts, pts[:2]]) if closed else np.vstack([2 * pts[0] - pts[1], pts, 2 * pts[-1] - pts[-2]]))
        spans = len(pts) if closed else len(pts) - 1
        dense = np.vstack([SH.catmull_rom(ext[i:i + 4], np.linspace(0.0, 1.0, 3001)) for i in range(spans)])
        d = float(distance_to_polyline(dense, sp.points, closed).max())
        if d > worst[0]:
            worst = (d, (seed, closed, len(sp.points)))
print("spline worst distance %.5f mm at %s" % worst)
worst = (0.0, None)
for a, b in ((20, 3), (40, 1), (60, 0.5), (100, 0.2), (10, 10), (5, 0.05)):
    e = SH.ellipse([0, 0, 0], [a, 0, 0], [0, b, 0])
    t = np.linspace(0, 2 * np.pi, 400001)
    true = np.stack([a * np.cos(t), b * np.sin(t), 0 * t], axis=1)
    d = float(distance_to_polyline(true, e.points, True).max())
    print("ellipse %g x %g: %d points, worst %.5f mm" % (a, b, len(e.points), d))
