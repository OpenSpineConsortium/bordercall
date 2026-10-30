"""Does parting() pin the slope at 2.5 mm slices? A synthetic lattice built as lattice_under
selects it: scanner voxel centres rotated by theta about x into the frame, a planar top
surface z = z0 + tan(s) y, bone below; per scanner column the read surface is the top bone
centre + fz/2 (G.surface), and the centres kept are those within SURFACE_LAYERS * fz of it.
Beside the max-margin slope: the interval [min b, max b] of slopes that still part the sets."""
import math
import numpy as np
from scipy.optimize import linprog
from morphometry.pedicle import parting, SURFACE_LAYERS

def run(theta, s_deg, z0, dy=0.86, dz=2.5, half_span=3.75):
    th = math.radians(theta)
    fz = dz * math.cos(th) + dy * math.sin(th)
    pts, col = [], []
    for i in range(-3, 4):
        for j in range(-30, 31):
            for k in range(-10, 11):
                ys, zs = j * dy, k * dz
                y = ys * math.cos(th) - zs * math.sin(th)
                z = ys * math.sin(th) + zs * math.cos(th)
                pts.append((i * dy, y, z)); col.append((i, j))
    p, col = np.array(pts), np.array(col)
    surf = z0 + math.tan(math.radians(s_deg)) * p[:, 1]
    bone = p[:, 2] < surf
    # each scanner column's own read surface: its top bone centre + fz/2 (the frame-z of that centre)
    keep = np.zeros(len(p), bool)
    for (i, j) in set(map(tuple, col)):
        m = (col[:, 0] == i) & (col[:, 1] == j)
        zb = p[m & bone, 2]
        if not len(zb):
            continue
        top = zb.max() + 0.5 * fz
        keep |= m & (np.abs(p[:, 2] - top) <= SURFACE_LAYERS * fz)
    keep &= (np.abs(p[:, 1]) <= half_span) & (np.abs(p[:, 0]) <= 2.0)
    q, b = p[keep], bone[keep]
    got = parting(q[:, 1], q[:, 0], q[:, 2], b, True)
    F = np.column_stack([np.ones(len(q)), q[:, 1], q[:, 0], q[:, 0] ** 2])
    sign = np.where(b, -1.0, 1.0)
    lo = linprog(c=[0, 1, 0, 0], A_ub=sign[:, None] * F, b_ub=sign * q[:, 2], bounds=[(None, None)] * 4, method="highs")
    hi = linprog(c=[0, -1, 0, 0], A_ub=sign[:, None] * F, b_ub=sign * q[:, 2], bounds=[(None, None)] * 4, method="highs")
    deg = lambda v: math.degrees(math.atan(v))
    return (deg(got["coefficients"][1]), got["margin"], got["across"], int(b.sum()), int((~b).sum()),
            deg(lo.x[1]) if lo.success else float("nan"), deg(hi.x[1]) if hi.success else float("nan"))

print("2.5 mm layers, span 7.5 mm; cells: angle read (margin, across, bone/air) in [min, max] feasible")
for theta in (0.0, 3.0, 8.0, 20.0):
    for s in (0.0, 10.0):
        cells = []
        for z0 in np.linspace(0.0, 2.5, 5, endpoint=False):
            r = run(theta, s, z0)
            cells.append("%5.1f (m%.2f x%d %d/%d) [%5.1f,%5.1f]" % r)
        print("tilt %4.1f truth %4.1f: " % (theta, s) + " | ".join(cells))
print()
print("1 mm layers (0.8 px), span 7.5 mm, as the prototype's phantoms")
for theta in (10.0, 18.0):
    for s in (0.0, 10.0):
        cells = []
        for z0 in np.linspace(0.0, 1.0, 4, endpoint=False):
            r = run(theta, s, z0, dy=0.8, dz=1.0)
            cells.append("%5.1f (m%.2f) [%5.1f,%5.1f]" % (r[0], r[1], r[5], r[6]))
        print("tilt %4.1f truth %4.1f: " % (theta, s) + " | ".join(cells))
