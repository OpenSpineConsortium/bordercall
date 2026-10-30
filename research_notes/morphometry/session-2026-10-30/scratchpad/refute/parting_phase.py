"""Call pedicle.parting on a synthetic lattice: a slab of bone (the pedicle) between two
parallel flat surfaces of true slope s, sampled on layers fz apart at a phase, under columns
over rows 0..span (half a pixel apart) and across x' (a pixel apart). For each surface the
centres within SURFACE_LAYERS of that column's own quantised surface, as lattice_under takes
them. Prints each surface's LP slope in degrees, its margin, and the mean climb's angle."""
import math, sys
import numpy as np
from morphometry import pedicle as PED

def run(fz, s_deg, phase_top, height=12.0, span=7.5, pixel=0.8):
    s = math.tan(math.radians(s_deg))
    ys = np.arange(0.0, span + 1e-9, 0.5 * pixel)
    xs = np.arange(-2.0, 2.0 + 1e-9, pixel)
    out = {}
    for top in (True, False):
        Y, X, Z, B = [], [], [], []
        for y in ys:
            ztop = phase_top + s * y
            zbot = ztop - height
            for x in xs:
                # the lattice's centres along z: k*fz
                ks = np.arange(math.floor((zbot - 3 * fz) / fz), math.ceil((ztop + 3 * fz) / fz) + 1)
                zc = ks * fz
                bone = (zc > zbot) & (zc < ztop)
                if not bone.any():
                    continue
                # the column's own quantised surface: midway between the last bone centre and the next air centre
                if top:
                    kb = np.flatnonzero(bone).max(); surf = 0.5 * (zc[kb] + zc[kb + 1])
                else:
                    kb = np.flatnonzero(bone).min(); surf = 0.5 * (zc[kb] + zc[kb - 1])
                keep = np.abs(zc - surf) <= PED.SURFACE_LAYERS * fz
                for z, b in zip(zc[keep], bone[keep]):
                    Y.append(y); X.append(x); Z.append(z); B.append(b)
        got = PED.parting(np.array(Y), np.array(X), np.array(Z), np.array(B), top)
        out["top" if top else "bottom"] = got
    st, sb = out["top"]["coefficients"][1], out["bottom"]["coefficients"][1]
    mean = 0.5 * (st + sb)
    print("fz %.2f truth %4.1f deg phase %.2f | top %6.2f deg (m %.3f across %d) bottom %6.2f deg (m %.3f across %d) | mean %6.2f deg  error %5.2f" % (
        fz, s_deg, phase_top, math.degrees(math.atan(st)), out["top"]["margin"], out["top"]["across"],
        math.degrees(math.atan(sb)), out["bottom"]["margin"], out["bottom"]["across"],
        math.degrees(math.atan(mean)), math.degrees(math.atan(mean)) - s_deg))

for fz in (1.24, 2.0, 3.0):
    for s_deg in (0.0, 3.0, 5.0):
        for phase in np.linspace(0.0, fz, 6, endpoint=False):
            run(fz, s_deg, float(phase))
    print()
