"""Choosing the rule by held-out prediction: nested leave-one-population-out over the papers.

The owner's words of 2026-10-30, 02:10 UTC: "I just want a statistically valid way to maximize
predictive ability that doesnt necessary have to rooted in realistic biology". So the rule is chosen
as a machine learner chooses a model: every paper is a population the rule has never seen (strata.py),
each is held out in turn, the candidates are built on the other papers alone, any knob a candidate
has is set by a second leave-one-out inside the training papers, and the candidates are compared on
the held-out populations by proper scores, never on the population that set the knob.

The rule itself is a classifier over places: a field of `width` bodies with its measures is scored
against every place in the lumbar run by the exact Gaussian likelihood of schwingcheck.rule, the
size integrated out, and a uniform prior gives the posterior over places (the "model" is the table
of means and SDs the rule reads, so a candidate is a way of making that table from the other
papers). The candidates:

- PLAIN: the other papers pooled by random effects, each cell's mean and its within-person SD
  (strata.MERGED, tables B and C as they stand);
- WIDENED: the same means, the SD widened by the spread between populations,
  sqrt(sd^2 + tau^2 + SE^2) (strata.PREDICTED), the theory's answer with no knob;
- SCALED: the same means, every SD multiplied by one factor k, the factor chosen by the inner
  leave-one-out on the log score over K_GRID (1 is PLAIN; the widening's factor is 1.7 to 1.8 over
  the quartiles of cells, so the grid holds it);
- TEMPERED: PLAIN's likelihood with the log evidence divided by a temperature T before the posterior
  is taken, T chosen per width by the inner leave-one-out over T_GRID (1 is PLAIN): temperature
  scaling, which moves only the posterior's confidence, never which place wins;
- MIXTURE: one table per other paper, the pool with that paper's own cells put in where it prints
  them, the field's evidence the equal-weight average of the components' evidences (Bayesian model
  averaging over the populations seen), so each population keeps its own shape instead of being
  merged into the pool.

Whether a paper should be left out of the prior is answered the same way (the owner's choice of
2026-10-30, 03:05 UTC, "Score exclusion held out", over excluding Yadav 2020 by eye): each paper of
EXCLUDABLE gives a candidate, PLAIN built as if that paper had never been read ("without <paper>"),
and ONE_VOTE pools every cell's SD as the geometric mean of the other populations' own SDs, each
population one vote whatever its size, the answer to two papers disagreeing on a spread without
choosing between them. Each of these, with PLAIN, is also scored tempered, its temperature per
width set by the same inner leave-one-out on its own rule ("<base>, tempered"; PLAIN's is TEMPERED).
Leaving a paper out changes nothing on the fold that holds it out, where PLAIN already never reads
it, so its candidate scores that fold as PLAIN does; a cell no third paper prints keeps PLAIN's
value, counted in the record as fallback_cells, so every candidate scores the same measures on the
same fields.

The scores, on every field of every column drawn from the held-out paper's own table, the same
fields for every candidate: the top-1 accuracy (exact naming), the log score, the mean log posterior
probability of the true place (its negative is the log loss, in nats), the expected calibration error
over the top probability in ten bins, and the promise at 0.99 (how often it answers, how often the
answer is right). OWN, the held-out paper's own table, is scored beside them as the oracle no
candidate can beat except by chance, so a candidate's regret is read against it. The outer folds are
the 22 papers of strata.leave_one_out, on the same seeds, so a population here is the population
there; the inner folds are the other papers that print any of the held-out paper's measures, on
fewer columns (INNER_COLUMNS), each scored by the rule built without the held-out paper and without
itself.

A candidate's number on the held-out populations is honest for that candidate; choosing the best of
five on the same folds is a small selection, said in the README, and the winner is the candidate
with the best mean held-out log score, its difference from PLAIN read paired by population with its
SE over the populations.
"""
from __future__ import annotations

import math
import re
from dataclasses import replace
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from schwingcheck import columns as C
from schwingcheck import rule as R
from schwingcheck import score as S

