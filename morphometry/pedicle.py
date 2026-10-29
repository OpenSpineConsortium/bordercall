"""The pedicles: width, height and area at the isthmus, the axis's two angles and the chord along
it, each side; and between them the interpedicular distance both ways it is defined, read on
the same walls.

The pedicle is the bridge of bone from the body to the articular pillar beside the canal, and
its width and height are the least across it, where Zindrick (1987) and Panjabi read them, each
on the cut that shows it: the width on an axial cut through the pedicle's middle height, the
height on a sagittal cut through its middle across. A whole-vertebra label gives no pedicle
subregion, so the pedicle is found from the canal. In a row front to back at a height, the
first bone outward from the canal's midline on a side is the canal's wall there, and the bone
from that wall outward as far as the first gap wider than GAP_VOXELS voxels is the section of
what stands beside the canal in that row (SideMap.chord). Over the rows from the body's
posterior wall back to the canal's posterior wall that section is wide where the body's
posterolateral corner stands beside the canal, narrow along the pedicle's free length, and wide
again where the transverse process, the articular pillar or the lamina joins: lateral of a
cervical pedicle lies the foramen transversarium, lateral of a thoracic or a lumbar one air up
to the transverse process's root behind it, so the row through the isthmus ends at a gap on
every level. Each row is read at three heights, the body's median and ANCHOR_SHARE of its
height above and below it, since a thoracic pedicle stands on the upper part of the body and a
lumbar one about its middle, and each reading is settled: the column of bone at the middle of
its section (height_run) gives the pedicle's top and bottom in that row, and the section is
read again at their middle, the pedicle's own middle height there, so a pitched pedicle is
followed row by row; the row keeps the reading of least area, width times height, since the
pedicle is the smallest thing beside the canal in any row through it (profile). The isthmus is
the least of that area profile, smoothed over three rows (canal.smoothed_values) and sought in
the front FRONT_SHARE of the canal's depth, where the pedicle stands, since behind it the
lamina's inner surface bounds the canal and a row through the lamina on the slant reads as
narrow as a pedicle; never the row at the body's wall itself, whose band catches the wall's own
voxels. The rows about it within ISTHMUS_SHARE of it are the isthmus rows, Zindrick's narrowest
part of the pedicle, less the rows that are not the pedicle's (pedicle_rows): one whose medial
wall stands more than CORNER_MM nearer the midline than the others', the body's posterolateral
corner in front or the lamina behind, which curve in toward the midline (at study 0004's L4 the
corner's row turned the left axis to 47 degrees), and one whose width or height is more than
OUTLIER_SHARE from the others', a cut through the articular process's edge (on the phantoms one
such row, 4 mm wide and 28 tall, pitched the sagittal angle 16 degrees). The width is the
median of their sections, the height the median of their columns; what joins the pedicle above
or below at the pillar does not stand in that column at the isthmus. A section wider than the
level's PEDICLE_MAX_MM is the pedicle with what joins it laterally, the transverse process's
root at L5 or the lateral mass in the neck, and is not read; nor is a cervical pedicle whose
lateral border, the foramen transversarium, the mask does not close (anatomy's body_foramina
flag), since the march then runs into the lateral mass (study 0004's C5 read 15 mm wide and
the band between the pedicles nothing).

Why the canal's hole is not used, as the readings of 2026-10-29 used it: a hole needs the ring
closed, laminae and pedicles in one slab, and on the masks the ring closes in two to eight
slabs only (study 0004: eight at L3, five at L5, one at C5), where the pedicles stand higher or
lower than the laminae's overlap or the frame lies 30 degrees against the scan's layers, so C3
to C7, L4 and L5 had no slab at the pedicle's height. The coronal island's extent, the run's
first reading, took the lateral mass and the transverse process's root with the pedicle (12 to
22 mm where 5 to 9 is real), and its fewest-voxel seed landed 5 to 9 mm from the pedicle at L5
and C5, since on real masks every coronal island holds a process's root. A reading in cuts
square to the axis crossed the lamina behind the short thoracic pedicle (widths of 20 to 30 mm
at study 0004's T7). The march needs no ring and no island: a wall is wherever bone first
stands beside the canal.

An axial cut through the pedicle's middle crosses a converging pedicle on the slant, so the
width is the section times the cosine of the transverse angle, and a sagittal column crosses a
pitched pedicle the same way, so the height is the run times the cosine of the sagittal angle
where that angle is read. The area is the ellipse's on the width and the height, pi w h / 4,
the shape a pedicle's section is taken to have, since no cut of a whole-vertebra label gives the
pedicle's own outline where a process joins it.

The axis runs through the isthmus rows, pointing back. Across, it follows the medial wall, the
canal's edge, each row's wall the median of its section's medial surface over the layers in the
middle half of its height (medial_wall), since one layer's edge steps with the raster. The
lateral surface is free only along the isthmus rows and flares into the transverse process's
root behind them and the body's corner in front, so the sections' middles read the pedicles
converging more than they do (at study 0004's L4 27 to 42 degrees where the walls read 15, and
at L3 17 where the wall read 5, the root joining in the lower layers two rows behind the
isthmus); the wall is the one surface read the same in every row. The wall's line is extended
row by row forward and back while the next row's wall lies within WALL_FIT_MM of the line
through the isthmus rows' walls, or of their median where they are too few for a line, and does
not jut in (CORNER_MM), so that a short pedicle still gets a baseline, and the transverse angle
is the line's angle to the midsagittal plane, positive where the pedicles converge toward the
front, read where the rows taken span AXIS_SPAN_MM. It is the angle of the canal's wall along
the pedicle, which under-reads the pedicle's bisector where the lateral cortex flares, so the
research note sets the level medians beside the papers'. Up, the axis follows the middle of the
height run: the isthmus rows' own, and in a row taken beyond them the column half the isthmus's
section out from its wall, where that column's height is within HEIGHT_SHARE of the isthmus's,
since the pedicle's top and bottom surfaces run on past its free lateral length, between the
notches, to the pillar. The sagittal angle is the climb's angle to the transverse plane,
positive where the posterior end is higher, taken against the plane square to the body's
posterior wall (wall_slope), read where the rows with a middle span SAGITTAL_SPAN_MM front to
back: the borders of so short a pedicle curve with the notch and the process, and the centres'
climb is theirs, not the pedicle's (study 0004's thoracic pedicles span 4.5 to 5.3 mm and
climbed 40 to 50 degrees); the chord then takes the axis level, and where the rows are too few
for an axis at all the chord and the transverse angle are not read. The chord is the length of
bone the axis line through the isthmus crosses, from where it enters the posterior elements to
where it leaves the body's anterior cortex, read by marching along the line voxel by voxel
(Zindrick's screw path).

The interpedicular distance, the least between the pedicles' medial walls (Hinck, the
paper-tables vocabulary), and Eisenstein's greatest interpedicular distance, the canal's width
at its widest between the pedicles, are read on the same walls (canal_between): at the
isthmus's place front to back, the mean of the two sides', the gap between the two walls in
every layer over the central half of the pedicles' height, its least; and over the rows from
the body's wall back to the isthmus in the same layers, its greatest, where at L4 and L5 the
walls flare into the lateral recesses and a caliper between the pedicles opens widest. A row
where bone stands within MIDLINE_CLEAR_MM of the midline on either side, the body's posterior
wall or the lamina crossing it, gives no gap (at study 0004's C5 the wall's rows read the
distance as nothing). Neither is read across the hole's middle, where scanimport reads a slab's
width: a lumbar canal is widest between the pedicles, and at its middle, behind them, the
laminae's junction bounds it, so the width through the middle read 2 to 3 mm under the papers'
at L4 and L5 and in the neck (the run of 2026-10-29, canal-shape.csv). canal.measures writes
both, and where a pedicle is not found on both sides reads the hole's width through the middle
for them, flagged.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from scanimport import geometry as G

from . import body as BODY
from . import canal as CANAL
from .anatomy import NAN, Vertebra

ISTHMUS_SHARE = 1.2           # the isthmus: the rows whose section's area is within this share of the least
FRONT_SHARE = 0.6             # the isthmus is sought in this share of the canal's depth from the body's wall
ANCHOR_SHARE = 0.25           # each row is read at the body's median height and this share of its height above and below
OUTLIER_SHARE = 0.25          # an isthmus row whose width or height is further than this share from the others' is not the pedicle's
CORNER_MM = 1.0               # a row whose medial wall stands this much nearer the midline than the isthmus rows' is the body's corner or the lamina
HEIGHT_SHARE = 0.35           # a column whose height is further than this share from the isthmus's is not the pedicle's
WALL_FIT_MM = 1.0             # the axis takes a row whose medial wall lies within this of the line through the isthmus rows' walls
AXIS_SPAN_MM = 2.0            # the transverse angle needs the walls to span this front to back
SAGITTAL_SPAN_MM = 5.5
PEDICLE_MAX_MM = {"C": 12.0, "T": 16.0, "L": 20.0}   # a section wider than the level's is the pedicle with what joins it laterally
MARCH_MM = 0.25
GAP_VOXELS = 2.0              # a step between voxel centres wider than this many voxels is a gap
REACH_MM = 30.0               # bone that first stands further out than this holds nothing of the pedicle
MIDLINE_CLEAR_MM = 4.0        # bone that first stands within this of the midline is the body's or the lamina's
SIDES = ((1, "right"), (-1, "left"))


class SideMap:
    """One side's sections of bone beside the canal, read on demand and kept: at a row y and a
    layer z, the voxels within three quarters of a pixel of the row and half a layer of the
    height, each at u = side (x - midline) out from the canal's midline, and the first run of
    bone outward, from the first voxel beyond the midline to the first gap of GAP_VOXELS, as
    (medial surface, lateral surface); None where no bone stands within REACH_MM of the
    midline, or one voxel alone."""

    def __init__(self, v: Vertebra, side: int):
        self.v, self.side = v, side
        self.u = side * (v.loc[:, 0] - v.midline)
        self.kept: Dict[Tuple[int, int], Optional[Tuple[float, float]]] = {}

    def chord(self, y0: float, z0: float) -> Optional[Tuple[float, float]]:
        v = self.v
        key = (int(round(10.0 * y0 / v.pixel)), int(round(10.0 * z0 / v.fz)))
        if key not in self.kept:
            self.kept[key] = self.read(y0, z0)
        return self.kept[key]

    def read(self, y0: float, z0: float) -> Optional[Tuple[float, float]]:
        v = self.v
        P = v.loc
        sel = (np.abs(P[:, 1] - y0) <= 0.75 * v.pixel) & (np.abs(P[:, 2] - z0) <= 0.5 * v.fz)
        u = np.sort(self.u[sel])
        u = u[u > 0]
        if len(u) < 2 or u[0] > REACH_MM:
            return None
        gaps = np.flatnonzero(np.diff(u) > GAP_VOXELS * v.fx)
        run = u[:gaps[0] + 1] if len(gaps) else u
        if len(run) < 2:
            return None
        return G.surface(run, False, v.fx), G.surface(run, True, v.fx)

    def x_of(self, u: float) -> float:
        return self.v.midline + self.side * u


# ---- the rows and their columns ----------------------------------------------------------------

def row_places(v: Vertebra) -> np.ndarray:
    """The rows' places front to back: from the body's posterior wall back to the canal's
    posterior wall, half a pixel apart, so that a short pedicle still gives rows enough."""
    return np.arange(v.wall, v.wall_post - 0.25 * v.pixel, -0.5 * v.pixel)


def anchors(v: Vertebra, zb: Tuple[float, float]) -> List[float]:
    """The heights every row is read at first: the body's median, and ANCHOR_SHARE of its
    height above and below it, since a thoracic pedicle stands on the upper part of the body
    and a lumbar one about its middle; each reading settles on its own column, and the row
    keeps the section with the least area (profile)."""
    B = v.body_pts
    z0 = float(np.median(B[:, 2])) if len(B) else 0.5 * (zb[0] + zb[1])
    step = ANCHOR_SHARE * (zb[1] - zb[0])
    return [z0, z0 + step, z0 - step]


def height_run(v: Vertebra, x0: float, y0: float, zc: float) -> Optional[Tuple[float, float]]:
    """The run of bone up the frame's z through (x0, y0) that holds zc: its bottom and top
    surfaces; None where no bone lies within a layer of zc there."""
    P = v.loc
    col = P[(np.abs(P[:, 0] - x0) <= 0.75 * v.pixel) & (np.abs(P[:, 1] - y0) <= 0.75 * v.pixel)]
    if len(col) < 2:
        return None
    z = np.sort(col[:, 2])
    k = int(np.argmin(np.abs(z - zc)))
    if abs(z[k] - zc) > v.fz:
        return None
    steps = np.diff(z)
    lo = k
    while lo > 0 and steps[lo - 1] <= GAP_VOXELS * v.fz:
        lo -= 1
    hi = k
    while hi + 1 < len(z) and steps[hi] <= GAP_VOXELS * v.fz:
        hi += 1
    run = z[lo:hi + 1]
    return G.surface(run, False, v.fz), G.surface(run, True, v.fz)


def section_at(m: SideMap, y0: float, z0: float) -> Optional[dict]:
    """The row's section at z0 and the column at its middle: the medial and lateral surfaces,
    the width between, the column's bottom and top, their middle and the height; None where
    nothing stands there, or where the first bone stands within MIDLINE_CLEAR_MM of the
    midline: that band catches the body's posterior wall, which curves forward from the
    midline, or the lamina, and no canal is so narrow (at the straight phantom the wall's row
    read a section 5.6 mm wide on the body's own wall, and with it in the run the axis turned
    55 degrees)."""
    ch = m.chord(y0, z0)
    if ch is None or ch[0] < MIDLINE_CLEAR_MM:
        return None
    x = m.x_of(0.5 * (ch[0] + ch[1]))
    run = height_run(m.v, x, y0, z0)
    if run is None:
        return None
    return {"y": y0, "u0": ch[0], "u1": ch[1], "w": ch[1] - ch[0], "x": x, "run": run,
            "z": 0.5 * (run[0] + run[1]), "h": run[1] - run[0]}


def settled(m: SideMap, y0: float, z0: float) -> Optional[dict]:
    """The row's section read at z0 and settled once on its own column's middle where that
    lies more than half a layer off."""
    r = section_at(m, y0, z0)
    if r is not None and abs(r["z"] - z0) > 0.5 * m.v.fz:
        r = section_at(m, y0, r["z"]) or r
    return r


def profile(m: SideMap, zs: List[float]) -> List[dict]:
    """Every row's section: read from each anchor height and settled, the one with the least
    area (width times height) kept, since the pedicle is the smallest thing beside the canal
    in any row through it, and a reading that lands on the body's posterolateral corner below
    it or on the articular process above it is taller or wider."""
    rows = []
    for y0 in row_places(m.v):
        found = [r for r in (settled(m, float(y0), z0) for z0 in zs) if r is not None]
        if found:
            rows.append(min(found, key=lambda r: r["w"] * r["h"]))
    return rows


def layers_of(v: Vertebra, run: Tuple[float, float]) -> np.ndarray:
    """The layers over the middle half of a column's run."""
    z0, z1 = run
    zs = np.arange(z0 + 0.25 * (z1 - z0), z1 - 0.25 * (z1 - z0) + 1e-9, v.fz)
    return zs if len(zs) else np.array([0.5 * (z0 + z1)])


