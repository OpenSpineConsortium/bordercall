"""The disc's height as the CT shows it, against the height the two masks leave between them.

The edge reading (edge.py) skips every point with a neighbour's label within CLEAR_MM of it, so
it cannot read an end-plate where two masks nearly meet, and that is where a mask that takes in
part of the disc would show. Here each disc is read along lines parallel to the column's line in
the frame of the vertebra below, as morphometry reads the disc heights, through a grid of points
over the middle of that vertebra's body (GRID_SHARES of its width and of its depth, clear of the
rims and the uncinate processes). Along each line:

- the masks' gap is the distance from the last sample of the lower vertebra's label to the first
  of the upper's, less one step, the two surfaces lying half a step outside those samples; the
  line counts only where nothing else is labelled between them;
- the CT's disc is the least value within JUNCTION_MM of the masks' junction, each end-plate's
  cortex the greatest within SEARCH_MM of it on its own side, and the disc's height the
  distance between the two half-maximum crossings, each where the CT falls half-way from that
  side's cortex to the disc's least, the edge a reader's caliper on a bone window is set to; the
  line counts only where both cortices stand MIN_CONTRAST_HU or more above the disc.

The difference, the masks' gap less the CT's, is negative where the masks take in the disc. The
summary counts a disc only where MIN_LINES_READ of its lines show both cortices.

    python -m maskedge disc --ct CT.nii.gz --labels MASK.nii.gz --scheme enhance --study 0004 --out disc.csv
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy import ndimage

from morphometry import anatomy as A
from scanimport import LEVELS
from scanimport import geometry as G

from . import edge as E

NAN = float("nan")
STEP_MM = 0.2
GRID_SHARES = (0.3, 0.4, 0.5, 0.6, 0.7)
FOOTPRINT_PERCENTILES = (10.0, 90.0)
JUNCTION_MM = 3.0
SEARCH_MM = 8.0
MIN_CONTRAST_HU = 150.0
MIN_LINES_READ = 8
REGION_OF = {**{lv: "cervical" for lv in ("C2", "C3", "C4", "C5", "C6", "C7")},
             **{"T%d" % i: "thoracic" for i in range(1, 13)},
             **{lv: "lumbar" for lv in ("L1", "L2", "L3", "L4", "L5", "L6")}}


def line_grid(L: A.Vertebra) -> np.ndarray:
    """The (x, y) of every line in the lower vertebra's frame: GRID_SHARES of the body's footprint
    along x by the same along y, the footprint taken between FOOTPRINT_PERCENTILES of its points."""
    b = L.body_pts
    (x0, x1), (y0, y1) = (np.percentile(b[:, k], FOOTPRINT_PERCENTILES) for k in (0, 1))
    xs = [x0 + t * (x1 - x0) for t in GRID_SHARES]
    ys = [y0 + t * (y1 - y0) for t in GRID_SHARES]
    return np.array([(x, y) for x in xs for y in ys])


def sample_lines(L: A.Vertebra, xy: np.ndarray, s: np.ndarray, arr: np.ndarray, order: int,
                 cval: float) -> np.ndarray:
    """arr read along each line (x, y, s) of the lower vertebra's frame, as (lines, len(s))."""
    local = np.concatenate([np.repeat(xy, len(s), 0), np.tile(s, len(xy))[:, None]], 1)
    world = L.points_world(local)
    aff = np.asarray(L.grid.affine, float)
    idx = (world - aff[:3, 3]) @ np.linalg.inv(aff[:3, :3]).T
    got = ndimage.map_coordinates(arr, idx.T, order=order, mode="constant", cval=cval, output=np.float32)
    return got.reshape(len(xy), len(s))


def masks_gap(lab: np.ndarray, s: np.ndarray, low_id: int, up_id: int) -> Tuple[float, int, int]:
    """The gap the two labels leave along one line, and the indices of the lower label's last
    sample and the upper's first; NaN where the line misses either or meets a third label."""
    up = np.flatnonzero(lab == up_id)
    if not len(up):
        return NAN, -1, -1
    low = np.flatnonzero(lab[:up[0]] == low_id)
    if not len(low):
        return NAN, -1, -1
    between = lab[low[-1] + 1:up[0]]
    if (between != 0).any():
        return NAN, -1, -1
    return float(s[up[0]] - s[low[-1]] - STEP_MM), int(low[-1]), int(up[0])


def rise(hu: np.ndarray, start: int, stop: int, level: float) -> float:
    """Walking from index start toward stop, the first place the profile reaches level, linearly
    between samples, as an index; NaN where it never does."""
    step = 1 if stop > start else -1
    for j in range(start + step, stop + step, step):
        if hu[j] >= level:
            a, b = hu[j - step], hu[j]
            return (j - step) + step * ((level - a) / (b - a) if b != a else 0.0)
    return NAN


