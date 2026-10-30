"""Centres on a lattice whose widest parting margin is set by hand: what the range's programs
answer, as wall_slope_range asks them now and as it asked them before this pass.

  margin_probe.py
"""
import math

import numpy as np
from scipy.optimize import linprog

from morphometry import body as BODY


def centres(m0):
    x, z = np.meshgrid(np.arange(-4.0, 4.1, 0.8), np.arange(-6.0, 6.1, 1.0))
    x, z = x.ravel(), z.ravel()
    bone = np.column_stack([x, np.zeros(len(x)), z])
    air = np.column_stack([x, -np.ones(len(x)), z])
    speck = np.array([[0.0, -1.0 + 2.0 * m0, 0.0]])
    partner = np.array([[0.0, -1.0, 0.0]])
    return np.vstack([bone, speck]), np.vstack([air, partner])


def old_programs(bone, air):
    A, b = BODY.wall_programme(bone, air, 0.0)
    out = []
    for c in ([0.0, 1.0, 0.0, 0.0], [0.0, -1.0, 0.0, 0.0]):
        res = linprog(c=c, A_ub=A, b_ub=b - BODY.WALL_PART_MM, bounds=[(None, None)] * 4, method="highs")
        out.append((res.status, None if res.x is None else float(res.x[1])))
    return out


def main():
    for m0 in (2e-6, 1.05e-6, 1e-6, 0.99e-6, 0.95e-6, 0.9e-6, 0.5e-6, 1e-7, 1e-8, 0.0):
        bone, air = centres(m0)
        print("m0 %.3g: now %s, before %s" % (m0, BODY.wall_slope_range(bone, air, 0.0), old_programs(bone, air)))


if __name__ == "__main__":
    main()
