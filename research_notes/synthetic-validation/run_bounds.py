"""The bounds card a generator of synthetic spines is held to: the records of synthval/bounds.py.

    python3 -I run_bounds.py --out records/bounds            # about three minutes on 4 CPUs
    python3 -I run_bounds.py --out /tmp/x --quick             # the same path on few populations

Run from this folder with the Python that holds bordercall's pinned packages, after run.py, whose
records/naming.csv names the state space's point nearest the papers. greg's question of 2026-10-30:
could the literature's results "at least serve as bounds for generative models making synthetic
spines from ideal spines". Writes calibration.csv (every paper left out in turn, the card of every
paper together built from the rest and the left-out paper's own means, SDs and steps scored on it,
and each specimen kind's card the same way on that kind's own papers: one row a kind of card,
held-out paper and test, at the within-person correlation the held-out step coverage chooses),
bounds.csv (per kind of population, measure and level: the pooled mean and the interval for a new
population's mean, the printed SDs' range, the pooled and the predictive SD and the interval for a
new population's SD, the sex contrast, read from the full snapshot with the sexes' snapshot beside
it as run_covariates.py reads it, and the age slope, with the interval for a new population's
effect where the papers print them), gradients.csv (per kind, measure and pair of adjacent levels:
the step read inside each paper, pooled, with the interval for a new population's step and how far
the difference of the pooled means sits from it) and bounds.json (the counts, the widths, the
borrowed spreads and why the means and the steps borrow apart, the covariates' borrowing under both
rules with the cells each leaves clear of zero and the sex contrasts' signs held out, the
within-person correlation chosen and its sensitivity, each kind's calibrated bar with the bar read
three ways with and without Tan 2004 and why the check takes the one it takes, what is not on the
card, the seeds, the commit, the snapshot's digest, the code, and the card's verdict on seven
cohorts: the papers' ideal spine at the card's centre, new populations drawn from the card's own
model under the z and the t interval paired, with why they fall below the steps' bar, the
generator's true and measured anatomy on Panjabi's table by kind, the state space's nearest point,
and the ideal spine with its lumbar gradient reversed and flattened, each set beside every reading
of the steps' bar).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import subprocess
import sys
import time
from typing import Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

import numpy as np  # noqa: E402

from synthval import bounds as B  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import register as RG  # noqa: E402
from synthval.population import GENERATOR, Settings, draw_table  # noqa: E402
from run import code_digests, log, write_csv, write_json  # noqa: E402

LUMBAR = ["L1", "L2", "L3", "L4", "L5"]
SEED_DRAWN = 4201
SEED_CENTRE = 4202
SEED_GENERATOR = 11          # the state space's seed (records/state_space.csv)
PEOPLE_DRAWN, PEOPLE_CENTRE, PEOPLE_GENERATOR = 300, 1000, 2000
POPULATIONS = 200
NEAREST = "nearest the papers"
SETTING_FIELDS = ("scale_sd", "rho", "phi", "r_between", "error_scale", "sd_mode", "floor", "blend", "sd_scale")
LEFT_OUT_BESIDE = "tan2004"  # the paper of the most held-out rows, whose SDs are uncertain; its pooled rates are given without it too

NOT_ON_THE_CARD = {
    "within-person structure of adjacent levels": {
        "why": "no paper in the records prints the correlation of one person's two adjacent levels, so a paper's "
               "step variance takes it as the parameter r, chosen by held-out coverage (step_r), and simulate "
               "draws people independent at every cell",
        "in_the_records": False,
        "could_bound_it": [
            {"source": "Hipp 2022, NHANES II films (7,364 lumbar, 9,662 cervical)",
             "gives": "the mean and SD of the absolute differences between adjacent vertebrae in six shape metrics"},
            {"source": "Palm 2025, 262 people, TotalSegmentator on CT",
             "gives": "mean ratios of body heights between every pair of levels from T1 to L5, by sex"},
            {"source": "EVOS, Ismail 1999, 13,562 people",
             "gives": "a body's posterior height predicted from up to four adjacent bodies, T4 to L4"},
            {"source": "J Bone Miner Res 1994;9:1895-1907, three European centres",
             "gives": "each body's posterior height as a ratio to the body above and the body below"}],
        "where": "SchwingNet docs/research/morphometry-beyond-the-42-papers.md, line 63 (where within-person "
                 "correlations could come from) and lines 137 to 153 (the published summaries, Hipp 2022 at line "
                 "139, and line 151: no covariance of Panjabi-type measures across the whole column from 200 or "
                 "more people was found), as the note stood at SchwingNet commit cdb0cce"},
    "anomalies schwingcheck generates": {
        "why": "the records hold no series of a transitional or anomalous group (no row of data/series_all.csv "
               "names one), and the only rows at an L6 or a T13 are Busscher 2010's porcine ones (data/series_all.csv, "
               "cohort porcine_landrace: disc_h_mid, h_ant, h_mid and h_post at both levels and the end plate's width "
               "and depth at L6, ten rows), which the selection drops as not human (synthval/literature.py, rule 2), "
               "so the card has no cell or step at an L6 or a T13. check() reads a cohort's bodies by their level "
               "names, so a generator's anomalous bodies that keep an ordinary name are scored against the "
               "ordinary cells and steps, the wrong bound rather than none, and only the L6 and the T13 go unscored",
        "where": "schwingcheck/columns.py, PHENOTYPES, phenotype_levels, _profile and profiles",
        "phenotypes": [
            "six_lumbar: an L6 whose mean is L5's plus half the L4 to L5 step, with L5's SD; the L6 is unscored, "
            "the L1 to L5 are typical bodies and scored as such",
            "t13: a T13 between T12 and L1, its mean and SD blended from theirs; the T13 is unscored, and the step "
            "the card holds from T12 to L1, adjacent in a typical column, is scored though two steps join them here",
            "lumbar_rib: the L1 blended toward T12 and still named L1, so scored against a typical L1's cell and "
            "the card's steps into and out of L1",
            "no_rib_t12: the T12 blended toward L1 and still named T12, so scored against a typical T12's cell and "
            "the card's steps into and out of T12",
            "four_lumbar: the column without L5, its L1 to L4 named as a typical column's and scored against their "
            "cells and steps; no L5 and no L4 to L5 step is scored"]}}


def nearest_settings(records: str) -> Settings:
    """The state space's point nearest the papers, as records/naming.csv names it."""
    with open(os.path.join(records, "naming.csv"), encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["setting"] == NEAREST:
                kw = {}
                for f in SETTING_FIELDS:
                    text = r["setting " + f]
                    kw[f] = text if f == "sd_mode" else (text == "True") if f == "floor" else float(text)
                return GENERATOR.but(name=NEAREST, **kw)
    raise SystemExit("records/naming.csv names no point %r; run run.py first" % NEAREST)


def quartiles(values) -> list:
    x = np.array([v for v in values if isinstance(v, float) and math.isfinite(v)])
    return [float(q) for q in np.quantile(x, [0.25, 0.5, 0.75])] if len(x) else []


def median_of(values) -> float:
    x = [v for v in values if isinstance(v, float) and math.isfinite(v)]
    return float(np.median(x)) if x else float("nan")


def counts(card: B.Card, kind: str) -> dict:
    cells, steps = card.of_kind(kind)
    def n(rows, f):
        return sum(1 for r in rows if f(r))
    return {"cells": len(cells), "measures": len({r["measure"] for r in cells}),
            "cells_with_own_tau": n(cells, lambda r: r["tau_from"] == B.TAU_OWN),
            "cells_with_own_tau_on_fewer_than_three_papers": n(cells, lambda r: r["tau_from"] == B.TAU_OWN and r["papers"] < 3),
            "cells_on_one_series": n(cells, lambda r: r["k"] == 1),
            "cells_with_sd_interval": n(cells, lambda r: math.isfinite(r["sd_low"])),
            "cells_with_own_sd_tau": n(cells, lambda r: r["sd_tau_from"] == B.TAU_OWN),
            "cells_with_sex_contrast": n(cells, lambda r: math.isfinite(r["sex_g"])),
            "cells_with_sex_contrast_on_one_paper": n(cells, lambda r: math.isfinite(r["sex_g"]) and r["sex_g_papers"] == 1),
            "cells_with_sex_contrast_whose_pooled_interval_clears_zero": n(cells, lambda r: B.clear_of_zero(r, "sex_g", "_low", "_high")),
            "cells_with_sex_contrast_whose_new_population_interval_clears_zero": n(cells, lambda r: B.clear_of_zero(r, "sex_g")),
            "of_them_on_a_tau_of_zero": n(cells, lambda r: B.clear_of_zero(r, "sex_g") and r["sex_g_tau_used"] == 0),
            "cells_with_age_slope": n(cells, lambda r: math.isfinite(r["age_slope"])),
            "cells_with_age_slope_whose_pooled_interval_clears_zero": n(cells, lambda r: B.clear_of_zero(r, "age_slope", "_low", "_high")),
            "cells_with_age_slope_whose_new_population_interval_clears_zero": n(cells, lambda r: B.clear_of_zero(r, "age_slope")),
            "of_them_on_an_age_tau_of_zero": n(cells, lambda r: B.clear_of_zero(r, "age_slope") and r["age_slope_tau_used"] == 0),
            "steps": len(steps), "steps_with_own_tau": n(steps, lambda r: r["tau_from"] == B.TAU_OWN),
            "steps_with_own_tau_of_zero": n(steps, lambda r: r["tau_from"] == B.TAU_OWN and r["step_tau"] == 0),
            "steps_on_one_paper": n(steps, lambda r: r["k"] == 1),
            "mean_half_width_over_sd_quartiles": quartiles(r["half_width_over_sd"] for r in cells),
            "predictive_over_sd_quartiles": quartiles(r["predictive_over_sd"] for r in cells),
            "sd_interval_high_over_low_quartiles": quartiles(r["sd_high"] / r["sd_low"] for r in cells if math.isfinite(r["sd_low"])),
            "step_half_width_over_sd_quartiles": quartiles(r["half_width_over_sd"] for r in steps),
            "abs_step_over_sd_quartiles": quartiles(abs(r["step_over_sd"]) for r in steps)}


def incoherent_spreads(card: B.Card, kind: str) -> list:
    """The steps no population of the card's model can honour together with both levels' mean
    intervals: the two levels' spreads differ by more than the step's, so the wider is looser than
    the narrower and the step together imply."""
    cells, steps = card.of_kind(kind)
    by = {(r["measure"], r["level"]): r for r in cells}
    out = []
    for s in steps:
        a, b = by[s["measure"], s["upper"]], by[s["measure"], s["lower"]]
        if abs(a["between"] - b["between"]) > s["between"]:
            out.append((s["measure"], s["upper"], s["lower"]))
    return out


def pass_rate(rows, key, keep=lambda r: True) -> dict:
    mine = [r for r in rows if key in r and keep(r)]
    return {"made": len(mine), "passed": sum(bool(r[key]) for r in mine),
            "rate": sum(bool(r[key]) for r in mine) / len(mine) if mine else float("nan")}


def by_measure(result: dict) -> list:
    """Each measure's pass rates in one check, the measures with the most failures first."""
    out = {}
    for r in result["cells"]:
        m = out.setdefault(r["measure"], {"measure": r["measure"], "made": 0, "passed": 0})
        for key in ("mean_pass", "sd_pass"):
            if key in r:
                m["made"] += 1
                m["passed"] += bool(r[key])
    for r in result["steps"]:
        m = out.setdefault(r["measure"], {"measure": r["measure"], "made": 0, "passed": 0})
        m["made"] += 1
        m["passed"] += bool(r["step_pass"])
    rows = [dict(m, failed=m["made"] - m["passed"], rate=m["passed"] / m["made"]) for m in out.values() if m["made"]]
    return sorted(rows, key=lambda m: (-m["failed"], m["measure"]))


# ---- the calibration ------------------------------------------------------------------------------------

def specimens_of(series, register) -> dict:
    """Each paper's specimens in the register, for the calibration's rows."""
    out = {}
    for s in B.series_of_kind(series, register, B.ALL):
        out.setdefault(s.paper, set()).add(B.specimen_of(s.paper, s.cohort, register))
    return {p: ";".join(sorted(k)) for p, k in out.items()}


def held_out_steps(verdicts, r: float, rule: str = B.STEP_RULE, test_r=None, **keys) -> dict:
    """The held-out steps pooled at the card's r (the left-out paper's own read at test_r, else r)."""
    return B.coverage(B.matching(verdicts, test="step", r=r, test_r=r if test_r is None else test_r, rule=rule, **keys))


def r_grid(verdicts) -> list:
    """The held-out step coverage at every r of the grid, under both borrowing rules, and the
    held-out papers' median and low step rates under the steps' rule."""
    out = []
    for r in B.STEP_R_GRID:
        bar = B.bar_of(B.per_paper(verdicts, r, B.STEP_RULE)).get("step", {})
        out.append({"r": r, "steps_rule": held_out_steps(verdicts, r),
                    "means_rule": held_out_steps(verdicts, r, B.MEDIAN),
                    "paper_median": bar.get("median"), "paper_low": bar.get("low")})
    return out


def pooled_rates(verdicts) -> dict:
    """The held-out rows of each calibrated test pooled over every paper, and the three together."""
    out = {t: B.coverage(B.matching(verdicts, test=t)) for t in B.CALIBRATED}
    passed = sum(v["passed"] for v in verdicts)
    out[B.ALL] = {"made": len(verdicts), "passed": passed, "rate": passed / len(verdicts) if verdicts else float("nan")}
    return out


def weighted_quantile(values, weights, q: float) -> float:
    """The q quantile of values each carrying its weight: the smallest value at which the weights at
    or below it reach the share q of the whole (the inverse of the weighted distribution)."""
    order = np.argsort(np.asarray(values, float), kind="stable")
    v, w = np.asarray(values, float)[order], np.asarray(weights, float)[order]
    share = np.cumsum(w) / w.sum()
    return float(v[min(int(np.searchsorted(share, q - 1e-12)), len(v) - 1)])


def weighted_bar(rows, without=()) -> dict:
    """Each test's bar with every held-out paper weighted by its rows: the weighted 10th percentile
    and median of the papers' rates."""
    out = {}
    for test in B.CALIBRATED:
        mine = [r for r in rows if r["test"] == test and r["made"] > 0 and r["paper"] not in without]
        if mine:
            rates, made = [r["passed"] / r["made"] for r in mine], [r["made"] for r in mine]
            out[test] = {"low": weighted_quantile(rates, made, B.BAR_LOW), "median": weighted_quantile(rates, made, 0.5),
                         "papers": len(mine), "rows": sum(made)}
    return out


def brief(bar: dict) -> dict:
    return {t: {k: b[k] for k in ("low", "median", "papers") if k in b} for t, b in bar.items()}


CHECKS_BAR = "the check's: papers with %d rows or more of the test, one paper one vote" % B.MIN_BAR_ROWS
EVERY_PAPER = "every paper with a row of the test, one paper one vote whatever its rows (the rule the bar had before)"
WEIGHTED = "every paper with a row of the test, each weighted by its rows"


def bar_variants(rows) -> dict:
    """One kind's bar read three ways, each with and without Tan 2004: the check's (bar_of), every
    paper one vote whatever its rows, and every paper weighted by its rows."""
    out = {}
    for name, without in (("with " + LEFT_OUT_BESIDE, ()), ("without " + LEFT_OUT_BESIDE, (LEFT_OUT_BESIDE,))):
        out[name] = {CHECKS_BAR: brief(B.bar_of(rows, without=without)),
                     EVERY_PAPER: brief(B.bar_of(rows, least_rows=1, min_papers=1, without=without)),
                     WEIGHTED: weighted_bar(rows, without)}
    return out


def bar_choice(rows) -> dict:
    """Which bar the check uses and why, with the run's own numbers: the papers that set the step bar
    of every paper, and the paper of the most rows of each test."""
    steps = [r for r in rows if r["test"] == "step" and r["made"] > 0]
    low = B.bar_of(rows, least_rows=1, min_papers=1)["step"]["low"]
    setting = sorted((r for r in steps if r["passed"] / r["made"] <= low), key=lambda r: (r["rate"], r["paper"]))
    most = {t: max((r for r in rows if r["test"] == t), key=lambda r: (r["made"], r["paper"])) for t in B.CALIBRATED}
    return {
        "used": CHECKS_BAR + ", Tan 2004 among them; a test with fewer than %d such papers has no bar" % B.MIN_BAR_PAPERS,
        "why_%d_rows" % B.MIN_BAR_ROWS: (
            "a paper's rate over a few rows is mostly binomial noise (eight rows move it in steps of 0.125), so the low "
            "quantile of every paper's rate is set by papers of few rows (every paper's step bar, %.3f, by %s) and "
            "sits below what a population scores, while a generated cohort is scored on hundreds of rows; only papers "
            "whose rate rests on %d rows vote"
            % (low, ", ".join("%s (%d rows, %.3f)" % (r["paper"], r["made"], r["rate"]) for r in setting), B.MIN_BAR_ROWS)),
        "why_not_weighted": (
            "weighting each paper by its rows gives the share of rows passed, which the paper of the most rows sets "
            "(%s), while a generated cohort is one population and is set beside populations' rates"
            % "; ".join("%s: %s, %d of %d rows" % (t, most[t]["paper"], most[t]["made"],
                                                     sum(r["made"] for r in rows if r["test"] == t)) for t in B.CALIBRATED)),
        "why_tan2004_stays": (
            "Tan 2004 is a real population of the card's domain held out like any other, one vote among the papers of "
            "%d rows; its SDs are uncertain (literature.DISPERSION_UNCERTAIN) and give it no SD row, and its means are "
            "read against the rest's pooled SD (strata.py), so the uncertainty does not reach the rows it votes with; "
            "leaving out the paper whose rows fail most would choose the reference populations by their outcome and "
            "hold a generator to a bar a real population fails. The bar without it stands beside (bars)" % B.MIN_BAR_ROWS)}


def calibration_record(verdicts, rows, bars, r: float, papers_left_out, kind_rows) -> dict:
    """bounds.json's calibration: the bar of every paper's card and its variants, the rates pooled
    over every held-out row (and without the paper of the most rows), the papers that gave no row,
    the papers of the lowest rates, each kind's own calibration, and why the sex test carries no
    bar."""
    mine = B.of_reading(verdicts, r, B.STEP_RULE)
    with_rows = sorted({row["paper"] for row in rows})
    worst = sorted((row for row in rows if row["test"] == B.ALL and row["made"] >= 5), key=lambda row: (row["rate"], row["paper"]))
    kinds = {}
    for kind, krows in sorted(kind_rows.items()):
        kinds[kind] = {"papers_with_rows": len({row["paper"] for row in krows}), "bar": bars[kind],
                       "bars": bar_variants(krows),
                       "rows_by_test": {t: sum(row["made"] for row in krows if row["test"] == t) for t in B.CALIBRATED}}
    return {"bar": bars[B.ALL], "bar_rule": bar_choice(rows), "bars": bar_variants(rows), "within_r": r, "step_rule": B.STEP_RULE,
            "rule": "each paper left out in turn; the card of every paper together built from the rest alone; the "
                    "left-out paper's own strata scored on it as check() scores a cohort, each widened by its own "
                    "sampling error; the bar is the median and the %.0fth percentile of the papers' own rates, one "
                    "paper one vote, over the papers with %d rows or more of the test" % (100 * B.BAR_LOW, B.MIN_BAR_ROWS),
            "pooled": pooled_rates(mine),
            "pooled_without_%s" % LEFT_OUT_BESIDE: pooled_rates([v for v in mine if v["paper"] != LEFT_OUT_BESIDE]),
            "papers_left_out": len(papers_left_out), "papers_with_rows": len(with_rows),
            "papers_with_no_row": sorted(set(papers_left_out) - set(with_rows)),
            "lowest_overall_of_five_rows_or_more": [{k: row[k] for k in ("paper", "made", "passed", "rate")} for row in worst[:6]],
            "kinds": {"rule": "each paper of the kind left out in turn, the kind's card built from the kind's other "
                              "papers with the spreads they cannot read borrowed from every other paper (as build "
                              "builds a kind's card), at the same r and steps' rule; the bar as every paper's",
                      **kinds},
            "not_calibrated": "the sex test: a sign test made only where the interval for a new population's contrast "
                              "clears zero, so it carries no pass rate a held-out paper's is set beside and enters no "
                              "verdict; how often a held-out paper's own sign agrees at such cells, under either "
                              "borrowing rule, is covariate_borrowing's held_out_signs"}


# ---- the within-person correlation and the borrowing -------------------------------------------------------

def step_stats(card: B.Card) -> dict:
    """The steps of every paper's card: how many have a tau of their own, how many of those are zero,
    and the median half-widths."""
    _, steps = card.of_kind(B.ALL)
    own = [s for s in steps if s["tau_from"] == B.TAU_OWN]
    return {"steps": len(steps), "own_tau": len(own), "own_tau_of_zero": sum(1 for s in own if s["step_tau"] == 0),
            "own_tau_half_width_over_sd_median": median_of(s["half_width_over_sd"] for s in own),
            "half_width_over_sd_median": median_of(s["half_width_over_sd"] for s in steps),
            "borrowed_overall_tau_over_sd": card.borrowed["step_tau_over_sd"]["overall"]}


def sensitivity(series, rows, voc, register, verdicts, generator_true) -> list:
    """At each r of STEP_R_SENSITIVITY: the steps of every paper's card, the held-out step coverage,
    apart for the steps whose card row has a tau of its own and those that borrow, with the left-out
    paper's own step variance read at every r of the set (the card's r first), and the generator's
    true anatomy's step pass rate."""
    out = []
    for r in B.STEP_R_SENSITIVITY:
        card = B.build(series, rows, voc, register, r=r, kinds=(B.ALL,))
        bar = B.bar_of(B.per_paper(verdicts, r, B.STEP_RULE)).get("step", {})
        out.append(dict(r=r, **step_stats(card), held_out_steps=held_out_steps(verdicts, r),
                        held_out_steps_own_tau=held_out_steps(verdicts, r, tau_from=B.TAU_OWN),
                        held_out_steps_borrowed_tau=B.coverage(v for v in B.matching(verdicts, test="step", r=r, test_r=r,
                                                                                      rule=B.STEP_RULE)
                                                               if v["tau_from"] != B.TAU_OWN),
                        held_out_steps_by_test_r={"%.1f" % t: held_out_steps(verdicts, r, test_r=t) for t in B.STEP_R_SENSITIVITY},
                        held_out_paper_median=bar.get("median"), held_out_paper_low=bar.get("low"),
                        generator_true_steps=B.check(generator_true, card)["summary"]["tests"]["step"]))
    return out


def width_ratio(card: B.Card, least: int = 1) -> dict:
    """The steps' intervals over the means', in SDs, over the cells and steps of `least` papers or
    more: the median step half-width over the median cell half-width, and, paired, the median over
    steps of each step's half-width over the mean of its two cells'."""
    cells, steps = card.of_kind(B.ALL)
    by = {(r["measure"], r["level"]): r for r in cells}
    cells = [r for r in cells if r["papers"] >= least]
    steps = [s for s in steps if s["k"] >= least]
    paired = []
    for s in steps:
        a, b = by[s["measure"], s["upper"]], by[s["measure"], s["lower"]]
        if a["papers"] >= least and b["papers"] >= least:
            paired.append(s["half_width_over_sd"] / (0.5 * (a["half_width_over_sd"] + b["half_width_over_sd"])))
    mean_half = median_of(r["half_width_over_sd"] for r in cells)
    step_half = median_of(s["half_width_over_sd"] for s in steps)
    return {"least_papers": least, "cells": len(cells), "steps": len(steps), "paired_steps": len(paired),
            "mean_half_width_over_sd_median": mean_half, "step_half_width_over_sd_median": step_half,
            "ratio_of_medians": step_half / mean_half if mean_half > 0 else float("nan"),
            "paired_ratio_median": median_of(paired)}


def borrowing(card: B.Card, card_median: B.Card, verdicts, r: float) -> dict:
    """Why the means and the steps borrow apart, with the held-out step coverage under each rule and
    the steps' width over the means' under each and where neither borrows."""
    return {
        "means": {"rule": card.borrowed["mean_tau_over_sd"]["rule"],
                  "why": "kept so that every paper's card has strata.between's spread to the bit, as the rest of the "
                         "note reads a cell's spread"},
        "steps": {"rule": B.STEP_RULE,
                  "why": "REML puts a tau of exactly zero on many steps of three to nine papers, and a median of such "
                         "zeros would lend a one-paper step no spread at all; the mean of tau^2 keeps what the steps "
                         "with a spread say, and one vote a measure keeps one method-bound measure from setting every "
                         "other's"},
        "held_out_step_coverage_at_r": r,
        "held_out_step_coverage": {"steps' rule": held_out_steps(verdicts, r),
                                   "means' rule": held_out_steps(verdicts, r, B.MEDIAN)},
        "step_over_mean_width": {"under the steps' rule": width_ratio(card),
                                 "under the means' rule": width_ratio(card_median),
                                 "three papers or more, where neither borrows": width_ratio(card, 3)}}


# ---- the checks -----------------------------------------------------------------------------------------

def add_tests(made: dict, passed: dict, summary: dict) -> None:
    for test, v in summary["tests"].items():
        made[test] = made.get(test, 0) + v["made"]
        passed[test] = passed.get(test, 0) + v["passed"]


def rates_of(made: dict, passed: dict) -> dict:
    return {t: {"made": made[t], "passed": passed[t], "rate": passed[t] / made[t]} for t in made}


def rate_of(counts: dict) -> dict:
    return dict(counts, rate=counts["passed"] / counts["made"] if counts["made"] else float("nan"))


def drawn(card: B.Card, kind: str, populations: int, people: int, seed: int, skip: set) -> dict:
    """New populations from the card's own model, each checked under the z and the t interval on
    the same draws: the tests pooled over the populations with their verdict, each population's own
    verdict counted, each population's overall rate spread, the steps the model can and cannot
    honour apart, and the t interval's rates beside the z's, paired."""
    rng = np.random.default_rng(seed)
    made, passed, t_made, t_passed, rates, msz, by_test = {}, {}, {}, {}, [], [], {}
    t_at_least = 0
    honoured, unhonoured = {"made": 0, "passed": 0}, {"made": 0, "passed": 0}
    outcomes = {"passed": 0, "failed": 0, "no verdict": 0}
    test_bars = {}
    for _ in range(populations):
        cohort = B.simulate(card, kind, people, rng)
        res, res_t = B.check(cohort, card, kind), B.check(cohort, card, kind, interval="t")
        add_tests(made, passed, res["summary"])
        add_tests(t_made, t_passed, res_t["summary"])
        t_at_least += res_t["summary"]["rate"] >= res["summary"]["rate"]
        rates.append(res["summary"]["rate"])
        msz.append(res["summary"]["mean_square_z"])
        for test, v in res["summary"]["mean_square_z_by_test"].items():
            by_test.setdefault(test, []).append(v)
        verdict = res["summary"]["verdict"]
        outcomes[{True: "passed", False: "failed", None: "no verdict"}[verdict["passed"]]] += 1
        for test, v in verdict["tests"].items():
            if v["passed"] is not None:
                got = test_bars.setdefault(test, {"made": 0, "passed": 0})
                got["made"] += 1
                got["passed"] += v["passed"]
        for s in res["steps"]:
            mine = unhonoured if (s["measure"], s["upper"], s["lower"]) in skip else honoured
            mine["made"] += 1
            mine["passed"] += bool(s["step_pass"])
    tests, t_tests = rates_of(made, passed), rates_of(t_made, t_passed)
    return {"populations": populations, "people": people, "seed": seed, "tests": tests,
            "verdict_of_the_pooled_rates": B.verdict(tests, card.bar(kind), bool(card.calibration)),
            "population_verdicts": outcomes,
            "populations_at_or_above_each_tests_bar": {t: rate_of(v) for t, v in test_bars.items()},
            "rate": sum(passed.values()) / sum(made.values()), "population_rate_quartiles": quartiles(rates),
            "population_rate_min": float(min(rates)), "mean_square_z_median": float(np.median(msz)),
            "mean_square_z_by_test_median": {t: float(np.median(v)) for t, v in by_test.items()},
            "steps_the_model_honours": rate_of(honoured), "steps_the_model_cannot_honour": rate_of(unhonoured),
            "paired_t": {"note": "the same populations under Higgins's t interval where a cell has three series or a "
                                 "step three papers, z elsewhere",
                         "tests": t_tests, "t_minus_z": {t: t_tests[t]["rate"] - tests[t]["rate"] for t in tests},
                         "populations_where_t_passes_at_least_as_often": int(t_at_least)}}


def incoherent_detail(card: B.Card, kind: str, skip: set) -> dict:
    """What sets the steps whose ends' spreads differ by more than the step's own apart from the
    others: how far the two levels' pooled SDs differ (over their mean), each level's spread of a new
    population's mean and the step's own in SDs, and where each end's tau came from."""
    cells, steps = card.of_kind(kind)
    by = {(r["measure"], r["level"]): r for r in cells}
    groups = {"incoherent": [], "coherent": []}
    pairs = {}
    for s in steps:
        a, b = by[s["measure"], s["upper"]], by[s["measure"], s["lower"]]
        mine = (s["measure"], s["upper"], s["lower"]) in skip
        groups["incoherent" if mine else "coherent"].append(
            (abs(a["sd"] - b["sd"]) / (0.5 * (a["sd"] + b["sd"])), 0.5 * (a["between"] / a["sd"] + b["between"] / b["sd"]),
             s["between"] / s["sd"]))
        if mine:
            key = " and ".join(sorted((a["tau_from"], b["tau_from"])))
            pairs[key] = pairs.get(key, 0) + 1
    out = {}
    for name, rows in groups.items():
        out[name] = {"steps": len(rows),
                     "sd_difference_over_mean_sd_median": median_of([r[0] for r in rows]),
                     "level_between_over_sd_median": median_of([r[1] for r in rows]),
                     "step_between_over_sd_median": median_of([r[2] for r in rows])}
    out["incoherent_by_tau_sources"] = dict(sorted(pairs.items(), key=lambda x: -x[1]))
    return out


def why_below_the_step_bar(drawn_check: dict, skip: set, steps: list, detail: dict, held_out_step: dict) -> str:
    """Why populations drawn from the card's own model fall below the steps' bar, in the run's numbers."""
    a, b = drawn_check["steps_the_model_honours"], drawn_check["steps_the_model_cannot_honour"]
    inc, coh = detail["incoherent"], detail["coherent"]
    same = detail["incoherent_by_tau_sources"].get(" and ".join([B.TAU_ALL] * 2), 0)
    return ("simulate keeps each level's spread of a new population's mean (between) and correlates adjacent levels "
            "so that their difference has the step's spread; at %d of the card's %d steps the two levels' betweens "
            "differ by more than the step's own, and since the SD of a difference is at least the difference of the "
            "SDs, no correlation gives both levels their spread and the step its own (incoherent_spreads), so the "
            "drawn steps there spread wider than the step's interval and pass at %.3f, against %.3f on the other %d. "
            "The betweens differ because each is read in its own level's SD, a new population's mean spreading about "
            "%.2f of the level's SD (median over those steps' two levels; %.2f over the others'), while a step's "
            "spread is %.2f of the pair's mean SD (%.2f): two adjacent levels whose pooled SDs differ by more than "
            "about %.2f of their mean, the ratio of the two spreads, have betweens further apart than the step's "
            "spread, and at those steps the two SDs differ by "
            "a median %.2f of their mean, against %.2f at the others. The borrowing does not set them apart: %d of "
            "them join two cells that both borrow every cell's median tau. Real populations held out are not drawn "
            "from the levels' spreads and pass the held-out steps at %.3f pooled (calibration), so the shortfall is "
            "the drawing model's, which no population of populations can honour on those steps, not a property of "
            "the steps' bar"
            % (len(skip), len(steps), b["rate"], a["rate"], len(steps) - len(skip),
               inc["level_between_over_sd_median"], coh["level_between_over_sd_median"],
               inc["step_between_over_sd_median"], coh["step_between_over_sd_median"],
               inc["step_between_over_sd_median"] / inc["level_between_over_sd_median"],
               inc["sd_difference_over_mean_sd_median"], coh["sd_difference_over_mean_sd_median"], same,
               held_out_step["rate"]))


def step_against(rate: float, variants: dict) -> dict:
    """A step pass rate set beside the steps' low bar of every variant (bar_variants)."""
    out = {}
    for tan, by in variants.items():
        for name, bar in by.items():
            b = bar.get("step", {})
            if "low" in b:
                out["%s, %s" % (name, tan)] = {"low": b["low"], "at_or_above": bool(rate >= b["low"])}
    return out


def broken(card: B.Card, cohort: B.Cohort, touched: str, variants: dict) -> dict:
    """A cohort whose lumbar gradient was broken, checked: the summary with its verdict, the step
    rate beside every variant of the steps' bar, and the tests the break touched (the lumbar cells
    and the steps into and down the lumbar run) apart."""
    res = B.check(cohort, card)
    lum_cells = lambda r: r["level"] in LUMBAR  # noqa: E731
    lum_steps = lambda r: r["lower"] in LUMBAR  # noqa: E731
    return {"summary": res["summary"], "touched": touched,
            "step_rate_against_every_bar": step_against(res["summary"]["tests"]["step"]["rate"], variants),
            "lumbar_means": pass_rate(res["cells"], "mean_pass", lum_cells),
            "lumbar_sds": pass_rate(res["cells"], "sd_pass", lum_cells),
            "lumbar_steps": pass_rate(res["steps"], "step_pass", lum_steps),
            "other_steps": pass_rate(res["steps"], "step_pass", lambda r: not lum_steps(r))}


# ---- the covariates' borrowing ------------------------------------------------------------------------------

def survivors(card: B.Card, prefix: str) -> dict:
    """The cells of every paper's card whose interval for a new population's effect clears zero,
    where check() makes the sex test (prefix sex_g) or the age slope's sign would be read."""
    cells, _ = card.of_kind(B.ALL)
    mine = [r for r in cells if B.clear_of_zero(r, prefix)]
    def name(r):
        return "%s %s" % (r["base_key"], r["level"])
    return {"cells": len(mine), "base_cells": len({name(r) for r in mine}),
            "of_them_on_a_borrowed_tau": sum(1 for r in mine if r[prefix + "_tau_from"] != B.TAU_OWN),
            "of_them_on_a_tau_of_zero": sum(1 for r in mine if r[prefix + "_tau_used"] == 0),
            "base_cells_named": sorted({name(r) for r in mine})}


def compare_survivors(rms: dict, median: dict) -> dict:
    a, b = set(rms["base_cells_named"]), set(median["base_cells_named"])
    return {"under the steps' rule (the card's)": rms, "under the means' rule": median, "under both": len(a & b),
            "only under the steps' rule": sorted(a - b), "only under the means' rule": sorted(b - a)}


def sign_rates(rows) -> dict:
    by = {}
    for r in rows:
        by.setdefault(r["paper"], []).append(r)
    per = [sum(r["passed"] for r in v) / len(v) for v in by.values()]
    out = B.coverage(rows)
    out.update(papers=len(by), paper_median=float(np.median(per)) if per else float("nan"),
               on_a_borrowed_tau=B.coverage(r for r in rows if r["tau_from"] != B.TAU_OWN))
    return out


def covariate_borrowing(card: B.Card, card_median: B.Card, items, register) -> dict:
    """The covariates' spreads borrowed under the steps' rule (the card's) and the means' rule: the
    taus each lends, the cells whose interval for a new population's effect clears zero under each,
    and, for the sex contrast, how often a paper held out has the sign at such cells (held_out_signs)."""
    out = {"rule": B.COVARIATE_RULE,
           "why": "the steps' rule, as the steps borrow: a donor cell's REML tau is exactly zero where its few papers "
                  "agree within their error, and a median over such cells lends a cell of one paper no spread at "
                  "all, so its sign is tested on that paper alone; the root mean square keeps what the donors with a "
                  "spread say, one vote a measure",
           "borrowed": {"under the steps' rule (the card's)": {k: card.borrowed[k] for k in ("sex_g_tau", "age_slope_tau")},
                        "under the means' rule": {k: card_median.borrowed[k] for k in ("sex_g_tau", "age_slope_tau")}}}
    for name, prefix in B.COVARIATES.items():
        out[name] = compare_survivors(survivors(card, prefix), survivors(card_median, prefix))
        lent = card.borrowed[prefix + "_tau"]
        if lent["donor_cells"] and lent["donor_taus_of_zero"] == lent["donor_cells"]:
            out[name]["note"] = (
                "every donor cell's REML tau is exactly zero (%d of %d, %s; %s), so either rule lends a spread of zero "
                "and every interval for a new population's %s on fewer than %d papers is its pooled interval: the "
                "spread between populations is not identified there, whichever rule is used%s"
                % (lent["donor_taus_of_zero"], lent["donor_cells"], lent["donors"], ", ".join(lent["donor_papers"]),
                   B.COVARIATE_UNITS[name].split(",")[0] if name == "sex" else "age slope", B.MIN_SERIES_FOR_TAU,
                   "; check() makes no test on the age slope" if name == "age" else ""))
    out["sex"]["held_out_signs"] = {"rule": "each paper with a sex contrast left out, the card's contrasts read from "
                                            "the rest, and at each cell whose interval for a new population's "
                                            "contrast clears zero there, whether the left-out paper's own contrast "
                                            "has the sign",
                                    "under the steps' rule (the card's)": sign_rates(B.held_out_signs(items, register, B.RMS)),
                                    "under the means' rule": sign_rates(B.held_out_signs(items, register, B.MEDIAN))}
    return out


def compact(result: dict) -> dict:
    return {"summary": result["summary"], "by_measure_worst": by_measure(result)[:12]}


def generator_checks(card: B.Card, steps: list, near: Settings, kinds: list) -> Tuple[dict, B.Cohort]:
    """The generator's and the nearest point's true and measured anatomy on Panjabi's table, checked,
    the steps on one paper and on two or more apart; and the generator's true anatomy by kind."""
    panjabi = PT.panjabi_table()
    one = {(s["measure"], s["upper"], s["lower"]) for s in steps if s["k"] == 1}
    checks, generator_true = {}, None
    for name, settings in (("generator", GENERATOR), (NEAREST, near)):
        pop = draw_table(panjabi, settings, PEOPLE_GENERATOR, SEED_GENERATOR)
        for which in ("true", "measured"):
            cohort = B.from_population(pop, which)
            res = B.check(cohort, card)
            entry = compact(res)
            entry["steps_on_one_paper"] = pass_rate(res["steps"], "step_pass", lambda r: (r["measure"], r["upper"], r["lower"]) in one)
            entry["steps_on_two_papers_or_more"] = pass_rate(res["steps"], "step_pass",
                                                            lambda r: (r["measure"], r["upper"], r["lower"]) not in one)
            checks["%s, %s" % (name, which)] = entry
            if name == "generator" and which == "true":
                generator_true = cohort
    checks["generator, true, by kind"] = {k: B.check(generator_true, card, k)["summary"] for k in kinds}
    return checks, generator_true


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--records", default=os.path.join(HERE, "records"), help="the first part's records, for the nearest point")
    ap.add_argument("--populations", type=int, default=POPULATIONS)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    if args.quick:
        args.populations = 5
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    started = time.time()
    code = code_digests()
    problems = PT.check_snapshot_all() + PT.check_snapshot_sexes()
    if problems:
        raise SystemExit("; ".join(problems))
    rows = PT.load_rows_all()
    sex_rows = rows + PT.load_rows_sexes()
    series, _ = PT.select_all(rows)
    voc = PT.load_vocabulary()
    register = RG.load()
    kinds = B.kinds_present(series, register)

    log("every paper left out in turn, at every within-person correlation of the grid")
    under = B.readings(B.STEP_R_GRID, (B.RMS, B.MEDIAN))
    under += [u for u in B.readings(B.STEP_R_SENSITIVITY, (B.STEP_RULE,), B.STEP_R_SENSITIVITY) if u[0] != u[1]]
    verdicts = B.held_out_verdicts(series, register, under)
    grid = r_grid(verdicts)
    chosen = B.choose_r({g["r"]: g["steps_rule"]["rate"] for g in grid})
    if chosen != B.STEP_R:
        log("the held-out step coverage chooses r = %.1f, not bounds.STEP_R = %.1f: set STEP_R and run again" % (chosen, B.STEP_R))
    specimens = specimens_of(series, register)
    cal_rows = [dict(r, specimens=specimens.get(r["paper"], "")) for r in B.per_paper(verdicts, chosen, B.STEP_RULE)]

    log("each kind's card calibrated on the kind's own papers held out")
    kind_rows = {}
    for kind in kinds[1:]:
        got = B.held_out_verdicts(series, register, ((chosen, chosen, B.STEP_RULE),), kind=kind)
        kind_rows[kind] = [dict(r, specimens=specimens.get(r["paper"], "")) for r in B.per_paper(got, chosen, B.STEP_RULE)]
    write_csv(out, "calibration.csv", cal_rows + [r for k in kinds[1:] for r in kind_rows[k]])
    bars = {B.ALL: B.bar_of(cal_rows), **{k: B.bar_of(v) for k, v in kind_rows.items()}}
    variants = bar_variants(cal_rows)

    log("the card at r = %.1f" % chosen)
    card = B.build(series, rows, voc, register, r=chosen, sex_rows=sex_rows)
    card.calibration = bars
    write_csv(out, "bounds.csv", card.cells)
    write_csv(out, "gradients.csv", card.steps)
    skip = set(incoherent_spreads(card, B.ALL))
    cells, steps = card.of_kind(B.ALL)
    incoherent_centres = [{"measure": s["measure"], "upper": s["upper"], "lower": s["lower"], "k": s["k"],
                           "coherence": s["coherence"], "step": s["step"], "mean_difference": s["mean_difference"]}
                          for s in steps if abs(s["coherence"]) > B.Z]

    log("the ideal spine at the card's centre, and new populations from the card")
    centre = B.simulate(card, B.ALL, PEOPLE_CENTRE, np.random.default_rng(SEED_CENTRE), centre=True)
    checks = {"centre": compact(B.check(centre, card))}
    checks["drawn"] = drawn(card, B.ALL, args.populations, PEOPLE_DRAWN, SEED_DRAWN, skip)

    log("the generator on Panjabi's table, and the nearest point")
    near = nearest_settings(args.records)
    found, generator_true = generator_checks(card, steps, near, kinds)
    checks.update(found)
    checks["settings"] = {"generator": GENERATOR.as_dict(), NEAREST: near.as_dict()}

    log("the ideal spine with its lumbar gradient broken")
    reverse = dict(zip(LUMBAR, LUMBAR[::-1]))
    checks["reversed lumbar"] = broken(card, B.with_levels(centre, reverse), "L1 to L5 reversed in every measure", variants)
    checks["flattened lumbar"] = broken(card, B.flattened(centre, LUMBAR),
                                        "every measure's L1 to L5 means set to their run's mean, the spread kept", variants)
    detail = incoherent_detail(card, B.ALL, skip)
    checks["drawn"]["why_below_the_step_bar"] = why_below_the_step_bar(
        checks["drawn"], skip, steps, detail, held_out_steps(verdicts, chosen))

    log("the sensitivity to the within-person correlation, and the borrowing rules")
    step_r = {"chosen": chosen, "bounds_py_default": B.STEP_R, "default_matches": chosen == B.STEP_R,
              "rule": "the r of the grid whose held-out step coverage, pooled over every held-out step under the steps' "
                      "borrowing rule, is nearest the nominal %.2f, the smaller r where two are as near" % B.NOMINAL,
              "variance": "a paper's step variance is sd_a^2 / n_a + sd_b^2 / n_b - 2 r sd_a sd_b / max(n_a, n_b)",
              "at_the_grids_edge": chosen in (min(B.STEP_R_GRID), max(B.STEP_R_GRID)),
              "caveat": "the left-out paper's own step variance is read at the card's r, so a smaller r widens the "
                        "test as well as the card and coverage alone cannot tell a right r from a lenient one; the "
                        "sensitivity reads the paper's own at every r of its set apart (held_out_steps_by_test_r)",
              "grid": grid,
              "sensitivity": sensitivity(series, rows, voc, register, verdicts, generator_true)}
    card_median = B.build(series, rows, voc, register, r=chosen, step_rule=B.MEDIAN, kinds=(B.ALL,), sex_rows=sex_rows)
    log("the covariates' spreads under both borrowing rules, and the sex contrasts' signs held out")
    card_cov_median = B.build(series, rows, voc, register, r=chosen, kinds=(B.ALL,), sex_rows=sex_rows,
                              covariate_rule=B.MEDIAN)
    cov = covariate_borrowing(card, card_cov_median, B.covariate_items(rows, voc, sex_rows), register)

    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    with open(PT.SOURCE_SEXES, encoding="utf-8") as fh:
        sexes_source = json.load(fh)
    every_count = {k: counts(card, k) for k in kinds}
    write_json(out, "bounds.json", {
        "command": "python3 -I run_bounds.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "snapshot_sexes": {"commit": sexes_source["commit"], "sha256": sexes_source["snapshot_sha256"],
                           "rows": sexes_source["rows"]},
        "reference_n_measured": B.reference_n_measured(series, register, cal_rows),
        "kinds": kinds, "kind_variable": "the register's specimen (data/populations.csv); every paper together is 'all'",
        "kinds_with_no_sex_or_age_cell": [k for k in kinds if not every_count[k]["cells_with_sex_contrast"]
                                          and not every_count[k]["cells_with_age_slope"]],
        "counts": every_count,
        "series_not_in_register": sorted({"%s/%s" % (s.paper, s.cohort) for s in B.series_of_kind(series, register, B.ALL)
                                          if B.specimen_of(s.paper, s.cohort, register) == B.NOT_IN_REGISTER}),
        "borrowed": card.borrowed,
        "borrowing": borrowing(card, card_median, verdicts, chosen),
        "step_r": step_r,
        "covariate_borrowing": cov,
        "calibration": calibration_record(verdicts, cal_rows, bars, chosen, sorted(specimens), kind_rows),
        "steps_whose_ends_spread_apart_more_than_the_step": dict(
            {"count": len(skip), "of": len(steps),
             "rule": "the two levels' betweens differ by more than the step's (incoherent_spreads)",
             "meaning": "no population of populations has both levels' spreads of a new population's mean and the "
                        "step's own spread, since the SD of a difference is at least the difference of the SDs; "
                        "checks.drawn.why_below_the_step_bar says what it does to populations drawn from the card"},
            **detail),
        "steps_whose_pooled_means_sit_off_the_step": {"count": len(incoherent_centres), "of": len(steps),
                                                      "rule": "|coherence| above %.2f" % B.Z, "steps": incoherent_centres},
        "checks": checks,
        "not on the card": NOT_ON_THE_CARD,
        "rules": {"z": B.Z, "nominal": B.NOMINAL, "min_series_for_tau": B.MIN_SERIES_FOR_TAU,
                  "tau_counts": {"mean": "series: a paper printing several cohorts gives several, the row's k; its "
                                         "papers are the row's papers",
                                 "sd": "populations, one a paper (the strata)", "step": "papers",
                                 "sex and age": "papers"},
                  "cohort_sampling": "every interval widened by the cohort's own sampling error",
                  "sex_test": "the cohort's men minus women has the papers' sign where the 95% interval for a new "
                              "population's contrast, tau included and borrowed below three papers under the "
                              "covariates' rule (covariate_borrowing), excludes zero; it carries no bar and enters "
                              "no verdict",
                  "bar": "each of the mean, SD and step tests' pass rate against the %.0fth percentile of the kind's "
                         "held-out papers' own rates, over the papers with %d rows or more of the test, a test with "
                         "fewer than %d such papers having no bar (calibration.bar_rule)"
                         % (100 * B.BAR_LOW, B.MIN_BAR_ROWS, B.MIN_BAR_PAPERS),
                  "verdict": "a test passes at or above its bar; the cohort fails where any test with a bar fails "
                             "and passes only where the step test was made and passes its bar, since naming lives "
                             "on the steps; the pass rate over every test decides nothing (bounds.verdict)"},
        "seeds": {"drawn": SEED_DRAWN, "centre": SEED_CENTRE, "generator": SEED_GENERATOR},
        "sizes": {"populations": args.populations, "people_drawn": PEOPLE_DRAWN, "people_centre": PEOPLE_CENTRE,
                  "people_generator": PEOPLE_GENERATOR},
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "code": code})
    log("done in %d s: %d cells and %d steps over %d kinds, r = %.1f" % (round(time.time() - started), len(card.cells),
                                                                          len(card.steps), len(kinds), chosen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
