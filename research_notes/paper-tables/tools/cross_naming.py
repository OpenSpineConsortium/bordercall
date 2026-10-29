"""Name fields drawn from each paper's own tables with the rule built on Panjabi's, and with a rule
that widens Panjabi's table by how much the papers disagree, and measure how much the papers
disagree, measure by measure and level by level.

Usage (from the repository's root, in the environment schwingcheck runs in):
    python research_notes/paper-tables/tools/cross_naming.py <series.csv> <out.json> [--fields 100] [--seed 2026]
        [--processes 4] [--cohorts <folder of the papers' cohorts files>] [--leave-out key,key]

Every paper is taken to measure other people by another technique than every other paper, as the
owner asked on 28 October 2026, unless its text says it shares subjects or a method; so each
paper is its own source, and a paper's several cohorts and subgroups are its own series. What a
series gives is a mean and a population SD per level, so the fields drawn from it are the
generator's (columns.draw_columns' formula: the patient's size, the patient's offset in each
measure, the level's own draw and the measurement error, with schwingcheck's settings) with the
series' means and SDs in place of Panjabi's. That is an assumption, stated: a paper's table does
not say how its measures correlate within a person. Where a paper's text says its values pool
another source's subjects, as a meta-analysis that took in Panjabi's spines does (--cohorts reads
it from the cohorts files' shared entries), that paper is kept out of every pool that holds the
source it took in, so no spine is counted twice, and its rows carry the sources it holds. A cohort
whose cohorts entry names a species other than human (the pig spines two papers measured beside
people's) is left out of everything, since Panjabi's rule names people's vertebrae. A measure named
by --leave-out is left out of everything too: the end-plate inclinations, whose L1 to L5 row in
Panjabi's lumbar paper reprints his cervical C3 to C7 row (research_notes/panjabi-endplate-inclination.md).

Three things are measured.

- Disagreement. For each measure and level, every source's mean against Panjabi's: in Panjabi's
  SDs, and in levels, the difference divided by how much Panjabi's mean changes from one level to
  the next there; and, across the sources, the between-source SD (tau) of a DerSimonian-Laird
  random-effects pool, with I-squared.
- Transport. Fields drawn from a source's series at every place it covers are named by
  Panjabi's rule on the measures that series has, and the same count of fields drawn from
  Panjabi's own table at the same places, on the same measures, are named by the same rule: the
  difference between the two is what moving from Panjabi's specimens and technique to that
  paper's costs, place for place.
- A widened rule. The same fields are named by a rule whose table is the random-effects pool of
  every source but the series' own paper, its SD widened by the between-source SD (the
  leave-one-paper-out rule); whether its answers at 0.99 are right 99% of the time is the test.

Only measures whose definition the mapping calls the same as Panjabi's or close to it enter the
naming; the disagreement is measured for those that differ too, and says so.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from typing import Dict, List, Sequence, Tuple

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from schwingcheck import rule as R  # noqa: E402

WIDTHS = (1, 3, 5)
CLAIM = 0.99
RHO, SCALE_SD = R.SYNTH["rho"], R.SYNTH["scale_sd"]
FLOOR = 0.5
SAME = ("same", "close")
PANJABI = "panjabi"


def read_series(path: str) -> List[dict]:
    rows = list(csv.DictReader(open(path, newline="")))
    for r in rows:
        r["mean"] = float(r["mean"])
        r["sd"] = float(r["sd"]) if r["sd"] else None
        r["n"] = float(r["n"]) if r["n"] else None
    return rows


def panjabi_table():
    pool = MS.pool()
    mu, sd = MS.arrays(pool)
    base = [m.key.split(":")[0] for m in pool]
    return pool, base, mu, sd, MS.errors(pool), MS.powers(pool)


def series_id(r: dict) -> Tuple[str, ...]:
    return (r["paper"], r["cohort"], r["technique"], r["sex"], r["group"])


def tables_of(series: Sequence[dict], base: Sequence[str], allowed=SAME) -> Dict[tuple, Dict[str, Dict[str, tuple]]]:
    """{series id: {key: {level: (mean, sd, n)}}} for this paper's own subjects, on Panjabi's
    measures, at the rule's levels, where the definition is allowed and an SD is known."""
    out: Dict[tuple, Dict[str, Dict[str, tuple]]] = {}
    for r in series:
        if (r["source_of_values"] != "this paper" or r["key"] not in base or r["level"] not in LEVELS
                or r["sd"] is None or r["sd"] <= 0 or r["vs_panjabi"] not in allowed):
            continue
        out.setdefault(series_id(r), {}).setdefault(r["key"], {})[r["level"]] = (r["mean"], r["sd"], r["n"])
    return out


