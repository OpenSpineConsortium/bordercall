"""Quality indicators of synthetic vertebrae, and the curation they make.

The generator draws every measure of a person apart from every other but for the size and, in the
correlated arm, an exchangeable offset (columns.py). Each indicator below asks whether a drawn
vertebra could exist: whether its values hold the relations that the papers' definitions make
geometrically necessary, whatever the population. None is fitted to data; each states its
assumption; run.py's quality record counts each per setting, and box_rates per measure and level.

- sign: a length or an area at or below zero, in the true anatomy;
- floor: a measured length or area held at the generator's floor of 0.5 (columns.FLOOR);
- box: an area larger than the rectangle its own width and depth bound. Panjabi's widths and
  depths are a section's largest extents in two perpendicular directions (mnemonics.py), and a
  plane region lies inside the rectangle of its extents, so area / (width x depth) is at most 1.
  The end-plate and the facets are curved surfaces, a little larger than their projection, so
  the end-plate is allowed 5 per cent over and a facet 15 per cent; the canal is a plane section;
- convex: an end-plate whose area is under half its width times its depth. A convex region that
  is symmetric about its sagittal axis holds the rhombus of its four extreme points, w d / 2; a
  convex region without that symmetry need not (a thin sliver along a diagonal of its box has
  extents w and d and almost no area). The end-plate is nearly symmetric and convex but for a
  shallow posterior notch, so the bound is a judgement for it, as box's allowances are; the canal
  is not convex (a lumbar canal can be trefoil), so only the end-plate is held to it;
- inside: a canal wider than the span of its own transverse processes, which cannot be, since the
  canal lies between the pedicles and the processes outside them.

The pedicle's area is left out of box and convex: Panjabi reads its width and its height each at
its own narrowest place, which need not be one section, so the area of the narrowest section can
pass their product.

Three unions are read beside each indicator: "sign or inside", which no anatomy can fail; "any
but floor", which adds the two bounds that hold only under their allowances and assumptions; and
"any", which adds floor, the generator's clip of a measured value rather than an anatomy.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np

from .population import FLOOR, Population

# (area, width, depth, the largest area / (width x depth) allowed, whether the convex bound holds)
BOX = (
    ("endplate_area", "endplate", "endplate_depth", 1.05, True),
    ("endplate_lower_area", "endplate_lower", "endplate_lower_depth", 1.05, True),
    ("canal_area", "canal_w", "canal_ap", 1.0, False),
    ("facet_area_sup:mean", "facet_w_sup:mean", "facet_h_sup:mean", 1.15, False),
    ("facet_area_inf:mean", "facet_w_inf:mean", "facet_h_inf:mean", 1.15, False),
)
INSIDE = (("canal_w", "transverse_width"),)
CONVEX_LEAST = 0.5
INDICATORS = ("sign", "floor", "box", "convex", "inside")
UNIONS = {"sign or inside": ("sign", "inside"), "any but floor": ("sign", "box", "convex", "inside")}


@dataclass
class Flags:
    """Boolean (person, body) arrays, one per indicator and source, and the count of tests made."""
    by: Dict[str, np.ndarray]
    tests: Dict[str, int]

    def any(self, of: Sequence[str] = ()) -> np.ndarray:
        """The union of the indicators named, or of all of them."""
        out = None
        for k, v in self.by.items():
            if not of or k in of:
                out = v.copy() if out is None else out | v
        return out


def _ix(pop: Population, key: str):
    return pop.keys.index(key) if key in pop.keys else None


def flags(pop: Population) -> Flags:
    """Every indicator on every vertebra of every person: sign and box on the true anatomy, floor
    on the measured values. A (person, body) is flagged by an indicator when any of its measures
    fails it; the tests count the vertebra-measure pairs each indicator could look at."""
    n, w, _ = pop.true.shape
    scaled = pop.power > 0
    by: Dict[str, np.ndarray] = {}
    tests: Dict[str, int] = {}
    by["sign"] = (pop.true[:, :, scaled] <= 0).any(2)
    tests["sign"] = int(n * w * scaled.sum())
    by["floor"] = pop.floored().any(2)
    tests["floor"] = tests["sign"]
    box = np.zeros((n, w), bool)
    convex = np.zeros((n, w), bool)
    nb = nc = 0
    for area, width, depth, most, holds_convex in BOX:
        ia, iw, idp = _ix(pop, area), _ix(pop, width), _ix(pop, depth)
        if None in (ia, iw, idp):
            continue
        k = shape_factor(pop.true, ia, iw, idp)
        box |= k > most
        nb += n * w
        if holds_convex:
            convex |= k < CONVEX_LEAST
            nc += n * w
    by["box"], tests["box"] = box, nb
    by["convex"], tests["convex"] = convex, nc
    inside = np.zeros((n, w), bool)
    ni = 0
    for inner, outer in INSIDE:
        ii, io = _ix(pop, inner), _ix(pop, outer)
        if None in (ii, io):
            continue
        inside |= pop.true[:, :, ii] >= pop.true[:, :, io]
        ni += n * w
    by["inside"], tests["inside"] = inside, ni
    return Flags(by=by, tests=tests)


def shape_factor(x: np.ndarray, ia: int, iw: int, idp: int) -> np.ndarray:
    """area / (width x depth), NaN where the product is not positive."""
    prod = x[:, :, iw] * x[:, :, idp]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(prod > 0, x[:, :, ia] / prod, np.nan)


def box_rates(pop: Population) -> Dict[str, Dict[str, np.ndarray]]:
    """Per area measure and level: the share of vertebrae over the box, under the convex bound,
    and the shape factor's mean and SD, on the true anatomy."""
    out = {}
    for area, width, depth, most, holds_convex in BOX:
        ia, iw, idp = _ix(pop, area), _ix(pop, width), _ix(pop, depth)
        if None in (ia, iw, idp):
            continue
        k = shape_factor(pop.true, ia, iw, idp)
        out[area] = {"over_box": np.nanmean(k > most, 0), "under_convex": np.nanmean(k < CONVEX_LEAST, 0) if holds_convex else None,
                     "k_mean": np.nanmean(k, 0), "k_sd": np.nanstd(k, 0), "limit": most, "convex": holds_convex}
    return out


