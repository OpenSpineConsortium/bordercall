"""The chain's study (chain_study.py) on fields small enough for a test, and its records as committed.

    python -m unittest tests.test_schwingcheck_chain_study -v      # from the repository's root, in the PyMC venv

name_stats reads a name right on chain.NAMES and within one level on curve.POSITION's half-step
scale, so a T13 is within one of T12 and of L1, and an L6 of L5 alone. The data axis's tables are
the build-up study's (curve.make_arms at its quick counts) to the bit, the predictive ones widened
by curve.predictive_factor, and a table that is the printed one scores on the axis as `run` scores
the printed one, so every row of the axis is read against `run` on the same fields. A quick run,
axis and speed give every row, the main and axis tables read the rows they name, at one body the
consecutive rule and the gaps rule are one rule, the weights' rows carry the papers' weights on the
stated chain's fields, the speed is timed with every thread pool at one thread, and every record
names the code it was made by. check finds a table that is stale, missing, written twice, followed
by rows of its own or by text with no blank line, or with no record. The committed records: the
README carries their tables, they hold 9 bodies, and each was made by committed code that did not
change while it ran, one commit for the three.
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

    def test_each_measure_set_is_timed_as_a_rule_cut_to_it(self):
        want = {"seven": len(MS.SPINEPS_7), "all": len(MS.pool())}
        for r in self.speed["rows"]:
            self.assertEqual(r["measures"], want[r["subset"]], (r["engine"], r["arm"], r["subset"], r["bodies"]))
        self.assertTrue(self.speed["cut"])

    def test_the_weights_rows_are_the_posterior_at_the_papers_weights(self):
        """Each weights row is what the posterior at those weights gives, computed path by path
        (chain.path_logev, not prepare and logev) on `run`'s fields."""
        pool, subsets, mu, sd, noise, power, nodes = CS.setting()
        mu_e, sd_e = CH.extended_table(mu, sd)
        drawn = CS.draw_all(pool, Q["columns"], Q["widths"])
        rows = {(r["weights"], r["type"], r["bodies"], r["subset"]): r for r in self.main["weight_rows"]}
        self.assertEqual(len(rows), len(self.main["weight_rows"]))
        for name, w in CS.WEIGHT_SETS.items():
            for B in Q["widths"]:
                ch = CH.build(CH.TYPES, w, CH.step_law(), B)
                pa = CH.paths_of(ch)
                t = CS.S.target_offset(B)
                for kind in CH.TYPES:
                    X, names, _, col = drawn[kind, B]
                    ev = CH.path_logev(X, pa, ch, mu_e, sd_e, subsets, noise, power, nodes)
                    for sub, v in ev.items():
                        st = CS.name_stats(CH.body_posterior(CH.posterior(v, pa.log_prior), pa.names, t), names[:, t])
                        st["floored"] = CV.floored_in(X, subsets[sub], power)
                        want, got = CV.rates(st, col), rows[name, kind, B, sub]
                        for key in ("exact", "within_one", "answered", "n_answered", "errors", "set_size"):
                            same(self, got[key], want[key], 0.0, (name, kind, B, sub, key))
                        same(self, got["log_loss"], want["log_loss"], 1e-9, (name, kind, B, sub))

    def test_the_claims_tables_cells_are_the_rows(self):
        key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in self.main["rows"]}
        lines = CS.claims_table(self.main).splitlines()
        self.assertEqual(len(lines), 2 + len(CH.TYPES) * len(self.main["widths"]))
        for line in lines[2:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            kind, B = cells[0].replace("-", "_"), int(cells[1])
            for arm, cell in zip(CS.ARMS, cells[2:]):
                r = key[kind, B, "all", arm]
                self.assertEqual(cell, "%s / %s (%d of %d)" % (CS.pct(r["answered"]), CS.pct(r["precision"], 2),
                                                             r["n_answered"] - r["errors"], r["n_answered"]), (kind, B, arm))

    def test_the_speed_tables_cells_are_the_rows(self):
        key = {(r["engine"], r["arm"], r["subset"], r["bodies"]): r for r in self.speed["rows"]}
        lines = CS.speed_table(self.speed).splitlines()
        for B, line in zip(self.speed["widths"], lines[2:]):
            cells = [c.strip() for c in line.strip("|").split("|")][2:]
            want = [key["prepared", a, k, B] for a in CS.CHAIN_ARMS for k in ("all", "seven")] + \
                   [key["path_logev", "chain", "all", B]]
            self.assertEqual(len(cells), len(want))
            for cell, r in zip(cells, want):
                self.assertEqual(cell, "%s / %s; %s" % (CS._ms(r["median_ms"]), CS._ms(r["max_ms"]), CS._ms(r["batch_ms"])),
                                 (B, r["engine"], r["arm"], r["subset"]))

    def test_the_tables_take_their_labels_from_the_records(self):
        moved = dict(self.main, weights={"typical": 0.8, "six_lumbar": 0.15, "t13": 0.05}, widths=[3])
        lines = CS.weights_table(moved, Q["widths"]).splitlines()
        self.assertTrue(all(line.startswith("| 3 |") for line in lines[2:]), lines)
        self.assertIn("| 3 | all | stated | 0.15, 0.05 |", "\n".join(lines))
        widths = {line.strip("|").split("|")[1].strip() for line in CS.main_table(moved).splitlines()[2:]}
        self.assertEqual(widths, {"3"})
        self.assertEqual(len(CS.claims_table(moved).splitlines()), 2 + len(CH.TYPES))
        one_rule = dict(self.axis, rules=["nominal"])
        lines = CS.axis_table(one_rule, self.main, 3, "all").splitlines()
        self.assertEqual(len(lines), 3 + len(Q["worlds"]))

    def test_every_record_names_the_code_it_was_made_by(self):
        for record in (self.main, self.axis, self.speed):
            self.assertEqual(set(record["made_by"]), {"digests", "git"})
            self.assertEqual(record["changed_during_run"], {})


class CutRule(unittest.TestCase):
    def test_a_rule_cut_to_the_seven_names_as_the_mask_does(self):
        pool, subsets, mu, sd, noise, power, nodes = CS.setting()
        mu_e, sd_e = CH.extended_table(mu, sd)
        drawn = CS.draw_all(pool, 2, (1, 3))
        for B in (1, 3):
            X = drawn["t13", B][0]
            t = CS.S.target_offset(B)
            for arm, ch in CS.chains(B).items():
                pa = CH.paths_of(ch)
                masked = CS.name_middle(CH.prepare(pa, mu_e, sd_e, subsets, noise, power, nodes), X, t)["seven"]
                table = CS.cut("seven", subsets["seven"], mu_e, sd_e, noise, power)
                self.assertEqual(table[0].shape[0], len(MS.SPINEPS_7))
                cut = CS.name_middle(CH.prepare(pa, *table, nodes), X[:, subsets["seven"], :], t)["seven"]
                np.testing.assert_allclose(cut, masked, rtol=0, atol=1e-12, err_msg="%s, %d bodies" % (arm, B))


class AxisOrder(unittest.TestCase):
    def test_the_rows_do_not_depend_on_the_order_the_jobs_finish(self):
        """axis_rows sorts the jobs' results first, so that the log loss, a sum over the fields in
        the order they are pooled, is the same to the bit whatever order the processes finish in."""
        pool = MS.pool()
        worlds = {12: 2}
        tables = CS.axis_tables(pool, worlds)
        CS._AXIS.clear()
        _, subsets, _, _, noise, power, nodes = CS.setting()
        CS._AXIS.update({"tables": tables, "drawn": CS.draw_all(pool, 2, (3,)), "subsets": subsets, "noise": noise,
                         "power": power, "nodes": nodes})
        jobs = [(i, rule, 3) for i in range(len(tables)) for rule in CS.RULES]
        results = [CS.axis_job(j) for j in jobs]
        forward = CS.axis_rows(results, tables, worlds)
        backward = CS.axis_rows(results[::-1], tables, worlds)
        self.assertEqual(len(forward), len(backward))
        for a, b in zip(forward, backward):
            self.assertEqual(set(a), set(b))
            for k in a:
                if isinstance(a[k], float) and np.isnan(a[k]):
                    self.assertTrue(np.isnan(b[k]), k)
                else:
                    self.assertEqual(a[k], b[k], k)


class LoadLoops(unittest.TestCase):
    SCRIPT = """
import json, sys
sys.path.insert(0, %r)
from threadpoolctl import threadpool_limits
from schwingcheck import chain as CH, chain_study as CS, curve as CV
pool, subsets, mu, sd, noise, power, nodes = CS.setting()
mu_e, sd_e = CH.extended_table(mu, sd)
X = CS.draw_all(pool, 2, (1,))["typical", 1][0]
if sys.argv[1] == "first":
    CS.load_loops(subsets, mu_e, sd_e, noise, power, nodes, X)
with threadpool_limits(1):
    if sys.argv[1] == "inside":
        CS.load_loops(subsets, mu_e, sd_e, noise, power, nodes, X)
    print(json.dumps(CV.pools()))
"""

    def pools(self, when):
        import json
        import subprocess
        out = subprocess.run([sys.executable, "-c", self.SCRIPT % ROOT, when], capture_output=True, text=True, check=True)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_compiled_first_every_pool_is_at_one_thread_in_a_fresh_process(self):
        pools = self.pools("first")
        self.assertTrue(pools)
        for pool in pools:
            self.assertEqual(pool["threads"], 1, pool)

    @unittest.skipIf((os.cpu_count() or 1) < 2, "one CPU: every pool has one thread whenever it loads")
    def test_compiled_inside_the_limit_a_pool_escapes_it(self):
        """The reason load_loops runs first: compiled inside the limit, a pool loaded by the
        compile is not held by it."""
        self.assertTrue(any(pool["threads"] > 1 for pool in self.pools("inside")))


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
            with open(readme, "w") as fh:          # with no blank line GitHub draws the note as a row
                fh.write("# A README\n\n" + text.replace(want[first], want[first] + "A note.\n", 1))
            self.assertEqual(CS.check(readme), ["the README's %s has text right after the record's table" % first])
        self.assertIn("the README's %s is not the record's" % first, problems)
        self.assertIn("the README has no block %s" % second, problems)
        self.assertIn("the README writes %s more than once" % third, problems)
        self.assertIn("the README's %s has rows after the record's table" % fourth, problems)
        self.assertIn("the README's chain:gone has no record", problems)
        self.assertEqual(len(problems), 5, problems)

    def test_the_records_must_read_the_same_fields(self):
        main = {"columns_per_type": 100, "fields_per_column": 2, "seeds": [401, 501, 601], "widths": [1, 3, 5, 9]}
        self.assertEqual(CS.consistent({"main": main, "axis": dict(main), "speed": dict(main, widths=[1, 3])}), [])
        problems = CS.consistent({"main": main, "axis": dict(main, seeds=[401, 501, 602], widths=[1, 3]),
                                  "speed": dict(main, columns_per_type=30), "pymc": dict(main, fields_per_column=1)})
        self.assertEqual(len(problems), 4, problems)
        for word in ("axis record's seeds", "axis record's widths", "speed record's columns_per_type",
                     "pymc record's fields_per_column"):
            self.assertTrue(any(word in p for p in problems), (word, problems))


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

    def test_each_was_made_by_committed_code_that_did_not_change(self):
        commits = set()
        for which, record in self.records.items():
            self.assertEqual(record["changed_during_run"], {}, which)
            self.assertFalse(record["made_by"]["git"]["package_changed"], which)
            commits.add(record["made_by"]["git"]["commit"])
        self.assertEqual(len(commits), 1, commits)

    def test_they_read_the_same_fields(self):
        self.assertEqual(CS.consistent(self.records), [])

    def test_the_speed_ran_with_every_pool_at_one_thread_and_cut(self):
        record = self.records["speed"]
        self.assertTrue(record["cut"])
        for pool in record["threads"]:
            self.assertEqual(pool["threads"], 1, pool)

    def test_the_pymc_records_exact_posteriors_are_runs(self):
        """The exact posteriors the PyMC models were set against are chain.py's on `run`'s fields."""
        record = self.records["pymc"]
        pool, subsets, mu, sd, noise, power, nodes = CS.setting()
        mu_e, sd_e = CH.extended_table(mu, sd)
        drawn = CS.draw_all(pool, record["columns_per_type"], record["sampling"]["widths"])
        for r in record["rows"]:
            X, names, col = CS.pymc_fields(drawn, r["type"], r["bodies"], record["sampling"]["fields"])
            t = CS.S.target_offset(r["bodies"])
            self.assertEqual(col.tolist(), r["columns"])
            self.assertEqual([CH.NAMES[n] for n in names[:, t]], r["truth"])
            rule = CH.prepare(CH.paths_of(CS.chains(r["bodies"])["chain"]), mu_e, sd_e, subsets, noise, power, nodes)
            exact = CS.name_middle(rule, X, t)[r["subset"]]
            np.testing.assert_allclose(exact.max(1), r["exact_top"], rtol=0, atol=1e-12)


if __name__ == "__main__":
    unittest.main()
