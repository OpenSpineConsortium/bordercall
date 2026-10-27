"""One object per measurement: what it is, where it can be read, its table rows and its error.

    from schwingcheck import measures
    seven = measures.select(measures.SPINEPS_7)          # the archive's seven, in its order
    ref = measures.reference(seven)                      # {name: {level: (mean, SD)}}
    post = measures.name(X, offsets, seven)              # the rule, read from the objects alone

A measure here is one quantity of one vertebra, with the side it is read on when the papers
print a right and a left: `pedicle_w` on the right, on the left, or as the mean of the two
(the archive's `pedicle`), never the right and the left as two independent measures (TODO.md,
item P step 4), which `select` refuses, as it refuses one measure named twice. The registry
holds every measure of the long table (TODO.md, item 2): its kind, the planes that can read it,
its definition and the papers' mnemonic for it; its table rows, the mean, the population SD,
the number of specimens and the provenance cell of every level; its own measurement error in
millimetres (1.0 for every length today, the archive's noise_mm; an angle's or an area's is set
when step e gives those kinds their own likelihood terms); the code that measures it, where
there is any; and its correlations with the other measures, empty until a CT table estimates
them. `name` scores fields from the selected objects and nothing else: the table from their
rows, the error of each from its own `error_mm`.

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
# The archive's three regimes as its record used them (archive/bordercall/neighbour.py), which
# rescore reproduces. Its AP regime keeps the posterior body height, taking a body's height as
# one either plane shows, though the measure's planes here are the mask and the lateral view
# (mnemonics.py), since an AP view lays the posterior wall over the anterior; the regimes are the
# record's selections and not what the planes field of each measure would select.
REGIMES = {"lateral": ["h_post", "endplate_depth", "endplate_lower_depth", "canal_ap"],
           "ap": ["h_post", "endplate", "endplate_lower", "canal_w"],
           "both": list(SPINEPS_7)}
ARCHIVE_NAMES = {"pedicle": ("pedicle_w", "mean"), "pedicle_h": ("pedicle_h", "mean")}


# The archive's measurer on a SPINEPS mask reads the seven (archive/bordercall/SPINEPS_MAPPING.md)
# and refuses the pedicle, which the mask does not label. It also takes extents for the transverse
# processes and the spinous process, which are not registered here: its spinous length starts at
# the body's centroid where Panjabi's SPL starts at the canal's posterior wall, and neither
# definition has been checked against the papers'.
SPINEPS_MAP = "archive/bordercall/spineps_map.py"
MEASURERS = {key: (SPINEPS_MAP,) for key in SPINEPS_7}


@dataclass(frozen=True)
class Row:
    """One level of a measure's table: the mean and the population SD the rule uses, the number
    of specimens, and the provenance cells the means were read from (the right's and the left's
    for the mean of a pair)."""
    level: str
    mean: float
    sd: float
    n: int
    cells: Tuple[str, ...]


@dataclass(frozen=True)
class Measure:
    name: str                       # the measure's name in the long table
    side: str                       # whole, right, left or mean (of right and left)
    kind: str
    planes: Tuple[str, ...]
    definition: str
    error_mm: Optional[float]       # its own measurement error; None until its kind has a term
    levels: Tuple[str, ...]         # the levels its table rows cover
    mnemonics: Tuple[str, ...] = ()                     # the papers' own, the right's and the left's for a pair's mean
    rows: Tuple[Row, ...] = ()                          # the table, one row per level in `levels`
    measurers: Tuple[str, ...] = ()                     # the code that reads it from a patient, where any does
    correlations: Tuple[Tuple[str, float], ...] = ()    # with other measures' keys, none until a CT table

    @property
    def key(self) -> str:
        return T.selection_name(self.name, self.side)

    @property
    def selection(self) -> Tuple[str, str]:
        return (self.name, self.side)

    def row(self, level: str) -> Row:
        for r in self.rows:
            if r.level == level:
                return r
        raise ValueError("%s has no table row at %s" % (self.key, level))


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


def _rows(ds, name: str, side: str, levels: Sequence[str]) -> Tuple[Row, ...]:
    """The table rows at the levels given, from the Dataset, the mean of a pair as table.reference
    takes it (the mean of the means and of the standard errors, the latter times sqrt(n)), so the
    numbers are table.reference's to the bit."""
    at = [LEVELS_C2.index(lv) for lv in levels]
    col = lambda var, sd: ds[var].sel(measure=name, side=sd).values[at]
    if side == "mean":
        mean = (col("mean", "right") + col("mean", "left")) / 2.0
        n = col("n", "right")
        spread = (col("sem", "right") + col("sem", "left")) / 2.0 * np.sqrt(n)
        cells = list(zip(col("cell", "right"), col("cell", "left")))
    else:
        mean, spread, n = col("mean", side), col("sd", side), col("n", side)
        cells = [(c,) for c in col("cell", side)]
    return tuple(Row(level=lv, mean=float(mean[i]), sd=float(spread[i]), n=int(n[i]), cells=tuple(str(c) for c in cells[i]))
                 for i, lv in enumerate(levels))


