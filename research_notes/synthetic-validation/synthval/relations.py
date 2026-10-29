"""Quality indicators between the measures the papers add to Panjabi's, and the five of qi.py read
on any table's population.

qi.py's indicators ask whether a drawn vertebra could exist, from relations Panjabi's definitions
make geometrically necessary (an area inside the rectangle of its own extents, a canal narrower
than the span of its transverse processes). The papers' measures bring relations of their own,
each necessary whatever the population, stated here with its reason:

- within: an inner (endosteal) pedicle width or height is less than the outer one (Makino 2012's
  inner widths against the pedicle's width and height), since the cancellous core lies inside the
  cortex; and the medial cortex (Otsuki 2021) with the inner width inside the pedicle's width, since
  the width is the two walls and the core together;
- past: the pedicle's chord along its axis (the screw path from the entry point to the anterior
  cortex of the body) runs past the pedicle proper (Masharawi 2021, Moncada 2025) and past the
  posterior longitudinal ligament (Arockiaraj 2025), since the body lies between them and the
  anterior cortex;
- outside: the pedicles stand between the canal and the transverse processes, so the interpedicular
  distance and the two pedicles' widths together fit inside the span of the transverse processes;
- box and convex, as qi.py's: Griffith's body section on the mid-pedicle slice inside the rectangle of
  Moncada's body width and depth on the slice through the pedicles, with the end-plate's allowances
  (5 per cent over the box, since the three come from different people's means; at least half the
  box, since the body section is nearly symmetric about the sagittal axis and convex but for its
  posterior concavity, a judgement as the end-plate's is); and Shin 2024's foramen area inside the
  rectangle of his own foramen width and height, with no convex bound, since the foramen is not
  symmetric;
- sign on a ratio: a ratio of two positive extents is positive (Griffith's canal to body area).

A relation whose measures the table does not hold tests nothing and is reported as such. Where a
relation joins measures from different papers' populations, the indicator asks whether the
generator's independent draws from those pooled means and SDs make vertebrae that could exist,
which is the question the state space is read on; it does not say the papers disagree.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np

from . import qi as Q
from .population import Population

# (name, kind, keys, allowance, reason). kind "less": keys[0] < keys[1]; "sum_less": the sum of all
# but the last key, a key counted as often as it is named, < the last; "box": area, width, depth with
# the allowance over the box and whether the convex bound holds; "positive": the key is above zero.
RELATIONS: Tuple[tuple, ...] = (
    ("inner width within the pedicle", "less", ("pedicle_w_inner", "pedicle"), None,
     "the cancellous core lies inside the cortex"),
    ("inner height within the pedicle", "less", ("pedicle_h_inner", "pedicle_h"), None,
     "the cancellous core lies inside the cortex"),
    ("cortex and core within the pedicle", "sum_less", ("pedicle_cortex [medial]", "pedicle_w_inner", "pedicle"), None,
     "the width is the two walls and the core together, so the medial wall and the core are less than it"),
    ("the chord runs past the pedicle", "less", ("pedicle_length [proper]", "pedicle_chord [along the axis]"), None,
     "the screw path reaches the anterior cortex of the body, beyond the pedicle proper"),
    ("the chord runs past the ligament", "less", ("pedicle_length [to the ligament]", "pedicle_chord [along the axis]"),
     None, "the posterior longitudinal ligament lies on the body's back wall, before its anterior cortex"),
    ("the pedicles inside the transverse processes", "sum_less", ("interpedicular", "pedicle", "pedicle", "transverse_width"),
     None, "the transverse processes arise lateral to the pedicles, which stand lateral to the canal"),
    ("body section inside its box", "box", ("body_area", "body_w", "body_d [through the pedicles]"), (1.05, True),
     "a plane region lies inside the rectangle of its extents; the body section is nearly symmetric and convex"),
    ("foramen inside its box", "box", ("foramen_area", "foramen_w [body to facet]", "foramen_h"), (1.0, False),
     "a plane region lies inside the rectangle of its extents; the foramen is not symmetric, so no convex bound"),
    ("a ratio above zero", "positive", ("canal_index [areas]",), None, "a ratio of two positive areas is positive"),
)
UNIONS = {"sign or inside": ("sign", "inside"),
          "necessary": ("sign", "inside", "within", "past", "outside", "positive"),
          "any but floor": ("sign", "inside", "within", "past", "outside", "positive", "box", "convex")}
GROUP = {"less": {"inner width within the pedicle": "within", "inner height within the pedicle": "within",
                  "the chord runs past the pedicle": "past", "the chord runs past the ligament": "past"},
         "sum_less": {"cortex and core within the pedicle": "within", "the pedicles inside the transverse processes": "outside"}}


def group_of(name: str, kind: str) -> str:
    """The indicator a relation counts under: within, past, outside, box, convex or positive."""
    if kind in GROUP:
        return GROUP[kind][name]
    return kind


def _col(pop: Population, key: str):
    return pop.true[:, :, pop.keys.index(key)] if key in pop.keys else None


def relation_flags(pop: Population) -> Tuple[Dict[str, np.ndarray], Dict[str, int], List[dict]]:
    """Each relation on the true anatomy of every vertebra: (person, body) flags per indicator
    group, the vertebra-measure tests each could make, and one row per relation with its own
    rate, NaN where the table lacks a measure of it."""
    n, w, _ = pop.true.shape
    by: Dict[str, np.ndarray] = {}
    tests: Dict[str, int] = {}
    rows = []
    for name, kind, keys, allowance, why in RELATIONS:
        cols = [_col(pop, k) for k in keys]
        group = group_of(name, kind)
        by.setdefault(group, np.zeros((n, w), bool))
        tests.setdefault(group, 0)
        if any(c is None for c in cols):
            rows.append({"relation": name, "indicator": group, "measures": "; ".join(keys), "tested": 0,
                         "flagged": float("nan"), "why": why, "missing": "; ".join(k for k, c in zip(keys, cols) if c is None)})
            continue
        with np.errstate(invalid="ignore"):
            if kind == "less":
                bad = cols[0] >= cols[1]
                have = np.isfinite(cols[0]) & np.isfinite(cols[1])
            elif kind == "sum_less":
                total = sum(cols[:-1])
                bad = total >= cols[-1]
                have = np.isfinite(total) & np.isfinite(cols[-1])
            elif kind == "box":
                most, convex = allowance
                prod = cols[1] * cols[2]
                k = np.where(prod > 0, cols[0] / np.where(prod > 0, prod, 1.0), np.nan)
                bad = k > most
                have = np.isfinite(k)
                if convex:
                    under = k < Q.CONVEX_LEAST
                    by.setdefault("convex", np.zeros((n, w), bool))
                    by["convex"] |= under
                    tests["convex"] = tests.get("convex", 0) + int(have.sum())
                    rows.append({"relation": name + " (convex bound)", "indicator": "convex", "measures": "; ".join(keys),
                                 "tested": int(have.sum()), "flagged": float(under[have].mean()) if have.any() else float("nan"),
                                 "why": why, "missing": ""})
            elif kind == "positive":
                bad = cols[0] <= 0
                have = np.isfinite(cols[0])
            else:
                raise ValueError("no relation of kind %r" % kind)
        bad = bad & have
        by[group] |= bad
        tests[group] += int(have.sum())
        rows.append({"relation": name, "indicator": group, "measures": "; ".join(keys), "tested": int(have.sum()),
                     "flagged": float(bad[have].mean()) if have.any() else float("nan"), "why": why, "missing": ""})
    return by, tests, rows


def flags_all(pop: Population) -> Tuple[Q.Flags, List[dict]]:
    """qi.py's five indicators and the relations above on one population: a Flags over every
    indicator group, and the per-relation rows."""
    base = Q.flags(pop)
    by, tests, rows = relation_flags(pop)
    for k, v in by.items():
        base.by[k] = base.by[k] | v if k in base.by else v
        base.tests[k] = base.tests.get(k, 0) + tests[k]
    return base, rows


def _union(fl: Q.Flags, of: Sequence[str]) -> np.ndarray:
    present = [k for k in of if k in fl.by]
    return fl.any(present) if present else np.zeros_like(next(iter(fl.by.values())))


def vertebra_rates(fl: Q.Flags) -> Dict[str, float]:
    """The share of vertebrae flagged per indicator group and union, with `any`."""
    out = {k: float(v.mean()) for k, v in fl.by.items()}
    out.update({name: float(_union(fl, of).mean()) for name, of in UNIONS.items()})
    out["any"] = float(fl.any().mean())
    return out


def person_rates(fl: Q.Flags) -> Dict[str, float]:
    """The share of people with a vertebra flagged, per indicator group and union, with `any`."""
    out = {k: float(v.any(1).mean()) for k, v in fl.by.items()}
    out.update({name: float(_union(fl, of).any(1).mean()) for name, of in UNIONS.items()})
    out["any"] = float(fl.any().any(1).mean())
    return out
