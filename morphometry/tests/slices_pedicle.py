"""Run with PYTHONPATH set to the repository. Pictures of a vertebra's mask in its own frame: axial slabs at several heights and coronal
slabs at several places front to back, each voxel centre a dot, with the pedicle reading's
rows and walls drawn over them.

  slices.py <labels.nii.gz> <level> <out.png> [z1,z2,...] [y1,y2,...]
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
import numpy as np                # noqa: E402

from morphometry import anatomy as A, measure as M, pedicle as PED, canal as CANAL   # noqa: E402
from scanimport import volume as V, LEVELS                                           # noqa: E402

labels, lv, out = sys.argv[1], sys.argv[2], sys.argv[3]
zs = [float(t) for t in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[4] else None
ys = [float(t) for t in sys.argv[5].split(",")] if len(sys.argv) > 5 and sys.argv[5] else None

vol, grid, names, problems, _ = V.read_labels(labels, "enhance")
vox = V.vertebra_voxels(vol, names)
for k in list(vox):
    vox[k], _ = M.main_piece(vox[k])
order = [k for k in LEVELS if k in vox]
spine = [k for k in order if k != "sacrum"]
cents = [grid.world(vox[k].astype(float)).mean(0) for k in spine]
whole = M.whole_levels(vox, spine, vol.shape)
axes = dict(zip(spine, M.column_line(cents, whole, grid.superior())))
v = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], vol.shape), M.neighbours_of(vox, order, lv))
zb = CANAL.body_span(v)
za = PED.anchors(v, zb)[0]
P = v.loc
if zs is None:
    zs = [za - 6, za - 3, za, za + 3, za + 6, za + 9]
if ys is None:
    ys = [v.wall - 2, v.wall - 5, v.wall - 8, v.wall - 11]
got, flags, info = PED.measures(v, zb)
fig, ax = plt.subplots(2, max(len(zs), len(ys)), figsize=(4 * max(len(zs), len(ys)), 8))
for j, z in enumerate(zs):
    a = ax[0, j]
    sel = np.abs(P[:, 2] - z) <= 0.5 * v.fz
    a.scatter(P[sel, 0], P[sel, 1], s=4, c="0.3")
    body = sel & v.body
    a.scatter(P[body, 0], P[body, 1], s=4, c="tab:orange")
    a.axhline(v.wall, color="g", lw=0.5)
    a.axhline(v.wall_post, color="g", lw=0.5)
    a.axvline(v.midline, color="g", lw=0.5)
    for name, inf in info.items():
        if name == "band":
            continue
        m = inf["map"]
        for i in inf["near"]:
            r = inf["rows"][i]
            if abs(r["z"] - z) <= 0.5 * v.fz + 0.01 or j == 0:
                a.plot([m.x_of(r["u0"]), m.x_of(r["u1"])], [r["y"], r["y"]], c="r", lw=1)
        c = inf["centre"]
        a.plot(c[0], c[1], "b+", ms=8)
    a.set_title("%s axial z=%.1f (anchor %.1f)" % (lv, z, za), fontsize=9)
    a.set_aspect("equal")
    a.set_xlim(-45, 45)
    a.set_ylim(-35, 35)
for j, y in enumerate(ys):
    a = ax[1, j]
    sel = np.abs(P[:, 1] - y) <= 0.75 * v.pixel
    a.scatter(P[sel, 0], P[sel, 2], s=4, c="0.3")
    body = sel & v.body
    a.scatter(P[body, 0], P[body, 2], s=4, c="tab:orange")
    a.axhline(za, color="g", lw=0.5)
    a.axvline(v.midline, color="g", lw=0.5)
    for name, inf in info.items():
        if name == "band":
            continue
        m = inf["map"]
        for i in inf["near"]:
            r = inf["rows"][i]
            if abs(r["y"] - y) <= 0.75 * v.pixel + 0.01:
                a.plot([m.x_of(r["u0"]), m.x_of(r["u1"])], [r["z"], r["z"]], c="r", lw=1)
                a.plot([r["x"], r["x"]], [r["run"][0], r["run"][1]], c="m", lw=1)
    a.set_title("%s coronal y=%.1f (wall %.1f)" % (lv, y, v.wall), fontsize=9)
    a.set_aspect("equal")
    a.set_xlim(-45, 45)
    a.set_ylim(-30, 30)
for j in range(len(zs), ax.shape[1]):
    ax[0, j].axis("off")
for j in range(len(ys), ax.shape[1]):
    ax[1, j].axis("off")
fig.suptitle("%s: w %.1f h %.1f t %.1f s %.1f  ip %.1f max %.1f  flags %s" % (
    lv, got.get("pedicle_w", np.nan), got.get("pedicle_h", np.nan), got.get("pedicle_angle_transverse", np.nan),
    got.get("pedicle_angle_sagittal", np.nan), (PED.band(info) or {}).get("interpedicular", np.nan),
    (PED.band(info) or {}).get("interpedicular_max", np.nan), list(flags)), fontsize=9)
fig.tight_layout()
fig.savefig(out, dpi=80)
print("wrote", out)
