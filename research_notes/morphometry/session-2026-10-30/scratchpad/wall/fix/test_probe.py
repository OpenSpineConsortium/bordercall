"""The readings the new and changed tests would assert on, measured with the suite's own helpers
(test_morphometry.built, wall_error, measured), before the tests are written.

  test_probe.py leaned | notch | refused | free | c2
"""
import copy
import math
import sys

import numpy as np

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T

LUMBAR = T.LUMBAR


def specked(vert, n):
    """A copy of vert with one voxel of bone one step behind each of n of the wall's edges, spread
    over the window near the midline."""
    B = vert.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    half, reach, lo, hi = BODY.wall_window(vert, B, xc)[0]
    bone, _ = BODY.wall_edges(vert, xc, half, lo, hi, reach)
    near = bone[np.abs(bone[:, 0] - xc) <= 0.5 * half]
    near = near[np.argsort(near[:, 2])]
    pick = near[np.linspace(0, len(near) - 1, n + 2).astype(int)[1:-1]]
    _, step, _ = BODY.scan_step_back(vert)
    add = np.array([vert.idx[int(np.argmin(np.linalg.norm(vert.loc - p, axis=1)))] + step for p in pick])
    u = copy.copy(vert)
    for k in ("_posterior_wall", "_box"):
        u.__dict__.pop(k, None)
    u.idx = np.vstack([vert.idx, add])
    u.loc = np.vstack([vert.loc, vert.frame.local(vert.grid.world(add.astype(float)))])
    u.body = np.concatenate([vert.body, np.zeros(len(add), bool)])
    return u


def record(tag, vert, placed, lean):
    vert.__dict__.pop("_posterior_wall", None)
    err = T.wall_error(vert, placed, lean)
    B = vert.body_pts
    info = BODY.posterior_wall(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))[1]
    print("%-36s err %+6.3f parted %s across %s free %s fitted %s lo %s hi %s why %s" % (
        tag, err, info.get("parted"), info.get("across"), info.get("free_deg"), info.get("fitted_deg"),
        info.get("free_lo_deg"), info.get("free_hi_deg"), info.get("why", "")), flush=True)
    return err, info


def leaned():
    lean = 5.0
    placed = P.straight(LUMBAR, P.lumbar(lean=lean), tilt=((1.0, 0.0, 0.0), 2.0))
    vert = T.built(placed, LUMBAR, "L3", grid_turn=((0.0, 0.0, 1.0), 0.0))
    err, info = record("leaned clean", vert, placed, lean)
    print("   fit alone err %+.3f" % (err + info["fitted_deg"] - BODY.degrees_of(BODY.posterior_wall(vert, vert.body_pts, 0.5 * (vert.body_pts[:, 0].min() + vert.body_pts[:, 0].max()))[0])))
    for n in (1, 2, 3, 5, 8):
        record("leaned %d specks" % n, specked(vert, n), placed, lean)


def notch():
    for z in (0.0, -4.0, 4.0):
        v = P.lumbar(notch_w=5.0, notch_h=6.0, notch_d=4.0, notch_z=z)
        placed = P.straight(LUMBAR, v)
        vert = T.built(placed, LUMBAR, "L3")
        record("notch 5x6x4 at %+.0f" % z, vert, placed, 0.0)
        got, flags = BODY.measures(vert)
        t = P.truth(v)
        print("   endplate_incl %+.2f lower %+.2f against %+.2f %+.2f flags %s canal line %+.2f" % (
            got["endplate_incl"], got["endplate_lower_incl"], t["endplate_incl"], t["endplate_lower_incl"],
            sorted(flags), math.degrees(math.atan(vert.wall_slope))))


def refused():
    v = P.lumbar(notch_w=8.0, notch_h=6.0, notch_d=5.0)
    rows = T.measured(P.straight(LUMBAR, v), LUMBAR, spacing=(0.86, 0.86, 2.5))["L3"]
    for k in ("endplate_incl", "endplate_lower_incl", "wedge", "pedicle_angle_sagittal_right",
              "pedicle_angle_sagittal_left", "pedicle_angle_transverse_left", "spinous_angle"):
        print("   %s %s" % (k, rows.get(k)))
    for k in sorted(rows):
        if k.startswith("flag:"):
            print("   %s: %s" % (k, rows[k]))


def free():
    for lean, tilt in ((5.0, 5.0), (4.0, 0.0)):
        v = P.lumbar(lean=lean) if lean == 5.0 else P.lumbar(lean=lean, Ha=30.0, concavity=2.0, waist=0.92,
                                                             ped_t=12.0, ped_s=6.0, facet=55.0, sp_angle=32.0)
        placed = P.straight(LUMBAR, v, tilt=((1.0, 0.0, 0.0), tilt))
        vert = T.built(placed, LUMBAR, "L3", spacing=(0.86, 0.86, 2.5), grid_turn=((0.0, 0.0, 1.0), 0.0))
        record("free lean %+.0f tilt %.0f thick" % (lean, tilt), vert, placed, lean)
        print("   flags", BODY.measures(vert)[1])


def main():
    globals()[sys.argv[1]]()


if __name__ == "__main__":
    main()
