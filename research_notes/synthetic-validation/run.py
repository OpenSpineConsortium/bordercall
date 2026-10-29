"""Write every record of this note: the validation, the state space, the curation and the power.

    python3 -I run.py --out records            # every record, about eight minutes on 4 CPUs
    python3 -I run.py --out records --quick    # small populations, fewer columns, to try the code

Run from this folder with the Python that holds bordercall's pinned packages
(requirements-schwingcheck.txt). Every number in README.md is read from these records by
figures.py and tables.py; each record carries the command, the seeds, bordercall's commit and the
snapshot's digest (RECORD.json).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

from schwingcheck import LEVELS  # noqa: E402
from schwingcheck import columns as C  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from synthval import literature as L  # noqa: E402
from synthval import naming as N  # noqa: E402
from synthval import population as PO  # noqa: E402
from synthval import power as PW  # noqa: E402
from synthval import qi as Q  # noqa: E402
from synthval import references as REF  # noqa: E402
from synthval import structure as ST  # noqa: E402
from synthval import sweep as SW  # noqa: E402
from synthval import validate as V  # noqa: E402

SEED_POPULATION = 2026
SEED_SWEEP = 11
SEED_NAMING = 4101
NAMING_WIDTHS = (1, 3, 9)
NAMING_POINTS = ("scale_sd=0.035", "scale_sd=0.1", "rho=0.25", "rho=0.9", "phi=0.6", "r_between=0.4", "error_scale=2.0",
                 "sd_mode=size_removed", "sd_scale=0.7")


def clean(x):
    """JSON-safe: NaN and infinities as None, numpy scalars as Python ones, tuples as lists."""
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not math.isfinite(float(x)) else float(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def write_json(out: str, name: str, data) -> None:
    with open(os.path.join(out, name), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(clean(data), fh, indent=1, sort_keys=True)
        fh.write("\n")


def write_csv(out: str, name: str, rows) -> None:
    rows = [clean(r) for r in rows]
    cols = []
    for r in rows:
        cols += [k for k in r if k not in cols]
    with open(os.path.join(out, name), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})


def log(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def selection_record(rows, series) -> dict:
    usable = [s for s in series if L.usable(s)]
    by_measure, by_paper, by_modality = {}, {}, {}
    for s in usable:
        by_measure[s.key] = by_measure.get(s.key, 0) + 1
        by_paper[s.paper] = by_paper.get(s.paper, 0) + 1
        by_modality[s.modality] = by_modality.get(s.modality, 0) + 1
    unusable = {}
    for s in series:
        if not L.usable(s):
            unusable[s.paper] = unusable.get(s.paper, 0) + 1
    _, why = L.select(rows)
    return {"rows": len(rows), "series": len(series), "usable": len(usable), "left_out": why,
            "usable_by_measure": by_measure, "usable_by_paper": by_paper, "usable_by_modality": by_modality,
            "unusable_by_paper": unusable, "papers": len(by_paper),
            "n_from_cohort": sum(1 for s in usable if s.n_note), "n_notes": count_of(s.n_note for s in usable if s.n_note),
            "sd_uncertain": sum(1 for s in usable if s.sd_uncertain),
            "one_sex_only": sum(1 for s in usable if s.flag.startswith("one sex")),
            "flags": count_of(s.flag for s in series if s.flag)}


def count_of(things) -> dict:
    out = {}
    for t in things:
        out[t] = out.get(t, 0) + 1
    return dict(sorted(out.items()))


def validation(out, series, settings, n):
    ms = V.validated_measures()
    pops = {st.name: PO.draw(st, n, SEED_POPULATION, ms) for st in settings}
    cells = []
    for modality in ("bone_ct", "film_mri", "bone", "ct"):
        cells += V.compare(pops, series, modality, ms)
    write_csv(out, "validation_cells.csv", cells)
    summary = {"by_setting": V.summarise([c for c in cells if c["modalities"] == "bone_ct"]),
               "by_measure": V.summarise([c for c in cells if c["modalities"] == "bone_ct" and c["which"] == "true"],
                                         by=("setting", "measure")),
               "by_modality": V.summarise([c for c in cells if c["which"] == "true"], by=("setting", "modalities")),
               "sd_ratio_by_kind": sd_ratio_by_kind([c for c in cells if c["modalities"] == "bone_ct"])}
    generator = [c for c in cells if c["modalities"] == "bone_ct" and c["setting"] == "generator" and c["which"] == "true"]
    without_tan = [c for c in V.compare({"generator": pops["generator"]}, [s for s in series if s.paper != "tan2004"],
                                        "bone_ct", ms) if c["which"] == "true"]
    summary.update({"panjabi": panjabi_summary(generator), "panjabi_without_tan2004": panjabi_summary(without_tan),
                    "panjabi_by_measure": panjabi_by_measure(generator, without_tan)})
    write_json(out, "validation_summary.json", summary)
    return pops


PANJABI_SPINES = 12


def panjabi_summary(cells) -> dict:
    """Panjabi's means against the pooled series, two ways: inside the prediction interval, where
    another population's mean may fall, and against the pooled mean itself, the stricter test of
    whether Panjabi's specimens sit at the papers' average. His mean is of twelve spines, so both
    tests take his own sampling variance, sd^2 / 12, beside the pool's: the difference is tested
    on sqrt(SE^2 + sd^2 / 12), by z and, since a cell rests on three to nine series, by t on k - 1
    degrees of freedom; the prediction interval is widened by the same variance. The test that
    takes his mean as exact is kept beside them. With three series the prediction interval takes t
    on one degree of freedom (12.7), so the count of series behind each cell is kept beside it.

    The distance d is given signed as well as absolute, since a median of |d| can hold steady while
    its sign moves, and in the papers' SD as well as his."""
    z = np.array([c["z_panjabi"] for c in cells if c["z_panjabi"] is not None and math.isfinite(c["z_panjabi"])])
    signed = np.array([c["d_panjabi"] for c in cells if math.isfinite(c["d_panjabi"])])
    d = np.abs(signed)
    in_papers_sd = np.array([abs(c["panjabi_mean"] - c["lit_mean"]) / c["lit_sd"] for c in cells
                             if math.isfinite(c["lit_sd"]) and c["lit_sd"] > 0])
    r = np.array([c["panjabi_sd_ratio"] for c in cells if math.isfinite(c["panjabi_sd_ratio"])])
    pooled = [c for c in cells if c["k"] >= 3 and math.isfinite(c["lit_se"])]
    tests = {name: [c for c in pooled if outside(c, name)] for name in ("exact", "z", "t")}
    outside_pi = [c for c in pooled if not inside_prediction(c)]
    ks = {}
    for c in pooled:
        ks[str(c["k"])] = ks.get(str(c["k"]), 0) + 1
    out = {"cells_with_interval": int(len(z)), "abs_z_median": float(np.median(np.abs(z))),
           "abs_z_over_2": float((np.abs(z) > 2).mean()), "cells": int(len(d)), "abs_d_median": float(np.median(d)),
           "d_median": float(np.median(signed)), "d_above": float((signed > 0).mean()),
           "abs_d_papers_sd_median": float(np.median(in_papers_sd)),
           "d_over_one": float((d > 1).mean()), "sd_ratio_cells": int(len(r)),
           "sd_ratio_quartiles": [float(np.quantile(r, q)) for q in (0.25, 0.5, 0.75)],
           "pooled_cells": len(pooled), "series_per_pooled_cell": ks,
           "outside_prediction_interval": len(outside_pi),
           "outside_prediction_interval_k5": sum(1 for c in outside_pi if c["k"] >= 5),
           "pooled_cells_k5": sum(1 for c in pooled if c["k"] >= 5),
           "cells_only_tan2004": sum(1 for c in cells if c["only_tan2004"]),
           "sd_cells_pooled": sum(1 for c in cells if c["k_sd"] >= 2),
           "sd_cells_one_series": sum(1 for c in cells if c["k_sd"] == 1),
           "sd_cells_none": sum(1 for c in cells if c["k_sd"] == 0)}
    for name, found in tests.items():
        out["outside_mean_%s" % name] = len(found)
        out["outside_mean_%s_above" % name] = sum(1 for c in found if c["panjabi_mean"] > c["lit_mean"])
    return out


