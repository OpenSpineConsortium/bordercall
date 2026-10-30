"""The fine-step-at-start fault applied by patching, and both suites run on it."""
import math, sys, unittest
import numpy as np
from morphoview import shapes as SH

def fine_at_start(self, a, b, length, lo, hi, step):
    t0, t1 = SH.slab(a, b, lo, hi)
    span = np.clip(t1 - t0, 0.0, None) * length
    n = int(math.ceil(float(span.max(initial=0.0)) / step)) if span.size else 0
    if n == 0:
        return np.zeros(len(a))
    hits = np.zeros(len(a))
    for k in range(0, n, 256):
        s = (np.arange(k, min(n, k + 256)) + 0.0) / n
        tk = t0[:, None] + s[None, :] * (t1 - t0)[:, None]
        pts = a[:, None, :] + tk[:, :, None] * (b - a)[:, None, :]
        hits += self.inside(pts).sum(axis=1)
    return hits * span / n
SH.Volume.fine_samples = fine_at_start
suite = unittest.defaultTestLoader.loadTestsFromNames(["morphoview.tests.test_shapes", "morphoview.tests.test_projection"])
result = unittest.TextTestRunner(verbosity=0).run(suite)
print("ran", result.testsRun, "failures", len(result.failures), "errors", len(result.errors), "skipped", len(result.skipped))
