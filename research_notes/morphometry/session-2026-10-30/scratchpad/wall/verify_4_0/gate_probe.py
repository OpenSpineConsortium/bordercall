"""Whether the gate about the canal's line, leaned by a notch, is what reads the wall off.

For one notch phantom: the reading as it stands; every candidate edge (air behind, bone in front)
in the band and the window with no gate, sorted by where it lies in the phantom's own frame (the
wall, the notch's floor, other); per 2 mm of z, the canal line, the true wall, how many of each
kind the gate lets in and how many the fit keeps; then the reading with the gate centred on the
true wall line, on a level line at the canal's median front, and widened.

  gate_probe.py <thin|thick> <suite|x2> <w,h,d>
"""
import copy
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.anatomy import square_to_wall
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
GRIDS = {"suite": (((1.0, 0.3, 0.0), 18.0), 7.0), "x2": (((1.0, 0.0, 0.0), 2.0), 0.0)}


def truth_deg(v, placed):
    R = [pl for pl in placed if pl.level == v.level][0].R
    w = R @ np.array([0.0, 0.0, 1.0])
    return math.degrees(math.atan(float(v.frame.ey @ w) / float(v.frame.ez @ w)))


def true_wall_line(v, placed):
    """The phantom's wall at the midline (local x 0, y 0) in v's frame: slope and y at v.wall_z0."""
    pl = [p for p in placed if p.level == v.level][0]
    pts = np.array([pl.c + pl.R @ np.array([0.0, 0.0, t]) for t in (-5.0, 5.0)])
    q = v.frame.local(pts)
    s = (q[1, 1] - q[0, 1]) / (q[1, 2] - q[0, 2])
    return s, q[0, 1] + s * (v.wall_z0 - q[0, 2])


def read(v, B, xc, placed):
    slope, info = BODY.posterior_wall(v, B, xc)
    return BODY.degrees_of(slope) - truth_deg(v, placed), info


def with_line(v, slope, y0):
    u = copy.copy(v)
    u.__dict__.pop("_posterior_wall", None)
    u.wall_slope, u.wall_y0 = slope, y0
    return u


def candidates(v, xc, half, lo, hi):
    """Every voxel with air one step back and bone WALL_RUN_MM in front in the band and the
    window, no gate: its local centre, its edge, its world edge."""
    w, step, d = BODY.scan_step_back(v)
    loc = v.loc
    near = (np.abs(loc[:, 0] - xc) <= half + v.pixel) & (loc[:, 2] >= lo - v.fz) & (loc[:, 2] <= hi + v.fz)
    Pi, q = v.idx[near], loc[near]
    keep = BODY.backmost_bone(v, Pi, step, v.grid.spacing[w])
    bone = q[keep]
    e = bone + 0.5 * d
    inside = (np.abs(e[:, 0] - xc) <= half) & (e[:, 2] >= lo) & (e[:, 2] <= hi)
    dw = step[w] * v.grid.spacing[w] * v.grid.axes[:, w]
    world = v.grid.world(Pi[keep].astype(float)) + 0.5 * dw
    return bone[inside], e[inside], world[inside]


