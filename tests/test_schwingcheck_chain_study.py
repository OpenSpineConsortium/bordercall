"""The chain's study (chain_study.py) on fields small enough for a test, and its records as committed.

    python -m unittest tests.test_schwingcheck_chain_study -v      # from the repository's root, in the PyMC venv

name_stats reads a name right on chain.NAMES and within one level on curve.POSITION's half-step
scale, so a T13 is within one of T12 and of L1, and an L6 of L5 alone. The data axis's tables are
the build-up study's (curve.make_arms at its quick counts) to the bit, the predictive ones widened
by curve.predictive_factor, and a table that is the printed one scores on the axis as `run` scores
the printed one, so every row of the axis is read against `run` on the same fields. A quick run,
axis and speed give every row, their tables read the rows they name, at one body the consecutive
rule and the gaps rule are one rule, the weights' rows differ from the stated chain only by the
prior, the speed is timed with every thread pool at one thread, and every record names the code it
was made by. check finds a table that is stale, missing, written twice, followed by rows of its own,
or with no record. The committed records: the README carries their tables, they hold 9 bodies, the
speed ran at one thread in every pool, and each was made by committed code that did not change while
it ran, one commit for the three.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import chain as CH                              # noqa: E402
from schwingcheck import chain_study as CS                        # noqa: E402
from schwingcheck import curve as CV                              # noqa: E402
from schwingcheck import measures as MS                           # noqa: E402

Q = CS.QUICK


def quiet(*args):
    pass


def same(case, a, b, tol, msg):
    """a and b equal within tol of b's size, or both NaN, as a share with no field answered is."""
    if np.isnan(b):
        case.assertTrue(np.isnan(a), msg)
    else:
        case.assertLessEqual(abs(a - b), tol * max(1.0, abs(b)), msg)


class NameStats(unittest.TestCase):
    def test_within_one_is_read_on_the_half_step_scale(self):
        cases = [("T13", "T12", False, True), ("T13", "L1", False, True), ("T13", "L2", False, False),
                 ("T13", "T11", False, False), ("L6", "L5", False, True), ("L6", "L4", False, False),
                 ("T12", "L1", False, True), ("L1", "L1", True, True)]
        n = len(CH.NAMES)
        post = np.full((len(cases), n), 1e-6)
        for i, (_, said, _, _) in enumerate(cases):
            post[i, CH.NAME_INDEX[said]] = 1.0
        post /= post.sum(1, keepdims=True)
        truth = np.array([CH.NAME_INDEX[t] for t, _, _, _ in cases])
        stats = CS.name_stats(post, truth)
        for i, (t, said, hit, within) in enumerate(cases):
            self.assertEqual(bool(stats["hit"][i]), hit, (t, said))
            self.assertEqual(bool(stats["within"][i]), within, (t, said))
        np.testing.assert_allclose(stats["logp"], np.log(post[np.arange(len(cases)), truth]))
        self.assertTrue(np.all(stats["size"] == 1))
        np.testing.assert_allclose(stats["top"], post.max(1))


class DataAxis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool = MS.pool()

    def test_the_tables_are_the_build_up_studys(self):
        names = list(CV.subsets(self.pool, list(range(len(self.pool)))))
        arms = CV.make_arms(self.pool, names, quick=True)
        worlds = CV.QUICK_COUNTS["worlds"]
        tables = CS.axis_tables(self.pool, worlds)
        self.assertEqual(len(tables), sum(worlds.values()))
        for people, w, emu, esd in tables:
            for rule, fac in (("nominal", 1.0), ("predictive", CV.predictive_factor(people))):
                arm = next(a for a in arms if a.name == "people-%d-%s" % (people, rule) and a.world == w)
                self.assertTrue(np.array_equal(arm.mu, emu), (people, w, rule))
                self.assertTrue(np.array_equal(arm.sd, esd * fac), (people, w, rule))

    def test_the_printed_table_scores_as_run_scores_it(self):
        mu, sd = MS.arrays(self.pool)
        printed = [(12, 0, mu, sd), (12, 1, mu, sd)]
        with mock.patch.object(CS, "axis_tables", return_value=printed):
            ax = CS.axis(Q["columns"], (3,), {12: 2}, processes=1, log=quiet)
        main = CS.run(Q["columns"], (3,))
        want = {(r["type"], r["arm"], r["subset"]): r for r in main["rows"]}
        rows = [r for r in ax["rows"] if r["rule"] == "nominal"]
        self.assertEqual(len(rows), len(want))
        for r in rows:
            w = want[r["type"], r["arm"], r["subset"]]
            for key in ("exact", "within_one", "answered", "precision", "set_size"):     # shares: one count over twice the fields
                same(self, r[key], w[key], 0.0, (r["type"], r["arm"], r["subset"], key))
            same(self, r["log_loss"], w["log_loss"], 1e-12, (r["type"], r["arm"], r["subset"]))   # a mean summed in another order
            self.assertEqual(r["n_answered"], 2 * w["n_answered"])


