"""Tan 2004's population modelled apart from the other papers' (greg's ask of 2026-10-29, 22:43 UTC:
"separate the tan population from the rest to reduce variance and re-evaluate in a quick way how
that effects the power and accuracy of the predictor").

The validation pools every usable series of a cell into one population of populations, Tan's ten
Chinese Singaporean cadavers among them. Tan prints 22 levels of 19 measures, so in many cells it
is one of three or four series, and its means sit apart from the rest (the README's answer 1:
Panjabi's excess over the papers falls from 0.69 to 0.17 of his SD once Tan is out). Pooled, Tan's
distance enters the spread between populations, tau, as if any population could sit as far off,
and every reading built on tau widens with it: part A's worth of a pool in scans, part B's f and
part C's tables, which move the rule's table by the calibrated spread before the rule names
fields. Dropping Tan, which run.py already does as a sensitivity reading, throws its information
away and changes the cells compared. Here Tan is a stratum of its own instead:

- the rest, every series but Tan's, is one population of populations with its own spread, read
  on the cells where the rest alone hold three series or more and Tan prints too, so the spread
  with Tan pooled in and with Tan apart are read on the same cells (matched_spread);
- Tan is one population, fixed, not a draw: its own means at every level it prints, its distance
  from the rest's pooled mean in Panjabi's SD per cell, and as a table for the rule, Tan's means
  for the seven SPINEPS measures with Panjabi's SDs (tan_table), scored as power.naming_loss
  scores a moved table, against the rule's own table on the same columns.

Tan's SDs stay out of every published SD as the validation leaves them out (literature.py,
DISPERSION_UNCERTAIN), so only Tan's means are used here, and his SE where the pool weights him.

The prediction (greg's word of 2026-10-29, 23:43 UTC: keep the populations separate and make "a
metaanalysis style prediction", never one merged population). The validation's pool is already a
random-effects meta-analysis, each paper's series one study and REML's tau the spread between
them (pooling.py), and its prediction for one more population is Higgins' interval, mean +/-
t(k - 2) sqrt(tau^2 + SE^2). prediction_by_stratum reads that interval three ways on the matched
cells: from the merged pool, Tan one study among the rest's; from the rest's stratum alone, the
prediction for a population known to be of their kind; and from the two strata as a mixture, the
prediction for a population of unknown kind, each population counting once. Holding each of the
rest's series out in turn says whether the narrower interval is honest: the share of held-out
series each interval covers against its nominal 95 per cent.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
from scipy import stats

from schwingcheck import LEVELS
from schwingcheck import measures as MS

from . import literature as L
from . import power as PW
from .validate import MODALITY_SETS, cells, literature_at, validated_measures

TAN = "tan2004"


def split(series: Sequence[L.Series]) -> Tuple[List[L.Series], List[L.Series]]:
    """The rest's series and Tan's."""
    return [s for s in series if s.paper != TAN], [s for s in series if s.paper == TAN]


def matched_spread(series: Sequence[L.Series], modality_set: str = "bone_ct",
                   measures: Optional[Sequence[MS.Measure]] = None) -> List[dict]:
    """Every cell where the rest hold three usable series or more and Tan prints one: the REML
    spread with Tan pooled in and with Tan apart (the rest alone), each over Panjabi's SD and over
    the papers' SD, part A's worth in scans of each, and Tan's distance from the rest's pooled
    mean in Panjabi's SD and in the rest's own spread."""
    rest, _ = split(series)
    every = cells(series, MODALITY_SETS[modality_set])
    seven = set(MS.SPINEPS_7)
    out = []
    for m, key, psd, level, rows in PW._cells_of_three(rest, modality_set, measures):
        tan_rows = [s for s in every.get((key, level), []) if s.paper == TAN]
        if not tan_rows:
            continue
        apart, pooled = literature_at(rows), literature_at(rows + tan_rows)
        lit_sd = apart.sd
        tau_apart, tau_pooled = apart.mean.tau, pooled.mean.tau
        distance = tan_rows[0].mean - apart.mean.mean
        out.append({"measure": key, "level": level, "kind": m.kind, "seven": key in seven, "k_rest": len(rows),
                    "panjabi_sd": psd, "literature_sd": lit_sd, "error": float(m.error),
                    "tau_pooled": tau_pooled, "tau_apart": tau_apart,
                    "f_panjabi_pooled": tau_pooled / psd, "f_panjabi_apart": tau_apart / psd,
                    "f_literature_pooled": tau_pooled / lit_sd, "f_literature_apart": tau_apart / lit_sd,
                    "worth_scans_pooled": PW.worth_in_scans(lit_sd, m.error, tau_pooled),
                    "worth_scans_apart": PW.worth_in_scans(lit_sd, m.error, tau_apart),
                    "tan_distance_panjabi_sd": distance / psd,
                    "tan_distance_rest_tau": distance / tau_apart if tau_apart > 0 else float("nan")})
    return out


def _quartiles(a) -> dict:
    a = np.array([x for x in a if math.isfinite(x)])
    if not len(a):
        return {"cells": 0}
    return {"cells": int(len(a)), "q1": float(np.quantile(a, 0.25)), "median": float(np.median(a)),
            "q3": float(np.quantile(a, 0.75))}


def spread_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Quartiles of each reading over all the matched cells and over the seven's, with the median
    ratio of the variance between populations pooled over apart (how much variance Tan adds)."""
    out = {}
    for group, rs in (("all", rows), ("seven", [r for r in rows if r["seven"]])):
        g = {k: _quartiles([r[k] for r in rs]) for k in
             ("f_panjabi_pooled", "f_panjabi_apart", "f_literature_pooled", "f_literature_apart",
              "worth_scans_pooled", "worth_scans_apart", "tan_distance_panjabi_sd", "tan_distance_rest_tau")}
        g["variance_ratio_pooled_over_apart"] = _quartiles(
            [(r["tau_pooled"] / r["tau_apart"]) ** 2 for r in rs if r["tau_apart"] > 0])
        g["tan_above_rest"] = int(sum(r["tan_distance_panjabi_sd"] > 0 for r in rs))
        out[group] = g
    return out


