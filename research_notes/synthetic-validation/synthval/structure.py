"""What a published table of means cannot test: correlations, ratios and how measures scale.

Three checks of the generator's structure against what the 39 papers print beside their means.

- Correlations of a person's measures. The only ones printed are Griffith's (griffith2016 Table 1,
  p. 674; the reread's note, research_notes/clinical-reread/notes/griffith2016.md L170-175 on the
  reread's branch): Pearson correlations of each subject's L1-L5 means, men and women apart, over
  540 of each, read on CT. The generator has no sex; its size spread stands for both sexes and
  every stature, so it is held to the correlation of Griffith's two sexes taken together
  (mixed_sex_r), from his within-sex r and his means and SDs of the subject means by sex. Mixing
  the sexes raises a correlation only where both measures differ by sex; where one barely does,
  as the canal's depth, it lowers it. They are read on the measured values, since Griffith's carry
  a CT's error too. Griffith's vertebral body area is
  the body's section at mid-pedicle; the generator has no such measure, so each of its two
  end-plate areas, the nearest sections it draws, stands in on its own and the two correlations
  are averaged (their mean would average two errors away and read higher than one section).
- Ratios with published normal values: each set beside the synthetic population's mean of
  per-vertebra ratios and the ratio of Panjabi's means, by level. Alonge's and Cizmic's are the
  reread's synthesis draft (measures.md), Amonoo-Kuofi's his Table 4 recomputed to two decimals by
  sex (the reread's note), and Tan's the ratio of his own means at each level, read from the
  snapshot (SNAPSHOT_RATIOS); a published ratio of means is not a mean of ratios, which reads a
  little higher for a ratio whose terms spread. A ratio of two Panjabi measures shows where his
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
from typing import Dict, List, Optional, Sequence

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
# griffith2016 Tables 2 to 5, p. 675: each subject's L1-L5 mean, mean (SD), men then women; the
# reread's note, research_notes/clinical-reread/notes/griffith2016.md L34, L46, L58 and L70.
GRIFFITH_SEX = {
    "canal_area": ((278.5, 50.3), (262.8, 42.5)),
    "canal_ap": ((15.82, 1.96), (15.55, 1.72)),
    "canal_w": ((23.66, 2.59), (22.26, 2.25)),
    "body_area": ((1419.3, 185.5), (1162.9, 153.7)),
}

# (name, numerator, denominator or None for area / (w x d), the published values by level, source)
RATIOS = (
    ("canal depth / body depth", "canal_ap", "endplate_depth",
     {"alonge2021": dict(zip(LUMBAR, (0.70, 0.64, 0.58, 0.58, 0.58))),
      "amonookuofi1985 (men)": dict(zip(LUMBAR, (0.57, 0.52, 0.46, 0.46, 0.50))),
      "amonookuofi1985 (women)": dict(zip(LUMBAR, (0.61, 0.55, 0.49, 0.45, 0.47)))},
     "alonge2021 p. 73 (CT, 120 Nigerian adults; body depth at mid-body); amonookuofi1985 Table 4, p. 74 (122"
     " skeletons), its ratio of the sexes' means recomputed to two decimals (the reread's note, amonookuofi1985.md"
     " L184-185)"),
    ("canal width / canal depth", "canal_w", "canal_ap",
     {"cizmic2023": dict(zip(LUMBAR, (1.30, 1.39, 1.55, 1.63, 1.79)))},
     "cizmic2023 (CT, 200 adults of Bosnia and Herzegovina); measures.md L695 on the reread's branch"),
    ("transverse width / end-plate width", "transverse_width", "endplate", {},
     "tan2004 (10 Singaporean cadavers), the ratio of his means at each level (the snapshot)"),
    ("canal area / (width x depth)", "canal_area", None, {},
     "tan2004, the ratio of his means at each level (the snapshot)"),
)
# (ratio name, paper): a published ratio taken as the ratio of the paper's own means at each level,
# from the snapshot's rows, where the paper prints the terms and not the ratio.
SNAPSHOT_RATIOS = (("transverse width / end-plate width", "tan2004"), ("canal area / (width x depth)", "tan2004"))


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


def mixed_sex_r(a: str, b: str, r_men: float, r_women: float) -> float:
    """The correlation of two subject means in Griffith's men and women taken together, half and
    half as he measured them: the within-sex covariances averaged, plus a quarter of the product of
    the differences of the sexes' means, over the mixed SDs."""
    def mixed(key):
        (m1, s1), (m2, s2) = GRIFFITH_SEX[key]
        return m1 - m2, 0.5 * (s1 ** 2 + s2 ** 2) + 0.25 * (m1 - m2) ** 2
    (da, va), (db, vb) = mixed(a), mixed(b)
    (_, sa1), (_, sa2) = GRIFFITH_SEX[a]
    (_, sb1), (_, sb2) = GRIFFITH_SEX[b]
    cov = 0.5 * (r_men * sa1 * sb1 + r_women * sa2 * sb2) + 0.25 * da * db
    return float(cov / math.sqrt(va * vb))


def griffith_targets() -> Dict[str, float]:
    """Griffith's four correlations for a population with no sex, by pair."""
    return {"%s~%s" % (a, b): mixed_sex_r(a, b, men, women) for a, b, men, women in GRIFFITH}


def ratios_of_means(rows: Sequence[dict], paper: str, num: str, den: Optional[str]) -> Dict[str, float]:
    """A paper's ratio of its own means by lumbar level, from the snapshot's rows of all its people
    (no group, side or sex of their own); for den None, the canal's area over its width and depth."""
    means: Dict[tuple, float] = {}
    for r in rows:
        if r["paper"] == paper and not r["group"] and not r["side"] and r["level"] in LUMBAR:
            means.setdefault((r["key"], r["level"]), r["mean"])
    out = {}
    for level in LUMBAR:
        terms = [num, den] if den else [num, "canal_w", "canal_ap"]
        if all((t, level) in means for t in terms):
            top = means[(num, level)]
            out[level] = top / means[(den, level)] if den else top / (means[("canal_w", level)] * means[("canal_ap", level)])
    return out


def ratio_table(pop: Population, mu: np.ndarray, keys: Sequence[str], levels: Sequence[str],
                rows: Sequence[dict] = ()) -> List[dict]:
    """Each published ratio beside the synthetic mean of per-vertebra ratios and Panjabi's ratio of
    means, by lumbar level. mu is the generator's table (measures, levels) in `keys` order; rows
    are the snapshot's, for the ratios SNAPSHOT_RATIOS reads from them."""
    out = []
    for name, num, den, published, source in RATIOS:
        published = dict(published)
        for ratio, paper in SNAPSHOT_RATIOS:
            if ratio == name:
                published[paper] = ratios_of_means(rows, paper, num, den)
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
    size it implies, the median over the median of the body's lengths (those of `anchor` that give
    a pair; body_unit_measures names them), against the generator's loading, its power (1 a length,
    2 an area, 0 an angle). The unit is one population's and a measure's pairs another's, so a share
    mixes the measure's dimorphism with how dimorphism differs between populations."""
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
                    "body_unit_papers": papers(body_pairs),
                    "body_unit_measures": ";".join(k for k in anchor if lr.get(k)), "is_unit": key in anchor and bool(lr.get(key))})
    return out
