#!/usr/bin/env python3
"""How many cadavers a meta-analysis of published tables needs to stand in for 2,000 CT scans.

greg, 2026-10-27 23:55 UTC: "also can you do a power calculation for how many cadavers i need in
the metaanalaysis to match 2000 empirical CT scans with sufficient power".

Run it with the Python that has bordercall's packages, from a checkout that holds the pool of 32
measures (bordercall pull request 15 or later):

    python3 cadaver_power.py --bordercall PATH --out DIR [--measures seven|pool] [--columns N] [--quick]
    python3 cadaver_power.py --bordercall PATH --out DIR --part-a-only

Part A is arithmetic, for the mean of one level of one measure. A CT scan's measure carries the
person's spread sd and the CT error e that measures.py assumes and no source measures (1 mm for a
length, sqrt(pi A / 2) mm2 for an area A, 3 degrees for an angle); a cadaver's carries sd alone
(calipers taken as exact, the case kindest to the cadavers); r = 1 + e^2/sd^2. The populations the
published studies sampled and the population being named are taken as draws about one centre with
SD tau = f * sd, f being part B's spread of the studies' means about their centre
(between_studies.py). So the population named is exchangeable with those studied: it lies tau from
the centre and sqrt(2) tau from any one study (0.55 sd at f = 0.39). That is an assumption, and the
ceiling below rests on it.

- One population, no differences between studies: n cadavers match N scans when
  n = N * sd^2 / (sd^2 + e^2) = N / r.
- k studies of m cadavers each are worth r / (f^2 (1 + 1/k) + 1/(k m)) scans of the population
  named; with unequal counts n_i, r / (f^2 + 1 / sum_i 1/(f^2 + 1/n_i)). However many cadavers it
  pools, a meta-analysis lands at the centre, tau from the population named, so it is worth at most
  r / f^2 scans of that population, and it matches N scans only when f <= sqrt(r / N).
- A bias b between the caliper chord and the CT's chord, shared by every study, adds (b / sd)^2 to
  that denominator, and no number of studies averages it away: a match also needs
  b <= sqrt(r / N) * sd.
- If the population named sat at the centre instead, there would be no ceiling: k studies would be
  worth r / (f^2/k + 1/(k m)), and k >= N * f^2 / r of them would bring the error of that average
  down to the scans'. No patient comes from that average.
- N CTs pooled from k_ct other populations about the same centre carry the same term: they are
  worth r / (f^2 (1 + 1/k_ct) + r / N) scans of the population named.

Part A's figures are summaries over cells, the median with the least and the most, over all 704
level-and-measure cells of the pool, by kind, and over the 154 cells of the seven SPINEPS measures,
the only ones a CT measurer (spineps_map.py) reads.

Part B, the note's part C, asks what naming needs, which is less than a match: the exact rule
(rule.py) is built on tables of each kind and scored on the same typical synthetic columns (the
generator with its CT errors, columns.py), so differences between tables are paired.

- true: the generator's own table.
- people-P: each level's mean and SD re-estimated from P people of the population being named,
  drawn from the generator as typical columns with no size spread and no measurement error
  (draw_columns with scale_sd=0 and noise_mm=0, in tables() below); nominal, and predictive
  (the SD widened by sqrt((1 + 1/P)(P - 1)/(P - 3))).
- profile-f: a population whose level means differ from the one named by f * sd, independently at
  every level and measure, estimated from so many cadavers that no sampling error is left (the
  ceiling of any meta-analysis of that population); nominal, and predictive (SD times sqrt(1+f^2)).
- shift-f: the same, but one difference per measure shared by all its levels, the kind a taller or
  shorter population makes; it moves every candidate place nearly alike, and the rule's size
  integral takes up part of the rest.
- observed, kind, seven: the disagreement Panjabi's comparison tables show, split by
  shift_profile.py into a shift per study, measure and region and a level-by-level part, at the
  sizes DISAGREEMENTS gives. Over all ten measures, read as seen (observed-0.28, observed-0.4) and
  kindly (kind-0.28); over the five that the seven SPINEPS measures read, as seen (seven-seen) and
  kindly (seven-kind). As seen, every region's shift is drawn apart, since a table from C3 to L5
  stitches cervical studies to thoracolumbar ones; kindly, a study's thoracic and lumbar shifts
  move together as far as they are seen to. kind-0.28 takes the sampling error of 12 specimens out
  of the shift and out of the level-by-level part both, which shift_profile.py's consistent() shows
  cannot both hold, so it is kinder than any reading the tables allow; it stays in DISAGREEMENTS
  only because every reading after it draws after it, and the note does not quote it.

What is not known: tau for any measure (the published studies, once three or more report one level
of one measure, estimate it, by DerSimonian-Laird or REML); whether the population named is
exchangeable with those studied; the CT errors, which measures.py assumes; the calipers' error;
whether a caliper landmark and a CT mask measure the same chord at all (scanimport/README.md: no
training-free CT chord measure has been validated in millimetres against calipers), which adds a
bias between the two methods that no number of cadavers removes.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing
import os
import sys
import time

import numpy as np

N_SCANS = 2000
FRACTIONS = (0.05, 0.1, 0.2, 0.3, 0.5)
# The spreads between studies the note reads, to two digits. From between_studies.json's summary:
# the median over the 74 cells left once the rows the papers attribute to another definition are
# out (0.272), the median over all 86 cells (0.392), the median over the 36 cells of the five
# measures the seven SPINEPS measures read (0.499) and the pooled moment estimate over all 86,
# weighted by degrees of freedom (0.715). Then the median spread of the series' own means in
# synthetic_spine's tables, over the 28 cells with three or more series, sampling error and
# definitions kept (verify/per_cell.py, 0.87). FIVE_SPREADS are two more readings of the five:
# their median once the depth rows the papers attribute to another definition are out (0.346, 34
# cells) and their pooled moment estimate weighted by degrees of freedom (0.621).
SPREADS = (0.27, 0.39, 0.5, 0.72, 0.87)
FIVE_SPREADS = (0.35, 0.62)
CT_POOL_SPREADS = (0.27, 0.39, 0.5)
PANJABI = 12                   # Panjabi's 12 spines, the only series at 675 of the pool's 704 cells (verify/recorded_counts.py)
CT_SOURCES = (1, 3, 5, 10, 20)  # other populations a pool of CTs might be drawn from
POPULATION_SHARE = (0.02, 0.12)  # f of a CT pool's populations alone; 0.12 holds a tenth of the 0.39's variance
ERROR_SCALES = (0.5, 2.0)      # measures.py's assumed CT errors halved and doubled
PEOPLE_EXACT = 50              # the error-free people of part B's people-50 tables
# The disagreement in Panjabi's comparison tables (shift_profile.py), read three ways over all ten
# measures and two ways over the five that the seven SPINEPS measures read (EPDl, EPWl, VBHp, SCD,
# SCW): name, the shift's SD per study, measure and region, the correlation of a study's thoracic
# and lumbar shifts (None: every region drawn apart) and the level-by-level SD. "As seen" keeps the
# sampling error in the shift and takes the level-by-level part with sampling error kept or taken
# out; "kind" takes the sampling error of 12 specimens out of the shift, lets the thoracic and
# lumbar shifts move together as far as they are seen to, and takes the smaller level-by-level part.
# kind-0.28 so takes the sampling error out twice, which consistent() shows cannot hold; it is
# kept, unquoted, because every reading after it draws its tables after it.
DISAGREEMENTS = (
    ("observed-0.28", 0.56, None, 0.28),
    ("observed-0.4", 0.56, None, 0.40),
    ("kind-0.28", 0.48, 0.6, 0.28),
    ("seven-seen", 0.59, None, 0.28),
    ("seven-kind", 0.51, 0.7, 0.0),
    # The seven's measures read consistently: the sampling error of 12 specimens split between the
    # shift and the level-by-level part by r, the correlation of one measure across a person's levels
    # (shift_profile_seven.json, "consistent"), the thoracic and lumbar shifts correlated 0.7.
    ("seven-r0", 0.57, 0.7, 0.0),
    ("seven-r0.5", 0.54, 0.7, 0.19),
    ("seven-r0.8", 0.53, 0.7, 0.25),
    ("seven-r1", 0.51, 0.7, 0.28),
)
PEOPLE = {12: 8, 25: 6, 50: 6, 100: 4, 200: 3, 500: 2, 2000: 2}      # people per table: tables drawn
OFFSET_TABLES = 4
WIDTHS = (1, 3, 9)
CLAIM = 0.99
COLUMN_SEED, TABLE_SEED = 4101, 4102

_STATE = {}


def load(bordercall: str):
    sys.path.insert(0, bordercall)
    from schwingcheck import LEVELS, columns as C, measures as MS, rule as R, score as S
    return LEVELS, C, MS, R, S


def over_cells(a) -> dict:
    """The median over cells, with the least and the most."""
    return {"min": float(a.min()), "median": float(np.median(a)), "max": float(a.max())}


def part_a(MS, pool) -> dict:
    """Part A over every level of every measure of the pool, summarised over cells: by kind, and
    over the seven SPINEPS measures. The per-cell figures for the 29 cells where synthetic_spine
    records a series beside Panjabi's are verify/recorded_counts.py's and verify/worth_real.py's."""
    mu, sd = MS.arrays(pool)
    e = np.broadcast_to(MS.errors(pool)[:, None], sd.shape)
    r = 1.0 + (e / sd) ** 2                                   # (sd^2 + e^2) / sd^2
    kinds = np.array([m.kind for m in pool])
    seven = {MS.archive_key(m) for m in MS.select(MS.SPINEPS_7)}
    in_seven = np.array([MS.archive_key(m) in seven for m in pool])
    q = over_cells
    out = {"n_scans": N_SCANS, "cells": int(r.size), "spreads": list(SPREADS), "by_kind": {}}
    for kind in ("all", "length", "area", "angle", "seven"):
        sel = {"all": np.ones(len(pool), bool), "seven": in_seven}.get(kind, kinds == kind)
        rr, ss, ee = r[sel].ravel(), sd[sel].ravel(), e[sel].ravel()
        scaled = {"%g" % s: 1.0 + (s * ee / ss) ** 2 for s in ERROR_SCALES}
        out["by_kind"][kind] = {
            "measures": int(sel.sum()),
            "cells": int(rr.size),
            "person_sd": q(ss),
            "ct_error": q(ee),
            "factor": q(rr),
            "factor_errors_scaled": {k: q(v) for k, v in scaled.items()},
            "error_over_sd": q(np.sqrt(rr - 1.0)),
            "cadavers_to_match_one_population": q(N_SCANS / rr),
            "cadavers_to_match_one_population_errors_scaled": {k: q(N_SCANS / v) for k, v in scaled.items()},
            "largest_f_that_matches": q(np.sqrt(rr / N_SCANS)),
            "largest_f_that_matches_errors_scaled": {k: q(np.sqrt(v / N_SCANS)) for k, v in scaled.items()},
            # In the measure's own units (mm, mm2 or degrees), so read within one kind.
            "largest_bias_that_matches": q(np.sqrt(rr / N_SCANS) * ss),
            "scans_a_meta_analysis_is_worth_at_most": {
                "%g" % f: q(rr / f ** 2) for f in FRACTIONS + SPREADS + FIVE_SPREADS},
            "scans_a_meta_analysis_is_worth_at_most_errors_scaled": {
                k: {"%g" % f: q(v / f ** 2) for f in SPREADS} for k, v in scaled.items()},
            "studies_to_match_the_average_population": {"%g" % f: q(N_SCANS * f ** 2 / rr) for f in FRACTIONS},
            # One series of 12 (k = 1, m = 12): exact at the cells where it is the only series.
            "scans_panjabi_alone_is_worth": {
                "%g" % f: q(rr / (2.0 * f * f + 1.0 / PANJABI)) for f in (0.0, 0.1, 0.2) + SPREADS + FIVE_SPREADS},
            "scans_a_ct_pool_is_worth": {
                "f %g, %d populations" % (f, k): q(rr / (f * f * (1.0 + 1.0 / k) + rr / N_SCANS))
                for f in POPULATION_SHARE + CT_POOL_SPREADS for k in CT_SOURCES},
            "largest_f_for_a_ct_pool_worth_1000": {
                "%d populations" % k: q(np.sqrt(rr * (1.0 / 1000 - 1.0 / N_SCANS) / (1.0 + 1.0 / k))) for k in CT_SOURCES},
            # CTs that match PEOPLE_EXACT error-free people: for the means P r, for the SDs 1 + (P - 1) r^2,
            # since a CT's SD estimate is s_ct^2 - e^2, whose variance is 2 (sd^2 + e^2)^2 / (N - 1).
            "cts_to_match_%d_people" % PEOPLE_EXACT: {
                "means": q(PEOPLE_EXACT * rr), "sds": q(1.0 + (PEOPLE_EXACT - 1) * rr ** 2)},
            "cts_to_match_%d_people_errors_scaled" % PEOPLE_EXACT: {
                k: {"means": q(PEOPLE_EXACT * v), "sds": q(1.0 + (PEOPLE_EXACT - 1) * v ** 2)} for k, v in scaled.items()},
        }
    return out


