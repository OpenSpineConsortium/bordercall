"""How far the frame's z (the column's line through the neighbours) lies from each vertebra's own
axis, by several readings of that axis, on one study; and sections of C5 and L5 square to each."""
import math
import os
import sys

import numpy as np
from scipy import ndimage

from morphometry import anatomy as A
from morphometry import body as BODY
from morphometry import measure as M
from scanimport import LEVELS
from scanimport import geometry as G
from scanimport import volume as V

OUT = sys.argv[1] if len(sys.argv) > 1 else ""
LABELS = sys.argv[2] if len(sys.argv) > 2 else ""
WANT = sys.argv[3:] or ["C3", "C4", "C5", "C6", "C7", "T1", "T8", "L3", "L4", "L5"]


def theil(z, w):
    i, j = np.triu_indices(len(z), 1)
    far = np.abs(z[j] - z[i]) >= 3.0
    if far.sum() < 3:
        return 0.0
    return float(np.median((w[j] - w[i])[far] / (z[j] - z[i])[far]))


def layer_centres(B, fz):
    zs = np.round(B[:, 2] / fz) * fz
    out = []
    for z in np.unique(zs):
        sel = zs == z
        if sel.sum() >= 20:
            out.append((z, B[sel, 0].mean(), B[sel, 1].mean(), B[sel, 1].min()))
    return np.array(out)


def candidates(v):
    B = v.body_pts
    got = {"column": v.frame.ez}
    bis = A.plate_axis(v)
    if bis is not None:
        got["plate bisector"] = bis
    tops = [BODY.plate_points(B, v.pixel, top) for top in (True, False)]
    if all(len(t) >= 6 for t in tops):
        got["plate centres"] = G.unit(v.to_world(tops[0].mean(0) - tops[1].mean(0)))
    L = layer_centres(B, v.fz)
    if len(L) >= 4:
        core = L[(L[:, 0] > np.percentile(L[:, 0], 15)) & (L[:, 0] < np.percentile(L[:, 0], 85))]
        if len(core) >= 4:
            got["layer centroids"] = G.unit(v.to_world(np.array([theil(core[:, 0], core[:, 1]), theil(core[:, 0], core[:, 2]), 1.0])))
            got["posterior wall"] = G.unit(v.to_world(np.array([theil(core[:, 0], core[:, 1]), theil(core[:, 0], core[:, 3]), 1.0])))
    W = v.points_world(B)
    c = np.cov((W - W.mean(0)).T)
    vals, vecs = np.linalg.eigh(c)
    e = vecs[:, 0]
    got["body PCA least"] = G.unit(e if e @ v.frame.ez > 0 else -e)
    return got


def deg(a, b):
    return math.degrees(math.acos(min(1.0, abs(float(a @ b)))))


def section(vol, grid, frame, z0, half=36.0, step=0.4):
    xs = np.arange(-half, half + step, step)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    P = frame.origin + X.ravel()[:, None] * frame.ex + Y.ravel()[:, None] * frame.ey + z0 * frame.ez
    aff = np.asarray(grid.affine, float)
    idx = (P - aff[:3, 3]) @ np.linalg.inv(aff[:3, :3]).T
    lab = ndimage.map_coordinates(vol, idx.T, order=0, mode="constant", cval=0)
    return lab.reshape(X.shape), xs


def sagittal(vol, grid, frame, x0, half=36.0, step=0.4):
    ys = np.arange(-half, half + step, step)
    Y, Z = np.meshgrid(ys, ys, indexing="ij")
    P = frame.origin + x0 * frame.ex + Y.ravel()[:, None] * frame.ey + Z.ravel()[:, None] * frame.ez
    aff = np.asarray(grid.affine, float)
    idx = (P - aff[:3, 3]) @ np.linalg.inv(aff[:3, :3]).T
    lab = ndimage.map_coordinates(vol, idx.T, order=0, mode="constant", cval=0)
    return lab.reshape(Y.shape), ys


def draw(ax, lab, xs, mine, title):
    img = np.where(lab == mine, 0.75, np.where(lab > 0, 0.95, 1.0))
    ax.imshow(img.T, cmap="gray", vmin=0, vmax=1, origin="lower", extent=[xs[0], xs[-1], xs[0], xs[-1]])
    ax.contour((lab > 0).T.astype(float), levels=[0.5], colors="k", linewidths=0.5, extent=[xs[0], xs[-1], xs[0], xs[-1]], origin="lower")
    ax.set_title(title, fontsize=8)
    ax.set_xticks([]); ax.set_yticks([])


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    vol, grid, names, _, _ = V.read_labels(LABELS, "enhance")
    ids = {lv: i for i, lv in names.items()}
    vox = V.vertebra_voxels(vol, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    spine = [lv for lv in order if lv != "sacrum"]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in spine]
    whole = M.whole_levels(vox, spine, vol.shape)
    axes = dict(zip(spine, M.column_line(cents, whole, grid.superior())))
    print("level  " + "  ".join("%-16s" % n for n in ("plate bisector", "plate centres", "layer centroids", "posterior wall", "body PCA least")))
    for lv in WANT:
        if lv not in vox:
            continue
        v = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], vol.shape))
        if not A.usable(v):
            print(lv, "unusable", v.flags.get("all"))
            continue
        got = candidates(v)
        line = "%-5s " % lv
        for n in ("plate bisector", "plate centres", "layer centroids", "posterior wall", "body PCA least"):
            line += "  %-16s" % ("%.1f deg" % deg(got["column"], got[n]) if n in got else "-")
        print(line)
        if lv in ("C5", "L5", "C3"):
            B = v.body_pts
            zc = float(np.median(B[:, 2]))
            zt = float(np.percentile(B[:, 2], 80))
            cand = [n for n in ("column", "plate bisector", "plate centres", "layer centroids", "posterior wall") if n in got]
            fig, axs = plt.subplots(3, len(cand), figsize=(3.0 * len(cand), 9.2))
            for k, n in enumerate(cand):
                f = G.frame_from(v.frame.origin, got[n], grid.anterior())
                f2 = A.toward_body(v, f) or f
                loc = f2.local(v.points_world(B))
                x0, zm, zu = float(np.median(loc[:, 0])), float(np.median(loc[:, 2])), float(np.percentile(loc[:, 2], 80))
                lab, ys = sagittal(vol, grid, f2, x0)
                draw(axs[0, k], lab, ys, ids[lv], "%s: sagittal, %.1f deg from column" % (n, deg(got["column"], got[n])))
                axs[0, k].axhline(zm, color="k", lw=0.6, ls=":"); axs[0, k].axhline(zu, color="k", lw=0.6, ls="--")
                axs[0, k].set_xlabel("P  <-  y  ->  A", fontsize=7)
                lab, xs = section(vol, grid, f2, zm)
                draw(axs[1, k], lab, xs, ids[lv], "axial at mid-body (dotted)")
                lab, xs = section(vol, grid, f2, zu)
                draw(axs[2, k], lab, xs, ids[lv], "axial at the upper fifth (dashed)")
            fig.suptitle("Study 0004, %s: the vertebra cut square to each reading of its axis" % lv, fontsize=10)
            fig.tight_layout()
            fig.savefig(os.path.join(OUT, "axis-%s.png" % lv), dpi=110)
            plt.close(fig)


if __name__ == "__main__":
    main()
