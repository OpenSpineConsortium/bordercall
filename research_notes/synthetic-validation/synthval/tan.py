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
DISPERSION_UNCERTAIN), so only Tan's means are used here.
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

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
