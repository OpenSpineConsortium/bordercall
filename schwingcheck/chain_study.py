"""The chain of levels scored against step d's rule: the first rung of step e's methods (TODO.md,
item P, step e).

    python -m schwingcheck.chain_study run [--columns 100]      # chain.json, the table as printed, about 8 minutes
    python -m schwingcheck.chain_study axis [--columns 100]     # axis.json, the data axis, about 46 minutes on 3 processes
    python -m schwingcheck.chain_study speed                    # speed.json, the time to name one field, about 20 minutes
    python -m schwingcheck.chain_study table [--table main|claims|weights|axis|speed]   # a record's table
    python -m schwingcheck.chain_study check                    # whether the README's tables are the records'

The records are in records/chain-2026-10-28/.

Fields are drawn by the chain's own law (chain.draw_fields: each step misses a body with
probability 1/6, chain.step_law at chain.SKIP 0.2 cut at one missed, before the fit to the column)
from the generator's columns of the three types,
typical, six-lumbar and with a T13, every measure of the pool drawn for the same patients
(curve.draw_pool). Four rules name the middle body of each, on the same fields:

- consecutive: step d's rule, which takes the bodies as consecutive on a typical column;
- gaps: the chain of the typical column alone, its missed bodies summed out;
- chain: the whole chain, its missed bodies and its three types summed out;
- known gaps: the rule told each field's true gaps, on the typical column (TODO.md item 4c).

Each is scored as curve.py scores (curve.rates: the name right, within one level on curve.POSITION's
scale, the answers at 0.99 with their precision, each with its SE clustered by column), at 1, 3, 5
and 9 bodies, on the seven SPINEPS measures and on all 32. The first three are chain.py's exact sum
over the paths read along their shared beginnings (chain.prepare and chain.logev), which gives
chain.path_logev's answer (the tests hold the two within 1e-9) in a small part of its time, the
smaller the more bodies (`speed`). The chain's L6 and T13 columns are the generator's construction
(chain.extended_table), so on those columns it is scored against the truth it was built from.

A rule with no name for the true body, the three typical-column rules on an L6 or a T13, gives it
a posterior of 0, which name_stats floors at 1e-300, so on those columns their log loss counts
690.8 nats a field for each such body and says only how often it happens.

The chain's type weights, 0.9, 0.05 and 0.05, are a stated choice (chain.WEIGHTS). `run` also
scores the chain at the weights the clinical reread found in the papers (WEIGHT_SETS, PR 21): six
lumbar bodies in 0.5% (Eisenstein 1977, 2 of 443 skeletons with a true L6) to 2.5% (the same 443
with the lumbarised S1 added, 11 of 443), and a rib-bearing body below T12 in 2.3% of 517 adults
on CT (Duman 2026), which no paper tells apart from a T13 and so is the T13's ceiling; the typical
type takes the rest. The fields are the same, so the rows differ only by the prior.

The data axis (`axis`) builds the four rules on the build-up study's own tables (curve.WORLDS from
curve.WORLD_SEED, drawn in curve.make_arms' order, so the same 8, 4, 2 and 2 tables re-estimated
from 12, 50, 200 and 2,000 people), as if exact (nominal) and with each SD widened to a new
person's spread about a P-person table (predictive, curve.predictive_factor), the L6 and T13 built
from each table as from the printed one, and scores them on the same fields as `run`, so every row
of the axis is read against the table as printed on the same fields. Its SEs are curve.pooled_rates':
clustered by column with the tables held fixed, and crossed with the tables, on one degree of
freedom fewer than the tables.

The speed (`speed`) is the time to name the middle body of one field, single-threaded, with the rule
built beforehand as a service would build it once (chain.prepare, whose seconds are given beside),
at 1, 3, 5, 7 and 9 bodies, for the consecutive, gaps and chain rules (the rule told the true gaps
is no rule a service could run, and is not timed) and each measure set alone: the median and the
largest over 30 single fields, and per field in a batch of 128, the median and the largest of five
calls after one that warms them, as curve.time_engine takes them. chain.path_logev, which builds its
blocks inside every call, is timed beside the chain at every width on fewer calls
(REFERENCE_COUNTS). Numba compiles chain.prepare's and chain.logev's loops on their first call in a
process: `speed` compiles them before it sets the thread limit (load_loops), and every pool's
threads are recorded inside the limit, while `run`'s seconds a field for the first cell each of
its processes scores hold the compile.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import os
import re
import time
from typing import Dict, List, Tuple

import numpy as np

from . import chain as CH
from . import curve as CV
from . import measures as MS
from . import rule as R
from . import score as S

WIDTHS = (1, 3, 5, 9)
SPEED_WIDTHS = (1, 3, 5, 7, 9)
ARMS = ("consecutive", "gaps", "chain", "known gaps")
CHAIN_ARMS = ARMS[:3]
SUBSETS = ("seven", "all")
SEED, EXTRA_SEED, FIELD_SEED, PER_COLUMN = 401, 501, 601, 2
RULES = ("nominal", "predictive")
WEIGHT_SETS = {"papers, high": (0.952, 0.025, 0.023), "papers, low": (0.972, 0.005, 0.023)}
PROCESSES = 4
SPEED_COUNTS = {"calls": 30, "batch": 128, "batches": 5}
REFERENCE_COUNTS = {"calls": 3, "batch": 16, "batches": 2}
QUICK = {"columns": 3, "widths": (1, 3), "worlds": {12: 2, 2000: 2}, "speed_widths": (1, 3),
         "speed": {"calls": 2, "batch": 4, "batches": 1}, "reference": {"calls": 1, "batch": 2, "batches": 1}}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD_DIR = os.path.join(ROOT, "records", "chain-2026-10-28")
RECORDS = {"main": os.path.join(RECORD_DIR, "chain.json"), "axis": os.path.join(RECORD_DIR, "axis.json"),
           "speed": os.path.join(RECORD_DIR, "speed.json")}
README = os.path.join(ROOT, "schwingcheck", "README.md")
NAME_POSITION = np.array([CV.POSITION[n] for n in CH.NAMES])


def name_stats(post: np.ndarray, truth: np.ndarray) -> Dict[str, np.ndarray]:
    """What a posterior over NAMES did on each field, in curve.field_stats' terms."""
    said_at, truth_at = NAME_POSITION[post.argmax(1)], NAME_POSITION[truth]
    size, _ = R.credible_sets(post, CV.CLAIM)
    return {"hit": said_at == truth_at, "within": np.abs(said_at - truth_at) <= 1.0, "top": post.max(1),
            "logp": np.log(np.maximum(post[np.arange(len(truth)), truth], 1e-300)), "size": size.astype(np.int16)}


