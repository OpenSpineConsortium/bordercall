"""The power calculations rerun on the 39 papers, and what a count of gold persons can test.

research_notes/cadaver-power measured how far published studies disagree from Panjabi's own
comparison tables (part B: 86 cells of 10 measures, three or more of 14 studies each, a median
spread of 0.39 of a person's SD once sampling error is out), and from it what a meta-analysis is
worth in scans of the population named (part A) and what a rule built on such a table loses in
naming (part C). The reread now gives the 39 papers' own series (literature.py), so part B is
taken again from them: in every cell with three or more series the REML spread between series,
tau, which the series' own SEs have already been taken out of, over the person's SD. Two SDs
are used, Panjabi's at that level, as part B used, and the pooled published SD.

Part A's worth follows as cadaver_power.part_a has it: an infinite pool of published series is
worth at most r / f^2 scans of the population named, r = 1 + (e / sd)^2 the share a CT's error
adds to a person's variance. Part C's rule is run again here on synthetic columns with its table
moved by the new spread (shifted_table), at 1, 3 and 9 bodies, so the loss reads against the same
rule built on its own table.

gold_power says what n persons with whole spines can test of the generator: the least shift of a
level's mean, in a person's SD, a two-sided test finds with 80 per cent power (one cell, and with
a Bonferroni split over the seven SPINEPS measures' 154 cells); the least SD ratio; the half-width
of the 95 per cent interval of a correlation of 0.5 between neighbouring levels, the number no
table gives; and how many columns of each anomaly the papers' prevalences lead one to expect.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence

import numpy as np
from scipy import optimize, stats

from schwingcheck import LEVELS
from schwingcheck import measures as MS

from . import literature as L
from . import pooling as P
from . import references as REF
from .validate import MODALITY_SETS, cells, validated_measures

ALPHA = 0.05
POWER = 0.80
SEVEN_CELLS = 7 * len(LEVELS)
GOLD_COUNTS = (12, 17, 50, 142, 159, 300, 1000, 2000)    # 159 held: TotalSegmentator 142, VerSe 17 (holdings/gold-tier-3.md)
OLD_PART_B = {"median_f": 0.39, "cells": 86, "measures": 10, "studies": 14,
              "source": "research_notes/cadaver-power/README.md, part B (between_studies.json, f_low)"}


def _cells_of_three(series: Sequence[L.Series], modality_set: str, measures: Optional[Sequence[MS.Measure]]):
    """(measure, its key, Panjabi's SD at the level, level, the cell's series) for every cell with
    three usable series or more."""
    measures = validated_measures(measures)
    by = cells(series, MODALITY_SETS[modality_set])
    _, sd = MS.arrays(measures, LEVELS)
    for j, m in enumerate(measures):
        key = L.measure_key(m.key)
        for i, level in enumerate(LEVELS):
            rows = by.get((key, level), [])
            if len(rows) >= 3:
                yield m, key, float(sd[j, i]), level, rows


def between_series(series: Sequence[L.Series], modality_set: str = "bone_ct",
                   measures: Optional[Sequence[MS.Measure]] = None) -> List[dict]:
    """Every (measure, level) with three or more usable series: tau, and tau over Panjabi's SD
    and over the pooled published SD."""
    seven = set(MS.SPINEPS_7)
    out = []
    for m, key, psd, level, rows in _cells_of_three(series, modality_set, measures):
        pooled = P.pool_means([s.mean for s in rows], [s.sd for s in rows], [s.n for s in rows])
        certain = [s for s in rows if not s.sd_uncertain]
        lit_sd = P.pooled_sd([s.sd for s in certain], [s.n for s in certain]) if certain else float("nan")
        r = 1.0 + (m.error / psd) ** 2
        out.append({"measure": key, "level": level, "kind": m.kind, "seven": key in seven, "k": len(rows),
                    "papers": ";".join(sorted({s.paper for s in rows})), "tau": pooled.tau,
                    "panjabi_sd": psd, "literature_sd": lit_sd, "i2": pooled.i2,
                    "f_panjabi": pooled.tau / psd,
                    "f_literature": pooled.tau / lit_sd if lit_sd > 0 else float("nan"),
                    "r": float(r), "worth_scans_panjabi_sd": float(r / max(pooled.tau / psd, 1e-9) ** 2)})
    return out


def spread_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Medians and quartiles of f over all cells, the seven's cells and each measure."""
    def q(a):
        a = np.array([x for x in a if math.isfinite(x)])
        if not len(a):
            return {"cells": 0}
        return {"cells": int(len(a)), "q1": float(np.quantile(a, 0.25)), "median": float(np.median(a)),
                "q3": float(np.quantile(a, 0.75)), "at_zero": int((a < 1e-6).sum())}
    groups = {"all": rows, "seven": [r for r in rows if r["seven"]]}
    for key in sorted({r["measure"] for r in rows}):
        groups[key] = [r for r in rows if r["measure"] == key]
    return {g: {"f_panjabi": q([r["f_panjabi"] for r in rs]), "f_literature": q([r["f_literature"] for r in rs]),
                "worth_scans": q([r["worth_scans_panjabi_sd"] for r in rs])} for g, rs in groups.items()}


