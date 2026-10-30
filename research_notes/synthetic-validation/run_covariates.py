"""Covariates both ways from what the papers print apart: the records of synthval/covariates.py.

    python3 -I run_covariates.py --out records/covariates      # seconds

Run from this folder with the Python that holds bordercall's pinned packages, after run_strata.py's
snapshot check passes. The sex contrasts read the full snapshot's rows with the sexes' snapshot's
beside them (data/series_sexes.csv, the sexes the reread's series.py pooled or left out, held to
pool back to the full snapshot's rows before anything is read); the gradients read the full
snapshot's alone. Writes contrasts.csv (every stratum printed for both sexes, men minus women, with
the within-sex SD each g is read against and where it and the counts came from, so that every g is
made again from its row), dropped.csv (every pair of both sexes that gives no contrast, with why),
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
    """A contrast with everything its g is made from: g = J (mean_male - mean_female) / sd_within,
    J = 1 - 3 / (4 (n_male + n_female) - 9), sd_within the two printed SDs pooled where sd_from is
    "printed", else the SD sd_from names."""
    return {"paper": c.paper, "cohort": c.cohort, "measure": c.base_key, "level": c.level, "group": c.group,
            "mean_male": c.mean_m, "sd_male": c.sd_m, "n_male": c.n_m, "mean_female": c.mean_f, "sd_female": c.sd_f,
            "n_female": c.n_f, "sd_within": c.sd_within, "g": c.g, "var_g": c.var_g, "sd_from": c.sd_from,
            "count_from": c.count_from, "key": c.key, "technique": c.technique, "modality": c.modality}


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
    problems = PT.check_snapshot_all() + PT.check_snapshot_sexes()
    if problems:
        raise SystemExit("; ".join(problems))
    rows, voc = PT.load_rows_all(), PT.load_vocabulary()
    apart = PT.load_rows_sexes()
    contrasts, dropped = CV.sex_strata(rows + apart, voc)
    gradients = {v: CV.gradients(rows, voc, v) for v in GRADIENT_VARIABLES}
    effects = CV.effects(contrasts, "sex") + [e for v in GRADIENT_VARIABLES for e in CV.effects(gradients[v], v)]
    held = CV.held_out(contrasts, "sex") + [r for v in GRADIENT_VARIABLES for r in CV.held_out(gradients[v], v)]
    summary = CV.summary(held)
    write_csv(out, "contrasts.csv", [contrast_row(c) for c in contrasts])
    write_csv(out, "dropped.csv", dropped)
    write_csv(out, "gradients.csv", [gradient_row(g) for v in GRADIENT_VARIABLES for g in gradients[v]])
    write_csv(out, "effects.csv", effects)
    write_csv(out, "held_out.csv", held)
    write_csv(out, "summary.csv", summary)
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    with open(PT.SOURCE_ALL, encoding="utf-8") as fh:
        source = json.load(fh)
    with open(PT.SOURCE_SEXES, encoding="utf-8") as fh:
        sexes = json.load(fh)
    few = [d for d in dropped if d["why"] == CV.FEW_PER_SEX]
    write_json(out, "covariates.json", {
        "command": "python3 -I run_covariates.py --out %s" % os.path.relpath(out, HERE),
        "bordercall_commit": commit,
        "snapshot": {"commit": source["commit"], "branch": source["branch"], "sha256": source["snapshot_sha256"]},
        "sexes_snapshot": {"commit": sexes["commit"], "sha256": sexes["snapshot_sha256"], "rows": sexes["rows"],
                           "readings_tree": sexes["readings_tree"], "series_tool_sha256": sexes["series_tool_sha256"],
                           "rows_by_why": sexes["rows_by_why"]},
        "counts": {"sex_contrasts": len(contrasts), "sex_papers": sorted({c.paper for c in contrasts}),
                   "sex_contrasts_by_paper": {p: sum(1 for c in contrasts if c.paper == p) for p in sorted({c.paper for c in contrasts})},
                   "sex_contrasts_from_the_sexes_snapshot_alone": len(contrasts) - len(CV.sex_contrasts(rows, voc)),
                   "sex_pairs_dropped": {why: sum(1 for d in dropped if d["why"] == why) for why in sorted({d["why"] for d in dropped})},
                   "dropped_below_min_per_sex": [{k: d[k] for k in ("paper", "cohort", "measure", "level", "group", "technique",
                                                                     "n_male", "n_female")} for d in few],
                   **{"%s_series" % v.replace(" ", "_"): len(gradients[v]) for v in GRADIENT_VARIABLES},
                   **{"%s_papers" % v.replace(" ", "_"): sorted({g.paper for g in gradients[v]}) for v in GRADIENT_VARIABLES},
                   "held_out": len(held)},
        "rules": {"source": CV.OWN_SOURCE, "kinds": list(CV.KINDS), "adult_from": CV.ADULT, "open_band_years": CV.OPEN_SPAN,
                  "min_per_sex": CV.MIN_PER_SEX,
                  "min_per_sex_why": "a sex of fewer gives its own mean to no better than sd / sqrt(n), over 0.45 within-sex SDs, "
                                     "the size of the effects measured, and the normal approximation to g's variance that the "
                                     "pooling's weights rest on fails at one to three degrees of freedom (covariates.py)",
                  "units": {v: CV.VARIABLES[v][2] for v in GRADIENT_VARIABLES}},
        "summary": summary,
        "python": platform.python_version(), "numpy": np.__version__, "seconds": round(time.time() - started),
        "code": code})
    log("done in %d s: %d sex contrasts, %s" % (round(time.time() - started), len(contrasts),
                                               ", ".join("%d %s series" % (len(gradients[v]), v) for v in GRADIENT_VARIABLES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
