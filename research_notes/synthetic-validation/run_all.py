"""Write the records of the second part of this note: every measure of the reread, not only the
generator's 32.

    python3 -I run_all.py --out records/all            # every record, about forty minutes on 4 CPUs
    python3 -I run_all.py --out records/all --quick    # small populations and a small grid, to try the code

Run from this folder with the Python that holds bordercall's pinned packages, after run.py, whose
records/grid.csv this part reads for the generator's nearest point. Every number in README.md's
second part is read from these records by figures_all.py and tables.py; RECORD_ALL.json carries
the command, the seeds, bordercall's commit, the full snapshot's digest and the code.
"""
from __future__ import annotations

import argparse
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
from schwingcheck import measures as MS  # noqa: E402
from synthval import all_measures as AM  # noqa: E402
from synthval import literature as L  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import population as PO  # noqa: E402
from synthval import sweep as SW  # noqa: E402
from run import QUICK_GRID, SEED_NAMING, SEED_POPULATION, SEED_SWEEP, clean, code_digests, log, write_csv, write_json  # noqa: E402

TABLES = ("panjabi", "papers", "both")
TABLE_NAMES = {"panjabi": "A", "papers": "B", "both": "C"}
LUMBAR = AM.LUMBAR
NAMING_WIDTHS = {"C3-L5": (1, 3, 9), "L1-L5": (1, 3, 5)}


def tables_of() -> dict:
    rows = PT.load_rows_all()
    series, why = PT.select_all(rows)
    cells = PT.pooled_cells(series)
    voc = PT.load_vocabulary()
    a = PT.panjabi_table()
    b = PT.papers_table(cells, voc)
    return {"rows": rows, "series": series, "why": why, "cells": cells, "vocabulary": voc,
            "tables": {"panjabi": a, "papers": b, "both": PT.combined_table(a, b)}}


def table_rows(t: PT.Table) -> list:
    err, power = t.error, t.power
    out = []
    for j, key in enumerate(t.keys):
        for i, level in enumerate(t.levels):
            if math.isfinite(t.mu[j, i]):
                out.append({"measure": key, "kind": t.kinds[j], "source": t.sources[j], "level": level,
                            "mean": float(t.mu[j, i]), "sd": float(t.sd[j, i]), "error": float(err[j]), "power": float(power[j])})
    return out


def selection(out, d) -> None:
    series, why, cells = d["series"], d["why"], d["cells"]
    usable = [s for s in series if L.usable(s)]
    pool = {L.measure_key(m.key) for m in MS.pool()}
    placed = [c for c in cells if c["placed_at"]]
    summary = {"rows": len(d["rows"]), "series": len(series), "usable": len(usable), "left_out": why,
               "usable_by_measure": count_by(s.key for s in usable), "usable_by_paper": count_by(s.paper for s in usable),
               "usable_by_modality": count_by(s.modality for s in usable), "papers": len({s.paper for s in usable}),
               "measures_with_usable_series": len({s.key for s in usable}),
               "keys_with_usable_series": len({PT.base_key(s.key) for s in usable}),
               "keys_with_usable_series_not_in_generator": len({PT.base_key(s.key) for s in usable} - pool),
               "cells_pooled": len(cells), "cells_placed": len(placed),
               "cells_placed_by_modality": count_by(c["modality"] for c in placed),
               "cells_placed_by_k": count_by(str(c["k"]) for c in placed),
               "cells_placed_by_sd_from": count_by(c["sd_from"] for c in placed),
               "cells_placed_only_tan2004": sum(1 for c in placed if c["papers"] == "tan2004"),
               "cells_unplaced_by_key": count_by(c["base_key"] for c in cells if not c["placed_at"]),
               "variants": {k: PT.VARIANT_WHY[k] for k in PT.VARIANTS}}
    for name, t in d["tables"].items():
        summary["table " + name] = {"letter": TABLE_NAMES[name], "name": t.name, "measures": len(t.keys), "cells": t.cells(),
                                    "complete_C3_L5": len(t.complete_over(LEVELS)), "complete_L1_L5": len(t.complete_over(LUMBAR)),
                                    "kinds": count_by(t.kinds), "sources": count_by(t.sources)}
        write_csv(out, "table_%s.csv" % name, table_rows(t))
    write_json(out, "selection_all.json", summary)
    write_csv(out, "cells.csv", cells)
    inv = PT.inventory(d["rows"], series, cells, d["vocabulary"], {TABLE_NAMES[k]: t for k, t in d["tables"].items()})
    write_csv(out, "inventory.csv", inv)


def count_by(things) -> dict:
    out = {}
    for t in things:
        out[t] = out.get(t, 0) + 1
    return dict(sorted(out.items()))


def generator_nearest(records: str) -> PO.Settings:
    """The generator's nearest point from the first part's grid (records/grid.csv), as naming() took it."""
    import csv
    with open(os.path.join(records, "grid.csv"), encoding="utf-8") as fh:
        best = next(csv.DictReader(fh))
    return PO.GENERATOR.but(name="nearest the papers (32 measures)", **{k: float(best[k]) for k in SW.GRID})


