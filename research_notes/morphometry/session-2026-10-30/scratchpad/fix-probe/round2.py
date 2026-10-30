"""Round two on the phantoms: each frame's axis and turn on the chain, the ends' names, and how
many keys a straight L3's rows hold against the keys drawn there."""
import csv, math, os, sys, tempfile
import numpy as np
from morphometry.tests import test_lines_export as T
from morphoview import lines as LN

def read(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))

tmp = tempfile.mkdtemp()
masks, out = os.path.join(tmp, "masks"), os.path.join(tmp, "out")
os.makedirs(masks)
T.chain_masks(masks)
T.run(["run", "--masks", masks, "--scheme", "verse", "--out", out, "--workers", "1", "--lines"])
frames = {r["level"]: r for r in read(os.path.join(out, "frames.csv"))}
rows = read(os.path.join(out, "rows.csv"))
for lv in T.LEVELS:
    f = frames[lv]
    ez = np.array([float(f["ez" + a]) for a in "xyz"])
    c = np.array([float(f["c" + a]) for a in "xyz"])
    turn = math.degrees(math.acos(min(1.0, float(ez @ c))))
    flags = [r["key"] for r in rows if r["level"] == lv and r["key"].startswith("flag:axis")]
    off = [r["value"] for r in rows if r["level"] == lv and r["key"] in ("axis_offset", "axis_residual")]
    print("chain", lv, f["axis"], "turn %.3f" % turn, flags, off)
lines = read(os.path.join(out, "lines.csv"))
bad = 0
for r in lines:
    f = frames[r["level"].split("-")[-1]]
    o = np.array([float(f["o" + a]) for a in "xyz"])
    R = np.array([[float(f[e + a]) for a in "xyz"] for e in ("ex", "ey", "ez")])
    a = R @ (np.array([float(r["a" + k]) for k in "xyz"]) - o)
    b = R @ (np.array([float(r["b" + k]) for k in "xyz"]) - o)
    names = (r["a_end"], r["b_end"])
    if names == ("medial", "lateral"):
        ok = abs(b[0]) > abs(a[0]); margin = abs(b[0]) - abs(a[0])
    else:
        axis, sign = T.ORDER[names]
        margin = sign * (b[axis] - a[axis]); ok = margin > 0
    if not ok or margin < 1.0:
        bad += 1
        print("ends", r["level"], r["key"], r["part"], names, r["status"], "margin %.3f" % margin)
print("chain lines", len(lines), "with a margin under 1 mm or wrong:", bad)
by = {}
for r in lines:
    by.setdefault(r["level"], set()).add(r["key"])
for lv in sorted(by):
    print("chain keys", lv, len(by[lv]))

tmp2 = tempfile.mkdtemp()
m2, o2 = os.path.join(tmp2, "masks"), os.path.join(tmp2, "out")
os.makedirs(m2)
T.masks(m2)
T.run(["run", "--masks", m2, "--scheme", "verse", "--out", o2, "--workers", "1", "--lines"])
rows = [r for r in read(os.path.join(o2, "rows.csv")) if r["study"] == "0001"]
lines = [r for r in read(os.path.join(o2, "lines.csv")) if r["study"] == "0001" and r["part"] == ""]
for lv in ("L3", "L2-L3"):
    keys = [r["key"] for r in rows if r["level"] == lv and not r["key"].startswith("flag")]
    finite = [r["key"] for r in rows if r["level"] == lv and not r["key"].startswith("flag") and r["value"] not in ("", "nan")]
    drawn = sorted({r["key"] for r in lines if r["level"] == lv})
    print("straight", lv, "keys", len(keys), "finite", len(finite), "drawn", len(drawn),
          "drawn not in keys", sorted(set(drawn) - set(keys)), "flags", [r["key"] for r in rows if r["level"] == lv and r["key"].startswith("flag")])