def outside(c: dict, test: str) -> bool:
    """Whether Panjabi's mean differs from the pooled mean at 5 per cent: "exact" takes his mean
    as a constant, "z" and "t" take his twelve spines' sampling variance in too."""
    se = c["lit_se"] if test == "exact" else math.sqrt(c["lit_se"] ** 2 + c["panjabi_sd"] ** 2 / PANJABI_SPINES)
    crit = stats.t.ppf(0.975, c["k"] - 1) if test == "t" else 1.959964
    return abs(c["panjabi_mean"] - c["lit_mean"]) > crit * se


def inside_prediction(c: dict) -> bool:
    """The prediction interval with Panjabi's own sampling variance added under its root."""
    half = (c["pi_high"] - c["pi_low"]) / 2
    centre = (c["pi_high"] + c["pi_low"]) / 2
    root = math.sqrt(c["lit_tau"] ** 2 + c["lit_se"] ** 2)
    wider = half / root * math.sqrt(root ** 2 + c["panjabi_sd"] ** 2 / PANJABI_SPINES)
    return centre - wider <= c["panjabi_mean"] <= centre + wider


def panjabi_by_measure(cells, without_tan) -> dict:
    """Per measure, the signed median of Panjabi's distance from the papers in his SDs, with all
    series and with Tan 2004's left out (a measure only Tan prints has no second reading)."""
    out = {}
    for key in sorted({c["measure"] for c in cells}):
        mine = [c["d_panjabi"] for c in cells if c["measure"] == key]
        rest = [c["d_panjabi"] for c in without_tan if c["measure"] == key]
        out[key] = {"cells": len(mine), "d_median": float(np.median(mine)), "cells_without_tan2004": len(rest),
                    "d_median_without_tan2004": float(np.median(rest)) if rest else None}
    return out


