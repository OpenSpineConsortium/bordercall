"""For named configs: the families of lattice planes nearest the true wall's plane, with their
spacing, their angle to the wall in the sagittal plane, and how many of them the wall crosses over
the span read; a family the wall crosses less than once leaves its slope free over about
2 atan(spacing / span).

  PYTHONPATH=<bordercall> python strips.py <cache_dir> limit.json key [key ...]
"""
import itertools
import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def main():
    cache, js, keys = sys.argv[1], sys.argv[2], sys.argv[3:]
    rows = {r["key"]: r for r in json.load(open(js))}
    from morphometry.tests import phantom as P
    import build_cache as BC
    for key in keys:
        r = rows[key]
        with open(os.path.join(cache, key + ".pkl"), "rb") as fh:
            rec = pickle.load(fh)
        name, lean, gname, tilt, turn, sname = rec["cfg"]
        placed = P.straight(BC.LUMBAR, P.lumbar(**BC.PHANTOMS[name]), tilt=tilt)
        pl = [p for p in placed if p.level == "L3"][0]
        Aff = np.asarray(rec["vert"].grid.affine, float)[:3, :3]
        L = pl.R.T @ Aff                       # lattice steps in the phantom's own frame (columns)
        G = np.linalg.inv(L).T                 # reciprocal: plane normals / spacing
        n_wall = np.array([0.0, 1.0, -math.tan(math.radians(lean))])
        n_wall /= np.linalg.norm(n_wall)
        span = r["span_mm"]
        found = []
        for h in itertools.product(range(-4, 5), repeat=3):
            if h == (0, 0, 0) or math.gcd(math.gcd(abs(h[0]), abs(h[1])), abs(h[2])) != 1:
                continue
            g = G @ np.array(h, float)
            d = 1.0 / np.linalg.norm(g)
            gn = g * d
            if gn @ n_wall < 0:
                gn = -gn
            # the plane family's lean in the sagittal plane against the wall's, and its turn about z
            sag = math.degrees(math.atan2(gn[2], gn[1])) - math.degrees(math.atan2(n_wall[2], n_wall[1]))
            ax = math.degrees(math.atan2(gn[0], gn[1]))
            if abs(ax) > 30 or abs(sag) > 30:
                continue
            cross = (span * abs(math.tan(math.radians(sag))) + 6.0 * abs(math.tan(math.radians(ax)))) / d
            found.append((cross, d, sag, ax, h))
        found.sort()
        f = r["fits"]["mask_curved"]
        print("%s: span %.1f mm, measured width %.2f deg" % (key, span, f["width_deg"]))
        for cross, d, sag, ax, h in found[:4]:
            print("   planes %-12s spacing %.3f mm, sagittal angle to the wall %+6.2f deg, turn %+6.2f, crossed %.2f times;"
                  " 2 atan(d/span) = %.2f deg" % (h, d, sag, ax, cross, 2 * math.degrees(math.atan(d / span))))


if __name__ == "__main__":
    main()
