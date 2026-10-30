"""Candidate B: the body's posterior wall parted from the canal on the scan's own lattice.

The wall's dy/dz is the slope b of the surface y = a + b z' + c x' + d x'^2 that parts the
vertebra's bone from the canal behind it with the widest margin, a linear program as
pedicle.parting runs for the pedicle's surfaces, z' measured from the window's middle and x'
from the midline xc. The c x' term takes the frame's roll against the wall and the d x'^2 term
the wall's curve across the strip; neither changes what b means. The widest-margin optimum is
often not unique in b, so the reading is the middle of the slopes at the widest margin, and the
info carries the range of slopes of every surface that still parts the centres (as
pedicle.slope_range), which says how far the lattice pins the wall at all.

Where it is read: the scan's voxel centres within ACROSS_HALF_MM of the midline, over the middle
HEIGHT_SHARE of the midline body's height (the region body.posterior_wall_slope reads), and front
to back within half the canal's midline depth of the canal's wall line (the line the body was
cut at). Bone is the vertebra's own label (v.is_bone), not the cut body B, since the cut runs in
front of the wall wherever the canal line leans off it and takes the wall's own centres away.
What the label does not hold there is the canal: at the midline nothing of the vertebra but the
body's wall stands within half the canal's depth of it, the lamina and the spinous process lying
behind the canal's middle (the margin column.wall_corner takes).

Where no surface of the family parts them, the least-crossing surface (a linear program over the
crossings) says which centres lie across, and the rest are parted by the widest margin. The
reading is refused where more than VIOLATED_SHARE of the centres within NEAR_ROWS rows of the
surface lie across, where one lies more than CROSS_ROWS rows across (a smooth wall cut by the
lattice at any phase is bracketed within a row, so a deeper crossing is a notch, a lip or a
fragment), or where the surfaces that part the centres leave the slope free over more than
RANGE_MAX_DEG. The three bounds are pedicle.py's own for its surfaces.
"""
import math

import numpy as np
from scipy import sparse
from scipy.optimize import linprog

ACROSS_HALF_MM = 3.0     # the strip about the midline, as body.posterior_wall_slope takes it
HEIGHT_SHARE = 0.6       # the middle share of the midline body's height, as it takes it
MIN_EACH = 20            # at least this many centres of bone and as many of the canal
NEAR_ROWS = 2.0          # the share across is counted among the centres this many rows from the surface
VIOLATED_SHARE = 0.1     # pedicle.VIOLATED_SHARE
CROSS_ROWS = 1.5         # pedicle.SURFACE_LAYERS
RANGE_MAX_DEG = 9.0      # pedicle.FREEDOM_DEG
MARGIN_CAP_MM = 10.0     # keeps the program bounded; a margin this wide is no wall's
NAN = float("nan")


def slope(v, B, xc):
    """dy/dz of the posterior wall in v's frame and a record of the parting, or NAN and why."""
    info = {}
    got = region(v, B, xc)
    if got is None:
        return NAN, dict(info, why="no canal depth or no midline body")
    q, bone = got
    info["n_bone"], info["n_canal"] = int(bone.sum()), int((~bone).sum())
    if min(info["n_bone"], info["n_canal"]) < MIN_EACH:
        return NAN, dict(info, why="too few centres of bone or of the canal")
    F = np.column_stack([np.ones(len(q)), q[:, 2], q[:, 0], q[:, 0] ** 2])
    sign = np.where(bone, 1.0, -1.0)          # bone at or in front of the surface, the canal behind
    y = q[:, 1]
    got = part(F, sign, y)
    if got is None:
        return NAN, dict(info, why="no surface parts the bone from the canal as a wall would")
    margin, coef, crossing = got
    keep = crossing <= 1e-9
    near = np.abs(y - F @ coef) <= NEAR_ROWS * v.fy
    lo, hi = slopes_at(F[keep], sign[keep], y[keep], 0.0)
    at_lo, at_hi = slopes_at(F[keep], sign[keep], y[keep], margin - 1e-7)
    info.update(margin_mm=margin, across=int((~keep).sum()), near=int(near.sum()),
                worst_mm=float(crossing.max()), lo_deg=deg(lo), hi_deg=deg(hi), width_deg=deg(hi) - deg(lo))
    why = refusal(info, v.fy)
    if why:
        return NAN, dict(info, why=why)
    return 0.5 * (at_lo + at_hi), info


