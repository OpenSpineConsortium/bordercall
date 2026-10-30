"""Subgroup meta-analysis of the published series by any population variable, cell by cell.

greg's ask of 2026-10-29, 23:54 UTC: split the populations "into as many known populations there
are, probably by author but if there are race variables and sex variables etc make sure you can
do subgroup analysis very easily". Every series is tagged with its variables by register.tag
(the series' own: paper, cohort, sex, modality, technique; its cohort's from the register:
country, region, ancestry, specimen, age band, decade), and the same three readings run for any
of them, so a new variable is one column of data/populations.csv and no code:

1. analysis: in every cell with three series or more and two subgroups or more, each subgroup
   pooled by REML as the whole cell is (pooling.pool; a subgroup of one series is its mean with
   its own SE and no spread), and the test for subgroup differences of the Cochrane Handbook
   (section 10.11.3, Borenstein and others 2009 chapter 19): Q_between = sum of w_g (mu_g - mu)^2
   over the subgroups, w_g = 1 / SE_g^2 with SE_g carrying its subgroup's tau^2 (random effects
   within the subgroups, the subgroup means fixed), on G - 1 degrees of freedom against chi
   square. Beside it the spread within the subgroups, tau^2 pooled over the subgroups with two
   series or more on their degrees of freedom, against the whole cell's, whose complement is the
   share of the spread between populations the variable accounts for (R^2, held at zero or above,
   as a mixed-effects meta-regression on the variable reads it; NaN where no subgroup has two
   series, as every subgroup of "paper" has one). With three to nine series a cell, the test
   has little power and a subgroup of one series proves nothing; the summary says in how many
   cells each reading could be made.
2. against_rest: one value of a variable against the rest of the cell, as tan.py reads Tan 2004
   (Tan is the case variable "paper", value "tan2004", and test_subgroups holds the two readings
   to the same distances): in every cell where the value has a series and the rest hold three or
   more, the value's pooled mean's distance from the rest's pooled mean in Panjabi's SD, the
   spread between populations with the value pooled in and apart, their variance ratio, and
   whether the rest's prediction interval for one more population (t on k - 2, and z with the
   spread taken as known) holds the value's mean. each_against_rest runs it for every value of a
   variable with enough cells.
3. paired_contrast: for a variable a paper prints apart on comparable people, the sexes of one
   cohort or the ancestries of one collection, the within-paper difference (male minus female,
   one ancestry minus another) with its SE in every pair that prints both, pooled across the pairs
   by REML in every cell with one pair or more, in the measure's unit and in Panjabi's SD; a
   difference read within a paper carries none of the paper's own shift, which a subgroup analysis
   across papers confounds with it. It takes the series of literature.select(rows, strata="apart"),
   which keeps every printed stratum and a cohort's sexes as series of their own, and only it does.

Every reading takes the register's words as they are: a country inferred from an institution,
an ancestry only where the paper states one, and "not stated" is a value like any other, which
the tables show so that a subgroup made of what papers left unsaid is not read as a population.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy import stats

from schwingcheck import LEVELS
from schwingcheck import measures as MS

from . import literature as L
from . import pooling as P
from . import power as PW
from . import register as RG
from .validate import MODALITY_SETS, cells, literature_at, validated_measures

Z = float(stats.norm.ppf(0.975))
ALPHA = 0.05


def by_value(rows: Sequence[L.Series], variable: str, register: Dict[tuple, RG.Population]) -> Dict[str, List[L.Series]]:
    """The series of one cell by the variable's value, values in order."""
    out: Dict[str, List[L.Series]] = {}
    for s in rows:
        out.setdefault(RG.tag(s, register)[variable], []).append(s)
    return dict(sorted(out.items()))


def pooled_or_one(rows: Sequence[L.Series]) -> dict:
    """A subgroup's estimate: pooling.pool's over two series or more (its mean, SE with tau^2 in
    it, tau^2 and Higgins' interval from three on), or the one series' mean and SE, no spread."""
    if len(rows) >= 2:
        p = literature_at(list(rows)).mean
        return {"k": p.k, "mean": p.mean, "se": p.se, "tau2": p.tau2, "low": p.pi_low, "high": p.pi_high}
    s = rows[0]
    return {"k": 1, "mean": s.mean, "se": s.sd / math.sqrt(s.n), "tau2": float("nan"), "low": float("nan"),
            "high": float("nan")}