def chains(n_bodies: int) -> Dict[str, CH.Chain]:
    return {"consecutive": CH.build(("typical",), (1.0,), (1.0,), n_bodies),
            "gaps": CH.build(("typical",), (1.0,), CH.step_law(), n_bodies),
            "chain": CH.build(CH.TYPES, None, CH.step_law(), n_bodies)}


def setting():
    """The pool, its subsets, its table, errors and powers, and the size's nodes."""
    pool = MS.pool()
    keys = [m.key for m in pool]
    subsets = {"seven": [keys.index(k) for k in MS.SPINEPS_7], "all": list(range(len(pool)))}
    mu, sd = MS.arrays(pool)
    return pool, subsets, mu, sd, MS.errors(pool), MS.powers(pool), R.trapezoid(R.SYNTH["scale_sd"])


def draw_all(pool, n_columns: int, widths) -> Dict[Tuple[str, int], tuple]:
    """The scored fields of every type and width, (X, names, offsets, col), from the seeds above:
    a type's columns from SEED and EXTRA_SEED plus its index, a width's fields from FIELD_SEED plus
    ten times the type's index plus the width."""
    out = {}
    for ti, kind in enumerate(CH.TYPES):
        cols = CV.draw_pool(pool, kind, SEED + ti, EXTRA_SEED + ti, n_columns)
        for B in widths:
            out[kind, B] = CH.draw_fields(cols, CH.step_law(), B, PER_COLUMN, FIELD_SEED + 10 * ti + B)
    return out


def prepared(n_bodies: int, mu_e, sd_e, subsets, noise, power, nodes) -> Tuple[Dict[str, CH.PathRule], Dict[str, float]]:
    """The three chain rules at this width, each built once, with the seconds each took."""
    rules, seconds = {}, {}
    for arm, ch in chains(n_bodies).items():
        t0 = time.perf_counter()
        rules[arm] = CH.prepare(CH.paths_of(ch), mu_e, sd_e, subsets, noise, power, nodes)
        seconds[arm] = time.perf_counter() - t0
    return rules, seconds


