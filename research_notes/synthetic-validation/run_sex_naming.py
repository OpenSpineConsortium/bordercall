"""Knowing the patient's sex while naming a short field: the records of synthval/sex_naming.py.

    python3 -I run_sex_naming.py --out records/sex_naming            # minutes on 4 CPUs
    python3 -I run_sex_naming.py --out /tmp/x --quick                 # the same path on few persons

Run from this folder with the Python that holds bordercall's pinned packages, after run_strata.py's
snapshot check passes, run_covariates.py has written records/covariates (the sex contrasts and the
pooled effects this reads, held to the snapshot's own before anything is drawn) and run_select.py
has written records/select (each paper's inner choice, which the run makes again and holds to the
record where the paper is one of the selection's). The contrasts read the full snapshot's rows with
the sexes' snapshot's beside them (data/series_sexes.csv, papers_table.load_rows_sexes), the
selection's cells the full snapshot's alone. Writes synthetic.csv (reading a: every table of
the selection, every arm of the sex shift, every width, rules A, A' and B on the same persons, each
difference paired), held_out.csv (reading b: every paper printing both sexes that can be scored,
rules A and B as the selection builds them for it, at its inner temperature, at T = 2 and at T = 1,
and the ceilings, each paper flagged where its persons' SD is borrowed from the rule's own pool,
and its temperature named a fallback where it has no inner fold), summary.csv (each reading over
its populations, the held-out headline over the papers whose persons' SDs are printed, with the
pool over every paper beside it; each difference with its SE between populations, the headline's,
and over persons) and sex_naming.json (the
coverage of reading b, each paper's inner choice, the level profile, the g read from the records,
the sizes, the seeds, the commit, the snapshot's digest and the code).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

import numpy as np  # noqa: E402

from synthval import covariates as CV  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import select as SEL  # noqa: E402
from synthval import sex_naming as SN  # noqa: E402
from synthval import strata as ST  # noqa: E402
from run import code_digests, log, write_csv, write_json  # noqa: E402

WIDTHS = (1, 2, 3)
COVARIATES = os.path.join(HERE, "records", "covariates")
CHOICES = os.path.join(HERE, "records", "select", "choices.csv")
SYNTHETIC_BY = ("reading", "arm", "d", "width", "rule", "against")
HELD_OUT_BY = ("width", "rule", "against")


def records_match(recorded, effects, fresh) -> list:
    """What differs between the covariate records and the snapshot's own contrasts and effects."""
    problems = []
    if len(fresh) != len(recorded):
        problems.append("contrasts.csv holds %d contrasts, the snapshot gives %d" % (len(recorded), len(fresh)))
    elif any(SN.contrast_differs(r, c) for r, c in zip(recorded, fresh)):
        problems.append("contrasts.csv differs from the snapshot's contrasts")
    for e in CV.effects(fresh, "sex"):
        if abs(effects.get(e["measure"], float("nan")) - e["mean"]) > 1e-9:
            problems.append("effects.csv's sex effect on %s differs from the snapshot's" % e["measure"])
    return problems


def choices_match(choices, widths, inner_columns) -> list:
    """What differs between the inner temperatures made here and records/select/choices.csv's, for
    every paper scored on the measures the selection holds it out on, where the run reads select.py's
    widths and columns (a paper scored on measures it prints only apart has a choice of its own)."""
    if tuple(widths) != WIDTHS or inner_columns != SEL.INNER_COLUMNS or not os.path.exists(CHOICES):
        return []
    with open(CHOICES, encoding="utf-8") as fh:
        record = {r["paper"]: r for r in csv.DictReader(fh)}
    problems = []
    for ch in choices:
        if ch["population"] != SN.SELECTION_POPULATION or ch["paper"] not in record:
            continue
        for w in widths:
            if abs(float(record[ch["paper"]]["t_%d" % w]) - ch["t"][w]) > 1e-12:
                problems.append("%s's inner T at width %d is %g here and %s in choices.csv" % (
                    ch["paper"], w, ch["t"][w], record[ch["paper"]]["t_%d" % w]))
    return problems


HEADLINE = "the headline: pooled over the papers whose persons' SDs are printed"
EVERY_PAPER = "pooled over every paper scored, those whose persons' SD is borrowed among them"
SELECTION = "pooled over the selection's populations whose persons' SDs are printed"