from . import strata as ST
from .all_measures import LUMBAR, rule_for
from .naming import CHUNK, CLAIM
from .papers_table import Table
from .population import GENERATOR, Population, Settings, draw_table

OWN, PLAIN, WIDENED, SCALED, TEMPERED, MIXTURE = "own table", "plain", "widened by tau", "scaled SD", "tempered", "mixture"
CORE = (PLAIN, WIDENED, SCALED, TEMPERED, MIXTURE)
EXCLUDABLE = ("yadav2020", "frontphys2026")     # the two papers that disagree on the end-plate spread
ONE_VOTE = "one vote per population"
WITHOUT = {"without %s" % p: p for p in EXCLUDABLE}
BASES = (PLAIN,) + tuple(WITHOUT) + (ONE_VOTE,)  # the rules a temperature is read on


def tempered_name(base: str) -> str:
    """The candidate that is `base` with its log evidence divided by its own inner temperature."""
    return TEMPERED if base == PLAIN else "%s, tempered" % base


EXCLUSION = tuple(name for base in BASES[1:] for name in (base, tempered_name(base)))
CANDIDATES = CORE + EXCLUSION
K_GRID = (0.7, 0.85, 1.0, 1.2, 1.45, 1.75, 2.1, 2.5, 3.0)      # SD factors, log-spaced about 1; 1 is PLAIN
T_GRID = (0.5, 0.7, 1.0, 1.4, 2.0, 2.8, 4.0, 5.6, 8.0)         # temperatures; 1 is the exact posterior
INNER_COLUMNS = 150
BINS = 10                                                     # of the top probability, for the calibration error
LOG_FLOOR = 1e-300


# ---- the evidence and the scores -----------------------------------------------------------------

def log_evidence(pop: Population, table: Table, width: int, settings: Settings) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """log p(field | place) for every field of `width` bodies of every column of `pop` under the rule
    built on `table`, the size integrated out, (fields, places), with the true place and the column
    of each: what strata.posterior takes its posterior from, kept so that temperatures and mixtures
    can be read from it."""
    idx = [pop.keys.index(k) for k in table.keys]
    li = [pop.level_index(lv) for lv in table.levels]
    X, truth, group = C.fields(pop.measured[:, li][:, :, idx], list(range(width)))
    mu, sd, synth, noise, power = rule_for(table, settings)
    sizes, logw = R.quadrature(synth["scale_sd"])
    offsets = list(range(width))
    parts = []
    for c0 in range(0, X.shape[0], CHUNK):
        LL = R.loglik(X[c0:c0 + CHUNK], offsets, mu, sd, synth, sizes=sizes, noise=noise, power=power)
        parts.append(R.log_evidence(LL, logw))
    return np.concatenate(parts) if parts else np.zeros((0, R.places_of(mu.shape[1], offsets))), truth, group


def tempered(logev: np.ndarray, temperature: float) -> np.ndarray:
    """The posterior over places at this temperature: 1 is the exact posterior, above 1 flatter."""
    return R.posterior(np.asarray(logev, float) / float(temperature))


def mixture_evidence(components: Sequence[np.ndarray]) -> np.ndarray:
    """log p(field | place) under the equal-weight mixture of these components' evidences."""
    stack = np.stack([np.asarray(c, float) for c in components])
    return R.logsumexp(stack, 0) - math.log(len(components))


def calibration_error(top: np.ndarray, hit: np.ndarray, bins: int = BINS) -> float:
    """The expected calibration error of the top probability: over `bins` equal bins of it, the
    share of fields in the bin times the gap between its mean top probability and its accuracy."""
    edges = np.linspace(0.0, 1.0, bins + 1)
    which = np.clip(np.searchsorted(edges, top, side="right") - 1, 0, bins - 1)
    n = np.bincount(which, minlength=bins).astype(float)
    conf = np.bincount(which, weights=top, minlength=bins)
    acc = np.bincount(which, weights=hit, minlength=bins)
    keep = n > 0
    return float((n[keep] / n.sum() * np.abs(acc[keep] / n[keep] - conf[keep] / n[keep])).sum())


