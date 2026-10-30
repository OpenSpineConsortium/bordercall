"""The staircase of a plane wall on a voxel lattice, with no mask, no cut and no bins: the wall
is y = 0 (vertical in z), the body y > 0; the lattice (row pitch p across the wall, layer pitch s
along it) is turned by rel degrees against the wall and shifted by (oy, oz). Each layer's least
y is the first voxel centre in front of the wall; a line through those over a window of W mm,
each at its own z, gives the slope a reader of least y per layer reads. Its error in degrees,
over a grid of lattice shifts, for the thin (0.8 across, 1.0 along) and thick (0.86, 2.5)
spacings of the cache. The period of the staircase is p / tan(rel) along the wall.

  staircase_model.py
"""
import math

import numpy as np

W = 16.2


def read(rel_deg, p, s, oy, oz, z0=-8.1):
    r = math.radians(rel_deg)
    sr, cr = math.sin(r), math.cos(r)
    zs, ys = [], []
    for k in range(-40, 41):
        j = math.ceil((k * s * sr - oy) / (p * cr) - 1e-12)
        y = j * p * cr - k * s * sr + oy
        z = j * p * sr + k * s * cr + oz
        if z0 <= z <= z0 + W:
            zs.append(z)
            ys.append(y)
    return math.degrees(math.atan(np.polyfit(zs, ys, 1)[0]))


def main():
    for name, p, s in (("thin", 0.8, 1.0), ("thick", 0.86, 2.5)):
        print("== %s: row pitch %.2f, layer pitch %.1f, window %.1f mm" % (name, p, s, W))
        for rel in (0.5, 1, 2, 3, 4, 5, 7, 10, 15, 18.9, 25, 28.8):
            errs = [read(rel, p, s, oy, oz) for oy in np.linspace(0, p, 24, endpoint=False)
                    for oz in np.linspace(0, s, 6, endpoint=False)]
            e = np.abs(errs)
            per = p / math.tan(math.radians(rel))
            print("  rel %5.1f  period %6.1f mm (window/period %.2f)  |err| max %.2f  median %.2f  mean signed %+.2f" % (
                rel, per, W / per, e.max(), float(np.median(e)), float(np.mean(errs))))


if __name__ == "__main__":
    main()
