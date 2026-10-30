"""On the clean cache: the reading as it stands (the clamp where the label parts) against the fit
alone (info["fitted_deg"]), each against the truth in the measured frame, by slice thickness."""
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def main():
    rows = {"thin": [], "thick": []}
    for key, rec in score.records(os.path.join(WALL, "cache")):
        v = rec["vert"]
        v.__dict__.pop("_posterior_wall", None)
        slope, info = BODY.posterior_wall(v, v.body_pts, rec["xc"])
        truth = score.wall_truth_in_frame(rec)
        got = BODY.degrees_of(slope) - truth
        fit = info.get("fitted_deg", np.nan) - truth
        sp = rec["cfg"][5]
        rows[sp].append((key, got, fit, info.get("parted")))
        print("%-42s clamp %+6.2f fit %+6.2f parted %s" % (key, got, fit, info.get("parted")), flush=True)
    for sp, r in rows.items():
        g = np.abs([x[1] for x in r])
        f = np.abs([x[2] for x in r])
        worst = max(r, key=lambda x: abs(x[2]))
        print("== %s n %d: clamp max %.2f median %.2f | fit alone max %.2f median %.2f (worst %s) | fit>0.5: %d"
              % (sp, len(r), np.nanmax(g), np.nanmedian(g), np.nanmax(f), np.nanmedian(f), worst[0],
                 int((f > 0.5).sum())))


if __name__ == "__main__":
    main()