def _cells(series: Sequence[L.Series], modality_set: str, measures: Optional[Sequence[MS.Measure]], least: int):
    """(measure, its key, Panjabi's SD at the level, level, the cell's series) for every cell with
    `least` usable series or more."""
    measures = validated_measures(measures)
    by = cells(series, MODALITY_SETS[modality_set])
    _, sd = MS.arrays(measures, LEVELS)
    for j, m in enumerate(measures):
        key = L.measure_key(m.key)
        for i, level in enumerate(LEVELS):
            rows = by.get((key, level), [])
            if len(rows) >= least:
                yield m, key, float(sd[j, i]), level, rows


def test_between(sub: Dict[str, dict]) -> Tuple[float, int, float]:
    """The test for subgroup differences: Q_between, its degrees of freedom and p."""
    w = np.array([1.0 / g["se"] ** 2 for g in sub.values()])
    mu = np.array([g["mean"] for g in sub.values()])
    centre = (w * mu).sum() / w.sum()
    q = float((w * (mu - centre) ** 2).sum())
    df = len(sub) - 1
    return q, df, float(stats.chi2.sf(q, df)) if df > 0 else float("nan")


def spread_within(sub: Dict[str, dict]) -> Tuple[float, int]:
    """tau^2 pooled over the subgroups with two series or more on their degrees of freedom, and
    how many subgroups it is read from."""
    pairs = [(g["k"] - 1, g["tau2"]) for g in sub.values() if g["k"] >= 2]
    if not pairs:
        return float("nan"), 0
    df = sum(d for d, _ in pairs)
    return float(sum(d * t for d, t in pairs) / df), len(pairs)


def analysis(series: Sequence[L.Series], variable: str, register: Dict[tuple, RG.Population],
             modality_set: str = "bone_ct", measures: Optional[Sequence[MS.Measure]] = None,
             least_groups: int = 2) -> List[dict]:
    """One row per cell with three series or more and `least_groups` values of the variable or
    more: the subgroups with their counts, the test for subgroup differences, the spread of the
    whole cell and within the subgroups over Panjabi's SD, the share the variable accounts for,
    and the widest gap between two subgroups' means in Panjabi's SD."""
    seven = set(MS.SPINEPS_7)
    out = []
    for m, key, psd, level, rows in _cells(series, modality_set, measures, 3):
        groups = by_value(rows, variable, register)
        if len(groups) < least_groups:
            continue
        total = literature_at(list(rows)).mean
        sub = {v: pooled_or_one(rs) for v, rs in groups.items()}
        q, df, p = test_between(sub)
        tau2_within, pooled_groups = spread_within(sub)
        r2 = (max(0.0, 1.0 - tau2_within / total.tau2) if total.tau2 > 0 and math.isfinite(tau2_within) else float("nan"))
        means = [g["mean"] for g in sub.values()]
        out.append({"variable": variable, "measure": key, "level": level, "kind": m.kind, "seven": key in seven,
                    "k": len(rows), "groups": len(groups), "values": ";".join("%s:%d" % (v, len(rs)) for v, rs in groups.items()),
                    "groups_with_two_or_more": pooled_groups, "q_between": q, "df": df, "p_between": p,
                    "tau2_total": total.tau2, "tau2_within": tau2_within, "f_total": math.sqrt(total.tau2) / psd,
                    "f_within": math.sqrt(tau2_within) / psd if math.isfinite(tau2_within) else float("nan"), "r2": r2,
                    "widest_gap_sd": (max(means) - min(means)) / psd, "panjabi_sd": psd})
    return out


def _quartiles(a) -> dict:
    a = np.array([x for x in a if isinstance(x, (int, float)) and math.isfinite(x)])
    if not len(a):
        return {"cells": 0}
    return {"cells": int(len(a)), "q1": float(np.quantile(a, 0.25)), "median": float(np.median(a)),
            "q3": float(np.quantile(a, 0.75))}