def medial_wall(m: SideMap, y: float, layers: np.ndarray) -> float:
    """A row's medial wall for the axis: the median of its section's medial surface over the
    layers, since one layer's surface steps with the raster; not a number where none is read
    or where bone stands within MIDLINE_CLEAR_MM of the midline in one."""
    got = [m.chord(y, float(z)) for z in layers]
    walls = [c[0] for c in got if c is not None]
    if not walls or min(walls) < MIDLINE_CLEAR_MM:
        return NAN
    return float(np.median(walls))


def pedicle_rows(rows: List[dict], near: List[int], walls: Dict[int, float]) -> List[int]:
    """The isthmus rows less those that are not the pedicle's: a row whose wall is not read or
    stands more than CORNER_MM nearer the midline than the rows' median wall, the body's
    corner or the lamina, and a row whose width or height is further than OUTLIER_SHARE from
    the rest's medians, a cut through a process's edge; the rest where that would leave none."""
    kept = [i for i in near if np.isfinite(walls[i])]
    if not kept:
        return []
    wall = float(np.median([walls[i] for i in kept]))
    kept = [i for i in kept if walls[i] >= wall - CORNER_MM]
    w = float(np.median([rows[i]["w"] for i in kept]))
    h = float(np.median([rows[i]["h"] for i in kept]))
    typical = [i for i in kept
               if abs(rows[i]["w"] - w) <= OUTLIER_SHARE * w and abs(rows[i]["h"] - h) <= OUTLIER_SHARE * h]
    return typical or kept


