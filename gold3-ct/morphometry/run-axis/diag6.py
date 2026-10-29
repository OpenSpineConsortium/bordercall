"""The plate-face axis on study 0004: each level's turn off the column's line, the residual
after the turn, the cells' bisector beside it, the face counts and flags; and sections of
C3, C5, T8 and L5 square to the new z."""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag as D  # noqa: E402
from morphometry import anatomy as A
from morphometry import measure as M
from scanimport import LEVELS
from scanimport import volume as V

OUT, LABELS = sys.argv[1], sys.argv[2]


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
    print("level  turn   residual  plate_offset  faces(above,below)  seconds  flags")
    shown = {}
    for lv in spine:
        if lv in M.SKIP:
            continue
        nb = M.neighbours_of(vox, order, lv)
        t0 = time.time()
        v = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], vol.shape), nb)
        dt = time.time() - t0
        if not A.usable(v):
            print(lv, "unusable:", v.flags.get("all"))
            continue
        faces = []
        for side in ("above", "below"):
            pts = A.plate_face(v, nb[side]) if side in nb else None
            faces.append(0 if pts is None else len(pts))
        print("%-4s  %5.1f   %5.1f     %5.1f         %5d %5d        %4.1f   %s" % (
            lv, v.axis_turn, v.axis_residual, A.plate_offset(v), faces[0], faces[1], dt,
            "; ".join("%s: %s" % kv for kv in v.flags.items() if kv[0].startswith("axis") or kv[0] == "body_foramina")))
        shown[lv] = v
    want = [lv for lv in ("C3", "C5", "T8", "L5") if lv in shown]
    fig, axs = plt.subplots(2, len(want), figsize=(4.6 * len(want), 9.2))
    for k, lv in enumerate(want):
        v = shown[lv]
        loc = v.body_pts
        x0, zp = float(np.median(loc[:, 0])), float(np.percentile(loc[:, 2], 72))
        lab, ys = D.sagittal(vol, grid, v.frame, x0, half=40.0, step=0.3)
        D.draw(axs[0, k], lab, ys, ids[lv], "%s, turned %.1f deg (residual %.1f): sagittal" % (lv, v.axis_turn, v.axis_residual))
        axs[0, k].axhline(zp, color="k", lw=0.8, ls="--")
        lab, xs = D.section(vol, grid, v.frame, zp, half=40.0, step=0.3)
        D.draw(axs[1, k], lab, xs, ids[lv], "axial at the body's upper quarter")
    fig.suptitle("Study 0004 in each vertebra's own frame (the end-plates' faces toward the neighbours)", fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "axis6.png"), dpi=110)


main()
