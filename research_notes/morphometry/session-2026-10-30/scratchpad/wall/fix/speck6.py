"""One voxel of bone added one step behind a wall edge, at several edges spread over the window,
on the named cached vertebrae (all where none are named). For each: whether the speck's own edge
falls among the edges kept for the parting test (within a step of the fitted surface), whether the
label still parts, and the reading's error against the truth beside the fit alone's."""
import copy
import os
import sys

import numpy as np

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402

SPREAD = 6


def with_voxel(v, ijk):
    """A copy of v with one voxel of the label added (not of the body), its caches cleared."""
    u = copy.copy(v)
    for k in ("_posterior_wall", "_box"):
        u.__dict__.pop(k, None)
    world = v.grid.world(ijk[None, :].astype(float))
    u.idx = np.vstack([v.idx, ijk[None, :]])
    u.loc = np.vstack([v.loc, v.frame.local(world)])
    u.body = np.concatenate([v.body, [False]])
    return u


def edge_voxels(v, B, xc):
    """The voxel indices of the wall's edges, SPREAD of them evenly over the window by z near the
    midline."""
    half, reach, lo, hi = BODY.wall_window(v, B, xc)[0]
    bone, _ = BODY.wall_edges(v, xc, half, lo, hi, reach)
    near = bone[np.abs(bone[:, 0] - xc) <= 0.5 * half]
    near = near[np.argsort(near[:, 2])]
    pick = near[np.linspace(0, len(near) - 1, SPREAD + 2).astype(int)[1:-1]]
    return [int(np.argmin(np.linalg.norm(v.loc - p, axis=1))) for p in pick]


def residual_of_speck(u, B, xc, speck_loc):
    """The speck's edge residual over the step along y, under the fit u's reading makes."""
    half, reach, lo, hi = BODY.wall_window(u, B, xc)[0]
    bone, d = BODY.wall_edges(u, xc, half, lo, hi, reach)
    e = bone + 0.5 * d
    X = BODY.wall_design(e, xc)
    step_y = abs(d[1])
    coef = BODY.biweight(X, e[:, 1], BODY.trimmed_start(X, e[:, 1], e[:, 2]), BODY.WALL_BIWEIGHT_STEPS * step_y)
    j = np.argmin(np.linalg.norm(bone - speck_loc, axis=1))
    found = np.linalg.norm(bone[j] - speck_loc) < 1e-6
    r = (e[j, 1] - BODY.wall_design(e[j:j + 1], xc) @ coef)[0] / step_y
    return found, float(r)


def main():
    names = sys.argv[1:]
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if names and key not in names:
            continue
        v = rec["vert"]
        v.__dict__.pop("_posterior_wall", None)
        B, xc = v.body_pts, rec["xc"]
        truth = score.wall_truth_in_frame(rec)
        s0, i0 = BODY.posterior_wall(v, B, xc)
        e0, f0 = BODY.degrees_of(s0) - truth, i0["fitted_deg"] - truth
        print("%s clean %+.2f fit %+.2f parted %s" % (key, e0, f0, i0["parted"]), flush=True)
        _, step, _ = BODY.scan_step_back(v)
        for j in edge_voxels(v, B, xc):
            ijk = v.idx[j] + step
            u = with_voxel(v, ijk)
            s1, i1 = BODY.posterior_wall(u, B, xc)
            found, r = residual_of_speck(u, B, xc, u.loc[-1])
            e1 = BODY.degrees_of(s1) - truth if np.isfinite(s1) else np.nan
            print("   z %+6.1f speck edge %s r/step %+5.2f kept %-5s parted %-5s err %+6.2f fit %+6.2f %s"
                  % (v.loc[j, 2], found, r, abs(r) <= 1.0, i1.get("parted"), e1,
                     i1.get("fitted_deg", np.nan) - truth, i1.get("why", "")), flush=True)


if __name__ == "__main__":
    main()
