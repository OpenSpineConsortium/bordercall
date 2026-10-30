"""Does the wall's error stay within half its freedom, as wall_flags's text and the
WALL_FREE_FLAG_DEG constant assume? Read on the 98 cached phantom vertebrae."""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)

import score as S  # noqa: E402
from morphometry import body as BODY  # noqa: E402

cache = os.path.join(WALL, "cache")
over_half = []
over_flagless = []
n = 0
for key, rec in S.records(cache):
    v = rec["vert"]
    v.__dict__.pop("_posterior_wall", None)
    B = v.body_pts
    slope, info = BODY.posterior_wall(v, B, rec["xc"])
    if not math.isfinite(slope):
        continue
    n += 1
    err = BODY.degrees_of(slope) - S.wall_truth_in_frame(rec)
    free = info["free_deg"]
    if abs(err) > 0.5 * free:
        over_half.append((key, err, free))
    if free <= BODY.WALL_FREE_FLAG_DEG and abs(err) > 0.5 * BODY.WALL_FREE_FLAG_DEG:
        over_flagless.append((key, err, free))
print("read", n)
print("error beyond half the freedom:", len(over_half))
for key, err, free in sorted(over_half, key=lambda r: -abs(r[1]) / r[2]):
    print("  %-40s err %+.2f free %.2f ratio %.2f" % (key, err, free, abs(err) / free))
print("unflagged with error beyond 1.5:", len(over_flagless))
