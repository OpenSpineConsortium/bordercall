"""The spinal canal read on the CT itself, not on the label's hole.

The label's canal is the hole the arch closes round in a slab, and on whole-vertebra masks the
ring closes in one to three slabs in the neck and at L5, where the pedicles stand higher or lower
than the laminae's overlap, so the canal's width falls back to the hole's width through its
middle; and a label boundary set at the voxel's majority narrows the hole by up to a voxel each
side. On 89 gold tier CTs the hole read the neck's canal 19 to 21 mm wide where Panjabi's SCW is
23 to 26, at every label source and every slice thickness alike.

On the CT the canal is what it is on a radiologist's screen: soft tissue (cord, fluid, fat) inside
a ring of bone. In each plane across the vertebra's frame from the body's bottom to its top, every
STEP_MM, the CT is sampled (trilinear) on a window behind the body; the canal is the connected
region below BONE_HU holding a seed SEED_MM behind the body's posterior wall at the midline, the
flood fill of Radnostics' canal finder (US 8,891,848) and of Yao 2006, with 200 HU, the floor the
published heuristic pipelines give dense bone (bordercall research_notes/Vertebra measures without
masks/ct_intensity_methods.md). A plane counts only where that region is enclosed (it touches no
side of the window, so no foramen or interlaminar gap opens it) and its area is a canal's: there
the arch is whole, as at Panjabi's pedicle level. The width is the plane's widest row through the
seed's column (Panjabi's SCW, the canal's greatest width between the pedicles' medial walls), the
depth the run along that column (SCD, front to back at the midline); each is the median over the
enclosed planes. On those 89 CTs the width read within about a millimetre of Panjabi's at 14 of 17
levels from C3 to L5; the neck's depth reads 2 to 4 mm under his, as CT series of the neck do.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

import numpy as np
from scipy import ndimage

from .anatomy import Vertebra

NAN = float("nan")
STEP_MM = 0.25              # the sampling step in each plane
PLANE_MM = 0.5              # the planes' spacing along the vertebra's axis
BONE_HU = 200.0             # bone at or above this
SEED_MM = 5.0               # the seed this far behind the body's posterior wall, at the midline
HALF_WIDTH_MM = 22.0        # the window's half width across
BEHIND_MM, AHEAD_MM = 32.0, 4.0   # the window from this far behind the wall to this far in front of it
AREA_MM2 = (40.0, 700.0)


def load(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """The CT's values as float32 and the inverse of its affine (world to index)."""
    import nibabel as nib
    img = nib.load(path)
    return np.asarray(img.dataobj, dtype=np.float32), np.linalg.inv(img.affine)


def plane(ct: np.ndarray, inv: np.ndarray, v: Vertebra, z: float, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    """The CT on the grid xs by ys of the frame's plane at height z, trilinear, the edge value past the volume."""
    f = v.frame
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    world = f.origin + X[..., None] * f.ex + Y[..., None] * f.ey + z * f.ez
    ijk = world.reshape(-1, 3) @ inv[:3, :3].T + inv[:3, 3]
    return ndimage.map_coordinates(ct, ijk.T, order=1, mode="nearest").reshape(X.shape)


def canal_in_plane(img: np.ndarray, seed: Tuple[int, int]) -> Optional[Tuple[float, float]]:
    """(width, depth) of the enclosed canal holding the seed, or None where the plane shows none."""
    soft = img < BONE_HU
    if not soft[seed]:
        return None
    lab, _ = ndimage.label(soft)
    reg = lab == lab[seed]
    if reg[0, :].any() or reg[-1, :].any() or reg[:, 0].any() or reg[:, -1].any():
        return None
    area = float(reg.sum()) * STEP_MM * STEP_MM
    if not (AREA_MM2[0] <= area <= AREA_MM2[1]):
        return None
    c = seed[0]
    widest = 0.0
    for j in np.flatnonzero(reg[c, :]):
        row = reg[:, j]
        lo = hi = c
        while lo - 1 >= 0 and row[lo - 1]:
            lo -= 1
        while hi + 1 < len(row) and row[hi + 1]:
            hi += 1
        widest = max(widest, (hi - lo + 1) * STEP_MM)
    return widest, float(reg[c, :].sum()) * STEP_MM


def measures(v: Vertebra, ct: Optional[Tuple[np.ndarray, np.ndarray]]) -> Tuple[Dict[str, float], Dict[str, str]]:
    """canal_w_ct and canal_ap_ct, the medians over the planes where the canal is enclosed."""
    out = {"canal_w_ct": NAN, "canal_ap_ct": NAN}
    if ct is None:
        return out, {}
    B = v.body_pts
    if not len(B) or not np.isfinite(v.midline) or not np.isfinite(v.wall):
        return out, {"canal_ct": "no body or no canal wall to seed the canal from"}
    values, inv = ct
    xs = np.arange(v.midline - HALF_WIDTH_MM, v.midline + HALF_WIDTH_MM + 1e-9, STEP_MM)
    ys = np.arange(v.wall - BEHIND_MM, v.wall + AHEAD_MM + 1e-9, STEP_MM)
    seed = (int(round((v.midline - xs[0]) / STEP_MM)), int(round((v.wall - SEED_MM - ys[0]) / STEP_MM)))
    found = []
    for z in np.arange(float(B[:, 2].min()), float(B[:, 2].max()) + 1e-6, PLANE_MM):
        got = canal_in_plane(plane(values, inv, v, z, xs, ys), seed)
        if got is not None:
            found.append(got)
    if not found:
        return out, {"canal_ct": "no plane through the body shows the canal enclosed by bone on the CT"}
    out["canal_w_ct"] = float(np.median([w for w, _ in found]))
    out["canal_ap_ct"] = float(np.median([d for _, d in found]))
    return out, {}
