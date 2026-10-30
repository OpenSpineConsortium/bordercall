"""Random damage to the wall's voxels on the 98 cached phantom vertebrae, to look for exceptions
(linprog, lstsq) and for readings accepted, unflagged, far from the truth. Each trial removes a
share of the label's voxels within 3 mm of the wall's line in the band and window, adds specks of
bone up to 4 mm behind it, or both, and reads the wall again on the altered label with the canal
and frame kept.

  fuzz.py <trials per vertebra> <seed> [<index> <count>]"""
import math
import os
import sys
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)

import score as S  # noqa: E402
from morphometry import anatomy as A, body as BODY  # noqa: E402


def altered(v, keep, extra_idx):
    """A copy of v whose label is v's kept voxels and the extra voxel indices."""
    w = A.Vertebra(**{f: getattr(v, f) for f in v.__dataclass_fields__})
    idx = np.vstack([v.idx[keep], extra_idx]) if len(extra_idx) else v.idx[keep]
    loc = v.frame.local(v.grid.world(idx.astype(float)))
    n_extra = len(idx) - int(keep.sum())
    w.idx, w.loc = idx, loc
    w.body = np.concatenate([v.body[keep], np.zeros(n_extra, bool)])
    w.touching = np.concatenate([v.touching[keep], np.zeros(n_extra, bool)])
    return w


def specks(v, rng, xc, share):
    """Voxel indices just behind the wall's voxels, up to 4 mm, a share of them."""
    sq = A.square_to_wall(v, v.loc)
    near = (np.abs(v.loc[:, 0] - xc) <= 6.0) & (np.abs(sq[:, 1] - v.wall_y0) <= 1.5) & v.body
    base = v.idx[near]
    if not len(base):
        return np.zeros((0, 3), int)
    w = int(np.argmax(np.abs(v.grid.axes.T @ v.frame.ey)))
    sign = -1 if v.grid.axes[:, w] @ v.frame.ey > 0 else 1
    step = np.zeros(3, int)
    step[w] = sign
    k = rng.integers(1, 1 + max(1, int(4.0 / v.grid.spacing[w])), size=len(base))
    cand = base + k[:, None] * step
    pick = rng.random(len(cand)) < share
    out = np.unique(cand[pick], axis=0)
    return out[~v.is_bone(out)]


def trial(v, rng, xc, kind):
    sq = A.square_to_wall(v, v.loc)
    zone = (np.abs(v.loc[:, 0] - xc) <= 6.0) & (np.abs(sq[:, 1] - v.wall_y0) <= 3.0)
    keep = np.ones(len(v.idx), bool)
    extra = np.zeros((0, 3), int)
    if kind in ("drop", "both"):
        p = rng.uniform(0.05, 0.5)
        keep &= ~(zone & (rng.random(len(keep)) < p))
    if kind in ("speck", "both"):
        extra = specks(v, rng, xc, rng.uniform(0.02, 0.3))
    return altered(v, keep, extra)


def main():
    n_trials, seed = int(sys.argv[1]), int(sys.argv[2])
    part = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 1)
    rng = np.random.default_rng(seed)
    raised, rows = 0, []
    for i, (key, rec) in enumerate(S.records(os.path.join(WALL, "cache"))):
        if i % part[1] != part[0]:
            continue
        v, xc = rec["vert"], rec["xc"]
        truth = S.wall_truth_in_frame(rec)
        for t in range(n_trials):
            kind = ("drop", "speck", "both")[t % 3]
            w = trial(v, rng, xc, kind)
            try:
                s, info = BODY.read_wall(w, w.body_pts, xc)
            except Exception:
                raised += 1
                print("RAISED", key, kind, t)
                traceback.print_exc()
                continue
            if not math.isfinite(s):
                rows.append((key, kind, float("nan"), info.get("free_deg", float("nan")), info["why"]))
                continue
            rows.append((key, kind, BODY.degrees_of(s) - truth, info["free_deg"], ""))
    read = [r for r in rows if math.isfinite(r[2])]
    print("trials %d raised %d refused %d read %d" % (len(rows) + raised, raised, len(rows) - len(read), len(read)))
    unflagged = [r for r in read if r[3] <= BODY.WALL_FREE_FLAG_DEG]
    for lim in (1.0, 1.5, 2.0, 3.0):
        print("  unflagged with |err| > %.1f: %d of %d" % (lim, sum(abs(r[2]) > lim for r in unflagged), len(unflagged)))
    print("  beyond the freedom itself: %d; beyond half of it: %d" % (
        sum(abs(r[2]) > r[3] for r in read), sum(abs(r[2]) > 0.5 * r[3] for r in read)))
    for r in sorted(unflagged, key=lambda r: -abs(r[2]))[:8]:
        print("  %-40s %-5s err %+.2f free %.2f" % r[:4])


if __name__ == "__main__":
    main()