def run_of(table: Dict[str, Dict[str, tuple]], least: int) -> Tuple[List[str], List[int]]:
    """The measures and the longest run of consecutive levels they all cover: measures are added,
    those covering most levels first, while the run they share stays at least `least` long."""
    keys = sorted(table, key=lambda k: (-len(table[k]), k))
    chosen, run = [], []
    for k in keys:
        trial = chosen + [k]
        common = [i for i, l in enumerate(LEVELS) if all(l in table[t] for t in trial)]
        best = longest_run(common)
        if len(best) >= least:
            chosen, run = trial, best
    return chosen, run


def longest_run(idx: Sequence[int]) -> List[int]:
    best, cur = [], []
    for i in idx:
        cur = cur + [i] if cur and i == cur[-1] + 1 else [i]
        if len(cur) > len(best):
            best = cur
    return best


def draw(mu: np.ndarray, sd: np.ndarray, noise: np.ndarray, power: np.ndarray, n: int, rng) -> np.ndarray:
    """n columns of the generator's formula over the levels of mu (measures, levels):
    (n, levels, measures), floored at 0.5 where a measure scales with the size."""
    M, L = mu.shape
    s = np.exp(rng.normal(0.0, SCALE_SD, size=n))
    g = s[:, None] ** power[None, :]
    z = rng.normal(size=(n, M, 1))
    e = rng.normal(size=(n, M, L))
    v = g[:, :, None] * (mu[None] + sd[None] * (RHO * z + math.sqrt(1 - RHO * RHO) * e)) + noise[None, :, None] * rng.normal(size=(n, M, L))
    v = np.where((power > 0)[None, :, None], np.maximum(v, FLOOR), v)
    return np.transpose(v, (0, 2, 1))


def fields_at(cols: np.ndarray, start: int, width: int) -> np.ndarray:
    """(columns, levels, measures) columns over a run; the fields starting at body `start` of the
    run: (fields, measures, bodies), as rule.name takes them."""
    return np.transpose(cols[:, start:start + width, :], (0, 2, 1))


def scores(post: np.ndarray, truth: int) -> dict:
    said = post.argmax(1)
    top = post.max(1)
    named = top >= CLAIM
    return {"fields": int(len(post)), "exact": int((said == truth).sum()), "within_one": int((np.abs(said - truth) <= 1).sum()),
            "named": int(named.sum()), "named_right": int((named & (said == truth)).sum())}


def add(total: dict, part: dict) -> None:
    for k, v in part.items():
        total[k] = total.get(k, 0) + v


def namer(mu: np.ndarray, sd: np.ndarray, noise: np.ndarray, power: np.ndarray, width: int):
    nodes = R.trapezoid(SCALE_SD)
    offsets = np.arange(width)

    def name(X):
        return R.name(X, offsets, mu, sd, R.SYNTH, noise=noise, power=power, nodes=nodes)["all"]
    return name


# ---- the disagreement --------------------------------------------------------------------

def dersimonian_laird(means: np.ndarray, var: np.ndarray) -> Tuple[float, float, float]:
    """The random-effects mean, the between-source SD and I-squared of k means with their
    variances; with one source, its mean and no spread."""
    k = len(means)
    if k == 1:
        return float(means[0]), 0.0, 0.0
    w = 1.0 / var
    fixed = float((w * means).sum() / w.sum())
    q = float((w * (means - fixed) ** 2).sum())
    c = float(w.sum() - (w ** 2).sum() / w.sum())
    tau2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    wr = 1.0 / (var + tau2)
    pooled = float((wr * means).sum() / wr.sum())
    i2 = max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0
    return pooled, math.sqrt(tau2), i2


def stated(entry: dict) -> bool:
    """Whether a shared entry rests on the paper's own words: the readers open an entry they
    inferred, or one the paper does not state, with those words."""
    opening = entry.get("evidence", "").strip().lower()
    return not (opening.startswith("inference") or opening.startswith("not stated")
                or "inference" in entry.get("what", "").lower())


