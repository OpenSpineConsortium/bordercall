#!/usr/bin/env python3
"""The figures the note quotes from the reviewers' part C runs, read from the logs and JSONs those
runs left, so that nothing is scored again and no .npz file is needed.

Every run scored the same 300 typical columns with the same rule as cadaver_power.py's part B (the
note's part C). A run's log prints each table's share named exactly, the share it answers at 0.99
and the precision of those answers, to four decimals. A table's loss is its share named exactly
minus the reference's, in points: the reference is the note's people-2000 nominal table of draw 0,
read from the note's own part_b_seven.json (exact minus minus_2000 of any arm), so a loss here is the
note's bracketed figure. The mean of per-table losses is the loss of the mean, so the logs' four
decimals give it to about 0.01 point. Per set of tables: the mean loss, its table-to-table SD and
the SE of the mean from that SD, the range, the mean precision, its SD, the worst table and how
many tables fall below 99%, and the mean share answered. Common-random-number arms share their
draws table by table, so their paired differences are given with the SE from the tables.

The column-clustered SEs the reviewers' analyse.py printed need the per-field results in the .npz
files and are not given here. The second reviewer's pooled-shift tables are read from
pooled_shift_read.log, which printed each table's row from that reviewer's .npz files.

    python3 -I verify/summarise_runs.py seven/part_b_seven.json verify
"""
import json
import math
import os
import re
import sys
from collections import OrderedDict

import numpy as np

CLAIM_SHARE = 0.99
SHORT = re.compile(r"^(?P<name>\S+)\s+(?P<draw>\d+) exact (?P<exact>[\d.]+) ans (?P<ans>[\d.]+) prec (?P<prec>[\d.]+|nan)")
ARMS = re.compile(r"^(?P<name>[^/\s]+)/(?P<rule>\w+)/(?P<draw>\d+)\s+exact (?P<exact>[\d.]+)\s+ans (?P<ans>[\d.]+)\s+prec (?P<prec>[\d.]+|nan)")
FRESH = re.compile(r"^(?P<name>\S+) seed (?P<seed>\d+) draw (?P<draw>\d+): exact (?P<exact>[\d.]+)\s+loss \S+\s+answered (?P<ans>[\d.]+)"
                   r"\s+n_ans \d+\s+wrong \d+\s+precision (?P<prec>[\d.]+|nan)")
PIPE = re.compile(r"^(?P<name>[^|\s]+)\|(?P<draw>\d+)\s+exact (?P<exact>[\d.]+) ans (?P<ans>[\d.]+) prec (?P<prec>[\d.]+|nan)")
POOLED = re.compile(r"^\s+(?P<name>w\d+:\S+) (?P<draw>\d+) exact (?P<exact>[\d.]+) ans (?P<ans>[\d.]+) prec (?P<prec>[\d.]+|nan)")


def reference(part_b: str) -> dict:
    """The people-2000 nominal table of draw 0, per width, from the note's own record."""
    b = json.load(open(part_b))
    arm = b["arms"]["people-2000/nominal"]
    return {int(n): s["exact"] - s["minus_2000"] for n, s in arm.items()}


def read(path: str, pattern) -> "OrderedDict[str, list]":
    """Each set of tables in a log, by name, as (exact, answered, precision) rows in log order."""
    sets = OrderedDict()
    for line in open(path):
        m = pattern.match(line)
        if m and not m.group("name").startswith("people-2000"):
            p = m.group("prec")
            sets.setdefault(m.group("name"), []).append(
                (float(m.group("exact")), float(m.group("ans")), float("nan") if p == "nan" else float(p)))
    return sets


def describe(label: str, rows: list, ref: float) -> np.ndarray:
    a = np.array(rows)
    loss = 100 * (a[:, 0] - ref)
    prec = 100 * a[:, 2]
    k = len(rows)
    sd = loss.std(ddof=1) if k > 1 else 0.0
    shown = prec[~np.isnan(prec)]
    print("%-44s tables %2d  loss %+6.2f (table SD %.2f, SE %.2f, range %+.1f to %+.1f)  answered %5.2f%%  "
          "0.99 right %.2f%% (table SD %.2f, worst %.2f, below 99%%: %d)" % (
              label, k, loss.mean(), sd, sd / math.sqrt(k), loss.min(), loss.max(), 100 * a[:, 1].mean(),
              shown.mean(), shown.std(ddof=1) if len(shown) > 1 else 0.0, shown.min(), (shown < 100 * CLAIM_SHARE).sum()))
    return loss


