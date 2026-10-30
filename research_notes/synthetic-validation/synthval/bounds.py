"""The bounds card: what the published populations say a generator's synthetic spines must look like.

greg's question of 2026-10-30: could the literature's results "at least serve as bounds for generative
models making synthetic spines from ideal spines". They can, on what the papers print: a level's mean
and SD in one population, how far one population's mean sits from another's, the step from one level
to the next inside one paper, and, where a paper prints them apart, the sexes and the age bands. This
module reads those into one card, calibrates it on real populations held out, and scores a generated
cohort against it.

The card, per measure, level and kind of population (the register's specimen: living, dry bone,
cadaver, mixed, and every paper together):

- the mean: the cell's random-effects pool and the 95% interval for a NEW population's mean,
  mean +/- 1.96 sqrt(tau^2 + SE^2), strata.between's spread. The pool is over the cell's series,
  not its papers (papers_table.pooled_cells's pool, which strata.strata_of keeps as the cell's
  pool): a paper printing several cohorts gives several series, so the row's k counts series and
  its papers the papers, and the cell has its own tau from three series on (on the snapshot every
  such cell also has three papers, bounds.json's counts); below that the measure's or every cell's
  median tau over SD (strata.median_f), borrowed from every paper's cells, so a kind with few
  papers is held no tighter than the papers together allow. Higgins's t interval stands beside it,
  on k - 2 degrees of freedom of series, where the cell has three series, since the z interval
  undercovers held-out series with few populations (the README's answer 8: 87%);
- the SD: the within-population SDs the papers print (min, median, max over the populations whose SD
  is certain, Tan 2004's left out as everywhere in this note), the cell's pooled within SD, the
  predictive SD of a person from an unseen population (strata.predictive_sd), and the 95% interval
  for a NEW population's SD, the papers' log SDs pooled by REML as pooling.pool_log_sd pools them and
  read as the means are, own tau from three populations (strata, one a paper) and below that the
  measure's or every measure's typical tau (typical_tau, which says why it is not a median);
- the sex contrast, men minus women in within-sex SDs (Hedges' g), and the age slope, within-band SDs
  per adult decade, each read inside one paper and pooled across papers as covariates.py reads
  them (its contrasts from the full snapshot with the sexes' snapshot beside it, its strata of one
  set of people one value, covariates.by_paper_cell; here per placed cell), with the 95% interval
  of the pooled effect and the 95% interval for a NEW population's effect, effect +/- 1.96
  sqrt(tau^2 + SE^2) read as the means' is: the cell's own tau from three papers, below that the
  measure's or every measure's typical tau of the donor cells, those with three papers or, where
  no cell has three, those with two (covariate_borrowed). The donors' taus are summarised by the
  steps' rule, root mean square by measure and the measures' median, since a donor's REML tau is
  exactly zero where its few papers agree within their error and a median of such zeros lends a
  one-paper effect no spread; run_bounds.py reads the means' rule beside it, with the cells each
  rule leaves clear of zero and how often a paper held out has the sign there (bounds.json's
  covariate_borrowing). Where every donor's tau is zero no rule lends a spread, and the interval
  for a new population is the pooled one (covariate_borrowing says where). A variant of a measure
  (a bracketed key) carries its base key's effect. Not every kind carries a covariate cell
  (bounds.json's counts and kinds_with_no_sex_or_age_cell).

The gradients, per measure and kind, the step from one level to the next (L1 to L2, and so on down
the column C3 to L5): each paper's step read inside the paper, its own mean at the lower level taken
from its own mean at the upper, so the shift a paper carries through a whole measure (its method,
its specimen, its country; 82% of the spread between populations, the first part's split) falls out,
and the steps pooled across papers by REML, with the interval for a new population's step read as
the means' is. Naming lives on these steps: a rule that names levels reads how a measure changes
down the column, so a generator whose steps are wrong names wrong whatever its means. A paper's step
counts only where it prints the same cohorts at both levels. Its variance (step_variance) takes the
correlation r of one person's two adjacent levels as a parameter, since no paper prints one: r = 0
overstates the variance of a paper's own step, which pushes REML's tau to zero on steps of a few
papers and narrows their intervals. The default STEP_R is the r of STEP_R_GRID whose held-out step
coverage (below) is nearest the nominal 0.95, chosen by run_bounds.py, which records the coverage at
every r and the sensitivity at 0, 0.5 and 0.8 (bounds.json's step_r). On the snapshot that is r = 0,
the grid's edge: the coverage falls as r rises and stays under 0.95 at every r. The left-out paper's
own step error is read at the same r, and the sensitivity, reading it at each r apart, finds the
coverage moving with that r far more than with the card's, so held-out coverage does not identify r:
it takes the most lenient reading. What would identify it, one person's levels measured together,
is not in the records (bounds.json's "not on the card"). Beside each step the difference
of the two cells' pooled means, which pool different papers, and how far it sits from the pooled step
in the step's own spread (coherence): where it is far, the mean card and the gradient card pull a
generator two ways and the gradient's is the one read inside papers.

Borrowing differs between the means and the steps, on purpose. A cell with fewer than three series
borrows the median over the cells (strata.median_f), which this module keeps so that every paper's
card has strata.between's spread to the bit, as the rest of the note reads it. A step fewer than
three papers print borrows typical_tau: the root mean square of the measure's REML taus over SD, and
over the measures their median, because REML puts a tau of exactly zero on many steps of three to
nine papers and a median of such zeros would lend a one-paper step no spread at all. run_bounds.py
records the held-out step coverage under both rules and the ratio of the steps' widths to the means'
on the cells and steps of three papers or more, where neither borrows (bounds.json's borrowing).

The calibration: every paper left out in turn, the card of every paper together built from the rest,
and the left-out paper's own strata scored on it as a cohort is scored, its mean, its SD and its steps
each widened by its own sampling error (held_out_verdicts); and each kind's card the same way on that
kind's own papers, its spreads borrowed from every other paper as build borrows them. A cohort drawn
from a card's own model (simulate) passes at about the nominal 0.95 where the card holds together
(tests/test_bounds.py); real populations held out pass less often (bounds.json's calibration,
calibration.csv), so check() judges each test against the bar of real populations, the 10th
percentile and the median of the held-out papers' own rates (bar_of), over the papers whose rate
rests on MIN_BAR_ROWS rows of the test, since a rate over a few rows is mostly binomial noise and
a generated cohort is scored on hundreds; a test with fewer than MIN_BAR_PAPERS such papers has no
bar, which on the snapshot leaves every specimen kind's step test without one (calibration.kinds).
A generated cohort is one population, as a held-out paper is, so the per-paper quantiles are its
comparison, not the rate pooled over every paper's rows nor one weighted by them (bounds.json's
calibration.bars sets the three side by side, with and without Tan 2004, and bar_rule says why).
The step bar is read at the r chosen on the same held-out papers, so it is a little optimistic;
the papers left out are scored on a card of the rest, a little looser than the card of every paper
a generator meets. The sex test is not calibrated: it is a sign, made only where the interval for a
new population's contrast clears zero, and carries no bar.

What the card cannot bound, and says so rather than guess: the correlation of one person's measures
or levels (no paper in the records prints one but Griffith 2016's four, structure.json; published
work beyond the records bounds part of the adjacent-level structure, and bounds.json's "not on the
card" names it), the anomalies (the records hold no series of a transitional or anomalous group,
and the only rows at an L6 or a T13, Busscher 2010's porcine ones in data/series_all.csv, the
selection drops as not human; check() reads a cohort's bodies by their level names, so of the
bodies schwingcheck's columns.py generates the L6 and the T13 go unscored, while the lumbar rib's
L1, the T12 with no rib and the four lumbar bodies keep their ordinary names and are held to the
ordinary cells and steps, the wrong bound rather than none, bounds.json's "not on the card"), a
population no paper sampled (children, the countries and specimens the register does not hold), a
measure or a level no paper prints, and any cell resting on one paper, whose spread between
populations is borrowed. Series whose cohort the register does not hold (the papers the
all-measures selection adds: Bach 2019, Shin 2024, Hinck 1966 and others) enter the card of every
paper together and no specimen's, since a specimen is never inferred.

check() scores a generated cohort, one row a person, measure and level with its value and, where
given, its sex and the person's id: per cell whether the cohort's mean lies in the interval for a new
population's mean, its SD in the interval for a new population's SD, each widened by the cohort's own
sampling error, each level step in its gradient's interval, and where sexes are given, whether the
cohort's sex contrast has the sign the papers' does where the interval for a new population's
contrast excludes zero (held out, the direction of an effect travels between populations and its size
does not, covariates.py). Its verdict (verdict) judges each of the mean, SD and step tests against its
bar, and the cohort fails where any test with a bar fails and passes only where the step test was
made and passes, since naming lives on the steps: the pass rate over every test decides nothing, as
a lumbar gradient flattened at the card's centre keeps it high (bounds.json's checks). On the papers'
card the step test falls short even for populations of the card's own model where two adjacent
levels' mean intervals differ in spread by more than their step's interval allows, which no
population can honour at once and run_bounds.py counts and explains (checks.drawn's
why_below_the_step_bar). The same z-scores give a penalty (their mean square: about 1 under a card
that holds together, the toy of the tests, and above 1 for populations drawn from the papers' own
card, bounds.json's checks.drawn, where the steps carry the excess, mean_square_z_by_test) and a
calibration target, so a generator can use the card as a prior-predictive acceptance test, as a loss
term or as the target its settings are tuned to.
"""
from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass, field, replace
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
from scipy import stats

