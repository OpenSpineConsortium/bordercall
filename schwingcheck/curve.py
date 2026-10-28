"""Step e's build-up study: how often the rule names a field right, and how long it takes, as the
measures are added one at a time, from one measure to all 32 of the pool (TODO.md, item P, step e).

    python -m schwingcheck curve run --outdir records/curve-2026-10-28     # the record, curve.nc
    python -m schwingcheck curve table --record records/curve-2026-10-28/curve.nc
    python -m schwingcheck curve figures --record records/curve-2026-10-28/curve.nc
    python -m schwingcheck curve check --record records/curve-2026-10-28/curve.nc

The owner's words of 27 October 2026, 21:27 UTC: "ok now contineu the work but do measure the speed
and accuracy as the number of features per sample increase all the way to all the possible
measurements". The measures are the 32 of measures.pool(), each with its own error and power of
the size, and the rule integrates the size on the trapezoid (rule.trapezoid) throughout.

The columns. The scoring columns are the archive's: 2,000 typical columns from seed 97, the seven
drawn exactly as the record of 2026-10-26 drew them, and the other 25 measures of the pool drawn
for the same patients from seed 197, given their sizes (columns.draw_columns, `scale`), so that the
seven's values stay the record's and rung 0 can be held to it. The selection columns, which choose
the order and are never scored, are 100 typical columns drawn the same way from seeds 311 and 312.
Each of the five anomalous phenotypes has 150 columns from seed 99, the archive's supplement's, and
the other measures from seed 314; a field there is judged by the name its own column's count gives
its middle body, as the supplement judged it, so a T13 or an L6 is never named right.

The order. Forward selection from no measure on the selection columns: at each step the measure
whose addition gives the smallest log loss of the true place, the mean over fields summed over 1,
3 and 9 bodies, joins the ones before it, an earlier measure of the pool's order winning a tie.
Every prefix of the order is then scored on the scoring columns, so the curve reports no number
from the columns that chose it.

What is scored besides the prefixes: the seven, rung 0; the seven with each family of measures
added alone, and the families added one after another (the pedicles, the processes, the facets,
the interfacet distances, then the rest of the body and the canal, which takes the ladder to all
32); the lengths, the seven with the areas and the seven with the angles; and what an AP view
reads, what a lateral view reads, both, and everything (measures.py's planes).

The arms, each scored on its own columns:

- nominal: the scoring columns and the five anomalous phenotypes, the rule built on the table as
  printed;
- errors-0.5 and errors-2: every measure's error halved or doubled in the columns and in the rule
  alike, since the errors are a stated assumption and the gain from a measure depends on them;
- correlated: a patient's offsets correlated at 0.4 between measures (the archive's combined
  world), all 32 drawn in one stream from seed 331; the rule, which multiplies its measures as
  independent, does not know it, so this arm measures what treating them so costs;
- people-P-nominal and people-P-predictive, the data axis: the table re-estimated from P people
  drawn from the generator with no size spread and no measurement error, as exact.py's specimen
  worlds draw twelve (P = 12, 50, 200 and 2,000; 8, 4, 2 and 1 tables from seed 317), the rule
  built on the estimate as if it were exact (nominal) or with each SD widened to the spread of a
  new person about a P-person mean and SD, a Student t on P - 1 degrees of freedom whose variance
  is (1 + 1/P)(P - 1)/(P - 3) times the SD squared (predictive, exact.py's rule for twelve), each
  scored on the first 200 scoring columns and the tables' fields pooled.

The rates of every arm, phenotype, subset and width are the share named exactly, the share within
one level (a T13 counted half-way between T12 and L1 and an L6 one below L5), the share named at a
posterior of 0.99 and the precision there, the log loss of the true place and the error the
posterior itself predicts (typical columns only, since an anomalous body may have no place), and
the mean size of the 99 per cent set, each share with its standard error clustered by column.

The time to name one field, single-threaded, is measured at every prefix of the order and every
width, with the rule built beforehand as a service would build it once: the median and the
largest over 30 single fields, and the mean per field over a batch of 128, for rule.py on the
trapezoid's nodes and on the Gauss-Hermite ones and for the compiled rule (compiled.py) on the
trapezoid's; and NUTS on the naming model (model.py) at 7, 16 and 32 measures of the order,
with how far its posterior falls from the exact one.
"""
from __future__ import annotations

import json
import math
import multiprocessing
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import LEVELS
from . import columns as C
from . import measures as MS
from . import rule as R
from . import score as S
from . import table as T