def reliability(top: np.ndarray, hit: np.ndarray, bins: int = BINS) -> List[dict]:
    """The calibration curve's bins: each one's fields, the sum of their top probabilities and of
    their hits, so that bins pooled over populations give the curve."""
    edges = np.linspace(0.0, 1.0, bins + 1)
    which = np.clip(np.searchsorted(edges, top, side="right") - 1, 0, bins - 1)
    out = []
    for b in range(bins):
        m = which == b
        if m.any():
            out.append({"bin": b, "low": float(edges[b]), "high": float(edges[b + 1]), "fields": int(m.sum()),
                        "sum_top": float(top[m].sum()), "sum_hit": float(hit[m].sum())})
    return out


def scores(logev: np.ndarray, truth: np.ndarray, group: np.ndarray, temperature: float = 1.0) -> dict:
    """Every score of one rule on these fields: the accuracy (exact), the log score (the mean log
    posterior of the true place; minus it is the log loss), the calibration error, the promise at
    0.99, each rate's SE clustered by column, and the hits, the top probabilities and the log
    probabilities themselves under keys the records leave out."""
    post = tempered(logev, temperature)
    call, top = post.argmax(1), post.max(1)
    hit = (call == truth).astype(float)
    lp = np.log(np.maximum(post[np.arange(len(truth)), truth], LOG_FLOOR))
    ans = top >= CLAIM
    groups = np.unique(group, return_inverse=True)[1]
    wrong = np.bincount(groups, weights=ans & (hit == 0))
    answered = np.bincount(groups, weights=ans)
    return {"fields": int(len(truth)), "columns": int(len(np.unique(group))),
            "exact": float(hit.mean()), "exact_se": S.clustered_se(hit, group),
            "within_one": float((np.abs(call - truth) <= 1).mean()),
            "log_score": float(lp.mean()), "log_score_se": S.clustered_se(lp, group),
            "ece": calibration_error(top, hit),
            "answered": float(ans.mean()), "n_answered": int(ans.sum()), "errors": int((ans & (hit == 0)).sum()),
            "precision": float(hit[ans].mean()) if ans.any() else float("nan"),
            "precision_se": S.ratio_se(wrong, answered) if ans.any() else float("nan"),
            "mean_top": float(top.mean()),
            "_hit": hit, "_top": top, "_lp": lp, "_group": group}


def record(row: dict) -> dict:
    return {k: v for k, v in row.items() if not k.startswith("_")}


# ---- the candidates' tables -----------------------------------------------------------------------

def scaled(table: Table, k: float) -> Table:
    """The same table with every SD multiplied by k."""
    return replace(table, name="%s, SD x %.3g" % (table.name, k), sd=table.sd * float(k))


def without_table(cells: Sequence[ST.Cell], paper: Optional[str], keys: Sequence[str], vocabulary: Dict[str, dict],
                  dropped: str, levels: Sequence[str] = LUMBAR) -> Tuple[Table, int]:
    """PLAIN as if `dropped` had never been read: each cell pooled over the papers but `paper` and
    `dropped`, with the pool's REML mean and SD as PLAIN's are made; a cell no third paper prints
    keeps PLAIN's value, and how many did is returned beside the table."""
    plain = ST.others_table(cells, paper, keys, vocabulary, ({}, float("nan")), False, levels)
    by = ST.cells_by_key(cells)
    mu, sd, kept = plain.mu.copy(), plain.sd.copy(), 0
    for j, key in enumerate(keys):
        for i, lv in enumerate(levels):
            rest = [s for st in by[key, lv].strata if st.paper not in (paper, dropped) for s in st.series]
            if not rest:
                kept += 1
                continue
            pool = ST._pool(rest)
            mu[j, i], sd[j, i] = pool.mean, pool.sd
    return replace(plain, name="%s, %s left out" % (plain.name, dropped), mu=mu, sd=sd), kept