def isthmus(rows: List[dict], v: Vertebra, m: SideMap) -> Optional[Tuple[int, List[int], Dict[int, float]]]:
    """The isthmus: on the profile of the sections' areas (width times height, the ellipse's
    up to a constant) smoothed over three rows (canal.smoothed_values), the least within the
    front FRONT_SHARE of the canal's depth and behind the row at the body's wall, and the rows
    about it within ISTHMUS_SHARE of it, less the rows that are not the pedicle's
    (pedicle_rows), with each row's medial wall; the row nearest the middle of those stands for
    the isthmus, since on a pedicle of even section the least is one row's noise. None with
    too few rows."""
    if len(rows) < 3:
        return None
    a = CANAL.smoothed_values(np.array([r["w"] * r["h"] for r in rows], float))
    depth = v.wall - v.wall_post
    front = [i for i, r in enumerate(rows)
             if 0.5 * v.pixel < v.wall - r["y"] <= FRONT_SHARE * depth and np.isfinite(a[i])]
    if not front:
        return None
    k = min(front, key=lambda i: a[i])
    lim = ISTHMUS_SHARE * a[k]
    lo = k
    while lo > 0 and a[lo - 1] <= lim:
        lo -= 1
    hi = k
    while hi + 1 < len(a) and a[hi + 1] <= lim:
        hi += 1
    about = list(range(lo, hi + 1))
    walls = {i: medial_wall(m, rows[i]["y"], layers_of(v, rows[i]["run"])) for i in about}
    near = pedicle_rows(rows, about, walls)
    if not near:
        return None
    mid = float(np.median([rows[i]["y"] for i in near]))
    return min(near, key=lambda i: abs(rows[i]["y"] - mid)), near, walls