def name_middle(rule: CH.PathRule, X: np.ndarray, t: int) -> Dict[str, np.ndarray]:
    """Body t's posterior over NAMES under each of the rule's subsets."""
    return {k: CH.body_posterior(CH.posterior(v, rule.log_prior), rule.names, t) for k, v in CH.logev(rule, X).items()}


def chain_stats(rule: CH.PathRule, drawn, subsets, power) -> Dict[str, dict]:
    """One chain rule's stats on one type's fields at one width, by subset."""
    X, names, _, _ = drawn
    t = S.target_offset(X.shape[2])
    out = {}
    for k, p in name_middle(rule, X, t).items():
        out[k] = name_stats(p, names[:, t])
        out[k]["floored"] = CV.floored_in(X, subsets[k], power)
    return out


def score_fields(rules, drawn, mu, sd, subsets, noise, power, nodes) -> List[dict]:
    """The four rules on one type's fields at one width, each subset's stats and the seconds a field."""
    X, names, offsets, col = drawn
    B = X.shape[2]
    t = S.target_offset(B)
    truth = names[:, t]
    out = []
    for arm in ARMS:
        t0 = time.perf_counter()
        if arm == "known gaps":
            post = CH.known_pattern_posterior(X, offsets, mu, sd, subsets, noise, power, nodes, t)
        else:
            post = name_middle(rules[arm], X, t)
        seconds = (time.perf_counter() - t0) / len(X)
        for k, p in post.items():
            stats = name_stats(p, truth)
            stats["floored"] = CV.floored_in(X, subsets[k], power)
            out.append({"arm": arm, "subset": k, "seconds": seconds, "stats": stats, "col": col})
    return out


def run(n_columns: int, widths=WIDTHS) -> dict:
    from threadpoolctl import threadpool_limits
    made_by = CV.code_state()
    pool, subsets, mu, sd, noise, power, nodes = setting()
    mu_e, sd_e = CH.extended_table(mu, sd)
    drawn = draw_all(pool, n_columns, widths)
    rows: List[dict] = []
    weight_rows: List[dict] = []
    setup = {}
    with threadpool_limits(1):
        for B in widths:
            rules, seconds = prepared(B, mu_e, sd_e, subsets, noise, power, nodes)
            setup[str(B)] = seconds
            for kind in CH.TYPES:
                for r in score_fields(rules, drawn[kind, B], mu, sd, subsets, noise, power, nodes):
                    rows.append({"type": kind, "bodies": B, "arm": r["arm"], "subset": r["subset"],
                                 "seconds_per_field_both_subsets": r["seconds"], **CV.rates(r["stats"], r["col"])})
            for name, w in WEIGHT_SETS.items():
                rule = CH.prepare(CH.paths_of(CH.build(CH.TYPES, w, CH.step_law(), B)), mu_e, sd_e, subsets, noise, power, nodes)
                for kind in CH.TYPES:
                    for k, st in chain_stats(rule, drawn[kind, B], subsets, power).items():
                        weight_rows.append({"weights": name, "type": kind, "bodies": B, "subset": k,
                                            **CV.rates(st, drawn[kind, B][3])})
    return {"command": "python -m schwingcheck.chain_study run --columns %d" % n_columns, "columns_per_type": n_columns,
            "fields_per_column": PER_COLUMN, "seeds": [SEED, EXTRA_SEED, FIELD_SEED], "skip": CH.SKIP,
            "max_step": CH.MAX_STEP, "weights": CH.WEIGHTS, "widths": list(widths),
            "weight_sets": {k: dict(zip(CH.TYPES, v)) for k, v in WEIGHT_SETS.items()},
            "prepare_seconds": setup, "single_threaded": True, "machine": CV.machine(), "versions": CV.versions(),
            **made(made_by), "rows": rows, "weight_rows": weight_rows}


def made(made_by: dict) -> dict:
    """The code and table a record was made by, taken before any work (curve.code_state), and what
    of them changed by the time the record was built (curve.changed_during), empty when nothing."""
    return {"made_by": made_by, "changed_during_run": CV.changed_during(made_by, CV.code_state())}


# ---- the data axis --------------------------------------------------------------------------

