"""Compare the saved path lengths of two trees pixel by pixel."""
import sys

import numpy as np

a, b = np.load(sys.argv[1]), np.load(sys.argv[2])
step = 0.25
for key in ("orth", "cone"):
    x, y = a[key], b[key]
    d = np.abs(x - y)
    changed = d > 1e-12
    flips = (x > 0) != (y > 0)
    print("%s: %d of %d path lengths changed, largest change %.4f mm (%.2f steps of %.2f mm), %d changed by more than one step, %d by more than two; silhouette pixels flipped %d (as written %d on, mutant %d on)"
          % (key, int(changed.sum()), x.size, float(d.max()), float(d.max()) / step, step,
             int((d > step + 1e-12).sum()), int((d > 2 * step + 1e-12).sum()), int(flips.sum()),
             int((x > 0).sum()), int((y > 0).sum())))
    if flips.any():
        r, c = np.nonzero(flips)
        for i, j in zip(r, c):
            print("   flipped pixel row %d col %d: as written %.4f mm, mutant %.4f mm" % (i, j, x[i, j], y[i, j]))
print("parallel sum / volume: as written %.6f, mutant %.6f" % (a["sum110"][0], b["sum110"][0]))
