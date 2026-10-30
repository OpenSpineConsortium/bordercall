"""On the same synthetic lattice as thick_probe.py: the max-margin slope beside the interval of
slopes that still part bone from air (two LPs, min b and max b under margin >= 0), at 2.5 mm
slices with small tilts and at 1 mm slices tilted 18 degrees, as the prototype's phantoms were."""
import math
import numpy as np
from scipy.optimize import linprog
from morphometry.pedicle import parting, SURFACE_LAYERS

def lattice(theta, s_deg, z0, dy, dz):
    th = math.radians(theta)
    out = []
    for i in range(-3, 4):
        for j in range(-24, 25):
            for k in range(-14, 15):
                ys, zs = j * dy, k * dz
                y = ys * math.cos(th) - zs * math.sin(th)
                z = ys * math.sin(th) + zs * math.cos(th)
                out.append((i * dy, y, z))
    p = np.array(out)
    fz = dz * math.cos(th) + dy * math.sin(th)
    surf = z0 + math.tan(math.radians(s_deg)) * p[:, 1]
    sel = (np.abs(p[:, 1]) <= 3.75) & (np.abs(p[:, 0]) <= 2.0) & (np.abs(p[:, 2] - surf) <= SURFACE_LAYERS * fz)
    p = p[sel]
    return p, p[:, 2] < surf[sel]

def interval(p, bone):
    y, across, z = p[:, 1], p[:, 0], p[:, 2]
    F = np.column_stack([np.ones_like(y), y, across, across ** 2])
    sign = np.where(bone, -1.0, 1.0)
    lo = linprog(c=[0, 1, 0, 0], A_ub=sign[:, None] * F, b_ub=sign * z, bounds=[(None, None)] * 4, method="highs")
    hi = linprog(c=[0, -1, 0, 0], A_ub=sign[:, None] * F, b_ub=sign * z, bounds=[(None, None)] * 4, method="highs")
    if not (lo.success and hi.success):
        return None
    return math.degrees(math.atan(lo.x[1])), math.degrees(math.atan(hi.x[1]))

for dy, dz, tilts in ((0.86, 2.5, (0.0, 3.0, 8.0)), (0.8, 1.0, (18.0,))):
    for theta in tilts:
        for s in (0.0, 10.0):
            cells = []
            for z0 in np.linspace(0.0, dz, 4, endpoint=False):
                p, bone = lattice(theta, s, z0, dy, dz)
                got = parting(p[:, 1], p[:, 0], p[:, 2], bone, True)
                iv = interval(p, bone)
                cells.append("%5.1f in [%5.1f, %5.1f] m %.2f" % (math.degrees(math.atan(got["coefficients"][1])), iv[0], iv[1], got["margin"])
                             if got and iv else "none")
            print("%.1f mm slices tilt %4.1f truth %4.1f: " % (dz, theta, s) + " | ".join(cells))
