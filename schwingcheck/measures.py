"""One object per measurement: what it is, where it can be read, its table rows and its error.

    from schwingcheck import measures
    seven = measures.select(measures.SPINEPS_7)          # the archive's seven, in its order
    ref = measures.reference(seven)                      # {name: {level: (mean, SD)}}

A measure here is one quantity of one vertebra, with the side it is read on when the papers
print a right and a left: `pedicle_w` on the right, on the left, or as the mean of the two
(the archive's `pedicle`), never the right and the left as two independent measures (TODO.md,
item P step 4). The registry holds every measure of the long table, with its kind, the planes
that can read it, its definition, its own measurement error in millimetres (1.0 for every
length today, the archive's noise_mm; an angle's or an area's is set when step e gives those
kinds their own likelihood terms) and the levels its table rows cover.

The rule of step c takes lengths only, as the archive does; `select` refuses an area or an
angle with a message that names step e, so nothing is scored under a wrong term by accident.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import LEVELS, LEVELS_C2, SIDES
from .mnemonics import MEASURE_INFO, MEASURES
from . import table as T

ERROR_MM = {"length": 1.0}              # the archive's noise_mm for every length; the other kinds wait for step e
SPINEPS_7 = ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post", "canal_w", "canal_ap"]
REGIMES = {"lateral": ["h_post", "endplate_depth", "endplate_lower_depth", "canal_ap"],
           "ap": ["h_post", "endplate", "endplate_lower", "canal_w"],
           "both": list(SPINEPS_7)}
ARCHIVE_NAMES = {"pedicle": ("pedicle_w", "mean"), "pedicle_h": ("pedicle_h", "mean")}


@dataclass(frozen=True)
class Measure:
    name: str                       # the measure's name in the long table
    side: str                       # whole, right, left or mean (of right and left)
    kind: str
    planes: Tuple[str, ...]
    definition: str
    error_mm: Optional[float]       # its own measurement error; None until its kind has a term
    levels: Tuple[str, ...]         # the levels its table rows cover

    @property
    def key(self) -> str:
        return T.selection_name(self.name, self.side)

    @property
    def selection(self) -> Tuple[str, str]:
        return (self.name, self.side)


_DS = None


def dataset():
    global _DS
    if _DS is None:
        _DS = T.load()
    return _DS


def _levels_with(ds, name: str, side: str) -> Tuple[str, ...]:
    if side == "mean":
        ok = ds["mean"].sel(measure=name, side="right").notnull() & ds["mean"].sel(measure=name, side="left").notnull() \
            & ds["sem"].sel(measure=name, side="right").notnull() & ds["sem"].sel(measure=name, side="left").notnull()
    else:
        ok = ds["mean"].sel(measure=name, side=side).notnull() & ds["sd"].sel(measure=name, side=side).notnull()
    return tuple(lv for lv, o in zip(LEVELS_C2, ok.values) if o)


def registry(ds=None) -> Dict[str, Measure]:
    """Every measure of the long table on every side it is printed, and the mean of a pair."""
    ds = dataset() if ds is None else ds
    out: Dict[str, Measure] = {}
    for name in MEASURES:
        if name not in ds["measure"].values:
            continue
        info = MEASURE_INFO[name]
        sides = [s for s in SIDES if ds["mean"].sel(measure=name, side=s).notnull().any()]
        if "right" in sides and "left" in sides:
            sides.append("mean")
        for side in sides:
            m = Measure(name=name, side=side, kind=info.kind, planes=tuple(info.planes), definition=info.definition,
                        error_mm=ERROR_MM.get(info.kind), levels=_levels_with(ds, name, side))
            out[m.key] = m
    return out


def resolve(key: str) -> Tuple[str, str]:
    """A key as the archive or the table spells it: `pedicle` is the mean of the pedicle widths,
    `pedicle_w:right` the right one, `endplate` the whole measure."""
    if key in ARCHIVE_NAMES:
        return ARCHIVE_NAMES[key]
    if ":" in key:
        name, side = key.split(":", 1)
        return name, side
    return key, "whole"


def select(keys: Sequence[str], levels: Sequence[str] = LEVELS, reg: Optional[Dict[str, Measure]] = None) -> List[Measure]:
    """The measures named, each checked: registered, a length (until step e), with its own error
    and table rows at every level the rule runs over."""
    reg = registry() if reg is None else reg
    out = []
    for key in keys:
        name, side = resolve(key)
        k = T.selection_name(name, side)
        if k not in reg:
            raise KeyError("no measure %r is registered; the registry has %s" % (key, ", ".join(sorted(reg))))
        m = reg[k]
        if m.kind != "length":
            raise ValueError("%s is an %s: the rule of step c takes lengths only; step e gives %ss their term" % (k, m.kind, m.kind))
        if m.error_mm is None or not m.error_mm > 0:
            raise ValueError("%s has no measurement error of its own" % k)
        missing = [lv for lv in levels if lv not in m.levels]
        if missing:
            raise ValueError("%s has no table row at %s" % (k, ", ".join(missing)))
        out.append(m)
    return out


def reference(measures: Sequence[Measure], levels: Sequence[str] = LEVELS, ds=None) -> Dict[str, Dict[str, tuple]]:
    """{key: {level: (mean, population SD)}} in the archive's shape, keyed as the archive keys
    its seven measures (endplate ... canal_ap) and the mean of a pair as `name` without a side
    where the archive has one (pedicle, pedicle_h), else `name:side`."""
    ds = dataset() if ds is None else ds
    ref = T.reference(ds, [m.selection for m in measures], levels)
    return {archive_key(m): ref[m.key] for m in measures}


ARCHIVE_CSV = os.path.join(T.ROOT, "archive", "bordercall", "reference", "panjabi_full_spine.csv")


def archive_reference(keys: Sequence[str], levels: Sequence[str] = LEVELS, path: str = ARCHIVE_CSV) -> Dict[str, Dict[str, tuple]]:
    """The archive's table as its loader reads it: {name: {level: (mean, sem * sqrt(n))}}. Kept
    so a test can hold the checked table to it value for value."""
    import csv
    import math
    out: Dict[str, Dict[str, tuple]] = {k: {} for k in keys}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(line for line in fh if not line.startswith("#")):
            m = r["measure"].strip()
            if m in out:
                n = float(r.get("n") or 12)
                out[m][r["level"].strip()] = (float(r["mean"]), float(r["sem"]) * math.sqrt(n))
    for k in keys:
        missing = [lv for lv in levels if lv not in out[k]]
        if missing:
            raise ValueError("the archive's table lacks %s at %s" % (k, ", ".join(missing)))
        out[k] = {lv: out[k][lv] for lv in levels}
    return out


def archive_key(m: Measure) -> str:
    for old, (name, side) in ARCHIVE_NAMES.items():
        if (name, side) == m.selection:
            return old
    return m.key


def arrays(measures: Sequence[Measure], levels: Sequence[str] = LEVELS, ds=None) -> Tuple[np.ndarray, np.ndarray]:
    """The means and population SDs as (measures, levels) arrays, in the order given."""
    ref = reference(measures, levels, ds)
    return T.arrays(ref, [archive_key(m) for m in measures], levels)


def errors(measures: Sequence[Measure]) -> np.ndarray:
    return np.array([m.error_mm for m in measures], float)