def axis_tables(pool, worlds) -> List[Tuple[int, int, np.ndarray, np.ndarray]]:
    """The build-up study's tables, (people, index, mu, sd), drawn as curve.make_arms draws them:
    one generator from curve.WORLD_SEED, the people in WORLDS' order, the tables of each in turn."""
    rng = np.random.default_rng(CV.WORLD_SEED)
    out = []
    for people, n_tables in worlds.items():
        for w in range(n_tables):
            emu, esd = CV.estimated_table(pool, people, rng)
            out.append((people, w, emu, esd))
    return out


_AXIS: dict = {}


def axis_job(job: Tuple[int, str, int]) -> Tuple[int, str, int, List[dict]]:
    """One table, one rule and one width: the four rules on every type's fields."""
    from threadpoolctl import threadpool_limits
    i, rule, B = job
    a = _AXIS
    people, w, emu, esd = a["tables"][i]
    esd = esd * (CV.predictive_factor(people) if rule == "predictive" else 1.0)
    mu_e, sd_e = CH.extended_table(emu, esd)
    out = []
    with threadpool_limits(1):
        rules, _ = prepared(B, mu_e, sd_e, a["subsets"], a["noise"], a["power"], a["nodes"])
        for kind in CH.TYPES:
            for r in score_fields(rules, a["drawn"][kind, B], emu, esd, a["subsets"], a["noise"], a["power"], a["nodes"]):
                out.append({"type": kind, "arm": r["arm"], "subset": r["subset"], "stats": r["stats"], "col": r["col"]})
    return i, rule, B, out


def axis(n_columns: int, widths=WIDTHS, worlds=None, processes: int = PROCESSES, log=print) -> dict:
    global _AXIS
    made_by = CV.code_state()
    worlds = dict(CV.WORLDS if worlds is None else worlds)
    pool, subsets, mu, sd, noise, power, nodes = setting()
    tables = axis_tables(pool, worlds)
    _AXIS = {"tables": tables, "drawn": draw_all(pool, n_columns, widths), "subsets": subsets, "noise": noise,
             "power": power, "nodes": nodes}
    jobs = sorted(((i, rule, B) for i in range(len(tables)) for rule in RULES for B in widths), key=lambda j: -j[2])
    t0 = time.time()
    if processes > 1:
        with multiprocessing.get_context("fork").Pool(processes) as p:
            results = list(_logged(p.imap_unordered(axis_job, jobs), len(jobs), t0, log))
    else:
        results = list(_logged(map(axis_job, jobs), len(jobs), t0, log))
    parts: Dict[tuple, dict] = {}
    for i, rule, B, out in results:
        people, w = tables[i][0], tables[i][1]
        for r in out:
            g = parts.setdefault((people, rule, r["type"], B, r["arm"]), {"col": [], "world": [], "stats": []})
            g["col"].append(r["col"])
            g["world"].append(w)
            g["stats"].append({r["subset"]: r["stats"]})
    rows = []
    for (people, rule, kind, B, arm), g in sorted(parts.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2], kv[0][3], kv[0][4])):
        for sub in SUBSETS:
            have = [k for k, st in enumerate(g["stats"]) if sub in st]
            sel = {"col": [g["col"][k] for k in have], "world": [g["world"][k] for k in have],
                   "stats": [g["stats"][k] for k in have]}
            rows.append({"people": people, "rule": rule, "tables": worlds[people], "type": kind, "bodies": B, "arm": arm,
                         "subset": sub, **CV.pooled_rates(sel, sub)})
    return {"command": "python -m schwingcheck.chain_study axis --columns %d" % n_columns, "columns_per_type": n_columns,
            "fields_per_column": PER_COLUMN, "seeds": [SEED, EXTRA_SEED, FIELD_SEED], "world_seed": CV.WORLD_SEED,
            "worlds": {str(k): v for k, v in worlds.items()}, "widths": list(widths), "rules": list(RULES),
            "machine": CV.machine(), "versions": CV.versions(), **made(made_by), "rows": rows}


def _logged(results, n: int, t0: float, log):
    for i, r in enumerate(results):
        if (i + 1) % 8 == 0 or i + 1 == n:
            log("axis: %d of %d jobs in %.0f s" % (i + 1, n, time.time() - t0))
        yield r


# ---- the speed ------------------------------------------------------------------------------

