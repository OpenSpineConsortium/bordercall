"""What a published table of means cannot test: correlations, ratios and how measures scale.

Three checks of the generator's structure against what the 39 papers print beside their means.

- Correlations of a person's measures. The only ones printed are Griffith's (griffith2016 Table 1,
  p. 674; the reread's note, research_notes/clinical-reread/notes/griffith2016.md L170-175 on the
  reread's branch): Pearson correlations of each subject's L1-L5 means, men and women apart, over
  540 of each, read on CT. The generator has no sex; its size spread stands for both sexes and
  every stature, so its correlations should sit at or above the within-sex ones. They are read on
  the measured values, since Griffith's carry a CT's error too. Griffith's vertebral body area is
  the body's section at mid-pedicle; the generator has no such measure, so each of its two
  end-plate areas, the nearest sections it draws, stands in on its own and the two correlations
  are averaged (their mean would average two errors away and read higher than one section).
- Ratios with published normal values (the reread's synthesis draft, measures.md, as the reader's
  report on it gives them): each set beside the synthetic population's mean of per-vertebra ratios
  and the ratio of Panjabi's means, by level. A ratio of two Panjabi measures shows where his
  definitions or his twelve spines part from another series in shape, not size.
- Isometry. The generator scales every length by one size s and every area by s^2, so the sexes,
  which differ mainly in size, should differ by the same log ratio in every length and twice it
  in every area. log(male / female) is read from every series that prints both sexes of one
  cohort, measure and level, of any definition, since a ratio within a paper does not depend on
  it, and pooled per measure by its median, with the papers behind each measure and the count of
  pairs whose two means are printed equal (a paper that rounds to whole millimetres gives many).
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence

import numpy as np

from . import literature as L
from .population import Population

LUMBAR = ("L1", "L2", "L3", "L4", "L5")

# griffith2016 Table 1, p. 674: r of each subject's L1-L5 means (men, women), n = 540 each.
GRIFFITH = (
    ("canal_area", "body_area", 0.293, 0.250),
    ("canal_w", "body_area", 0.439, 0.372),
    ("canal_ap", "body_area", 0.287, 0.196),
    ("canal_ap", "canal_w", 0.610, 0.553),
)
GRIFFITH_N = 540
BODY_AREA = ("endplate_area", "endplate_lower_area")

# (name, numerator, denominator or None for area / (w x d), the published values by level, source)
RATIOS = (
    ("canal depth / body depth", "canal_ap", "endplate_depth",
     {"alonge2021": dict(zip(LUMBAR, (0.70, 0.64, 0.58, 0.58, 0.58))),
      "amonookuofi1985 (low end)": dict(zip(LUMBAR, (0.57, 0.52, 0.45, 0.45, 0.45))),
      "amonookuofi1985 (high end)": dict(zip(LUMBAR, (0.61, 0.55, 0.50, 0.50, 0.50)))},
     "alonge2021 p. 73 (CT, 120 Nigerian adults; body depth at mid-body); amonookuofi1985 Table 4 (122 skeletons)"),
    ("canal width / canal depth", "canal_w", "canal_ap",
     {"cizmic2023": dict(zip(LUMBAR, (1.30, 1.39, 1.55, 1.63, 1.79)))},
     "cizmic2023 (CT, 200 adults of Bosnia and Herzegovina); measures.md L695 on the reread's branch"),
    ("transverse width / end-plate width", "transverse_width", "endplate",
     {"tan2004 (low end)": dict(zip(LUMBAR, (1.48,) * 5)), "tan2004 (high end)": dict(zip(LUMBAR, (1.79,) * 5))},
     "tan2004 (10 Singaporean cadavers), as measures.md L1498 gives its range over L1-L5"),
    ("canal area / (width x depth)", "canal_area", None,
     {"tan2004 (low end)": dict(zip(LUMBAR, (0.70,) * 5)), "tan2004 (high end)": dict(zip(LUMBAR, (0.90,) * 5))},
     "tan2004, as measures.md L717 gives its range"),
)


def _col(pop: Population, key: str, which: str = "true") -> np.ndarray:
    """(people, levels) of one measure, true or measured."""
    return getattr(pop, which)[:, :, pop.keys.index(key)]


def _subject_r(pop: Population, a: str, b: str, which: str) -> float:
    """r of the subject means over L1-L5 of two measures, the body area read as each end-plate
    area in turn and the two r averaged."""
    lumbar = [pop.level_index(l) for l in LUMBAR]
    xs = BODY_AREA if a == "body_area" else (a,)
    ys = BODY_AREA if b == "body_area" else (b,)
    rs = [np.corrcoef(_col(pop, x, which)[:, lumbar].mean(1), _col(pop, y, which)[:, lumbar].mean(1))[0, 1]
          for x in xs for y in ys]
    return float(np.mean(rs))


def subject_mean_correlations(pop: Population, which: str = "measured") -> List[dict]:
    """Griffith's four correlations of subject means over L1-L5, on the synthetic people."""
    out = []
    for a, b, men, women in GRIFFITH:
        out.append({"pair": "%s with %s" % (a, b), "synthetic": _subject_r(pop, a, b, which), "griffith_men": men,
                    "griffith_women": women, "griffith_ci_men": fisher_ci(men, GRIFFITH_N),
                    "griffith_ci_women": fisher_ci(women, GRIFFITH_N)})
    return out


