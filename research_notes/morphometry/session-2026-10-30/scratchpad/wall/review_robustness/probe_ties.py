"""Does the wall's reading depend on how np.argsort orders ties? trimmed_start sorts the edges by z,
where every layer of an axial grid holds many edges at one z, and cuts the order into halves; the
default sort's order among equal keys is the implementation's (numpy's AVX-512 quicksort on this
machine, another on a machine without it). The same reading is taken with the sorts made stable,
and with the ties taken in reverse, on the 98 cached phantom vertebrae."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)

import score as S  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from scanimport import geometry as G  # noqa: E402

ORIGINAL = BODY.trimmed_start


def trimmed_with(sorter):
    def trimmed_start(X, y, z):
        n = len(y)
        h = max(int(BODY.WALL_TRIM_KEEP * n), G.MIN_CHORD_POINTS)
        order = sorter(z)
        best = None
        for sub in [order] + [order[i * n // 4:(i + 2) * n // 4] for i in range(3)]:
            coef = np.linalg.lstsq(X[sub], y[sub], rcond=None)[0]
            for _ in range(BODY.WALL_TRIM_STEPS):
                idx = sorter((y - X @ coef) ** 2)[:h]
                new = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
                done = np.allclose(new, coef, atol=1e-10)
                coef = new
                if done:
                    break
            cost = np.sort((y - X @ coef) ** 2)[:h].sum()
            if best is None or cost < best[0]:
                best = (cost, coef)
        return best[1]
    return trimmed_start


def stable(a):
    return np.argsort(a, kind="stable")


def reverse_ties(a):
    """Equal keys in the reverse of their stable order."""
    n = len(a)
    return np.lexsort((-np.arange(n), a))


def reading(rec, fn):
    BODY.trimmed_start = fn
    v = rec["vert"]
    v.__dict__.pop("_posterior_wall", None)
    s, _ = BODY.posterior_wall(v, v.body_pts, rec["xc"])
    BODY.trimmed_start = ORIGINAL
    v.__dict__.pop("_posterior_wall", None)
    return BODY.degrees_of(s) if math.isfinite(s) else float("nan")


cache = os.path.join(WALL, "cache")
worst = []
for key, rec in S.records(cache):
    a = reading(rec, ORIGINAL)
    b = reading(rec, trimmed_with(stable))
    c = reading(rec, trimmed_with(reverse_ties))
    d = max(abs(a - b), abs(a - c), abs(b - c))
    worst.append((d, key, a, b, c))
worst.sort(reverse=True)
moved = [w for w in worst if w[0] > 1e-9]
print("vertebrae whose reading moves with the order of ties: %d of %d" % (len(moved), len(worst)))
for d, key, a, b, c in moved[:15]:
    print("  %-40s default %+.3f stable %+.3f reversed %+.3f  (spread %.3f)" % (key, a, b, c, d))