WIDTHS = (1, 3, 9)
ANOMALOUS_WIDTHS = (1, 3, 5, 9)
ANOMALOUS = ("four_lumbar", "six_lumbar", "t13", "lumbar_rib", "no_rib_t12")
SCORE_SEED, EXTRA_SEED, N_SCORE = 97, 197, 2000
SELECT_SEED, SELECT_EXTRA_SEED, N_SELECT = 311, 312, 100
ANOMALOUS_SEED, ANOMALOUS_EXTRA_SEED, N_ANOMALOUS = 99, 314, 150
ERROR_SCALES = (0.5, 2.0)
CORRELATED_SEED, R_BETWEEN = 331, 0.4
WORLD_SEED, N_WORLD_COLUMNS = 317, 200
WORLDS = {12: 8, 50: 4, 200: 2, 2000: 1}            # tables drawn per number of people
NUTS_MEASURES = (7, 16, 32)
NUTS_FIELDS, NUTS_DRAWS, NUTS_TUNE, NUTS_CHAINS, NUTS_SEED = 4, 500, 500, 2, 7
SPEED_CALLS, SPEED_BATCH = 30, 128
CLAIM = 0.99
PROCESSES = 4
JOB_COLUMNS = 25                                     # columns per job of the pool of processes
FIELD_BLOCK = 128                                    # fields per log likelihood array, to bound memory
FAMILIES = ("pedicles", "processes", "facets", "interfacet", "body")
FAMILY_NAMES = {"pedicles": "the pedicles", "processes": "the processes", "facets": "the facets",
                "interfacet": "the interfacet distances", "body": "the rest of the body and the canal"}
STATS = ("n_fields", "n_columns", "exact", "exact_se", "within_one", "within_one_se", "answered", "answered_se",
         "precision", "precision_se", "errors", "log_loss", "predicted_error", "set_size",
         "exact_table_sd", "answered_table_sd", "precision_table_sd")
# the half-step scale on which "within one level" is read: C3 0 ... T12 16, T13 16.5, L1 17 ... L5 21, L6 22
POSITION = dict({lv: float(i) for i, lv in enumerate(LEVELS)}, T13=LEVELS.index("T12") + 0.5, L6=float(len(LEVELS)))
PLACE_POSITION = np.array([POSITION[lv] for lv in LEVELS])


# ---- the measures and their subsets ---------------------------------------------------------

def family_of(m: MS.Measure) -> str:
    """The part of the vertebra a measure of the pool describes."""
    if m.name.startswith("pedicle"):
        return "pedicles"
    if m.name.startswith(("spinous", "transverse")):
        return "processes"
    if m.name.startswith("interfacet"):
        return "interfacet"
    if m.name.startswith("facet"):
        return "facets"
    return "body"


def subsets(pool: Sequence[MS.Measure], order: Sequence[int]) -> Dict[str, List[int]]:
    """Every subset the study scores, by name, as indices into the pool: the prefixes of the order
    (prefix-01 to prefix-32), then the named ones."""
    keys = [m.key for m in pool]
    seven = [keys.index(k) for k in MS.SPINEPS_7]
    fam = {f: [i for i, m in enumerate(pool) if family_of(m) == f and i not in seven] for f in FAMILIES}
    kind = {k: [i for i, m in enumerate(pool) if m.kind == k] for k in ("length", "area", "angle")}
    plane = {p: [i for i, m in enumerate(pool) if p in m.planes] for p in ("ap", "lateral")}
    out = {"prefix-%02d" % k: list(order[:k]) for k in range(1, len(order) + 1)}
    out["seven"] = seven
    for f in FAMILIES:
        out["seven+" + f] = sorted(seven + fam[f])
    ladder = list(seven)
    for f in FAMILIES:
        ladder = sorted(ladder + fam[f])
        out["ladder-" + f] = list(ladder)
    out["lengths"] = kind["length"]
    out["seven+areas"] = sorted(set(seven) | set(kind["area"]))
    out["seven+angles"] = sorted(set(seven) | set(kind["angle"]))
    out["ap"] = plane["ap"]
    out["lateral"] = plane["lateral"]
    out["ap+lateral"] = sorted(set(plane["ap"]) | set(plane["lateral"]))
    out["all"] = list(range(len(pool)))
    return out


def prefixes_and_seven(names: Sequence[str]) -> List[str]:
    """The subsets the robustness arms score: the prefixes of the order and the seven."""
    return [n for n in names if n.startswith("prefix-") or n == "seven"]


# ---- the columns ----------------------------------------------------------------------------

def _keys(measures: Sequence[MS.Measure]) -> List[str]:
    return [MS.archive_key(m) for m in measures]


def draw_pool(pool: Sequence[MS.Measure], phenotype: str, seed: int, extra_seed: int, n: int,
              error_scale: float = 1.0) -> C.Columns:
    """n columns of one phenotype with every measure of the pool, in the pool's order: the seven
    from `seed` exactly as the archive draws them, the rest from `extra_seed` for the same patients."""
    seven = MS.select(MS.SPINEPS_7)
    rest = [m for m in pool if m.key not in MS.SPINEPS_7]
    first = C.draw_columns(MS.reference(seven), [phenotype], seed, n, _keys(seven),
                           noise_mm=MS.errors(seven) * error_scale, power=MS.powers(seven))
    more = C.draw_columns(MS.reference(rest), [phenotype], extra_seed, n, _keys(rest),
                          noise_mm=MS.errors(rest) * error_scale, power=MS.powers(rest), scale=first.scale)
    if first.levels != more.levels:
        raise AssertionError("the two draws laid the columns out differently")
    drawn = [m.key for m in seven] + [m.key for m in rest]
    where = [drawn.index(m.key) for m in pool]
    values = np.concatenate([first.values, more.values], axis=2)[:, :, where]
    return C.Columns(values=values, levels=first.levels, measures=[m.key for m in pool], phenotype=first.phenotype,
                     scale=first.scale, transitional_at=first.transitional_at, blend=first.blend, seed=seed,
                     meta=dict(first.meta, extra_seed=extra_seed, error_scale=error_scale))