def sd_ratio_by_kind(cells) -> dict:
    """The median SD ratio over the lengths and areas apart from the angles, and over the seven
    SPINEPS measures, for Panjabi's SD and each setting's true and measured SD: the angles' ratios
    run about twice the others', so one median over both hides that one scale fits neither."""
    seven = set(MS.SPINEPS_7)
    groups = {"lengths and areas": lambda c: c["kind"] in ("length", "area"), "angles": lambda c: c["kind"] == "angle",
              "the seven SPINEPS measures": lambda c: c["measure"] in seven}
    out = {}
    for gname, keep in groups.items():
        mine = [c for c in cells if keep(c)]
        panjabi = {(c["measure"], c["level"]): c["panjabi_sd_ratio"] for c in mine}
        row = {"cells": len(panjabi), "panjabi": float(np.nanmedian(list(panjabi.values())))}
        for setting in sorted({c["setting"] for c in mine}):
            for which in ("true", "measured"):
                got = [c["sd_ratio"] for c in mine if c["setting"] == setting and c["which"] == which]
                row["%s, %s" % (setting, which)] = float(np.nanmedian(got))
        out[gname] = row
    return out


def structure(out, pops, rows):
    ms = MS.pool()
    mu, _ = MS.arrays(ms, LEVELS)
    keys = [MS.archive_key(m) for m in ms]
    full = {name: PO.draw(pop.settings, pop.true.shape[0], SEED_POPULATION, ms) for name, pop in pops.items()}
    powers = {L.measure_key(m.key): float(p) for m, p in zip(ms, MS.powers(ms))}
    data = {"correlations": {name: ST.subject_mean_correlations(p) for name, p in full.items()},
            "ratios": ST.ratio_table(full["generator"], mu, keys, LEVELS, rows),
            "isometry": ST.isometry_table(rows, powers),
            "griffith": [{"pair": "%s with %s" % (a, b), "men": m, "women": w, "sexes_together": ST.mixed_sex_r(a, b, m, w)}
                         for a, b, m, w in ST.GRIFFITH]}
    write_json(out, "structure.json", data)


def references(out):
    write_json(out, "references.json", {
        "errors": [dict(zip(("what", "modality", "low", "high", "unit", "source"), e)) for e in REF.ERRORS],
        "generator_errors": REF.generator_errors(MS.pool()),
        "prevalence": [dict(zip(("state", "generator_share", "chain_weight", "papers", "low", "high", "source"), p))
                       for p in REF.PREVALENCE]})