def tables(MS, C, LEVELS, pool, quick: bool):
    """Every table of part B: (arm, rule, draw, mu, sd, settings)."""
    mu, sd = MS.arrays(pool)
    keys = [MS.archive_key(m) for m in pool]
    rng = np.random.default_rng(TABLE_SEED)
    out = [("true", "nominal", 0, mu, sd, {})]
    people = {12: 2, 2000: 1} if quick else PEOPLE
    for P, n_tables in people.items():
        fac = math.sqrt((1.0 + 1.0 / P) * (P - 1.0) / (P - 3.0))
        for t in range(n_tables):
            spec = C.draw_columns(MS.reference(pool), ["typical"], int(rng.integers(1 << 30)), P, keys,
                                  noise_mm=0.0, scale_sd=0.0, power=MS.powers(pool))
            vals = spec.values[:, :len(LEVELS), :]
            emu, esd = vals.mean(0).T.copy(), vals.std(0, ddof=1).T.copy()
            for rule, f in (("nominal", 1.0), ("predictive", fac)):
                out.append(("people-%d" % P, rule, t, emu, esd * f, {"people": P, "sd_factor": f}))
    fractions = (0.1, 0.3) if quick else FRACTIONS
    n_off = 1 if quick else OFFSET_TABLES
    for kind in ("profile", "shift"):
        for f in fractions:
            for t in range(n_off):
                d = rng.normal(size=mu.shape) if kind == "profile" else np.repeat(rng.normal(size=(mu.shape[0], 1)), mu.shape[1], 1)
                tmu = mu + f * sd * d
                for rule, g in (("nominal", 1.0), ("predictive", math.sqrt(1.0 + f * f))):
                    out.append(("%s-%g" % (kind, f), rule, t, tmu, sd * g, {"f": f, "sd_factor": g}))
    # The disagreement Panjabi's comparison tables show, split by shift_profile.py into a shift per
    # study, measure and region and a level-by-level part. Drawn after every other arm, and each
    # reading after the ones before it, so adding one changes no other table.
    region = np.array(["CTL".index(name[0]) for name in LEVELS])
    for name, shift_sd, thoracic_lumbar, level_sd in DISAGREEMENTS:
        for t in range(n_off):
            z = rng.normal(size=(mu.shape[0], 3))
            if thoracic_lumbar is not None:
                z[:, 2] = thoracic_lumbar * z[:, 1] + math.sqrt(1.0 - thoracic_lumbar ** 2) * z[:, 2]
            tmu = mu + sd * (shift_sd * z[:, region] + level_sd * rng.normal(size=mu.shape))
            g = math.sqrt(1.0 + shift_sd ** 2 + level_sd ** 2)
            for rule, h in (("nominal", 1.0), ("predictive", g)):
                out.append((name, rule, t, tmu, sd * h,
                            {"shift": shift_sd, "thoracic_lumbar": thoracic_lumbar, "level_by_level": level_sd,
                             "sd_factor": h}))
    return out


