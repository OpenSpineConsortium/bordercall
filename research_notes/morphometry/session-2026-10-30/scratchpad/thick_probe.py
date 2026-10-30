"""Feed parting() a synthetic lattice: 0.86 x 0.86 x 2.5 mm voxels, the frame tilted theta
about x against the scan; the top surface z = z0 + tan(s) * y over the isthmus rows; bone
below it. What slope and margin come out at each tilt and phase?"""
import math, sys
import numpy as np
from morphometry.pedicle import parting, SURFACE_LAYERS

def run(theta, s_deg, z0, dy=0.86, dz=2.5):
    th = math.radians(theta)
    # scan lattice (j, k) in the sagittal plane plus i across; frame y,z by rotation about x
    out = []
    for i in range(-3, 4):
        for j in range(-20, 21):
            for k in range(-6, 7):
                ys, zs = j * dy, k * dz
                y = ys * math.cos(th) - zs * math.sin(th)
                z = ys * math.sin(th) + zs * math.cos(th)
                x = i * 0.86
                out.append((x, y, z))
    p = np.array(out)
    fz = dz * math.cos(th) + dy * math.sin(th)
    surf = z0 + math.tan(math.radians(s_deg)) * p[:, 1]
    sel = (np.abs(p[:, 1]) <= 3.75) & (np.abs(p[:, 0]) <= 2.0) & (np.abs(p[:, 2] - surf) <= SURFACE_LAYERS * fz)
    p, surf = p[sel], surf[sel]
    bone = p[:, 2] < surf
    got = parting(p[:, 1], p[:, 0], p[:, 2], bone, True)
    if got is None:
        return None
    b = got["coefficients"][1]
    return math.degrees(math.atan(b)), got["margin"], got["across"], int(bone.sum()), int((~bone).sum())

for theta in (0.0, 2.0, 5.0, 10.0, 20.0):
    for s in (0.0, 10.0):
        rows = []
        for z0 in np.linspace(0.0, 2.5, 6, endpoint=False):
            r = run(theta, s, z0)
            rows.append("None" if r is None else "%6.1f deg (m %.2f, x %d, n %d/%d)" % r)
        print("tilt %4.1f truth %4.1f:" % (theta, s), " | ".join(rows))