def quality(out, settings, n):
    seven = MS.select(MS.SPINEPS_7)
    data = {"typical": [], "phenotypes": SW.phenotype_qi(PO.GENERATOR, n, SEED_POPULATION, C.PHENOTYPES), "box": {},
            "curation": {}}
    for st in settings:
        for label, ms in (("pool", None), ("seven", seven)):
            pop = PO.draw(st, n, SEED_POPULATION, ms)
            fl = Q.flags(pop)
            row = {"setting": st.name, "measures": label}
            row.update({"vertebra " + k: v for k, v in Q.vertebra_rates(fl).items()})
            row.update({"person " + k: v for k, v in Q.person_rates(fl).items()})
            row.update({"sign by measure": sign_by_measure(pop)})
            data["typical"].append(row)
            if label == "pool":
                data["box"][st.name] = {k: {kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv) for kk, vv in v.items()}
                                        for k, v in Q.box_rates(pop).items()}
                data["curation"][st.name] = Q.curate(pop)[1]
    data["levels"] = list(LEVELS)
    write_json(out, "qi.json", data)


def sign_by_measure(pop) -> dict:
    """The share of vertebrae whose true value is at or below zero, per measure that has any."""
    out = {}
    for j, k in enumerate(pop.keys):
        if pop.power[j] > 0:
            share = float((pop.true[:, :, j] <= 0).mean())
            if share > 0:
                out[k] = share
    return out


QUICK_GRID = {"scale_sd": (0.0, 0.07), "sd_scale": (0.7, 1.0), "rho": (0.5,), "r_between": (0.0, 0.2)}


def grid_of(quick: bool) -> dict:
    return QUICK_GRID if quick else SW.GRID


def state_space(out, series, n, quick):
    points = SW.one_at_a_time()
    rows = []
    for st in points:
        rows.append(SW.read_point(st, series, n, SEED_SWEEP))
    write_csv(out, "state_space.csv", rows)
    near = SW.nearest(series, n=n, seed=SEED_SWEEP, grid=grid_of(quick))
    write_csv(out, "grid.csv", near)
    write_csv(out, "grid_edges.csv", SW.beyond_edges(near[0], series, n=n, seed=SEED_SWEEP, grid=grid_of(quick)))
    return points, near[0]


def naming(out, points, nearest_point, columns):
    seven = MS.select(MS.SPINEPS_7)
    named = {p.name: p for p in points}
    chosen = [PO.GENERATOR] + [named[k] for k in NAMING_POINTS if k in named]
    near = PO.GENERATOR.but(name="nearest the papers", **{k: nearest_point[k] for k in SW.GRID})
    chosen.append(near)
    rows = []
    for st in chosen:
        pop = PO.draw(st, columns, SEED_NAMING, seven)
        for w in NAMING_WIDTHS:
            for rule_name, rule in (("generator's rule", PO.GENERATOR), ("rule matched", st)):
                if rule_name == "rule matched" and st is PO.GENERATOR:
                    continue
                # no rule here holds phi or r_between (naming.py): the matched rule holds the rest
                ignores = ",".join(k for k in ("phi", "r_between") if getattr(st, k)) if rule is st else ""
                got = N.score(pop, seven, w, rule)
                rows.append(dict(got, setting=st.name, rule=rule_name, rule_ignores=ignores, width=w,
                                 **{"setting " + k: v for k, v in st.as_dict().items() if k not in ("name", "loadings")}))
    write_csv(out, "naming.csv", rows)
    return near


def power(out, series, columns, tables):
    """Part B, A and C again. The two-sample tests against Panjabi's twelve take his SD as the
    validation found it, the median of his SD over the papers' (validation_summary.json)."""
    with open(os.path.join(out, "validation_summary.json"), encoding="utf-8") as fh:
        sd_ratio = json.load(fh)["panjabi"]["sd_ratio_quartiles"][1]
    main = PW.between_series(series)
    write_csv(out, "power_cells.csv", main)
    no_tan = [s for s in series if s.paper != "tan2004"]
    same_rows, _ = L.select(L.load_rows(), ("same",))
    splits = {"all": PW.shift_split(series), "without tan2004": PW.shift_split(no_tan),
              "same definition only": PW.shift_split(same_rows)}
    variants = {"main": series, "without tan2004": no_tan, "same definition only": same_rows}
    calibrated = {k: {"panjabi": PW.calibrated_median_f(v, "panjabi"), "literature": PW.calibrated_median_f(v, "literature")}
                  for k, v in variants.items()}
    calibrated["main"]["panjabi, the seven only"] = PW.calibrated_median_f(series, "panjabi", only_seven=True)
    data = {"old_part_b": PW.OLD_PART_B,
            "spread": {k: PW.spread_summary(main if k == "main" else PW.between_series(v)) for k, v in variants.items()},
            "calibrated_median_f": calibrated, "split": splits, "split_recovery": PW.split_recovery(series),
            "panjabi_sd_ratio": sd_ratio, "gold": PW.gold_power(panjabi_sd_ratio=sd_ratio)}
    write_json(out, "power.json", data)
    arms = list(PW.ARMS) + [("39 papers, %s" % k, v["shift_sd_calibrated"], v["level_sd_calibrated"])
                            for k, v in splits.items()]
    a = splits["all"]
    arms.append(("39 papers, all, one shift for every measure", a["shift_sd_calibrated"], a["level_sd_calibrated"], True))
    write_csv(out, "power_naming.csv", PW.naming_loss(arms, columns=columns, tables=tables))


