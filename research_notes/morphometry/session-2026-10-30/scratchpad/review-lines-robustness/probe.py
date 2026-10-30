"""Draw one phantom variant, measure it with keep, draw its lines as the run does, and report.

    python probe.py VARIANT

Each variant is one of the shapes test_morphometry.py draws, or a mask cut or emptied in a way a
real mask can be. What is printed: the flags study_lines raised, the lines' statuses, which
levels have rows but no lines, and any exception that escaped study_lines (which would stop the
run, since one_study only guards the measuring).
"""
import sys
import time
import traceback
from collections import Counter

import numpy as np

from morphometry import __main__ as RUN
from morphometry import measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G

LUMBAR = ["L2", "L3", "L4"]


def crop_axis(lab, aff, axis, keep_from=None, keep_to=None):
    sl = [slice(None)] * 3
    sl[axis] = slice(keep_from, keep_to)
    out = np.array(aff, float)
    if keep_from:
        out[:3, 3] += keep_from * out[:3, axis]
    return lab[tuple(sl)], out


def cut_at_percentile(level, axis, pct, keep_high=True):
    def hook(lab, aff):
        idx = np.argwhere(lab == P.LEVEL_IDS[level])
        k = int(np.percentile(idx[:, axis], pct))
        return crop_axis(lab, aff, axis, keep_from=k) if keep_high else crop_axis(lab, aff, axis, keep_to=k)
    return hook