def person_rates(fl: Flags) -> Dict[str, float]:
    """The share of people with at least one vertebra flagged, per indicator and for any."""
    out = {k: float(v.any(1).mean()) for k, v in fl.by.items()}
    out.update({name: float(fl.any(of).any(1).mean()) for name, of in UNIONS.items()})
    out["any"] = float(fl.any().any(1).mean())
    return out


def vertebra_rates(fl: Flags) -> Dict[str, float]:
    """The share of vertebrae flagged, per indicator and for any."""
    out = {k: float(v.mean()) for k, v in fl.by.items()}
    out.update({name: float(fl.any(of).mean()) for name, of in UNIONS.items()})
    out["any"] = float(fl.any().mean())
    return out


def curate(pop: Population, drop: Sequence[str] = ("sign", "inside")) -> Tuple[np.ndarray, Dict[str, int]]:
    """The people kept: those with no vertebra failing an indicator in `drop`. By default only the
    indicators no anatomy can fail are dropped on; box and convex fail so often under the
    generator's independent draws that dropping on them would keep almost nobody (the README's quality table), and
    their rates are reported instead."""
    fl = flags(pop)
    bad = np.zeros(pop.true.shape[0], bool)
    counts = {}
    for k in drop:
        hit = fl.by[k].any(1)
        counts[k] = int(hit.sum())
        bad |= hit
    counts["dropped"] = int(bad.sum())
    counts["kept"] = int((~bad).sum())
    return ~bad, counts
