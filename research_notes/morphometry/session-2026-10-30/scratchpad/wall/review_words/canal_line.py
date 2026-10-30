"""The canal line's lean (anatomy.wall_slope as built) against the true wall in the measured
frame, over the 98 cached vertebrae, per grid and spacing: does it trace the staircase?"""
import math
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)
import score as S  # noqa: E402

out = {}
for key, rec in S.records(os.path.join(WALL, "cache")):
    v = rec["vert"]
    t = S.wall_truth_in_frame(rec)
    line = math.degrees(math.atan(v.wall_slope))
    old = rec["raw"]["wall_now"]
    out.setdefault((rec["cfg"][5], rec["cfg"][2]), []).append((line - t, old - t))
for k in sorted(out):
    a = np.array(out[k])
    print("%-6s %-8s canal line err max %5.2f median %5.2f | old wall err max %5.2f" % (
        k[0], k[1], np.abs(a[:, 0]).max(), np.median(np.abs(a[:, 0])), np.abs(a[:, 1]).max()))
