import json, sys, time, csv
import numpy as np
from scipy import ndimage
sys.path.insert(0, "/home/user/bordercall")
from morphoview.projection import Camera, View
from morphoview.shapes import Volume
from morphoview.tests import flexray_record as FR
d = json.load(open(sys.argv[1]))
t0 = time.time()
lab, aff = FR.phantom()
print("phantom %.1f s; sha matches: %s" % (time.time() - t0, FR.digest(lab, aff) == d["phantom"]["sha256"]))
lines = [r for r in csv.DictReader(open(sys.argv[2])) if r["status"] == "drawn"]
ids = d["phantom"]["ids"]
for v in d["views"]:
    view = View(**{k: (tuple(x) if isinstance(x, list) else x) for k, x in v["view"].items()})
    cam = Camera(view)
    shape = (view.height, view.width)
    sup, msk = {}, {}
    for lv, i in ids.items():
        t1 = time.time()
        ours = Volume.from_labels(lab, aff, i, largest=False).silhouette(cam, n_samples=d["n_samples"])
        theirs = FR.unpack(v["supports"][lv], shape)
        sup[lv], msk[lv] = theirs, FR.unpack(v["masks"][lv], shape)
        diff = ours ^ theirs
        edge = theirs ^ ndimage.binary_erosion(theirs)
        near_edge = ndimage.binary_dilation(edge)
        print("%s %s: ours %d theirs %d differ %d (%.3f%%), all at the edge: %s; touches border: %s; %.1f s" % (
            v["name"][:12], lv, ours.sum(), theirs.sum(), diff.sum(), 100.0 * diff.sum() / theirs.sum(),
            bool((diff <= near_edge).all()), bool(theirs[0].any() or theirs[-1].any() or theirs[:, 0].any() or theirs[:, -1].any()),
            time.time() - t1))
    worst_sup, worst_msk = 0.0, 0.0
    off = []
    for r in lines:
        a = np.array([float(r["ax"]), float(r["ay"]), float(r["az"])]); b = np.array([float(r["bx"]), float(r["by"]), float(r["bz"])])
        levels = r["level"].split("-")
        S_ = np.zeros(shape, bool); M_ = np.zeros(shape, bool)
        for lv in levels:
            S_ |= sup[lv]; M_ |= msk[lv]
        dS = ndimage.distance_transform_edt(~S_); dM = ndimage.distance_transform_edt(~M_)
        for name, p in (("a", a), ("b", b), ("mid", 0.5 * (a + b))):
            pr = cam.project(p[None])
            rr, cc = pr.pixels()[0]
            if not (0 <= rr < shape[0] and 0 <= cc < shape[1]):
                off.append((r["level"], r["key"], name, "off detector")); continue
            worst_sup = max(worst_sup, dS[rr, cc]); worst_msk = max(worst_msk, dM[rr, cc])
            if dS[rr, cc] > 1.0:
                off.append((r["level"], r["key"], r["part"], name, round(float(dS[rr, cc]), 2)))
    print("  lines %d: worst px from support %.2f, from FleXray's mask %.2f; off support by >1 px: %s" % (len(lines), worst_sup, worst_msk, off[:6]))
