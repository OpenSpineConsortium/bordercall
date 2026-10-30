"""Classify every bin of posterior_wall_slope on every cached phantom:

  wall   the least-y point has air (or nothing of the mask) one lattice step behind it: the bin
         caught a wall voxel
  cut    bone lies behind it but outside B: the body cut stopped B in front of the mask's wall
  alias  bone lies behind it and inside B but outside this bin's z range: the bin caught a layer
         only away from its wall voxel, the aliasing the hypothesis names
  inner  bone behind it inside B and inside the bin: cannot happen for a least y (a check)

and count bins whose wall points come from two or more lattice layers. Then print the summary
of decompose.json by spacing and by the wall's angle to the lattice.

  alias.py <cache_dir> <decompose.json>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from morphometry import body as BODY  # noqa: E402
import score as SC  # noqa: E402


def back_step(v):
    c = v.grid.axes.T @ v.frame.ey
    a = int(np.argmax(np.abs(c)))
    s = np.zeros(3, int)
    s[a] = -1 if c[a] > 0 else 1
    return s


def classify(rec):
    v, xc = rec["vert"], rec["xc"]
    B, K = v.body_pts, v.idx[v.body]
    keyset = {tuple(r) for r in K.tolist()}
    zof = {tuple(r): p[2] for r, p in zip(K.tolist(), B)}
    sel = np.abs(B[:, 0] - xc) <= BODY.ACROSS_HALF_MM
    mid, kid = B[sel], K[sel]
    z0, z1 = mid[:, 2].min(), mid[:, 2].max()
    lo, hi = z0 + 0.2 * (z1 - z0), z1 - 0.2 * (z1 - z0)
    step = max(v.fz, 0.5)
    bs = back_step(v)
    out = {"wall": 0, "cut": 0, "alias": 0, "inner": 0, "two_layers": 0, "bins": 0}
    for z in np.arange(lo, hi + 1e-9, step):
        m = np.abs(mid[:, 2] - z) <= 0.5 * step
        if not m.any():
            out["empty"] = out.get("empty", 0) + 1
            continue
        out["bins"] += 1
        L, KL = mid[m], kid[m]
        a = int(np.argmin(L[:, 1]))
        behind = tuple((KL[a] + bs).tolist())
        if not v.is_bone(np.array([behind]))[0]:
            out["wall"] += 1
        elif behind not in keyset:
            out["cut"] += 1
        elif abs(zof[behind] - z) > 0.5 * step:
            out["alias"] += 1
        else:
            out["inner"] += 1
        near = L[:, 1] <= L[a, 1] + 0.5 * v.fy
        if len(np.unique(KL[near, 2])) >= 2:
            out["two_layers"] += 1
    return out


def summary(js):
    res = json.load(open(js))
    cols = ["cur", "cur_zp", "layer", "uncut", "uncut_lay", "oracle", "canal"]
    print("\nmax |error| (degrees) by spacing, over the configs:")
    for sp in ("thin", "thick"):
        ks = [k for k in res if k.endswith(sp)]
        print("  %-5s n=%d  " % (sp, len(ks)) + "  ".join(
            "%s %.2f" % (c, max(abs(res[k][c] - res[k]["truth"]) for k in ks)) for c in cols)
            + "  phase-spread max %.2f" % max(res[k]["phase_spread"] for k in ks))
    print("\nmedian |error| by spacing:")
    for sp in ("thin", "thick"):
        ks = [k for k in res if k.endswith(sp)]
        print("  %-5s " % sp + "  ".join(
            "%s %.2f" % (c, float(np.median([abs(res[k][c] - res[k]["truth"]) for k in ks]))) for c in cols))
    print("\nby the wall's angle to the nearest lattice plane (all phantoms, both spacings):")
    buckets = [(-0.1, 0.5), (0.5, 3.5), (3.5, 7.5), (7.5, 12.5), (12.5, 40)]
    for b0, b1 in buckets:
        for sp in ("thin", "thick"):
            ks = [k for k in res if k.endswith(sp) and b0 < res[k]["rel_angle"] <= b1]
            if not ks:
                continue
            print("  rel %4.1f..%4.1f %-5s n=%2d  " % (max(b0, 0), b1, sp, len(ks)) + "  ".join(
                "%s %.2f" % (c, max(abs(res[k][c] - res[k]["truth"]) for k in ks)) for c in ("cur", "layer", "uncut", "uncut_lay", "oracle"))
                + "  cut-binds in %d configs" % sum(1 for k in ks if res[k]["cut_binds"]))
    resid = [abs(res[k]["cur"] - res[k]["truth"] - res[k]["excess_fit"]) for k in res]
    print("\n|cur error - fit of the least-y points' excess over the true wall|: max %.2f median %.2f" % (
        max(resid), float(np.median(resid))))


def main():
    cache, js = sys.argv[1], sys.argv[2]
    tot = {}
    for key, rec in SC.records(cache):
        c = classify(rec)
        for k2, n in c.items():
            tot[k2] = tot.get(k2, 0) + n
        if c["cut"] or c["alias"] or c["inner"] or c.get("empty"):
            print("%-38s %s" % (key, c))
    print("all configs:", tot)
    summary(js)


if __name__ == "__main__":
    main()