def ct_disc(hu: np.ndarray, s: np.ndarray, j_low: int, j_up: int) -> Tuple[float, float]:
    """The CT's disc height along one line, read about the masks' junction (module docstring),
    and the lesser cortex's contrast over the disc; NaN where the CT shows no disc."""
    n = len(s)
    reach = int(round(JUNCTION_MM / STEP_MM))
    search = int(round(SEARCH_MM / STEP_MM))
    lo, hi = max(j_low - reach, 0), min(j_up + reach, n - 1)
    dip = lo + int(np.argmin(hu[lo:hi + 1]))
    below = slice(max(dip - search, 0), dip + 1)
    above = slice(dip, min(dip + search, n - 1) + 1)
    pb = below.start + int(np.argmax(hu[below]))
    pa = above.start + int(np.argmax(hu[above]))
    contrast = float(min(hu[pb], hu[pa]) - hu[dip])
    if contrast < MIN_CONTRAST_HU or pb == dip or pa == dip:
        return NAN, contrast
    eb = rise(hu, dip, pb, 0.5 * (hu[pb] + hu[dip]))
    ea = rise(hu, dip, pa, 0.5 * (hu[pa] + hu[dip]))
    if not (np.isfinite(eb) and np.isfinite(ea)):
        return NAN, contrast
    return float((ea - eb) * STEP_MM), contrast


def pair_rows(U: A.Vertebra, L: A.Vertebra, hu: np.ndarray, labels: np.ndarray, ids: Dict[str, int],
              study: str) -> Optional[Dict[str, object]]:
    """One disc: the lines read, and the medians of the masks' gap, the CT's height, their
    difference and the contrast, with the difference's quartiles."""
    up_local = L.frame.local(U.points_world(U.body_pts))
    z0, z1 = float(np.median(L.body_pts[:, 2])), float(np.median(up_local[:, 2]))
    if z1 <= z0:
        return None
    s = np.round(z0 + STEP_MM * np.arange(int((z1 - z0) / STEP_MM) + 1), 6)
    xy = line_grid(L)
    lab = sample_lines(L, xy, s, labels, 0, 0.0).round().astype(int)
    ct = sample_lines(L, xy, s, hu, 1, -1000.0)
    got = []
    for k in range(len(xy)):
        gap, jl, ju = masks_gap(lab[k], s, ids[L.level], ids[U.level])
        if not np.isfinite(gap):
            continue
        height, contrast = ct_disc(ct[k], s, jl, ju)
        got.append((gap, height, contrast))
    read = [g for g in got if np.isfinite(g[1])]
    row = {"study": study, "disc": "%s-%s" % (U.level, L.level), "region": REGION_OF.get(L.level, ""),
           "lines": len(xy), "masks_lines": len(got), "read": len(read)}
    if read:
        arr = np.array(read)
        diff = arr[:, 0] - arr[:, 1]
        q = np.percentile(diff, [25, 50, 75])
        row.update({"masks_gap": float(np.median(arr[:, 0])), "ct_height": float(np.median(arr[:, 1])),
                    "difference": float(q[1]), "difference_q25": float(q[0]), "difference_q75": float(q[2]),
                    "contrast": float(np.median(arr[:, 2]))})
    return row


def measure_arrays(hu: np.ndarray, labels: np.ndarray, grid: G.VoxelGrid, names: Dict[int, str],
                   study: str) -> List[Dict[str, object]]:
    """Every disc between two whole vertebrae the volume holds, one row each."""
    vs = E.vertebrae(labels, grid, names)
    ids = {lv: i for i, lv in names.items()}
    order = [lv for lv in LEVELS if lv in vs]
    rows = []
    for up, low in zip(order, order[1:]):
        if LEVELS.index(low) - LEVELS.index(up) != 1:
            continue
        row = pair_rows(vs[up], vs[low], hu, labels, ids, study)
        if row is not None:
            rows.append(row)
    return rows


def measure_study(ct_path: str, labels_path: str, scheme: str, study: str) -> List[Dict[str, object]]:
    from scanimport import volume as V
    labels, grid, names, _, _ = V.read_labels(labels_path, scheme)
    raw, slope, inter, affine = E.read_ct(ct_path)
    if raw.shape != labels.shape or not np.allclose(affine, np.asarray(grid.affine, float), atol=1e-3):
        raise SystemExit("%s and %s are not on one grid" % (ct_path, labels_path))
    hu = raw if (slope, inter) == (1.0, 0.0) else (raw * np.float32(slope) + np.float32(inter)).astype(np.float32)
    return measure_arrays(hu, labels, grid, names, study)


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return NAN


def summary(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, float]]:
    """By region, over the discs read on MIN_LINES_READ lines or more (a third of the grid; a disc
    read on one or two lines is where the CT shows almost no edge, and its reading is as likely a
    dip inside a body as the disc): how many, and the medians of their masks' gaps, CT heights and
    differences, with the differences' quartiles."""
    out: Dict[str, Dict[str, float]] = {}
    for region in ("cervical", "thoracic", "lumbar"):
        got = [r for r in rows if r.get("region") == region and np.isfinite(num(r.get("difference")))
               and num(r.get("read")) >= MIN_LINES_READ]
        if not got:
            continue
        diff = np.array([float(r["difference"]) for r in got])
        q = np.percentile(diff, [25, 50, 75])
        out[region] = {"discs": len(got), "masks_gap": float(np.median([float(r["masks_gap"]) for r in got])),
                       "ct_height": float(np.median([float(r["ct_height"]) for r in got])),
                       "difference": float(q[1]), "q25": float(q[0]), "q75": float(q[2])}
    return out