def state_space(out, d, n, quick) -> dict:
    grid = QUICK_GRID if quick else SW.GRID
    nearest = {}
    rows, one = [], []
    for name, t in d["tables"].items():
        log("grid on table %s (%s)" % (TABLE_NAMES[name], t.name))
        near = AM.nearest(t, n=n, seed=SEED_SWEEP, grid=grid)
        for p in near:
            p["table_letter"] = TABLE_NAMES[name]
        rows += near
        nearest[name] = PO.GENERATOR.but(name="nearest the papers (%s)" % TABLE_NAMES[name], **{k: near[0][k] for k in grid})
        pts = AM.one_at_a_time(t, n, SEED_SWEEP)
        for p in pts:
            p["table_letter"] = TABLE_NAMES[name]
        one += pts
    write_csv(out, "grid_all.csv", rows)
    write_csv(out, "state_space_all.csv", one)
    return nearest


def quality(out, d, nearest, gen_nearest, n) -> None:
    data = []
    for name, t in d["tables"].items():
        settings = [PO.GENERATOR, PO.GENERATOR.but(name="size_removed", sd_mode="size_removed"),
                    PO.GENERATOR.but(name="size_removed, scale_sd 0.035", sd_mode="size_removed", scale_sd=0.035),
                    gen_nearest, nearest[name]]
        for st in settings:
            q = AM.quality(t, st, n, SEED_POPULATION)
            q["table_letter"] = TABLE_NAMES[name]
            data.append(q)
    write_json(out, "qi_all.json", data)


def naming(out, d, nearest, columns) -> None:
    """The rule on columns drawn from table C at its nearest point, built on subsets complete over
    the run scored: over C3 to L5 the seven, the generator's 32 and every complete measure of C; over
    L1 to L5 the seven, the 32 and every complete measure of A, B and C."""
    both = d["tables"]["both"]
    seven = [both.keys.index(MS.archive_key(m)) for m in MS.select(MS.SPINEPS_7)]
    pool = [both.keys.index(MS.archive_key(m)) for m in MS.pool()]
    subsets = {"C3-L5": [("the seven", seven), ("the generator's 32", pool), ("every complete measure of C", both.complete_over(LEVELS))],
               "L1-L5": [("the seven", seven), ("the generator's 32", pool)]}
    a_keys = {k for k in d["tables"]["panjabi"].keys}
    b_keys = {k for k in d["tables"]["papers"].keys}
    lumbar_complete = both.complete_over(LUMBAR)
    subsets["L1-L5"] += [("every complete measure of A", [j for j in lumbar_complete if both.keys[j] in a_keys]),
                         ("every complete measure of B", [j for j in lumbar_complete if both.keys[j] in b_keys]),
                         ("every complete measure of C", lumbar_complete)]
    rows = []
    for st in (PO.GENERATOR, nearest["both"]):
        pop = PO.draw_table(both, st, columns, SEED_NAMING)
        for run, levels in (("C3-L5", list(LEVELS)), ("L1-L5", LUMBAR)):
            for label, idx in subsets[run]:
                for w in NAMING_WIDTHS[run]:
                    got = AM.score(pop, both, idx, w, levels, st)
                    rows.append(dict(got, setting=st.name, run=run, measures=label, n_measures=len(idx), width=w,
                                     **{"setting " + k: v for k, v in st.as_dict().items() if k not in ("name", "loadings")}))
                log("naming %s %s width %d: exact %.3f" % (run, label, w, got["exact"]))
    write_csv(out, "naming_all.csv", rows)


def spread(out, d) -> None:
    both = d["tables"]["both"]
    errors = dict(zip(both.keys, both.error))
    panjabi = {L.measure_key(m.key) for m in PT.panjabi_measures()}
    rows = AM.spread(d["cells"], errors, panjabi)
    write_csv(out, "spread_all.csv", rows)
    write_json(out, "spread_all.json", {"summary": AM.spread_summary(rows),
                                        "by_measure": {k: AM.spread_summary([r for r in rows if r["measure"] == k])["all"]
                                                       for k in sorted({r["measure"] for r in rows})}})


def record(out, args, started, code) -> None:
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    digests = {}
    for name in sorted(os.listdir(out)):
        if name != "RECORD_ALL.json":
            with open(os.path.join(out, name), "rb") as fh:
                digests[name] = hashlib.sha256(fh.read()).hexdigest()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    write_json(out, "RECORD_ALL.json", {
        "command": "python3 -I run_all.py --out %s%s" % (os.path.relpath(out, HERE), " --quick" if args.quick else ""),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"],
                     "vocabulary_sha256": source["vocabulary_sha256"]},
        "seeds": {"population": SEED_POPULATION, "sweep": SEED_SWEEP, "naming_columns": SEED_NAMING},
        "sizes": {"population": args.n, "naming_columns": args.columns,
                  "grid_points": math.prod(len(v) for v in (QUICK_GRID if args.quick else SW.GRID).values())},
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "files": digests, "code": code})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--records", default=os.path.join(HERE, "records"), help="the first part's records, for the generator's nearest point")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args(argv)
    args.n = 500 if args.quick else 4000
    args.columns = 100 if args.quick else 2000
    started = time.time()
    code = code_digests()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    problems = PT.check_snapshot_all()
    if problems:
        raise SystemExit("; ".join(problems))
    d = tables_of()
    log("selection and tables")
    selection(out, d)
    log("state space")
    nearest = state_space(out, d, args.n, args.quick)
    log("quality")
    quality(out, d, nearest, generator_nearest(args.records), args.n)
    log("naming")
    naming(out, d, nearest, args.columns)
    log("spread")
    spread(out, d)
    record(out, args, started, code)
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
