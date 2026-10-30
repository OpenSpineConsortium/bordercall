"""The wall on grids further from the vertebra's frame than the cache's 25 degrees: the vertebra
pitched about x (a lordotic L5, a flexed neck) and the grid turned about z (a rotated scoliotic
level), on 1 mm and 2.5 mm slices.

  steep.py <lean> <thin|thick> <pitch,...> <turn,...>
"""
import sys

from morphometry import body as BODY
from morphometry.tests import phantom as P

from storage_order import LUMBAR, build_from, reading

SPACINGS = {"thin": (0.8, 0.8, 1.0), "thick": (0.86, 0.86, 2.5)}


def main():
    lean, sname = float(sys.argv[1]), sys.argv[2]
    pitches = [float(s) for s in sys.argv[3].split(",")]
    turns = [float(s) for s in sys.argv[4].split(",")]
    for pitch in pitches:
        for turn in turns:
            placed = P.straight(LUMBAR, P.lumbar(lean=lean), tilt=((1.0, 0.0, 0.0), pitch))
            try:
                lab, aff = P.draw(placed, spacing=SPACINGS[sname], grid_turn=((0.0, 0.0, 1.0), turn), strict=False)
                v = build_from(lab, aff)
                err, info = reading(v, placed, lean)
                w, step, d = BODY.scan_step_back(v)
            except Exception as e:  # recorded, not hidden
                print("pitch %5.1f turn %5.1f FAILED %r" % (pitch, turn, e), flush=True)
                continue
            print("lean %+.0f %s pitch %5.1f turn %5.1f axis %d d %s err %+6.2f edges %s dropped %s free %5.2f "
                  "parted %s fit %+.2f why %s flags %s"
                  % (lean, sname, pitch, turn, w, d.round(3), err, info.get("edges"), info.get("dropped"),
                     info.get("free_deg", float("nan")), info.get("parted"), info.get("fitted_deg", float("nan")),
                     info.get("why", ""), sorted(k for k in v.flags)), flush=True)


if __name__ == "__main__":
    main()