def kind_of(world, placed, level, pv):
    pl = [p for p in placed if p.level == level][0]
    q = (world - pl.c) @ pl.R
    wall = np.abs(q[:, 1]) <= 1.0
    notch = ((np.abs(q[:, 1] - pv.notch_d) <= 1.0) & (np.abs(q[:, 0]) <= pv.notch_w / 2 + 1.0)
             & (np.abs(q[:, 2]) <= pv.notch_h / 2 + 1.0))
    k = np.full(len(q), "other", object)
    k[wall] = "wall"
    k[notch & ~wall] = "notch"
    return k


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w_, h_, d_ = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    pv = P.lumbar(notch_w=w_, notch_h=h_, notch_d=d_)
    placed = P.straight(LUMBAR, pv, tilt=tilt)
    v = built(placed, LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn))
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    err, info = read(v, B, xc, placed)
    ts, ty0 = true_wall_line(v, placed)
    print("%s %s notch %s: err %+.2f edges %s dropped %s span %s free %.2f parted %s why %s"
          % (sname, gname, spec, err, info.get("edges"), info.get("dropped"), info.get("span_mm"),
             info.get("free_deg", float("nan")), info.get("parted"), info.get("why", "")))
    print("  canal line %+.2f deg y0 %+.2f at z0 %+.2f; true wall %+.2f deg y0 %+.2f; reach %s"
          % (math.degrees(math.atan(v.wall_slope)), v.wall_y0, v.wall_z0, math.degrees(math.atan(ts)), ty0,
             None if BODY.wall_window(v, B, xc)[0] is None else round(BODY.wall_window(v, B, xc)[0][1], 2)))
    place, why = BODY.wall_window(v, B, xc)
    half, reach, lo, hi = place
    bone, e, world = candidates(v, xc, half, lo, hi)
    kinds = kind_of(world, placed, v.level, pv)
    gate_y = square_to_wall(v, bone)[:, 1] - v.wall_y0
    gated = np.abs(gate_y) <= reach
    # the edges the fit kept, as read_wall keeps them
    gb, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    ge = gb + 0.5 * d
    X = BODY.wall_design(ge, xc)
    coef = BODY.biweight(X, ge[:, 1], BODY.trimmed_start(X, ge[:, 1], ge[:, 2]), BODY.WALL_BIWEIGHT_STEPS * abs(d[1]))
    good = np.abs(ge[:, 1] - X @ coef) <= abs(d[1])
    # kinds of the fitted edges: match to candidates by position
    def kind_at(p):
        j = int(np.argmin(np.linalg.norm(e - p, axis=1)))
        return kinds[j]
    gk = np.array([kind_at(p) for p in ge], object)
    print("  window %.1f..%.1f; candidates %d (wall %d, notch %d, other %d); gated wall %d notch %d other %d;"
          " fit kept wall %d notch %d other %d of %d"
          % (lo, hi, len(e), (kinds == "wall").sum(), (kinds == "notch").sum(), (kinds == "other").sum(),
             (gated & (kinds == "wall")).sum(), (gated & (kinds == "notch")).sum(), (gated & (kinds == "other")).sum(),
             (good & (gk == "wall")).sum(), (good & (gk == "notch")).sum(), (good & (gk == "other")).sum(), len(ge)))
    for z0 in np.arange(lo, hi, 2.0):
        sel = (e[:, 2] >= z0) & (e[:, 2] < z0 + 2.0)
        gsel = (ge[:, 2] >= z0) & (ge[:, 2] < z0 + 2.0)
        zm = z0 + 1.0
        line = v.wall_y0 + v.wall_slope * (zm - v.wall_z0)
        tw = ty0 + ts * (zm - v.wall_z0)
        wy = e[sel & (kinds == "wall"), 1]
        ny = e[sel & (kinds == "notch"), 1]
        print("   z %+5.1f: line %+6.2f true wall %+6.2f (line-wall %+5.2f); wall edges %3d y~%s in gate %3d;"
              " notch edges %3d y~%s in gate %3d; kept wall %3d notch %3d"
              % (zm, line, tw, line - tw, len(wy), "%+6.2f" % np.median(wy) if len(wy) else "  none",
                 (gated & sel & (kinds == "wall")).sum(), len(ny), "%+6.2f" % np.median(ny) if len(ny) else "  none",
                 (gated & sel & (kinds == "notch")).sum(), (good & gsel & (gk == "wall")).sum(),
                 (good & gsel & (gk == "notch")).sum()))
    for name, u in (("gate about the true wall line", with_line(v, ts, ty0)),
                    ("gate about a level line at the canal's median front", with_line(v, 0.0, v.wall))):
        err2, info2 = read(u, B, xc, placed)
        print("  %s: err %+.2f edges %s dropped %s free %.2f parted %s why %s"
              % (name, err2, info2.get("edges"), info2.get("dropped"), info2.get("free_deg", float("nan")),
                 info2.get("parted"), info2.get("why", "")))


if __name__ == "__main__":
    main()