def draw_correlated(pool: Sequence[MS.Measure], seed: int, n: int, r_between: float) -> C.Columns:
    """n typical columns with every measure of the pool drawn in one stream, a patient's offsets
    correlated at r_between between measures."""
    return C.draw_columns(MS.reference(pool), ["typical"], seed, n, _keys(pool), r_between=r_between,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))


def estimated_table(pool: Sequence[MS.Measure], people: int, rng) -> Tuple[np.ndarray, np.ndarray]:
    """The table (measures, levels) re-estimated from `people` typical columns drawn from the
    generator with no size spread and no measurement error, as exact.redrawn_table's specimens:
    each level's mean and SD over the people."""
    spec = C.draw_columns(MS.reference(pool), ["typical"], int(rng.integers(1 << 30)), people, _keys(pool),
                          noise_mm=0.0, scale_sd=0.0, power=MS.powers(pool))
    vals = spec.values[:, :len(LEVELS), :]
    return vals.mean(0).T.copy(), vals.std(0, ddof=1).T.copy()


def predictive_factor(people: int) -> float:
    """The SD of a new person about a table of `people`: sqrt((1 + 1/P)(P - 1)/(P - 3))."""
    return math.sqrt((1.0 + 1.0 / people) * (people - 1.0) / (people - 3.0))


# ---- one arm's work -------------------------------------------------------------------------

@dataclass
class Arm:
    """What one arm scores: its columns, the table and errors its rule is built on, its widths and
    subsets; `world` tells the tables of the data axis apart, whose fields are pooled."""
    name: str
    phenotype: str
    values: np.ndarray
    levels: List[List[str]]
    mu: np.ndarray
    sd: np.ndarray
    noise: np.ndarray
    power: np.ndarray
    widths: Tuple[int, ...]
    subsets: List[str]
    world: int = 0
    settings: dict = field(default_factory=dict)


def true_positions(start: np.ndarray, col: np.ndarray, levels: Sequence[Sequence[str]], n: int) -> np.ndarray:
    """Where the middle body of each field sits on the half-step scale of POSITION, by the name
    its own column's count gives it."""
    t = S.target_offset(n)
    return np.array([POSITION[levels[c][s + t]] for s, c in zip(start, col)])


def field_stats(post: np.ndarray, start: np.ndarray, truth_at: np.ndarray, n: int, typical: bool) -> Dict[str, np.ndarray]:
    """What one posterior over places did on each field: right or not by the name of the middle
    body (truth_at, true_positions), within one level, its top posterior, the log posterior of the
    true place (typical columns, where the place is the field's start) and the size of its 99 per
    cent set."""
    call = post.argmax(1)
    said_at = PLACE_POSITION[call + S.target_offset(n)]
    logp = np.log(np.maximum(post[np.arange(len(start)), start], 1e-300)) if typical else np.full(len(start), np.nan)
    size, _ = R.credible_sets(post, CLAIM)
    return {"hit": said_at == truth_at, "within": np.abs(said_at - truth_at) <= 1.0, "top": post.max(1),
            "logp": logp, "size": size.astype(np.int16)}


def score_fields(X: np.ndarray, offsets: np.ndarray, arm: Arm, names: Sequence[str], index: Dict[str, List[int]],
                 nodes) -> Dict[str, np.ndarray]:
    """The posterior over places of each field under every subset named, as one log likelihood
    per measure: the prefixes of the order read off its running sum, the rest summed afresh."""
    sizes, logw = nodes
    LL = R.loglik(X, offsets, arm.mu, arm.sd, R.SYNTH, sizes=sizes, noise=arm.noise, power=arm.power)
    order = index["prefix-%02d" % LL.shape[2]]                 # the whole order, the longest prefix
    running = np.cumsum(LL[:, :, order, :], axis=2)
    out = {}
    for name in names:
        idx = index[name]
        total = running[:, :, len(idx) - 1, :] if name.startswith("prefix-") else LL[:, :, idx, :].sum(2)
        out[name] = R.posterior(R.logsumexp(total + logw, 2))
    return out


_ARMS: List[Arm] = []
_INDEX: Dict[str, List[int]] = {}