def fisher_ci(r: float, n: int, z: float = 1.959964) -> tuple:
    h = z / math.sqrt(n - 3)
    return math.tanh(math.atanh(r) - h), math.tanh(math.atanh(r) + h)


def ratio_table(pop: Population, mu: np.ndarray, keys: Sequence[str], levels: Sequence[str]) -> List[dict]:
    """Each published ratio beside the synthetic mean of per-vertebra ratios and Panjabi's ratio of
    means, by lumbar level. mu is the generator's table (measures, levels) in `keys` order."""
    out = []
    for name, num, den, published, source in RATIOS:
        for level in LUMBAR:
            i = pop.level_index(level)
            n = _col(pop, num)[:, i]
            if den is None:
                w, d = _col(pop, "canal_w")[:, i], _col(pop, "canal_ap")[:, i]
                syn = n / (w * d)
                pj = mu[keys.index(num), levels.index(level)] / (mu[keys.index("canal_w"), levels.index(level)]
                                                                  * mu[keys.index("canal_ap"), levels.index(level)])
            else:
                syn = n / _col(pop, den)[:, i]
                pj = mu[keys.index(num), levels.index(level)] / mu[keys.index(den), levels.index(level)]
            row = {"ratio": name, "level": level, "synthetic_mean": float(np.mean(syn)), "synthetic_sd": float(np.std(syn)),
                   "panjabi_ratio_of_means": float(pj), "source": source}
            for paper, values in published.items():
                row[paper] = values.get(level, float("nan"))
            out.append(row)
    return out


ALL_DEFINITIONS = ("same", "close", "differs", "none")
MIN_PER_SEX = 10        # a sex printed from fewer people says little of its mean (Mitra's two women)


def sex_log_ratios(rows: Sequence[dict]) -> Dict[str, List[tuple]]:
    """log(male mean / female mean) for every cohort, technique, group, measure and level that
    prints both sexes, of the paper's own rows of human adults (literature.excluded_why), of any
    definition: a ratio within one paper's definition is the same whichever it is."""
    pairs: Dict[tuple, Dict[str, float]] = {}
    for r in rows:
        if r["sex"] not in ("male", "female") or L.excluded_why(r, ALL_DEFINITIONS):
            continue
        if r["side"] in L.ONE_SIDE:
            continue
        if math.isfinite(r["n"]) and r["n"] < MIN_PER_SEX:
            continue
        cell = (r["paper"], r["cohort"], r["technique"], r["group"], r["key"], r["level"])
        pairs.setdefault(cell, {})[r["sex"]] = r["mean"]
    out: Dict[str, List[tuple]] = {}
    for (paper, _, _, _, key, level), m in sorted(pairs.items()):
        if "male" in m and "female" in m and m["male"] > 0 and m["female"] > 0:
            out.setdefault(key, []).append((paper, math.log(m["male"] / m["female"])))
    return out


def isometry_table(rows: Sequence[dict], powers: Dict[str, float], anchor: Sequence[str] = ("endplate", "endplate_depth", "h_post")) -> List[dict]:
    """Per measure: the cells with both sexes, the papers behind them (with their counts), how many
    print the two sexes' means equal, the median log(M/F) and its quartiles, and the loading on
    size it implies, the median over the median of the body's lengths (`anchor`), against the
    generator's loading, its power (1 a length, 2 an area, 0 an angle)."""
    lr = sex_log_ratios(rows)

    def papers(pairs):
        count: Dict[str, int] = {}
        for p, _ in pairs:
            count[p] = count.get(p, 0) + 1
        return "; ".join("%s %d" % kv for kv in sorted(count.items(), key=lambda kv: (-kv[1], kv[0])))
    body_pairs = [x for k in anchor for x in lr.get(k, [])]
    unit = float(np.median([v for _, v in body_pairs])) if body_pairs else float("nan")
    out = []
    for key in sorted(lr):
        v = np.array([x for _, x in lr[key]])
        out.append({"measure": key, "cells": len(v), "papers": papers(lr[key]), "equal_means": int((v == 0).sum()),
                    "median_log_mf": float(np.median(v)), "q1": float(np.quantile(v, 0.25)),
                    "q3": float(np.quantile(v, 0.75)), "loading": float(np.median(v)) / unit if unit else float("nan"),
                    "generator_loading": powers.get(key, float("nan")), "body_unit": unit,
                    "body_unit_papers": papers(body_pairs)})
    return out
