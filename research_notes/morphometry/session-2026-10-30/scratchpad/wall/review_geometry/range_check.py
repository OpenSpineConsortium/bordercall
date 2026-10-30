"""For each cached vertebra: the wall reading, its record, the truth in the measured frame, and
whether the truth lies inside the parted range (the clamp's premise) and within half the freedom
(the flag's wording)."""
import math
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def main():
    rows = []
    for key, rec in score.records(os.path.join(WALL, "cache")):
        v = rec["vert"]
        B = v.body_pts
        slope, info = BODY.posterior_wall(v, B, rec["xc"])
        truth = score.wall_truth_in_frame(rec)
        got = BODY.degrees_of(slope) if np.isfinite(slope) else float("nan")
        err = got - truth
        lo, hi = info.get("free_lo_deg", float("nan")), info.get("free_hi_deg", float("nan"))
        inside = lo - 1e-9 <= truth <= hi + 1e-9
        rows.append((key, err, info.get("parted"), lo, hi, info.get("free_deg"), truth, got,
                     info.get("fitted_deg"), inside, info.get("why", "")))
        print("%-42s err %+6.2f parted %-5s range [%+7.2f, %+7.2f] free %5.2f truth %+6.2f got %+6.2f fit %+6.2f in %s %s"
              % (key, err, info.get("parted"), lo, hi, info.get("free_deg", float("nan")), truth, got,
                 info.get("fitted_deg", float("nan")), inside, info.get("why", "")), flush=True)
    parted = [r for r in rows if r[2]]
    out = [r for r in parted if not r[9]]
    print("parted %d; truth outside the parted range %d" % (len(parted), len(out)))
    for r in out:
        print("  outside:", r[0], "truth %+.3f range [%+.3f, %+.3f] err %+.2f" % (r[6], r[3], r[4], r[1]))
    half = [r for r in rows if np.isfinite(r[1]) and abs(r[1]) > 0.5 * r[5]]
    print("|err| > free/2: %d of %d" % (len(half), len(rows)))
    flagged = [r for r in rows if r[5] is not None and r[5] > BODY.WALL_FREE_FLAG_DEG]
    for r in flagged:
        print("  flagged:", r[0], "free %.2f err %+.2f" % (r[5], r[1]))


if __name__ == "__main__":
    main()
