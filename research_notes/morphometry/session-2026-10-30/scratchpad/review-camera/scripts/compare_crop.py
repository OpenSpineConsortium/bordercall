"""The command's landing beside FleXray's own channels and image at each end's pixel."""
import csv, math, sys
import numpy as np
from scipy import ndimage
C = sys.argv[1]
fx = np.load(C + "/flexray_support.npz")
for r in csv.DictReader(open(C + "/out/lines2d.csv")):
    lv = r["level"]
    sup = fx[lv]
    for e in "ab":
        u, v = float(r[e + "u"]), float(r[e + "v"])
        rr, cc = int(math.floor(v)), int(math.floor(u))
        off_fx = float(ndimage.distance_transform_edt(~sup)[rr, cc]) if sup.any() else float("inf")
        print("%s end %s: px (%d, %d) in_beam %s, command off %s px; FleXray: %s channel there %s, nearest support %s px, image %.4g (image max %.4g)"
              % (lv, e, rr, cc, r[e + "_in_beam"], r[e + "_off_px"], lv, bool(sup[rr, cc]), off_fx, fx["image"][rr, cc], fx["image"].max()))