def load_loops(subsets, mu_e, sd_e, noise, power, nodes, X: np.ndarray) -> None:
    """Compile chain.prepare's and chain.logev's loops now, on a whole field and one with a value
    not read, outside the thread limit: Numba's first compile loads scipy's own BLAS, and
    threadpool_limits holds only the libraries loaded when it is entered, so a limit entered first
    would leave that one at every thread (curve.load_compiled, the build-up study's same step)."""
    rule = CH.prepare(CH.paths_of(chains(1)["chain"]), mu_e, sd_e, subsets, noise, power, nodes)
    part = np.array(X[:2])
    part[1, 0, 0] = np.nan
    CH.logev(rule, part)


def speed(n_columns: int = 100, widths=SPEED_WIDTHS, counts=None, reference=None, log=print) -> dict:
    """The time to name the middle body of one field, single-threaded (the module's docstring), on
    the typical type's fields of `run`'s seeds."""
    from threadpoolctl import threadpool_limits
    made_by = CV.code_state()
    counts = dict(SPEED_COUNTS if counts is None else counts)
    reference = dict(REFERENCE_COUNTS if reference is None else reference)
    pool, subsets, mu, sd, noise, power, nodes = setting()
    mu_e, sd_e = CH.extended_table(mu, sd)
    drawn = draw_all(pool, n_columns, widths)
    load_loops(subsets, mu_e, sd_e, noise, power, nodes, drawn["typical", widths[0]][0])
    rows = []
    with threadpool_limits(1):
        for B in widths:
            X = drawn["typical", B][0]
            t = S.target_offset(B)
            for arm, ch in chains(B).items():
                pa = CH.paths_of(ch)
                for sub in SUBSETS:
                    one = {sub: subsets[sub]}
                    t0 = time.perf_counter()
                    rule = CH.prepare(pa, mu_e, sd_e, one, noise, power, nodes)
                    setup = time.perf_counter() - t0
                    times = CV.time_engine(lambda x: name_middle(rule, x, t), X, counts["calls"], counts["batch"], counts["batches"])
                    rows.append({"engine": "prepared", "arm": arm, "subset": sub, "bodies": B, "paths": len(pa),
                                 "prepare_s": setup, **times})
                    log("speed: %s, %s, %d bodies: %.2f ms a field alone, %.2f ms in a batch"
                        % (arm, sub, B, times["median_ms"], times["batch_ms"]))
            ch = chains(B)["chain"]
            pa = CH.paths_of(ch)
            for sub in SUBSETS:
                one = {sub: subsets[sub]}

                def ref(x, one=one):
                    ev = CH.path_logev(x, pa, ch, mu_e, sd_e, one, noise, power, nodes)
                    return {k: CH.body_posterior(CH.posterior(v, pa.log_prior), pa.names, t) for k, v in ev.items()}
                times = CV.time_engine(ref, X, reference["calls"], reference["batch"], reference["batches"])
                rows.append({"engine": "path_logev", "arm": "chain", "subset": sub, "bodies": B, "paths": len(pa),
                             "prepare_s": 0.0, **times})
                log("speed: path_logev, %s, %d bodies: %.0f ms a field alone, %.0f ms in a batch"
                    % (sub, B, times["median_ms"], times["batch_ms"]))
        threads = CV.pools()
    return {"command": "python -m schwingcheck.chain_study speed", "columns_per_type": n_columns,
            "counts": counts, "reference_counts": reference, "widths": list(widths), "threads": threads,
            "machine": CV.machine(), "versions": CV.versions(), **made(made_by), "rows": rows}


# ---- the tables -----------------------------------------------------------------------------

def pct(x: float, digits: int = 1) -> str:
    return "-" if x is None or not np.isfinite(x) else "%.*f" % (digits, 100 * x)


def main_table(record: dict) -> str:
    out = ["| Column | Bodies | Measures | " + " | ".join(ARMS) + " |", "|---|---:|---|" + "---:|" * len(ARMS)]
    key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in record["rows"]}
    for kind in CH.TYPES:
        for B in record.get("widths", (1, 3, 5)):
            for k in SUBSETS:
                cells = ["%s (%s)" % (pct(key[kind, B, k, a]["exact"]), pct(key[kind, B, k, a]["exact_se"])) for a in ARMS]
                out.append("| %s | %d | %s | %s |" % (kind.replace("_", "-"), B, k, " | ".join(cells)))
    return "\n".join(out) + "\n"