def one_vote_table(cells: Sequence[ST.Cell], paper: Optional[str], keys: Sequence[str], vocabulary: Dict[str, dict],
                   levels: Sequence[str] = LUMBAR) -> Tuple[Table, int]:
    """PLAIN's means with every cell's SD the geometric mean of the other populations' own SDs
    (strata.Stratum.sd, certain alone), each population one vote whatever its size; a cell where no
    other population has an SD of its own keeps PLAIN's, and how many did is returned beside it."""
    plain = ST.others_table(cells, paper, keys, vocabulary, ({}, float("nan")), False, levels)
    by = ST.cells_by_key(cells)
    sd, kept = plain.sd.copy(), 0
    for j, key in enumerate(keys):
        for i, lv in enumerate(levels):
            own = [st.sd for st in by[key, lv].strata if st.paper != paper and math.isfinite(st.sd) and st.sd > 0]
            if not own:
                kept += 1
                continue
            sd[j, i] = float(math.exp(np.mean(np.log(own))))
    return replace(plain, name="%s, one vote per population" % plain.name, sd=sd), kept


def base_table(cells: Sequence[ST.Cell], paper: Optional[str], keys: Sequence[str], vocabulary: Dict[str, dict],
               base: str, levels: Sequence[str] = LUMBAR) -> Tuple[Table, int]:
    """The table of one of BASES built without `paper`, and its fallback cells."""
    if base == PLAIN:
        return ST.others_table(cells, paper, keys, vocabulary, ({}, float("nan")), False, levels), 0
    if base == ONE_VOTE:
        return one_vote_table(cells, paper, keys, vocabulary, levels)
    return without_table(cells, paper, keys, vocabulary, WITHOUT[base], levels)


def component_tables(cells: Sequence[ST.Cell], paper: Optional[str], keys: Sequence[str], vocabulary: Dict[str, dict],
                     levels: Sequence[str] = LUMBAR) -> Dict[str, Table]:
    """The mixture's components, one per other paper that prints any of `keys` over `levels`: the
    pool without `paper` (strata.others_table) with that other paper's own mean, and its own SD where
    certain, put in at every cell it prints. A paper printing no cell of these has no component."""
    by = ST.cells_by_key(cells)
    base = ST.others_table(cells, paper, keys, vocabulary, ST.median_f(ST.without(cells, paper) if paper else cells), False, levels)
    out: Dict[str, Table] = {}
    others = sorted({s.paper for c in cells for s in c.strata if s.paper != paper})
    for other in others:
        mu, sd, touched = base.mu.copy(), base.sd.copy(), 0
        for j, key in enumerate(keys):
            for i, lv in enumerate(levels):
                st = by[key, lv].stratum(other)
                if st is None:
                    continue
                mu[j, i], touched = st.mean, touched + 1
                if math.isfinite(st.sd) and st.sd > 0:
                    sd[j, i] = st.sd
        if touched:
            out[other] = replace(base, name="component %s" % other, mu=mu, sd=sd)
    return out


# ---- the inner leave-one-out: the knobs -------------------------------------------------------------

def drop_paper(cells: Sequence[ST.Cell], paper: str) -> List[ST.Cell]:
    """Every cell with this paper's stratum taken out and the pool made over the rest, a cell only
    this paper prints left out. strata.without changes a cell's pool alone and keeps the stratum, so
    a reading over its cells still sees the paper; the inner folds, which choose the knobs, must not
    see the held-out paper at all, neither as a fold nor in any pool a fold's rule is built on."""
    out = []
    for c in cells:
        rest = [st for st in c.strata if st.paper != paper]
        if rest:
            out.append(replace(c, strata=rest, pool=ST._pool([s for st in rest for s in st.series]), between=float("nan"), tau_from=""))
    return out


