"""Probes of body.posterior_wall as the working tree has it, on phantoms only.

  probe.py notch <thin|thick> <suite|x2> <w,h,d[,z]> ...   the notch phantom, the notch's middle z above mid-height
  probe.py c2 <thin|thick> <x2|suite18> [tall]              a cervical C2 with a dens of several shapes
  probe.py cerv <thin|thick|fine> <x0,x2,...> [clip]        the reviewer's cervical C5, pedicles clipped or not
  probe.py speck [<key> ...]                                one voxel behind the middle edge of each cached L3
"""
import copy
import math
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)
sys.path.insert(0, os.path.join(WALL, "review_robustness"))

from morphometry import anatomy as A, body as BODY, measure as M  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402
from scanimport import geometry as G, volume as V, LEVELS  # noqa: E402

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5), "fine": (0.4, 0.4, 0.6)}
GRIDS = {"suite": (((1.0, 0.3, 0.0), 18.0), 7.0), "x2": (((1.0, 0.0, 0.0), 2.0), 0.0),
         "x0": (((1.0, 0.0, 0.0), 0.0), 0.0), "x5": (((1.0, 0.0, 0.0), 5.0), 0.0),
         "suite18": (((1.0, 0.3, 0.0), 18.0), 0.0)}


def build(levels, level, vert, spacing, tilt, turn, edit=None):
    placed = P.straight(levels, vert, tilt=tilt)
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
    if edit is not None:
        lab = edit(lab, aff, placed)
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in levels})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    axes = dict(zip(order, M.column_line(cents, M.whole_levels(vox, order, lab.shape), grid.superior())))
    v = A.build(level, vox[level], grid, axes[level], V.touching_edge(vox[level], lab.shape),
                M.neighbours_of(vox, order, level))
    return v, placed


def truth_deg(v, placed, lean):
    R = [pl for pl in placed if pl.level == v.level][0].R
    w = R @ np.array([0.0, math.tan(math.radians(lean)), 1.0])
    return math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))


