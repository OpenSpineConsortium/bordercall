"""Each end-plate's own width and depth, without what the label joins to the plate's edge.

A whole-vertebra label gives the body with everything fused to it, and scanimport's end-plate
slab (geometry.body_chords) takes the extent of all of it: in the neck the uncinate processes,
which rise above the upper plate at its posterolateral edges, and the costal roots of the
transverse processes; in the thorax the pedicles' bases and the rib heads' facets at the
posterolateral corners; at L5 the transverse processes' roots. On 89 gold tier CTs (calibration
runs of 2026-10-31, SchwingNet docs/research/morphometry-against-panjabi.md) that slab's upper
width read 4 to 6 mm over Panjabi's EPWu at C3 to C6 and at T10 to L3, 11 mm at L5, and 14 mm at
T1, while its depth read within about a millimetre.

So the plate is read on its own layer and its front half. The slab is the body's points within
the end-plate's thickness inside its plane (scanimport's plate_plane and ENDPLATE_SHARE) and no
more than half a voxel layer beyond it, which leaves out an uncinate process or a lip rising past
the plate. The width is the widest row of that slab across the front half of the body's depth at
the plate, each row taken as the run of cells through the row's middle, so a piece apart from
the body in the row does not join it; every appendage named above stands on the back half. The
depth is the plate's front surface at the midline, the cells within MIDLINE_MM of it, less the
canal's anterior wall, as Panjabi's EPD is taken.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from scanimport import geometry as G

from .anatomy import Vertebra, square_to_wall

NAN = float("nan")
FRONT_SHARE = 0.5          # the width is read over this front share of the plate's depth
BEYOND_LAYERS = 0.5        # the slab reaches this many voxel layers beyond the plate's plane
MIDLINE_MM = 3.0           # the depth is read on the cells within this of the plate's middle
MIN_POINTS = 20


def measures(v: Vertebra) -> Tuple[Dict[str, float], Dict[str, str]]:
    """plate_w, plate_d (the upper end plate) and plate_w_lower, plate_d_lower."""
    out = {k: NAN for k in ("plate_w", "plate_d", "plate_w_lower", "plate_d_lower")}
    B = square_to_wall(v, v.body_pts)
    if len(B) < G.MIN_BODY_VOXELS or v.touching[v.body].any():
        return out, {}
    fx = v.grid.footprint(v.frame.ex)
    fz = v.grid.footprint(v.frame.ez)
    pixel = v.pixel
    inner = G.central(B[:, 0], B[:, 1])
    t = max(min(max(G.ENDPLATE_SHARE * (float(np.ptp(B[:, 2])) + fz), G.ENDPLATE_MM[0]), G.ENDPLATE_MM[1]), fz)
    for top, suffix in ((True, ""), (False, "_lower")):
        slab = plate_layer(B, inner, pixel, t, top, fz)
        if len(slab) < MIN_POINTS:
            continue
        out["plate_w" + suffix] = front_width(slab, v.wall_y0, pixel)
        out["plate_d" + suffix] = midline_depth(slab, v.wall_y0, pixel)
    return out, {}


def plate_layer(B: np.ndarray, inner: np.ndarray, pixel: float, t: float, top: bool, layer: float) -> np.ndarray:
    """The body's points within t inside the plate's plane and no more than BEYOND_LAYERS layers past it."""
    c = G.plate_plane(B, inner, pixel, top, layer)
    d = B[:, 2] - (c[0] + c[1] * B[:, 0] + c[2] * B[:, 1])
    if not top:
        d = -d
    return B[(d >= -t - 1e-6) & (d <= BEYOND_LAYERS * layer + 1e-6)]


def row_runs(slab: np.ndarray, pixel: float) -> List[Tuple[float, float]]:
    """Each row of the slab across y: its mean y and the width of the run of cells through its middle."""
    out = []
    rows = np.floor((slab[:, 1] - slab[:, 1].min()) / pixel).astype(int)
    for r in np.unique(rows):
        xs = slab[rows == r, 0]
        if len(xs) < 2:
            continue
        xm = 0.5 * (xs.min() + xs.max())
        cells = set(np.floor((xs - xm) / pixel).astype(int).tolist())
        start = 0 if 0 in cells else (-1 if -1 in cells else None)
        if start is None:
            continue
        lo = hi = start
        while lo - 1 in cells:
            lo -= 1
        while hi + 1 in cells:
            hi += 1
        out.append((float(slab[rows == r, 1].mean()), (hi - lo + 1) * pixel))
    return out


def front_width(slab: np.ndarray, wall: float, pixel: float) -> float:
    front = float(slab[:, 1].max())
    reach = front - FRONT_SHARE * (front - wall)
    widths = [w for y, w in row_runs(slab, pixel) if y >= reach]
    return max(widths) if widths else NAN


def midline_depth(slab: np.ndarray, wall: float, pixel: float) -> float:
    xm = 0.5 * (slab[:, 0].min() + slab[:, 0].max())
    near = slab[np.abs(slab[:, 0] - xm) <= MIDLINE_MM]
    return float(near[:, 1].max() - wall + 0.5 * pixel) if len(near) else NAN
