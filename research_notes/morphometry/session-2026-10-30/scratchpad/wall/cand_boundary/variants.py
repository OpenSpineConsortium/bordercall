"""Variants of candidate C on the whole cache, to say which of its parts carry the result.

  PYTHONPATH=<bordercall> python variants.py ../cache ../diag_limit/limit.json > variants.txt

Each variant changes one thing: the x terms of the plane (none, c x, c x + d x^2), the trimming,
the set read as inside (the label, or B as the canal line cut it), every entry on a scan line
against the most posterior only. The truth is score.py's (the wall taken into the measured frame).
The information limit's curved range per config (diag_limit/limit.json) says whether a reading
lies inside the slopes the mask allows.
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import score as S  # noqa: E402
import cand as C   # noqa: E402
import cand_crack as K  # noqa: E402

ORIGINAL_PAIRS = C.wall_pairs


def body_box_test(v):
    """is_bone's twin for B: whether each voxel index is one of the body's (the cut body)."""
    lo = v.idx.min(0)
    box = np.zeros(tuple(v.idx.max(0) - lo + 1), bool)
    box[tuple((v.idx[v.body] - lo).T)] = True

    def inside(ijk):
        rel = ijk - lo
        ok = ((rel >= 0) & (rel < np.array(box.shape))).all(1)
        out = np.zeros(len(ijk), bool)
        out[ok] = box[tuple(rel[ok].T)]
        return out
    return inside


def pairs_on_body(v, xc, z_lo, z_hi):
    """The same pairs with B as inside: entries from outside B into B, from B's points only."""
    keep_idx, keep_loc = v.idx, v.loc
    try:
        v.idx, v.loc = keep_idx[v.body], keep_loc[v.body]
        v.is_bone = body_box_test_cached[id(v)]
        return ORIGINAL_PAIRS(v, xc, z_lo, z_hi)
    finally:
        v.idx, v.loc = keep_idx, keep_loc
        del v.is_bone


body_box_test_cached = {}


def pairs_every_entry(v, xc, z_lo, z_hi):
    step, axis, step_f = C.nearest_step(v)
    half = C.canal_half_depth(v)
    q = v.loc
    off_line = q[:, 1] - (v.wall_y0 + v.wall_slope * (q[:, 2] - v.wall_z0))
    mid = q + 0.5 * step_f
    near = ((np.abs(mid[:, 0] - xc) <= C.ACROSS_HALF_MM) & (mid[:, 2] >= z_lo) & (mid[:, 2] <= z_hi)
            & (np.abs(off_line) <= half))
    entry = ~v.is_bone(v.idx[near] + step)
    return mid[near][entry], step_f


def run(rec, variant):
    v = rec["vert"]
    B = v.body_pts
    if "crack_floor" in variant:
        K.H_FLOOR_MM = variant["crack_floor"]
        got, info = K.slope(v, B, rec["xc"])
        K.H_FLOOR_MM = 0.05
        return math.degrees(math.atan(got)), info
    C.X_TERMS, C.TRIM_ROUNDS = variant.get("x_terms", 2), variant.get("trim", 3)
    C.wall_pairs = variant.get("pairs", ORIGINAL_PAIRS)
    if variant.get("pairs") is pairs_on_body:
        body_box_test_cached[id(v)] = body_box_test(v)
    try:
        got, info = C.slope(v, B, rec["xc"])
    finally:
        C.wall_pairs = ORIGINAL_PAIRS
        C.X_TERMS, C.TRIM_ROUNDS = 2, 3
    deg = math.degrees(math.atan(got)) if np.isfinite(got) else float("nan")
    if variant.get("clamp") and np.isfinite(info.get("range_deg", NAN)):
        deg = min(max(deg, info["range_lo_deg"]), info["range_hi_deg"])
    return deg, info


NAN = float("nan")


VARIANTS = {
    "C (label, x+x^2, trim)": {},
    "no x terms": {"x_terms": 0},
    "c x only": {"x_terms": 1},
    "no trimming": {"trim": 0},
    "every entry per line": {"pairs": pairs_every_entry},
    "inside = B (cut)": {"pairs": pairs_on_body},
    "clamped into own range": {"clamp": True},
    "risers too, floor 0.02": {"crack_floor": 0.02},
    "risers too, floor 0.05": {"crack_floor": 0.05},
    "risers too, floor 0.10": {"crack_floor": 0.10},
    "risers too, floor 0.20": {"crack_floor": 0.20},
    "risers too, floor 0.40": {"crack_floor": 0.40},
}


def main():
    cache, limit_path = sys.argv[1], sys.argv[2]
    limit = {r["key"]: r for r in json.load(open(limit_path))}
    recs = list(S.records(cache))
    truths = {k: S.wall_truth_in_frame(r) for k, r in recs}
    table = {}
    for name, variant in VARIANTS.items():
        errs, inside, beyond_half = {"thin": [], "thick": []}, 0, 0
        t0 = time.perf_counter()
        per = {}
        for key, rec in recs:
            deg, info = run(rec, variant)
            e = deg - truths[key]
            errs[rec["cfg"][5]].append(abs(e))
            per[key] = (deg, e, info)
            lim = limit[key]["fits"]["mask_curved"]
            if abs(limit[key]["truth_dir_deg"] - truths[key]) > 0.01:
                print("truth differs", key, limit[key]["truth_dir_deg"], truths[key])
            if lim["lo_deg"] - 1e-6 <= deg <= lim["hi_deg"] + 1e-6:
                inside += 1
        dt = (time.perf_counter() - t0) / len(recs)
        table[name] = per
        print("%-26s thin max %5.2f median %4.2f | thick max %5.2f median %4.2f | inside the mask's range %2d/98 | %.1f ms"
              % (name, np.nanmax(errs["thin"]), np.nanmedian(errs["thin"]), np.nanmax(errs["thick"]),
                 np.nanmedian(errs["thick"]), inside, 1000 * dt))
    print()
    print("Per config, C against the information limit (curved family, diag_limit/limit.json):")
    print("%-40s %7s %7s %7s %7s %7s %6s" % ("config", "truth", "C", "C err", "lo", "hi", "inside"))
    worse_than_half = 0
    for key, rec in recs:
        deg, e, info = table["C (label, x+x^2, trim)"][key]
        lim = limit[key]["fits"]["mask_curved"]
        half = 0.5 * (lim["hi_deg"] - lim["lo_deg"])
        ins = lim["lo_deg"] - 1e-6 <= deg <= lim["hi_deg"] + 1e-6
        worse_than_half += abs(e) > half + 1e-6
        print("%-40s %+7.2f %+7.2f %+7.2f %+7.2f %+7.2f %6s  half-width %.2f" % (
            key, truths[key], deg, e, lim["lo_deg"], lim["hi_deg"], "yes" if ins else "NO", half))
    print("C's |error| exceeds the range's half-width (the least worst case any reader can promise) in %d of 98"
          % worse_than_half)


if __name__ == "__main__":
    main()