def read_contains(cohorts_dir: str) -> Dict[str, List[str]]:
    """{paper: the other sources whose subjects its values hold}, from the papers' own words: a
    cohorts file's shared entry that says the data were pooled or the subjects are the same, and
    names a paper of the set or Panjabi. An entry the reader marked as inference does not count,
    since the owner's rule takes papers as independent unless their text says otherwise."""
    if not cohorts_dir:
        return {}
    papers = {name.split(".")[0] for name in os.listdir(cohorts_dir) if name.endswith(".cohorts.json")}
    out: Dict[str, List[str]] = {}
    for paper in sorted(papers):
        record = json.load(open(os.path.join(cohorts_dir, paper + ".cohorts.json")))
        for entry in record.get("shared", []):
            if entry.get("what") not in ("data pooled", "subjects") or not stated(entry):
                continue
            named = set(re.findall(r"\b([a-z]+[0-9]{4}[a-z]?)\b", entry.get("with", "")))
            if "panjabi" in entry.get("with", "").lower():
                named.add(PANJABI)
            named = {n if n in papers else PANJABI for n in named if n in papers or n.startswith(PANJABI)} - {paper}
            if named:
                out[paper] = sorted(set(out.get(paper, [])) | named)
    return out


def read_not_human(cohorts_dir: str) -> List[Tuple[str, str]]:
    """(paper, cohort) for every cohort whose cohorts entry gives a species other than human."""
    if not cohorts_dir:
        return []
    out = []
    for name in sorted(os.listdir(cohorts_dir)):
        if not name.endswith(".cohorts.json"):
            continue
        record = json.load(open(os.path.join(cohorts_dir, name)))
        for c in record.get("cohorts", []):
            if c.get("species", "human").strip().lower() != "human":
                out.append((record.get("paper", name.split(".")[0]), c["cohort"]))
    return out


def one_per_paper(rows: Sequence[dict], contains: Dict[str, List[str]] = None) -> List[dict]:
    """One series per paper at a measure and level, its largest count, so that no subjects are
    counted twice in the pool; the papers are taken as independent of each other (the owner's
    rule) and Panjabi's four as one source, except where a paper's text says its values hold
    another source's subjects (a meta-analysis that pooled Panjabi's spines): such a paper is
    left out of every pool that holds Panjabi or the source it took in."""
    contains = contains or {}
    best: Dict[str, dict] = {}
    for r in rows:
        # A printed SD (or SEM) of zero is a small spread rounded away; it would give the source an
        # infinite weight and the pool no mean (Tan 2004 prints an SEM of 0.0 for EPWu at C6).
        if r["sd"] is None or r["sd"] <= 0 or not r["n"] or r["n"] < 2:
            continue
        cur = best.get(r["paper"])
        if cur is None or r["n"] > cur["n"]:
            best[r["paper"]] = r
    present = set(best) | {PANJABI}
    return [r for p, r in best.items() if not (set(contains.get(p, [])) & (present - {p}))]


def disagreement(series: Sequence[dict], base, mu, sd, contains: Dict[str, List[str]] = None) -> List[dict]:
    """Per measure and level: Panjabi's mean and SD, every source's difference from it in his SDs
    and in levels, and the random-effects pool of the sources with Panjabi among them."""
    out = []
    by = {}
    for r in series:
        if r["source_of_values"] == "this paper" and r["key"] in base and r["level"] in LEVELS:
            by.setdefault((r["key"], r["level"]), []).append(r)
    for (key, level), rows in sorted(by.items()):
        m, li = base.index(key), LEVELS.index(level)
        step = level_step(mu[m], li)
        sources = []
        for r in rows:
            d_sd = (r["mean"] - mu[m, li]) / sd[m, li]
            d_lv = (r["mean"] - mu[m, li]) / step if step else None
            sources.append({"paper": r["paper"], "cohort": r["cohort"], "technique": r["technique"], "sex": r["sex"],
                            "group": r["group"], "mean": r["mean"], "sd": r["sd"], "n": r["n"], "vs_panjabi": r["vs_panjabi"],
                            "d_panjabi_sd": d_sd, "d_levels": d_lv,
                            "holds_subjects_of": (contains or {}).get(r["paper"], [])})
        pooled = pool_with_panjabi(one_per_paper([r for r in rows if r["vs_panjabi"] in SAME], contains), mu[m, li], sd[m, li])
        out.append({"key": key, "level": level, "panjabi_mean": float(mu[m, li]), "panjabi_sd": float(sd[m, li]),
                    "panjabi_step_per_level": step, "sources": sources, **pooled})
    return out