# ---- the axis and the chord --------------------------------------------------------------------

def wall_line(rows: List[dict], near: List[int], walls: Dict[int, float]) -> np.ndarray:
    """The line (slope, intercept in y) through the isthmus rows' walls, or the flat line at
    their median where they are too few or too close for a slope."""
    ys = np.array([rows[i]["y"] for i in near])
    ws = np.array([walls[i] for i in near])
    if len(near) >= 3 and np.ptp(ys) >= AXIS_SPAN_MM:
        return np.polyfit(ys, ws, 1)
    return np.array([0.0, float(np.median(ws))])


def axis_rows(m: SideMap, rows: List[dict], near: List[int], k: int, sec: float, hgt: float,
              walls: Dict[int, float]) -> Tuple[List[int], Dict[int, float], Dict[int, float]]:
    """The rows the axis is read on and their medial walls, with the heights of the pedicle's
    middle in the rows that give one: the isthmus rows, each with its own wall, extended
    forward and back row by row while the next row's wall, read over the isthmus row's layers,
    lies within WALL_FIT_MM of the isthmus rows' line (wall_line) and stands no further in than
    CORNER_MM from their median, up to the body's posterolateral corner in front and the
    lamina or the articular process behind, where the wall steps off the line or juts in. An
    extended row's middle height comes from the column half the isthmus's section out from
    its wall, and counts where that column's height is within HEIGHT_SHARE of the isthmus's."""
    v = m.v
    taken = list(near)
    walls = dict(walls)
    mids = {i: rows[i]["z"] for i in taken}
    line = wall_line(rows, near, walls)
    floor = float(np.median([walls[i] for i in near])) - CORNER_MM
    layers = layers_of(v, rows[k]["run"])
    for step in (-1, 1):
        i = (min(near) if step < 0 else max(near)) + step
        while 0 <= i < len(rows):
            wall = walls[i] if i in near else medial_wall(m, rows[i]["y"], layers)
            if not np.isfinite(wall) or wall < floor or abs(wall - np.polyval(line, rows[i]["y"])) > WALL_FIT_MM:
                break
            taken.append(i)
            walls[i] = wall
            run = height_run(v, m.x_of(wall + 0.5 * sec), rows[i]["y"], rows[k]["z"])
            if run is not None and abs((run[1] - run[0]) - hgt) <= HEIGHT_SHARE * hgt:
                mids[i] = 0.5 * (run[0] + run[1])
            i += step
    return sorted(taken), walls, mids


