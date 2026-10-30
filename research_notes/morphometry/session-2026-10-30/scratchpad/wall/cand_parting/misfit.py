"""Where the crossers of the least-crossing surface lie along the window, on the perturbed
phantoms: their signed first moment in z (mm), the window's half-length, and the lean in degrees
that the set-aside centres' crossing depths would give a line fitted to them alone (sum c z' /
sum z'^2 over the centres about the wall). A diagnostic for a guard, not part of the reader."""
import math, os, pickle, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import perturb as PB  # noqa: E402  (runs its table first)
C = PB.C


def moments(v, B, xc):
    q, bone = C.region(v, B, xc)
    F = np.column_stack([np.ones(len(q)), q[:, 2], q[:, 0], q[:, 0] ** 2])
    sign = np.where(bone, 1.0, -1.0); y = q[:, 1]
    m, coef = C.widest_margin(F, sign, y)
    if m > 0:
        return None
    c = C.least_crossing(F, sign, y)
    near = np.abs(y - F @ coef) <= C.NEAR_ROWS * v.fy
    z = q[:, 2]
    across = c > 1e-9
    signed = np.where(bone, -c, c)       # bone behind pulls the wall back, the canal in front pulls it forward
    lean = math.degrees(math.atan(np.sum(signed[near] * z[near]) / np.sum(z[near] ** 2)))
    return across.sum(), float(np.mean(z[across])) if across.any() else 0.0, 0.5 * np.ptp(z), lean


print("\n# misfit moments")
for key in PB.KEYS:
    rec = pickle.load(open(os.path.join(os.path.dirname(here), "cache", key + ".pkl"), "rb"))
    for name, change in PB.CHANGES.items():
        va, Ba = PB.altered(rec, change)
        got = moments(va, Ba, rec["xc"])
        if got is None:
            print("%-30s %-46s parted" % (key, name)); continue
        n, zbar, half, lean = got
        print("%-30s %-46s across %4d mean z' %+5.1f of +-%.1f, misfit lean %+5.2f" % (key, name, n, zbar, half, lean))
