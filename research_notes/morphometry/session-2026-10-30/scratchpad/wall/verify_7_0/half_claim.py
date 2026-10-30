"""Does the free-wall flag's "off by up to half that" hold? body.posterior_wall as it stands in the
working tree, over the 98 cached clean phantom vertebrae: the wall's error against the truth in the
measured frame, the freedom, whether the truth and the reading lie in the range the clamp uses, where
in that range each lies (0 its low end, 1 its high end), and the downstream angles' errors."""
import json
import math
import os
import pickle
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
OUT = os.path.join(WALL, "verify_7_0")
sys.path.insert(0, WALL)
import score as S  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def place(x, lo, hi):
    return (x - lo) / (hi - lo) if hi > lo else math.nan


rows = []
for key, rec in S.records(os.path.join(WALL, "cache")):
    v = rec["vert"]
    v.__dict__.pop("_posterior_wall", None)
    slope, info = BODY.posterior_wall(v, v.body_pts, rec["xc"])
    t = S.wall_truth_in_frame(rec)
    deg = BODY.degrees_of(slope)
    lo, hi = info.get("free_lo_deg", math.nan), info.get("free_hi_deg", math.nan)
    down = S.downstream(dict(rec, wall_truth_deg=rec["wall_truth_deg"]), deg) if math.isfinite(deg) else {}
    rows.append({"key": key, "sp": rec["cfg"][5], "err": deg - t, "free": info.get("free_deg", math.nan),
                 "lo": lo, "hi": hi, "parted": bool(info.get("parted")), "why": info.get("why", ""),
                 "truth_in": lo - 1e-9 <= t <= hi + 1e-9, "read_at": place(deg, lo, hi), "truth_at": place(t, lo, hi),
                 "fitted_at": place(info.get("fitted_deg", math.nan), lo, hi),
                 "down": {k: x for k, x in down.items() if math.isfinite(x)}})
json.dump(rows, open(os.path.join(OUT, "half_claim.json"), "w"), indent=0, default=float)

for sp in ("thin", "thick"):
    sel = [r for r in rows if r["sp"] == sp and math.isfinite(r["err"])]
    part = [r for r in sel if r["parted"]]
    print("== %s: %d read, %d parted, truth inside the range on %d of the parted" % (
        sp, len(sel), len(part), sum(r["truth_in"] for r in part)))
    print("   |err| > free/2: %d   |err| > free: %d" % (
        sum(abs(r["err"]) > 0.5 * r["free"] for r in sel), sum(abs(r["err"]) > r["free"] for r in sel)))
    ratio = np.array([abs(r["err"]) / r["free"] for r in sel])
    print("   |err|/free: max %.2f median %.2f" % (ratio.max(), np.median(ratio)))
    at = np.array([r["read_at"] for r in part])
    print("   reading's place in the range (parted): min %.2f median %.2f max %.2f; at an end (<0.01 or >0.99): %d" % (
        at.min(), np.median(at), at.max(), int(((at < 0.01) | (at > 0.99)).sum())))
    worst = sorted(sel, key=lambda r: -abs(r["err"]) / r["free"])[:4]
    for r in worst:
        print("   %-40s err %+5.2f free %4.2f range [%+6.2f, %+6.2f] read at %.2f truth at %.2f parted %s" % (
            r["key"], r["err"], r["free"], r["lo"], r["hi"], r["read_at"], r["truth_at"], r["parted"]))
    flagged = [r for r in sel if r["free"] > BODY.WALL_FREE_FLAG_DEG]
    for r in flagged:
        print("   flagged %-32s err %+5.2f free %4.2f half %4.2f downstream %s" % (
            r["key"], r["err"], r["free"], 0.5 * r["free"],
            " ".join("%s %+.2f" % kv for kv in r["down"].items())))
    dn = [(r["key"], k, x, r["free"]) for r in sel for k, x in r["down"].items() if abs(x) > 0.5 * r["free"]]
    print("   downstream angle readings off by more than half the freedom: %d of %d" % (
        len(dn), sum(len(r["down"]) for r in sel)))