def axis_from(rows: List[dict], taken: List[int], walls: Dict[int, float], mids: Dict[int, float], side: int) -> Tuple[np.ndarray, str, str]:
    """The axis pointing back through the rows taken, a note where they are too few for an
    axis or for its sagittal angle, and which of its angles were read: "both", "transverse",
    or "neither" where the axis is taken front to back and stands for nothing measured."""
    y = np.array([rows[i]["y"] for i in taken])
    if len(taken) < 3 or np.ptp(y) < AXIS_SPAN_MM:
        return np.array([0.0, -1.0, 0.0]), "the free pedicle is too short to give an axis: taken front to back", "neither"
    across = np.polyfit(y, side * np.array([walls[i] for i in taken]), 1)[0]
    with_z = [i for i in taken if i in mids]
    yz = np.array([rows[i]["y"] for i in with_z])
    if len(with_z) < 3 or np.ptp(yz) < SAGITTAL_SPAN_MM:
        d = np.array([across, 1.0, 0.0])
        note = "the free pedicle spans %.1f mm front to back: its sagittal angle is not read" % (np.ptp(yz) if len(yz) else 0.0)
        reads = "transverse"
    else:
        d = np.array([across, 1.0, np.polyfit(yz, np.array([mids[i] for i in with_z]), 1)[0]])
        note, reads = "", "both"
    return -d / np.linalg.norm(d), note, reads


