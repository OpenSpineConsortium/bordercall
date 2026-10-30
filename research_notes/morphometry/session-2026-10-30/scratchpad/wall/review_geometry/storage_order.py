"""The wall read on one phantom stored three ways: as drawn, with its anterior-most array axis
flipped (so a step of +1 index runs backward), and with the array's axes permuted (so the axis
nearest the frame's y is another index). The readings should agree, since the voxels' centres
in the world are the same."""
import math
import sys

import numpy as np

from morphometry import anatomy as A, body as BODY, measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]


def build_from(lab, aff, level="L3"):
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in LUMBAR})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    return A.build(level, vox[level], grid, axes[level], V.touching_edge(vox[level], lab.shape),
                   M.neighbours_of(vox, order, level))


def flipped(lab, aff, k):
    a = np.array(aff, float)
    a[:3, 3] = a[:3, 3] + a[:3, k] * (lab.shape[k] - 1)
    a[:3, k] = -a[:3, k]
    return np.ascontiguousarray(np.flip(lab, axis=k)), a


def permuted(lab, aff, perm):
    a = np.array(aff, float)
    a[:3, :3] = a[:3, list(perm)]
    return np.ascontiguousarray(lab.transpose(perm)), a


def reading(v, placed, lean):
    B = v.body_pts
    slope, info = BODY.posterior_wall(v, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
    R = [pl for pl in placed if pl.level == v.level][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    truth = math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))
    return BODY.degrees_of(slope) - truth, info


def main():
    lean, spacing = float(sys.argv[1]), tuple(float(s) for s in sys.argv[2].split(","))
    placed = P.straight(LUMBAR, P.lumbar(lean=lean), tilt=((1.0, 0.0, 0.0), 2.0))
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), 0.0))
    ways = {"drawn": (lab, aff), "flip y": flipped(lab, aff, 1), "flip x,y,z": None,
            "permute (1,0,2)": permuted(lab, aff, (1, 0, 2)), "permute (2,1,0)": permuted(lab, aff, (2, 1, 0))}
    l2, a2 = flipped(*flipped(lab, aff, 0), 1)
    ways["flip x,y,z"] = flipped(l2, a2, 2)
    for name, (l, a) in ways.items():
        v = build_from(l, a)
        err, info = reading(v, placed, lean)
        w, step, d = BODY.scan_step_back(v)
        print("%-16s axis %d step %s d %s err %+.3f edges %s free %.2f why %s"
              % (name, w, step, np.round(d, 3), err, info.get("edges"), info.get("free_deg", float("nan")),
                 info.get("why", "")), flush=True)


if __name__ == "__main__":
    main()