def analysis_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Per variable, over all its cells and over the seven's: the cells, the series and subgroups
    a cell holds, the cells whose test is below ALPHA, the cells the share could be read in and its
    quartiles, the spread of the whole cell and within the subgroups, the widest gap."""
    out: Dict[str, dict] = {}
    for variable in dict.fromkeys(r["variable"] for r in rows):
        out[variable] = {}
        for group, rs in (("all", [r for r in rows if r["variable"] == variable]),
                          ("seven", [r for r in rows if r["variable"] == variable and r["seven"]])):
            tested = [r for r in rs if math.isfinite(r["p_between"])]
            out[variable][group] = {
                "cells": len(rs), "series_per_cell": _quartiles([r["k"] for r in rs]),
                "groups_per_cell": _quartiles([r["groups"] for r in rs]), "cells_tested": len(tested),
                "cells_below_alpha": int(sum(r["p_between"] < ALPHA for r in tested)),
                "share_below_alpha": float(np.mean([r["p_between"] < ALPHA for r in tested])) if tested else float("nan"),
                "r2": _quartiles([r["r2"] for r in rs]), "f_total": _quartiles([r["f_total"] for r in rs]),
                "f_within": _quartiles([r["f_within"] for r in rs]),
                "widest_gap_sd": _quartiles([r["widest_gap_sd"] for r in rs])}
    return out


def against_rest(series: Sequence[L.Series], variable: str, value: str, register: Dict[tuple, RG.Population],
                 modality_set: str = "bone_ct", measures: Optional[Sequence[MS.Measure]] = None) -> List[dict]:
    """One value of a variable against the rest of each cell, as tan.matched_spread reads Tan:
    every cell where the value has a series and the rest hold three or more."""
    seven = set(MS.SPINEPS_7)
    out = []
    for m, key, psd, level, rows in _cells(series, modality_set, measures, 3):
        own = [s for s in rows if RG.tag(s, register)[variable] == value]
        rest = [s for s in rows if s not in own]
        if not own or len(rest) < 3:
            continue
        apart, pooled, mine = literature_at(rest).mean, literature_at(list(rows)).mean, pooled_or_one(own)
        scale = math.sqrt(apart.tau2 + apart.se ** 2)
        distance = mine["mean"] - apart.mean
        out.append({"variable": variable, "value": value, "measure": key, "level": level, "kind": m.kind,
                    "seven": key in seven, "k_value": len(own), "k_rest": len(rest), "panjabi_sd": psd,
                    "value_mean": mine["mean"], "rest_mean": apart.mean, "distance_sd": distance / psd,
                    "f_pooled": pooled.tau / psd, "f_apart": apart.tau / psd,
                    "variance_ratio_pooled_over_apart": (pooled.tau2 / apart.tau2) if apart.tau2 > 0 else float("nan"),
                    "inside_rest_t": bool(apart.pi_low <= mine["mean"] <= apart.pi_high),
                    "inside_rest_z": bool(abs(distance) <= Z * scale)})
    return out


def against_rest_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Over all the cells and the seven's: the distance's quartiles, its absolute median, the
    variance ratio's median, the cells with the value above the rest and inside the rest's
    intervals."""
    out = {}
    for group, rs in (("all", rows), ("seven", [r for r in rows if r["seven"]])):
        out[group] = {"cells": len(rs), "series": int(sum(r["k_value"] for r in rs)),
                      "distance_sd": _quartiles([r["distance_sd"] for r in rs]),
                      "abs_distance_sd": _quartiles([abs(r["distance_sd"]) for r in rs]),
                      "variance_ratio_pooled_over_apart": _quartiles([r["variance_ratio_pooled_over_apart"] for r in rs]),
                      "above_rest": int(sum(r["distance_sd"] > 0 for r in rs)),
                      "inside_rest_t": int(sum(r["inside_rest_t"] for r in rs)),
                      "inside_rest_z": int(sum(r["inside_rest_z"] for r in rs))}
    return out


def each_against_rest(series: Sequence[L.Series], variable: str, register: Dict[tuple, RG.Population],
                      least_cells: int = 1, modality_set: str = "bone_ct",
                      measures: Optional[Sequence[MS.Measure]] = None) -> Tuple[List[dict], Dict[str, dict]]:
    """against_rest for every value of the variable, the rows of all of them and a summary per
    value with `least_cells` cells or more."""
    values = sorted({RG.tag(s, register)[variable] for s in series if L.usable(s)})
    rows, summary = [], {}
    for v in values:
        got = against_rest(series, variable, v, register, modality_set, measures)
        rows += got
        if len(got) >= least_cells:
            summary[v] = against_rest_summary(got)
    return rows, summary


