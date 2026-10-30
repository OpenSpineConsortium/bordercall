"""Why one speck behind the wall leaves it unread on some cached vertebrae: the record."""
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402
from one_voxel import altered, middle_edge  # noqa: E402


def main():
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if key not in sys.argv[1:]:
            continue
        v = rec["vert"]
        B = v.body_pts
        j = middle_edge(v, B, rec["xc"])
        w, step, d = BODY.scan_step_back(v)
        u = altered(v, add=v.idx[j] + step)
        print(key, "speck at", v.idx[j] + step, "was bone:", bool(v.is_bone((v.idx[j] + step)[None, :])[0]))
        s0, i0 = BODY.posterior_wall(v, B, rec["xc"])
        s1, i1 = BODY.posterior_wall(u, u.body_pts, rec["xc"])
        print("   clean:", {k: (round(x, 3) if isinstance(x, float) else x) for k, x in i0.items()})
        print("   speck:", {k: (round(x, 3) if isinstance(x, float) else x) for k, x in i1.items()})


if __name__ == "__main__":
    main()