def inner_choice(cells: Sequence[ST.Cell], paper: str, keys: Sequence[str], vocabulary: Dict[str, dict], widths: Sequence[int],
                 settings: Settings = GENERATOR, columns: int = INNER_COLUMNS, seed: int = ST.SEED_COLUMNS,
                 k_grid: Sequence[float] = K_GRID, t_grid: Sequence[float] = T_GRID, levels: Sequence[str] = LUMBAR) -> dict:
    """The SD factor k and the temperature T per width chosen on the training papers alone, the
    held-out `paper` dropped from the cells first (drop_paper): each training paper that prints any
    of `keys` is held out of the rest in turn, its population drawn on `columns` columns, the rule
    built on the rest at every k of the grid and scored by the log score at every width; k is the
    one with the best mean log score over the folds and widths, and T, read on the k = 1 rule, the
    best per width over the folds; each of BASES gets its own T the same way, on its own rule
    (t_by, PLAIN's being t). The folds' means are the record."""
    training = drop_paper(cells, paper)
    folds = []
    for j, other in enumerate(sorted({s.paper for c in training for s in c.strata})):
        mine = ST.paper_measures(training, other, vocabulary, levels, keys)
        if not mine:
            continue
        rest = ST.without(training, other)
        borrowed = ST.median_f(rest)
        if math.isnan(borrowed[1]):
            borrowed = (borrowed[0], ST.median_f(training)[1])
        own, _ = ST.paper_table(training, other, mine, vocabulary, levels)
        pool = ST.others_table(training, other, mine, vocabulary, borrowed, False, levels)
        pop = draw_table(own, settings, columns, seed + 1000 + j)
        bases = {b: base_table(training, other, mine, vocabulary, b, levels)[0] for b in BASES if b != PLAIN}
        by_k = {k: [] for k in k_grid}
        by_t = {(b, t, w): [] for b in BASES for t in t_grid for w in widths}
        for w in widths:
            for k in k_grid:
                logev, truth, group = log_evidence(pop, scaled(pool, k), w, settings)
                by_k[k].append(scores(logev, truth, group)["log_score"])
                if k == 1.0:
                    for t in t_grid:
                        by_t[PLAIN, t, w].append(scores(logev, truth, group, t)["log_score"])
            for b, table in bases.items():
                logev = log_evidence(pop, table, w, settings)[0]
                for t in t_grid:
                    by_t[b, t, w].append(scores(logev, truth, group, t)["log_score"])
        folds.append({"paper": other, "n_measures": len(mine), "k": {k: float(np.mean(v)) for k, v in by_k.items()},
                      "t": {(t, w): float(by_t[PLAIN, t, w][0]) for t in t_grid for w in widths},
                      "t_by": {key: float(v[0]) for key, v in by_t.items()}})
    if not folds:
        flat = {w: 1.0 for w in widths}
        return {"k": 1.0, "t": flat, "t_by": {b: dict(flat) for b in BASES}, "folds": [], "k_curve": {}, "t_curve": {}, "t_curves": {}}
    k_curve = {k: float(np.mean([f["k"][k] for f in folds])) for k in k_grid}
    t_curves = {key: float(np.mean([f["t_by"][key] for f in folds])) for key in folds[0]["t_by"]}
    t_curve = {(t, w): t_curves[PLAIN, t, w] for t in t_grid for w in widths}
    k_best = max(k_grid, key=lambda k: k_curve[k])
    t_by = {b: {w: max(t_grid, key=lambda t: t_curves[b, t, w]) for w in widths} for b in BASES}
    return {"k": float(k_best), "t": t_by[PLAIN], "t_by": t_by, "folds": folds, "k_curve": k_curve, "t_curve": t_curve,
            "t_curves": t_curves}


# ---- the outer leave-one-out: the candidates scored -------------------------------------------------