def run_job(job: Tuple[int, int, int, int]) -> Tuple[int, int, int, dict]:
    """One job of the pool: the fields of columns c0 to c1 of one arm at one width."""
    from threadpoolctl import threadpool_limits
    a, n, c0, c1 = job
    arm = _ARMS[a]
    offsets = np.arange(n)
    nodes = R.trapezoid(R.SYNTH["scale_sd"])
    X, start, col = C.fields(arm.values[c0:c1], offsets)
    col = col + c0
    truth_at = true_positions(start, col, arm.levels, n)
    parts: Dict[str, List[dict]] = {name: [] for name in arm.subsets}
    with threadpool_limits(1):
        for f0 in range(0, len(X), FIELD_BLOCK):
            f1 = min(len(X), f0 + FIELD_BLOCK)
            posts = score_fields(X[f0:f1], offsets, arm, arm.subsets, _INDEX, nodes)
            for name, post in posts.items():
                parts[name].append(field_stats(post, start[f0:f1], truth_at[f0:f1], n, arm.phenotype == "typical"))
    stats = {name: {k: np.concatenate([p[k] for p in ps]) for k in ps[0]} for name, ps in parts.items() if ps}
    return a, n, c0, {"col": col, "world": arm.world, "stats": stats}


def rates(stats: Dict[str, np.ndarray], group: np.ndarray) -> dict:
    """The rates of one arm, phenotype, subset and width from its fields' stats."""
    hit, within, top = stats["hit"].astype(float), stats["within"].astype(float), stats["top"]
    said = top >= CLAIM
    inv = np.unique(group, return_inverse=True)[1]
    wrong = np.bincount(inv, weights=said & (hit == 0))
    answered = np.bincount(inv, weights=said)
    out = {"n_fields": int(len(hit)), "n_columns": int(inv.max() + 1) if len(inv) else 0,
           "exact": float(hit.mean()), "exact_se": S.clustered_se(hit, group),
           "within_one": float(within.mean()), "within_one_se": S.clustered_se(within, group),
           "answered": float(said.mean()), "answered_se": S.clustered_se(said.astype(float), group),
           "precision": float(hit[said].mean()) if said.any() else float("nan"),
           "precision_se": S.ratio_se(wrong, answered), "errors": int(wrong.sum()),
           "log_loss": float(-np.mean(stats["logp"])) if np.all(np.isfinite(stats["logp"])) else float("nan"),
           "predicted_error": float((1.0 - top).mean()) if np.all(np.isfinite(stats["logp"])) else float("nan"),
           "set_size": float(stats["size"].mean())}
    return out


# ---- the order ------------------------------------------------------------------------------

def log_loss(total: np.ndarray, truth: np.ndarray, logw: np.ndarray) -> float:
    """The mean over fields of minus the log posterior of the true place, from the summed log
    likelihood (fields, places, nodes)."""
    logev = R.logsumexp(total + logw, 2)
    return float(-(logev[np.arange(len(truth)), truth] - R.logsumexp(logev, 1)).mean())


def selection_loglik(pool: Sequence[MS.Measure], cols: C.Columns, n: int, nodes) -> Tuple[np.ndarray, np.ndarray]:
    """Every measure's log likelihood on the selection fields of one width, (fields, places,
    measures, nodes), kept in single precision, which ranks the measures as well as double does
    in a quarter of the memory of the three widths in double."""
    mu, sd = MS.arrays(pool)
    offsets = np.arange(n)
    X, truth, _ = C.fields(cols.values, offsets)
    parts = [R.loglik(X[f:f + FIELD_BLOCK], offsets, mu, sd, R.SYNTH, sizes=nodes[0], noise=MS.errors(pool),
                      power=MS.powers(pool)).astype(np.float32) for f in range(0, len(X), FIELD_BLOCK)]
    return np.concatenate(parts), truth


def greedy_order(pool: Sequence[MS.Measure], cols: C.Columns, widths: Sequence[int] = WIDTHS,
                 log=print) -> Tuple[List[int], List[dict]]:
    """Forward selection from no measure: at each step the measure whose addition gives the
    smallest log loss of the true place, summed over the widths, joins the order."""
    from threadpoolctl import threadpool_limits
    nodes = R.trapezoid(R.SYNTH["scale_sd"])
    with threadpool_limits(1):
        parts = [selection_loglik(pool, cols, n, nodes) for n in widths]
    running = [np.zeros((LL.shape[0], LL.shape[1], LL.shape[3])) for LL, _ in parts]
    order: List[int] = []
    trace: List[dict] = []
    for step in range(len(pool)):
        best = None
        for m in range(len(pool)):
            if m in order:
                continue
            losses = [log_loss(run + LL[:, :, m, :], truth, nodes[1]) for (LL, truth), run in zip(parts, running)]
            if best is None or sum(losses) < best[0]:
                best = (sum(losses), m, losses)
        order.append(best[1])
        for (LL, _), run in zip(parts, running):
            run += LL[:, :, best[1], :]
        trace.append({"step": step + 1, "measure": pool[best[1]].key, "loss": best[0],
                      "loss_by_width": {str(n): l for n, l in zip(widths, best[2])}})
        log("order: %2d %-26s log loss %.4f" % (step + 1, pool[best[1]].key, best[0]))
    return order, trace


