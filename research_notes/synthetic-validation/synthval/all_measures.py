"""The state space, the naming and the spread between papers read on every measure's table.

The first part of this note reads the generator's 32 measures. This module does the same work on
the tables papers_table.py builds from every measure of the reread: Panjabi's own at every level
he prints a spread (A), the papers' pooled values (B) and the two together (C). The populations are
population.draw_table's, so a cell no paper prints is missing and skipped.

- read_point reads one point of the state space of a table: the median SD of the true anatomy over
  the table's own SD (1 is the table's, as validate.py's SD ratio has 1 for the papers'), Griffith's
  four correlations of L1-L5 subject means (structure.GRIFFITH, his body area read directly where
  the table holds Griffith's body area, else as the two end-plate areas), the correlation of
  neighbouring levels, and every indicator of relations.py; nearest searches sweep.GRID with
  sweep.distance, so a table's nearest point is found as the generator's was;
- naming scores the rule on fields drawn from one table and built on a subset of its measures that
  is complete over the column scored (naming.py's rule, the table's own errors and powers), the
  whole column C3 to L5 or the lumbar run L1 to L5 alone, where a field is known to be lumbar and
  the question is which lumbar level, so that the measures the papers add, most of them lumbar,
  can be scored;
- spread is power.py's part B on every pooled cell with three series or more: tau over the cell's
  SD, by measure, with the worth of an infinite pool of series in scans, (sd^2 + e^2) / tau^2.
"""
from __future__ import annotations

import itertools
import math
from typing import Dict, List, Optional, Sequence

import numpy as np

from schwingcheck import columns as C
from schwingcheck import rule as R
from schwingcheck import score as S

from . import relations as REL
from . import structure as ST
from . import sweep as SW
from .naming import CHUNK, CLAIM
from .papers_table import Table
from .population import GENERATOR, Population, Settings, calibrated, draw_table

LUMBAR = list(ST.LUMBAR)


# ---- one point of a table's state space ---------------------------------------------------------

def sd_ratio(pop: Population, table: Table, which: str = "true") -> Dict[str, float]:
    """The median, quartiles and count of the SD over people of each finite cell over the table's SD."""
    x = getattr(pop, which)
    with np.errstate(invalid="ignore"):
        s = np.nanstd(x, 0, ddof=1).T                        # (measures, levels)
    ok = np.isfinite(table.sd) & (table.sd > 0) & np.isfinite(s) & (np.sum(np.isfinite(x), 0).T > 2)
    r = s[ok] / table.sd[ok]
    if r.size == 0:
        return {"median": float("nan"), "q1": float("nan"), "q3": float("nan"), "cells": 0}
    q1, med, q3 = np.quantile(r, [0.25, 0.5, 0.75])
    return {"median": float(med), "q1": float(q1), "q3": float(q3), "cells": int(r.size)}


def _subject_means(pop: Population, key: str, which: str) -> Optional[np.ndarray]:
    if key not in pop.keys:
        return None
    lumbar = [pop.level_index(lv) for lv in LUMBAR]
    with np.errstate(invalid="ignore"):
        return np.nanmean(getattr(pop, which)[:, lumbar, pop.keys.index(key)], 1)


def griffith_r(pop: Population, which: str = "true") -> Dict[str, float]:
    """Griffith's four correlations of L1-L5 subject means on the population: his body area read
    directly where the table holds it (B and C), else as structure.py reads it, each end-plate area
    in turn and the two correlations averaged (A and the generator)."""
    out = {}
    for a, b, _, _ in ST.GRIFFITH:
        xs = ["body_area"] if (a == "body_area" and "body_area" in pop.keys) else (list(ST.BODY_AREA) if a == "body_area" else [a])
        ys = ["body_area"] if (b == "body_area" and "body_area" in pop.keys) else (list(ST.BODY_AREA) if b == "body_area" else [b])
        rs = []
        for x in xs:
            for y in ys:
                u, v = _subject_means(pop, x, which), _subject_means(pop, y, which)
                if u is None or v is None:
                    continue
                keep = np.isfinite(u) & np.isfinite(v)
                if keep.sum() > 2:
                    rs.append(np.corrcoef(u[keep], v[keep])[0, 1])
        out["griffith %s~%s" % (a, b)] = float(np.mean(rs)) if rs else float("nan")
    return out