def chord(v: Vertebra, c0: np.ndarray, d: np.ndarray) -> float:
    """The run of the vertebra's voxels along the line through c0, voxel by voxel."""
    ts = np.arange(-150.0, 150.0 + 1e-9, MARCH_MM)
    world = v.points_world(c0[None, :] + ts[:, None] * d[None, :])
    inv = np.linalg.inv(np.asarray(v.grid.affine, float))
    inside = v.is_bone(np.rint(world @ inv[:3, :3].T + inv[:3, 3]).astype(int))
    k = int(np.argmin(np.abs(ts)))
    if not inside[k]:
        near = np.flatnonzero(inside & (np.abs(ts) <= 2.0))
        if not len(near):
            return NAN
        k = int(near[np.argmin(np.abs(ts[near]))])
    a = k
    while a > 0 and inside[a - 1]:
        a -= 1
    b = k
    while b + 1 < len(ts) and inside[b + 1]:
        b += 1
    if a == 0 or b == len(ts) - 1:
        return NAN
    return float(ts[b] - ts[a] + MARCH_MM)


def wall_slope(v: Vertebra) -> float:
    """dy/dz of the body's posterior wall (body.posterior_wall_slope), so that the sagittal angle
    is taken against the plane square to the wall, as the end-plates' inclinations are, and not
    against the column's line, which leans against a vertebra where its neighbours slip."""
    B = v.body_pts
    if len(B) < G.MIN_CHORD_POINTS:
        return 0.0
    return BODY.posterior_wall_slope(v, B, 0.5 * (B[:, 0].min() + B[:, 0].max()))


# ---- one side, both sides ----------------------------------------------------------------------

def nearest(rows: List[dict], chosen: List[int], value_of, target: float) -> int:
    """Of the chosen rows, the one whose value lies nearest the target."""
    return min(chosen, key=lambda i: abs(value_of(rows[i]) - target))