# ---- the arms -------------------------------------------------------------------------------

def make_arms(pool: Sequence[MS.Measure], names: Sequence[str], quick: bool = False) -> List[Arm]:
    """Every arm of the study, columns drawn. quick shrinks every count for the tests."""
    mu, sd = MS.arrays(pool)
    noise, power = MS.errors(pool), MS.powers(pool)
    n_score = 20 if quick else N_SCORE
    n_anom = 6 if quick else N_ANOMALOUS
    n_world = 10 if quick else N_WORLD_COLUMNS
    worlds = {12: 2, 2000: 1} if quick else WORLDS
    robust = prefixes_and_seven(names)
    arms = []
    score = draw_pool(pool, "typical", SCORE_SEED, EXTRA_SEED, n_score)
    arms.append(Arm("nominal", "typical", score.values, score.levels, mu, sd, noise, power, WIDTHS, list(names)))
    for ph in ANOMALOUS:
        c = draw_pool(pool, ph, ANOMALOUS_SEED, ANOMALOUS_EXTRA_SEED, n_anom)
        arms.append(Arm("nominal", ph, c.values, c.levels, mu, sd, noise, power, ANOMALOUS_WIDTHS, list(names)))
    for f in ERROR_SCALES:
        c = draw_pool(pool, "typical", SCORE_SEED, EXTRA_SEED, n_score, error_scale=f)
        arms.append(Arm("errors-%g" % f, "typical", c.values, c.levels, mu, sd, noise * f, power, WIDTHS, robust,
                        settings={"error_scale": f}))
    c = draw_correlated(pool, CORRELATED_SEED, n_score, R_BETWEEN)
    arms.append(Arm("correlated", "typical", c.values, c.levels, mu, sd, noise, power, WIDTHS, robust,
                    settings={"r_between": R_BETWEEN}))
    rng = np.random.default_rng(WORLD_SEED)
    for people, n_tables in worlds.items():
        for w in range(n_tables):
            emu, esd = estimated_table(pool, people, rng)
            for rule, fac in (("nominal", 1.0), ("predictive", predictive_factor(people))):
                arms.append(Arm("people-%d-%s" % (people, rule), "typical", score.values[:n_world], score.levels[:n_world],
                                emu, esd * fac, noise, power, WIDTHS, robust, world=w,
                                settings={"people": people, "rule": rule, "sd_factor": fac, "tables": n_tables}))
    return arms


def jobs_of(arms: Sequence[Arm]) -> List[Tuple[int, int, int, int]]:
    """Every (arm, width, first column, last column) of the study, the widest fields first, since
    their jobs run longest."""
    out = []
    for a, arm in enumerate(arms):
        for n in arm.widths:
            for c0 in range(0, len(arm.values), JOB_COLUMNS):
                out.append((a, n, c0, min(len(arm.values), c0 + JOB_COLUMNS)))
    return sorted(out, key=lambda j: (j[1], -(j[3] - j[2])))


def run_arms(arms: List[Arm], index: Dict[str, List[int]], processes: int = PROCESSES, log=print) -> Dict[tuple, dict]:
    """Every job of every arm on a pool of processes, gathered into the rates of every arm,
    phenotype, subset and width, the tables of one arm of the data axis pooled."""
    global _ARMS, _INDEX
    _ARMS, _INDEX = list(arms), dict(index)
    jobs = jobs_of(arms)
    gathered: Dict[tuple, Dict[str, List]] = {}
    t0 = time.time()
    if processes > 1:
        ctx = multiprocessing.get_context("fork")
        with ctx.Pool(processes) as pool:
            results = pool.imap_unordered(run_job, jobs)
            gathered = _gather(results, arms, len(jobs), t0, log)
    else:
        gathered = _gather(map(run_job, jobs), arms, len(jobs), t0, log)
    out = {}
    for (name, phenotype, n), parts in gathered.items():
        for sub in parts["stats"][0]:
            out[(name, phenotype, sub, n)] = pooled_rates(parts, sub)
    return out


def pooled_rates(parts: Dict[str, List], sub: str) -> dict:
    """One subset's rates over every job of an arm, phenotype and width, clustered by column; where
    the arm's fields come from several tables (the data axis), their columns are the same ones, so
    the clusters stay the columns, and the spread of the rates between tables is given beside them."""
    def joined(which):
        stats = {k: np.concatenate([p[sub][k] for p, keep in zip(parts["stats"], which) if keep])
                 for k in parts["stats"][0][sub]}
        return stats, np.concatenate([c for c, keep in zip(parts["col"], which) if keep])
    out = rates(*joined([True] * len(parts["col"])))
    worlds = sorted(set(parts["world"]))
    for s in ("exact", "answered", "precision"):
        out[s + "_table_sd"] = float("nan")
    if len(worlds) > 1:
        each = [rates(*joined([w == world for w in parts["world"]])) for world in worlds]
        for s in ("exact", "answered", "precision"):
            out[s + "_table_sd"] = float(np.std([e[s] for e in each], ddof=1))
    return out


