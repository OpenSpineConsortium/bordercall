"""Every paper's population kept apart, and the rule predicted for one more.

papers_table.pooled_cells pools each cell's series by random effects (pooling.py: the REML
spread between populations, tau, and Higgins's prediction interval for one more population's
mean), so the papers are combined as a meta-analysis combines them. Downstream, the tables B and
C and the rule built on them keep only the pooled mean and the within-person SD: a population
drawn from such a table is every paper merged into one, and tau is read (all_measures.spread)
but never used. The owner's word of 2026-10-29, 23:43 UTC: keep the populations separate and
predict as a meta-analysis predicts, never merge them all together.

This module keeps each paper a population of its own and asks what the rule built on the others
does on it, on the lumbar run, where most of the papers print:

- strata_of: every placed cell (papers_table.pooled_cells's grouping and modality class), each
  paper's series a stratum of its own, its cohorts pooled where it prints several, and the cell's
  random-effects pool over every paper, as the records hold it;
- pooled_without: the same cell pooled over the other papers alone, so that no paper is in the
  table that names it;
- between: the SD of one more population's mean, sqrt(tau^2 + SE^2), Higgins's half-width with
  no t; a cell with fewer than MIN_SERIES_FOR_TAU series has no tau of its own and takes its
  measure's median tau over the cell's SD from the cells that have one, else every cell's, and
  says so (tau_from);
- predictive_sd: the SD a person of a population the rule has not seen is drawn with,
  sqrt(sd^2 + tau^2 + SE^2), which is what the rule's table carries when it names such a one;
- leave_one_out: the rule scored on fields drawn from each paper's own population, on the
  measures the paper prints at every lumbar level and the others still pool there, built four
  ways and read on the same fields, so the arms are paired: the paper's own table (the loss's
  zero), the others' pooled table as tables B and C hold it (MERGED), the same means with the
  predictive SD (PREDICTED), and the paper's own means with the others' SD (SD_ONLY), whose loss
  is what the SD difference alone costs, the rest of MERGED's being the shift of the means;
- pooled_losses: the per-paper losses combined by random effects (pooling.pool), the loss one
  more population is predicted to bring, with its interval: the meta-analysis of the strata;
- new_populations: part C's reading on the papers' pooled table, populations drawn from the
  random-effects model itself (each cell's mean moved by `between`, a share of it one shift
  through a whole measure and the rest level by level, the split the first part calibrated),
  with the merged and the predicted rules scored on each.

Everything is synthetic but the papers' numbers. Tan 2004's SDs stay out of every table's SD, as
the validation leaves them out (literature.DISPERSION_UNCERTAIN); a paper whose SD is uncertain
is drawn with the others' pooled SD, and only its means are its own.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from schwingcheck import columns as C
from schwingcheck import rule as R
from schwingcheck import score as S

from . import literature as L
from . import papers_table as PT
from . import pooling as P
from .all_measures import LUMBAR, rule_for
from .naming import CHUNK, CLAIM
from .papers_table import Table
from .population import GENERATOR, Population, Settings, draw_table
from .validate import literature_at

MIN_SERIES_FOR_TAU = 3
OWN, MERGED, PREDICTED = "own table", "merged: the others pooled", "predicted: the others pooled, SD widened by tau"
SD_ONLY = "own means, the others' SD"
ARMS = (OWN, MERGED, PREDICTED, SD_ONLY)
TAU_OWN, TAU_MEASURE, TAU_ALL = "own", "the measure's median", "every cell's median"
# The papers that print the two pedicle dimensions at every lumbar level are the most that print
# any pair there, so this pair is the common reading, every paper on the same measures.
COMMON = ("pedicle", "pedicle_h")
LOSS_SE_FLOOR = 0.1      # points: a loss of exactly zero on every field has no SE, and a weight of 1/0 would take the pool
SEED_COLUMNS = 4105
SEED_TABLES = 4106


# ---- the cells, each paper a stratum ---------------------------------------------------------------

@dataclass
class Pool:
    """One cell pooled over some of its papers: the random-effects mean, its SE and tau, the
    within-person SD and where it came from, and how many series and papers it holds."""
    k: int
    papers: int
    mean: float
    se: float
    tau: float
    sd: float
    sd_from: str
    v: List[float] = field(default_factory=list)   # each series' within variance, sd^2 / n, as the mean was pooled


@dataclass
class Stratum:
    """One population at one cell, a paper's unless strata_of was told another grouping: its series
    (several where a paper prints cohorts), their pooled mean, its own SD where certain (NaN where
    not, Tan's), and its people."""
    paper: str
    series: List[L.Series]
    mean: float
    sd: float
    n: float


@dataclass
class Cell:
    """One placed cell of the papers' table: its key in the tables, the reread's key, the level,
    the modality class, each paper's stratum and the pool over all of them."""
    measure: str
    base_key: str
    level: str
    modality: str
    strata: List[Stratum]
    pool: Pool
    between: float = float("nan")
    tau_from: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def papers(self) -> List[str]:
        """The strata's names: the papers under by_paper, else whatever the grouping named."""
        return [s.paper for s in self.strata]

    def stratum(self, paper: str) -> Optional[Stratum]:
        for s in self.strata:
            if s.paper == paper:
                return s
        return None

    @property
    def predictive_sd(self) -> float:
        return predictive_sd(self.pool.sd, self.between)


def _pool(rows: Sequence[L.Series]) -> Pool:
    """pooled_cells's numbers for these series: the REML mean with its SE and tau where two or
    more pool, the one series' mean and its SE (sd / sqrt n) where one, and the SD as
    papers_table._sd_of gives it."""
    lit = literature_at(list(rows))
    sd, sd_from = PT._sd_of(lit, rows)
    v = [float(s.sd * s.sd / s.n) for s in rows]
    if lit.mean:
        return Pool(k=lit.k, papers=len({s.paper for s in rows}), mean=lit.mean.mean, se=lit.mean.se, tau=lit.mean.tau,
                    sd=sd, sd_from=sd_from, v=v)
    one = rows[0]
    return Pool(k=1, papers=1, mean=one.mean, se=float(one.sd / math.sqrt(one.n)), tau=float("nan"), sd=sd, sd_from=sd_from, v=v)


def _stratum(paper: str, rows: Sequence[L.Series]) -> Stratum:
    """One population from its series: its people together, the mean weighted by their counts
    and the SD over the whole of them, the spread between the cohorts' means included, as
    literature._pool_sexes joins two sexes; the SD over the series whose SD is certain alone, NaN
    where none is. A paper printing cohorts of different means is then one population as wide
    as its people, not the REML mean of its cohorts over their within SD."""
    n = float(sum(s.n for s in rows))
    mean = sum(s.n * s.mean for s in rows) / n
    certain = [s for s in rows if not s.sd_uncertain and math.isfinite(s.sd) and s.n > 0]
    sd = float("nan")
    if len(certain) == 1:
        sd = float(certain[0].sd)
    elif len(certain) >= 2:
        nc = sum(s.n for s in certain)
        mc = sum(s.n * s.mean for s in certain) / nc
        ss = sum((s.n - 1) * s.sd * s.sd + s.n * (s.mean - mc) ** 2 for s in certain)
        sd = float(math.sqrt(ss / (nc - 1)))
    return Stratum(paper=paper, series=list(rows), mean=float(mean), sd=sd, n=n)


def by_paper(s: L.Series) -> str:
    return s.paper


def by_cohort(s: L.Series) -> str:
    return "%s/%s" % (s.paper, s.cohort)


def strata_of(series: Sequence[L.Series], by=by_paper) -> List[Cell]:
    """Every placed cell, grouped and classed by modality as papers_table.pooled_cells groups it,
    with each population's stratum and the pool over all of them; the pools are pooled_cells's
    numbers (tests hold them equal). `by` names the population a series belongs to, the paper
    unless another grouping is given (by_cohort, or a variable of the population register, once
    it maps a paper and cohort to a country, a sex or a kind of specimen), so the strata and
    everything built on them read the same whichever population a reading splits by."""
    to_panjabi = PT._reread_to_panjabi()
    groups: Dict[tuple, List[L.Series]] = {}
    for s in series:
        if L.usable(s):
            groups.setdefault((s.key, s.level), []).append(s)
    out = []
    for (key, level), rows in sorted(groups.items()):
        cls, mine = PT._class_of(rows)
        places = {PT.place(key, level, s.paper) for s in mine}
        at = places.pop() if len(places) == 1 else None
        if at is None:
            continue
        papers: Dict[str, List[L.Series]] = {}
        for s in mine:
            papers.setdefault(by(s), []).append(s)
        strata = [_stratum(p, rs) for p, rs in sorted(papers.items())]
        out.append(Cell(measure=to_panjabi.get(key, key), base_key=PT.base_key(key), level=at, modality=cls,
                        strata=strata, pool=_pool(mine)))
    return out


def pooled_without(cell: Cell, paper: str) -> Optional[Pool]:
    """The cell pooled over every paper but this one; None where no other paper prints it."""
    rest = [s for st in cell.strata if st.paper != paper for s in st.series]
    return _pool(rest) if rest else None


def without(cells: Sequence[Cell], paper: str) -> List[Cell]:
    """Every cell pooled over the papers but this one, the cells only this paper prints left out:
    what a reading that leaves the paper out may borrow its medians from, so that the tau a
    left-out paper's rule is widened by never comes from that paper's own distance from the rest."""
    out = []
    for c in cells:
        pool = pooled_without(c, paper)
        if pool is not None:
            out.append(replace(c, pool=pool, between=float("nan"), tau_from=""))
    return out


# ---- one more population -------------------------------------------------------------------------

def median_f(cells: Sequence[Cell]) -> Tuple[Dict[str, float], float]:
    """The median tau over the cell's SD by measure, over the cells with MIN_SERIES_FOR_TAU series
    or more, and the median over all such cells, for the cells that have no tau of their own."""
    by: Dict[str, List[float]] = {}
    every: List[float] = []
    for c in cells:
        if c.pool.k >= MIN_SERIES_FOR_TAU and math.isfinite(c.pool.tau) and c.pool.sd > 0:
            by.setdefault(c.measure, []).append(c.pool.tau / c.pool.sd)
            every.append(c.pool.tau / c.pool.sd)
    return {k: float(np.median(v)) for k, v in by.items()}, float(np.median(every)) if every else float("nan")


def between(pool: Pool, borrowed: Tuple[Dict[str, float], float], measure: str) -> Tuple[float, str]:
    """The SD of one more population's mean, Higgins's sqrt(tau^2 + SE^2) with the SE taken under
    the same tau, 1 / sum 1 / (v_i + tau^2) over the series' variances: the cell's own tau where
    it holds MIN_SERIES_FOR_TAU series or more, where this is pooling.pool's SE, else the measure's
    median tau over SD times this cell's SD, else every cell's median; and which of the three it
    was. Under a borrowed tau the SE is not the pool's own: a one-series cell's is sqrt(v + tau^2),
    the one series being itself a population away from the grand mean, so its between is
    sqrt(2 tau^2 + v), and a two-series cell's drops the tau its own two series gave."""
    by_measure, overall = borrowed
    if pool.k >= MIN_SERIES_FOR_TAU and math.isfinite(pool.tau):
        tau, came = pool.tau, TAU_OWN
    elif measure in by_measure:
        tau, came = by_measure[measure] * pool.sd, TAU_MEASURE
    else:
        tau, came = overall * pool.sd, TAU_ALL
    return float(math.sqrt(tau * tau + se_under(pool, tau) ** 2)), came


def se_under(pool: Pool, tau: float) -> float:
    """The random-effects SE of the pool's mean under `tau`; the pool's own SE where it carries no
    series variances."""
    v = [x for x in pool.v if math.isfinite(x) and x > 0]
    if not v:
        return pool.se
    return float(math.sqrt(1.0 / sum(1.0 / (x + tau * tau) for x in v)))


def predictive_sd(sd: float, between_sd: float) -> float:
    """The SD of a person drawn from a population the table has not seen: the within-person SD
    and the spread of the population's own mean, together."""
    return float(math.sqrt(sd * sd + between_sd * between_sd))


def set_between(cells: Sequence[Cell]) -> Tuple[Dict[str, float], float]:
    """Give every cell its `between` and `tau_from` from the pool over all its papers."""
    borrowed = median_f(cells)
    for c in cells:
        c.between, c.tau_from = between(c.pool, borrowed, c.measure)
    return borrowed


def cell_rows(cells: Sequence[Cell]) -> List[dict]:
    """One row per cell for the record: the pool, the strata, between and the predictive SD."""
    out = []
    for c in cells:
        out.append({"measure": c.measure, "base_key": c.base_key, "level": c.level, "modality": c.modality,
                    "k": c.pool.k, "papers": c.pool.papers, "strata_list": ";".join(c.papers),
                    "mean": c.pool.mean, "se": c.pool.se, "tau": c.pool.tau, "sd": c.pool.sd, "sd_from": c.pool.sd_from,
                    "tau_from": c.tau_from, "between": c.between, "predictive_sd": c.predictive_sd,
                    "predictive_over_sd": c.predictive_sd / c.pool.sd if c.pool.sd > 0 else float("nan"),
                    "strata_means": ";".join("%s=%.6g" % (s.paper, s.mean) for s in c.strata)})
    return out


# ---- the tables of one paper and of the others -----------------------------------------------------

def _kinds(keys: Sequence[str], cells_by: Dict[tuple, Cell], vocabulary: Dict[str, dict], levels: Sequence[str]) -> List[str]:
    return [vocabulary[cells_by[k, levels[0]].base_key]["kind"] for k in keys]


def cells_by_key(cells: Sequence[Cell]) -> Dict[tuple, Cell]:
    return {(c.measure, c.level): c for c in cells}


def paper_measures(cells: Sequence[Cell], paper: str, vocabulary: Dict[str, dict], levels: Sequence[str] = LUMBAR,
                   keys: Optional[Sequence[str]] = None) -> List[str]:
    """The measures a paper's population can be drawn on and the others name: printed by the paper
    at every level of the run, pooled by another paper at every level too, and of a kind with a
    modelled error (a ratio has none, papers_table.Table.error); `keys` restricts them."""
    by = cells_by_key(cells)
    candidates = sorted({c.measure for c in cells}) if keys is None else list(keys)
    out = []
    for key in candidates:
        mine = [by.get((key, lv)) for lv in levels]
        if any(c is None for c in mine):
            continue
        if vocabulary[mine[0].base_key]["kind"] not in ("length", "area", "angle"):
            continue
        if any(c.stratum(paper) is None or pooled_without(c, paper) is None for c in mine):
            continue
        out.append(key)
    return out


def paper_table(cells: Sequence[Cell], paper: str, keys: Sequence[str], vocabulary: Dict[str, dict],
                levels: Sequence[str] = LUMBAR) -> Tuple[Table, int]:
    """The paper's own population as a table over the run: its means, its own SD where certain and
    the others' pooled SD where not; and how many of its cells carry its own SD."""
    by = cells_by_key(cells)
    mu = np.full((len(keys), len(levels)), np.nan)
    sd = np.full_like(mu, np.nan)
    own = 0
    for j, key in enumerate(keys):
        for i, lv in enumerate(levels):
            c = by[key, lv]
            st = c.stratum(paper)
            mu[j, i] = st.mean
            if math.isfinite(st.sd) and st.sd > 0:
                sd[j, i], own = st.sd, own + 1
            else:
                sd[j, i] = pooled_without(c, paper).sd
    return Table(name="%s's own" % paper, keys=list(keys), kinds=_kinds(keys, by, vocabulary, levels), mu=mu, sd=sd,
                 sources=[paper] * len(keys), levels=list(levels)), own


def others_table(cells: Sequence[Cell], paper: Optional[str], keys: Sequence[str], vocabulary: Dict[str, dict],
                 borrowed: Tuple[Dict[str, float], float], predictive: bool, levels: Sequence[str] = LUMBAR) -> Table:
    """The others' pooled table over the run, this paper left out (every paper in, with None): the
    random-effects means with the within SD as tables B and C hold them, or, `predictive`, with
    the SD widened for one more population."""
    by = cells_by_key(cells)
    mu = np.full((len(keys), len(levels)), np.nan)
    sd = np.full_like(mu, np.nan)
    for j, key in enumerate(keys):
        for i, lv in enumerate(levels):
            c = by[key, lv]
            pool = c.pool if paper is None else pooled_without(c, paper)
            mu[j, i] = pool.mean
            sd[j, i] = predictive_sd(pool.sd, between(pool, borrowed, key)[0]) if predictive else pool.sd
    name = ("the others pooled" if paper else "every paper pooled") + (", widened by tau" if predictive else "")
    return Table(name=name, keys=list(keys), kinds=_kinds(keys, by, vocabulary, levels), mu=mu, sd=sd,
                 sources=["papers"] * len(keys), levels=list(levels))


# ---- scoring, paired ---------------------------------------------------------------------------------

def posterior(pop: Population, table: Table, width: int, settings: Settings):
    """The rule built on `table`, on every field of `width` bodies of every column of `pop` (drawn
    on the same keys over the same levels): the posterior's call and top, the truth and the column."""
    idx = [pop.keys.index(k) for k in table.keys]
    li = [pop.level_index(lv) for lv in table.levels]
    X, truth, group = C.fields(pop.measured[:, li][:, :, idx], list(range(width)))
    mu, sd, synth, noise, power = rule_for(table, settings)
    post = R.name(X, list(range(width)), mu, sd, synth, noise=noise, power=power, chunk=CHUNK)["all"]
    return post.argmax(1), post.max(1), truth, group


def summary(call, top, truth, group) -> dict:
    """naming.score's readings from a posterior's call and top."""
    hit = (call == truth).astype(float)
    ans = top >= CLAIM
    groups = np.unique(group, return_inverse=True)[1]
    wrong = np.bincount(groups, weights=ans & (hit == 0))
    answered = np.bincount(groups, weights=ans)
    return {"fields": int(len(truth)), "columns": int(len(np.unique(group))),
            "exact": float(hit.mean()), "exact_se": S.clustered_se(hit, group),
            "within_one": float((np.abs(call - truth) <= 1).mean()),
            "answered": float(ans.mean()), "n_answered": int(ans.sum()), "errors": int((ans & (hit == 0)).sum()),
            "precision": float(hit[ans].mean()) if ans.any() else float("nan"),
            "precision_se": S.ratio_se(wrong, answered) if ans.any() else float("nan"),
            "mean_top": float(top.mean())}


def paired_loss(hit_own: np.ndarray, hit: np.ndarray, group: np.ndarray) -> Tuple[float, float]:
    """The loss against the own table in points of fields named exactly, and its SE clustered by
    column, read on the difference field by field, so the pairing is kept."""
    diff = hit_own - hit
    return float(100.0 * diff.mean()), float(100.0 * S.clustered_se(diff, group))


def score_arms(pop: Population, tables: Dict[str, Table], width: int, settings: Settings) -> List[dict]:
    """Every arm's table on the same fields, each with its loss against the arm OWN."""
    got = {}
    for arm, t in tables.items():
        call, top, truth, group = posterior(pop, t, width, settings)
        got[arm] = (summary(call, top, truth, group), (call == truth).astype(float), group)
    out = []
    for arm, (row, hit, group) in got.items():
        loss, se = paired_loss(got[OWN][1], hit, group)
        out.append(dict(row, arm=arm, width=width, loss=loss, loss_se=se))
    return out


# ---- leave one paper out ---------------------------------------------------------------------------

def leave_one_out(cells: Sequence[Cell], vocabulary: Dict[str, dict], columns: int, widths: Sequence[int] = (1, 2, 3),
                  seed: int = SEED_COLUMNS, settings: Settings = GENERATOR, keys: Optional[Sequence[str]] = None,
                  levels: Sequence[str] = LUMBAR, reading: str = "every measure the paper prints") -> List[dict]:
    """For every paper with a measure to score (paper_measures): `columns` people drawn from its
    own table, the four arms' tables built on the same measures, and each arm scored at each
    width on the same fields; one row per paper, width and arm. The arm SD_ONLY, the paper's own
    means under the others' SD, says what the SD difference alone costs, so that MERGED's loss
    can be read as that part and the shift of the means. The medians a cell with fewer
    than MIN_SERIES_FOR_TAU series borrows its tau from are taken over the cells pooled without
    the paper (`without`), so nothing of the paper reaches the rule scored on it; the row says
    which of its measures lost their own median that way (measures_tau_fell), the overall median
    without it (f_overall_without) and its own SD against the others' (own_sd_over_pool). Each
    paper's columns are drawn on a seed of its own, `seed` plus its index among the papers sorted
    by name, so that two papers' losses never share one draw's Monte Carlo error, which
    pooled_losses pools as independent."""
    full = median_f(cells)
    by = cells_by_key(cells)
    out = []
    for i, paper in enumerate(sorted({s.paper for c in cells for s in c.strata})):
        mine = paper_measures(cells, paper, vocabulary, levels, keys)
        if not mine or (keys is not None and len(mine) < len(keys)):
            continue
        borrowed = median_f(without(cells, paper))
        fell = [k for k in mine if k in full[0] and k not in borrowed[0]]
        f_without = borrowed[1]
        if math.isnan(f_without):     # nothing left to borrow from, which only a toy pool can reach: the full pool's median
            borrowed = (borrowed[0], full[1])
        own, own_sd = paper_table(cells, paper, mine, vocabulary, levels)
        merged = others_table(cells, paper, mine, vocabulary, borrowed, False, levels)
        sd_only = Table(name="%s's means, the others' SD" % paper, keys=list(mine), kinds=list(own.kinds), mu=own.mu.copy(),
                        sd=merged.sd.copy(), sources=list(own.sources), levels=list(levels))
        tables = {OWN: own, MERGED: merged, PREDICTED: others_table(cells, paper, mine, vocabulary, borrowed, True, levels),
                  SD_ONLY: sd_only}
        pop = draw_table(own, settings, columns, seed + i)
        for w in widths:
            for row in score_arms(pop, tables, w, settings):
                out.append(dict(row, reading=reading, paper=paper, n_measures=len(mine), measures=";".join(mine),
                                cells_with_own_sd=own_sd, cells=len(mine) * len(levels),
                                people=float(np.mean([by[k, lv].stratum(paper).n for k in mine for lv in levels])),
                                own_sd_over_pool=own_sd_over_pool(by, paper, mine, levels),
                                f_overall_without=f_without, measures_tau_fell=";".join(fell)))
    return out


def own_sd_over_pool(by: Dict[tuple, Cell], paper: str, keys: Sequence[str], levels: Sequence[str]) -> float:
    """The median, over the paper's cells with an SD of their own, of that SD over the others'
    pooled SD: above 1 the paper's people are spread wider than the pool the rule is built on."""
    ratios = []
    for key in keys:
        for lv in levels:
            st = by[key, lv].stratum(paper)
            if math.isfinite(st.sd) and st.sd > 0:
                ratios.append(st.sd / pooled_without(by[key, lv], paper).sd)
    return float(np.median(ratios)) if ratios else float("nan")


def pooled_losses(rows: Sequence[dict], widths: Sequence[int] = (1, 2, 3)) -> List[dict]:
    """Per reading, arm and width: the per-paper losses combined by random effects, pooling.pool
    on each loss and its SE squared (floored at LOSS_SE_FLOOR), the pooled loss, its SE, the spread
    between populations and the interval for one more population's loss (three or more); beside it
    the plain mean and median of the losses, the papers, the precision at 0.99 as the mean over
    the papers and at its least, and pooled over the answers themselves (precision_pooled: every
    paper's answers together, so a paper that answers often weighs more)."""
    out = []
    for reading in dict.fromkeys(r["reading"] for r in rows):
        for arm in ARMS[1:]:
            for w in widths:
                rs = [r for r in rows if r["reading"] == reading and r["arm"] == arm and r["width"] == w]
                if not rs:
                    continue
                y = np.array([r["loss"] for r in rs])
                v = np.maximum(np.array([r["loss_se"] for r in rs]), LOSS_SE_FLOOR) ** 2
                p = P.pool(y, v)
                prec = [r["precision"] for r in rs if math.isfinite(r["precision"])]
                n_ans = sum(r.get("n_answered", 0) for r in rs)
                errors = sum(r.get("errors", 0) for r in rs)
                out.append({"reading": reading, "arm": arm, "width": w, "populations": len(rs),
                            "loss_pooled": p.mean if p else float(y[0]), "loss_se": p.se if p else float("nan"),
                            "tau_between_populations": p.tau if p else float("nan"),
                            "pi_low": p.pi_low if p else float("nan"), "pi_high": p.pi_high if p else float("nan"),
                            "loss_mean": float(y.mean()), "loss_median": float(np.median(y)),
                            "loss_min": float(y.min()), "loss_max": float(y.max()),
                            "exact_mean": float(np.mean([r["exact"] for r in rs])),
                            "precision_mean": float(np.mean(prec)) if prec else float("nan"),
                            "precision_min": float(np.min(prec)) if prec else float("nan"),
                            "precision_pooled": float((n_ans - errors) / n_ans) if n_ans else float("nan"),
                            "answered_mean": float(np.mean([r["answered"] for r in rs]))})
    return out


# ---- populations drawn from the random-effects model ---------------------------------------------------

def shift_share(split: dict) -> float:
    """The share of the spread between populations that one shift through a whole measure carries,
    from the first part's calibrated split (power.shift_split's shift and level-by-level parts)."""
    s, lv = split["shift_sd_calibrated"], split["level_sd_calibrated"]
    return float(s * s / (s * s + lv * lv))


def new_table(pooled: Table, between_sd: np.ndarray, share: float, rng: np.random.Generator) -> np.ndarray:
    """The means of one more population: each cell's pooled mean moved by its `between`, a share
    of the variance as one draw through the whole measure and the rest cell by cell."""
    together = rng.normal(size=(pooled.mu.shape[0], 1))
    apart = rng.normal(size=pooled.mu.shape)
    return pooled.mu + between_sd * (math.sqrt(share) * together + math.sqrt(1.0 - share) * apart)


def new_populations(cells: Sequence[Cell], vocabulary: Dict[str, dict], keys: Sequence[str], share: float, columns: int,
                    tables: int = 4, widths: Sequence[int] = (1, 2, 3), seed: int = SEED_COLUMNS,
                    table_seed: int = SEED_TABLES, settings: Settings = GENERATOR, levels: Sequence[str] = LUMBAR,
                    reading: str = "a population drawn from the model") -> List[dict]:
    """`tables` populations drawn from the random-effects model on the papers' pooled table over
    `keys`, each scored on its own table, the merged rule and the predicted rule; the rows carry
    the table's index as the paper."""
    borrowed = median_f(cells)
    by = cells_by_key(cells)
    pooled = others_table(cells, None, keys, vocabulary, borrowed, False, levels)
    predicted = others_table(cells, None, keys, vocabulary, borrowed, True, levels)
    bet = np.array([[between(by[k, lv].pool, borrowed, k)[0] for lv in levels] for k in keys])
    rng = np.random.default_rng(table_seed)
    out = []
    for t in range(tables):
        mu = new_table(pooled, bet, share, rng)
        own = Table(name="population %d" % t, keys=list(keys), kinds=list(pooled.kinds), mu=mu, sd=pooled.sd.copy(),
                    sources=list(pooled.sources), levels=list(levels))
        pop = draw_table(own, settings, columns, seed + t)
        for w in widths:
            for row in score_arms(pop, {OWN: own, MERGED: pooled, PREDICTED: predicted}, w, settings):
                out.append(dict(row, reading=reading, paper="population %d" % t, n_measures=len(keys), measures=";".join(keys),
                                cells_with_own_sd=0, cells=len(keys) * len(levels), people=float("nan")))
    return out