def job(args):
    """One table at one width: per field, right or not, its top posterior."""
    from threadpoolctl import threadpool_limits
    i, n = args
    C, R, noise, power = _STATE["C"], _STATE["R"], _STATE["noise"], _STATE["power"]
    arm, rule, draw, mu, sd, settings = _STATE["tables"][i]
    offsets = np.arange(n)
    X, start, col = C.fields(_STATE["values"], offsets)
    with threadpool_limits(1):
        post = R.name(X, offsets, mu, sd, R.SYNTH, noise=noise, power=power)["all"]
    hit = post.argmax(1) == start
    return i, n, hit, post.max(1), col


def rates(hit, top, col, S) -> dict:
    said = top >= CLAIM
    inv = np.unique(col, return_inverse=True)[1]
    wrong = np.bincount(inv, weights=said & ~hit)
    answered = np.bincount(inv, weights=said)
    return {"exact": float(hit.mean()), "exact_se": S.clustered_se(hit.astype(float), col),
            "answered": float(said.mean()), "precision": float(hit[said].mean()) if said.any() else float("nan"),
            "precision_se": S.ratio_se(wrong, answered), "errors_at_claim": int(wrong.sum()),
            "n_answered": int(said.sum())}


def paired(hit, ref, col, S) -> dict:
    """The difference in the share named exactly from a reference table on the same fields, with
    its standard error clustered by column."""
    d = hit.astype(float) - ref.astype(float)
    return {"minus_ref": float(d.mean()), "minus_ref_se": S.clustered_se(d, col)}


