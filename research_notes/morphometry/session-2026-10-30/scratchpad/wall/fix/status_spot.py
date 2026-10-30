"""On the suite's own build of the wall leaned 5 degrees on 1 mm slices whose grid lies 5 degrees
off about x, which speck of speck6's six gives the range's programs HiGHS's status 4, and what the
reader reads there now and with wall_slope_range as it stood before this pass.

  status_spot.py
"""
import os
import sys
from unittest import mock

FIX = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FIX)
import speck6  # noqa: E402
from status_probe import kept_pairs, statuses  # noqa: E402
from bite import old_range  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from morphometry.tests import phantom as P  # noqa: E402
from morphometry.tests import test_morphometry as T  # noqa: E402


def main():
    placed = P.straight(T.LUMBAR, P.lumbar(lean=5.0), tilt=((1.0, 0.0, 0.0), 5.0))
    v = T.built(placed, T.LUMBAR, "L3", grid_turn=((0.0, 0.0, 1.0), 0.0))
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    _, step, _ = BODY.scan_step_back(v)
    print("clean: err %+.3f" % T.wall_error(v, placed, 5.0))
    for k, j in enumerate(speck6.edge_voxels(v, B, xc)):
        u = speck6.with_voxel(v, v.idx[j] + step)
        ends, wstat, margin = statuses(*kept_pairs(u, B, xc), xc)
        now_err = T.wall_error(u, placed, 5.0)
        now = T.wall_reading(u)[1]
        u.__dict__.pop("_posterior_wall", None)
        with mock.patch.object(BODY, "wall_slope_range", old_range):
            before_err = T.wall_error(u, placed, 5.0)
            before = T.wall_reading(u)[1]
        print("spot %d: ends %s margin %.3g | now %+.3f parted %s across %s | before %+.3f parted %s why %s" % (
            k, ends, margin, now_err, now.get("parted"), now.get("across"), before_err, before.get("parted"),
            before.get("why", "")), flush=True)


if __name__ == "__main__":
    main()