def paired(label: str, a: list, b: list) -> None:
    """b minus a, table by table on the same draws, in points."""
    d = 100 * (np.array([r[0] for r in b]) - np.array([r[0] for r in a]))
    print("%-44s tables %2d  difference %+.2f (SE from tables %.2f)" % (label, len(d), d.mean(), d.std(ddof=1) / math.sqrt(len(d))))


def chance_of_mild_draws(observed_rms: float = 0.463) -> float:
    """How often four tables of the seven-r0 arm's own draw (7 measures by 3 regions, the thoracic and
    lumbar shifts correlated 0.7, SD 0.57) come out with a pooled shift RMS as small as the note's four
    (0.463, verify/draws.log); the reviewers' analyse.py did the same with this seed."""
    rng = np.random.default_rng(1)
    z = rng.normal(size=(200000, 4, 7, 3))
    z[..., 2] = 0.7 * z[..., 1] + math.sqrt(1 - 0.49) * z[..., 2]
    pooled = 0.57 * np.sqrt((z ** 2).mean(axis=(1, 2, 3)))
    return float((pooled <= observed_rms).mean())


def main(part_b: str, folder: str) -> int:
    ref = reference(part_b)
    j = lambda name: os.path.join(folder, name)
    print("reference (people-2000, nominal, draw 0): " + ", ".join("%d bodies %.5f" % (n, ref[n]) for n in sorted(ref)))

    print("\n== The note's own tables, replayed (run_jobs.py, r_arms_w3.log), 3 bodies")
    note = read(j("r_arms_w3.log"), ARMS)
    for name, rows in note.items():
        describe(name, rows, ref[3])

    print("\n== Common random numbers, 8 fresh tables per arm, seed 99001 (crn.py, crn2.py)")
    a3, b3, c9 = read(j("crn_a_w3.log"), SHORT), read(j("crn_b_w3.log"), SHORT), read(j("crn_c_w9.log"), SHORT)
    labels = {"r0": "r = 0, median shift 0.57, level by level 0", "r0.5": "r = 0.5, shift 0.54, level by level 0.19",
              "r0pooled": "r = 0, pooled shift 0.736, level by level 0", "shift0.5all": "one shift of 0.5 for every region"}
    for name, rows in list(a3.items()) + list(b3.items()):
        describe("3 bodies, " + labels[name], rows, ref[3])
    for name, rows in c9.items():
        describe("9 bodies, " + labels[name], rows, ref[9])
    paired("3 bodies, r = 0.5 minus r = 0", a3["r0"], a3["r0.5"])
    paired("3 bodies, pooled shift minus median shift", a3["r0"], b3["r0pooled"])
    paired("9 bodies, r = 0.5 minus r = 0", c9["r0"], c9["r0.5"])
    paired("9 bodies, pooled shift minus median shift", c9["r0"], c9["r0pooled"])

    print("\n== seven-r0 at other TABLE_SEEDs, 4 tables each (run.py; the note's four are seed 4102)")
    orig = read(j("orig_w3.log"), FRESH)["seven-r0"]
    fresh = {n: read(j("fresh_w%d.log" % n), FRESH)["seven-r0"] for n in (1, 3, 9)}
    describe("1 body, 16 fresh tables (seeds 7001-7004)", fresh[1], ref[1])
    describe("3 bodies, the note's 4 (seed 4102)", orig, ref[3])
    describe("3 bodies, 16 fresh tables (seeds 7001-7004)", fresh[3], ref[3])
    describe("3 bodies, 24 fresh (16 and the 8 above)", fresh[3] + a3["r0"], ref[3])
    describe("3 bodies, all 28", orig + fresh[3] + a3["r0"], ref[3])
    describe("9 bodies, 16 fresh tables (seeds 7001-7004)", fresh[9], ref[9])
    describe("9 bodies, 24 fresh (16 and the 8 above)", fresh[9] + c9["r0"], ref[9])
    describe("3 bodies, the same 16, predictive (run_rule.py)", read(j("fresh_pred_w3.log"), FRESH)["seven-r0"], ref[3])
    print("chance that four tables of the arm come out as mild as the note's four: %.4f" % chance_of_mild_draws())

    print("\n== The shift pooled, a second reviewer's (pooled_shift.py, read by pooled_shift_read.py): the note's 4 r = 0"
          "\n   tables and fresh ones (seed 9090; 4 at 1 body, 8 at 3 and 9), each at the median shift 0.57 and scaled to"
          "\n   the pooled shift 0.7355, on the same draws")
    ps = read(j("pooled_shift_read.log"), POOLED)
    width = lambda n: "%d %s" % (n, "body" if n == 1 else "bodies")
    for n in (1, 3, 9):
        med = ps["w%d:note-median" % n] + ps["w%d:fresh-median" % n]
        pld = ps["w%d:note-pooled" % n] + ps["w%d:fresh-pooled" % n]
        describe("%s, median shift, the note's 4 + fresh" % width(n), med, ref[n])
        describe("%s, median shift, the fresh alone" % width(n), ps["w%d:fresh-median" % n], ref[n])
        describe("%s, pooled shift, the note's 4 + fresh" % width(n), pld, ref[n])
        paired("%s, pooled shift minus median shift" % width(n), med, pld)

    print("\n== Every r = 0 table: at the median shift the note's 4, crn.py's 8 (not run at 1 body), run.py's 16"
          "\n   and pooled_shift.py's 8 (4 at 1 body); at the pooled shift crn2.py's 8 (not run at 1 body) and"
          "\n   pooled_shift.py's 12 (8 at 1 body)")
    describe("1 body, median shift, all 24 tables", ps["w1:note-median"] + fresh[1] + ps["w1:fresh-median"], ref[1])
    describe("3 bodies, median shift, all 36 tables", orig + a3["r0"] + fresh[3] + ps["w3:fresh-median"], ref[3])
    describe("9 bodies, median shift, all 36 tables", ps["w9:note-median"] + c9["r0"] + fresh[9] + ps["w9:fresh-median"], ref[9])
    describe("3 bodies, pooled shift, all 20 tables", b3["r0pooled"] + ps["w3:note-pooled"] + ps["w3:fresh-pooled"], ref[3])
    describe("9 bodies, pooled shift, all 20 tables", c9["r0pooled"] + ps["w9:note-pooled"] + ps["w9:fresh-pooled"], ref[9])

    print("\n== Tables from CTs (ct_people.py, 6 tables each, 3 bodies; error taken out of each level's SD)")
    describe("58 CTs, no size spread", read(j("ct58_w3.log"), SHORT)["ct-58"], ref[3])
    describe("58 CTs, the generator's size spread 0.07", read(j("ct58size_w3.log"), SHORT)["ct-58"], ref[3])
    print("\n== Tables from CTs, a second reviewer's (ct_tables.py; err: error out, no size spread; errsize: size"
          "\n   spread left in; plain: nothing taken out; oracle: each person's own size divided out)")
    for log, n in (("ct_run4_w1.log", 1), ("ct_run1_w3.log", 3), ("ct_run2_w3.log", 3), ("ct_run3_w9.log", 9)):
        for name, rows in read(j(log), PIPE).items():
            describe("%d bodies, %s" % (n, name), rows, ref[n])

    print("\n== seven-r0's own draws with the level-by-level part larger earlier series leave at r = 0 (r0_large.py)")
    for name in ("run1_base_lbl0.233.json", "run2_lbl0.174_lbl0.135.json"):
        arms = json.load(open(j(name)))["arms"]
        for arm, by in arms.items():
            if arm == "true":
                continue
            cells = []
            for n in ("1", "3", "9"):
                s = by[n]
                cells.append("%s bodies: loss %+5.1f vs the generator's table, %+5.1f vs 2,000, 0.99 right %.2f%% (worst %.2f)" % (
                    n, 100 * s["minus_true"], 100 * (s["exact"] - ref[int(n)]), 100 * s["precision"], 100 * min(s["precision_each"])))
            print("%-10s %s" % (arm, "; ".join(cells)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
