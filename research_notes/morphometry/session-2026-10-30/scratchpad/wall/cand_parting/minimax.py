"""A variant fallback for the record: where nothing parts, read the widest-margin program as it
stands, its margin negative, i.e. the surface of least worst crossing (Chebyshev), the middle of
the slopes at that margin, instead of the least-total-crossing surface. Scored on the perturbed
phantoms beside the candidate."""
import math, os, pickle, sys
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import perturb as PB  # noqa: E402
C = PB.C
import score as S  # noqa: E402


def minimax(v, B, xc):
    q, bone = C.region(v, B, xc)
    F = np.column_stack([np.ones(len(q)), q[:, 2], q[:, 0], q[:, 0] ** 2])
    sign = np.where(bone, 1.0, -1.0); y = q[:, 1]
    m, coef = C.widest_margin(F, sign, y)
    lo, hi = C.slopes_at(F, sign, y, m - 1e-7)
    return 0.5 * (lo + hi), m


print("\n# minimax fallback")
for key in PB.KEYS:
    rec = pickle.load(open(os.path.join(os.path.dirname(here), "cache", key + ".pkl"), "rb"))
    t = S.wall_truth_in_frame(rec)
    for name, change in PB.CHANGES.items():
        va, Ba = PB.altered(rec, change)
        b, m = minimax(va, Ba, rec["xc"])
        b1, info = C.slope(va, Ba, rec["xc"])
        e1 = math.degrees(math.atan(b1)) - t if math.isfinite(b1) else float("nan")
        print("%-28s %-46s minimax err %+6.2f margin %+.2f mm (row %.2f) | candidate %+6.2f %s" % (
            key, name, math.degrees(math.atan(b)) - t, m, va.fy, e1, "refused" if "why" in info else ""))
