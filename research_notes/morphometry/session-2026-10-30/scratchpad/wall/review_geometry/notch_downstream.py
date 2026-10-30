"""The four angles taken against the wall, and their flags, on a notch phantom: body.measures,
pedicle.measures and posterior.measures against phantom.truth.

  notch_downstream.py <thin|thick> <suite|x2> <w,h,d>
"""
import sys

from morphometry import body as BODY, canal as CANAL, pedicle as PED, posterior as POST
from morphometry.tests import phantom as P

from notches import GRIDS, SPACINGS
from storage_order import LUMBAR, build_from, reading


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h, d = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    vp = P.lumbar(notch_w=w, notch_h=h, notch_d=d)
    placed = P.straight(LUMBAR, vp, tilt=tilt)
    lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
    v = build_from(lab, aff)
    t = P.truth(vp)
    err, info = reading(v, placed, 0.0)
    body, bflags = BODY.measures(v)
    ped, pflags, _ = PED.measures(v, CANAL.body_span(v))
    post, sflags = POST.measures(v)
    print("%s %s notch %s: wall err %+.2f, edges %s dropped %s free %.2f" % (sname, gname, spec, err, info.get("edges"),
                                                                          info.get("dropped"), info.get("free_deg", float("nan"))))
    for k in ("endplate_incl", "endplate_lower_incl", "wedge"):
        print("  %-24s %+7.2f truth %+7.2f" % (k, body[k], t[k]))
    for k in ("pedicle_angle_sagittal_right", "pedicle_angle_sagittal_left"):
        print("  %-24s %+7.2f truth %+7.2f" % (k, ped[k], t["pedicle_angle_sagittal"]))
    print("  %-24s %+7.2f truth %+7.2f" % ("spinous_angle", post["spinous_angle"], t["spinous_angle"]))
    print("  wall flags:", {k: x for k, x in bflags.items() if "wall" in k}, "spinous flag:", sflags.get("spinous"))
    print("  pedicle notes:", {k: x[:60] for k, x in pflags.items()})


if __name__ == "__main__":
    main()
