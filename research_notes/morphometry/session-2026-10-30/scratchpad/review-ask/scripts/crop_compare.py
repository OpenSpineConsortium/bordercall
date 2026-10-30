"""The command's landing against what the stored render shows: each line end's pixel, the command's
in_beam and off_px (measured on the whole mask's shadow), and the distance from that pixel to the
level's support on the render FleXray made of the drawn crop, with the image's value there."""
import csv
import math
import os
import sys
from collections import defaultdict
import numpy as np
from scipy import ndimage

out = sys.argv[1]
sup = dict(zip(("L2", "L3", "L4"), np.load(os.path.join(out, "supports.npy"))))
image = np.load(os.path.join(out, "image.npy"))
rows = list(csv.DictReader(open(os.path.join(out, "projected", "lines2d.csv"))))
summary = defaultdict(lambda: [0, 0, 0, 0, []])
for r in rows:
    shadow = np.logical_or.reduce([sup[lv] for lv in r["level"].split("-")])
    edt = ndimage.distance_transform_edt(~shadow) if shadow.any() else None
    for e in "ab":
        u, v = float(r[e + "u"]), float(r[e + "v"])
        rr, cc = int(math.floor(v)), int(math.floor(u))
        on_det = 0 <= rr < 256 and 0 <= cc < 256
        s = summary[r["level"]]
        s[0] += 1
        s[1] += r[e + "_in_beam"] == "True"
        s[2] += r[e + "_off_px"] == "0.0"
        real = (float(edt[rr, cc]) if edt is not None else math.inf) if on_det else None
        s[3] += real == 0.0
        if on_det:
            s[4].append(image[rr, cc])
print("level  ends  in_beam(command)  on shadow(command)  on the render's bone  median image value at the ends")
for lv in sorted(summary):
    n, ib, on, real, vals = summary[lv]
    print("%-6s %4d  %16d  %18d  %20d  %.3f" % (lv, n, ib, on, real, float(np.median(vals)) if vals else float("nan")))
bone = image[np.logical_or.reduce(list(sup.values()))]
print("image value on rendered bone: median %.3f; off it: median %.3f" % (np.median(bone), np.median(image[~np.logical_or.reduce(list(sup.values()))])))
r = next(r for r in rows if r["level"] == "L2" and r["key"] == "h_ant")
print("L2 h_ant row:", {k: r[k] for k in ("au", "av", "a_in_beam", "a_off_px", "bu", "bv", "b_in_beam", "b_off_px", "mid_off_px")})
