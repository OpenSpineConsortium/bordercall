"""Run with PYTHONPATH set to the repository. Score the posterior wall's reading on phantom L3s, the
clean cache the figures of body.posterior_wall's docstring and research_notes/morphometry come from:

  probe_wall.py build <cache_dir> [<index> <count>]
  probe_wall.py score <cache_dir> [<module.py> <function>] [--json out.json]

build draws L2 to L4 and builds L3 as measure_volume builds it, one pickle a configuration: four
phantoms and their walls' leans (phantom.Vert.lean), seven grids, each the column's tilt and the
grid's turn about z, and two slice thicknesses, 98 in all; index and count take every count-th
configuration from index, so that several builds can run side by side. Each pickle holds the
Vertebra, the truths and the raw readings the wall's slope is taken off (the pedicles' sagittal
climb, the end-plates' rim slopes, the spinous angle), so a candidate reading is scored downstream
without measuring again.

score reads the wall with body.posterior_wall_slope, or with fn(v, B, xc) from the module named,
which may return dy/dz, (dy/dz, info) or NAN to refuse, and sets it against the true lean taken into
the frame the vertebra was read in, so that an error of the frame is not counted against the wall;
downstream the pedicles' sagittal angle, the end-plates' inclinations and the spinous angle against
their truths, the raw readings combined with the candidate as pedicle.one_side, body.inclinations
and posterior.spinous_angle combine them. The column "built" is the reading pedicle.wall_slope gave
when the cache was built. The alterations and the specks of the handoff of 30 October, 14:00 UTC,
were scratch scripts of that pass and are described there, not kept.
"""
import importlib.util
import json
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


def configs():
    return [(name, lean, gname, tilt, turn, sname)
            for name in PHANTOMS for lean in LEANS[name]
            for gname, tilt, turn in GRIDS for sname in SPACINGS]


def key_of(cfg):
    return "%s_lean%+.0f_%s_%s" % (cfg[0], cfg[1], cfg[2], cfg[5])


def placed_of(cfg):
    name, lean, _, tilt, _, _ = cfg
    v = P.lumbar(lean=lean, **PHANTOMS[name])
    return v, P.straight(LUMBAR, v, tilt=tilt)


def degrees_or_nan(slope):
    return math.degrees(math.atan(slope)) if np.isfinite(slope) else float("nan")


def raw_readings(vert, wall_deg):
    """The readings with the wall's own slope taken back out, so any other wall can be put in."""
    raw = {"wall_built": wall_deg}
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    for k, val in BODY.inclinations(vert, B, xc).items():
        raw[k + "_raw"] = -val - wall_deg if np.isfinite(val) else float("nan")
    sp = POST.spinous_angle(vert)
    raw["spinous_angle_raw"] = sp - wall_deg if np.isfinite(sp) else float("nan")
    zb = CANAL.body_span(vert)
    for side, side_name in PED.SIDES:
        out, _, _ = PED.one_side(vert, side, zb)
        a = out.get("pedicle_angle_sagittal", float("nan"))
        raw["sag_raw_" + side_name] = a + wall_deg if np.isfinite(a) else float("nan")
    return raw, float(xc)


def build(cfg):
    v, placed = placed_of(cfg)
    lab, aff = P.draw(placed, spacing=SPACINGS[cfg[5]], grid_turn=((0.0, 0.0, 1.0), cfg[4]), strict=False)
    grid = G.VoxelGrid(aff, lab.shape)
    vox = V.vertebra_voxels(lab, {P.LEVEL_IDS[lv]: lv for lv in LUMBAR})
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    order = [lv for lv in LEVELS if lv in vox]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in order]
    whole = M.whole_levels(vox, order, lab.shape)
    axes = dict(zip(order, M.column_line(cents, whole, grid.superior())))
    vert = A.build("L3", vox["L3"], grid, axes["L3"], V.touching_edge(vox["L3"], lab.shape),
                   M.neighbours_of(vox, order, "L3"))
    R = [p for p in placed if p.level == "L3"][0].R
    frame_err = math.degrees(math.acos(min(1.0, abs(float((vert.frame.ez @ R)[2])))))
    raw, xc = raw_readings(vert, degrees_or_nan(PED.wall_slope(vert)))
    return {"cfg": cfg, "vert": vert, "truth": P.truth(v), "raw": raw, "frame_err_deg": frame_err,
            "wall_truth_deg": float(cfg[1]), "xc": xc}