def variants():
    v = {}
    v["straight"] = dict(placed=P.straight(LUMBAR), levels=LUMBAR)
    v["thick2.5"] = dict(placed=P.straight(LUMBAR, P.Vert(), tilt=((1.0, 0.0, 0.0), 20.0)), levels=LUMBAR,
                         spacing=(0.86, 0.86, 2.5), grid_turn=((0.0, 0.0, 1.0), 0.0))
    v["thick5"] = dict(placed=P.straight(LUMBAR, P.Vert(), tilt=((1.0, 0.0, 0.0), 20.0)), levels=LUMBAR,
                       spacing=(0.98, 0.98, 5.0), grid_turn=((0.0, 0.0, 1.0), 0.0))
    v["shapes"] = dict(placed=P.straight(LUMBAR, P.lumbar(Ha=30.0, concavity=2.0, waist=0.92, ped_t=12.0, ped_s=6.0,
                                                          facet=55.0, sp_angle=32.0)), levels=LUMBAR)
    v["lateralmass"] = dict(placed=P.straight(LUMBAR, P.lumbar(ped_waist=0.02, mass_w=8.0, mass_h=24.0, foramen_d=6.5)),
                            levels=LUMBAR, strict=False)
    joint = P.Joint(gap=9.0, sagittal=8.0, coronal=4.0, axial=6.0, slip=3.0)
    v["joints"] = dict(placed=P.chain(LUMBAR, {lv: P.Vert() for lv in LUMBAR}, {lv: joint for lv in LUMBAR[1:]},
                                      R0=P.rotation((1.0, 0.2, 0.0), 12.0)), levels=LUMBAR, strict=False)
    cerv = ["C2", "C3", "C4"]
    verts = {"C2": P.cervical(dens_r=4.5, dens_h=14.0, dens_y=1.5), "C3": P.cervical(), "C4": P.cervical()}
    v["dens"] = dict(placed=P.chain(cerv, verts, {lv: P.Joint() for lv in cerv[1:]}, R0=P.rotation((1.0, 0.0, 0.0), 2.0)),
                     levels=cerv, grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
    verts_open = {lv: P.cervical(foramen_d=0.0, mass_w=0.0) for lv in cerv}
    v["cervical_nomass"] = dict(placed=P.chain(cerv, verts_open, {lv: P.Joint() for lv in cerv[1:]},
                                               R0=P.rotation((1.0, 0.0, 0.0), 2.0)), levels=cerv, strict=False)
    v["cut_body_L4"] = dict(placed=P.straight(LUMBAR), levels=LUMBAR, hook=cut_at_percentile("L4", 2, 30))
    v["cut_x_L3"] = dict(placed=P.straight(LUMBAR), levels=LUMBAR, hook=cut_at_percentile("L3", 0, 8))
    v["cut_y_L3"] = dict(placed=P.straight(LUMBAR), levels=LUMBAR, hook=cut_at_percentile("L3", 1, 8))
    v["cut_y_L3_front"] = dict(placed=P.straight(LUMBAR), levels=LUMBAR, hook=cut_at_percentile("L3", 1, 92, keep_high=False))
    v["one_level"] = dict(placed=P.straight(["L3"]), levels=["L3"])
    v["pelvis"] = dict(placed=P.straight(["L4", "L5"]), levels=["L4", "L5"], spacing=(1.0, 1.0, 1.0), pelvis=P.Pelvis())
    v["turned45"] = dict(placed=P.straight(LUMBAR, tilt=((1.0, 0.3, 0.0), 40.0)), levels=LUMBAR,
                         grid_turn=((0.0, 0.0, 1.0), 45.0))
    v["aniso"] = dict(placed=P.straight(LUMBAR), levels=LUMBAR, spacing=(0.5, 0.5, 3.0))
    v["notch"] = dict(placed=P.straight(LUMBAR, P.lumbar(notch_w=8.0, notch_h=6.0, notch_d=5.0)), levels=LUMBAR,
                      spacing=(0.86, 0.86, 2.5))
    v["lean"] = dict(placed=P.straight(LUMBAR, P.lumbar(lean=8.0), tilt=((1.0, 0.0, 0.0), 2.0)), levels=LUMBAR)
    v["dens_cut_top"] = dict(placed=P.chain(cerv, verts, {lv: P.Joint() for lv in cerv[1:]},
                                           R0=P.rotation((1.0, 0.0, 0.0), 2.0)), levels=cerv,
                             grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False, hook=cut_at_percentile("C2", 2, 70, keep_high=False))
    v["c2_alone"] = dict(placed=[P.chain(cerv, verts, {lv: P.Joint() for lv in cerv[1:]},
                                        R0=P.rotation((1.0, 0.0, 0.0), 2.0))[0]], levels=["C2"],
                         grid_turn=((0.0, 0.0, 1.0), 0.0), strict=False)
    return v


def main(name):
    spec = variants()[name]
    t = time.time()
    lab, aff = P.draw(spec["placed"], spacing=spec.get("spacing", (0.8, 0.8, 1.0)),
                      grid_turn=spec.get("grid_turn", ((0.0, 0.0, 1.0), 7.0)), pelvis=spec.get("pelvis"),
                      strict=spec.get("strict", True))
    if spec.get("hook"):
        lab, aff = spec["hook"](lab, aff)
    names = {P.LEVEL_IDS[lv]: lv for lv in spec["levels"]}
    if spec.get("pelvis") is not None:
        names.update({P.SACRUM: "sacrum", P.HIP_RIGHT: "hip_right", P.HIP_LEFT: "hip_left"})
    kept = {}
    rows = M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), names, "probe", pelvis=spec.get("pelvis") is not None,
                            keep=kept)
    t_measure = time.time() - t
    t = time.time()
    try:
        lines, frames, flags = RUN.study_lines("probe", kept)
    except BaseException as e:
        print("%-16s ESCAPED study_lines: %s: %s" % (name, type(e).__name__, e))
        traceback.print_exc()
        return
    t_draw = time.time() - t
    status = Counter(r["status"].split(":")[0] for r in lines if r["part"] == "")
    row_levels = sorted({r["level"] for r in rows if r["level"] not in ("column", "pelvis", "study")})
    line_levels = sorted({r["level"] for r in lines})
    print("%-16s measure+draw-volume %.0f s, lines %.1f s; verts %s; discs %s; flags %s; statuses %s; levels with rows "
          "but no lines %s" % (name, t_measure, t_draw, sorted(kept.get("verts", {})), sorted(kept.get("discs", {})),
                               [(f["level"], f["note"][:120]) for f in flags], dict(status),
                               [lv for lv in row_levels if lv not in line_levels]))
    for r in lines:
        if r["part"] == "" and r["status"].startswith("withheld"):
            print("    withheld %s %s: %s" % (r["level"], r["key"], r["status"]))


if __name__ == "__main__":
    main(sys.argv[1])
