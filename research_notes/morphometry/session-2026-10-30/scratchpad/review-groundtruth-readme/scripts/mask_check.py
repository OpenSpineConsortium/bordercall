"""The canal rows set against FleXray's label mask (channels above 0.5) as well as its support."""
import json, math, sys
import numpy as np
from scipy import ndimage
from morphoview.tests import flexray_record as FR
OUT = sys.argv[1]
R = json.load(open(FR.FIXTURE))
T = json.load(open(OUT + "/landing.json"))
import csv
views = {v["name"]: v for v in R["views"]}
def unpack(v, key, levels):
    shape = (v["view"]["height"], v["view"]["width"])
    return np.logical_or.reduce([FR.unpack(v[key][lv], shape) for lv in levels])
def off(sh, u, vv):
    r, c = int(math.floor(vv)), int(math.floor(u))
    return float(ndimage.distance_transform_edt(~sh)[r, c])
for k, v in enumerate(R["views"]):
    rows = list(csv.DictReader(open(OUT + "/projected%d/lines2d.csv" % k)))
    for line in rows:
        if line["key"] != "canal_ap_lateral_film":
            continue
        lv = line["level"].split("-")
        mask = unpack(v, "masks", lv)
        sup = unpack(v, "supports", lv)
        a = (float(line["au"]), float(line["av"])); b = (float(line["bu"]), float(line["bv"]))
        m = (0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1]))
        print("%-12s %-3s %-13s cmd a/b/mid=%s/%s/%s  support a/b/mid=%.2f/%.2f/%.2f  mask a/b/mid=%.2f/%.2f/%.2f" % (
            v["name"][:12], line["level"], line["part"] or "(line)", line["a_off_px"], line["b_off_px"], line["mid_off_px"],
            off(sup, *a), off(sup, *b), off(sup, *m), off(mask, *a), off(mask, *b), off(mask, *m)))
