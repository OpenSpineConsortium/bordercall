"""Does the wall's freedom bound its error? On the cached phantom L3s, clean and altered as the
judge's robust.py alters them, read body.posterior_wall as it stands in the tree and count, apart
for labels that part and labels that do not: the truth inside [free_lo, free_hi], |err| within
the freedom and within half of it (the flag's words), and how often the flag and the refusal fire.

  coverage.py <out.json> <alt,alt,...> [<index> <count>]"""
import json
import math
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = os.path.dirname(HERE)
sys.path.insert(0, WALL)
sys.path.insert(0, os.path.join(WALL, "judge"))
os.environ["READERS"] = "current"

import score as S  # noqa: E402
import robust as R  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def one(rec, alt):
    v = rec["vert"] if alt == "clean" else R.altered(rec, alt)
    B = v.body_pts
    xc = rec["xc"] if alt == "clean" else 0.5 * (B[:, 0].min() + B[:, 0].max())
    v.__dict__.pop("_posterior_wall", None)
    s, info = BODY.posterior_wall(v, B, xc)
    t = S.wall_truth_in_frame(rec)
    row = {"alt": alt, "spacing": rec["cfg"][5], "truth": t, "why": info.get("why", "")}
    for k in ("parted", "free_lo_deg", "free_hi_deg", "free_deg", "fitted_deg"):
        if k in info:
            row[k] = float(info[k])
    row["err"] = BODY.degrees_of(s) - t if math.isfinite(s) else float("nan")
    return row


def main():
    out, alts = sys.argv[1], sys.argv[2].split(",")
    keys = sorted(f[:-4] for f in os.listdir(os.path.join(WALL, "cache")) if f.endswith(".pkl"))
    if len(sys.argv) > 4:
        keys = keys[int(sys.argv[3])::int(sys.argv[4])]
    rows = []
    for key in keys:
        with open(os.path.join(WALL, "cache", key + ".pkl"), "rb") as fh:
            rec = pickle.load(fh)
        for alt in alts:
            row = one(rec, alt)
            row["key"] = key
            rows.append(row)
    with open(out, "w") as f:
        json.dump(rows, f)


if __name__ == "__main__":
    main()