def region(v, B, xc):
    """The voxel centres the wall is parted on, as (x', y, z') in v's frame, and whether each is
    the vertebra's bone; None where the canal gives no depth or the strip holds no body."""
    rings = v.full_rings()
    strip = B[np.abs(B[:, 0] - xc) <= ACROSS_HALF_MM]
    if not rings or len(strip) < MIN_EACH:
        return None
    reach = 0.5 * float(np.median([s.ap for s in rings]))
    z0, z1 = strip[:, 2].min(), strip[:, 2].max()
    trim = 0.5 * (1.0 - HEIGHT_SHARE) * (z1 - z0)
    lo, hi = z0 + trim, z1 - trim

    def line(z):
        return v.wall_y0 + v.wall_slope * (z - v.wall_z0)

    ijk = index_box(v, [[x, line(z) + dy, z] for x in (xc - ACROSS_HALF_MM, xc + ACROSS_HALF_MM)
                        for z in (lo, hi) for dy in (-reach, reach)])
    q = v.frame.local(v.grid.world(ijk.astype(float)))
    inside = ((np.abs(q[:, 0] - xc) <= ACROSS_HALF_MM) & (q[:, 2] >= lo) & (q[:, 2] <= hi)
              & (np.abs(q[:, 1] - line(q[:, 2])) <= reach))
    q, ijk = q[inside], ijk[inside]
    return np.column_stack([q[:, 0] - xc, q[:, 1], q[:, 2] - 0.5 * (lo + hi)]), v.is_bone(ijk)


def index_box(v, corners):
    """Every voxel index in the box of indices round these frame points."""
    inv = np.linalg.inv(np.asarray(v.grid.affine, float))
    c = v.points_world(np.array(corners, float)) @ inv[:3, :3].T + inv[:3, 3]
    a, b = np.floor(c.min(0)).astype(int) - 1, np.ceil(c.max(0)).astype(int) + 1
    axes = [np.arange(a[k], b[k] + 1) for k in range(3)]
    return np.stack(np.meshgrid(*axes, indexing="ij"), -1).reshape(-1, 3)


def part(F, sign, y):
    """The widest margin, the surface that has it, and how far each centre lies across it: where
    no surface parts them all, the centres across the least-crossing surface are set aside and the
    rest parted. None where a program fails or the margin is no wall's."""
    crossing = np.zeros(len(y))
    got = widest_margin(F, sign, y)
    if got is not None and got[0] <= 0.0:
        crossing = least_crossing(F, sign, y)
        if crossing is None:
            return None
        keep = crossing <= 1e-9
        got = widest_margin(F[keep], sign[keep], y[keep])
    if got is None or got[0] >= MARGIN_CAP_MM:
        return None
    return got[0], got[1], crossing


def widest_margin(F, sign, y):
    """(margin, coefficients) of the surface parting the centres by the widest margin, the
    margin negative where none parts them."""
    A = np.vstack([np.column_stack([sign[:, None] * F, np.ones(len(y))]), np.r_[np.zeros(4), 1.0]])
    x = solve(np.r_[np.zeros(4), -1.0], A, np.r_[sign * y, MARGIN_CAP_MM], 5)
    return None if x is None else (float(x[4]), np.asarray(x[:4], float))


def least_crossing(F, sign, y):
    """How far each centre lies across the surface of least total crossing."""
    n = len(y)
    A = sparse.hstack([sparse.csr_matrix(sign[:, None] * F), -sparse.identity(n)], format="csr")
    x = solve(np.r_[np.zeros(4), np.ones(n)], A, sign * y, 4)
    return None if x is None else np.asarray(x[4:], float)


def slopes_at(F, sign, y, floor):
    """The least and greatest slope b of a surface keeping every centre at least floor mm on its
    own side; an end the centres do not bound is infinite."""
    ends = []
    for sense in (1.0, -1.0):
        x = solve(np.array([0.0, sense, 0.0, 0.0]), sign[:, None] * F, sign * y - floor, 4)
        ends.append(x[1] if x is not None else -sense * math.inf)
    return ends[0], ends[1]


def solve(c, A, b, n_free):
    """linprog (HiGHS) with the first n_free variables free and the rest at least nought."""
    bounds = [(None, None)] * n_free + [(0.0, None)] * (len(c) - n_free)
    res = linprog(c=c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    return res.x if res.success else None


def deg(b):
    return math.degrees(math.atan(b)) if math.isfinite(b) else math.copysign(90.0, b)


def refusal(info, row):
    """Why the parting is not read as the wall, or nothing."""
    if info["across"] > VIOLATED_SHARE * max(info["near"], 1):
        return "%d of the %d centres about the wall lie across the best surface" % (info["across"], info["near"])
    if info["worst_mm"] > CROSS_ROWS * row:
        return "a centre lies %.2f mm across the best surface, more than %.1f rows" % (info["worst_mm"], CROSS_ROWS)
    if not info["width_deg"] <= RANGE_MAX_DEG:
        return "the lattice leaves the wall free over %.1f degrees, more than %.0f" % (info["width_deg"], RANGE_MAX_DEG)
    return ""