def score_paper(cells: Sequence[ST.Cell], paper: str, keys: Sequence[str], vocabulary: Dict[str, dict], columns: int,
                widths: Sequence[int], choice: dict, settings: Settings = GENERATOR, seed: int = ST.SEED_COLUMNS,
                k_grid: Sequence[float] = K_GRID, t_grid: Sequence[float] = T_GRID,
                levels: Sequence[str] = LUMBAR) -> Tuple[List[dict], List[dict], List[dict], List[dict]]:
    """Every candidate on the held-out paper's population at every width, with OWN beside them: the
    score rows, the calibration bins, the held-out curve over every k and the held-out curve over
    every T (what the knobs would have scored had they been set on this population, drawn to show
    that the inner choice sits near the held-out best, never to choose by)."""
    training = ST.without(cells, paper)
    borrowed = ST.median_f(training)
    if math.isnan(borrowed[1]):
        borrowed = (borrowed[0], ST.median_f(cells)[1])
    own, own_sd = ST.paper_table(cells, paper, keys, vocabulary, levels)
    plain = ST.others_table(cells, paper, keys, vocabulary, borrowed, False, levels)
    widened = ST.others_table(cells, paper, keys, vocabulary, borrowed, True, levels)
    components = component_tables(cells, paper, keys, vocabulary, levels)
    bases = {b: base_table(cells, paper, keys, vocabulary, b, levels) for b in BASES if b != PLAIN}
    t_by = choice.get("t_by") or {PLAIN: choice["t"]}
    pop = draw_table(own, settings, columns, seed)
    rows, bins, k_rows, t_rows = [], [], [], []
    for w in widths:
        got: Dict[str, dict] = {}
        ev_own, truth, group = log_evidence(pop, own, w, settings)
        got[OWN] = scores(ev_own, truth, group)
        ev_plain = log_evidence(pop, plain, w, settings)[0]
        got[PLAIN] = scores(ev_plain, truth, group)
        got[WIDENED] = scores(log_evidence(pop, widened, w, settings)[0], truth, group)
        got[TEMPERED] = scores(ev_plain, truth, group, choice["t"][w])
        for k in k_grid:
            sc = scores(ev_plain if k == 1.0 else log_evidence(pop, scaled(plain, k), w, settings)[0], truth, group)
            k_rows.append({"paper": paper, "width": w, "k": k, "log_score": sc["log_score"], "exact": sc["exact"], "ece": sc["ece"]})
            if k == choice["k"]:
                got[SCALED] = sc
        for t in t_grid:
            sc = scores(ev_plain, truth, group, t)
            t_rows.append({"paper": paper, "width": w, "temperature": t, "log_score": sc["log_score"], "exact": sc["exact"], "ece": sc["ece"]})
        got[MIXTURE] = scores(mixture_evidence([log_evidence(pop, t, w, settings)[0] for t in components.values()]), truth, group)
        temperature, fallback = {TEMPERED: choice["t"][w]}, {}
        for b, (table, kept) in bases.items():
            ev = log_evidence(pop, table, w, settings)[0]
            t_b = t_by.get(b, choice["t"])[w]
            got[b], got[tempered_name(b)] = scores(ev, truth, group), scores(ev, truth, group, t_b)
            temperature[tempered_name(b)], fallback[b], fallback[tempered_name(b)] = t_b, kept, kept
        for name, sc in got.items():
            loss, loss_se = ST.paired_loss(got[OWN]["_hit"], sc["_hit"], group)
            regret = got[OWN]["_lp"] - sc["_lp"]
            rows.append(dict(record(sc), candidate=name, width=w, paper=paper, n_measures=len(keys), measures=";".join(keys),
                             cells_with_own_sd=own_sd, cells=len(keys) * len(levels), components=len(components),
                             k=choice["k"] if name == SCALED else (1.0 if name in (PLAIN, TEMPERED) + EXCLUSION else float("nan")),
                             temperature=temperature.get(name, 1.0), fallback_cells=fallback.get(name, 0),
                             loss=loss, loss_se=loss_se, regret=float(regret.mean()), regret_se=S.clustered_se(regret, group),
                             log_score_vs_plain=sc["log_score"] - got[PLAIN]["log_score"],
                             log_score_vs_plain_se=S.clustered_se(sc["_lp"] - got[PLAIN]["_lp"], group),
                             exact_vs_plain=sc["exact"] - got[PLAIN]["exact"],
                             exact_vs_plain_se=S.clustered_se(sc["_hit"] - got[PLAIN]["_hit"], group)))
            bins += [dict(b, candidate=name, width=w, paper=paper) for b in reliability(sc["_top"], sc["_hit"])]
    return rows, bins, k_rows, t_rows