def _gather(results, arms: Sequence[Arm], n_jobs: int, t0: float, log) -> Dict[tuple, Dict[str, List]]:
    gathered: Dict[tuple, Dict[str, List]] = {}
    for i, (a, n, c0, res) in enumerate(results):
        arm = arms[a]
        g = gathered.setdefault((arm.name, arm.phenotype, n), {"col": [], "world": [], "stats": []})
        g["col"].append(res["col"])
        g["world"].append(res["world"])
        g["stats"].append(res["stats"])
        if (i + 1) % 50 == 0 or i + 1 == n_jobs:
            log("scored %d of %d jobs in %.0f s" % (i + 1, n_jobs, time.time() - t0))
    return gathered


# ---- the time to name a field ---------------------------------------------------------------

def _numpy_namer(mu, sd, noise, power, offsets, nodes):
    """rule.py with its table blocks built once, as a service builds them for a pattern of offsets."""
    sizes, logw = nodes
    blocks = R.table_blocks(offsets, mu, sd, R.SYNTH, sizes, noise, power)

    def name(X):
        LL = R.loglik(X, offsets, mu, sd, R.SYNTH, sizes=sizes, blocks=blocks)
        return R.posterior(R.log_evidence(LL, logw))
    return name


def _compiled_namer(mu, sd, noise, power, offsets, nodes):
    from . import compiled as K
    rule = K.ExactRule(mu, sd, noise=noise, power=power, nodes=nodes)
    hyp = K.hypotheses(rule.n_levels, [offsets])

    def name(X):
        return rule.evaluate(X, hyp)["all"]["post"]
    return name


ENGINES = {"numpy-trapezoid": (_numpy_namer, "trapezoid"), "numpy-gauss-hermite": (_numpy_namer, "gauss-hermite"),
           "pytensor-trapezoid": (_compiled_namer, "trapezoid")}


def _nodes(kind: str):
    return R.trapezoid(R.SYNTH["scale_sd"]) if kind == "trapezoid" else R.quadrature(R.SYNTH["scale_sd"])


def time_engine(namer, X: np.ndarray, calls: int = SPEED_CALLS, batch: int = SPEED_BATCH) -> dict:
    """The time to name one field, called one field at a time (median and largest over `calls`)
    and in a batch (the mean per field), after one call that warms the caches."""
    namer(X[:1])
    single = []
    for i in range(calls):
        t0 = time.perf_counter()
        namer(X[i % len(X):i % len(X) + 1])
        single.append(time.perf_counter() - t0)
    t0 = time.perf_counter()
    namer(X[:batch])
    per = (time.perf_counter() - t0) / min(batch, len(X))
    return {"median_ms": 1e3 * float(np.median(single)), "max_ms": 1e3 * float(np.max(single)), "batch_ms": 1e3 * per}


def speed(pool: Sequence[MS.Measure], order: Sequence[int], cols: C.Columns, widths: Sequence[int] = WIDTHS,
          ks: Optional[Sequence[int]] = None, engines: Sequence[str] = tuple(ENGINES), calls: int = SPEED_CALLS,
          batch: int = SPEED_BATCH, log=print) -> Dict[tuple, dict]:
    """{(engine, measures, width): times} at every prefix of the order, single-threaded."""
    from threadpoolctl import threadpool_limits
    mu, sd = MS.arrays(pool)
    noise, power = MS.errors(pool), MS.powers(pool)
    ks = range(1, len(order) + 1) if ks is None else ks
    out = {}
    with threadpool_limits(1):
        for n in widths:
            offsets = np.arange(n)
            X, _, _ = C.fields(cols.values, offsets)
            for engine in engines:
                make, kind = ENGINES[engine]
                nodes = _nodes(kind)
                for k in ks:
                    idx = list(order[:k])
                    namer = make(mu[idx], sd[idx], noise[idx], power[idx], offsets, nodes)
                    out[(engine, k, n)] = time_engine(namer, X[:, idx, :], calls, batch)
                log("speed: %s at %d bodies, %d measures: %.2f ms a field alone, %.2f ms in a batch"
                    % (engine, n, ks[-1], out[(engine, ks[-1], n)]["median_ms"], out[(engine, ks[-1], n)]["batch_ms"]))
    return out