from schwingcheck import LEVELS

from . import covariates as CV
from . import literature as L
from . import papers_table as PT
from . import pooling as P
from . import register as RG
from . import strata as ST

Z = 1.96
NOMINAL = 0.95
ALL = "all"
NOT_IN_REGISTER = "not in the register"
MIN_SERIES_FOR_TAU = ST.MIN_SERIES_FOR_TAU
TAU_OWN, TAU_MEASURE, TAU_ALL = ST.TAU_OWN, ST.TAU_MEASURE, ST.TAU_ALL
NO_TAU = "no tau"
NO_CERTAIN_SD = "no certain SD"
TESTS = ("mean", "sd", "step", "sex")
CALIBRATED = ("mean", "sd", "step")
MALE, FEMALE = "male", "female"
RHO_CLIP = 0.999
RMS = "root mean square by measure, the measures' median"
MEDIAN = "median by measure, every item's median"
STEP_RULE = RMS
STEP_R_GRID = tuple(round(0.1 * i, 1) for i in range(10))
STEP_R_SENSITIVITY = (0.0, 0.5, 0.8)
STEP_R = 0.0                 # run_bounds.py's choice on STEP_R_GRID, bounds.json's step_r
BAR_LOW = 0.1                # the bar's low quantile of the held-out papers' rates
MIN_BAR_ROWS = 20            # a held-out paper's rows of a test for its rate to enter that test's bar
MIN_BAR_PAPERS = 5           # papers of MIN_BAR_ROWS rows a test's bar needs; fewer give the test no bar
REFERENCE_N = 40             # people a cell check() scores a cohort at (the docstring of check says why)
COVARIATES = {"sex": "sex_g", "age": "age_slope"}
COVARIATE_RULE = RMS


# ---- the kinds of population ---------------------------------------------------------------------

def specimen_of(paper: str, cohort: str, register: Dict[Tuple[str, str], RG.Population]) -> str:
    """The register's specimen of a cohort, or NOT_IN_REGISTER; never inferred from a modality."""
    p = register.get((paper, cohort))
    return p.specimen if p else NOT_IN_REGISTER


def kinds_present(series: Sequence[L.Series], register: Dict[Tuple[str, str], RG.Population]) -> List[str]:
    """ALL first, then every specimen a usable series' cohort carries, in alphabetical order."""
    found = {specimen_of(s.paper, s.cohort, register) for s in series if L.usable(s)}
    return [ALL] + sorted(k for k in found if k not in (NOT_IN_REGISTER, RG.NOT_STATED))


def series_of_kind(series: Sequence[L.Series], register: Dict[Tuple[str, str], RG.Population], kind: str) -> List[L.Series]:
    if kind == ALL:
        return [s for s in series if L.usable(s)]
    return [s for s in series if L.usable(s) and specimen_of(s.paper, s.cohort, register) == kind]


# ---- random effects under a given spread --------------------------------------------------------------

def under(y: Sequence[float], v: Sequence[float], tau: float) -> Tuple[float, float]:
    """The random-effects mean of estimates y with within variances v under the spread tau, and its SE."""
    y, v = np.asarray(y, float), np.asarray(v, float)
    w = 1.0 / (v + tau * tau)
    return float((w * y).sum() / w.sum()), float(math.sqrt(1.0 / w.sum()))


def spread(y: Sequence[float], v: Sequence[float], scale: float, measure: str,
           borrowed: Tuple[Dict[str, float], float]) -> Tuple[float, float, float, float, str]:
    """The centre, its SE, tau, the SD of a new population's value sqrt(tau^2 + SE^2), and where tau
    came from: the estimates' own REML tau from MIN_SERIES_FOR_TAU on, else the measure's typical tau
    over scale (typical_tau) times this scale, else every item's; as strata.between reads a cell's
    mean, the SE taken under the same tau, so one estimate widens by tau twice."""
    by_measure, overall = borrowed
    if len(y) >= MIN_SERIES_FOR_TAU:
        p = P.pool(y, v)
        tau, came = p.tau, TAU_OWN
    elif measure in by_measure:
        tau, came = by_measure[measure] * scale, TAU_MEASURE
    else:
        tau, came = overall * scale, TAU_ALL
    centre, se = under(y, v, tau)
    return centre, se, float(tau), float(math.sqrt(tau * tau + se * se)), came


def typical_tau(items: Iterable[Tuple[str, Sequence[float], Sequence[float], float]],
                rule: str = RMS) -> Tuple[Dict[str, float], float]:
    """What an item with fewer than MIN_SERIES_FOR_TAU estimates borrows, from the items (measure,
    estimates, variances, scale) with that many or more. Under RMS, by measure the root mean square
    of their REML tau over scale, over all the median of the measures' values, one vote a measure:
    not the median over items, as strata.median_f takes for the means, since REML puts a tau of
    exactly zero on many steps of three to nine papers (at r = 0, five of h_post's six, four of
    h_ant's six) and a median of such zeros would lend a one-paper step no spread at all, its
    interval its own sampling error; the mean of tau^2 keeps what the items with a spread say. And
    not the root mean square over all items, which one method-bound measure would set for every
    other (the pedicle's sagittal inclination, whose steps spread 0.55 to 2.22 SDs between papers,
    gradients.csv). Under MEDIAN, strata.median_f's rule, the median by measure and over every
    item, which run_bounds.py reads beside it."""
    by: Dict[str, List[float]] = {}
    for measure, y, v, scale in items:
        if len(y) >= MIN_SERIES_FOR_TAU and scale > 0:
            p = P.pool(y, v)
            if p is not None:
                by.setdefault(measure, []).append(p.tau / scale)
    return taus_by_rule(by, rule)


def taus_by_rule(by: Dict[str, List[float]], rule: str) -> Tuple[Dict[str, float], float]:
    """The donors' taus (by measure) summarised under a borrowing rule: under RMS each measure's
    root mean square and over all the median of the measures' values, under MEDIAN each measure's
    median and over all the median of every donor's."""
    if rule == MEDIAN:
        every = [t for x in by.values() for t in x]
        return {k: float(np.median(x)) for k, x in by.items()}, float(np.median(every)) if every else float("nan")
    per = {k: float(math.sqrt(np.mean(np.square(x)))) for k, x in by.items()}
    return per, float(np.median(list(per.values()))) if per else float("nan")


def t_interval(centre: float, se: float, tau: float, k: int) -> Tuple[float, float]:
    """Higgins's prediction interval on k - 2 degrees of freedom, from three estimates; NaN below."""
    if k < MIN_SERIES_FOR_TAU or not math.isfinite(tau):
        return float("nan"), float("nan")
    half = float(stats.t.ppf(0.975, k - 2)) * math.sqrt(tau * tau + se * se)
    return centre - half, centre + half


# ---- the mean and the SD of a cell -------------------------------------------------------------------

def mean_band(cell: ST.Cell, borrowed: Tuple[Dict[str, float], float]) -> dict:
    """The pooled mean and the interval for a new population's mean, z and, from three series, t."""
    pool = cell.pool
    between, came = ST.between(pool, borrowed, cell.measure)
    lo_t, hi_t = t_interval(pool.mean, pool.se, pool.tau, pool.k)
    return {"k": pool.k, "papers": pool.papers, "mean": pool.mean, "mean_se": pool.se, "mean_tau": pool.tau,
            "tau_from": came, "between": between, "mean_low": pool.mean - Z * between, "mean_high": pool.mean + Z * between,
            "mean_t_low": lo_t, "mean_t_high": hi_t}


def certain_sds(cell: ST.Cell) -> List[Tuple[float, float]]:
    """(SD, n) of every population whose SD is certain at the cell."""
    return [(st.sd, st.n) for st in cell.strata if math.isfinite(st.sd) and st.sd > 0 and st.n > 1]


