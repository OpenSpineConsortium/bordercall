"""What measures says on a notch phantom: the inclinations against their truth and the wall's flags."""
import sys

from morphometry import body as BODY
from morphometry.tests import phantom as P
from morphometry.tests.test_morphometry import LUMBAR, built

from gate_probe import GRIDS, SPACINGS, read


def main():
    sname, gname, spec = sys.argv[1], sys.argv[2], sys.argv[3]
    w, h, d = (float(s) for s in spec.split(","))
    tilt, turn = GRIDS[gname]
    pv = P.lumbar(notch_w=w, notch_h=h, notch_d=d)
    placed = P.straight(LUMBAR, pv, tilt=tilt)
    v = built(placed, LUMBAR, "L3", spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn))
    B = v.body_pts
    err, _ = read(v, B, 0.5 * (B[:, 0].min() + B[:, 0].max()), placed)
    out, flags = BODY.measures(v)
    truth = P.truth(pv)
    print("%s %s notch %s: wall err %+.2f; endplate_incl %+.2f (truth %+.2f), endplate_lower_incl %+.2f (truth %+.2f);"
          " wall flags %s" % (sname, gname, spec, err, out["endplate_incl"], truth["endplate_incl"],
                              out["endplate_lower_incl"], truth["endplate_lower_incl"],
                              {k: f for k, f in flags.items() if k.startswith("posterior_wall")}))


if __name__ == "__main__":
    main()
