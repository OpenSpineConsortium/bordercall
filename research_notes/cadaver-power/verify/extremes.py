# Copied for the cadaver-power note from the reviewers' verify-verify-arithmetic/ct-error-assumed/extremes.py,
# 2026-10-28. Changed: bordercall's checkout became the argument below, where it was an absolute path.
#     python3 -I verify/extremes.py BORDERCALL
"""Which cells give the 51 and the 1,988 of README item 1, and the median at 3x (the archive's noise_mm=3 world)."""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
from schwingcheck import LEVELS, measures as MS  # noqa: E402
pool = MS.pool()
mu, sd = MS.arrays(pool)
e = MS.errors(pool)[:, None]
n = 2000.0 / (1.0 + (e / sd) ** 2)
order = np.argsort(n, axis=None)
for idx in list(order[:3]) + list(order[-3:]):
    i, j = np.unravel_index(idx, n.shape)
    print("%-26s %-6s %-4s sd %.3f e %.2f -> cadavers %.1f" % (pool[i].key, pool[i].kind, LEVELS[j], sd[i, j], e[i, 0], n[i, j]))
print("cells by kind:", {k: int(sum(sd.shape[1] for m in pool if m.kind == k)) for k in ("length", "area", "angle")})
for scale in (3.0,):
    nn = 2000.0 / (1.0 + (scale * e / sd) ** 2)
    print("errors x%.0f: median %.0f (min %.1f, max %.0f)" % (scale, np.median(nn), nn.min(), nn.max()))
