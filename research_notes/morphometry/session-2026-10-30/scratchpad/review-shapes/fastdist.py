import numpy as np
from scipy.spatial import cKDTree

def dist_to_polyline(q, pts, closed, step=0.002):
    """Distance from each q to the polyline, by sampling the polyline every `step` mm: within step / 2
    of the exact distance (an upper bound on it)."""
    ring = np.vstack([pts, pts[:1]]) if closed else pts
    parts = []
    for a, b in zip(ring[:-1], ring[1:]):
        n = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        parts.append(a + np.linspace(0, 1, n, endpoint=False)[:, None] * (b - a))
    parts.append(ring[-1:])
    return cKDTree(np.vstack(parts)).query(q)[0]
