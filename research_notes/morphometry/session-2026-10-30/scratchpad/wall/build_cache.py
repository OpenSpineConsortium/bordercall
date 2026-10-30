"""Build and pickle the phantom L3 vertebrae the wall-slope candidates are scored on.

Run with PYTHONPATH set to the bordercall checkout:
  build_cache.py <out_dir> [<index> <count>]
Each config is one phantom, one lean of its posterior wall, one grid and one spacing. The lean is
drawn by shearing the body's inside test, y -> y - z tan(lean), so the wall's true dy/dz in the
phantom's own frame is tan(lean); the frame's error against the phantom's axis is recorded too.
For each config the pickle holds the Vertebra, the truths and the raw readings the wall slope is
taken off (the pedicles' sagittal climb, the end-plates' rim slopes, the spinous angle), so a
candidate wall slope is scored downstream without measuring again.
"""
import math
import os
import pickle
import sys

import numpy as np

from morphometry import anatomy as A, measure as M, pedicle as PED, body as BODY, posterior as POST, canal as CANAL
from morphometry.tests import phantom as P
from scanimport import geometry as G, volume as V, LEVELS

LUMBAR = ["L2", "L3", "L4"]
PHANTOMS = {
    "straight": {},
    "pitched": dict(ped_s=10.0),
    "shapes": dict(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0),
    "pitched_down": dict(ped_s=-8.0, ped_t=8.0),
}
LEANS = {"straight": (0.0, 5.0, -5.0), "pitched": (0.0,), "shapes": (0.0, 4.0), "pitched_down": (0.0,)}
GRIDS = [
    ("aligned", ((1.0, 0.0, 0.0), 0.0), 0.0),
    ("x2", ((1.0, 0.0, 0.0), 2.0), 0.0),
    ("x5", ((1.0, 0.0, 0.0), 5.0), 0.0),
    ("x10", ((1.0, 0.0, 0.0), 10.0), 0.0),
    ("suite18", ((1.0, 0.3, 0.0), 18.0), 7.0),
    ("t25", ((1.0, 0.3, 0.0), 25.0), 15.0),
    ("y12", ((0.3, 1.0, 0.0), 12.0), 4.0),
]
SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}

_BODY_INSIDE = P.body_inside


def configs():
    out = []
    for name, kw in PHANTOMS.items():
        for lean in LEANS[name]:
            for gname, tilt, turn in GRIDS:
                for sname in SPACINGS:
                    out.append((name, lean, gname, tilt, turn, sname))
    return out


def sheared(lean_deg):
    t = math.tan(math.radians(lean_deg))

    def inside(q, v):
        q2 = np.array(q, float, copy=True)
        q2[:, 1] = q2[:, 1] - t * q2[:, 2]
        return _BODY_INSIDE(q2, v)
    return inside


def build(cfg):
    name, lean, gname, tilt, turn, sname = cfg
    P.body_inside = sheared(lean) if lean else _BODY_INSIDE
    try:
        v = P.lumbar(**PHANTOMS[name])
        placed = P.straight(LUMBAR, v, tilt=tilt)
        lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
    finally:
        P.body_inside = _BODY_INSIDE
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in LUMBAR}
    vox = V.vertebra_voxels(lab, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    whole = M.whole_levels(vox, order, lab.shape)
    axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
    vert = A.build("L3", vox["L3"], grid, axes["L3"], V.touching_edge(vox["L3"], lab.shape), M.neighbours_of(vox, order, "L3"))
    pl = [p for p in placed if p.level == "L3"][0]
    ez = vert.frame.ez @ pl.R
    frame_err = math.degrees(math.acos(min(1.0, abs(float(ez[2])))))
    truth = P.truth(v)
    cur_wall = math.degrees(math.atan(PED.wall_slope(vert)))
    raw = {"wall_now": cur_wall}
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    inc = BODY.inclinations(vert, B, xc)
    for k, val in inc.items():
        raw[k + "_raw"] = (-val - cur_wall) if np.isfinite(val) else float("nan")  # = degrees of the rim's own slope
    sp = POST.spinous_angle(vert)
    raw["spinous_angle_raw"] = sp - cur_wall if np.isfinite(sp) else float("nan")
    zb = CANAL.body_span(vert)
    for side, sname2 in PED.SIDES:
        out, note, info = PED.one_side(vert, side, zb)
        a = out.get("pedicle_angle_sagittal", float("nan"))
        raw["sag_raw_" + sname2] = a + cur_wall if np.isfinite(a) else float("nan")
    return {"cfg": cfg, "vert": vert, "truth": truth, "raw": raw, "frame_err_deg": frame_err,
            "wall_truth_deg": float(lean), "xc": float(xc)}


def main():
    out_dir = sys.argv[1]
    os.makedirs(out_dir, exist_ok=True)
    cfgs = configs()
    if len(sys.argv) > 3:
        i, n = int(sys.argv[2]), int(sys.argv[3])
        cfgs = cfgs[i::n]
    for cfg in cfgs:
        key = "%s_lean%+.0f_%s_%s" % (cfg[0], cfg[1], cfg[2], cfg[5])
        path = os.path.join(out_dir, key + ".pkl")
        if os.path.exists(path):
            continue
        try:
            rec = build(cfg)
        except Exception as e:  # recorded, not hidden
            print("FAILED", key, repr(e), flush=True)
            continue
        with open(path + ".tmp", "wb") as f:
            pickle.dump(rec, f)
        os.replace(path + ".tmp", path)
        r = rec["raw"]
        print("%-40s frame %.2f wall_now %+.2f truth %+.1f sag %s" % (
            key, rec["frame_err_deg"], r["wall_now"], rec["wall_truth_deg"],
            " ".join("%+.2f" % r[k] for k in r if k.startswith("sag_raw"))), flush=True)


if __name__ == "__main__":
    main()
