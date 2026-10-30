"""What C2's kept rows carry when its wall is read on the dens: endplate_lower_incl against the
phantom's truth, the spinous angle and the pedicles' sagittal angles, with every flag measure_one
sets on the wall, for the body without a dens and with two dens shapes.

  probe_c2_rows.py <thin|thick> <Hp>
"""
import math
import sys

from morphometry import measure as M
from morphometry.tests import phantom as P

from probe_c2 import CERV, SPACINGS, TILTS, build, dens_edit, truth_deg
from morphometry import body as BODY


def main():
    sname, Hp = sys.argv[1], float(sys.argv[2])
    vert = P.lumbar(Hp=Hp, Ha=Hp, **CERV)
    truth = P.truth(vert)
    cases = [("no dens", None), ("dens back +1.0 lean 0", dens_edit(Hp / 2, 1.0, 0.0)),
             ("dens back -1.0 lean 12", dens_edit(Hp / 2, -1.0, 12.0))]
    for cname, edit in cases:
        v, placed = build(vert, SPACINGS[sname], TILTS["x2"], edit)
        vals, flags, _ = M.vertebra_values(v)
        B = v.body_pts
        slope, info = BODY.posterior_wall(v, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))
        wall = BODY.degrees_of(slope) - truth_deg(v, placed)
        keys = ("endplate_lower_incl", "spinous_angle") + tuple(k for k in vals if k.startswith("pedicle_angle_sagittal"))
        got = {k: vals.get(k, float("nan")) for k in keys} if vals else {}
        err = {k: round(got[k] - truth[k.split("_right")[0].split("_left")[0]], 2)
               if math.isfinite(got[k]) else "nan" for k in keys}
        wall_flags = sorted(k for k in (flags or {}) if "wall" in k or k == "spinous" or k.startswith("pedicle"))
        print("H%.0f %s x2 %-24s wall %+.2f  %s  flags %s" % (Hp, sname, cname, wall, err, wall_flags), flush=True)


if __name__ == "__main__":
    main()