class QuickStudy(unittest.TestCase):
    """One quick run, axis and speed, made once for the tests that read them."""

    @classmethod
    def setUpClass(cls):
        cls.main = CS.run(Q["columns"], Q["widths"])
        cls.axis = CS.axis(Q["columns"], Q["widths"], Q["worlds"], processes=2, log=quiet)
        cls.speed = CS.speed(Q["columns"], Q["speed_widths"], Q["speed"], Q["reference"], log=quiet)

    def test_every_row_is_there(self):
        n_types, n_widths, n_subsets = len(CH.TYPES), len(Q["widths"]), len(CS.SUBSETS)
        self.assertEqual(len(self.main["rows"]), n_types * n_widths * len(CS.ARMS) * n_subsets)
        self.assertEqual(len(self.main["weight_rows"]), len(CS.WEIGHT_SETS) * n_types * n_widths * n_subsets)
        self.assertEqual(len(self.axis["rows"]),
                         len(Q["worlds"]) * len(CS.RULES) * n_types * n_widths * len(CS.ARMS) * n_subsets)
        self.assertEqual(len(self.speed["rows"]),
                         len(Q["speed_widths"]) * (len(CS.CHAIN_ARMS) * n_subsets + n_subsets))
        for r in self.main["rows"]:
            self.assertEqual(r["n_fields"], Q["columns"] * CS.PER_COLUMN)
        for r in self.axis["rows"]:
            self.assertEqual(r["n_fields"], Q["worlds"][r["people"]] * Q["columns"] * CS.PER_COLUMN)

    def test_at_one_body_consecutive_and_gaps_are_one_rule(self):
        key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in self.main["rows"]}
        for kind in CH.TYPES:
            for sub in CS.SUBSETS:
                a, b = key[kind, 1, sub, "consecutive"], key[kind, 1, sub, "gaps"]
                for stat in ("exact", "answered", "set_size"):
                    self.assertEqual(a[stat], b[stat], (kind, sub, stat))
                self.assertAlmostEqual(a["log_loss"], b["log_loss"], places=12)

    def test_the_weights_rows_are_the_chain_at_other_priors(self):
        sets = self.main["weight_sets"]
        self.assertEqual(set(sets), set(CS.WEIGHT_SETS))
        for name, w in sets.items():
            self.assertAlmostEqual(sum(w.values()), 1.0, places=12)
            self.assertEqual(tuple(w[k] for k in CH.TYPES), CS.WEIGHT_SETS[name])
        stated = {(r["type"], r["bodies"], r["subset"]): r for r in self.main["rows"] if r["arm"] == "chain"}
        for r in self.main["weight_rows"]:
            self.assertEqual(r["n_fields"], stated[r["type"], r["bodies"], r["subset"]]["n_fields"])
        lines = CS.weights_table(self.main, Q["widths"]).splitlines()
        self.assertEqual(len(lines), 2 + len(Q["widths"]) * len(CS.SUBSETS) * (1 + len(CS.WEIGHT_SETS)))
        B = Q["widths"][0]                                # the table's first row: the narrowest width, all 32, stated
        r = stated["typical", B, "all"]
        self.assertTrue(lines[2].startswith("| %d | all | stated | 0.05, 0.05 | %s (%s) / %s |"
                                            % (B, CS.pct(r["exact"]), CS.pct(r["exact_se"]), CS.pct(r["precision"], 2))),
                        lines[2])
        other = {(r["weights"], r["type"], r["bodies"], r["subset"]): r for r in self.main["weight_rows"]}
        B = Q["widths"][-1]
        row = next(line for line in lines if line.startswith("| %d | seven | papers, low |" % B))
        cells = [c.strip() for c in row.strip("|").split("|")][4:]
        for kind, cell in zip(CH.TYPES, cells):
            r = other["papers, low", kind, B, "seven"]
            self.assertEqual(cell, "%s (%s) / %s" % (CS.pct(r["exact"]), CS.pct(r["exact_se"]), CS.pct(r["precision"], 2)))

    def test_the_tables_read_the_rows_they_name(self):
        key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in self.main["rows"]}
        lines = CS.main_table(self.main).splitlines()
        self.assertEqual(len(lines), 2 + len(CH.TYPES) * len(Q["widths"]) * len(CS.SUBSETS))
        row = next(line for line in lines if line.startswith("| t13 | 3 | all |"))
        cells = [c.strip() for c in row.strip("|").split("|")][3:]
        for arm, cell in zip(CS.ARMS, cells):
            r = key["t13", 3, "all", arm]
            self.assertEqual(cell, "%s (%s)" % (CS.pct(r["exact"]), CS.pct(r["exact_se"])))
        lines = CS.axis_table(self.axis, self.main, 3, "all").splitlines()
        self.assertTrue(lines[2].startswith("| as printed | - | 1 | "), lines[2])
        self.assertEqual(len(lines), 3 + len(Q["worlds"]) * len(CS.RULES))
        ax = {(r["people"], r["rule"], r["type"], r["bodies"], r["subset"], r["arm"]): r for r in self.axis["rows"]}
        row = next(line for line in lines if line.startswith("| 12 | nominal |"))
        x, ref = ax[12, "nominal", "typical", 3, "all", "chain"], key["typical", 3, "all", "chain"]
        cell = [c.strip() for c in row.strip("|").split("|")][3]
        self.assertEqual(cell, "%s (%s / %s), %+.1f" % (CS.pct(x["exact"]), CS.pct(x["exact_se"]),
                                                        CS.pct(x["exact_se_tables"]), 100 * (x["exact"] - ref["exact"])))
        lines = CS.speed_table(self.speed).splitlines()
        self.assertEqual(len(lines), 2 + len(Q["speed_widths"]))
        for B, line in zip(Q["speed_widths"], lines[2:]):
            paths = len(CH.paths_of(CS.chains(B)["chain"]))
            self.assertTrue(line.startswith("| %d | %s |" % (B, "{:,}".format(paths))), line)

    def test_the_speed_ran_at_one_thread(self):
        self.assertTrue(self.speed["threads"])
        for pool in self.speed["threads"]:
            self.assertEqual(pool["threads"], 1, pool)

    def test_every_record_names_the_code_it_was_made_by(self):
        for record in (self.main, self.axis, self.speed):
            self.assertEqual(set(record["made_by"]), {"digests", "git"})
            self.assertEqual(record["changed_during_run"], {})


