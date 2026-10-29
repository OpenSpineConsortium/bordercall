"""The offsets of a mask's surface from the bone's edge in the CT, point by point along each
surface's outward normal, gathered region by region of every vertebra.

The vertebrae are built as morphometry.measure builds them (the label's main piece, the
column's line through whole neighbours, morphometry.anatomy.build), so the regions are those
of the same frame the measures read: z the column's line, y from the canal toward the body.
A surface point is a voxel of the vertebra with a face-neighbour outside it; its outward
normal is the gradient of the vertebra's mask smoothed by one voxel, turned outward. A point
is read only where the line beyond it holds no label at all from CLEAR_MM[0] to CLEAR_MM[1]
(not a neighbour across a thin disc, not the vertebra itself folding back), and only where the
CT along the line shows an edge: a peak in PEAK_MM standing MIN_CONTRAST_HU or more above the
median in OUTSIDE_MM, with the fall through half-way between them before OUTSIDE_MM begins.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np
from scipy import ndimage

from morphometry import anatomy as A
from morphometry import measure as M
from scanimport import LEVELS
from scanimport import geometry as G
from scanimport import volume as V

NAN = float("nan")
PROFILE_MM = (-5.0, 4.0)
STEP_MM = 0.2
PEAK_MM = (-4.0, 2.0)
OUTSIDE_MM = (2.5, 3.5)
MIN_CONTRAST_HU = 150.0
CLEAR_MM = (0.6, 3.5)
COS_REGION = math.cos(math.radians(30.0))
MIDDLE = (0.2, 0.8)
POINTS_PER_REGION = 400
MARGIN_MM = 8.0
SMOOTH_VOXELS = 1.0
REGIONS = ("upper_plate", "lower_plate", "lateral_wall", "anterior_wall", "posterior_wall", "arch")


def vertebrae(vol: np.ndarray, grid: G.VoxelGrid, names: Dict[int, str]) -> Dict[str, A.Vertebra]:
    """Each level from C2 to L6 the volume holds whole, built as morphometry.measure builds it."""
    vox = V.vertebra_voxels(vol, names)
    for lv in list(vox):
        vox[lv], _ = M.main_piece(vox[lv])
    spine = [lv for lv in LEVELS if lv in vox and lv != "sacrum"]
    cents = [grid.world(vox[lv].astype(float)).mean(0) for lv in spine]
    axes = dict(zip(spine, M.column_line(cents, M.whole_levels(vox, spine, vol.shape), grid.superior())))
    out: Dict[str, A.Vertebra] = {}
    for lv in spine:
        if lv in M.SKIP or len(vox[lv]) < G.MIN_BODY_VOXELS:
            continue
        v = A.build(lv, vox[lv], grid, axes[lv], V.touching_edge(vox[lv], vol.shape))
        if A.usable(v) and not v.touching.any():
            out[lv] = v
    return out


def samples() -> np.ndarray:
    n = int(round((PROFILE_MM[1] - PROFILE_MM[0]) / STEP_MM)) + 1
    return np.round(PROFILE_MM[0] + STEP_MM * np.arange(n), 6)


def box(idx: np.ndarray, shape, spacing: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    m = np.ceil(MARGIN_MM / spacing).astype(int)
    return np.maximum(idx.min(0) - m, 0), np.minimum(idx.max(0) + m + 1, np.asarray(shape))


def crop(arr: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    return arr[lo[0]:hi[0], lo[1]:hi[1], lo[2]:hi[2]]


def outward_normals(inside: np.ndarray, at: np.ndarray, affine3: np.ndarray) -> np.ndarray:
    """The unit outward normal in world space at each of the points `at` (indices into inside):
    a mask m(w) read through the index map i = inv(A)(w - t) has the world gradient inv(A)^T
    times its gradient over the indices."""
    smooth = ndimage.gaussian_filter(inside.astype(np.float32), SMOOTH_VOXELS)
    g = np.stack([np.gradient(smooth, axis=k)[tuple(at.T)] for k in range(3)], 1)
    w = -(g @ np.linalg.inv(affine3))
    norm = np.linalg.norm(w, axis=1)
    return np.where(norm[:, None] > 1e-9, w / np.maximum(norm, 1e-9)[:, None], np.nan)


def along(arr: np.ndarray, at: np.ndarray, steps: np.ndarray, s: np.ndarray, order: int, cval: float) -> np.ndarray:
    """arr read at at + s * steps for every point and every s, as (points, len(s))."""
    q = at[:, None, :] + s[None, :, None] * steps[:, None, :]
    got = ndimage.map_coordinates(arr, q.reshape(-1, 3).T, order=order, mode="constant", cval=cval)
    return got.reshape(len(at), len(s))


def crossing(prof: np.ndarray, s: np.ndarray, level: np.ndarray, after: np.ndarray) -> np.ndarray:
    """Per profile, where it first falls below its level at an index past `after`, linearly
    between the samples either side; NaN where it never does."""
    rows = np.arange(len(prof))
    hit = (prof < level[:, None]) & (np.arange(len(s))[None, :] > after[:, None])
    j = np.argmax(hit, axis=1)
    jp = np.maximum(j - 1, 0)
    a, b = prof[rows, jp], prof[rows, j]
    frac = np.where(a != b, (a - level) / np.where(a != b, a - b, 1.0), 0.0)
    return np.where(hit.any(1), s[jp] + frac * (s[j] - s[jp]), NAN)


def bone_edge(hu: np.ndarray, s: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The half-maximum edge outward of the cortex's peak, and the peak's contrast over the
    level outside; the edge is NaN where the profile shows none (module docstring)."""
    pk, out = (s >= PEAK_MM[0]) & (s <= PEAK_MM[1]), (s >= OUTSIDE_MM[0]) & (s <= OUTSIDE_MM[1])
    jp = np.flatnonzero(pk)[0] + np.argmax(hu[:, pk], axis=1)
    peak = hu[np.arange(len(hu)), jp]
    level = np.median(hu[:, out], axis=1)
    edge = crossing(hu, s, 0.5 * (peak + level), jp)
    good = (peak - level >= MIN_CONTRAST_HU) & (edge < OUTSIDE_MM[0])
    return np.where(good, edge, NAN), peak - level


