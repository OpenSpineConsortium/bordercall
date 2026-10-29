"""Which reading of a vertebra's axis holds still when the frame it is read in turns, the body's
voxels fixed once: each reading taken in the column frame and in that frame turned 10 and 20
degrees about x and about y, and the spread of the world directions."""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag as D  # noqa: E402
from morphometry import anatomy as A
from morphometry import body as BODY
from morphometry import measure as M
from scanimport import LEVELS
from scanimport import geometry as G
from scanimport import volume as V

LABELS = sys.argv[1]
WANT = ["C3", "C4", "C5", "C6", "C7", "T1", "T6", "T8", "T11", "L1", "L3", "L4", "L5"]


def rotate(frame, axis_local, deg):
    """The frame turned by deg about one of its own axes (0 x, 1 y)."""
    a = [frame.ex, frame.ey, frame.ez]
    k = a[axis_local]
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    def rot(v):
        return v * c + np.cross(k, v) * s + k * (k @ v) * (1 - c)
    ez = rot(frame.ez)
    return G.frame_from(frame.origin, ez, rot(frame.ey))


def theil(z, w):
    i, j = np.triu_indices(len(z), 1)
    far = np.abs(z[j] - z[i]) >= 4.0
    if far.sum() < 3:
        return math.nan
    return float(np.median((w[j] - w[i])[far] / (z[j] - z[i])[far]))


def readings(Bw, frame, pixel, fz):
    """World directions of each reading, from the body's world points in the given frame."""
    B = frame.local(Bw)
    def to_world(d):
        return G.unit(d[0] * frame.ex + d[1] * frame.ey + d[2] * frame.ez)
    out = {}
    normals = []
    for top in (True, False):
        ext = BODY.plate_points(B, pixel, top)
        if len(ext) >= 6:
            c = BODY.plane_robust(ext, fz)
            n = np.array([-c[1], -c[2], 1.0])
            normals.append(n / np.linalg.norm(n))
    if len(normals) == 2:
        out["bisector"] = to_world(G.unit(normals[0] + normals[1]))
    layer = np.round(B[:, 2] / fz)
    zs, counts = np.unique(layer, return_counts=True)
    zs = zs[counts >= 20]
    lo, hi = np.percentile(zs, (15, 85))
    zs = zs[(zs >= lo) & (zs <= hi)]
    cents, backs = [], []
    for z in zs:
        L = B[layer == z]
        cents.append(L.mean(0))
        backs.append(L[L[:, 1] <= np.percentile(L[:, 1], 10)].mean(0))
    cents, backs = np.array(cents), np.array(backs)
    if len(cents) >= 4:
        dx, dy = theil(cents[:, 2], cents[:, 0]), theil(cents[:, 2], cents[:, 1])
        if np.isfinite(dx) and np.isfinite(dy):
            out["centroids"] = to_world(np.array([dx, dy, 1.0]))
        dx, dy = theil(backs[:, 2], backs[:, 0]), theil(backs[:, 2], backs[:, 1])
        if np.isfinite(dx) and np.isfinite(dy):
            out["posterior"] = to_world(np.array([dx, dy, 1.0]))
    W = Bw - Bw.mean(0)
    vals, vecs = np.linalg.eigh(np.cov(W.T))
    out["pca least"] = vecs[:, 0]
    return out


def main():
    vol, grid, names, _, _ = V.read_labels(LABELS, "enhance")
    vox = V.vertebra_voxels(vol, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    spine = [lv for lv in LEVELS if lv in vox and lv != "sacrum"]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in spine]
    whole = M.whole_levels(vox, spine, vol.shape)
    axes = dict(zip(spine, M.column_line(cents, whole, grid.superior())))
    names_r = ("bisector", "centroids", "posterior", "pca least")
    print("spread over turned frames (largest angle to the reading in the column frame), and the reading's angle to the column line")
    print("level  " + "  ".join("%-22s" % n for n in names_r))
    for lv in WANT:
        if lv not in vox:
            continue
        v = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], vol.shape))
        if not A.usable(v):
            print(lv, "unusable")
            continue
        Bw = v.points_world(v.body_pts)
        base = v.column_ez if v.column_ez is not None else v.frame.ez
        f0 = G.frame_from(v.frame.origin, base, v.frame.ey)
        r0 = readings(Bw, f0, v.pixel, v.fz)
        spread = {n: 0.0 for n in names_r}
        for ax in (0, 1):
            for deg in (-20, -10, 10, 20):
                r = readings(Bw, rotate(f0, ax, deg), v.pixel, v.fz)
                for n in names_r:
                    if n in r and n in r0:
                        spread[n] = max(spread[n], D.deg(r[n], r0[n]))
        print("%-5s  " % lv + "  ".join("%5.1f (%5.1f off)      " % (spread[n], D.deg(r0[n], base)) if n in r0 else "    -                 " for n in names_r))


main()