def code_digests() -> dict:
    """The sha256 of every Python file of this folder (the run, the figures, the renders, the
    tables, the snapshot, synthval/ and the tests), read before the run starts."""
    code = {}
    for folder, dirs, files in os.walk(HERE):
        dirs[:] = sorted(d for d in dirs if d not in ("__pycache__", "records") and not d.startswith("."))
        for f in sorted(files):
            if f.endswith(".py"):
                name = os.path.relpath(os.path.join(folder, f), HERE).replace(os.sep, "/")
                with open(os.path.join(folder, f), "rb") as fh:
                    code[name] = hashlib.sha256(fh.read()).hexdigest()
    return dict(sorted(code.items()))


def record(out, args, started, code):
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "schwingcheck"], capture_output=True,
                           text=True).stdout.strip()
    digests = {}
    for name in sorted(os.listdir(out)):
        if name != "RECORD.json":
            with open(os.path.join(out, name), "rb") as fh:
                digests[name] = hashlib.sha256(fh.read()).hexdigest()
    with open(L.SOURCE, encoding="utf-8") as fh:
        source = json.load(fh)
    write_json(out, "RECORD.json", {
        "command": "python3 -I run.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit, "schwingcheck_changed_since_commit": bool(dirty),
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "seeds": {"population": SEED_POPULATION, "sweep": SEED_SWEEP, "naming_columns": SEED_NAMING,
                  "power_columns": PW.NAMING_COLUMN_SEED, "power_tables": PW.NAMING_TABLE_SEED,
                  "power_calibration": PW.CALIBRATION_SEED, "split_recovery": PW.RECOVERY_SEED,
                  "split_recovery_calibrations": "split_recovery + 1000 + trial"},
        "sizes": {"population": args.n, "naming_columns": args.columns, "power_tables": args.tables,
                  "calibration_replicates": PW.CALIBRATION_REPLICATES, "split_replicates": PW.SPLIT_REPLICATES,
                  "split_recovery_trials": PW.RECOVERY_TRIALS, "grid_points": math.prod(len(v) for v in grid_of(args.quick).values())},
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "files": digests, "code": code})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    args.n, args.columns, args.tables = (2000, 60, 1) if args.quick else (20000, 300, 4)
    out = os.path.join(HERE, args.out) if not os.path.isabs(args.out) else args.out
    os.makedirs(out, exist_ok=True)
    started = time.time()
    code = code_digests()
    problems = L.check_snapshot()
    if problems:
        raise SystemExit("; ".join(problems))
    rows = L.load_rows()
    series, _ = L.select(rows)
    write_json(out, "selection.json", selection_record(rows, series))
    write_csv(out, "series.csv", [dict(s.as_dict(), usable=L.usable(s)) for s in series])
    log("state space")
    points, nearest_point = state_space(out, series, args.n // 5, args.quick)
    near = PO.GENERATOR.but(name="nearest the papers", **{k: nearest_point[k] for k in SW.GRID})
    settings = [PO.GENERATOR, PO.GENERATOR.but(name="size_removed", sd_mode="size_removed"), near]
    log("validation")
    pops = validation(out, series, settings, args.n)
    log("structure")
    structure(out, pops, rows)
    references(out)
    log("quality")
    quality(out, settings, args.n // 2)
    log("naming")
    naming(out, points, nearest_point, args.columns)
    log("power")
    power(out, series, args.columns, args.tables)
    record(out, args, started, code)
    log("done")


if __name__ == "__main__":
    main()