CALIBRATION_REPLICATES = 400
CALIBRATION_SEED = 4103


def calibrated_median_f(series: Sequence[L.Series], scale: str = "panjabi", only_seven: bool = False,
                        modality_set: str = "bone_ct", replicates: int = CALIBRATION_REPLICATES,
                        seed: int = CALIBRATION_SEED) -> Dict[str, float]:
    """The median f corrected for REML's downward pull at three to seven series, where tau^2 often
    comes out at zero: the f that, given to every cell with its own series' SEs and count, makes
    the expected median of the estimates over the cells equal to the median observed. The same
    normal draws serve every f tried (common random numbers), so the expected median rises with f
    and a bisection finds it. One f for every cell is an assumption: it corrects the median, not
    the spread of f between measures. scale is "panjabi" (tau over his SD) or "literature" (over
    the pooled published SD, Tan's left out)."""
    rows = [r for r in between_series(series, modality_set) if r["seven"] or not only_seven]
    key = "f_panjabi" if scale == "panjabi" else "f_literature"
    rows_by = {(r["measure"], r["level"]): r for r in rows}
    rng = np.random.default_rng(seed)
    cells_ = []
    for _, key_, psd, level, found in _cells_of_three(series, modality_set, None):
        r = rows_by.get((key_, level))
        if r is None or not math.isfinite(r[key]):
            continue
        v = np.array([s.sd ** 2 / s.n for s in found])
        size = psd if scale == "panjabi" else r["literature_sd"]
        cells_.append((v, size, rng.normal(size=(replicates, len(v))), rng.normal(size=(replicates, len(v)))))
    observed = float(np.median([rows_by[k][key] for k in rows_by if math.isfinite(rows_by[k][key])]))

    def expected(f: float) -> float:
        got = np.empty((replicates, len(cells_)))
        for c, (v, size, between, within) in enumerate(cells_):
            t2, _ = P.reml_rows(f * size * between + np.sqrt(v) * within, v)
            got[:, c] = np.sqrt(t2) / size
        return float(np.median(got, axis=1).mean())

    lo, hi = 0.0, 2.0 * observed + 0.5
    while expected(hi) < observed:
        hi *= 2.0
    for _ in range(40):
        mid = (lo + hi) / 2.0
        lo, hi = (mid, hi) if expected(mid) < observed else (lo, mid)
    f = (lo + hi) / 2.0
    median_r = float(np.median([r["r"] for r in rows]))
    return {"cells": len(cells_), "observed_median": observed, "calibrated_median": f,
            "expected_median_if_true_were_observed": expected(observed),
            "worth_scans_at_calibrated": median_r / f ** 2 if f > 0 else float("inf")}


def least_shift(n: int, tests: int = 1, alpha: float = ALPHA, power: float = POWER) -> float:
    """The least difference of means, in a person's SD, that n people find against a published mean
    by a two-sided one-sample t test (the SD estimated from the same people), from the noncentral t."""
    df, crit = n - 1, stats.t.ppf(1 - alpha / (2 * tests), n - 1)

    def short(nc):
        lower = stats.nct.cdf(-crit, df, nc)
        return stats.nct.sf(crit, df, nc) + (lower if math.isfinite(lower) else 0.0) - power
    return float(optimize.brentq(short, 0.0, 40.0) / math.sqrt(n))


def least_sd_ratio(n: int, alpha: float = ALPHA, power: float = POWER) -> float:
    """The least SD ratio above 1 that n people find against a published SD, by the upper tail of
    the two-sided chi-square test of (n - 1) s^2 / sd0^2 on n - 1 degrees of freedom."""
    return float(math.sqrt(stats.chi2.ppf(1 - alpha / 2, n - 1) / stats.chi2.ppf(1 - power, n - 1)))


def correlation_half_width(n: int, r: float = 0.5) -> float:
    h = 1.959964 / math.sqrt(n - 3)
    return float((math.tanh(math.atanh(r) + h) - math.tanh(math.atanh(r) - h)) / 2)


