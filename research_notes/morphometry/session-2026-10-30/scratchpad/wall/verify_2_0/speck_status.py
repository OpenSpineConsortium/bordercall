"""Check a reviewer's claim: one voxel of bone added one step behind the wall's middle edge
makes HiGHS answer status 4 in body.wall_slope_range, which the code takes as an unbounded end,
so the wall is refused as free over 180 degrees.

For each cached vertebra named (or all), a copy with one speck is read by body.posterior_wall as
it stands, with every linprog call that body makes logged (status and message). For each logged
call of wall_slope_range, the same bone and air centres are given to a widest-margin program
(maximise t with every centre on its side by t) under three HiGHS solvers, so the answer the
code should have given (no parting where the widest margin is under WALL_PART_MM) is known.
"""
import copy
import math
import os
import sys

import numpy as np
from scipy.optimize import linprog as scipy_linprog

WALL = "/tmp/claude-0/-home-user/cbdcd57f-bcf8-5a71-ab64-4f0b9fbdb74f/scratchpad/wall"
sys.path.insert(0, WALL)

import score  # noqa: E402
from morphometry import body as BODY  # noqa: E402

CALLS = []


def logged_linprog(*args, **kw):
    res = scipy_linprog(*args, **kw)
    CALLS.append({"c": tuple(kw["c"]), "A": kw["A_ub"], "b": kw["b_ub"], "status": res.status,
                  "message": res.message, "x1": float(res.x[1]) if res.x is not None else None})
    return res


def with_speck(v, B, xc):
    """A copy of v with one voxel of bone one step behind the wall's edge nearest the window's
    middle, on the midline: a speck stuck to the wall."""
    half, reach, lo, hi = BODY.wall_window(v, B, xc)[0]
    bone, d = BODY.wall_edges(v, xc, half, lo, hi, reach)
    zc = 0.5 * (lo + hi)
    p = bone[np.argmin(np.abs(bone[:, 0] - xc) + np.abs(bone[:, 2] - zc))]
    j = int(np.argmin(np.linalg.norm(v.loc - p, axis=1)))
    _, step, _ = BODY.scan_step_back(v)
    add = v.idx[j] + step
    assert not v.is_bone(add[None, :])[0], "the speck's voxel is bone already"
    u = copy.copy(v)
    for k in ("_posterior_wall", "_box"):
        u.__dict__.pop(k, None)
    world = v.grid.world(add[None, :].astype(float))
    u.idx = np.vstack([v.idx, add[None, :]])
    u.loc = np.vstack([v.loc, v.frame.local(world)])
    u.body = np.concatenate([v.body, [False]])
    u.touching = np.concatenate([v.touching, [False]])
    return u


def widest_margin(A, b, solver):
    """The widest margin t of the same constraints with the part margin taken back out: A x <= b0 - t,
    where b0 = b + WALL_PART_MM."""
    b0 = b + BODY.WALL_PART_MM
    n = len(b0)
    res = scipy_linprog(c=[0, 0, 0, 0, -1.0], A_ub=np.column_stack([A, np.ones(n)]), b_ub=b0,
                        bounds=[(None, None)] * 4 + [(None, 10.0)], method=solver)
    return res.status, (-res.fun if res.status == 0 else float("nan"))


def read(u, rec):
    CALLS.clear()
    BODY.linprog = logged_linprog
    try:
        slope, info = BODY.posterior_wall(u, u.body_pts, rec["xc"])
    finally:
        BODY.linprog = scipy_linprog
    return slope, info, list(CALLS)


def report(key, rec):
    v = rec["vert"]
    truth = score.wall_truth_in_frame(rec)
    s0, i0, _ = read(copy.copy(v), rec)
    u = with_speck(v, v.body_pts, rec["xc"])
    s1, i1, calls = read(u, rec)
    e0 = BODY.degrees_of(s0) - truth
    e1 = BODY.degrees_of(s1) - truth if np.isfinite(s1) else float("nan")
    statuses = [c["status"] for c in calls]
    line = "%-38s clean %+5.2f | speck %+6.2f parted %-5s free %6.1f statuses %s" % (
        key, e0, e1, i1.get("parted"), i1.get("free_deg", float("nan")), statuses)
    if "why" in i1:
        line += " why: " + i1["why"][:60]
    print(line, flush=True)
    if any(s not in (0, 2) for s in statuses):
        first = calls[0]
        for solver in ("highs", "highs-ds", "highs-ipm"):
            st, m = widest_margin(first["A"], first["b"], solver)
            print("    widest margin by %-9s status %d margin %.3g (part needs > %.0e)"
                  % (solver, st, m, BODY.WALL_PART_MM), flush=True)
        for c in calls:
            if c["status"] not in (0, 2):
                print("    call c=%s status %d: %s" % (c["c"], c["status"], c["message"]), flush=True)
    return statuses, i1


def main():
    keys = sys.argv[1:]
    tally = {}
    for key, rec in score.records(os.path.join(WALL, "cache")):
        if keys and key not in keys:
            continue
        statuses, info = report(key, rec)
        k = ("status4" if 4 in statuses else "other") + (" refused" if "why" in info else " read")
        tally[k] = tally.get(k, 0) + 1
    print("tally", tally)


if __name__ == "__main__":
    main()