def paired_contrast(series_apart: Sequence[L.Series], variable: str, pair: Tuple[str, str],
                    register: Dict[tuple, RG.Population], modality_set: str = "bone_ct",
                    measures: Optional[Sequence[MS.Measure]] = None) -> List[dict]:
    """The within-paper difference pair[0] minus pair[1] of a variable a paper prints apart on
    comparable people (the sexes of one cohort and stratum, the ancestries of one cohort and sex),
    pooled across the pairs by REML in every cell with one pair or more: the pooled difference in
    the measure's unit and in Panjabi's SD, its SE, z and p, the spread of the difference between
    the pairs where two or more pool, and Higgins' interval from three on. A pair is two series of
    one paper, cohort and technique that agree on every other stratum (the group for the sexes,
    the sex for a stratum's variable) and differ only in the variable."""
    seven = set(MS.SPINEPS_7)
    out = []
    for m, key, psd, level, rows in _cells(series_apart, modality_set, measures, 1):
        by_key: Dict[tuple, Dict[str, L.Series]] = {}
        for s in rows:
            value = RG.tag(s, register)[variable]
            if value not in pair:
                continue
            same = (s.paper, s.cohort, s.technique) + ((s.group,) if variable == "sex" else (s.sex,))
            by_key.setdefault(same, {})[value] = s
        pairs = [(k, d[pair[0]], d[pair[1]]) for k, d in by_key.items() if len(d) == 2]
        if not pairs:
            continue
        diff = np.array([a.mean - b.mean for _, a, b in pairs])
        var = np.array([a.sd ** 2 / a.n + b.sd ** 2 / b.n for _, a, b in pairs])
        if len(pairs) >= 2:
            p = P.pool(diff, var)
            mean, se, tau2, lo, hi = p.mean, p.se, p.tau2, p.pi_low, p.pi_high
        else:
            mean, se, tau2, lo, hi = float(diff[0]), float(math.sqrt(var[0])), float("nan"), float("nan"), float("nan")
        z = mean / se if se > 0 else float("nan")
        out.append({"variable": variable, "pair": "%s - %s" % pair, "measure": key, "level": level, "kind": m.kind,
                    "seven": key in seven, "pairs": len(pairs), "within": ";".join("/".join(str(x) for x in k) for k, _, _ in pairs),
                    "panjabi_sd": psd, "difference": mean, "se": se, "difference_sd": mean / psd,
                    "ci_low_sd": (mean - Z * se) / psd, "ci_high_sd": (mean + Z * se) / psd, "z": z,
                    "p": float(2 * stats.norm.sf(abs(z))) if math.isfinite(z) else float("nan"),
                    "tau_between_pairs_sd": math.sqrt(tau2) / psd if math.isfinite(tau2) else float("nan"),
                    "pi_low_sd": lo / psd if math.isfinite(lo) else float("nan"),
                    "pi_high_sd": hi / psd if math.isfinite(hi) else float("nan")})
    return out


def contrast_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Over all cells, the seven's and each measure: the cells, the pairs a cell pools, the
    difference's quartiles in Panjabi's SD, the cells where it is above zero and below ALPHA."""
    groups = {"all": list(rows), "seven": [r for r in rows if r["seven"]]}
    for key in sorted({r["measure"] for r in rows}):
        groups[key] = [r for r in rows if r["measure"] == key]
    out = {}
    for g, rs in groups.items():
        out[g] = {"cells": len(rs), "pairs_per_cell": _quartiles([r["pairs"] for r in rs]),
                  "difference_sd": _quartiles([r["difference_sd"] for r in rs]),
                  "above_zero": int(sum(r["difference_sd"] > 0 for r in rs)),
                  "below_alpha": int(sum(r["p"] < ALPHA for r in rs if math.isfinite(r["p"]))),
                  "tau_between_pairs_sd": _quartiles([r["tau_between_pairs_sd"] for r in rs])}
    return out