def part_b(LEVELS, C, MS, R, S, pool, n_columns: int, processes: int, quick: bool, log=print,
           arms=None) -> dict:
    keys = [MS.archive_key(m) for m in pool]
    cols = C.draw_columns(MS.reference(pool), ["typical"], COLUMN_SEED, n_columns, keys,
                          noise_mm=MS.errors(pool), power=MS.powers(pool))
    tabs = tables(MS, C, LEVELS, pool, quick)
    if arms:
        # Every table is still drawn, so the ones kept are those of the full run.
        keep = {"true", "people-2000"} | set(arms)
        tabs = [t for t in tabs if t[0] in keep]
    _STATE.update(C=C, R=R, noise=MS.errors(pool), power=MS.powers(pool), tables=tabs, values=cols.values)
    jobs = [(i, n) for n in sorted(WIDTHS, reverse=True) for i in range(len(tabs))]
    t0 = time.time()
    res = {}
    with multiprocessing.get_context("fork").Pool(processes) as p:
        for k, (i, n, hit, top, col) in enumerate(p.imap_unordered(job, jobs)):
            res[(i, n)] = (hit, top, col)
            if (k + 1) % 25 == 0 or k + 1 == len(jobs):
                log("  %d of %d table-widths, %.0f s" % (k + 1, len(jobs), time.time() - t0))
    out = {"columns": n_columns, "measures": keys, "widths": list(WIDTHS), "arms": {}}
    for n in WIDTHS:
        ref_true = res[(0, n)][0]
        ref_2000 = [res[(i, n)][0] for i, t in enumerate(tabs) if t[0] == "people-2000" and t[1] == "nominal"]
        groups = {}
        for i, (arm, rule, draw, mu, sd, settings) in enumerate(tabs):
            groups.setdefault((arm, rule), []).append(i)
        for (arm, rule), idx in groups.items():
            rows = []
            for i in idx:
                hit, top, col = res[(i, n)]
                row = rates(hit, top, col, S)
                row.update({"vs_true": paired(hit, ref_true, col, S)})
                if ref_2000:
                    row.update({"vs_2000": paired(hit, ref_2000[0], col, S)})
                rows.append(row)
            summary = {k: float(np.mean([r[k] for r in rows])) for k in ("exact", "answered", "precision")}
            summary.update({
                "exact_table_sd": float(np.std([r["exact"] for r in rows], ddof=1)) if len(rows) > 1 else 0.0,
                "precision_table_sd": float(np.std([r["precision"] for r in rows], ddof=1)) if len(rows) > 1 else 0.0,
                "precision_worst": float(np.min([r["precision"] for r in rows])),
                "exact_se_columns": float(np.mean([r["exact_se"] for r in rows])),
                "minus_true": float(np.mean([r["vs_true"]["minus_ref"] for r in rows])),
                "minus_2000": float(np.mean([r["vs_2000"]["minus_ref"] for r in rows])) if ref_2000 else None,
                "tables": len(rows), "settings": tabs[idx[0]][5]})
            out["arms"].setdefault("%s/%s" % (arm, rule), {})[str(n)] = summary
    out["seconds"] = time.time() - t0
    return out