def log_sd_terms(pairs: Sequence[Tuple[float, float]]) -> Tuple[np.ndarray, np.ndarray]:
    """Each log SD with its small-sample bias added back and its variance, as pooling.pool_log_sd."""
    sd = np.array([s for s, _ in pairs], float)
    n = np.array([m for _, m in pairs], float)
    v = 1.0 / (2.0 * (n - 1.0))
    return np.log(sd) + v, v


def sd_borrowed(cells: Sequence[ST.Cell]) -> Tuple[Dict[str, float], float]:
    """The typical tau of the log SD by measure and over all cells with three certain SDs or more."""
    return typical_tau((c.measure, *log_sd_terms(certain_sds(c)), 1.0) for c in cells if certain_sds(c))


def sd_band(cell: ST.Cell, borrowed: Tuple[Dict[str, float], float]) -> dict:
    """The printed SDs' range, the pooled SD, and the interval for a new population's SD on the log
    scale; NaN where no population's SD is certain (a cell of Tan 2004's alone)."""
    pairs = certain_sds(cell)
    out = {"sd": cell.pool.sd, "sd_from": cell.pool.sd_from, "sd_strata": len(pairs)}
    if not pairs:
        nan = float("nan")
        return dict(out, sd_min=nan, sd_median=nan, sd_max=nan, sd_centre=nan, sd_log_centre=nan, sd_log_between=nan,
                    sd_log_tau=nan, sd_tau_from=NO_CERTAIN_SD, sd_low=nan, sd_high=nan)
    y, v = log_sd_terms(pairs)
    centre, _, tau, between, came = spread(y, v, 1.0, cell.measure, borrowed)
    sds = [s for s, _ in pairs]
    return dict(out, sd_min=float(min(sds)), sd_median=float(np.median(sds)), sd_max=float(max(sds)),
                sd_centre=math.exp(centre), sd_log_centre=centre, sd_log_between=between, sd_log_tau=tau, sd_tau_from=came,
                sd_low=math.exp(centre - Z * between), sd_high=math.exp(centre + Z * between))


# ---- the covariates at a cell -------------------------------------------------------------------------

COVARIATE_UNITS = {"sex": "men minus women, within-sex SDs", "age": "within-band SDs per adult decade"}


def covariate_items(rows: Sequence[dict], vocabulary: Dict[str, dict],
                    sex_rows: Optional[Sequence[dict]] = None) -> Dict[str, list]:
    """The sex contrasts and the age gradients as run_covariates.py reads them: the contrasts from
    sex_rows, the full snapshot's rows with the sexes' snapshot's beside them
    (papers_table.load_rows_sexes, the rows covariates.sex_strata is written for; `rows` where none
    are given), and the gradients from the full snapshot's rows."""
    return {"sex": CV.sex_contrasts(rows if sex_rows is None else sex_rows, vocabulary),
            "age": CV.gradients(rows, vocabulary, "age")}


def covariate_effects(items: Dict[str, list], register: Dict[Tuple[str, str], RG.Population],
                      kind: str) -> Dict[Tuple[str, str], Dict[str, dict]]:
    """Per (base key, placed level), the sex contrast and the age slope pooled over the papers of the
    kind that print them: each item placed in the rule's column (papers_table.place) and read as
    covariates.by_paper_cell reads it, the strata of one set of people one value and the sets of
    different people combined by inverse variance, then the papers by REML (covariates.pooled),
    with the papers named and each paper's value kept (values) for the spread a new population's
    effect is read with."""
    out: Dict[Tuple[str, str], Dict[str, dict]] = {}
    for name, found in items.items():
        placed = []
        for it in found:
            if kind != ALL and specimen_of(it.paper, it.cohort, register) != kind:
                continue
            level = PT.place(it.base_key, it.level, it.paper)
            if level is not None:
                placed.append(replace(it, level=level))
        cells = CV.by_paper_cell(placed)
        for base, level in sorted({(b, lv) for _, b, lv in cells}):
            values = CV.paper_values(cells, base, level)
            got = CV.pooled(values)
            got["values"] = values
            got["papers_named"] = ";".join(sorted({p for p, b, lv in cells if b == base and lv == level}))
            got["strata"] = sum(n for (p, b, lv), (_, _, n) in cells.items() if b == base and lv == level)
            out.setdefault((base, level), {})[name] = got
    return out


def _donors(found: Sequence[Tuple[str, dict]]) -> Tuple[List[Tuple[str, dict]], str]:
    """The cells a covariate's spread is borrowed from: those with MIN_SERIES_FOR_TAU papers or more,
    else, where none has that many, those with two, the fewest REML reads a tau from."""
    for least in (MIN_SERIES_FOR_TAU, 2):
        got = [(b, g) for b, g in found if g["papers"] >= least and math.isfinite(g["tau"])]
        if got:
            return got, ("cells with %d papers or more" % least if least > 2
                         else "cells with two papers, since no cell has three")
    return [], "none: no cell has two papers"


def covariate_borrowed(effects: Dict[Tuple[str, str], Dict[str, dict]], rule: str = COVARIATE_RULE) -> Dict[str, dict]:
    """Per covariate, what a cell with fewer than MIN_SERIES_FOR_TAU papers borrows for the spread of a
    new population's effect, from the donor cells' REML taus (_donors), with which cells and papers
    they were and how many of their taus are exactly zero. Under COVARIATE_RULE, the steps' rule
    (RMS): by measure the root mean square, over all the median of the measures' values, since REML
    puts a tau of exactly zero on a donor whose few papers agree within their error, and a median
    of such zeros lends a one-paper effect no spread at all, so its interval for a new population is
    its own sampling error and its sign is tested where no paper beside it has said the sign holds;
    the rule the steps reject for that reason (typical_tau). Under MEDIAN, strata.median_f's rule,
    which run_bounds.py reads beside it. An effect is already in within-group SDs, so its tau is
    borrowed as it is, with no scale."""
    out = {}
    for name in COVARIATES:
        found = [(base, d[name]) for (base, _), d in sorted(effects.items()) if name in d]
        donors, which = _donors(found)
        by: Dict[str, List[float]] = {}
        for base, g in donors:
            by.setdefault(base, []).append(g["tau"])
        per, overall = taus_by_rule(by, rule)
        out[name] = {"by_measure": per, "overall": overall, "donors": which, "donor_cells": len(donors),
                     "donor_taus_of_zero": sum(1 for _, g in donors if g["tau"] == 0),
                     "donor_papers": sorted({p for _, g in donors for p in g["papers_named"].split(";")}),
                     "cells": len(found), "rule": rule}
    return out


def covariate_spread(got: dict, borrowed: dict, base: str) -> Tuple[float, str, float]:
    """The tau a new population's effect is read with, where it came from, and the SD of that
    effect, sqrt(tau^2 + SE^2) with the SE under the same tau, so one paper's effect widens by tau
    twice, as strata.between widens a one-series mean."""
    if got["papers"] >= MIN_SERIES_FOR_TAU and math.isfinite(got["tau"]):
        tau, came = got["tau"], TAU_OWN
    elif base in borrowed["by_measure"]:
        tau, came = borrowed["by_measure"][base], TAU_MEASURE
    elif math.isfinite(borrowed["overall"]):
        tau, came = borrowed["overall"], TAU_ALL
    else:
        return float("nan"), NO_TAU, float("nan")
    values = list(got["values"].values())
    _, se = under([e for e, _ in values], [v for _, v in values], tau)
    return float(tau), came, float(math.sqrt(tau * tau + se * se))


def covariate_columns(effects: Dict[str, dict], borrowed: Dict[str, dict], base: str) -> dict:
    out = {}
    for name, prefix in COVARIATES.items():
        got = effects.get(name)
        keys = ("mean", "se", "ci_low", "ci_high", "tau", "pi_low", "pi_high", "papers", "papers_named")
        names = ("", "_se", "_low", "_high", "_tau", "_pi_low", "_pi_high", "_papers", "_papers_named")
        for k, suffix in zip(keys, names):
            out[prefix + suffix] = got.get(k) if got else (float("nan") if k not in ("papers", "papers_named") else "")
        tau, came, between = covariate_spread(got, borrowed[name], base) if got else (float("nan"), "", float("nan"))
        centre = got["mean"] if got else float("nan")
        out.update({prefix + "_tau_used": tau, prefix + "_tau_from": came, prefix + "_between": between,
                    prefix + "_new_low": centre - Z * between, prefix + "_new_high": centre + Z * between})
    return out


def clear_of_zero(row: dict, prefix: str, low: str = "_new_low", high: str = "_new_high") -> bool:
    """Whether a covariate's interval (by default the one for a new population) excludes zero."""
    lo, hi = row.get(prefix + low, float("nan")), row.get(prefix + high, float("nan"))
    return bool(math.isfinite(lo) and math.isfinite(hi) and (lo > 0 or hi < 0))