def tan_table(series: Sequence[L.Series], measures: Sequence[MS.Measure]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """The rule's table as Tan's population would give it: Tan's mean at every level he prints,
    Panjabi's SD (Tan's SDs being left out as the validation leaves them out). A level Tan does not
    print takes Panjabi's mean times Tan's ratio to Panjabi at the nearest printed levels on each
    side, averaged, and is listed."""
    mu, sd = MS.arrays(list(measures), LEVELS)
    out = mu.copy()
    by = {(s.key, s.level): s.mean for s in series if s.paper == TAN and L.usable(s)}
    filled = []
    for j, m in enumerate(measures):
        key = L.measure_key(m.key)
        have = [i for i, lv in enumerate(LEVELS) if (key, lv) in by]
        if not have:
            raise ValueError("Tan prints no %s" % key)
        ratio = {i: by[key, LEVELS[i]] / mu[j, i] for i in have}
        for i, lv in enumerate(LEVELS):
            if i in ratio:
                out[j, i] = by[key, lv]
                continue
            near = [r for r in (max([h for h in have if h < i], default=None), min([h for h in have if h > i], default=None))
                    if r is not None]
            out[j, i] = mu[j, i] * float(np.mean([ratio[r] for r in near]))
            filled.append("%s %s" % (key, lv))
    return out, sd, filled


BEFORE = "before: 39 papers pooled"
AFTER_REST = "after: the rest without Tan"
AFTER_TAN = "after: Tan's own table"


def naming_by_stratum(series: Sequence[L.Series], splits: Dict[str, dict], widths: Sequence[int] = (1, 3, 9),
                      columns: int = 300, tables: int = 4, column_seed: int = PW.NAMING_COLUMN_SEED,
                      table_seed: int = PW.NAMING_TABLE_SEED) -> List[dict]:
    """Part C's naming loss, before and after: the rule's own table; tables moved by the calibrated
    split of all 39 papers pooled (before) and of the rest alone (after, the rest's stratum); and
    Tan's own table, one fixed table (after, Tan's stratum). The columns are power.naming_loss's,
    the same seeds. The before and after tables of one index take the same standard draws
    (power.shifted_table's `together` and `apart`), scaled by each stratum's own shift and rest, so
    the two arms are paired table by table and their difference carries no draw of its own: the
    comparison is of the spreads, not of which tables the seeds gave each arm."""
    from . import naming as N
    from .population import GENERATOR, draw
    seven = MS.select(MS.SPINEPS_7)
    pop = draw(GENERATOR, columns, column_seed, seven)
    mu, sd = MS.arrays(seven, LEVELS)
    mu_t, sd_t, _ = tan_table(series, seven)
    arms = {BEFORE: (splits["pooled"]["shift_sd_calibrated"], splits["pooled"]["level_sd_calibrated"]),
            AFTER_REST: (splits["rest"]["shift_sd_calibrated"], splits["rest"]["level_sd_calibrated"])}
    out = []
    for w in widths:
        own = N.score(pop, seven, w)
        out.append(dict(own, arm="own table", shift=0.0, level=0.0, table=0, width=w, loss=0.0))
        rng = np.random.default_rng(table_seed)
        for t in range(tables):
            together = rng.normal(size=(mu.shape[0], 1))
            apart = rng.normal(size=mu.shape)
            for name, (shift, level) in arms.items():
                moved = mu + sd * (shift * together + level * apart)
                got = N.score(pop, seven, w, table=(moved, sd))
                out.append(dict(got, arm=name, shift=float(shift), level=float(level), table=t, width=w,
                                loss=100.0 * (own["exact"] - got["exact"])))
        got = N.score(pop, seven, w, table=(mu_t, sd_t))
        out.append(dict(got, arm=AFTER_TAN, shift=float("nan"), level=float("nan"), table=0, width=w,
                        loss=100.0 * (own["exact"] - got["exact"])))
    return out


def naming_summary(rows: Sequence[dict]) -> List[dict]:
    """Per arm and width: the mean loss over its tables in points named exactly, the SD of the
    loss between tables (the variance a table from that population brings), the mean share
    answered at 0.99 and its precision, and for the rest's arm the paired difference from the
    pooled arm, table by table: its mean and the standard error of that mean over the tables."""
    out = []
    for arm in dict.fromkeys(r["arm"] for r in rows):
        for w in sorted({r["width"] for r in rows if r["arm"] == arm}):
            rs = [r for r in rows if r["arm"] == arm and r["width"] == w]
            loss = np.array([r["loss"] for r in rs])
            row = {"arm": arm, "width": w, "tables": len(rs), "exact": float(np.mean([r["exact"] for r in rs])),
                   "loss_mean": float(loss.mean()), "loss_sd_between_tables": float(loss.std(ddof=1)) if len(rs) > 1 else 0.0,
                   "answered": float(np.mean([r["answered"] for r in rs])),
                   "precision": float(np.nanmean([r["precision"] for r in rs]))}
            if arm == AFTER_REST:
                before = {r["table"]: r["loss"] for r in rows if r["arm"] == BEFORE and r["width"] == w}
                diff = np.array([r["loss"] - before[r["table"]] for r in rs])
                row["paired_difference_mean"] = float(diff.mean())
                row["paired_difference_se"] = float(diff.std(ddof=1) / math.sqrt(len(diff))) if len(diff) > 1 else float("nan")
            out.append(row)
    return out


def gold_against_tan(rows: Sequence[dict], counts: Sequence[int] = PW.GOLD_COUNTS) -> List[dict]:
    """How many gold persons tell a population as far off as Tan's from a table taken as exact:
    at each count, the least mean shift a one-cell test finds (power.least_shift, in a person's SD,
    read as Panjabi's) against the median and the quartiles of Tan's distance over the seven's
    matched cells, and the share of those cells whose distance it finds."""
    d = np.abs([r["tan_distance_panjabi_sd"] for r in rows if r["seven"]])
    out = []
    for n in counts:
        least = PW.least_shift(n)
        out.append({"persons": n, "least_mean_shift_one_cell": least, "tan_median_distance": float(np.median(d)),
                    "share_of_seven_cells_found": float((d >= least).mean()), "cells": int(len(d))})
    return out


# ----- the prediction for one more population: merged, by stratum, as a mixture ----------------

BAND = 0.95


Z = float(stats.norm.ppf(0.975))


def _prediction(rows: Sequence[L.Series]) -> dict:
    """pooling.pool's prediction for one more population's mean from these series: the pooled
    mean, the predictive scale sqrt(tau^2 + SE^2), Higgins' interval on it, t on k - 2 degrees of
    freedom, which carries how uncertain the spread is from k series, and the plug-in interval,
    z on the same scale, the spread taken as known; both NaN with fewer than three series."""
    p = literature_at(list(rows)).mean
    scale = math.sqrt(p.tau2 + p.se ** 2)
    plug = (p.mean - Z * scale, p.mean + Z * scale) if p.k >= 3 else (float("nan"), float("nan"))
    return {"k": p.k, "mean": p.mean, "low": p.pi_low, "high": p.pi_high, "tau2": p.tau2, "scale": scale,
            "plug_low": plug[0], "plug_high": plug[1]}


def _quantile(cdf, prob: float, lo: float, hi: float, steps: int = 200) -> float:
    for _ in range(steps):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if cdf(mid) < prob else (lo, mid)
    return (lo + hi) / 2.0


def mixture_band(rest: dict, tan: L.Series, level: float = BAND) -> Tuple[float, float]:
    """The central band of a population of unknown kind, the two strata as a mixture with each
    population counting once: with probability k / (k + 1) it is of the rest's kind, its mean
    Student t on k - 2 degrees of freedom at the rest's pooled mean with the predictive scale, as
    Higgins' interval has it; with probability 1 / (k + 1) of Tan's, its mean normal at Tan's with
    the rest's spread between populations and Tan's own SE, as the pool weights him, since a
    stratum of one population gives no spread of its own (a subgroup analysis' common tau). The
    edges are found by bisection on the mixture's distribution function."""
    k = rest["k"]
    w_tan = 1.0 / (k + 1)
    tan_scale = math.sqrt(rest["tau2"] + tan.sd ** 2 / tan.n)

    def cdf(x: float) -> float:
        return ((1.0 - w_tan) * stats.t.cdf((x - rest["mean"]) / rest["scale"], k - 2)
                + w_tan * stats.norm.cdf((x - tan.mean) / tan_scale))
    span = 10.0 * max(rest["scale"], tan_scale) + abs(rest["mean"] - tan.mean)
    lo, hi = min(rest["mean"], tan.mean) - span, max(rest["mean"], tan.mean) + span
    return _quantile(cdf, (1.0 - level) / 2.0, lo, hi), _quantile(cdf, 1.0 - (1.0 - level) / 2.0, lo, hi)


def prediction_by_stratum(series: Sequence[L.Series], modality_set: str = "bone_ct",
                          measures: Optional[Sequence[MS.Measure]] = None) -> List[dict]:
    """On matched_spread's cells, the prediction for one more population's mean three ways: from
    the merged pool (the rest and Tan as one meta-analysis), from the rest's stratum alone and from
    the two strata as a mixture (mixture_band), each interval's half-width in Panjabi's SD, the
    merged and the rest's as Higgins' t interval and as the plug-in z interval (_prediction);
    whether Tan's mean falls inside the merged and the rest's intervals; and, where the rest hold
    four series or more, each of the rest's series held out in turn and every interval built on
    the others, counting the series each covers, so the share covered reads against 95 per cent."""
    rest, _ = split(series)
    every = cells(series, MODALITY_SETS[modality_set])
    seven = set(MS.SPINEPS_7)
    out = []
    for m, key, psd, level, rows in PW._cells_of_three(rest, modality_set, measures):
        tan_rows = [s for s in every.get((key, level), []) if s.paper == TAN]
        if not tan_rows:
            continue
        tan = tan_rows[0]
        merged, apart = _prediction(rows + tan_rows), _prediction(rows)
        mixed = mixture_band(apart, tan)
        row = {"measure": key, "level": level, "kind": m.kind, "seven": key in seven, "k_rest": len(rows),
               "panjabi_sd": psd, "tan_mean": tan.mean, "rest_means": ";".join("%.6g" % s.mean for s in rows),
               "merged_mean": merged["mean"], "merged_low": merged["low"], "merged_high": merged["high"],
               "rest_mean": apart["mean"], "rest_low": apart["low"], "rest_high": apart["high"],
               "mixture_low": mixed[0], "mixture_high": mixed[1],
               "half_width_merged_sd": (merged["high"] - merged["low"]) / 2.0 / psd,
               "half_width_rest_sd": (apart["high"] - apart["low"]) / 2.0 / psd,
               "half_width_mixture_sd": (mixed[1] - mixed[0]) / 2.0 / psd,
               "half_width_merged_plug_sd": Z * merged["scale"] / psd,
               "half_width_rest_plug_sd": Z * apart["scale"] / psd,
               "tan_inside_merged": bool(merged["low"] <= tan.mean <= merged["high"]),
               "tan_inside_rest": bool(apart["low"] <= tan.mean <= apart["high"]),
               "tan_inside_merged_plug": bool(merged["plug_low"] <= tan.mean <= merged["plug_high"]),
               "tan_inside_rest_plug": bool(apart["plug_low"] <= tan.mean <= apart["plug_high"]),
               "held_out": 0, "covered_merged": 0, "covered_rest": 0, "covered_mixture": 0,
               "covered_merged_plug": 0, "covered_rest_plug": 0}
        if len(rows) >= 4:
            for s in rows:
                others = [r for r in rows if r is not s]
                m_, a_ = _prediction(others + tan_rows), _prediction(others)
                b_ = mixture_band(a_, tan)
                row["held_out"] += 1
                row["covered_merged"] += int(m_["low"] <= s.mean <= m_["high"])
                row["covered_rest"] += int(a_["low"] <= s.mean <= a_["high"])
                row["covered_mixture"] += int(b_[0] <= s.mean <= b_[1])
                row["covered_merged_plug"] += int(m_["plug_low"] <= s.mean <= m_["plug_high"])
                row["covered_rest_plug"] += int(a_["plug_low"] <= s.mean <= a_["plug_high"])
        out.append(row)
    return out


def prediction_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Over all the matched cells and over the seven's: the quartiles of each interval's half-width
    in Panjabi's SD and of the ratio of the rest's over the merged pool's, t and plug-in alike, the
    cells where Tan's mean falls inside each, and the leave-one-out coverage of each interval, the
    series held out and the share each covers."""
    out = {}
    for group, rs in (("all", rows), ("seven", [r for r in rows if r["seven"]])):
        held = sum(r["held_out"] for r in rs)
        g = {"cells": len(rs), "cells_held_out": int(sum(r["held_out"] > 0 for r in rs)), "series_held_out": int(held)}
        for name in ("merged", "rest", "mixture", "merged_plug", "rest_plug"):
            g["half_width_%s_sd" % name] = _quartiles([r["half_width_%s_sd" % name] for r in rs])
        for name in ("", "_plug"):
            g["half_width_ratio_rest_over_merged" + name] = _quartiles(
                [r["half_width_rest%s_sd" % name] / r["half_width_merged%s_sd" % name] for r in rs
                 if r["half_width_merged%s_sd" % name] > 0])
        for name in ("merged", "rest", "merged_plug", "rest_plug"):
            g["tan_inside_" + name] = int(sum(r["tan_inside_" + name] for r in rs))
        for name in ("merged", "rest", "mixture", "merged_plug", "rest_plug"):
            covered = sum(r["covered_" + name] for r in rs)
            g["covered_" + name] = int(covered)
            g["coverage_" + name] = covered / held if held else float("nan")
        out[group] = g
    return out
