"""What the lines and frames files give per level, against the rows."""
import csv
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

RUN = sys.argv[1]


def read(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


rows = read(os.path.join(RUN, "rows.csv"))
lines = read(os.path.join(RUN, "lines.csv"))
frames = read(os.path.join(RUN, "frames.csv"))

print("columns lines:", list(lines[0].keys()) if lines else None)
print("columns frames:", list(frames[0].keys()) if frames else None)

# 1. per (study, level): main lines, extra rows, statuses
per = defaultdict(lambda: Counter())
for r in lines:
    k = (r["study"], r["level"])
    per[k]["main" if r["part"] == "" else "extra"] += 1
    if r["part"] == "":
        per[k][r["status"].split(":")[0]] += 1
for k in sorted(per):
    print(k, dict(per[k]))

# 2. duplicates of the join key
dup = Counter((r["study"], r["level"], r["key"], r["part"]) for r in lines)
print("duplicate (study, level, key, part):", [k for k, n in dup.items() if n > 1])
dup3 = Counter((r["study"], r["level"], r["key"]) for r in lines)
print("(study, level, key) seen more than once (main plus its parts):",
      sorted({k[2] for k, n in dup3.items() if n > 1}))

# 3. keys with a finite row value and no line, per vertebra level
vals = defaultdict(dict)
for r in rows:
    if r["key"].startswith("flag") or r["level"] in ("study", "column", "pelvis"):
        continue
    try:
        v = float(r["value"])
    except ValueError:
        continue
    vals[(r["study"], r["level"])][r["key"]] = v
lined = defaultdict(set)
for r in lines:
    if r["part"] == "":
        lined[(r["study"], r["level"])].add(r["key"])
for k in sorted(vals):
    finite = {key for key, v in vals[k].items() if math.isfinite(v)}
    print(k, "finite row keys", len(finite), "with a line", len(finite & lined[k]),
          "lines drawn", sum(1 for r in lines if (r["study"], r["level"]) == k and r["part"] == "" and r["status"] == "drawn"))
k0 = ("0001", "L3")
finite = {key for key, v in vals[k0].items() if math.isfinite(v)}
print("L3 of 0001, finite keys without a line:", sorted(finite - lined[k0]))
print("L3 of 0001, keys with a line:", sorted(lined[k0]))
for key in ("h_post", "canal_w", "canal_ap"):
    print("  row value of", key, "at 0001 L3:", vals[k0].get(key), "line?", key in lined[k0])

# 4. frames: orthonormal after rounding, and the flags the rows give on the axis
flags = defaultdict(dict)
for r in rows:
    if r["key"].startswith("flag:"):
        flags[(r["study"], r["level"])][r["key"]] = r["note"]
for f in frames:
    R = np.array([[float(f[p + a]) for a in "xyz"] for p in ("ex", "ey", "ez")])
    o = np.array([float(f["o" + a]) for a in "xyz"])
    k = (f["study"], f["level"])
    off = vals[k].get("axis_offset")
    print(k, "|R R'-I| %.1e" % np.abs(R @ R.T - np.eye(3)).max(), "det %.6f" % np.linalg.det(R),
          "axis_offset", off, "axis flags", {n: v[:60] for n, v in flags[k].items() if "axis" in n})