def held_out_signs(items: Dict[str, list], register: Dict[Tuple[str, str], RG.Population],
                   rule: str = COVARIATE_RULE, name: str = "sex") -> List[dict]:
    """Every paper with a covariate effect left out in turn: the effects of every paper together
    read from the other papers alone, their spreads borrowed under `rule` from the other papers'
    donor cells, and at each cell where the interval for a new population's effect clears zero
    there, whether the left-out paper's own effect (its strata at the cell as covariate_effects
    reads them) has the sign, as check() tests a cohort's. A record of how the sign test holds on
    real populations held out under either borrowing rule; the test carries no bar."""
    prefix = COVARIATES[name]
    out = []
    for paper in sorted({it.paper for it in items[name]}):
        rest = covariate_effects({name: [it for it in items[name] if it.paper != paper]}, register, ALL)
        own = covariate_effects({name: [it for it in items[name] if it.paper == paper]}, register, ALL)
        borrowed = covariate_borrowed(rest, rule)
        for (base, level), d in sorted(own.items()):
            other = rest.get((base, level), {}).get(name)
            if other is None:
                continue
            row = covariate_columns({name: other}, borrowed, base)
            if not clear_of_zero(row, prefix):
                continue
            g = d[name]["mean"]
            out.append({"paper": paper, "base_key": base, "level": level, "rule": rule, "own": g, "card": other["mean"],
                        "tau_from": row[prefix + "_tau_from"], "passed": bool(np.sign(g) == np.sign(other["mean"]))})
    return out


# ---- the gradients --------------------------------------------------------------------------------------

@dataclass
class StepEstimate:
    """One measure's step from one level to the next, as each paper that prints both levels gives it."""
    measure: str
    base_key: str
    upper: str
    lower: str
    papers: List[str]
    steps: List[float]
    variances: List[float]
    scale: float                 # the two cells' mean pooled SD, the unit a borrowed tau is read in
    mean_difference: float       # the lower cell's pooled mean minus the upper's, over their own papers
    skipped: List[str] = field(default_factory=list)   # papers printing both levels with other cohorts at each
    r: float = 0.0               # the within-person correlation the variances were read under


def _cohorts(st: ST.Stratum) -> Tuple[str, ...]:
    return tuple(sorted({s.cohort for s in st.series}))


def _sd_or_pool(st: ST.Stratum, cell: ST.Cell) -> float:
    return st.sd if math.isfinite(st.sd) and st.sd > 0 else cell.pool.sd


def step_variance(sd_a: float, n_a: float, sd_b: float, n_b: float, r: float) -> float:
    """The sampling variance of a step, the lower level's mean less the upper's over the same cohorts:
    each mean's sd^2 / n, less twice their covariance r sd_a sd_b / max(n_a, n_b), the people of the
    smaller count taken to be among the larger's (a person measured at one level and not the other
    shares nothing), r the correlation of one person's two levels."""
    return sd_a * sd_a / n_a + sd_b * sd_b / n_b - 2.0 * r * sd_a * sd_b / max(n_a, n_b)


def step_estimates(cells: Sequence[ST.Cell], r: Optional[float] = None) -> List[StepEstimate]:
    """Every adjacent pair of levels down the column (C3 to L5) at which a measure has two cells, with
    each paper's own step where it prints the same cohorts at both levels, its variance under the
    within-person correlation r (STEP_R unless given)."""
    r = STEP_R if r is None else r
    by = ST.cells_by_key(cells)
    out = []
    for measure in sorted({c.measure for c in cells}):
        for upper, lower in zip(LEVELS, LEVELS[1:]):
            ca, cb = by.get((measure, upper)), by.get((measure, lower))
            if ca is None or cb is None:
                continue
            papers, steps, variances, skipped = [], [], [], []
            for paper in sorted(set(ca.papers) & set(cb.papers)):
                sa, sb = ca.stratum(paper), cb.stratum(paper)
                if _cohorts(sa) != _cohorts(sb):
                    skipped.append(paper)
                    continue
                papers.append(paper)
                steps.append(sb.mean - sa.mean)
                variances.append(step_variance(_sd_or_pool(sa, ca), sa.n, _sd_or_pool(sb, cb), sb.n, r))
            out.append(StepEstimate(measure=measure, base_key=ca.base_key, upper=upper, lower=lower, papers=papers,
                                    steps=steps, variances=variances, scale=0.5 * (ca.pool.sd + cb.pool.sd),
                                    mean_difference=cb.pool.mean - ca.pool.mean, skipped=skipped, r=r))
    return out


def step_borrowed(estimates: Iterable[StepEstimate], rule: str = STEP_RULE) -> Tuple[Dict[str, float], float]:
    return typical_tau(((e.measure, e.steps, e.variances, e.scale) for e in estimates if e.steps), rule)


def step_row(kind: str, e: StepEstimate, borrowed: Tuple[Dict[str, float], float]) -> Optional[dict]:
    """The pooled step and the interval for a new population's step; None where no paper gives one."""
    if not e.steps:
        return None
    centre, se, tau, between, came = spread(e.steps, e.variances, e.scale, e.measure, borrowed)
    lo_t, hi_t = t_interval(centre, se, tau if came == TAU_OWN else float("nan"), len(e.steps))
    return {"kind": kind, "measure": e.measure, "base_key": e.base_key, "upper": e.upper, "lower": e.lower,
            "k": len(e.steps), "papers": ";".join(e.papers), "step": centre, "step_se": se, "step_tau": tau,
            "tau_from": came, "between": between, "step_low": centre - Z * between, "step_high": centre + Z * between,
            "step_t_low": lo_t, "step_t_high": hi_t, "sd": e.scale,
            "step_over_sd": centre / e.scale if e.scale > 0 else float("nan"),
            "half_width_over_sd": Z * between / e.scale if e.scale > 0 else float("nan"),
            "mean_difference": e.mean_difference,
            "coherence": (e.mean_difference - centre) / between if between > 0 else float("nan"),
            "within_r": e.r,
            "paper_steps": ";".join("%s=%.6g" % (p, s) for p, s in zip(e.papers, e.steps)),
            "papers_skipped": ";".join(e.skipped)}


# ---- the card -------------------------------------------------------------------------------------------

@dataclass
class Card:
    """The bounds: one row a (kind, measure, level) and one a (kind, measure, upper, lower) step, the
    spreads borrowed, and per kind the calibrated bar of that kind's held-out papers (bar_of, keyed
    by kind; empty for a card no calibration was read for)."""
    cells: List[dict]
    steps: List[dict]
    borrowed: dict = field(default_factory=dict)
    calibration: Dict[str, dict] = field(default_factory=dict)

    def __post_init__(self):
        self._cells = {(r["kind"], r["measure"], r["level"]): r for r in self.cells}
        self._steps = {(r["kind"], r["measure"], r["upper"], r["lower"]): r for r in self.steps}

    def bar(self, kind: str) -> Optional[dict]:
        return self.calibration.get(kind)

    def cell(self, kind: str, measure: str, level: str) -> Optional[dict]:
        return self._cells.get((kind, measure, level))

    def step(self, kind: str, measure: str, upper: str, lower: str) -> Optional[dict]:
        return self._steps.get((kind, measure, upper, lower))

    def of_kind(self, kind: str) -> Tuple[List[dict], List[dict]]:
        return [r for r in self.cells if r["kind"] == kind], [r for r in self.steps if r["kind"] == kind]


def cell_row(kind: str, cell: ST.Cell, borrowed_mean, borrowed_sd, effects: Dict[str, dict], borrowed_cov) -> dict:
    row = {"kind": kind, "measure": cell.measure, "base_key": cell.base_key, "level": cell.level, "modality": cell.modality,
           "strata_list": ";".join(cell.papers)}
    row.update(mean_band(cell, borrowed_mean))
    row.update(sd_band(cell, borrowed_sd))
    sd = cell.pool.sd
    row["predictive_sd"] = ST.predictive_sd(sd, row["between"])
    row["half_width_over_sd"] = Z * row["between"] / sd if sd > 0 else float("nan")
    row["predictive_over_sd"] = row["predictive_sd"] / sd if sd > 0 else float("nan")
    row.update(covariate_columns(effects, borrowed_cov, cell.base_key))
    return row