def nuts_speed(pool: Sequence[MS.Measure], order: Sequence[int], cols: C.Columns, ks: Sequence[int] = NUTS_MEASURES,
               n: int = 3, n_fields: int = NUTS_FIELDS, log=print) -> Dict[int, dict]:
    """NUTS on the naming model at each number of measures of the order: the seconds per field to
    build the model, to sample and to average the posterior, and the largest distance of its
    posterior from the exact rule's."""
    from threadpoolctl import threadpool_limits
    from . import compiled as K
    from . import model as MD
    mu, sd = MS.arrays(pool)
    noise, power = MS.errors(pool), MS.powers(pool)
    offsets = np.arange(n)
    X, _, _ = C.fields(cols.values, offsets)
    hyp = K.hypotheses(len(LEVELS), [offsets])
    out = {}
    with threadpool_limits(1):
        for k in ks:
            idx = list(order[:k])
            Xk = X[:n_fields, idx, :]
            t0 = time.perf_counter()
            m = MD.naming(Xk, hyp, mu[idx], sd[idx], [pool[i].key for i in idx], noise=noise[idx], power=power[idx])
            t1 = time.perf_counter()
            idata = MD.sample(m, draws=NUTS_DRAWS, tune=NUTS_TUNE, chains=NUTS_CHAINS, seed=NUTS_SEED)
            t2 = time.perf_counter()
            post, mcse = MD.hypothesis_posterior(m, idata)
            t3 = time.perf_counter()
            exact = _numpy_namer(mu[idx], sd[idx], noise[idx], power[idx], offsets, _nodes("trapezoid"))(Xk)
            out[k] = {"fields": n_fields, "width": n, "draws": NUTS_DRAWS, "tune": NUTS_TUNE, "chains": NUTS_CHAINS,
                      "build_s": (t1 - t0) / n_fields, "sample_s": (t2 - t1) / n_fields, "posterior_s": (t3 - t2) / n_fields,
                      "max_abs_diff": float(np.abs(post - exact).max()), "max_mcse": float(mcse.max())}
            log("nuts: %d measures, %.1f s a field to sample, posterior within %.1e of the exact one"
                % (k, out[k]["sample_s"], out[k]["max_abs_diff"]))
    return out


# ---- the record -----------------------------------------------------------------------------

def build_record(rate_rows: Dict[tuple, dict], pool: Sequence[MS.Measure], order: Sequence[int], trace: Sequence[dict],
                 index: Dict[str, List[int]], arms: Sequence[Arm], times: Dict[tuple, dict], nuts: Dict[int, dict],
                 command: str, quick: bool):
    """The study as one xarray DataTree: rates (arm, phenotype, subset, width) for every statistic,
    NaN where an arm did not score a subset, phenotype or width; the order and its selection log
    loss; the subsets' members; the times; and in the root's attributes the command, the seeds,
    the settings and the digests."""
    import arviz as az
    import xarray as xr
    from . import __version__
    from .records import code_digest
    arm_names = list(dict.fromkeys(a.name for a in arms))
    phenotypes = ["typical"] + list(ANOMALOUS)
    subs = list(index)
    widths = sorted({n for a in arms for n in a.widths})
    shape = (len(arm_names), len(phenotypes), len(subs), len(widths))
    data = {s: np.full(shape, np.nan) for s in STATS}
    for (name, ph, sub, n), row in rate_rows.items():
        at = (arm_names.index(name), phenotypes.index(ph), subs.index(sub), widths.index(n))
        for s in STATS:
            data[s][at] = row[s]
    dims = ("arm", "phenotype", "subset", "width")
    rates_ds = xr.Dataset({s: (dims, v) for s, v in data.items()},
                          coords={"arm": arm_names, "phenotype": phenotypes, "subset": subs, "width": widths})
    keys = [m.key for m in pool]
    member = np.zeros((len(subs), len(keys)), bool)
    for i, sub in enumerate(subs):
        member[i, index[sub]] = True
    subsets_ds = xr.Dataset({"member": (("subset", "measure"), member)}, coords={"subset": subs, "measure": keys})
    order_ds = xr.Dataset({"measure": ("step", [t["measure"] for t in trace]), "loss": ("step", [t["loss"] for t in trace])},
                          coords={"step": np.arange(1, len(trace) + 1)})
    for n in WIDTHS:
        order_ds["loss_%d" % n] = ("step", [t["loss_by_width"][str(n)] for t in trace])
    tree = xr.DataTree.from_dict({"/rates": rates_ds, "/subsets": subsets_ds, "/order": order_ds,
                                  "/speed": speed_dataset(times), "/nuts": nuts_dataset(nuts)})
    settings = {a.name: a.settings for a in arms if a.settings}
    seeds = {"score": SCORE_SEED, "score_extra": EXTRA_SEED, "select": SELECT_SEED, "select_extra": SELECT_EXTRA_SEED,
             "anomalous": ANOMALOUS_SEED, "anomalous_extra": ANOMALOUS_EXTRA_SEED, "correlated": CORRELATED_SEED,
             "worlds": WORLD_SEED, "nuts": NUTS_SEED}
    counts = {"score": len(arms[0].values), "select": N_SELECT if not quick else None,
              "anomalous": len(arms[1].values), "world_columns": N_WORLD_COLUMNS if not quick else None,
              "worlds": {str(k): v for k, v in WORLDS.items()} if not quick else None, "quick": quick}
    tree.attrs.update({
        "command": command, "seeds": json.dumps(seeds, sort_keys=True), "counts": json.dumps(counts, sort_keys=True),
        "synth": json.dumps(R.SYNTH, sort_keys=True), "settings": json.dumps(settings, sort_keys=True),
        "order": json.dumps([pool[i].key for i in order]),
        "pool": json.dumps([{"key": m.key, "kind": m.kind, "error": m.error, "power": m.size_power,
                             "family": family_of(m), "planes": list(m.planes)} for m in pool]),
        "nuts": json.dumps({str(k): v for k, v in nuts.items()}, sort_keys=True),
        "digests": json.dumps({"panjabi_long.csv": T.sha256(T.LONG_CSV), "schwingcheck": code_digest()}, sort_keys=True),
        "git": json.dumps(git_state(), sort_keys=True),
        "schwingcheck": __version__, "numpy": np.__version__, "xarray": xr.__version__, "arviz": az.__version__,
        "nodes": "trapezoid, step %g in log s out to %g SD" % (R.TRAPEZOID_STEP, R.TRAPEZOID_REACH)})
    return tree


