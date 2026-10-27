"""Hold the tables to what the papers say in their running text.

    python check_prose.py        # every prose value against the cells it speaks of

prose.csv is one row per number the four papers state in their abstracts, results,
discussions and captions, and in their Methods about the specimens, read by eye from the
rendered pages by two passes as the tables were (README.md). Each row names the cells the
number speaks of and the rule that turns those cells into the number: the value of one cell,
the mean of several, the lowest or highest of a run, the mean of a left and a right, a
difference, or a count of cells. A paper that contradicts the table its sentence speaks of
is recorded as such, agrees=no with the note saying so, and the test holds that record to
the cells too: a contradiction that goes away, or an agreement that stops holding, fails it
either way.
"""
from __future__ import annotations

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FIELDS = ["paper", "pdf_page", "printed_page", "where", "quote", "measure", "level", "statistic",
          "printed", "value", "units", "cells", "rule", "tolerance", "agrees", "note", "passA", "passB"]


def read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def counts(rule: str) -> bool:
    """A rule that counts cells, which may be words, and so takes the printed strings."""
    return rule == "count" or rule.startswith("count:")


def cell_values(prov: dict[str, dict], ids: str, rule: str = "") -> list:
    out = []
    for cid in ids.split(";"):
        cid = cid.strip()
        if cid not in prov:
            raise KeyError("prose.csv names a cell that is not in provenance.csv: %s" % cid)
        v = prov[cid]["value"]
        if v == "":
            raise ValueError("prose.csv names a cell with no value: %s" % cid)
        out.append(v if counts(rule) else float(v))
    return out


def evaluate(rule: str, values: list) -> float:
    if rule == "count":                    # how many cells: twelve specimens are twelve rows
        return float(len(values))
    if rule.startswith("count:"):          # how many of the cells print the word after the colon
        return float(sum(1 for v in values if v == rule[len("count:"):]))
    if rule == "equal":
        (v,) = values
        return v
    if rule in ("mean", "lr_mean"):
        return sum(values) / len(values)
    if rule == "low":
        return min(values)
    if rule == "high":
        return max(values)
    if rule == "diff":
        a, b = values
        return a - b
    if rule == "ratio":
        a, b = values
        return a / b
    if rule == "percent":
        a, b = values
        return 100.0 * (a - b) / b
    if rule == "sum":
        return sum(values)
    if rule == "lr_diff":                  # mean of the first pair minus mean of the second
        a, b, c, d = values
        return (a + b) / 2.0 - (c + d) / 2.0
    if rule == "lr_ratio":                 # mean of the first pair over mean of the second
        a, b, c, d = values
        return (a + b) / (c + d)
    if rule == "abs_low":
        return min(abs(v) for v in values)
    if rule == "abs_high":
        return max(abs(v) for v in values)
    if rule == "abs_mean":
        return sum(abs(v) for v in values) / len(values)
    raise ValueError("unknown rule %r" % rule)


def check(prov_rows: list[dict], prose: list[dict]) -> list[str]:
    """Each prose row's claim of agreement or contradiction, held to the cells."""
    prov = {r["id"]: r for r in prov_rows}
    problems = []
    for p in prose:
        if p["cells"] == "":
            continue                       # a value the tables do not carry: recorded, not tested
        try:
            got = evaluate(p["rule"], cell_values(prov, p["cells"], p["rule"]))
        except (KeyError, ValueError) as e:
            problems.append("%s p.%s %r: %s" % (p["paper"], p["printed_page"], p["quote"], e))
            continue
        want = float(p["value"])
        tol = float(p["tolerance"] or 0.05)
        holds = abs(got - want) <= tol + 1e-9
        if p["agrees"] == "yes" and not holds:
            problems.append("%s p.%s says %s %s = %s; the cells give %.4f (%s of %s)"
                            % (p["paper"], p["printed_page"], p["measure"], p["level"], p["value"], got, p["rule"], p["cells"]))
        if p["agrees"] == "no" and holds:
            problems.append("%s p.%s says %s %s = %s and prose.csv calls it a contradiction, but the cells give %.4f"
                            % (p["paper"], p["printed_page"], p["measure"], p["level"], p["value"], got))
        if p["agrees"] not in ("yes", "no"):
            problems.append("%s p.%s %r: agrees must be yes or no" % (p["paper"], p["printed_page"], p["quote"]))
    return problems


def main() -> int:
    prov = read_csv(os.path.join(HERE, "provenance.csv"))
    prose = read_csv(os.path.join(HERE, "prose.csv"))
    problems = check(prov, prose)
    tested = sum(1 for p in prose if p["cells"])
    print("%d prose values, %d held to cells, %d problems" % (len(prose), tested, len(problems)))
    for s in problems:
        print("  " + s)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