def build(series: Sequence[L.Series], rows: Sequence[dict], vocabulary: Dict[str, dict],
          register: Dict[Tuple[str, str], RG.Population], r: Optional[float] = None, step_rule: str = STEP_RULE,
          kinds: Optional[Sequence[str]] = None, sex_rows: Optional[Sequence[dict]] = None,
          covariate_rule: str = COVARIATE_RULE) -> Card:
    """The card over every kind (or the kinds given), every spread a kind's cell or step cannot read
    of its own borrowed from every paper's cells and steps, so no kind is held tighter than the
    papers together allow; the steps' variances under the within-person correlation r (STEP_R
    unless given) and their borrowing under step_rule; the sex contrasts read from sex_rows
    (covariate_items) and the covariates' spreads borrowed under covariate_rule."""
    every = ST.strata_of(series_of_kind(series, register, ALL))
    borrowed_mean, borrowed_sd = ST.median_f(every), sd_borrowed(every)
    every_steps = step_estimates(every, r)
    borrowed_step = step_borrowed(every_steps, step_rule)
    items = covariate_items(rows, vocabulary, sex_rows)
    effects_all = covariate_effects(items, register, ALL)
    borrowed_cov = covariate_borrowed(effects_all, covariate_rule)
    cells, steps = [], []
    for kind in (kinds_present(series, register) if kinds is None else kinds):
        mine = every if kind == ALL else ST.strata_of(series_of_kind(series, register, kind))
        effects = effects_all if kind == ALL else covariate_effects(items, register, kind)
        cells += [cell_row(kind, c, borrowed_mean, borrowed_sd, effects.get((c.base_key, c.level), {}), borrowed_cov)
                  for c in mine]
        for e in (every_steps if kind == ALL else step_estimates(mine, r)):
            got = step_row(kind, e, borrowed_step)
            if got is not None:
                steps.append(got)
    return Card(cells=cells, steps=steps, borrowed={
        "mean_tau_over_sd": {"by_measure": borrowed_mean[0], "overall": borrowed_mean[1],
                             "rule": MEDIAN + ", strata.median_f, over the cells with three series or more"},
        "log_sd_tau": {"by_measure": borrowed_sd[0], "overall": borrowed_sd[1], "rule": RMS},
        "step_tau_over_sd": {"by_measure": borrowed_step[0], "overall": borrowed_step[1], "rule": step_rule,
                             "within_r": STEP_R if r is None else r},
        "sex_g_tau": borrowed_cov["sex"], "age_slope_tau": borrowed_cov["age"]})


# ---- reading a written card back -----------------------------------------------------------------------

TEXT_COLUMNS = {"kind", "measure", "base_key", "level", "upper", "lower", "modality", "strata_list", "sd_from", "tau_from",
                "sd_tau_from", "papers", "paper_steps", "papers_skipped", "sex_g_papers_named", "age_slope_papers_named",
                "sex_g_tau_from", "age_slope_tau_from"}


def _value(key: str, text: str):
    if key in TEXT_COLUMNS:
        return text
    if text == "":
        return float("nan")
    try:
        return float(text)
    except ValueError:
        return text


def load(folder: str) -> Card:
    """The card from bounds.csv and gradients.csv as run_bounds.py writes them, with each kind's
    calibrated bar from calibration.csv where it is there (a row with no kind is every paper's), so
    a generator elsewhere reads the bounds without the papers' rows."""
    def read(name):
        with open(os.path.join(folder, name), encoding="ascii", newline="") as fh:
            return [{k: _value(k, v) for k, v in r.items()} for r in csv.DictReader(fh)]
    cells, steps = read("bounds.csv"), read("gradients.csv")
    for r in cells + steps:
        if "k" in r and isinstance(r["k"], float) and math.isfinite(r["k"]):
            r["k"] = int(r["k"])
    by_kind: Dict[str, List[dict]] = {}
    if os.path.exists(os.path.join(folder, "calibration.csv")):
        for r in read("calibration.csv"):
            by_kind.setdefault(r.get("kind") or ALL, []).append(dict(r, made=int(r["made"]), passed=int(r["passed"])))
    return Card(cells=cells, steps=steps, calibration={k: bar_of(v) for k, v in by_kind.items()})


# ---- a generated cohort ------------------------------------------------------------------------------------

