"""The phantom benchmarks: every measure the phantom fixes, read on grids from thin to thick and at
several tilts, against its truth; and the mask-edge and disc readings of the exact, grown and
shrunk masks, with the same readings of real CTs gathered by region."""
from __future__ import annotations

import math
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Tuple

import numpy as np
from scipy import ndimage

from maskedge import disc as D
from maskedge import edge as E
from morphometry import measure as M
from morphometry.tests import phantom as P
from scanimport import geometry as G

LEVELS = ["L2", "L3", "L4"]
# (name, spacing): a thin research scan, ENHANCE.PET's coarsest thin series, two clinical thicknesses
GRIDS = (("1.0 mm", (0.8, 0.8, 1.0)), ("1.25 mm", (0.98, 0.98, 1.25)), ("2.5 mm", (0.86, 0.86, 2.5)),
         ("5.0 mm", (0.98, 0.98, 5.0)))
TILTS = (0.0, 10.0, 20.0)
TURNS = (0.0, 11.0)
TILT_AXIS = (1.0, 0.2, 0.0)
DISC_KEYS = ("disc_h_ant", "disc_h_mid", "disc_h_post")


def truths() -> Dict[str, float]:
    v = P.Vert()
    t = P.truth(v)
    t.update(P.canal_profile(v))
    t.update({k: P.Joint().gap for k in DISC_KEYS})
    return t


def one(job: Tuple[str, Tuple[float, float, float], float, float]) -> List[dict]:
    grid_name, spacing, tilt, turn = job
    placed = P.straight(LEVELS, P.Vert(), tilt=(TILT_AXIS, tilt))
    lab, aff = P.draw(placed, spacing=spacing, grid_turn=((0.0, 0.0, 1.0), turn))
    rows = M.measure_volume(lab, G.VoxelGrid(aff, lab.shape), {P.LEVEL_IDS[lv]: lv for lv in LEVELS}, "phantom",
                            pelvis=False)
    t = truths()
    out = []
    for r in rows:
        key = r["key"]
        if r["level"] not in ("L3", "L2-L3", "L3-L4") or key not in t or not isinstance(r["value"], float):
            continue
        if r["level"] != "L3" and key not in DISC_KEYS:
            continue
        val = r["value"]
        out.append({"grid": grid_name, "slice_mm": spacing[2], "tilt_deg": tilt, "turn_deg": turn, "level": r["level"],
                    "key": key, "value": val, "truth": t[key], "error": val - t[key] if math.isfinite(val) else math.nan})
    return out


def phantom_truth(workers: int = 1) -> List[dict]:
    jobs = [(name, sp, tilt, turn) for name, sp in GRIDS for tilt in TILTS for turn in TURNS]
    rows: List[dict] = []
    with ProcessPoolExecutor(workers) as pool:
        for got in pool.map(one, jobs):
            rows += got
    return rows


# ---- the mask's edge on the phantom -------------------------------------------------------------

def phantom_ct(placed: P.Placed, lab: np.ndarray, aff: np.ndarray) -> np.ndarray:
    """The CT maskedge's tests draw for the phantom (maskedge/tests/test_edge.py, ct_for)."""
    from maskedge.tests import test_edge as T
    return T.ct_for(placed, lab, aff)


def maskedge_phantom() -> List[dict]:
    _, grid, names, ct, masks = phantom_masks()
    out = []
    for name, mask in masks.items():
        for r in E.measure_arrays(ct, mask, grid, names, name):
            if r["level"] == "L3":
                out.append({"source": "phantom", "case": name, "region": r["region"], "vertebrae": 1,
                            "median": r["offset_median"], "q25": r["offset_q25"], "q75": r["offset_q75"]})
    return out


def maskedge_ct(rows: List[dict], study: str) -> List[dict]:
    """One study's maskedge rows as the median over its vertebrae of each region's median offset."""
    got = E.summary(rows)
    return [{"source": "ENHANCE.PET CT", "case": study, "region": reg, "vertebrae": got[reg]["vertebrae"],
             "median": got[reg]["median"], "q25": got[reg]["q25"], "q75": got[reg]["q75"]}
            for reg in E.REGIONS if reg in got]


# ---- the disc in the CT -------------------------------------------------------------------------