def _mnemonics(ds, name: str, side: str) -> Tuple[str, ...]:
    sides = ("right", "left") if side == "mean" else (side,)
    return tuple(str(ds["mnemonic"].sel(measure=name, side=sd).item()) for sd in sides)


_REGISTRY = None


def registry(ds=None) -> Dict[str, Measure]:
    """Every measure of the long table on every side it is printed, and the mean of a pair; the
    committed table's is built once per process."""
    global _REGISTRY
    if ds is None:
        if _REGISTRY is None:
            _REGISTRY = _build_registry(dataset())
        return dict(_REGISTRY)
    return _build_registry(ds)


def _build_registry(ds) -> Dict[str, Measure]:
    out: Dict[str, Measure] = {}
    for name in MEASURES:
        if name not in ds["measure"].values:
            continue
        info = MEASURE_INFO[name]
        sides = [s for s in SIDES if ds["mean"].sel(measure=name, side=s).notnull().any()]
        if "right" in sides and "left" in sides:
            sides.append("mean")
        for side in sides:
            levels = _levels_with(ds, name, side)
            key = T.selection_name(name, side)
            m = Measure(name=name, side=side, kind=info.kind, planes=tuple(info.planes), definition=info.definition,
                        error_mm=ERROR_MM.get(info.kind), levels=levels, mnemonics=_mnemonics(ds, name, side),
                        rows=_rows(ds, name, side, levels), measurers=MEASURERS.get(_archive_name(name, side), ()))
            out[m.key] = m
    return out


def _archive_name(name: str, side: str) -> str:
    for old, sel in ARCHIVE_NAMES.items():
        if sel == (name, side):
            return old
    return T.selection_name(name, side)


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
    and table rows at every level the rule runs over, and none of them named twice, on one side
    or on two: the right and the left of a pair are one measurement of one vertebra, and the rule
    multiplies its measures as independent, so a pair enters as one side or as its mean."""
    reg = registry() if reg is None else reg
    out = []
    taken: Dict[str, str] = {}
    for key in keys:
        name, side = resolve(key)
        k = T.selection_name(name, side)
        if k not in reg:
            raise KeyError("no measure %r is registered; the registry has %s" % (key, ", ".join(sorted(reg))))
        if name in taken:
            raise ValueError("%s is selected twice (%s and %s): a measure enters the rule once, a pair as one side or "
                             "as the mean of the two, never as independent measures" % (name, taken[name], key))
        taken[name] = key
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


def reference(measures: Sequence[Measure], levels: Sequence[str] = LEVELS) -> Dict[str, Dict[str, tuple]]:
    """{key: {level: (mean, population SD)}} in the archive's shape, read from the measures' own
    rows, keyed as the archive keys its seven measures (endplate ... canal_ap) and the mean of a
    pair as `name` without a side where the archive has one (pedicle, pedicle_h), else
    `name:side`."""
    return {archive_key(m): {lv: (m.row(lv).mean, m.row(lv).sd) for lv in levels} for m in measures}


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


def arrays(measures: Sequence[Measure], levels: Sequence[str] = LEVELS) -> Tuple[np.ndarray, np.ndarray]:
    """The means and population SDs as (measures, levels) arrays, in the order given."""
    ref = reference(measures, levels)
    return T.arrays(ref, [archive_key(m) for m in measures], levels)


def errors(measures: Sequence[Measure]) -> np.ndarray:
    """Each measure's own measurement error in millimetres, the rule's noise, in the order given."""
    return np.array([m.error_mm for m in measures], float)


def name(X: np.ndarray, offsets: Sequence[int], measures: Sequence[Measure], synth: Optional[dict] = None,
         levels: Sequence[str] = LEVELS, **kwargs) -> Dict[str, np.ndarray]:
    """rule.name on the measures given and nothing else: the table from their rows, each one's
    error from its own error_mm; X is (fields, measures, bodies) in their order."""
    from . import rule as R
    mu, sd = arrays(measures, levels)
    return R.name(X, offsets, mu, sd, R.SYNTH if synth is None else synth, noise=errors(measures), **kwargs)
