"""The lines export of the phantom carried onto the three recorded views, with the numbers the
note gives: ends on the shadow, the construction's places, the discs' midpoints, the mask."""
import contextlib, csv, io, json, math, os, sys, tempfile, time
import nibabel as nib
import numpy as np
from scipy import ndimage
from morphometry import __main__ as RUN
from morphoview import __main__ as MV
from morphoview import projection as PJ
from morphoview.tests import flexray_record as FR

R = json.load(open(FR.FIXTURE))
lab, aff = FR.phantom()
tmp = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()
masks = os.path.join(tmp, "masks"); os.makedirs(masks, exist_ok=True)
mask = os.path.join(masks, "0001.nii.gz")
nib.save(nib.Nifti1Image(lab.astype(np.int16), aff), mask)
run = os.path.join(tmp, "run")
with contextlib.redirect_stdout(io.StringIO()):
    RUN.main(["run", "--masks", masks, "--scheme", "verse", "--out", run, "--workers", "1", "--lines"])
lines, frames = os.path.join(run, "lines.csv"), os.path.join(run, "frames.csv")
rows = list(csv.DictReader(open(lines)))
print("rows", len(rows), "status", sorted({r["status"] for r in rows}), "levels", sorted({r["level"] for r in rows}))

def support(v, levels, key="supports"):
    shape = (v["view"]["height"], v["view"]["width"])
    return np.logical_or.reduce([FR.unpack(v[key][lv], shape) for lv in levels])

def off(shadow, u, vv):
    r, c = int(math.floor(vv)), int(math.floor(u))
    return float(ndimage.distance_transform_edt(~shadow)[r, c])

def construction(row, end):
    if row["key"] != "canal_ap_lateral_film":
        return False
    return row["part"] == "apex to apex" or end in ("a", "mid")

for k, v in enumerate(R["views"]):
    path = os.path.join(tmp, "view%d.json" % k)
    json.dump(dict(v["view"], n_samples=R["n_samples"]), open(path, "w"))
    out = os.path.join(tmp, "projected%d" % k)
    t = time.time()
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        MV.main(["project", "--lines", lines, "--frames", frames, "--view", path, "--labels", mask, "--scheme", "verse", "--out", out])
    dt = time.time() - t
    got = list(csv.DictReader(open(os.path.join(out, "lines2d.csv"))))
    print("\n== %s: %.1f s; %s" % (v["name"], dt, said.getvalue().strip()))
    plain, cons, discmid, maskoff, midoff = [], [], [], [], []
    for row, line in zip(rows, got):
        if row["status"] != "drawn":
            continue
        levels = row["level"].split("-")
        shadow = support(v, levels)
        fmask = support(v, levels, "masks")
        for e in "ab":
            d = off(shadow, float(line[e + "u"]), float(line[e + "v"]))
            dm = off(fmask, float(line[e + "u"]), float(line[e + "v"]))
            maskoff.append((dm, d, row["level"], row["key"], row["part"], e))
            (cons if construction(row, e) else plain).append((d, row["level"], row["key"], row["part"], e))
        mid = 0.5 * (np.array([float(line["au"]), float(line["av"])]) + np.array([float(line["bu"]), float(line["bv"])]))
        dmid = off(shadow, *mid)
        if "-" in row["level"]:
            discmid.append((dmid, row["level"], row["key"], row["part"], float(line["mid_off_px"])))
        else:
            midoff.append((dmid, construction(row, "mid"), row["level"], row["key"], row["part"]))
    print("plain ends: n %d, max off %.3f, how many > 0: %d" % (len(plain), max(p[0] for p in plain), sum(p[0] > 0 for p in plain)))
    print("plain ends > 0:", sorted([p for p in plain if p[0] > 0], reverse=True)[:8])
    print("construction ends:", sorted(cons, reverse=True))
    print("disc midpoints (on the render, mid_off_px):", [(round(d[0], 3), d[1], d[2], d[3], round(d[4], 3)) for d in discmid])
    print("vertebra midpoints: max non-construction %.3f; construction mids %s" % (
        max(m[0] for m in midoff if not m[1]), sorted([round(m[0], 3) for m in midoff if m[1]])))
    on_shadow = [m for m in maskoff if m[1] == 0]
    print("ends on the shadow: %d; their distance to FleXray's mask: max %.3f; > 0: %d" % (
        len(on_shadow), max(m[0] for m in on_shadow), sum(m[0] > 0 for m in on_shadow)))
    print("largest mask distances:", sorted(maskoff, reverse=True)[:5])