class Check(unittest.TestCase):
    def test_check_finds_a_stale_a_missing_a_doubled_and_a_stray_table(self):
        want = CS.tables()
        text = "".join("<!-- %s -->\n%s<!-- /%s -->\n\n" % (k, v, k) for k, v in want.items())
        with tempfile.TemporaryDirectory() as tmp:
            readme = os.path.join(tmp, "README.md")
            with open(readme, "w") as fh:
                fh.write("# A README\n\n" + text + "More prose.\n")
            self.assertEqual(CS.check(readme), [])
            first, second, third, fourth = list(want)[:4]
            stale = text.replace(want[first], want[first].replace("|", "| ", 1), 1)
            stale = stale.replace("<!-- %s -->" % second, "<!-- chain:gone -->", 1)
            stale = stale.replace("<!-- /%s -->" % second, "<!-- /chain:gone -->", 1)
            stale += "<!-- %s -->\n%s<!-- /%s -->\n" % (third, want[third], third)
            stale = stale.replace(want[fourth], want[fourth] + "| a row | left over |\n\nA note.\n", 1)
            with open(readme, "w") as fh:
                fh.write(stale)
            problems = CS.check(readme)
            with open(readme, "w") as fh:          # a note below a table is the table's, as the README's are
                fh.write("# A README\n\n" + text.replace(want[first], want[first] + "\nA note.\n", 1))
            self.assertEqual(CS.check(readme), [])
        self.assertIn("the README's %s is not the record's" % first, problems)
        self.assertIn("the README has no block %s" % second, problems)
        self.assertIn("the README writes %s more than once" % third, problems)
        self.assertIn("the README's %s has rows after the record's table" % fourth, problems)
        self.assertIn("the README's chain:gone has no record", problems)
        self.assertEqual(len(problems), 5, problems)


class CommittedRecords(unittest.TestCase):
    """The records of 28 October 2026 as committed in records/chain-2026-10-28/."""

    @classmethod
    def setUpClass(cls):
        cls.records = {k: CS.load(k) for k in CS.RECORDS}

    def test_the_readme_carries_their_tables(self):
        self.assertEqual(CS.check(), [])

    def test_they_hold_9_bodies(self):
        for which in ("main", "axis"):
            self.assertIn(9, self.records[which]["widths"], which)
            self.assertTrue(any(r["bodies"] == 9 for r in self.records[which]["rows"]), which)
        self.assertEqual(self.records["speed"]["widths"], list(CS.SPEED_WIDTHS))
        self.assertEqual(self.records["main"]["columns_per_type"], 100)
        self.assertEqual(self.records["axis"]["worlds"], {str(k): v for k, v in CV.WORLDS.items()})

    def test_the_speed_ran_at_one_thread(self):
        self.assertTrue(self.records["speed"]["threads"])
        for pool in self.records["speed"]["threads"]:
            self.assertEqual(pool["threads"], 1, pool)

    def test_each_was_made_by_committed_code_that_did_not_change(self):
        commits = set()
        for which, record in self.records.items():
            self.assertEqual(record["changed_during_run"], {}, which)
            self.assertFalse(record["made_by"]["git"]["package_changed"], which)
            commits.add(record["made_by"]["git"]["commit"])
        self.assertEqual(len(commits), 1, commits)


if __name__ == "__main__":
    unittest.main()