def phantom_masks() -> Tuple[np.ndarray, G.VoxelGrid, Dict[int, str], np.ndarray, Dict[str, np.ndarray]]:
    """The phantom's labels, grid, names and CT, and its exact, grown and shrunk masks (L3 grown or
    shrunk by one voxel), as maskedge's tests draw them."""
    from maskedge.tests import test_edge as T
    placed = P.straight(LEVELS, P.Vert())
    lab, aff = P.draw(placed, spacing=tuple(T.SPACING))
    grid = G.VoxelGrid(aff, lab.shape)
    names = {P.LEVEL_IDS[lv]: lv for lv in LEVELS}
    ct = phantom_ct(placed[1], lab, aff)
    l3 = P.LEVEL_IDS["L3"]
    grown = lab.copy()
    grown[ndimage.binary_dilation(lab == l3) & (lab == 0)] = l3
    shrunk = lab.copy()
    shrunk[(lab == l3) & ~ndimage.binary_erosion(lab == l3)] = 0
    return lab, grid, names, ct, {"exact": lab, "grown one voxel": grown, "shrunk one voxel": shrunk}


def disc_phantom() -> List[dict]:
    """The phantom's two discs read by maskedge.disc on the exact, grown and shrunk masks, against
    the true gap."""
    _, grid, names, ct, masks = phantom_masks()
    out = []
    for case, mask in masks.items():
        for r in D.measure_arrays(ct, mask, grid, names, case):
            out.append({"source": "phantom", "case": case, "region": r["disc"], "discs": 1, "read": r["read"],
                        "masks_gap": r["masks_gap"], "ct_height": r["ct_height"], "truth": P.Joint().gap,
                        "median": r["difference"], "q25": r["difference_q25"], "q75": r["difference_q75"]})
    return out


def disc_ct(rows: List[dict], study: str) -> List[dict]:
    """One study's disc rows as the median over its discs, by region, of the masks' gap less the CT's."""
    got = D.summary(rows)
    return [{"source": "ENHANCE.PET CT", "case": study, "region": reg, "discs": g["discs"], "read": "",
             "masks_gap": g["masks_gap"], "ct_height": g["ct_height"], "truth": "", "median": g["difference"],
             "q25": g["q25"], "q75": g["q75"]} for reg, g in got.items()]


# ---- where across the canal its width is read ----------------------------------------------------

SHAPE_LEVELS = ("C4", "C5", "C6", "T4", "T8", "L1", "L2", "L3", "L4", "L5")


def hole_rows(hole: np.ndarray) -> Dict[float, float]:
    """A canal slab's hole as its width at each row front to back: the span of the pixel centres
    in the row, so a pixel narrower than the surfaces the measures read."""
    ys = np.round(hole[:, 1], 3)
    return {float(y): float(np.ptp(hole[ys == y, 0])) for y in np.unique(ys)}


def canal_shape(labels: np.ndarray, grid: G.VoxelGrid, names: Dict[int, str], study: str) -> List[dict]:
    """Per level, over the full rings of the middle half of the canal's height: the width the
    canal measures read (across the hole's middle front to back), the hole's width at that middle,
    and its widest in the front half, where the pedicles join the body; medians over the rings."""
    out = []
    for lv, v in E.vertebrae(labels, grid, names).items():
        if lv not in SHAPE_LEVELS:
            continue
        rings = v.full_rings()
        if not rings:
            continue
        lo, hi = np.percentile([s.z for s in rings], [25, 75])
        mid, front, read = [], [], []
        for s in rings:
            if not lo <= s.z <= hi:
                continue
            rows = hole_rows(s.hole)
            ys = np.array(sorted(rows))
            ym = 0.5 * (ys.min() + ys.max())
            mid.append(rows[float(ys[np.argmin(np.abs(ys - ym))])])
            front.append(max(rows[float(y)] for y in ys if y >= ym))
            read.append(s.width)
        if not mid:
            continue
        out.append({"study": study, "level": lv, "rings": len(mid), "width_read": float(np.median(read)),
                    "hole_middle": float(np.median(mid)), "hole_front_widest": float(np.median(front)),
                    "front_less_middle": float(np.median(front) - np.median(mid))})
    return out
