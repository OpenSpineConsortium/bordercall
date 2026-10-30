"""How much one voxel moves the wall: on cached clean vertebrae, one voxel of bone added one step
behind the wall's edge nearest the window's middle at the midline (a speck on the wall, as a
segmenter leaves), or that edge's voxel taken away (a pit). The label then may not part, the
clamp lets go, and the reading is the fit alone."""
import copy
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402


def middle_edge(v, B, xc):
    """The index into v.idx of the wall's edge voxel nearest the window's middle at the midline."""
    half, reach, lo, hi = BODY.wall_window(v, B, xc)[0]
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    zc = 0.5 * (lo + hi)
    p = bone[np.argmin(np.abs(bone[:, 0] - xc) + np.abs(bone[:, 2] - zc))]
    return int(np.argmin(np.linalg.norm(v.loc - p, axis=1)))


def altered(v, keep=None, add=None):
    """A copy of v with voxels taken away (keep a mask over v.idx) or one added (add an index)."""
    u = copy.copy(v)
    for k in ("_posterior_wall", "_box"):
        u.__dict__.pop(k, None)
    if keep is not None:
        u.idx, u.loc, u.body = v.idx[keep], v.loc[keep], v.body[keep]
    if add is not None:
        world = v.grid.world(add[None, :].astype(float))
        u.idx = np.vstack([v.idx, add[None, :]])
        u.loc = np.vstack([v.loc, v.frame.local(world)])
        u.body = np.concatenate([v.body, [False]])
    return u


def err_of(v, rec):
    B = v.body_pts
    slope, info = BODY.posterior_wall(v, B, rec["xc"])
    return BODY.degrees_of(slope) - score.wall_truth_in_frame(rec), info


def main():
    names = sys.argv[1:]
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if names and key not in names:
            continue
        v = rec["vert"]
        B = v.body_pts
        e0, i0 = err_of(v, rec)
        j = middle_edge(v, B, rec["xc"])
        w, step, _ = BODY.scan_step_back(v)
        speck = altered(v, add=v.idx[j] + step)
        e1, i1 = err_of(speck, rec)
        keep = np.ones(len(v.idx), bool)
        keep[j] = False
        pit = altered(v, keep=keep)
        e2, i2 = err_of(pit, rec)
        print("%-40s clean %+5.2f (parted %s, %d edges) | speck %+5.2f (parted %s) | pit %+5.2f (parted %s)"
              % (key, e0, i0.get("parted"), i0.get("edges", 0), e1, i1.get("parted"), e2, i2.get("parted")), flush=True)


if __name__ == "__main__":
    main()