def gold_power(counts: Sequence[int] = GOLD_COUNTS) -> List[dict]:
    out = []
    for n in counts:
        row = {"persons": n, "least_mean_shift_one_cell": least_shift(n),
               "least_mean_shift_154_cells": least_shift(n, SEVEN_CELLS), "least_sd_ratio": least_sd_ratio(n),
               "neighbour_r_half_width": correlation_half_width(n)}
        for state, _, _, point, lo, hi, _ in REF.PREVALENCE:
            if math.isfinite(point):
                row["expected: " + state] = n * point
        out.append(row)
    return out


def shifted_table(mu: np.ndarray, sd: np.ndarray, rng: np.random.Generator, shift: float = 0.0,
                  level: float = 0.0) -> np.ndarray:
    """A table from another population: every measure's means moved together by `shift` person
    SDs (one draw per measure), and every cell apart by `level` (one draw per level), as
    shift_profile.py split the disagreement of Panjabi's comparison tables."""
    together = np.repeat(rng.normal(size=(mu.shape[0], 1)), mu.shape[1], 1)
    apart = rng.normal(size=mu.shape)
    return mu + sd * (shift * together + level * apart)


# (name, shift, level-by-level): part C's readings run again beside the 39 papers' (run.py adds
# those from shift_split): its 0.3 SD level by level, to check this rule against its table, and its
# seven-r0, the seven's comparison tables read consistently (cadaver_power.DISAGREEMENTS; the
# thoracic and lumbar shifts there are drawn apart with correlation 0.7, here as one).
ARMS = (
    ("part C, 0.3 SD level by level", 0.0, 0.3),
    ("part C, seven-r0", 0.57, 0.0),
)


def naming_loss(arms: Sequence[tuple], widths: Sequence[int] = (1, 3, 9), columns: int = 300, tables: int = 4,
                column_seed: int = 4101, table_seed: int = 4102) -> List[dict]:
    """Part C again: the exact rule on `columns` typical columns of the seven SPINEPS measures with
    their CT errors, built on the generator's own table and on `tables` tables moved as each arm
    (name, shift, level) says, scored at each width. Each row is one table at one width; loss is
    in points of the share named exactly, against the rule's own table on the same columns."""
    from . import naming as N
    from .population import GENERATOR, draw
    seven = MS.select(MS.SPINEPS_7)
    pop = draw(GENERATOR, columns, column_seed, seven)
    mu, sd = MS.arrays(seven, LEVELS)
    out = []
    for w in widths:
        own = N.score(pop, seven, w)
        out.append(dict(own, arm="own table", shift=0.0, level=0.0, table=0, width=w, loss=0.0))
        rng = np.random.default_rng(table_seed)
        for name, shift, level in arms:
            for t in range(tables):
                got = N.score(pop, seven, w, table=(shifted_table(mu, sd, rng, shift, level), sd))
                out.append(dict(got, arm=name, shift=float(shift), level=float(level), table=t, width=w,
                                loss=100.0 * (own["exact"] - got["exact"])))
    return out


def _split_layout(series: Sequence[L.Series], modality_set: str, measures: Optional[Sequence[MS.Measure]]) -> dict:
    """The cells with three series or more, flattened: each series' cell, Panjabi's SD there, its
    within-series variance, and the (paper, cohort, measure) it belongs to."""
    cell_cols, means, psd, var, group = [], [], [], [], []
    names: Dict[tuple, int] = {}
    for _, key, sd_p, _, rows in _cells_of_three(series, modality_set, measures):
        start = len(means)
        for s_ in rows:
            means.append(s_.mean)
            psd.append(sd_p)
            var.append(s_.sd ** 2 / s_.n)
            group.append(names.setdefault((s_.paper, s_.cohort, key), len(names)))
        cell_cols.append(np.arange(start, len(means)))
    return {"cells": cell_cols, "means": np.array(means), "psd": np.array(psd), "var": np.array(var),
            "group": np.array(group), "groups": len(names)}


def _split_estimate(lay: dict, y: np.ndarray) -> tuple:
    """shift_split's moment estimates for every row of y (replicates by series): each distance
    from its cell's pooled mean in Panjabi's SD; per (paper, cohort, measure) with two levels or
    more, the mean distance is its shift and the rest is level by level. Within a group of m
    levels the residuals keep (1 - 1/m) of the level-by-level variance and of the sampling
    variance, and the shift's variance carries 1/m of each, so both are taken out."""
    x = np.empty_like(y)
    for cols in lay["cells"]:
        _, mu = P.reml_rows(y[:, cols], lay["var"][cols])
        x[:, cols] = (y[:, cols] - mu[:, None]) / lay["psd"][cols]
    e2 = lay["var"] / lay["psd"] ** 2
    m = np.bincount(lay["group"], minlength=lay["groups"])
    keep = m[lay["group"]] >= 2
    g = lay["group"][keep]
    used = np.unique(g)
    sums = np.zeros((len(y), lay["groups"]))
    np.add.at(sums.T, g, x[:, keep].T)
    shift = sums / np.maximum(m, 1)
    resid = x[:, keep] - shift[:, g]
    mk = m[g].astype(float)
    level2 = ((resid ** 2).mean(1) - (e2[keep] * (1 - 1 / mk)).mean()) / (1 - 1 / mk).mean()
    level2 = np.maximum(0.0, level2)
    e2_shift = np.bincount(g, weights=e2[keep], minlength=lay["groups"])[used] / m[used] ** 2
    shift2 = shift[:, used].var(axis=1, ddof=1) - e2_shift.mean() - level2 * (1.0 / m[used]).mean()
    return np.sqrt(np.maximum(0.0, shift2)), np.sqrt(level2), int(len(used)), int(keep.sum())