def select(cells: Sequence[ST.Cell], vocabulary: Dict[str, dict], columns: int, widths: Sequence[int] = (1, 2, 3),
           inner_columns: int = INNER_COLUMNS, settings: Settings = GENERATOR, seed: int = ST.SEED_COLUMNS,
           k_grid: Sequence[float] = K_GRID, t_grid: Sequence[float] = T_GRID, levels: Sequence[str] = LUMBAR,
           log=None) -> dict:
    """The whole study: every paper with a measure to score held out in turn (the papers and seeds
    of strata.leave_one_out), its knobs set by inner_choice on the other papers, every candidate
    scored on its population. Returns the score rows, the calibration bins, the two held-out curves,
    and each paper's choice with its inner curves."""
    rows, bins, k_rows, t_rows, choices = [], [], [], [], []
    for i, paper in enumerate(sorted({s.paper for c in cells for s in c.strata})):
        keys = ST.paper_measures(cells, paper, vocabulary, levels)
        if not keys:
            continue
        if log:
            log("held out: %s (%d measures)" % (paper, len(keys)))
        choice = inner_choice(cells, paper, keys, vocabulary, widths, settings, inner_columns, seed + i, k_grid, t_grid, levels)
        r, b, kr, tr = score_paper(cells, paper, keys, vocabulary, columns, widths, choice, settings, seed + i, k_grid, t_grid, levels)
        rows += r
        bins += b
        k_rows += kr
        t_rows += tr
        choices.append({"paper": paper, "n_measures": len(keys), "k": choice["k"],
                        **{"t_%d" % w: choice["t"][w] for w in widths},
                        **{"t_%s_%d" % (slug(b), w): choice["t_by"][b][w] for b in BASES[1:] for w in widths},
                        "inner_folds": len(choice["folds"]), "inner_columns": inner_columns,
                        **{"inner_log_score_k_%g" % k: choice["k_curve"].get(k, float("nan")) for k in k_grid},
                        **{"inner_log_score_t_%g_%d" % (t, w): choice["t_curve"].get((t, w), float("nan")) for t in t_grid for w in widths},
                        **{"inner_log_score_t_%s_%g_%d" % (slug(b), t, w): choice["t_curves"].get((b, t, w), float("nan"))
                           for b in BASES[1:] for t in t_grid for w in widths}})
    return {"scores": rows, "bins": bins, "k_curve": k_rows, "t_curve": t_rows, "choices": choices}


def slug(base: str) -> str:
    """A base's name as a record's column takes it."""
    return re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")


# ---- over the populations -------------------------------------------------------------------------

def _mean_se(xs: Sequence[float]) -> Tuple[float, float]:
    a = np.asarray([x for x in xs if math.isfinite(x)], float)
    if a.size == 0:
        return float("nan"), float("nan")
    return float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)) if a.size > 1 else float("nan")


def pooled_bins(bins: Sequence[dict], candidate: str, width: int) -> List[dict]:
    """The calibration curve of one candidate at one width over every population: per bin, the
    fields, the mean top probability and the accuracy."""
    out = {}
    for b in bins:
        if b["candidate"] == candidate and b["width"] == width:
            o = out.setdefault(b["bin"], {"bin": b["bin"], "low": b["low"], "high": b["high"], "fields": 0, "sum_top": 0.0, "sum_hit": 0.0})
            o["fields"] += b["fields"]
            o["sum_top"] += b["sum_top"]
            o["sum_hit"] += b["sum_hit"]
    rows = []
    for b in sorted(out):
        o = out[b]
        rows.append({"candidate": candidate, "width": width, "bin": b, "low": o["low"], "high": o["high"], "fields": o["fields"],
                     "confidence": o["sum_top"] / o["fields"], "accuracy": o["sum_hit"] / o["fields"]})
    return rows


