"""C2 drawn with the phantom's own dens (phantom.Vert.dens_r) on cervical-sized vertebrae, read with
the window bounded at C2 and, relabelled, without; and C2's rows from measure_volume.

  c2_phantom.py <thin|thick> <x2|suite18>
"""
import copy
import math
import sys

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests import test_morphometry as T

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}
TILTS = {"x2": (((1.0, 0.0, 0.0), 2.0), 0.0), "suite18": (((1.0, 0.3, 0.0), 18.0), 7.0)}
LEVELS = ["C2", "C3", "C4"]


def column(dens):
    c2 = P.cervical(**dens)
    plain = P.cervical()
    return {"C2": c2, "C3": plain, "C4": plain}


def main():
    sname, tname = sys.argv[1], sys.argv[2]
    tilt, turn = TILTS[tname]
    for dens in ({}, dict(dens_r=4.5, dens_h=14.0, dens_y=1.5, dens_lean=12.0),
                 dict(dens_r=4.5, dens_h=14.0, dens_y=1.5, dens_lean=0.0),
                 dict(dens_r=4.5, dens_h=14.0, dens_y=0.0, dens_lean=0.0)):
        placed = P.chain(LEVELS, column(dens), {lv: P.Joint() for lv in LEVELS[1:]}, R0=P.rotation(*tilt))
        vert = T.built(placed, LEVELS, "C2", spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn),
                       strict=False)
        err = T.wall_error(vert, placed, 0.0)
        other = copy.copy(vert)
        other.__dict__.pop("_posterior_wall", None)
        other.level = "C3"
        err_other = T.wall_error(other, placed, 0.0)
        B = vert.body_pts
        info = BODY.posterior_wall(vert, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))[1]
        print("%s %s dens %s: wall %+.2f (window not bounded %+.2f) free %.2f parted %s flags %s" % (
            sname, tname, dens or "none", err, err_other, info.get("free_deg", math.nan), info.get("parted"),
            sorted(BODY.measures(vert)[1])), flush=True)


if __name__ == "__main__":
    main()
