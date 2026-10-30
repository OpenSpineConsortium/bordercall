"""body.posterior_wall as it stands over the 98 cached clean vertebrae: the error, the gate's
reach, whether the label parts, the freedom, and how the error stands to the freedom."""
import json
import math
import os
import pickle
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)
import score as S  # noqa: E402
from morphometry import body as BODY  # noqa: E402

rows = []
for key, rec in S.records(os.path.join(WALL, "cache")):
    v = rec["vert"]
    v.__dict__.pop("_posterior_wall", None)
    B = v.body_pts
    slope, info = BODY.posterior_wall(v, B, rec["xc"])
    rings = v.full_rings()
    reach = BODY.WALL_GATE_SHARE * float(np.median([s.ap for s in rings]))
    half = min(BODY.WALL_BAND_MAX_MM, BODY.WALL_BAND_SHARE * float(np.median([s.width for s in rings])))
    t = S.wall_truth_in_frame(rec)
    err = BODY.degrees_of(slope) - t
    rows.append({"key": key, "sp": rec["cfg"][5], "err": err, "reach": reach, "half": half,
                 "parted": bool(info.get("parted")), "free": float(info.get("free_deg", math.nan)),
                 "fitted_err": info.get("fitted_deg", math.nan) - t, "why": info.get("why", ""),
                 "edges": info.get("edges"), "dropped": info.get("dropped"), "fz": v.fz, "pixel": v.pixel})
json.dump(rows, open(os.path.join(WALL, "review_words", "clean_stats.json"), "w"), indent=0, default=float)
for sp in ("thin", "thick"):
    sel = [r for r in rows if r["sp"] == sp]
    e = np.array([abs(r["err"]) for r in sel])
    print("==", sp, "n", len(sel), "max %.2f median %.2f" % (np.nanmax(e), np.nanmedian(e)),
          "refused", sum(1 for r in sel if r["why"]))
    print("  reach %.2f to %.2f, half band %.2f to %.2f" % (min(r["reach"] for r in sel), max(r["reach"] for r in sel),
                                                           min(r["half"] for r in sel), max(r["half"] for r in sel)))
    print("  parted", sum(r["parted"] for r in sel))
    print("  free > 3:", [(r["key"], round(r["free"], 2)) for r in sel if r["free"] > 3.0])
    print("  err > free/2:", [(r["key"], round(r["err"], 2), round(r["free"], 2)) for r in sel if abs(r["err"]) > 0.5 * r["free"]])
    print("  err > free:", [(r["key"], round(r["err"], 2), round(r["free"], 2)) for r in sel if abs(r["err"]) > r["free"]])
