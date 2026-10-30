"""The reviewer's two altered examples, read again with body.posterior_wall as it stands: the error,
the freedom, whether the label parts and the flag measures would write."""
import math
import os
import pickle
import sys

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, os.path.join(WALL, "judge"))
os.environ["READERS"] = "current"
import robust as R  # noqa: E402
from morphometry import body as BODY  # noqa: E402

for key, alt in (("straight_lean+0_x2_thin", "ragged_0.5_4"), ("straight_lean-5_x2_thick", "lip_top_1.5")):
    rec = pickle.load(open(os.path.join(WALL, "cache", key + ".pkl"), "rb"))
    t = R.S.wall_truth_in_frame(rec)
    v = R.altered(rec, alt)
    v.__dict__.pop("_posterior_wall", None)
    B = v.body_pts
    xc = 0.5 * (B[:, 0].min() + B[:, 0].max())
    slope, info = BODY.posterior_wall(v, B, xc)
    err = BODY.degrees_of(slope) - t
    print("%-28s %-14s err %+6.2f free %5.2f half %5.2f parted %s range [%+.2f, %+.2f] truth %+.2f fitted %+.2f" % (
        key, alt, err, info["free_deg"], 0.5 * info["free_deg"], info["parted"], info["free_lo_deg"],
        info["free_hi_deg"], t, info["fitted_deg"]))
    print("   flag:", BODY.wall_flags(info))