def split_recovery(series: Sequence[L.Series], truth: Sequence[float] = (0.9, 0.4), trials: int = 24,
                   seed: int = 4104, modality_set: str = "bone_ct") -> Dict[str, object]:
    """Whether the calibration finds a known pair: `trials` sets of series laid out as the papers'
    are, drawn with shift and level-by-level parts `truth`, each split and calibrated as the papers'
    series are; the mean of each estimate over the trials and its standard error."""
    lay = _split_layout(series, modality_set, None)
    rng = np.random.default_rng(seed)
    got = []
    for t in range(trials):
        a = rng.normal(size=lay["groups"])[lay["group"]]
        b = rng.normal(size=len(lay["means"]))
        e = rng.normal(size=len(lay["means"]))
        drawn = dict(lay, means=lay["psd"] * (truth[0] * a + truth[1] * b) + np.sqrt(lay["var"]) * e)
        r = _calibrated_split(drawn, seed=CALIBRATION_SEED + 1 + t)
        got.append([r["shift_sd"], r["level_sd"], r["shift_sd_calibrated"], r["level_sd_calibrated"]])
    got = np.array(got)
    names = ("shift_sd", "level_sd", "shift_sd_calibrated", "level_sd_calibrated")
    return {"truth": {"shift_sd": float(truth[0]), "level_sd": float(truth[1])}, "trials": trials,
            "mean": dict(zip(names, map(float, got.mean(0)))),
            "standard_error": dict(zip(names, map(float, got.std(0, ddof=1) / math.sqrt(trials))))}


def shift_split(series: Sequence[L.Series], modality_set: str = "bone_ct",
                measures: Optional[Sequence[MS.Measure]] = None, replicates: int = 200,
                seed: int = CALIBRATION_SEED) -> Dict[str, float]:
    """How the spread between series splits, as shift_profile.py split Panjabi's comparison
    tables: each series' distance from the pooled mean of its cell, in Panjabi's SD, over the cells
    with three or more series; per paper and measure the mean of its distances over the levels it
    covers (the shift a population carries through a measure), and what is left level by level,
    with the sampling error and each part's share of the other taken out (_split_estimate).

    The pooled mean a distance is measured from holds the series itself and the same paper's
    shift, so the moments still read low; the calibrated pair is the (shift, level) that, put
    into series laid out as the papers' are (their cells, counts and SEs), gives on average the
    moments the papers give, found by fixed-point iteration on common random numbers. Part C's
    arms take the calibrated pair."""
    return _calibrated_split(_split_layout(series, modality_set, measures), replicates, seed)


def _calibrated_split(lay: dict, replicates: int = 200, seed: int = CALIBRATION_SEED) -> Dict[str, float]:
    shift_sd, level_sd, groups, distances = _split_estimate(lay, lay["means"][None, :])
    observed = np.array([shift_sd[0], level_sd[0]])
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(replicates, lay["groups"]))[:, lay["group"]]
    b = rng.normal(size=(replicates, len(lay["means"])))
    e = rng.normal(size=(replicates, len(lay["means"])))
    sampling = np.sqrt(lay["var"]) * e

    def expected(theta: np.ndarray) -> np.ndarray:
        y = lay["psd"] * (theta[0] * a + theta[1] * b) + sampling
        s_, l_, _, _ = _split_estimate(lay, y)
        return np.array([s_.mean(), l_.mean()])

    theta = observed.copy()
    for step in range(100):
        new = np.maximum(0.0, theta + observed - expected(theta))
        moved = float(np.abs(new - theta).max())
        theta = new
        if moved < 1e-5:
            break
    return {"series_measures": groups, "distances": distances, "shift_sd": float(observed[0]),
            "level_sd": float(observed[1]), "total": float(math.hypot(*observed)),
            "shift_sd_calibrated": float(theta[0]), "level_sd_calibrated": float(theta[1]),
            "total_calibrated": float(math.hypot(*theta)), "calibration_steps": step + 1}