def one_side(v: Vertebra, side: int, zb: Tuple[float, float]) -> Tuple[Dict[str, float], str, Optional[dict]]:
    if v.level.startswith("C") and "body_foramina" in v.flags:
        return {}, ("the foramen transversarium is not closed in the mask, so the pedicle's lateral border is not "
                    "there: the pedicle is not read"), None
    m = SideMap(v, side)
    rows = profile(m, anchors(v, zb))
    got = isthmus(rows, v, m)
    if got is None:
        return {}, "no bone stands beside the canal in the rows through the pedicle", None
    k, near, walls = got
    sec = float(np.median([rows[i]["w"] for i in near]))
    hgt = float(np.median([rows[i]["h"] for i in near]))
    if sec > PEDICLE_MAX_MM.get(v.level[:1], 20.0):
        return {}, ("no row shows the pedicle free of what joins it laterally, the transverse process's root or "
                    "the lateral mass: its section reads %.0f mm" % sec), None
    taken, walls, mids = axis_rows(m, rows, near, k, sec, hgt, walls)
    d, note, reads = axis_from(rows, taken, walls, mids, side)
    level = np.array([d[0], d[1], 0.0]) / np.linalg.norm(d[:2])
    pitch = abs(d[1]) / math.hypot(d[1], d[2])
    width = sec * abs(level[1])
    height = hgt * (pitch if reads == "both" else 1.0)
    out = {"pedicle_w": width, "pedicle_h": height, "pedicle_area": math.pi * width * height / 4.0,
           "pedicle_angle_transverse": math.degrees(math.atan2(side * d[0], -d[1])),
           "pedicle_angle_sagittal": math.degrees(math.atan2(d[2], -d[1])) - math.degrees(math.atan(wall_slope(v)))}
    c0 = np.array([rows[k]["x"], rows[k]["y"], rows[k]["z"]])
    out["pedicle_chord"] = chord(v, c0, d)
    if reads != "both":
        out["pedicle_angle_sagittal"] = NAN
    if reads == "neither":
        out["pedicle_angle_transverse"] = out["pedicle_chord"] = NAN
    info = {"centre": c0, "axis": d, "height": hgt, "rows": rows, "isthmus": k, "near": near, "taken": taken,
            "walls": walls, "mids": mids, "map": m,
            "width_row": nearest(rows, near, lambda r: r["w"], sec),
            "height_row": nearest(rows, near, lambda r: r["h"], hgt)}
    return out, note, info


def measures(v: Vertebra, zb: Tuple[float, float]) -> Tuple[Dict[str, float], Dict[str, str], Dict[str, dict]]:
    out: Dict[str, float] = {}
    flags: Dict[str, str] = {}
    info: Dict[str, dict] = {}
    for side, name in SIDES:
        got, note, inf = one_side(v, side, zb)
        if note:
            flags["pedicle_" + name] = note
        if inf is not None:
            info[name] = inf
        for k, val in got.items():
            out["%s_%s" % (k, name)] = val
    for k in ("pedicle_w", "pedicle_h", "pedicle_area", "pedicle_angle_transverse", "pedicle_angle_sagittal",
              "pedicle_chord"):
        vals = [out.get("%s_%s" % (k, n), NAN) for _, n in SIDES]
        fin = [x for x in vals if np.isfinite(x)]
        out[k] = float(np.mean(fin)) if len(fin) == 2 else NAN
    if v.touching.any():
        for k in list(out):
            if k.startswith("pedicle_chord"):
                out[k] = NAN
    if "right" in info and "left" in info:
        info["band"] = canal_between(v, info["right"], info["left"])
    return out, flags, info


def band(info: Dict[str, dict]) -> Optional[dict]:
    """What canal.measures takes from the pedicles: the band between them (canal_between), or
    None where a pedicle was not found on both sides."""
    return info.get("band") if info else None


# ---- between the pedicles ----------------------------------------------------------------------

def gap_between(right: SideMap, left: SideMap, y: float, z: float) -> Tuple[float, float, float]:
    """The canal's width between the two sides' medial walls at (y, z), with the walls' x; not
    a number where a wall is not read on either side, or where bone stands within
    MIDLINE_CLEAR_MM of the midline on one, the body's wall or the lamina crossing it."""
    a, b = right.chord(y, z), left.chord(y, z)
    if a is None or b is None or a[0] < MIDLINE_CLEAR_MM or b[0] < MIDLINE_CLEAR_MM:
        return NAN, NAN, NAN
    return a[0] + b[0], left.x_of(b[0]), right.x_of(a[0])