def neighbour_r(pop: Population, which: str = "true") -> float:
    """The median over measures and lumbar levels of the correlation of a level with the next, over
    the people with both."""
    x = getattr(pop, which)
    idx = [pop.level_index(lv) for lv in LUMBAR]
    rs = []
    for m in range(x.shape[2]):
        for a, b in zip(idx, idx[1:]):
            u, v = x[:, a, m], x[:, b, m]
            keep = np.isfinite(u) & np.isfinite(v)
            if keep.sum() > 2:
                rs.append(np.corrcoef(u[keep], v[keep])[0, 1])
    return float(np.nanmedian(rs)) if rs else float("nan")


def read_point(table: Table, settings: Settings, n: int, seed: int) -> dict:
    """Spread, correlations and indicators of one point's population drawn from the table."""
    pop = draw_table(table, settings, n, seed)
    t, m = sd_ratio(pop, table, "true"), sd_ratio(pop, table, "measured")
    out = dict(settings.as_dict(), table=table.name, n=n, seed=seed, clipped=pop.clipped, clipped_size_passes=pop.size_passes,
               sd_ratio_true=t["median"], sd_ratio_measured=m["median"], sd_ratio_true_q1=t["q1"], sd_ratio_true_q3=t["q3"],
               sd_cells=t["cells"], neighbour_r=neighbour_r(pop))
    out.update(griffith_r(pop))
    fl, _ = REL.flags_all(pop)
    for k, v in REL.vertebra_rates(fl).items():
        out["qi vertebra " + k] = v
    for k, v in REL.person_rates(fl).items():
        out["qi person " + k] = v
    return out


def grid_points(grid: Dict[str, Sequence] = SW.GRID) -> List[dict]:
    """The grid's points in one fixed order, the product of its axes as listed, so that a point has
    a number a Slurm array task can take and a merge can put the points back in this order."""
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[k] for k in keys))]


def grid_point(table: Table, kw: dict, n: int = 4000, seed: int = 11, base: Settings = GENERATOR) -> dict:
    """One grid point read on the table, with its distance."""
    st = base.but(name="grid " + " ".join("%s=%s" % kv for kv in kw.items()), **kw)
    p = read_point(table, st, n, seed)
    p["distance"] = SW.distance(p)
    return p


def nearest(table: Table, n: int = 4000, seed: int = 11, grid: Dict[str, Sequence] = SW.GRID,
            base: Settings = GENERATOR, points: Optional[List[dict]] = None) -> List[dict]:
    """Every grid point of sweep.GRID read on the table and scored by sweep.distance, nearest first;
    given `points`, the rows already read in grid_points order (a Slurm array's), sorted the same."""
    out = points if points is not None else [grid_point(table, kw, n, seed, base) for kw in grid_points(grid)]
    return sorted(out, key=lambda p: p["distance"])


def one_at_a_time(table: Table, n: int, seed: int, axes: Dict[str, Sequence] = SW.AXES,
                  base: Settings = GENERATOR) -> List[dict]:
    """sweep.one_at_a_time's points read on the table."""
    return [read_point(table, st, n, seed) for st in SW.one_at_a_time(axes, base)]


# ---- the relations at one point -------------------------------------------------------------------

def quality(table: Table, settings: Settings, n: int, seed: int) -> dict:
    """Every indicator and every relation on one population of the table."""
    pop = draw_table(table, settings, n, seed)
    fl, rows = REL.flags_all(pop)
    return {"table": table.name, "setting": settings.name, "measures": len(table.keys), "cells": table.cells(),
            "vertebra": REL.vertebra_rates(fl), "person": REL.person_rates(fl), "tests": dict(fl.tests), "relations": rows}


# ---- naming on a table ----------------------------------------------------------------------------

def rule_for(table: Table, settings: Settings):
    """The table, synth settings, errors and powers of a rule built on a table at these settings."""
    power = table.power * np.array([settings.loading(k) for k in table.keys])
    mu, sd, _ = calibrated(table.mu, table.sd * settings.sd_scale, power, settings)
    synth = {"rho": settings.rho, "noise_mm": 1.0, "scale_sd": settings.scale_sd}
    return mu, sd, synth, table.error * settings.error_scale, power