def claims_table(record: dict, bodies=WIDTHS) -> str:
    """The answers at 0.99: the share answered and right of those answered, each rule, all 32."""
    out = ["| Column | Bodies | " + " | ".join("%s: answered / right" % a for a in ARMS) + " |",
           "|---|---:|" + "---:|" * len(ARMS)]
    key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in record["rows"]}
    for kind in CH.TYPES:
        for B in bodies:
            cells = []
            for a in ARMS:
                r = key[kind, B, "all", a]
                cells.append("%s / %s (%d of %d)" % (pct(r["answered"]), pct(r["precision"], 2),
                                                    r["n_answered"] - r["errors"], r["n_answered"]))
            out.append("| %s | %d | %s |" % (kind.replace("_", "-"), B, " | ".join(cells)))
    return "\n".join(out) + "\n"


def weights_table(record: dict, bodies=(1, 5, 9)) -> str:
    """The chain at its stated type weights and at the clinical reread's (WEIGHT_SETS): each type's
    share named exactly (SE) and the precision of the answers at 0.99, on the same fields; one body
    among the widths, since a lone body is where the prior counts most."""
    stated = {(r["type"], r["bodies"], r["subset"]): r for r in record["rows"] if r["arm"] == "chain"}
    other = {(r["weights"], r["type"], r["bodies"], r["subset"]): r for r in record["weight_rows"]}
    sets = [("stated", CH.WEIGHTS)] + list(record["weight_sets"].items())
    head = ["Bodies", "Measures", "Weights", "Six-lumbar, t13"] + \
           ["%s: exact / right at 0.99" % k.replace("_", "-") for k in CH.TYPES]
    out = ["| " + " | ".join(head) + " |", "|---:|---|---|---|" + "---:|" * len(CH.TYPES)]
    for B in bodies:
        for sub in SUBSETS[::-1]:
            for name, w in sets:
                rs = [stated[k, B, sub] if name == "stated" else other[name, k, B, sub] for k in CH.TYPES]
                cells = ["%s (%s) / %s" % (pct(r["exact"]), pct(r["exact_se"]), pct(r["precision"], 2)) for r in rs]
                out.append("| %d | %s | %s | %g, %g | %s |" % (B, sub, name, w["six_lumbar"], w["t13"], " | ".join(cells)))
    return "\n".join(out) + "\n"


def axis_table(record: dict, main: dict, bodies: int = 5, subset: str = "all") -> str:
    """The data axis at one width and measure set: each type's share named exactly by the chain,
    with both SEs and the difference from the table as printed on the same fields, and the
    chain's precision at 0.99 over the three types, against the consecutive rule's typical share."""
    printed = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in main["rows"]}
    rows = {(r["people"], r["rule"], r["type"], r["bodies"], r["subset"], r["arm"]): r for r in record["rows"]}
    head = ["People", "Rule", "Tables"] + ["Chain, %s" % k.replace("_", "-") for k in CH.TYPES] + \
           ["Chain, right at 0.99 (typical / six-lumbar / t13)", "Consecutive, typical"]
    out = ["| " + " | ".join(head) + " |", "|---:|---|---:|" + "---:|" * (len(head) - 3)]

    def cell(r, ref=None, two=True):
        se = "%s / %s" % (pct(r["exact_se"]), pct(r.get("exact_se_tables", float("nan")))) if two else pct(r["exact_se"])
        diff = "" if ref is None else ", %+.1f" % (100 * (r["exact"] - ref["exact"]))
        return "%s (%s)%s" % (pct(r["exact"]), se, diff)

    p = [printed[k, bodies, subset, "chain"] for k in CH.TYPES]
    out.append("| as printed | - | 1 | " + " | ".join(cell(r, two=False) for r in p) + " | " +
               " / ".join(pct(r["precision"], 2) for r in p) + " | " +
               cell(printed["typical", bodies, subset, "consecutive"], two=False) + " |")
    worlds = {int(k): v for k, v in record["worlds"].items()}
    for people in sorted(worlds):
        for rule in RULES:
            c = [rows[people, rule, k, bodies, subset, "chain"] for k in CH.TYPES]
            cells = [cell(r, ref) for r, ref in zip(c, p)]
            prec = " / ".join(pct(r["precision"], 2) for r in c)
            cons = cell(rows[people, rule, "typical", bodies, subset, "consecutive"], printed["typical", bodies, subset, "consecutive"])
            out.append("| {:,} | {} | {} | {} | {} | {} |".format(people, rule, worlds[people], " | ".join(cells), prec, cons))
    return "\n".join(out) + "\n"