def build_all(out_dir, index=0, count=1):
    os.makedirs(out_dir, exist_ok=True)
    for cfg in configs()[index::count]:
        path = os.path.join(out_dir, key_of(cfg) + ".pkl")
        if os.path.exists(path):
            continue
        try:
            rec = build(cfg)
        except Exception as e:  # recorded, not hidden
            print("FAILED", key_of(cfg), repr(e), flush=True)
            continue
        with open(path + ".tmp", "wb") as f:
            pickle.dump(rec, f)
        os.replace(path + ".tmp", path)
        print("%-40s frame %.2f wall %+.2f truth %+.1f" % (
            key_of(cfg), rec["frame_err_deg"], rec["raw"]["wall_built"], rec["wall_truth_deg"]), flush=True)


def wall_truth_in_frame(rec):
    """The true wall's dy/dz in the frame the vertebra was read in, in degrees: the phantom's wall
    direction (0, tan lean, 1) taken into the measured frame."""
    _, placed = placed_of(rec["cfg"])
    R = [p for p in placed if p.level == "L3"][0].R
    f = rec["vert"].frame
    w = np.array([0.0, math.tan(math.radians(rec["cfg"][1])), 1.0])
    return math.degrees(math.atan(((f.ey @ R) @ w) / ((f.ez @ R) @ w)))


def downstream(rec, wall_deg):
    t, r, lean = rec["truth"], rec["raw"], rec["wall_truth_deg"]
    out = {}
    for side in ("right", "left"):
        out["sag_" + side] = (r["sag_raw_" + side] - wall_deg) - (t["pedicle_angle_sagittal"] - lean)
    for k in ("endplate_incl", "endplate_lower_incl"):
        out[k] = -(r[k + "_raw"] + wall_deg) - (t[k] - lean)
    out["spinous"] = (r["spinous_angle_raw"] + wall_deg) - (t["spinous_angle"] + lean)
    return out


def load_reader(argv):
    if len(argv) < 2 or argv[0].startswith("--"):
        return BODY.posterior_wall_slope
    spec = importlib.util.spec_from_file_location("candidate", argv[0])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, argv[1])


def records(cache):
    for f in sorted(os.listdir(cache)):
        if f.endswith(".pkl"):
            with open(os.path.join(cache, f), "rb") as fh:
                yield f[:-4], pickle.load(fh)


def score_one(key, rec, reader):
    v = rec["vert"]
    got = reader(v, v.body_pts, rec["xc"])
    got, info = got if isinstance(got, tuple) else (got, {})
    wall = degrees_or_nan(got) if got is not None else float("nan")
    truth = wall_truth_in_frame(rec)
    return {"key": key, "phantom": rec["cfg"][0], "lean": rec["cfg"][1], "grid": rec["cfg"][2],
            "spacing": rec["cfg"][5], "wall_deg": wall, "wall_err": wall - truth,
            "built_err": rec["raw"]["wall_built"] - truth, "wall_truth_frame": truth,
            "frame_err": rec["frame_err_deg"], "down": downstream(rec, wall) if np.isfinite(wall) else {},
            "info": {k: float(x) if isinstance(x, (int, float, np.floating)) else str(x) for k, x in info.items()}}


def summarise(rows):
    for sp in SPACINGS:
        sel = [r for r in rows if r["spacing"] == sp]
        if not sel:
            continue
        read = [r for r in sel if np.isfinite(r["wall_err"])]
        e = np.array([abs(r["wall_err"]) for r in read]) if read else np.array([np.nan])
        print("== %s: %d configurations, %d read; |wall err| max %.2f median %.2f" % (
            sp, len(sel), len(read), np.nanmax(e), np.nanmedian(e)))
        for g in [g for g, _, _ in GRIDS if any(r["grid"] == g for r in sel)]:
            gs = [abs(r["wall_err"]) for r in read if r["grid"] == g]
            print("   %-8s max %5.2f over %d" % (g, max(gs) if gs else float("nan"), len(gs)))
        sag = [abs(x) for r in read for k, x in r["down"].items() if k.startswith("sag") and np.isfinite(x)]
        print("   sagittal angle |err| max %.2f over %d readings" % (max(sag) if sag else float("nan"), len(sag)))


def score_all(cache, argv):
    reader = load_reader(argv)
    rows = []
    for key, rec in records(cache):
        rows.append(score_one(key, rec, reader))
        r = rows[-1]
        print("%-42s wall %+7.2f err %+6.2f (built %+6.2f) %s" % (
            key, r["wall_deg"], r["wall_err"], r["built_err"],
            " ".join("%s %+.2f" % (k, x) for k, x in r["down"].items() if np.isfinite(x))), flush=True)
    summarise(rows)
    if "--json" in argv:
        with open(argv[argv.index("--json") + 1], "w") as f:
            json.dump(rows, f, indent=1, default=float)


def main():
    what, cache, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
    if what == "build":
        build_all(cache, *(int(x) for x in rest[:2]))
    else:
        score_all(cache, rest)


if __name__ == "__main__":
    main()
