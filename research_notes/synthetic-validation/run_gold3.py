"""Gold tier 3's real CTs on the bounds card: the records of synthval/gold3.py.

    python3 -I run_gold3.py --out records/gold3            # a second

Run from this folder with the Python that holds bordercall's pinned packages, after run_bounds.py
has written records/bounds. Reads records/gold3/report.txt, the report of SchwingNet's gate word
`morphometry covariates` as the grid printed it (job 40878978 of 2026-10-30, read back in two pages
and joined, aggregates alone), and the card. Writes cells.csv (each member, measure and level: the
pooled count, mean and SD, each sex's mean, the card's intervals, the mean, SD and sex verdicts and
the age slope's record), steps.csv (each member's steps against the card's), by_measure.csv (each
engine key's pass counts and mean z by test) and gold3.json (each member's summary with the verdict
against the bar of every paper held out, the tests by family of measures, the covariates' coverage,
the members' fill as the report prints it, the inputs' sha256, the commit and the code). greg's
question of 2026-10-30, whether the literature's results can bound a generator of synthetic spines,
asked of two real cohorts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [REPO, HERE]

import numpy as np  # noqa: E402

from synthval import bounds as B  # noqa: E402
from synthval import gold3 as G3  # noqa: E402
from run import code_digests, log, write_csv, write_json  # noqa: E402

REPORT = os.path.join(HERE, "records", "gold3", "report.txt")
CARD = os.path.join(HERE, "records", "bounds")
SOURCE = ("SchwingNet gate word `morphometry covariates`, job 40878978 on zfh15 at SchwingNet c656299, "
          "2026-10-30 13:08 UTC, read back by the reads covread-1 and covread-2 and joined")


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def fill_lines(text: str) -> list:
    """The report's lines that say how many persons each member's sex and age reached."""
    return [line[2:] for line in text.splitlines() if line.startswith(("- fill ", "- member "))]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--report", default=REPORT)
    ap.add_argument("--card", default=CARD)
    args = ap.parse_args(argv)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    code = code_digests()
    with open(args.report, encoding="ascii") as fh:
        text = fh.read()
    moments = G3.parse(text)
    card = B.load(args.card)
    cells, steps, members = [], [], {}
    for member in G3.MEMBERS:
        log("scoring %s on the card" % member)
        got = G3.score(moments, card, member)
        cells += got["cells"]
        steps += got["steps"]
        members[member] = {"name": G3.MEMBER_NAMES[member], "summary": got["summary"],
                           "by_family": G3.by_family(got["cells"], got["steps"]),
                           "sex": G3.covariate_record(got["cells"], "sex"),
                           "age": G3.covariate_record(got["cells"], "age")}
    with open(os.path.join(args.card, "calibration.csv"), encoding="ascii", newline="") as fh:
        papers = [r for r in csv.DictReader(fh) if (r.get("kind") or B.ALL) == B.ALL]
    write_csv(out, "cells.csv", cells)
    write_csv(out, "steps.csv", steps)
    write_csv(out, "by_measure.csv", [dict(r, member=m) for m in G3.MEMBERS
                                      for r in G3.by_measure([c for c in cells if c["member"] == m],
                                                             [s for s in steps if s["member"] == m])])
    commit = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    write_json(out, "gold3.json", {
        "command": "python3 -I run_gold3.py --out %s" % os.path.relpath(out, HERE),
        "bordercall_commit": commit, "python": platform.python_version(), "numpy": np.__version__, "code": code,
        "source": SOURCE, "report_sha256": sha256(args.report),
        "card_sha256": {n: sha256(os.path.join(args.card, n)) for n in ("bounds.csv", "gradients.csv", "calibration.csv")},
        "reference_n": B.REFERENCE_N, "bar": card.bar(B.ALL),
        "bar_papers": sorted({r["paper"] for r in papers}),
        "members": members, "fill": fill_lines(text),
        "not_scored": ["VerSe: the join read no person's sex (fill verse: sex 0), so its 21 persons enter no table",
                       "ENHANCE.PET's Leipzig and Careggi: their releases carry no sex or age",
                       "the age slope is a record and no test: check() makes none, the card's spread for it "
                       "being not identified (bounds.json, covariate_borrowing)",
                       "within each member, the keys, cells and steps its summary's not_scored names, each with why: "
                       "keys no paper of the card prints, the card's spinous_length under Panjabi's definition, the "
                       "card's film interpedicular cells and steps and its MRI end-plate cell, and the cells whose one "
                       "sex's mean the report withholds (withheld_cells)"],
        "readings": {
            "mean, sd": "the two sexes pooled from their moments, against the card's interval for a new population, "
                        "widened by the sampling error of reference_n people, as check() scores a cohort",
            "step": "the pooled means' difference, its sampling variance from the levels' pooled SDs and the "
                    "covariance the within-sex correlations with the level above and the sexes' shift give",
            "sex": "the sign where the card's interval for a new population's contrast clears zero (check()'s "
                   "test); inside_card: g within that interval as the card gives it; inside: within it widened "
                   "by g's own variance, at every cell",
            "age": "each sex's slope per decade over its SD, the sexes pooled by inverse variance; the card's "
                   "slopes are over the within-band SD, a little narrower than a sex's SD over every age"}})
    for member, rec in members.items():
        s = rec["summary"]
        log("%s: %s; sex inside the card's interval %s of %s, age %s of %s" % (
            member, ", ".join("%s %d/%d" % (t, v["passed"], v["made"]) for t, v in s["tests"].items()),
            rec["sex"].get("inside_card"), rec["sex"].get("cells"), rec["age"].get("inside_card"), rec["age"].get("cells")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
