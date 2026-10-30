"""Measure the wall band's half-width and full width against the canal's width, on the cached
phantom vertebrae and the suite's notch phantom, and compare the window's z-range trim with
quantiles of the band's body points."""
import os
import pickle
import sys

import numpy as np

from morphometry import body as BODY

CACHE = sys.argv[1]


def band_of(v, B, xc):
    rings = v.full_rings()
    w = float(np.median([s.width for s in rings]))
    place, why = BODY.wall_window(v, B, xc)
    if place is None:
        return None
    half, reach, lo, hi = place
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    e = bone + 0.5 * d
    xs = e[:, 0] - xc
    mid = B[np.abs(B[:, 0] - xc) <= half]
    qlo, qhi = np.quantile(mid[:, 2], [0.2, 0.8])
    return dict(width=w, half=half, full=2 * half, share_full=2 * half / w,
                edge_x_min=float(xs.min()), edge_x_max=float(xs.max()), edge_x_span=float(np.ptp(xs)),
                lo=lo, hi=hi, qlo=float(qlo), qhi=float(qhi))


def main():
    rows = []
    for f in sorted(os.listdir(CACHE)):
        if not f.endswith(".pkl"):
            continue
        with open(os.path.join(CACHE, f), "rb") as fh:
            rec = pickle.load(fh)
        v = rec["vert"]
        r = band_of(v, v.body_pts, rec["xc"])
        if r is None:
            print(f, "no window")
            continue
        rows.append(r)
    a = {k: np.array([r[k] for r in rows]) for k in rows[0]}
    print("cache: %d vertebrae" % len(rows))
    print("canal width   %.2f to %.2f mm" % (a["width"].min(), a["width"].max()))
    print("half (code)   %.2f to %.2f mm; capped at 6 on %d" % (a["half"].min(), a["half"].max(), int((a["half"] >= 6.0 - 1e-9).sum())))
    print("full band     %.2f to %.2f mm, share of canal width %.3f to %.3f"
          % (a["full"].min(), a["full"].max(), a["share_full"].min(), a["share_full"].max()))
    print("edges' x from midline: min %.2f max %.2f, span %.2f to %.2f mm"
          % (a["edge_x_min"].min(), a["edge_x_max"].max(), a["edge_x_span"].min(), a["edge_x_span"].max()))
    d_lo, d_hi = a["lo"] - a["qlo"], a["hi"] - a["qhi"]
    print("window lo minus 20%% quantile of band points' z: %.2f to %.2f mm; hi minus 80%%: %.2f to %.2f mm"
          % (d_lo.min(), d_lo.max(), d_hi.min(), d_hi.max()))


if __name__ == "__main__":
    main()