def speed_dataset(times: Dict[tuple, dict]):
    """The times as (engine, measures, width) arrays, NaN where none was measured."""
    import xarray as xr
    engines = list(ENGINES)
    ks = sorted({k for _, k, _ in times}) or [0]
    tw = sorted({n for _, _, n in times}) or list(WIDTHS)
    sp = {s: np.full((len(engines), len(ks), len(tw)), np.nan) for s in ("median_ms", "max_ms", "batch_ms")}
    for (e, k, n), row in times.items():
        for s in sp:
            sp[s][engines.index(e), ks.index(k), tw.index(n)] = row[s]
    return xr.Dataset({s: (("engine", "measures", "width"), v) for s, v in sp.items()},
                      coords={"engine": engines, "measures": ks, "width": tw})


def nuts_dataset(nuts: Dict[int, dict]):
    import xarray as xr
    nk = sorted(nuts) or [0]
    return xr.Dataset({s: ("measures", [nuts[k][s] if k in nuts else np.nan for k in nk])
                       for s in ("build_s", "sample_s", "posterior_s", "max_abs_diff", "max_mcse")},
                      coords={"measures": nk})


def git_state() -> dict:
    """The commit the code ran from and whether the package's files differed from it, so a record
    names the code that made it even after later commits change the package's digest."""
    def git(*a):
        return subprocess.run(["git", "-C", T.ROOT] + list(a), capture_output=True, text=True).stdout.strip()
    return {"commit": git("rev-parse", "HEAD"), "package_changed": bool(git("status", "--porcelain", "--", "schwingcheck"))}


def add_speed(path: str, command: str, quick: bool = False, log=print) -> None:
    """Measure the times on the order a record holds and write them into the record, which is
    done apart from the scoring so that the times are taken with nothing else running."""
    from .records import read, write
    tree = read(path)
    tree.load()
    tree.close()
    pool = MS.pool()
    keys = [m.key for m in pool]
    order = [keys.index(k) for k in json.loads(tree.attrs["order"])]
    cols = draw_pool(pool, "typical", SCORE_SEED, EXTRA_SEED, 20)
    times = speed(pool, order, cols, calls=3 if quick else SPEED_CALLS, batch=8 if quick else SPEED_BATCH,
                  ks=[1, 7, 32] if quick else None, log=log)
    nuts = nuts_speed(pool, order, cols, ks=(7,) if quick else NUTS_MEASURES, log=log)
    parts = {"/" + name: tree[name].to_dataset() for name in ("rates", "subsets", "order")}
    import xarray as xr
    out = xr.DataTree.from_dict(dict(parts, **{"/speed": speed_dataset(times), "/nuts": nuts_dataset(nuts)}))
    out.attrs.update(tree.attrs)
    out.attrs.update({"speed_command": command, "speed_git": json.dumps(git_state(), sort_keys=True),
                      "nuts": json.dumps({str(k): v for k, v in nuts.items()}, sort_keys=True)})
    write(out, path)


def run(outdir: Optional[str], command: str = "", quick: bool = False, processes: int = PROCESSES,
        with_speed: bool = True, log=print):
    """The whole study: the order, every arm, the times, written to outdir/curve.nc."""
    pool = MS.pool()
    t0 = time.time()
    select = draw_pool(pool, "typical", SELECT_SEED, SELECT_EXTRA_SEED, 8 if quick else N_SELECT)
    order, trace = greedy_order(pool, select, log=log)
    log("the order took %.0f s" % (time.time() - t0))
    index = subsets(pool, order)
    arms = make_arms(pool, list(index), quick)
    rate_rows = run_arms(arms, index, processes, log)
    times, nuts = {}, {}
    if with_speed:
        times = speed(pool, order, arms[0], calls=3 if quick else SPEED_CALLS, batch=8 if quick else SPEED_BATCH,
                      ks=[1, 7, 32] if quick else None, log=log)
        nuts = nuts_speed(pool, order, arms[0], ks=(7,) if quick else NUTS_MEASURES, log=log)
    tree = build_record(rate_rows, pool, order, trace, index, arms, times, nuts, command, quick)
    if outdir:
        from .records import write
        write(tree, os.path.join(outdir, "curve.nc"))
    log("the study took %.0f s" % (time.time() - t0))
    return tree
