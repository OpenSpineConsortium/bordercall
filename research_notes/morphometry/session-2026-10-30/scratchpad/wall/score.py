"""Score a candidate posterior-wall slope on the cached phantom vertebrae.

  PYTHONPATH=<bordercall> python score.py <cache_dir> <module.py> <function> [--json out.json]

The function is called as fn(v, B, xc) -> dy/dz, the signature of body.posterior_wall_slope, on
each cached L3 (build_cache.py). It may also return (slope, info) where info is a dict, or NAN to
refuse. Scored against the wall's true lean, and downstream against the truths of the pedicle's
sagittal angle, the end-plates' inclinations and the spinous angle, each taken against the plane
square to the true wall: the cached raw readings are combined with the candidate exactly as
pedicle.one_side, body.inclinations and posterior.spinous_angle combine them.
The function "current" in this file is body.posterior_wall_slope as it stands.
"""
import importlib.util
import json
import math
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def current(v, B, xc):
    from morphometry import body as BODY
    return BODY.posterior_wall_slope(v, B, xc)


def load_fn(path, name):
    if path == "current":
        return current
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, name)


def records(cache):
    for f in sorted(os.listdir(cache)):
        if f.endswith(".pkl"):
            with open(os.path.join(cache, f), "rb") as fh:
                yield f[:-4], pickle.load(fh)


def wall_truth_in_frame(rec):
    """The true wall's dy/dz in the frame the vertebra was read in, in degrees: the phantom's
    wall direction (0, tan lean, 1) taken into the measured frame, so that an error of the frame
    itself is not counted against the wall slope, which is read in that frame."""
    from morphometry.tests import phantom as P
    import build_cache as BC
    name, lean, gname, tilt, turn, sname = rec["cfg"]
    placed = P.straight(BC.LUMBAR, P.lumbar(**BC.PHANTOMS[name]), tilt=tilt)
    R = [p for p in placed if p.level == "L3"][0].R
    f = rec["vert"].frame
    w = np.array([0.0, math.tan(math.radians(lean)), 1.0])
    ey, ez = f.ey @ R, f.ez @ R
    return math.degrees(math.atan((ey @ w) / (ez @ w)))


def downstream(rec, cand_deg):
    t, r, lean = rec["truth"], rec["raw"], rec["wall_truth_deg"]
    out = {}
    for side in ("right", "left"):
        raw = r.get("sag_raw_" + side, float("nan"))
        out["sag_" + side] = (raw - cand_deg) - (t["pedicle_angle_sagittal"] - lean)
    for k in ("endplate_incl", "endplate_lower_incl"):
        raw = r.get(k + "_raw", float("nan"))
        out[k] = -(raw + cand_deg) - (t[k] - lean)
    raw = r.get("spinous_angle_raw", float("nan"))
    out["spinous"] = (raw + cand_deg) - (t["spinous_angle"] + lean)
    return out


def main():
    cache, path, name = sys.argv[1], sys.argv[2], sys.argv[3]
    js = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    fn = load_fn(path, name)
    rows = []
    for key, rec in records(cache):
        v = rec["vert"]
        B = v.body_pts
        got = fn(v, B, rec["xc"])
        info = {}
        if isinstance(got, tuple):
            got, info = got
        cand = math.degrees(math.atan(got)) if got is not None and np.isfinite(got) else float("nan")
        truth_f = wall_truth_in_frame(rec)
        err = cand - truth_f
        d = downstream(rec, cand) if np.isfinite(cand) else {}
        rows.append({"key": key, "phantom": rec["cfg"][0], "lean": rec["cfg"][1], "grid": rec["cfg"][2],
                     "spacing": rec["cfg"][5], "wall_deg": cand, "wall_err": err,
                     "now_err": rec["raw"]["wall_now"] - truth_f, "wall_truth_frame": truth_f, "frame_err": rec["frame_err_deg"],
                     "down": d, "info": {k: (float(x) if isinstance(x, (int, float, np.floating)) else str(x)) for k, x in info.items()}})
        print("%-42s wall %+7.2f err %+6.2f (now %+6.2f) %s" % (
            key, cand, err, rows[-1]["now_err"],
            " ".join("%s %+.2f" % (k, x) for k, x in d.items() if np.isfinite(x))), flush=True)
    for sp in ("thin", "thick"):
        sel = [r for r in rows if r["spacing"] == sp]
        fin = [r for r in sel if np.isfinite(r["wall_err"])]
        if not sel:
            continue
        e = np.array([abs(r["wall_err"]) for r in fin]) if fin else np.array([np.nan])
        n = np.array([abs(r["now_err"]) for r in sel])
        print("== %s: %d configs, %d read; |wall err| max %.2f median %.2f mean %.2f; current max %.2f median %.2f" % (
            sp, len(sel), len(fin), np.nanmax(e), np.nanmedian(e), np.nanmean(e), n.max(), np.median(n)))
        for g in sorted({r["grid"] for r in sel}):
            gs = [abs(r["wall_err"]) for r in fin if r["grid"] == g]
            gn = [abs(r["now_err"]) for r in sel if r["grid"] == g]
            print("   %-8s max %5.2f (current %5.2f) over %d" % (g, max(gs) if gs else float("nan"), max(gn), len(gs)))
        dd = [abs(x) for r in fin for k, x in r["down"].items() if k.startswith("sag") and np.isfinite(x)]
        print("   sagittal angle |err| max %.2f over %d readings" % (max(dd) if dd else float("nan"), len(dd)))
    if js:
        with open(js, "w") as f:
            json.dump(rows, f, indent=1, default=float)


if __name__ == "__main__":
    main()