def level_step(row: np.ndarray, i: int) -> float:
    """How much Panjabi's mean changes per level at level i: the central difference, one-sided at
    the ends."""
    if i == 0:
        return float(row[1] - row[0])
    if i == len(row) - 1:
        return float(row[-1] - row[-2])
    return float((row[i + 1] - row[i - 1]) / 2)


def pool_with_panjabi(rows: Sequence[dict], p_mean: float, p_sd: float) -> dict:
    means = np.array([p_mean] + [r["mean"] for r in rows])
    var = np.array([p_sd ** 2 / 12] + [r["sd"] ** 2 / r["n"] for r in rows])
    pooled, tau, i2 = dersimonian_laird(means, var)
    return {"pool_k": len(means), "pool_mean": pooled, "pool_tau": tau, "pool_i2": i2,
            "pool_papers": [PANJABI] + [r["paper"] for r in rows]}


# ---- the widened rule --------------------------------------------------------------------

def widened_table(series: Sequence[dict], base, mu, sd, leave_out: str, kinds: Sequence[str],
                  contains: Dict[str, List[str]] = None) -> Tuple[np.ndarray, np.ndarray, dict]:
    """Panjabi's table with each mean replaced by the random-effects pool of every paper but
    `leave_out` (Panjabi among them), and each SD widened by the between-source SD: where three
    or more sources hold a level, theirs; elsewhere the measure's median between-source spread
    over its levels, as a share of the mean for a length or an area and in degrees for an angle;
    where no level of a measure has three, Panjabi's own."""
    mu_w, sd_w = mu.copy(), sd.copy()
    by = {}
    for r in series:
        if (r["source_of_values"] == "this paper" and r["paper"] != leave_out and r["key"] in base
                and r["level"] in LEVELS and r["vs_panjabi"] in SAME):
            by.setdefault((r["key"], r["level"]), []).append(r)
    taus: Dict[str, List[float]] = {}
    fit: Dict[Tuple[str, str], Tuple[float, float, int]] = {}
    for (key, level), rows in by.items():
        m, li = base.index(key), LEVELS.index(level)
        p = pool_with_panjabi(one_per_paper(rows, contains), mu[m, li], sd[m, li])
        fit[(key, level)] = (p["pool_mean"], p["pool_tau"], p["pool_k"])
        if p["pool_k"] >= 3:
            spread = p["pool_tau"] if kinds[m] == "angle" else p["pool_tau"] / abs(p["pool_mean"])
            taus.setdefault(key, []).append(spread)
    typical = {k: float(np.median(v)) for k, v in taus.items()}
    for m, key in enumerate(base):
        for li, level in enumerate(LEVELS):
            mean, tau, k = fit.get((key, level), (mu[m, li], 0.0, 1))
            if k < 3:
                spread = typical.get(key, 0.0)
                tau = spread if kinds[m] == "angle" else spread * abs(mean)
            mu_w[m, li] = mean
            sd_w[m, li] = math.sqrt(sd[m, li] ** 2 + tau ** 2)
    return mu_w, sd_w, {"between_source_spread": typical}


# ---- the transport -----------------------------------------------------------------------

def transport(series, pool, base, mu, sd, noise, power, n_fields: int, seed: int, processes: int = 1,
              log=print, contains: Dict[str, List[str]] = None) -> List[dict]:
    """Every series' transport rows, the series spread over `processes` worker processes; the
    draws of each series come from a stream of its own (the seed, its place in the sorted list
    and the width), so the record does not depend on how many processes ran it."""
    tables = sorted(tables_of(series, base).items())
    jobs = [(t_i, sid, table, series, n_fields, seed, contains) for t_i, (sid, table) in enumerate(tables)]
    if processes > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(processes) as workers:
            parts = workers.map(one_source, jobs, chunksize=1)
    else:
        parts = [one_source(j) for j in jobs]
    out = [row for part in parts for row in part]
    for r in out:
        log("%s %s %s %s %s, %d bodies, %d measures over %s to %s: exact %.1f%% against %.1f%% on Panjabi's"
            % (r["paper"], r["cohort"], r["technique"], r["sex"], r["group"], r["width"], len(r["measures"]),
               r["levels"][0], r["levels"][-1], 100 * r["source"]["exact"] / r["source"]["fields"],
               100 * r["panjabi"]["exact"] / r["panjabi"]["fields"]))
    return out