def summarise(rows: Sequence[dict], bins: Sequence[dict], widths: Sequence[int] = (1, 2, 3)) -> List[dict]:
    """Per candidate and width over the held-out populations, each population one fold with equal
    weight: the mean log score and accuracy with their SE over the folds, the paired difference from
    PLAIN with its SE, how many folds the candidate beat PLAIN on, the mean regret against OWN, the
    calibration error of the pooled fields, and the promise at 0.99 pooled over the answers."""
    out = []
    for name in (OWN,) + CANDIDATES:
        for w in widths:
            rs = [r for r in rows if r["candidate"] == name and r["width"] == w]
            if not rs:
                continue
            ls, ls_se = _mean_se([r["log_score"] for r in rs])
            ex, ex_se = _mean_se([r["exact"] for r in rs])
            d_ls, d_ls_se = _mean_se([r["log_score_vs_plain"] for r in rs])
            d_ex, d_ex_se = _mean_se([r["exact_vs_plain"] for r in rs])
            pooled = pooled_bins(bins, name, w)
            n = sum(b["fields"] for b in pooled)
            ece = sum(b["fields"] / n * abs(b["accuracy"] - b["confidence"]) for b in pooled) if n else float("nan")
            n_ans = sum(r["n_answered"] for r in rs)
            errors = sum(r["errors"] for r in rs)
            out.append({"candidate": name, "width": w, "populations": len(rs),
                        "log_score_mean": ls, "log_score_se": ls_se, "log_loss_mean": -ls,
                        "exact_mean": ex, "exact_se": ex_se,
                        "log_score_vs_plain": d_ls, "log_score_vs_plain_se": d_ls_se,
                        "exact_vs_plain": d_ex, "exact_vs_plain_se": d_ex_se,
                        "wins_vs_plain": int(sum(r["log_score_vs_plain"] > 0 for r in rs)),
                        "regret_mean": _mean_se([r["regret"] for r in rs])[0],
                        "loss_mean": _mean_se([r["loss"] for r in rs])[0],
                        "ece_pooled": ece, "ece_mean": _mean_se([r["ece"] for r in rs])[0],
                        "answered_mean": _mean_se([r["answered"] for r in rs])[0],
                        "precision_pooled": float((n_ans - errors) / n_ans) if n_ans else float("nan"),
                        "fields": n})
    return out


def winner(summary: Sequence[dict], widths: Sequence[int] = (1, 2, 3)) -> dict:
    """The candidate with the best mean held-out log score over the widths, and the one with the best
    accuracy, each with its paired difference from PLAIN at every width."""
    def mean_over(name, key):
        return float(np.mean([r[key] for r in summary if r["candidate"] == name and r["width"] in widths]))
    held = [c for c in CANDIDATES if any(r["candidate"] == c for r in summary)]
    by_log = max(held, key=lambda c: mean_over(c, "log_score_mean"))
    by_exact = max(held, key=lambda c: mean_over(c, "exact_mean"))
    out = {"by_log_score": by_log, "by_accuracy": by_exact,
           "log_score_over_widths": {c: mean_over(c, "log_score_mean") for c in held},
           "exact_over_widths": {c: mean_over(c, "exact_mean") for c in held}}
    for which, name in (("by_log_score", by_log), ("by_accuracy", by_exact)):
        out[which + "_vs_plain"] = [{"width": r["width"], "log_score": r["log_score_vs_plain"], "log_score_se": r["log_score_vs_plain_se"],
                                     "exact": r["exact_vs_plain"], "exact_se": r["exact_vs_plain_se"], "wins": r["wins_vs_plain"],
                                     "populations": r["populations"]}
                                    for r in summary if r["candidate"] == name]
    return out
