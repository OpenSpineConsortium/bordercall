"""Scattered single-voxel holes in the bone just inside the posterior wall, as a label resampled,
stacked from overlapping masks or thresholded shows: a share p of the label's voxels within 3 mm in
front of the wall, in the band and the window, taken out at random. An edge must stand at the back
of WALL_RUN_MM of solid bone, so one hole within 3 mm of the wall on a scan line moves that line's
edge in front of the hole. Read on the 98 cached vertebrae by body.posterior_wall and by the
reading it replaced (old_slope, a9f21fd), three seeds per share.

  probe_specks.py <share> [<index> <count>]"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)
sys.path.insert(0, HERE)

import score as S  # noqa: E402
from fuzz import altered  # noqa: E402
from morphometry import anatomy as A, body as BODY  # noqa: E402
from probe_label_edits import old_slope  # noqa: E402


def holes_in_front(v, xc, p, rng):
    sq = A.square_to_wall(v, v.loc)
    behind_wall = sq[:, 1] - v.wall_y0
    zone = (np.abs(v.loc[:, 0] - xc) <= 6.0) & (behind_wall >= 0.0) & (behind_wall <= 3.0)
    keep = ~(zone & (rng.random(len(v.idx)) < p))
    return altered(v, keep, np.zeros((0, 3), int))


def main():
    p = float(sys.argv[1])
    part = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
    rows = []
    for i, (key, rec) in enumerate(S.records(os.path.join(WALL, "cache"))):
        if i % part[1] != part[0]:
            continue
        truth = S.wall_truth_in_frame(rec)
        for seed in range(3):
            rng = np.random.default_rng(1000 * i + seed)
            w = holes_in_front(rec["vert"], rec["xc"], p, rng)
            B = w.body_pts
            s, info = BODY.read_wall(w, B, rec["xc"])
            new = BODY.degrees_of(s) - truth if math.isfinite(s) else float("nan")
            old = BODY.degrees_of(old_slope(w, B, rec["xc"])) - truth
            rows.append((key, new, old, info.get("free_deg", float("nan")), info.get("why", "")))
    for thick in ("thin", "thick"):
        sel = [r for r in rows if r[0].endswith(thick)]
        new = np.array([r[1] for r in sel])
        old = np.array([r[2] for r in sel])
        ok = np.isfinite(new)
        free = np.array([r[3] for r in sel])
        unflagged = ok & (free <= BODY.WALL_FREE_FLAG_DEG)
        print("p %.2f %-5s n %d refused %d | new |err| max %.2f median %.2f, unflagged > 1.5: %d | old |err| max %.2f median %.2f"
              % (p, thick, len(sel), int((~ok).sum()), np.abs(new[ok]).max(), np.median(np.abs(new[ok])),
                 int((unflagged & (np.abs(new) > 1.5)).sum()), np.abs(old).max(), np.median(np.abs(old))), flush=True)
        worst = sorted([r for r in sel if math.isfinite(r[1])], key=lambda r: -abs(r[1]))[:3]
        for r in worst:
            print("    %-40s new %+.2f old %+.2f free %.2f" % r[:4])


if __name__ == "__main__":
    main()
