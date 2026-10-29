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


# ---- what a change of frame moved -----------------------------------------------------------------

AXIS_KEYS = ("axis_offset", "plate_offset", "axis_residual")
SKIP_KEYS = ("lowest_lumbar", "intercristal_level")
TOL_MM, TOL_DEG, TOL_SHARE = 0.75, 1.5, 0.04
ANGLE_WORDS = ("angle", "incl", "wedge", "tropism", "segment_", "lordosis", "kyphosis", "cobb", "slope", "tilt",
               "incidence")
RATIO_WORDS = ("index", "share", "pct", "ratio")


def kind_of(key: str) -> str:
    """A key's kind, which sets the tolerance its shift is judged against: the phantom's bounds,
    0.75 mm for a length, 1.5 degrees for an angle, 4 per cent for an area or a volume, 0.04 for
    a ratio."""
    if any(w in key for w in ANGLE_WORDS):
        return "angle"
    if "area" in key:
        return "area"
    if "volume" in key:
        return "volume"
    if any(w in key for w in RATIO_WORDS):
        return "ratio"
    return "length"


def beyond(kind: str, before: float, shift: float) -> bool:
    if kind == "angle":
        return abs(shift) > TOL_DEG
    if kind in ("area", "volume"):
        return abs(shift) > TOL_SHARE * abs(before)
    if kind == "ratio":
        return abs(shift) > TOL_SHARE
    return abs(shift) > TOL_MM


def region_of(level: str) -> str:
    """cervical, thoracic or lumbar by the level's letter, a disc under its lower vertebra;
    pelvis and column as they are; nothing for a study's own rows."""
    if level in ("pelvis", "column"):
        return level
    if level == "study":
        return ""
    low = level.split("-")[-1]
    return {"C": "cervical", "T": "thoracic", "L": "lumbar"}.get(low[:1], "")


def numbered(rows: List[dict]) -> Dict[Tuple[str, str, str], float]:
    out = {}
    for r in rows:
        key = r["key"]
        if key.startswith("flag") or key in AXIS_KEYS or key in SKIP_KEYS:
            continue
        try:
            v = float(r["value"])
        except (TypeError, ValueError):
            continue
        if math.isfinite(v):
            out[(r["study"], r["level"], key)] = v
    return out


def axis_shift(before: List[dict], after: List[dict]) -> List[dict]:
    """Each key's shift between two runs' rows, after less before, paired by study and level and
    gathered by region, over the studies both runs hold: how many pairs, the median shift and its
    10th and 90th percentiles, the median absolute shift, and the share of pairs beyond the
    tolerance of the key's kind. A value read in one run and not the other is no pair and is
    counted apart (lost, gained)."""
    b, a = numbered(before), numbered(after)
    studies = {k[0] for k in b} & {k[0] for k in a}
    by: Dict[Tuple[str, str], List[Tuple[float, float]]] = {}
    lost: Dict[Tuple[str, str], int] = {}
    gained: Dict[Tuple[str, str], int] = {}
    for k, vb in b.items():
        reg = region_of(k[1])
        if not reg or k[0] not in studies:
            continue
        if k in a:
            by.setdefault((reg, k[2]), []).append((vb, a[k] - vb))
        else:
            lost[(reg, k[2])] = lost.get((reg, k[2]), 0) + 1
    for k in a:
        reg = region_of(k[1])
        if reg and k[0] in studies and k not in b:
            gained[(reg, k[2])] = gained.get((reg, k[2]), 0) + 1
    out = []
    for (reg, key), pairs in sorted(by.items()):
        kind = kind_of(key)
        shifts = np.array([d for _, d in pairs])
        out.append({"region": reg, "key": key, "kind": kind, "n": len(pairs),
                    "median_shift": float(np.median(shifts)), "p10_shift": float(np.percentile(shifts, 10)),
                    "p90_shift": float(np.percentile(shifts, 90)), "median_abs": float(np.median(np.abs(shifts))),
                    "share_beyond": float(np.mean([beyond(kind, v, d) for v, d in pairs])),
                    "lost": lost.get((reg, key), 0), "gained": gained.get((reg, key), 0)})
    return out


def axis_turn(after: List[dict]) -> List[dict]:
    """By level, the turn from the column's line onto the vertebra's own axis (axis_offset) over
    the vertebrae whose frame was turned: how many, the median and the 10th and 90th
    percentiles, the median residual after the turn, and beside them how many vertebrae kept
    the column's line (the flag axis), whose turn is nought by construction and is left out."""
    turns: Dict[Tuple[str, str], float] = {}
    resid: Dict[Tuple[str, str], float] = {}
    kept = set()
    for r in after:
        at = (r["study"], r["level"])
        if r["key"] == "flag:axis":
            kept.add(at)
        elif r["key"] in ("axis_offset", "axis_residual"):
            try:
                v = float(r["value"])
            except (TypeError, ValueError):
                continue
            if math.isfinite(v):
                (turns if r["key"] == "axis_offset" else resid)[at] = v
    levels = sorted({at[1] for at in turns} | {at[1] for at in kept}, key=level_rank)
    out = []
    for lv in levels:
        a = np.array([v for at, v in turns.items() if at[1] == lv and at not in kept])
        res = [v for at, v in resid.items() if at[1] == lv and at not in kept]
        if not len(a):
            continue
        out.append({"level": lv, "n": len(a), "median_deg": float(np.median(a)), "p10_deg": float(np.percentile(a, 10)),
                    "p90_deg": float(np.percentile(a, 90)), "median_residual_deg": float(np.median(res)) if res else math.nan,
                    "kept_column_line": sum(1 for at in kept if at[1] == lv)})
    return out


def level_rank(level: str) -> float:
    letter, num = level[:1], level[1:]
    base = {"C": 0, "T": 100, "L": 200}.get(letter, 300)
    return base + (float(num) if num.isdigit() else 0.0)
