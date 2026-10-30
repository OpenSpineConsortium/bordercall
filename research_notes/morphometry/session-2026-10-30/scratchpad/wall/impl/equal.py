"""The reader now in body.py against the judge's proposed.py on every cached phantom vertebra:
slopes, refusals and the record's numbers; with the gate's reach in mm, the iterations the trimmed
fit and the biweight take, and the Newton residual where the fitted surface crosses a scan line.

  PYTHONPATH=<bordercall> python equal.py <cache_dir> <proposed.py>
"""
import importlib.util
import math
import os
import pickle
import sys

import numpy as np

from morphometry import body as BODY


def load(path):
    spec = importlib.util.spec_from_file_location("proposed", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def iterations(X, y, z, scale):
    """How many concentration steps the slowest start of the trimmed fit took, and how many
    biweight rounds, with the bodies of body.trimmed_start and body.biweight."""
    n = len(y)
    h = max(int(BODY.WALL_TRIM_KEEP * n), 8)
    order = np.argsort(z)
    worst = 0
    for sub in [order] + [order[i * n // 4:(i + 2) * n // 4] for i in range(3)]:
        coef = np.linalg.lstsq(X[sub], y[sub], rcond=None)[0]
        for k in range(1, 1000):
            idx = np.argsort((y - X @ coef) ** 2)[:h]
            new = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
            done = np.allclose(new, coef, atol=1e-10)
            coef = new
            if done:
                break
        worst = max(worst, k)
    coef = BODY.trimmed_start(X, y, z)
    for r in range(1, 1000):
        u = (y - X @ coef) / scale
        w = np.where(np.abs(u) < 1.0, (1.0 - u * u) ** 2, 0.0)
        sw = np.sqrt(w)
        new = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        done = np.allclose(new, coef, atol=1e-9)
        coef = new
        if done:
            break
    return worst, r, coef


def crossing_residual(bone, d, coef, xc):
    a, b, c, dd = coef
    x = bone[:, 0] - xc
    t = np.zeros(len(bone))
    for _ in range(BODY.WALL_CROSSING_STEPS):
        px, pz = x + t * d[0], bone[:, 2] + t * d[2]
        g = bone[:, 1] + t * d[1] - (a + b * pz + c * px + dd * px * px)
        dg = d[1] - (b * d[2] + c * d[0] + 2.0 * dd * px * d[0])
        t = t - g / dg
    px, pz = x + t * d[0], bone[:, 2] + t * d[2]
    g = bone[:, 1] + t * d[1] - (a + b * pz + c * px + dd * px * px)
    return float(np.abs(g).max())


def main():
    cache, proposed = sys.argv[1], load(sys.argv[2])
    worst = {"slope": 0.0, "info": 0.0, "refusal_mismatch": 0}
    reach, steps, rounds, resid = [], [], [], []
    for f in sorted(os.listdir(cache)):
        if not f.endswith(".pkl"):
            continue
        rec = pickle.load(open(os.path.join(cache, f), "rb"))
        v, xc = rec["vert"], rec["xc"]
        B = v.body_pts
        mine, minfo = BODY.posterior_wall(v, B, xc)
        theirs, tinfo = proposed.posterior_wall(v, B, xc)
        if math.isfinite(mine) != math.isfinite(theirs) or minfo.get("why") != tinfo.get("why"):
            worst["refusal_mismatch"] += 1
            print("MISMATCH", f, mine, theirs, minfo.get("why"), tinfo.get("why"))
            continue
        if math.isfinite(mine):
            worst["slope"] = max(worst["slope"], abs(mine - theirs))
        for k, x in tinfo.items():
            if isinstance(x, float) and math.isfinite(x):
                worst["info"] = max(worst["info"], abs(x - minfo[k]))
            elif minfo[k] != x and not (isinstance(x, float) and math.isnan(x) and math.isnan(minfo[k])):
                print("INFO", f, k, x, minfo[k])
        place, _ = BODY.wall_window(v, B, xc)
        half, r, lo, hi = place
        reach.append(r)
        bone, d = BODY.wall_edges(v, xc, half, lo, hi, r)
        e = bone + 0.5 * d
        X = BODY.wall_design(e, xc)
        k, n, coef = iterations(X, e[:, 1], e[:, 2], BODY.WALL_BIWEIGHT_STEPS * abs(d[1]))
        steps.append(k)
        rounds.append(n)
        good = np.abs(e[:, 1] - X @ coef) <= abs(d[1])
        resid.append(crossing_residual(bone[good], d, coef, xc))
    print("largest slope difference", worst["slope"], "largest record difference", worst["info"],
          "refusals told apart", worst["refusal_mismatch"])
    print("gate reach mm: min %.2f median %.2f max %.2f" % (min(reach), float(np.median(reach)), max(reach)))
    print("concentration steps of the slowest start: max %d median %d" % (max(steps), int(np.median(steps))))
    print("biweight rounds: max %d median %d" % (max(rounds), int(np.median(rounds))))
    print("Newton residual after %d steps: max %.3g mm" % (BODY.WALL_CROSSING_STEPS, max(resid)))


if __name__ == "__main__":
    main()