def held_out_summary(rows) -> list:
    """Reading (b) per paper; the headline, pooled over the papers whose persons' SDs are printed
    (a paper whose persons' SD is the rule's own pool's scores what the synthetic reading scores);
    pooled over every paper scored, those among them; and pooled over the headline's papers scored on
    the measures the selection names their populations with."""
    out = []
    for paper in sorted({r["paper"] for r in rows}):
        out += [dict(r, paper=paper) for r in SN.summarise([r for r in rows if r["paper"] == paper], HELD_OUT_BY, "held out")]
    printed = [r for r in rows if not r["synthetic_persons"]]
    out += [dict(r, paper=HEADLINE) for r in SN.summarise(printed, HELD_OUT_BY, "held out")]
    out += [dict(r, paper=EVERY_PAPER) for r in SN.summarise(rows, HELD_OUT_BY, "held out")]
    mine = [r for r in printed if r["population"] == SN.SELECTION_POPULATION]
    out += [dict(r, paper=SELECTION) for r in SN.summarise(mine, HELD_OUT_BY, "held out")]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--persons", type=int, default=SN.PERSONS)
    ap.add_argument("--resamples", type=int, default=SN.RESAMPLES)
    ap.add_argument("--inner-columns", type=int, default=SEL.INNER_COLUMNS)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    if args.quick:
        args.persons, args.resamples, args.inner_columns = 60, 20, 30
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    started = time.time()
    code = code_digests()
    problems = PT.check_snapshot_all() + PT.check_snapshot_sexes()
    rows, voc = PT.load_rows_all(), PT.load_vocabulary()
    with_sexes = rows + PT.load_rows_sexes()
    recorded = SN.load_contrasts(os.path.join(COVARIATES, "contrasts.csv"))
    effects = SN.load_effects(os.path.join(COVARIATES, "effects.csv"))
    contrasts = CV.sex_contrasts(with_sexes, voc)
    problems += records_match(recorded, effects, contrasts)
    if problems:
        raise SystemExit("; ".join(problems))
    series, _ = PT.select_all(rows)
    cells = ST.strata_of(series)
    ST.set_between(cells)
    cells_g = SN.placed(contrasts)
    profile, profile_from = SN.level_profile(cells_g)
    g_cell = SN.cell_effects(cells_g)

    held, choices = SN.held_out(cells, with_sexes, contrasts, voc, WIDTHS, persons=args.persons, resamples=args.resamples,
                                inner_columns=args.inner_columns, log=log)
    problems = choices_match(choices, WIDTHS, args.inner_columns)
    if problems:
        raise SystemExit("; ".join(problems))
    synthetic = SN.synthetic(cells, voc, profile, effects, g_cell, WIDTHS, persons=args.persons, resamples=args.resamples, log=log)
    cover = SN.coverage(cells, contrasts, voc)
    summary = (SN.summarise([r for r in synthetic if r["reading"] == "every measure the selection uses"], SYNTHETIC_BY,
                            "synthetic, every measure the selection uses")
               + SN.summarise([r for r in synthetic if r["reading"] == "each held-out paper's measures"], SYNTHETIC_BY,
                              "synthetic, each held-out paper's measures")
               + held_out_summary(held))
    write_csv(out, "synthetic.csv", synthetic)
    write_csv(out, "held_out.csv", held)
    write_csv(out, "summary.csv", summary)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    with open(PT.SOURCE_SEXES, encoding="utf-8") as fh:
        sexes = json.load(fh)
    tables = SN.selection_tables(cells, voc)
    write_json(out, "sex_naming.json", {
        "command": "python3 -I run_sex_naming.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "records_read": ["records/covariates/contrasts.csv", "records/covariates/effects.csv", "records/select/choices.csv"],
        "sexes_snapshot": {"path": os.path.relpath(PT.SEXES_APART, HERE), "sha256": sexes["snapshot_sha256"],
                           "rows": sexes["rows"], "commit": sexes["commit"]},
        "min_per_sex": CV.MIN_PER_SEX,
        "headline": {"held_out": HEADLINE, "beside_it": [EVERY_PAPER, SELECTION], "se": SN.SE_BETWEEN,
                     "papers_in_headline": sorted({r["paper"] for r in held if not r["synthetic_persons"]}),
                     "papers_with_borrowed_sd": sorted({r["paper"] for r in held if r["synthetic_persons"]}),
                     "papers_with_fallback_t": sorted({r["paper"] for r in held if r["inner_t_from"] == SN.FALLBACK_T})},
        "sizes": {"persons": args.persons, "men": args.persons // 2, "women": args.persons - args.persons // 2,
                  "resamples": args.resamples, "inner_columns": args.inner_columns, "widths": list(WIDTHS),
                  "synthetic_tables": len(tables), "held_out_papers": sorted({r["paper"] for r in held})},
        "seeds": {"synthetic": SN.SEED_SYNTHETIC, "held_out": SN.SEED_HELD_OUT, "streams": list(SN.STREAMS),
                  "rule": "numpy SeedSequence(synthetic) spawned once per table of the synthetic reading (every measure "
                          "first, then the held-out papers by name) and SeedSequence(held_out) once per paper printing both "
                          "sexes (by name), each unit spawned once per stream: its men, its women, its bootstrap and its "
                          "inner choice; every arm of one table reads the same men's and women's streams; a paper that is "
                          "one of the selection's papers takes its inner choice on select.py's own seed, strata.SEED_COLUMNS "
                          "+ its index among them, and any other on its inner stream"},
        "d_grid": list(SN.D_GRID), "fixed_temperature": SN.FIXED_T, "claim": SN.CLAIM,
        "inner_choices": [dict(ch, t={str(w): t for w, t in ch["t"].items()}) for ch in choices],
        "level_profile": profile, "level_profile_by_paper": profile_from,
        "g_per_measure": effects, "g_per_cell": {"%s at %s" % k: v for k, v in sorted(g_cell.items())},
        "tables": [{"reading": rd, "paper_held_out": p, "measures": t.keys} for rd, p, t in tables],
        "coverage": cover,
        "half_and_half": "every population is half men and half women, so that each weighs the sexes alike, as the synthetic "
                         "reading's split does (a table split by sex keeps its mean and SD only for half men and half women); "
                         "each held-out paper's own counts by sex, each stratum's own (covariates.own_counts), weigh its "
                         "strata within a sex and are in held_out.csv as own_men_per_cell and own_women_per_cell",
        "summary": summary,
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "code": code})
    log("done in %d s: %d synthetic rows, %d held-out rows, papers scored held out: %s" % (
        round(time.time() - started), len(synthetic), len(held), ", ".join(sorted({r["paper"] for r in held})) or "none"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