def one_source(job) -> List[dict]:
    t_i, sid, table, series, n_fields, seed, contains = job
    pool, base, mu, sd, noise, power = panjabi_table()
    kinds = [m.kind for m in pool]
    widened = widened_table(series, base, mu, sd, sid[0], kinds, contains)
    out = []
    for width in WIDTHS:
        keys, run = run_of(table, width)
        if not keys:
            continue
        idx = [base.index(k) for k in keys]
        mu_b = np.array([[table[k][LEVELS[i]][0] for i in run] for k in keys])
        sd_b = np.array([[table[k][LEVELS[i]][1] for i in run] for k in keys])
        rng = np.random.default_rng([seed, t_i, width])
        from_source = draw(mu_b, sd_b, noise[idx], power[idx], n_fields, rng)
        from_panjabi = draw(mu[idx][:, run], sd[idx][:, run], noise[idx], power[idx], n_fields, rng)
        rule_p = namer(mu[idx], sd[idx], noise[idx], power[idx], width)
        rule_w = namer(widened[0][idx], widened[1][idx], noise[idx], power[idx], width)
        res = {"source": {}, "panjabi": {}, "widened_source": {}}
        for start in range(len(run) - width + 1):
            truth = run[start]
            Xs, Xp = fields_at(from_source, start, width), fields_at(from_panjabi, start, width)
            add(res["source"], scores(rule_p(Xs), truth))
            add(res["panjabi"], scores(rule_p(Xp), truth))
            add(res["widened_source"], scores(rule_w(Xs), truth))
        out.append({"paper": sid[0], "cohort": sid[1], "technique": sid[2], "sex": sid[3], "group": sid[4],
                    "width": width, "measures": keys, "levels": [LEVELS[i] for i in run],
                    "places": len(run) - width + 1, "fields_per_place": n_fields,
                    "holds_subjects_of": (contains or {}).get(sid[0], []),
                    "widened_spread": {k: widened[2]["between_source_spread"].get(k) for k in keys}, **res})
    return out


def not_a_number(x, where: str = "") -> List[str]:
    """Every place in the record that holds NaN or an infinity, so a bad pool stops the run instead
    of reaching the page."""
    if isinstance(x, float):
        return [where] if math.isnan(x) or math.isinf(x) else []
    if isinstance(x, dict):
        return [p for k, v in x.items() for p in not_a_number(v, where + "/" + str(k))]
    if isinstance(x, list):
        return [p for i, v in enumerate(x) for p in not_a_number(v, where + "/" + str(i))]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("series")
    ap.add_argument("out")
    ap.add_argument("--fields", type=int, default=100, help="fields drawn per place, per source and per width")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--processes", type=int, default=1)
    ap.add_argument("--cohorts", default="", help="the folder of <paper>.cohorts.json files, for the subjects papers share")
    ap.add_argument("--leave-out", default="", help="measures, comma-separated, that no series is compared or named on")
    a = ap.parse_args(argv)
    not_human = read_not_human(a.cohorts)
    animals = set(not_human)
    left_out = sorted(k for k in a.leave_out.split(",") if k)
    series = [r for r in read_series(a.series) if (r["paper"], r["cohort"]) not in animals and r["key"] not in left_out]
    contains = read_contains(a.cohorts)
    pool, base, mu, sd, noise, power = panjabi_table()
    record = {"command": "python research_notes/paper-tables/tools/cross_naming.py %s %s --fields %d --seed %d%s%s"
                         % (a.series, a.out, a.fields, a.seed, " --cohorts %s" % a.cohorts if a.cohorts else "",
                            " --leave-out %s" % ",".join(left_out) if left_out else ""),
              "settings": {"rho": RHO, "scale_sd": SCALE_SD, "claim": CLAIM, "widths": list(WIDTHS), "floor": FLOOR,
                           "definitions_named": list(SAME)},
              "panjabi_measures": base, "levels": LEVELS,
              "holds_subjects_of": contains,
              "left_out_not_human": [list(pc) for pc in not_human],
              "left_out_measures": left_out,
              "disagreement": disagreement(series, base, mu, sd, contains),
              "transport": transport(series, pool, base, mu, sd, noise, power, a.fields, a.seed, a.processes,
                                     contains=contains)}
    bad = not_a_number(record)
    if bad:
        raise ValueError("the record holds no number at %d places, the first %s" % (len(bad), ", ".join(bad[:5])))
    with open(a.out, "w") as f:
        json.dump(record, f, indent=1, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
