"""lp_paths.py: drive the new engine's linear programs down the paths the phantoms never reach,
under whichever scipy is on the interpreter: pedicle.parting's least-crossing program (n slack
variables beside the four coefficients, a dense -eye(n) block) on centres no surface parts, at
several n, and the unbounded ends of pedicle.slope_range and body.wall_slope_range. Prints the
answers and the seconds, so two scipy versions can be set side by side.
"""
import math
import sys
import time

import numpy as np
import scipy

from morphometry import body as B
from morphometry import pedicle as PD


def tangled(n, seed):
    """Centres above and below z = 0.1 y + 0.05 x'^2 with 8 percent of them on the wrong side, so
    no surface of the family parts them and the margin program's margin is negative."""
    rng = np.random.default_rng(seed)
    y = rng.uniform(-6, 6, n)
    across = rng.uniform(-3, 3, n)
    surf = 0.1 * y + 0.05 * across ** 2
    z = surf + rng.choice([-1.0, 1.0], n) * rng.uniform(0.1, 1.5, n)
    bone = z < surf
    flip = rng.random(n) < 0.08
    return y, across, z, bone ^ flip


def main():
    print("scipy %s numpy %s" % (scipy.__version__, np.__version__))
    for n in (100, 300, 1000, 3000):
        y, across, z, bone = tangled(n, n)
        t0 = time.perf_counter()
        got = PD.parting(y, across, z, bone, True)
        dt = time.perf_counter() - t0
        if got is None:
            print("parting n=%d: None in %.3f s" % (n, dt))
        else:
            print("parting n=%d: margin %.4f, %d across, coefficients %s, freedom %s, %.3f s"
                  % (n, got["margin"], got["across"], np.round(got["coefficients"], 4),
                     tuple(round(f, 4) for f in got["freedom"]), dt))
    # every centre at one y: the slope b is free both ways (unbounded ends)
    n = 40
    rng = np.random.default_rng(1)
    across = rng.uniform(-3, 3, n)
    z = rng.uniform(-1, 1, n)
    bone = z < 0
    F = np.column_stack([np.ones(n), np.zeros(n), across, across ** 2])
    sign = np.where(bone, -1.0, 1.0)
    print("slope_range, one y:", PD.slope_range(F, sign, z))
    # the wall: bone in front (y > 0) and air behind (y < -1), every centre on one z, so the
    # wall's lean along z is free (body.wall_design's second column is z)
    bone_pts = np.column_stack([rng.uniform(-4, 4, n), rng.uniform(0.5, 3, n), np.zeros(n)])
    air_pts = np.column_stack([rng.uniform(-4, 4, n), rng.uniform(-4, -1.5, n), np.zeros(n)])
    print("wall_slope_range, one z:", B.wall_slope_range(bone_pts, air_pts, 0.0))
    # the wall over a spread of z: bounded both ways
    bone_pts[:, 2] = rng.uniform(-5, 5, n)
    air_pts[:, 2] = rng.uniform(-5, 5, n)
    print("wall_slope_range, spread z:", tuple(round(v, 4) for v in B.wall_slope_range(bone_pts, air_pts, 0.0)))
    # the wall with one speck of bone behind it: no surface parts them
    air_pts[0] = [0.0, 2.0, 0.0]
    print("wall_slope_range, a speck across:", B.wall_slope_range(bone_pts, air_pts, 0.0))


if __name__ == "__main__":
    main()
