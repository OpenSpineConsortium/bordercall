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
            "n_from_cohort": sum(1 for s in usable if s.n_note), "sd_uncertain": sum(1 for s in usable if s.sd_uncertain),
            "one_sex_only": sum(1 for s in usable if s.flag.startswith("one sex"))}


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
               "panjabi": panjabi_summary([c for c in cells if c["modalities"] == "bone_ct"
                                           and c["setting"] == "generator" and c["which"] == "true"]),
               "panjabi_without_tan2004": panjabi_summary(
                   [c for c in V.compare({"generator": pops["generator"]}, [s for s in series if s.paper != "tan2004"],
                                         "bone_ct", ms) if c["which"] == "true"])}
    write_json(out, "validation_summary.json", summary)
    return pops


def panjabi_summary(cells) -> dict:
    """Panjabi's means against the pooled series, two ways: inside the prediction interval, where
    another population's mean may fall, and inside the 95 per cent interval of the pooled mean
    itself, the stricter test of whether Panjabi's specimens sit at the papers' average. With three
    series the prediction interval takes t on one degree of freedom (12.7), so the count of
    series behind each cell is kept beside it."""
    z = np.array([c["z_panjabi"] for c in cells if c["z_panjabi"] is not None and math.isfinite(c["z_panjabi"])])
    d = np.array([abs(c["d_panjabi"]) for c in cells if math.isfinite(c["d_panjabi"])])
    r = np.array([c["panjabi_sd_ratio"] for c in cells if math.isfinite(c["panjabi_sd_ratio"])])
    pooled = [c for c in cells if c["k"] >= 3 and math.isfinite(c["lit_se"])]
    outside_ci = [c for c in pooled if abs(c["panjabi_mean"] - c["lit_mean"]) > 1.959964 * c["lit_se"]]
    outside_pi = [c for c in pooled if not c["pi_low"] <= c["panjabi_mean"] <= c["pi_high"]]
    ks = {}
    for c in pooled:
        ks[str(c["k"])] = ks.get(str(c["k"]), 0) + 1
    return {"cells_with_interval": int(len(z)), "abs_z_median": float(np.median(np.abs(z))),
            "abs_z_over_2": float((np.abs(z) > 2).mean()), "cells": int(len(d)), "abs_d_median": float(np.median(d)),
            "d_over_one": float((d > 1).mean()), "sd_ratio_cells": int(len(r)),
            "sd_ratio_quartiles": [float(np.quantile(r, q)) for q in (0.25, 0.5, 0.75)],
            "pooled_cells": len(pooled), "series_per_pooled_cell": ks,
            "outside_prediction_interval": len(outside_pi), "outside_pooled_mean_ci": len(outside_ci),
            "outside_pooled_mean_ci_above": sum(1 for c in outside_ci if c["panjabi_mean"] > c["lit_mean"]),
            "outside_prediction_interval_k5": sum(1 for c in outside_pi if c["k"] >= 5),
            "pooled_cells_k5": sum(1 for c in pooled if c["k"] >= 5),
            "cells_only_tan2004": sum(1 for c in cells if c["only_tan2004"]),
            "sd_cells_pooled": sum(1 for c in cells if c["k_sd"] >= 2),
            "sd_cells_one_series": sum(1 for c in cells if c["k_sd"] == 1),
            "sd_cells_none": sum(1 for c in cells if c["k_sd"] == 0)}


def structure(out, pops, rows):
    ms = MS.pool()
    mu, _ = MS.arrays(ms, LEVELS)
    keys = [MS.archive_key(m) for m in ms]
    full = {name: PO.draw(pop.settings, pop.true.shape[0], SEED_POPULATION, ms) for name, pop in pops.items()}
    powers = {L.measure_key(m.key): float(p) for m, p in zip(ms, MS.powers(ms))}
    data = {"correlations": {name: ST.subject_mean_correlations(p) for name, p in full.items()},
            "ratios": ST.ratio_table(full["generator"], mu, keys, LEVELS),
            "isometry": ST.isometry_table(rows, powers),
            "griffith": [{"pair": "%s with %s" % (a, b), "men": m, "women": w} for a, b, m, w in ST.GRIFFITH]}
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


def state_space(out, series, n, quick):
    points = SW.one_at_a_time()
    rows = []
    for st in points:
        rows.append(SW.read_point(st, series, n, SEED_SWEEP))
    write_csv(out, "state_space.csv", rows)
    grid = SW.GRID if not quick else {"scale_sd": (0.02, 0.07), "sd_scale": (0.7, 1.0), "rho": (0.5,), "r_between": (0.0, 0.2)}
    near = SW.nearest(series, n=n, seed=SEED_SWEEP, grid=grid)
    write_csv(out, "grid.csv", near)
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
            "gold": PW.gold_power()}
    write_json(out, "power.json", data)
    arms = list(PW.ARMS) + [("39 papers, %s" % k, v["shift_sd_calibrated"], v["level_sd_calibrated"])
                            for k, v in splits.items()]
    write_csv(out, "power_naming.csv", PW.naming_loss(arms, columns=columns, tables=tables))


def code_digests() -> dict:
    """The sha256 of run.py and every module of synthval/, read before the run starts."""
    code = {}
    for name in ["run.py"] + ["synthval/" + f for f in sorted(os.listdir(os.path.join(HERE, "synthval"))) if f.endswith(".py")]:
        with open(os.path.join(HERE, name), "rb") as fh:
            code[name] = hashlib.sha256(fh.read()).hexdigest()
    return code


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
                  "power_columns": 4101, "power_tables": 4102},
        "sizes": {"population": args.n, "naming_columns": args.columns, "power_tables": args.tables},
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