def show_b(b: dict) -> str:
    lines = ["%-26s %s" % ("table (rule)", "  ".join("%d bod: exact  vs2000  ans@.99 prec@.99 worst" % n for n in WIDTHS))]
    for name, by in b["arms"].items():
        cells = []
        for n in WIDTHS:
            s = by[str(n)]
            m2 = s["minus_2000"]
            cells.append("%13.1f%% %+6.1f %7.1f%% %7.2f%% %6.2f%%" % (
                100 * s["exact"], 100 * m2 if m2 is not None else float("nan"), 100 * s["answered"],
                100 * s["precision"], 100 * s["precision_worst"]))
        lines.append("%-26s %s" % (name, "  ".join(cells)))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bordercall", default=os.getcwd())
    ap.add_argument("--out", required=True)
    ap.add_argument("--measures", choices=("seven", "pool"), default="seven")
    ap.add_argument("--columns", type=int, default=600)
    ap.add_argument("--processes", type=int, default=4)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--arms", nargs="*", help="run only these arms, beside the true and 2,000-person tables")
    ap.add_argument("--part-a-only", action="store_true", help="write part_a.json and stop")
    a = ap.parse_args(argv)
    LEVELS, C, MS, R, S = load(a.bordercall)
    pool = MS.pool()
    os.makedirs(a.out, exist_ok=True)
    A = part_a(MS, pool)
    with open(os.path.join(a.out, "part_a.json"), "w") as fh:
        json.dump(A, fh, indent=1)
    print(json.dumps(A["by_kind"]["all"], indent=1))
    if a.part_a_only:
        return 0
    chosen = MS.select(MS.SPINEPS_7) if a.measures == "seven" else pool
    B = part_b(LEVELS, C, MS, R, S, chosen, 30 if a.quick else a.columns, a.processes, a.quick, arms=a.arms)
    B["command"] = " ".join(["cadaver_power.py"] + (argv if argv is not None else sys.argv[1:]))
    name = "part_b_%s%s" % (a.measures, "_" + "_".join(a.arms) if a.arms else "")
    with open(os.path.join(a.out, name + ".json"), "w") as fh:
        json.dump(B, fh, indent=1)
    text = show_b(B)
    with open(os.path.join(a.out, name + ".txt"), "w") as fh:
        fh.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