def speed_table(record: dict) -> str:
    """Milliseconds to name one field, alone (median / largest) and in a batch, all 32 and seven."""
    key = {(r["engine"], r["arm"], r["subset"], r["bodies"]): r for r in record["rows"]}
    head = ["Bodies", "Paths, chain"] + ["%s, %s" % (a, k) for a in CHAIN_ARMS for k in ("all 32", "seven")] + \
           ["chain, all 32, path_logev"]
    out = ["| " + " | ".join(head) + " |", "|---:|---:|" + "---:|" * (len(head) - 2)]
    for B in record["widths"]:
        cells = []
        for a in CHAIN_ARMS:
            for k in ("all", "seven"):
                r = key["prepared", a, k, B]
                cells.append("%s / %s; %s" % (_ms(r["median_ms"]), _ms(r["max_ms"]), _ms(r["batch_ms"])))
        r = key["path_logev", "chain", "all", B]
        cells.append("%s / %s; %s" % (_ms(r["median_ms"]), _ms(r["max_ms"]), _ms(r["batch_ms"])))
        out.append("| %d | %s | %s |" % (B, "{:,}".format(key["prepared", "chain", "all", B]["paths"]), " | ".join(cells)))
    return "\n".join(out) + "\n"


def _ms(v: float) -> str:
    return "%.3g" % v if v < 100 else "{:,.0f}".format(v)


def load(which: str) -> dict:
    with open(RECORDS[which]) as f:
        return json.load(f)


def tables() -> Dict[str, str]:
    """Every README table of the chain, by its marker."""
    main = load("main")
    out = {"chain:main": main_table(main), "chain:claims": claims_table(main), "chain:weights": weights_table(main)}
    if os.path.exists(RECORDS["axis"]):
        ax = load("axis")
        out["chain:axis-5"] = axis_table(ax, main, 5, "all")
        out["chain:axis-5-seven"] = axis_table(ax, main, 5, "seven")
    if os.path.exists(RECORDS["speed"]):
        out["chain:speed"] = speed_table(load("speed"))
    return out


def readme_blocks(text: str) -> Dict[str, List[str]]:
    """The tables between <!-- name --> and <!-- /name --> in the README, by name, each as often
    as it is written."""
    out: Dict[str, List[str]] = {}
    for m in re.finditer(r"<!-- (chain:[\w-]+) -->\n(.*?)<!-- /\1 -->", text, re.S):
        out.setdefault(m.group(1), []).append(m.group(2))
    return out


def check(readme: str = README) -> List[str]:
    """What differs between the README's chain tables and the records': an empty list when none.
    A block may carry notes below its table, after a blank line or prose; the table itself must be
    the record's, with no row of its own after the record's last."""
    with open(readme) as f:
        have = readme_blocks(f.read())
    want = tables()
    out = []
    for name, table in want.items():
        if name not in have:
            out.append("the README has no block %s" % name)
        elif len(have[name]) > 1:
            out.append("the README writes %s more than once" % name)
        elif not have[name][0].startswith(table):
            out.append("the README's %s is not the record's" % name)
        elif have[name][0][len(table):].startswith("|"):
            out.append("the README's %s has rows after the record's table" % name)
    for name in have:
        if name not in want:
            out.append("the README's %s has no record" % name)
    return out


def write(record: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(record, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m schwingcheck.chain_study")
    ap.add_argument("what", choices=("run", "axis", "speed", "table", "check"))
    ap.add_argument("--columns", type=int, default=100)
    ap.add_argument("--processes", type=int, default=PROCESSES)
    ap.add_argument("--out", default=None, help="where run, axis or speed writes its record")
    ap.add_argument("--table", choices=("main", "claims", "weights", "axis", "speed"), default="main")
    a = ap.parse_args(argv)
    if a.what == "run":
        write(run(a.columns), a.out or RECORDS["main"])
    elif a.what == "axis":
        write(axis(a.columns, processes=a.processes), a.out or RECORDS["axis"])
    elif a.what == "speed":
        write(speed(a.columns), a.out or RECORDS["speed"])
    elif a.what == "table":
        main_rec = load("main")
        if a.table == "main":
            print(main_table(main_rec), end="")
        elif a.table == "claims":
            print(claims_table(main_rec), end="")
        elif a.table == "weights":
            print(weights_table(main_rec), end="")
        elif a.table == "axis":
            print(axis_table(load("axis"), main_rec), end="")
        else:
            print(speed_table(load("speed")), end="")
    else:
        problems = check()
        for p in problems:
            print(p)
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