def read(v, placed, lean):
    v.__dict__.pop("_posterior_wall", None)
    B = v.body_pts
    slope, info = BODY.posterior_wall(v, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
    err = BODY.degrees_of(slope) - truth_deg(v, placed, lean) if math.isfinite(slope) else float("nan")
    return err, info


def line(tag, err, info):
    n = info.get("edges", 0) + info.get("dropped", 0)
    share = info.get("dropped", 0) / n if n else float("nan")
    print("%-44s err %+7.2f share %.2f gate %+6.2f parted %-5s across %s free %6.2f fit %+7.2f why %s"
          % (tag, err, share, info.get("gate_off_mm", float("nan")), info.get("parted"), info.get("across"),
             info.get("free_deg", float("nan")), info.get("fitted_deg", float("nan")), info.get("why", "")),
          flush=True)


def notch(sname, gname, specs):
    tilt, turn = GRIDS[gname]
    for spec in specs:
        vals = [float(s) for s in spec.split(",")]
        w, h, d = vals[:3]
        z = vals[3] if len(vals) > 3 else 0.0
        vert = P.lumbar(notch_w=w, notch_h=h, notch_d=d, notch_z=z)
        v, placed = build(["L2", "L3", "L4"], "L3", vert, SPACINGS[sname], tilt, turn)
        err, info = read(v, placed, 0.0)
        line("%s %s notch %s" % (sname, gname, spec), err, info)


def c2(sname, gname, tall):
    from probe_cervical import CERVICAL
    from probe_label_edits import add_dens
    kw = dict(CERVICAL)
    if tall:
        kw.update(Hp=20.0, Ha=20.0)
    height = 15.0 if tall else 14.0
    tilt, turn = GRIDS[gname]
    shapes = [(None, None), (0.0, 0.0), (0.0, 10.0), (1.5, 0.0), (1.5, 12.0), (3.0, 12.0), (2.0, 10.0)]
    for back_y, lean_back in shapes:
        edit = None if back_y is None else add_dens("C2", kw["Hp"] / 2, back_y=back_y, lean_back_deg=lean_back,
                                                    height=height)
        v, placed = build(["C2", "C3", "C4"], "C2", P.lumbar(**kw), SPACINGS[sname], tilt, turn, edit)
        tag = "C2 %s %s %s" % (sname, gname, "no dens" if back_y is None else "dens %+.1f back %.0f"
                               % (back_y, lean_back))
        if "all" in v.flags:
            print(tag, "NOT BUILT", v.flags["all"])
            continue
        err, info = read(v, placed, 0.0)
        line(tag, err, info)


def cerv(sname, tilts, clip):
    from probe_cervical import CERVICAL
    sys.path.insert(0, os.path.join(WALL, "verify_5_0"))
    for tname in tilts:
        tilt, turn = GRIDS[tname]
        for lean in (0.0, 5.0, -5.0):
            for ped_z in (2.0, -2.0):
                vert = P.lumbar(lean=lean, **dict(CERVICAL, ped_z=ped_z))
                v, placed = build(["C4", "C5", "C6"], "C5", vert, SPACINGS[sname], tilt, turn)
                if "all" in v.flags:
                    print("C5", tname, lean, "NOT BUILT")
                    continue
                err, info = read(v, placed, lean)
                line("C5 %s %s lean %+.0f ped_z %+.0f half %.2f" % (sname, tname, lean, ped_z,
                                                                   info.get("half_band_mm", float("nan"))), err, info)


def speck(names):
    import score
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if names and key not in names:
            continue
        v = rec["vert"]
        B = v.body_pts
        v.__dict__.pop("_posterior_wall", None)
        s0, i0 = BODY.posterior_wall(v, B, rec["xc"])
        t = score.wall_truth_in_frame(rec)
        half, reach, lo, hi = BODY.wall_window(v, B, rec["xc"])[0]
        bone, d = BODY.wall_edges(v, rec["xc"], half, lo, hi, reach)
        zc = 0.5 * (lo + hi)
        p = bone[np.argmin(np.abs(bone[:, 0] - rec["xc"]) + np.abs(bone[:, 2] - zc))]
        j = int(np.argmin(np.linalg.norm(v.loc - p, axis=1)))
        w, step, _ = BODY.scan_step_back(v)
        add = v.idx[j] + step
        u = copy.copy(v)
        for k in ("_posterior_wall", "_box"):
            u.__dict__.pop(k, None)
        u.idx = np.vstack([v.idx, add[None, :]])
        u.loc = np.vstack([v.loc, v.frame.local(v.grid.world(add[None, :].astype(float)))])
        u.body = np.concatenate([v.body, [False]])
        s1, i1 = BODY.posterior_wall(u, u.body_pts, rec["xc"])
        e0 = BODY.degrees_of(s0) - t if math.isfinite(s0) else float("nan")
        e1 = BODY.degrees_of(s1) - t if math.isfinite(s1) else float("nan")
        print("%-40s clean %+6.2f (parted %s) speck %+6.2f (parted %s, free %.2f, %s) %s"
              % (key, e0, i0.get("parted"), e1, i1.get("parted"), i1.get("free_deg", float("nan")),
                 i1.get("clamp", ""), i1.get("why", "")), flush=True)


def main():
    what = sys.argv[1]
    if what == "notch":
        notch(sys.argv[2], sys.argv[3], sys.argv[4:])
    elif what == "c2":
        c2(sys.argv[2], sys.argv[3], len(sys.argv) > 4 and sys.argv[4] == "tall")
    elif what == "cerv":
        cerv(sys.argv[2], sys.argv[3].split(","), len(sys.argv) > 4)
    elif what == "speck":
        speck(sys.argv[2:])


if __name__ == "__main__":
    main()
