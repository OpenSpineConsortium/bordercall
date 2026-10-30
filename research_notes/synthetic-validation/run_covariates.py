"""Covariates both ways from what the papers print apart: the records of synthval/covariates.py.

    python3 -I run_covariates.py --out records/covariates      # seconds

Run from this folder with the Python that holds bordercall's pinned packages, after run_strata.py's
snapshot check passes. Writes contrasts.csv (every stratum printed for both sexes, men minus women),
gradients.csv (every series printed over two or more bands of age, body height or body weight, its
slope), effects.csv (per variable and measure, the papers pooled), held_out.csv (every stratum and
series scored with the effect from the other papers alone, both ways), summary.csv (per variable over
the held-out papers) and covariates.json (the counts, the rules, the commit, the snapshot's digest
and the code).
"""
from __future__ import annotations

import argparse
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
from run import code_digests, log, write_csv, write_json  # noqa: E402

GRADIENT_VARIABLES = ("age", "body height", "body weight")


def contrast_row(c: CV.Contrast) -> dict:
    return {"paper": c.paper, "cohort": c.cohort, "measure": c.base_key, "level": c.level, "group": c.group,
            "mean_male": c.mean_m, "sd_male": c.sd_m, "n_male": c.n_m, "mean_female": c.mean_f, "sd_female": c.sd_f,
            "n_female": c.n_f, "g": c.g, "var_g": c.var_g}


def gradient_row(g: CV.Gradient) -> dict:
    b, v = g.slope()
    return {"variable": g.variable, "paper": g.paper, "cohort": g.cohort, "measure": g.base_key, "level": g.level, "sex": g.sex,
            "bands": len(g.x), "midpoints": ";".join("%g" % x for x in g.x), "means": ";".join("%g" % m for m in g.mean),
            "people": float(g.n.sum()), "sd_within": g.sd_within, "slope_sd": b, "var_slope": v, "unit": CV.VARIABLES[g.variable][2]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    started = time.time()
    code = code_digests()
    problems = PT.check_snapshot_all()
    if problems:
        raise SystemExit("; ".join(problems))
    rows, voc = PT.load_rows_all(), PT.load_vocabulary()
    contrasts = CV.sex_contrasts(rows, voc)
    gradients = {v: CV.gradients(rows, voc, v) for v in GRADIENT_VARIABLES}
    effects = CV.effects(contrasts, "sex") + [e for v in GRADIENT_VARIABLES for e in CV.effects(gradients[v], v)]
    held = CV.held_out(contrasts, "sex") + [r for v in GRADIENT_VARIABLES for r in CV.held_out(gradients[v], v)]
    summary = CV.summary(held)
    write_csv(out, "contrasts.csv", [contrast_row(c) for c in contrasts])
    write_csv(out, "gradients.csv", [gradient_row(g) for v in GRADIENT_VARIABLES for g in gradients[v]])
    write_csv(out, "effects.csv", effects)
    write_csv(out, "held_out.csv", held)
    write_csv(out, "summary.csv", summary)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    write_json(out, "covariates.json", {
        "command": "python3 -I run_covariates.py --out %s" % os.path.relpath(out, HERE),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "counts": {"sex_contrasts": len(contrasts), "sex_papers": sorted({c.paper for c in contrasts}),
                   **{"%s_series" % v.replace(" ", "_"): len(gradients[v]) for v in GRADIENT_VARIABLES},
                   **{"%s_papers" % v.replace(" ", "_"): sorted({g.paper for g in gradients[v]}) for v in GRADIENT_VARIABLES},
                   "held_out": len(held)},
        "rules": {"source": CV.OWN_SOURCE, "kinds": list(CV.KINDS), "adult_from": CV.ADULT, "open_band_years": CV.OPEN_SPAN,
                  "units": {v: CV.VARIABLES[v][2] for v in GRADIENT_VARIABLES}},
        "summary": summary,
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "code": code})
    log("done in %d s: %d sex contrasts, %s" % (round(time.time() - started), len(contrasts),
                                               ", ".join("%d %s series" % (len(gradients[v]), v) for v in GRADIENT_VARIABLES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