def score(pop: Population, table: Table, subset: Sequence[int], width: int, levels: Sequence[str],
          rule_settings: Settings) -> Dict[str, float]:
    """naming.score on the fields of `width` bodies in the run of `levels` of every person's column,
    the rule built on the measures `subset` of the table over those levels; every measure of the
    subset must be complete over them."""
    sub = table.subset(subset).over(levels)
    missing = [sub.keys[j] for j in range(len(sub.keys)) if j not in sub.complete_over(levels)]
    if missing:
        raise ValueError("not complete over %s to %s: %s" % (levels[0], levels[-1], ", ".join(missing)))
    idx = [pop.keys.index(k) for k in sub.keys]
    li = [pop.level_index(lv) for lv in levels]
    X, truth, group = C.fields(pop.measured[:, li][:, :, idx], list(range(width)))
    mu, sd, synth, noise, power = rule_for(sub, rule_settings)
    post = R.name(X, list(range(width)), mu, sd, synth, noise=noise, power=power, chunk=CHUNK)["all"]
    call, top = post.argmax(1), post.max(1)
    hit = (call == truth).astype(float)
    ans = top >= CLAIM
    groups = np.unique(group, return_inverse=True)[1]
    wrong = np.bincount(groups, weights=ans & (hit == 0))
    answered = np.bincount(groups, weights=ans)
    return {"fields": int(len(truth)), "columns": int(pop.true.shape[0]), "places": int(post.shape[1]),
            "exact": float(hit.mean()), "exact_se": S.clustered_se(hit, group),
            "within_one": float((np.abs(call - truth) <= 1).mean()),
            "answered": float(ans.mean()), "answered_se": S.clustered_se(ans.astype(float), group),
            "n_answered": int(ans.sum()), "errors": int((ans & (hit == 0)).sum()),
            "precision": float(hit[ans].mean()) if ans.any() else float("nan"),
            "precision_se": S.ratio_se(wrong, answered) if ans.any() else float("nan"),
            "mean_top": float(top.mean()), "bayes_error_predicted": float((1.0 - top).mean()),
            "bayes_error_counted": float(1.0 - hit.mean())}


# ---- the spread between papers on every measure ----------------------------------------------------

def spread(cells: Sequence[dict], errors: Dict[str, float], panjabi_keys: Sequence[str]) -> List[dict]:
    """power.py's part B on every pooled cell with three series or more: tau over the cell's SD and
    the worth of an infinite pool in scans, (sd^2 + e^2) / tau^2, e the measure's error."""
    out = []
    for c in cells:
        if c["k"] < 3 or not (math.isfinite(c["tau"]) and c["sd"] > 0):
            continue
        e = errors.get(c["measure"], errors.get(c["base_key"], 0.0))
        tau, sd = c["tau"], c["sd"]
        out.append({"measure": c["measure"], "base_key": c["base_key"], "level": c["level"], "placed_at": c["placed_at"],
                    "panjabi": c["base_key"] in panjabi_keys, "k": c["k"], "papers": c["papers"], "tau": tau, "sd": sd,
                    "f": tau / sd, "worth_scans": (sd ** 2 + e ** 2) / tau ** 2 if tau > 0 else float("inf"),
                    "sd_from": c["sd_from"]})
    return out


def spread_summary(rows: Sequence[dict]) -> Dict[str, dict]:
    """Median tau over SD and cells, over every cell, Panjabi's measures and the others."""
    def summary(mine):
        fs = [r["f"] for r in mine]
        return {"cells": len(mine), "measures": len({r["measure"] for r in mine}),
                "median_f": float(np.median(fs)) if fs else float("nan"),
                "q1_f": float(np.quantile(fs, 0.25)) if fs else float("nan"),
                "q3_f": float(np.quantile(fs, 0.75)) if fs else float("nan"),
                "share_f_over_half": float(np.mean([x > 0.5 for x in fs])) if fs else float("nan")}
    return {"all": summary(list(rows)), "panjabi's measures": summary([r for r in rows if r["panjabi"]]),
            "the papers' own": summary([r for r in rows if not r["panjabi"]])}