def picked_layer(vals: np.ndarray, within: np.ndarray, pick) -> Optional[Tuple[float, int]]:
    """The value picked (nanmin or nanmax) over the layers `within` on the profile smoothed
    over three layers (canal.smoothed_values), and the layer of the three whose raw value it
    came from; None where none was read."""
    smooth = CANAL.smoothed_values(vals)
    held = np.where(within, smooth, NAN)
    if not np.isfinite(held).any():
        return None
    k = int(pick(held))
    near = [j for j in (k - 1, k, k + 1) if 0 <= j < len(vals) and np.isfinite(vals[j])]
    return float(smooth[k]), (min(near, key=lambda j: abs(vals[j] - smooth[k])) if near else k)


def least_gap(mr: SideMap, ml: SideMap, ys: List[float], z: float) -> Tuple[float, Optional[Tuple[float, float, float, float]]]:
    """The gap at a layer for the least distance: the median over the rows about the isthmus,
    since one row's walls step with the raster, and where the row nearest the median was read."""
    found = [(gap_between(mr, ml, y, z), y) for y in ys]
    found = [(g, y) for g, y in found if np.isfinite(g[0])]
    if not found:
        return NAN, None
    med = float(np.median([g[0] for g, _ in found]))
    (g, xl, xr), y = min(found, key=lambda t: abs(t[0][0] - med))
    return med, (y, z, xl, xr)


def widest_gap(mr: SideMap, ml: SideMap, ys: List[float], z: float) -> Tuple[float, Optional[Tuple[float, float, float, float]]]:
    """The gap at a layer for the greatest distance: the widest over the rows from the body's
    wall back to the isthmus, and where it was read."""
    found = [(gap_between(mr, ml, y, z), y) for y in ys]
    found = [(g, y) for g, y in found if np.isfinite(g[0])]
    if not found:
        return NAN, None
    (g, xl, xr), y = max(found, key=lambda t: t[0][0])
    return g, (y, z, xl, xr)


def canal_between(v: Vertebra, right: dict, left: dict) -> dict:
    """The interpedicular distance, least and greatest, between the two sides' walls over the
    layers of the central half of the pedicles' height, where the walls bulge furthest into
    the canal and above and below which the body's posterolateral corner or the articular
    process stands in a wall's place (at study 0004's T8 the layers below the pedicles read
    the body's corners 2 mm nearer the midline); with where each was read for the drawing:
    (y, z, left wall x, right wall x). A layer counts in the band when its slab, half a layer
    either way, reaches into it."""
    mr, ml = right["map"], left["map"]
    yc = 0.5 * (right["centre"][1] + left["centre"][1])
    zc = 0.5 * (right["centre"][2] + left["centre"][2])
    h = 0.5 * (right["height"] + left["height"])
    n = int(math.ceil(0.25 * h / v.fz)) + 2
    zs = zc + v.fz * np.arange(-n, n + 1)
    central = np.abs(zs - zc) <= 0.25 * h + 0.5 * v.fz
    out = {"zc": zc, "h": h, "yc": yc, "interpedicular": NAN, "interpedicular_max": NAN}
    about = [float(y) for y in row_places(v) if abs(y - yc) <= 1.5 * v.pixel]
    least = [least_gap(mr, ml, about, float(z)) for z in zs]
    got = picked_layer(np.array([g for g, _ in least], float), central, np.nanargmin)
    if got is not None:
        out["interpedicular"], j = got
        out["interpedicular_at"] = least[j][1]
    front = [float(y) for y in row_places(v) if y >= yc - 0.5 * v.pixel]
    widest = [widest_gap(mr, ml, front, float(z)) for z in zs]
    got = picked_layer(np.array([g for g, _ in widest], float), central, np.nanargmax)
    if got is not None:
        out["interpedicular_max"], j = got
        out["interpedicular_max_at"] = widest[j][1]
    return out