@dataclass
class Cohort:
    """A cohort as columns: one entry a person, measure and level, its value, and optional sex and person."""
    measure: np.ndarray
    level: np.ndarray
    value: np.ndarray
    sex: Optional[np.ndarray] = None
    person: Optional[np.ndarray] = None

    @classmethod
    def of(cls, rows) -> "Cohort":
        """From a Cohort, a dict of columns, or rows as dicts with measure, level, value and maybe sex
        and person."""
        if isinstance(rows, Cohort):
            return rows
        if isinstance(rows, dict):
            cols = rows
        else:
            rows = list(rows)
            cols = {k: [r.get(k) for r in rows] for k in ("measure", "level", "value", "sex", "person")}
        def col(k, dtype=object):
            got = cols.get(k)
            if got is None or all(x is None for x in got):
                return None
            return np.asarray(got, dtype=dtype)
        return cls(measure=np.asarray(cols["measure"], dtype=object), level=np.asarray(cols["level"], dtype=object),
                   value=np.asarray(cols["value"], dtype=float), sex=col("sex"), person=col("person"))

    def groups(self) -> Dict[Tuple[str, str], np.ndarray]:
        """The entries of each (measure, level) whose value is finite, read once a cohort: the
        measures and the levels are coded apart and the pair grouped by its integer code, since a
        string a row would cost seconds on a generator's millions of entries."""
        cached = getattr(self, "_groups", None)
        if cached is not None:
            return cached
        out: Dict[Tuple[str, str], np.ndarray] = {}
        idx = np.flatnonzero(np.isfinite(self.value))
        if len(idx):
            measures, m_code = np.unique(self.measure[idx], return_inverse=True)
            levels, l_code = np.unique(self.level[idx], return_inverse=True)
            code = m_code.astype(np.int64) * len(levels) + l_code
            order = np.argsort(code, kind="stable")
            uniq, starts = np.unique(code[order], return_index=True)
            ends = np.append(starts[1:], len(order))
            for c, a, b in zip(uniq, starts, ends):
                out[str(measures[c // len(levels)]), str(levels[c % len(levels)])] = idx[order[a:b]]
        self._groups = out
        return out


def hedges_g(men: np.ndarray, women: np.ndarray) -> Tuple[float, float]:
    """Men minus women over the pooled within-sex SD, small-sample corrected, and its variance."""
    c = CV.Contrast("", "", "", "", "", float(men.mean()), float(men.std(ddof=1)), float(len(men)),
                    float(women.mean()), float(women.std(ddof=1)), float(len(women)))
    return c.g, c.var_g


def _verdict(test: str, distance: float, half: float) -> dict:
    """A test's z-score (the distance over its spread) and whether it lies inside the interval."""
    sd = half / Z
    return {"test": test, "z": distance / sd if sd > 0 else float("nan"), "passed": bool(abs(distance) <= half)}


def mean_verdict(c: dict, n: float, mean: float, sd: float, sampling: bool = True, interval: str = "z") -> dict:
    """A population's mean (n people, their SD) against a card cell's interval for a new population's
    mean, z, or t where the cell has three series, widened by the sampling error of n people."""
    between = c["between"]
    if interval == "t" and math.isfinite(c.get("mean_t_low", float("nan"))):
        between = (c["mean_t_high"] - c["mean"]) / Z
    return _verdict("mean", mean - c["mean"], Z * math.sqrt(between ** 2 + (sd * sd / n if sampling else 0.0)))


def sd_verdict(c: dict, n: float, sd: float, sampling: bool = True, at: Optional[float] = None) -> Optional[dict]:
    """A population's SD against the card cell's interval for a new population's SD, on the log
    scale with the small-sample bias of its n people added back and the interval widened by the
    sampling error of `at` people (n where not given); None where the cell has no SD interval or the
    population fewer than three people."""
    if not (math.isfinite(c["sd_log_centre"]) and n >= 3 and sd > 0):
        return None
    at = n if at is None else at
    log_sd = math.log(sd) + 1.0 / (2.0 * (n - 1))
    half = Z * math.sqrt(c["sd_log_between"] ** 2 + (1.0 / (2.0 * (at - 1)) if sampling else 0.0))
    return _verdict("sd", log_sd - c["sd_log_centre"], half)


def step_verdict(s: dict, step: float, var: float, sampling: bool = True, interval: str = "z") -> dict:
    """A population's step (with its sampling variance) against the card's interval for a new
    population's step, z, or t where the step has three papers."""
    between = s["between"]
    if interval == "t" and math.isfinite(s.get("step_t_low", float("nan"))):
        between = (s["step_t_high"] - s["step"]) / Z
    return _verdict("step", step - s["step"], Z * math.sqrt(between ** 2 + (var if sampling else 0.0)))


def check(rows, card: Card, kind: str = ALL, sampling: bool = True, interval: str = "z",
          reference_n: Optional[float] = REFERENCE_N) -> dict:
    """Score a generated cohort against the card of one kind of population.

    Per cell the cohort has values at (two or more): its mean against the interval for a new
    population's mean (interval "z", or "t" for Higgins's where the cell has three series, z
    elsewhere), its SD against the interval for a new population's SD, each widened by the cohort's
    own sampling error unless `sampling` is off; per step of the card both of whose levels the
    cohort has, its step against the gradient's interval, the sampling error taken from the people
    present at both levels where person ids are given and from the two levels apart otherwise; and
    where sexes are given and the interval for a new population's contrast at the cell is clear of
    zero, whether the cohort's contrast has its sign (and, for the record only, whether it lies in
    that interval widened by the cohort's own error). The summary gives each test's count and pass
    rate, the pass rate over every test (a record that decides nothing), the mean square of the
    z-scores, and the verdict (verdict): each calibrated test against the bar of the kind's own
    held-out papers, and the cohort's, which fails where the step test fails its bar.

    The bar is the rate of real papers scored with their own few people, whose sampling error widens
    every interval, so a cohort's rate rises as it shrinks: a flattened lumbar gradient passes with
    six to ten people and a population the card itself draws fails the step bar at a few hundred.
    So each cell is scored as if the cohort had reference_n people, about the median of the bar
    papers' own median people a cell (bounds.json's reference_n_measured), and a cell where the
    cohort has fewer is left out and counted (short_cells); reference_n None scores each cell at the
    cohort's own count, for the record. A measure of the cohort the card does not hold is scored on
    nothing and named in measures_not_on_card, and the verdict's why says so, so a
    cohort keyed by other names than the card's (pedicle_w:mean for the card's pedicle) is not
    passed over in silence, whether the cohort's other measures give a verdict or none."""
    cohort = Cohort.of(rows)
    cells, steps = card.of_kind(kind)
    groups = cohort.groups()
    not_on_card = sorted({m for m, _ in groups} - {c["measure"] for c in cells})
    out_cells, out_steps, verdicts = [], [], []
    moments: Dict[Tuple[str, str], Tuple[int, float, float]] = {}
    short = 0
    for c in cells:
        idx = groups.get((c["measure"], c["level"]))
        if idx is None or len(idx) < 2:
            continue
        if reference_n is not None and len(idx) < reference_n:
            short += 1
            continue
        x = cohort.value[idx]
        n, mean, sd = len(x), float(x.mean()), float(x.std(ddof=1))
        at = n if reference_n is None else reference_n
        moments[c["measure"], c["level"]] = (n, mean, sd)
        row = {"measure": c["measure"], "level": c["level"], "n": n, "mean": mean, "sd": sd, "card_mean": c["mean"],
               "mean_low": c["mean_low"], "mean_high": c["mean_high"], "card_sd_low": c["sd_low"], "card_sd_high": c["sd_high"]}
        v = mean_verdict(c, at, mean, sd, sampling, interval)
        row.update(mean_z=v["z"], mean_pass=v["passed"])
        verdicts.append(v)
        v = sd_verdict(c, n, sd, sampling, at)
        if v is not None:
            row.update(sd_z=v["z"], sd_pass=v["passed"])
            verdicts.append(v)
        if cohort.sex is not None and math.isfinite(c.get("sex_g", float("nan"))):
            got = _sex_test(cohort, idx, c, sampling)
            if got is not None:
                row.update(got[0])
                verdicts.append(got[1])
        out_cells.append(row)
    for s in steps:
        a, b = moments.get((s["measure"], s["upper"])), moments.get((s["measure"], s["lower"]))
        if a is None or b is None:
            continue
        step = b[1] - a[1]
        var = _step_sampling(cohort, groups[s["measure"], s["upper"]], groups[s["measure"], s["lower"]], a, b, reference_n)
        v = step_verdict(s, step, var, sampling, interval)
        out_steps.append({"measure": s["measure"], "upper": s["upper"], "lower": s["lower"], "step": step,
                          "card_step": s["step"], "step_low": s["step_low"], "step_high": s["step_high"],
                          "step_z": v["z"], "step_pass": v["passed"]})
        verdicts.append(v)
    summary = summarise(verdicts, card.bar(kind), bool(card.calibration))
    summary.update(reference_n=reference_n, short_cells=short, measures_not_on_card=not_on_card)
    if short and summary["verdict"]["passed"] is None:
        summary["verdict"]["why"] += "; %d cells had fewer people than the %s a cell is scored at" % (short, reference_n)
    if not_on_card:
        summary["verdict"]["why"] += "; %d of the cohort's measures are not on the card: %s" % (
            len(not_on_card), ", ".join(not_on_card[:5]) + (", ..." if len(not_on_card) > 5 else ""))
    return {"kind": kind, "cells": out_cells, "steps": out_steps, "summary": summary}


def _sex_test(cohort: Cohort, idx: np.ndarray, c: dict, sampling: bool) -> Optional[Tuple[dict, dict]]:
    """The sign of the cohort's sex contrast at a cell whose interval for a new population's contrast
    is clear of zero; None where it is not, or the cohort has fewer than two of either sex there."""
    sex = cohort.sex[idx]
    x = cohort.value[idx]
    men, women = x[sex == MALE], x[sex == FEMALE]
    if len(men) < 2 or len(women) < 2 or not clear_of_zero(c, "sex_g"):
        return None
    g, var_g = hedges_g(men, women)
    inside = abs(g - c["sex_g"]) <= Z * math.sqrt(c["sex_g_between"] ** 2 + (var_g if sampling else 0.0))
    passed = bool(np.sign(g) == np.sign(c["sex_g"]))
    z = g / math.sqrt(var_g) if var_g > 0 else float("nan")
    return ({"sex_g": g, "card_sex_g": c["sex_g"], "sex_pass": passed, "sex_inside": bool(inside)},
            {"test": "sex", "z": z, "passed": passed})


def _step_sampling(cohort: Cohort, ia: np.ndarray, ib: np.ndarray, a: tuple, b: tuple,
                   at: Optional[float] = None) -> float:
    """The sampling variance of the cohort's step with `at` people (its own where not given): from
    the persons at both levels where ids are given and at least two persons pair, else from the two
    levels' own variances."""
    if cohort.person is not None:
        _, ja, jb = np.intersect1d(cohort.person[ia], cohort.person[ib], return_indices=True)
        if len(ja) >= 2:
            d = cohort.value[ib[jb]] - cohort.value[ia[ja]]
            return float(d.var(ddof=1) / (len(d) if at is None else at))
    return a[2] ** 2 / (a[0] if at is None else at) + b[2] ** 2 / (b[0] if at is None else at)


def _mean_square(verdicts: Sequence[dict]) -> float:
    z = np.array([v["z"] for v in verdicts if v["test"] != "sex" and math.isfinite(v["z"])])
    return float((z ** 2).mean()) if len(z) else float("nan")


def summarise(verdicts: Sequence[dict], bar: Optional[dict] = None, calibrated: Optional[bool] = None) -> dict:
    """Each test's count and pass rate, all of them together, the mean square of the z-scores over
    all and by test (the sex test's sign carries none), and the verdict against the kind's bar."""
    out = {"nominal": NOMINAL, "tests": {}, "mean_square_z_by_test": {}}
    for test in TESTS:
        mine = [v for v in verdicts if v["test"] == test]
        if mine:
            out["tests"][test] = {"made": len(mine), "passed": sum(v["passed"] for v in mine),
                                  "rate": sum(v["passed"] for v in mine) / len(mine)}
            if test != "sex":
                out["mean_square_z_by_test"][test] = _mean_square(mine)
    out["made"] = len(verdicts)
    out["passed"] = sum(v["passed"] for v in verdicts)
    out["rate"] = out["passed"] / len(verdicts) if verdicts else float("nan")
    out["mean_square_z"] = _mean_square(verdicts)
    out["verdict"] = verdict(out["tests"], bar, bool(bar) if calibrated is None else calibrated)
    return out


UNCALIBRATED = "the card carries no held-out calibration"
TOO_FEW = "no bar: fewer than %d of the kind's held-out papers have %d rows or more of this test (calibration)"


def _test_verdict(got: dict, b: Optional[dict], calibrated: bool) -> dict:
    row = {"made": got["made"], "rate": got["rate"]}
    if b is not None and "low" in b:
        return dict(row, low=b["low"], median=b["median"], papers=b["papers"], passed=bool(got["rate"] >= b["low"]),
                    at_or_above_median=bool(got["rate"] >= b["median"]))
    if not calibrated:
        return dict(row, passed=None, nominal=NOMINAL, at_or_above_nominal=bool(got["rate"] >= NOMINAL), why=UNCALIBRATED)
    return dict(row, passed=None, papers=b["papers"] if b else 0, why=TOO_FEW % (MIN_BAR_PAPERS, MIN_BAR_ROWS))


def verdict(tests: Dict[str, dict], bar: Optional[dict], calibrated: bool = True) -> dict:
    """Each calibrated test against its bar (bar_of), and the cohort's verdict.

    A test passes where its pass rate is at or above the bar's low quantile, the 10th percentile of
    the rates real populations held out score on a card of the rest, so about one real population
    in ten fails it; the median is beside it. A generated cohort is one population, so the bar is a
    population's rate, never the rate pooled over every paper's rows. The cohort fails where any
    test with a bar fails, and passes only where the step test was made and passes its bar, since
    naming lives on the steps; the pass rate over the three tests together decides nothing, since
    a broken gradient keeps it high (the flattened lumbar spine's, bounds.json's checks). A test
    with no bar (fewer than MIN_BAR_PAPERS of the kind's held-out papers with MIN_BAR_ROWS rows of
    it, or a card with no calibration, where the nominal stands beside it for the record) has no
    verdict and says why, and the sex test has none, since no held-out paper is scored on it."""
    out = {"bar": ("the %.0fth percentile of the kind's held-out papers' own rates, one paper one vote, over the "
                   "papers with %d rows or more of the test (bar_of), the median beside it"
                   % (100 * BAR_LOW, MIN_BAR_ROWS)) if calibrated else UNCALIBRATED,
           "tests": {t: _test_verdict(tests[t], (bar or {}).get(t), calibrated) for t in CALIBRATED if t in tests}}
    failed = [t for t, v in out["tests"].items() if v["passed"] is False]
    unjudged = [t for t, v in out["tests"].items() if v["passed"] is None]
    step = out["tests"].get("step")
    if failed:
        passed, why = False, "fails its bar on: " + ", ".join(failed)
    elif step is None:
        passed, why = None, "no step scored: naming lives on the steps, so no cohort passes without them"
    elif step["passed"] is None:
        passed, why = None, "the step test has no verdict: " + step["why"]
    else:
        passed, why = True, "the step test and every test with a bar at or above its bar"
        if unjudged:
            why += "; no verdict on: " + ", ".join(unjudged)
    out.update(passed=passed, why=why)
    return out


# ---- the calibration on real populations held out -----------------------------------------------------------

def _held_out_cells(every: Sequence[ST.Cell], rest: Sequence[ST.Cell], paper: str, sampling: bool,
                    rest_all: Optional[Sequence[ST.Cell]] = None) -> List[dict]:
    """The left-out paper's own mean and SD at every cell the rest also print, each scored on the
    rest's card cell, its spreads borrowed from rest_all (every other paper's cells, as build
    borrows a kind's; the rest itself where not given): its mean widened by its own sd^2 / n (its SD
    where certain, else the rest's pooled SD), its SD where certain."""
    donors = rest if rest_all is None else rest_all
    borrowed_mean, borrowed_sd = ST.median_f(donors), sd_borrowed(donors)
    theirs = ST.cells_by_key(rest)
    out = []
    for c in every:
        own, other = c.stratum(paper), theirs.get((c.measure, c.level))
        if own is None or other is None:
            continue
        row = dict(mean_band(other, borrowed_mean), **sd_band(other, borrowed_sd))
        certain = math.isfinite(own.sd) and own.sd > 0
        where = {"measure": c.measure, "level": c.level}
        mean = mean_verdict(row, own.n, own.mean, own.sd if certain else other.pool.sd, sampling)
        out.append(dict(mean, tau_from=row["tau_from"], **where))
        v = sd_verdict(row, own.n, own.sd, sampling) if certain else None
        if v is not None:
            out.append(dict(v, tau_from=row["sd_tau_from"], **where))
    return out


def _held_out_steps(own: Sequence[StepEstimate], rest: Sequence[StepEstimate], borrowed, paper: str,
                    sampling: bool) -> List[dict]:
    """The left-out paper's own steps at every step the rest also print, each scored on the rest's
    step widened by the paper's own step variance."""
    theirs = {(e.measure, e.upper, e.lower): e for e in rest}
    out = []
    for e in own:
        other = theirs.get((e.measure, e.upper, e.lower))
        if paper not in e.papers or other is None:
            continue
        row = step_row(ALL, other, borrowed)
        if row is None:
            continue
        i = e.papers.index(paper)
        out.append(dict(step_verdict(row, e.steps[i], e.variances[i], sampling), measure=e.measure, upper=e.upper,
                        lower=e.lower, tau_from=row["tau_from"]))
    return out


def readings(rs: Sequence[float], rules: Sequence[str], test_rs: Optional[Sequence[float]] = None) -> List[tuple]:
    """The (card's r, left-out paper's r, borrowing rule) a held-out step is read under: each r for
    both sides unless the left-out paper's own step variances are read at test_rs instead."""
    return [(r, r if test_rs is None else t, rule) for r in rs for t in (test_rs or (r,)) for rule in rules]


def held_out_verdicts(series: Sequence[L.Series], register: Dict[Tuple[str, str], RG.Population],
                      under_readings: Sequence[tuple] = ((STEP_R, STEP_R, STEP_RULE),),
                      sampling: bool = True, kind: str = ALL) -> List[dict]:
    """Every paper of the kind left out in turn: the kind's card built from the rest alone, as
    build builds it (the kind's pools and steps from the kind's other papers, the spreads they
    cannot read of their own borrowed from every other paper's cells and steps, so nothing of the
    left-out paper is in the card it is scored on), and the left-out paper's own strata of the kind
    scored on it, as check() scores a cohort. For every paper together the kind's card is the card
    of every paper. One verdict a test, with the kind, the paper and the card row's tau source; a
    step's under each reading (readings): the card's within-person correlation r, the one the
    left-out paper's own step variance is read at (test_r; the same r but where a reading sets the
    two apart, since a smaller r widens the paper's own error as well as the card's spread, and
    coverage alone cannot tell a right r from a lenient one), and the borrowing rule. The means and
    SDs depend on none of these and carry None."""
    usable = series_of_kind(series, register, ALL)
    mine = usable if kind == ALL else series_of_kind(series, register, kind)
    every = ST.strata_of(mine)
    own_steps = {t: step_estimates(every, t) for _, t, _ in under_readings}
    out = []
    for paper in sorted({s.paper for s in mine}):
        rest_all = ST.strata_of([s for s in usable if s.paper != paper])
        rest = rest_all if kind == ALL else ST.strata_of([s for s in mine if s.paper != paper])
        where = {"kind": kind, "paper": paper}
        out += [dict(v, r=None, test_r=None, rule=None, **where) for v in _held_out_cells(every, rest, paper, sampling, rest_all)]
        theirs_all: Dict[float, List[StepEstimate]] = {}
        theirs: Dict[float, List[StepEstimate]] = {}
        borrowed: Dict[tuple, tuple] = {}
        for r, t, rule in under_readings:
            if r not in theirs:
                theirs_all[r] = step_estimates(rest_all, r)
                theirs[r] = theirs_all[r] if kind == ALL else step_estimates(rest, r)
            if (r, rule) not in borrowed:
                borrowed[r, rule] = step_borrowed(theirs_all[r], rule)
            got = _held_out_steps(own_steps[t], theirs[r], borrowed[r, rule], paper, sampling)
            out += [dict(v, r=r, test_r=t, rule=rule, **where) for v in got]
    return out


def matching(verdicts: Iterable[dict], **keys) -> List[dict]:
    """The verdicts whose every named field has the value given."""
    return [v for v in verdicts if all(v.get(k) == x for k, x in keys.items())]


def of_reading(verdicts: Iterable[dict], r: float, rule: str) -> List[dict]:
    """The verdicts of one reading: every mean and SD, and the steps read under r on both sides and rule."""
    verdicts = list(verdicts)
    return [v for v in verdicts if v["test"] != "step"] + matching(verdicts, test="step", r=r, test_r=r, rule=rule)


def coverage(verdicts: Iterable[dict]) -> dict:
    """Held-out verdicts pooled over every paper: how many, how many passed, the rate."""
    verdicts = list(verdicts)
    passed = sum(v["passed"] for v in verdicts)
    return {"made": len(verdicts), "passed": passed, "rate": passed / len(verdicts) if verdicts else float("nan")}


def per_paper(verdicts: Iterable[dict], r: float, rule: str) -> List[dict]:
    """One row a kind of card, held-out paper and test (mean, sd, step, and the three together,
    all): how many it made, passed, its rate and the mean square of its z-scores; a paper none of
    whose cells the rest print has no row."""
    mine = of_reading(verdicts, r, rule)
    by: Dict[Tuple[str, str], List[dict]] = {}
    for v in mine:
        by.setdefault((v.get("kind", ALL), v["paper"]), []).append(v)
    out = []
    for kind, paper in sorted(by):
        for test in CALIBRATED + (ALL,):
            got = by[kind, paper] if test == ALL else [v for v in by[kind, paper] if v["test"] == test]
            if got:
                passed = sum(v["passed"] for v in got)
                out.append({"kind": kind, "paper": paper, "test": test, "made": len(got), "passed": passed,
                            "rate": passed / len(got), "mean_square_z": _mean_square(got), "within_r": r, "step_rule": rule})
    return out


def bar_of(rows: Sequence[dict], least_rows: int = MIN_BAR_ROWS, min_papers: int = MIN_BAR_PAPERS,
           without: Sequence[str] = ()) -> dict:
    """The calibrated bar of each test check() judges (mean, sd, step), from one kind's held-out
    rows: the median and the BAR_LOW quantile (numpy's linear) of the papers' own pass rates, each
    paper one population and one vote, over the papers with least_rows rows of the test or more
    (the papers in `without` left out), with the rate pooled over their rows beside. A paper's rate
    over a few rows is mostly its rows' binomial noise (eight rows move it in steps of 0.125), and
    the low quantile of noisy rates sits below what any population scores, while a generated cohort
    is scored on hundreds of rows; so only papers whose rate rests on MIN_BAR_ROWS rows vote.
    Weighting each paper by its rows would answer another question, the share of rows passed, which
    the paper of the most rows sets (Tan 2004, bounds.json's calibration.bar_rule), and a bar is one
    population's rate. Fewer than min_papers papers give the test no bar (its entry carries only how
    many there are): a 10th percentile of four rates is the lowest of them moved 0.3 of the way to
    the next, one population's rate in all but name."""
    out = {}
    for test in CALIBRATED:
        have = [r for r in rows if r["test"] == test and r["made"] > 0]
        if not have:
            continue
        mine = [r for r in have if r["made"] >= least_rows and r["paper"] not in without]
        entry = {"papers": len(mine), "least_rows": least_rows, "low_quantile": BAR_LOW, "papers_with_any_row": len(have)}
        if len(mine) >= min_papers:
            rates = [r["passed"] / r["made"] for r in mine]
            entry.update(median=float(np.median(rates)), low=float(np.quantile(rates, BAR_LOW)),
                         pooled=sum(r["passed"] for r in mine) / sum(r["made"] for r in mine),
                         papers_named=";".join(sorted(r["paper"] for r in mine)))
        out[test] = entry
    return out


def reference_n_measured(series: Sequence[L.Series], register: Dict[Tuple[str, str], RG.Population],
                         calibration_rows: Sequence[dict], least_rows: int = MIN_BAR_ROWS) -> dict:
    """The people a cell the bar's papers score with: each paper whose rows of the mean or step test
    reach least_rows in every paper's calibration, its median people a stratum, and the median of
    those, the figure REFERENCE_N stands near."""
    people: Dict[str, List[float]] = {}
    for c in ST.strata_of(series_of_kind(series, register, ALL)):
        for st in c.strata:
            people.setdefault(st.paper, []).append(float(st.n))
    papers = sorted({r["paper"] for r in calibration_rows if (r.get("kind") or ALL) == ALL
                     and r["test"] in ("mean", "step") and int(r["made"]) >= least_rows and r["paper"] in people})
    medians = {p: float(np.median(people[p])) for p in papers}
    return {"papers": medians, "median": float(np.median(list(medians.values()))) if medians else float("nan"),
            "reference_n": REFERENCE_N}


def choose_r(rates: Dict[float, float], nominal: float = NOMINAL) -> float:
    """The within-person correlation whose held-out step coverage is nearest the nominal rate, the
    smaller r where two are as near."""
    return min(sorted(rates), key=lambda r: (abs(rates[r] - nominal), r))


# ---- cohorts for testing the card ---------------------------------------------------------------------------

def _chain(rows: Sequence[dict], card: Card, kind: str, rng: np.random.Generator) -> Dict[str, float]:
    """One new population's level means for one measure: each cell's mean moved by its `between`, the
    moves of adjacent levels correlated so that their difference has the gradient's spread where the
    card has the step (a Gaussian chain down the column), independent where it has none."""
    by_level = {r["level"]: r for r in rows}
    means: Dict[str, float] = {}
    previous, z_prev = None, 0.0
    for level in LEVELS:
        r = by_level.get(level)
        if r is None:
            previous = None
            continue
        e = rng.normal()
        z = e
        if previous is not None:
            s = card.step(kind, r["measure"], previous["level"], level)
            if s is not None and previous["between"] > 0 and r["between"] > 0:
                rho = (previous["between"] ** 2 + r["between"] ** 2 - s["between"] ** 2) / (2 * previous["between"] * r["between"])
                rho = max(-RHO_CLIP, min(RHO_CLIP, rho))
                z = rho * z_prev + math.sqrt(1.0 - rho * rho) * e
        means[level] = r["mean"] + r["between"] * z
        previous, z_prev = r, z
    return means


def simulate(card: Card, kind: str, people: int, rng: np.random.Generator, centre: bool = False,
             measures: Optional[Sequence[str]] = None) -> Cohort:
    """A cohort drawn from the card's own model, people independent at every cell: a new population
    (its level means by _chain, its SD at each cell from the interval for a new population's SD,
    the pooled SD where no SD is certain), or, `centre`, the population at the card's centre, every
    mean the pooled mean and every SD the pooled SD: the papers' ideal spine."""
    cells, _ = card.of_kind(kind)
    by_measure: Dict[str, List[dict]] = {}
    for r in cells:
        if measures is None or r["measure"] in measures:
            by_measure.setdefault(r["measure"], []).append(r)
    cols = {"measure": [], "level": [], "value": [], "person": []}
    persons = np.arange(people)
    for measure in sorted(by_measure):
        rows = by_measure[measure]
        means = {r["level"]: r["mean"] for r in rows} if centre else _chain(rows, card, kind, rng)
        for r in sorted(rows, key=lambda r: LEVELS.index(r["level"])):
            sd = r["sd"]
            if not centre and math.isfinite(r["sd_log_centre"]):
                sd = math.exp(r["sd_log_centre"] + r["sd_log_between"] * rng.normal())
            cols["value"].append(means[r["level"]] + sd * rng.normal(size=people))
            cols["measure"] += [measure] * people
            cols["level"] += [r["level"]] * people
            cols["person"].append(persons)
    return Cohort(measure=np.array(cols["measure"], dtype=object), level=np.array(cols["level"], dtype=object),
                  value=np.concatenate(cols["value"]) if cols["value"] else np.zeros(0),
                  person=np.concatenate(cols["person"]) if cols["person"] else np.zeros(0, int))


def from_population(pop, which: str = "true") -> Cohort:
    """A drawn population (population.Population) as a cohort, one entry a person, body and measure."""
    x = getattr(pop, which)
    n, w, m = x.shape
    person = np.repeat(np.arange(n), w * m)
    level = np.tile(np.repeat(np.array(pop.levels, dtype=object), m), n)
    measure = np.tile(np.array(pop.keys, dtype=object), n * w)
    return Cohort(measure=measure, level=level, value=x.reshape(-1).astype(float), person=person)


def with_levels(cohort: Cohort, mapping: Dict[str, str]) -> Cohort:
    """The same cohort with its levels renamed, a level absent from `mapping` kept: a reversed or
    swapped run breaks the gradient and leaves every value as it was."""
    level = np.array([mapping.get(lv, lv) for lv in cohort.level], dtype=object)
    return Cohort(measure=cohort.measure, level=level, value=cohort.value, sex=cohort.sex, person=cohort.person)


def flattened(cohort: Cohort, levels: Sequence[str]) -> Cohort:
    """The same cohort with every measure's mean over `levels` the same at each of them: each level's
    values moved by the gap between the run's mean and its own, so every spread is kept and the
    gradient along the run is gone."""
    value = cohort.value.copy()
    groups = cohort.groups()
    for m in sorted({m for m, _ in groups}):
        mine = [groups[m, lv] for lv in levels if (m, lv) in groups]
        if len(mine) < 2:
            continue
        run_mean = float(np.mean([cohort.value[i].mean() for i in mine]))
        for i in mine:
            value[i] += run_mean - cohort.value[i].mean()
    return Cohort(measure=cohort.measure, level=cohort.level, value=value, sex=cohort.sex, person=cohort.person)