def mask_surface(m: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Where the mask, read linearly, first falls below one half outward of the surface voxel."""
    start = int(np.searchsorted(s, 0.0))
    return crossing(m, s, np.full(len(m), 0.5), np.full(len(m), start - 1))


def regions(v: A.Vertebra, rows: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """Each surface point's region by its place and its normal in the vertebra's frame."""
    f = v.frame
    nl = np.stack([normal @ f.ex, normal @ f.ey, normal @ f.ez], 1)
    body = v.body[rows]
    z0, z1 = np.percentile(v.loc[v.body, 2], [2, 98])
    z = v.loc[rows, 2]
    mid = (z >= z0 + MIDDLE[0] * (z1 - z0)) & (z <= z0 + MIDDLE[1] * (z1 - z0))
    out = np.full(len(rows), "", dtype=object)
    out[body & (nl[:, 2] >= COS_REGION)] = "upper_plate"
    out[body & (nl[:, 2] <= -COS_REGION)] = "lower_plate"
    out[body & mid & (np.abs(nl[:, 0]) >= COS_REGION)] = "lateral_wall"
    out[body & mid & (nl[:, 1] >= COS_REGION)] = "anterior_wall"
    out[body & mid & (nl[:, 1] <= -COS_REGION)] = "posterior_wall"
    out[~body] = "arch"
    return out


def evenly(rows: np.ndarray, n: int) -> np.ndarray:
    return rows if len(rows) <= n else rows[np.linspace(0, len(rows) - 1, n).round().astype(int)]


def vertebra_offsets(v: A.Vertebra, hu: np.ndarray, labels: np.ndarray, outside_hu: float) -> Dict[str, Dict[str, np.ndarray]]:
    """The offsets (bone's edge less mask's surface, mm) and contrasts of the sampled surface
    points of one vertebra, by region."""
    grid = v.grid
    lo, hi = box(v.idx, labels.shape, grid.spacing)
    inside = np.zeros(tuple(hi - lo), bool)
    at_all = v.idx - lo
    inside[tuple(at_all.T)] = True
    eroded = ndimage.binary_erosion(inside, structure=ndimage.generate_binary_structure(3, 1), border_value=0)
    surf = np.flatnonzero(~eroded[tuple(at_all.T)])
    a3 = np.asarray(grid.affine, float)[:3, :3]
    normal = outward_normals(inside, at_all[surf], a3)
    keep = np.isfinite(normal).all(1)
    surf, normal = surf[keep], normal[keep]
    region = regions(v, surf, normal)
    s = samples()
    ct = crop(hu, lo, hi).astype(np.float32)
    lab = crop(labels, lo, hi)
    out: Dict[str, Dict[str, np.ndarray]] = {}
    for name in REGIONS:
        pick = evenly(np.flatnonzero(region == name), POINTS_PER_REGION)
        if not len(pick):
            continue
        at = at_all[surf[pick]].astype(float)
        steps = normal[pick] @ np.linalg.inv(a3).T
        clear_s = s[(s >= CLEAR_MM[0]) & (s <= CLEAR_MM[1])]
        clear = (along(lab, at, steps, clear_s, 0, 0) == 0).all(1)
        edge, contrast = bone_edge(along(ct, at, steps, s, 1, outside_hu), s)
        surface = mask_surface(along(inside.astype(np.float32), at, steps, s, 1, 0.0), s)
        out[name] = {"offset": np.where(clear, edge - surface, NAN), "contrast": contrast, "points": len(pick)}
    return out


def measure_arrays(hu: np.ndarray, labels: np.ndarray, grid: G.VoxelGrid, names: Dict[int, str], study: str,
                   outside_hu: float = -1000.0) -> List[Dict[str, object]]:
    """One row per vertebra and region: the points sampled, the edges read, and the offsets'
    median and quartiles with the median contrast."""
    rows: List[Dict[str, object]] = []
    for lv, v in vertebrae(labels, grid, names).items():
        for name, got in vertebra_offsets(v, hu, labels, outside_hu).items():
            off = got["offset"][np.isfinite(got["offset"])]
            q = np.percentile(off, [25, 50, 75]) if len(off) else [NAN] * 3
            ctr = got["contrast"][np.isfinite(got["offset"])]
            rows.append({"study": study, "level": lv, "region": name, "points": got["points"], "edges": len(off),
                         "offset_median": round(float(q[1]), 3), "offset_q25": round(float(q[0]), 3),
                         "offset_q75": round(float(q[2]), 3),
                         "contrast_median": round(float(np.median(ctr)), 1) if len(ctr) else NAN})
    return rows


def read_ct(path: str):
    """The CT's stored integers with the scale that makes them Hounsfield units, and its
    affine, so a 512 by 512 by 1,000 CT is held as int16 and not as float64."""
    import nibabel as nib
    img = nib.load(path)
    proxy = img.dataobj
    raw = proxy.get_unscaled() if hasattr(proxy, "get_unscaled") else np.asanyarray(proxy)
    slope = float(getattr(proxy, "slope", 1.0) or 1.0)
    inter = float(getattr(proxy, "inter", 0.0) or 0.0)
    return raw, slope, inter, np.asarray(img.affine, float)


def measure_study(ct_path: str, labels_path: str, scheme: str, study: str) -> List[Dict[str, object]]:
    labels, grid, names, problems, _ = V.read_labels(labels_path, scheme)
    raw, slope, inter, affine = read_ct(ct_path)
    if raw.shape != labels.shape or not np.allclose(affine, np.asarray(grid.affine, float), atol=1e-3):
        raise SystemExit("%s and %s are not on one grid" % (ct_path, labels_path))
    hu = raw if (slope, inter) == (1.0, 0.0) else (raw * np.float32(slope) + np.float32(inter)).astype(np.float32)
    rows = measure_arrays(hu, labels, grid, names, study)
    for p in problems:
        rows.append({"study": study, "level": "study", "region": "problem", "points": 0, "edges": 0,
                     "offset_median": NAN, "offset_q25": NAN, "offset_q75": NAN, "contrast_median": NAN, "note": p})
    return rows


def summary(rows: List[Dict[str, object]]) -> Dict[str, Dict[str, float]]:
    """Per region over every vertebra: how many, the median of their medians and its
    quartiles; then what the offsets make of a height, a disc, a width and a depth."""
    out: Dict[str, Dict[str, float]] = {}
    for name in REGIONS:
        med = np.array([float(r["offset_median"]) for r in rows if r.get("region") == name], float)
        med = med[np.isfinite(med)]
        if len(med):
            q = np.percentile(med, [25, 50, 75])
            out[name] = {"vertebrae": len(med), "median": float(q[1]), "q25": float(q[0]), "q75": float(q[2])}
    get = lambda k: out.get(k, {}).get("median", NAN)  # noqa: E731
    out["implied"] = {"height": -(get("upper_plate") + get("lower_plate")),
                      "disc": get("upper_plate") + get("lower_plate"),
                      "width": -2.0 * get("lateral_wall"),
                      "depth": -(get("anterior_wall") + get("posterior_wall"))}
    return out
