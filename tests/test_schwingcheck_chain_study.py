"""The chain's study (chain_study.py) on fields small enough for a test, and its records as committed.

    python -m unittest tests.test_schwingcheck_chain_study -v      # from the repository's root, in the PyMC venv

name_stats reads a name right on chain.NAMES and within one level on curve.POSITION's half-step
scale, so a T13 is within one of T12 and of L1, and an L6 of L5 alone. The data axis's tables are
the build-up study's (curve.make_arms at its quick counts) to the bit, the predictive ones widened
by curve.predictive_factor, and a table that is the printed one scores on the axis as `run` scores
the printed one, so every row of the axis is read against `run` on the same fields. A quick run,
axis, speed and PyMC comparison give every row, the main and axis tables read the rows they name,
at one body the consecutive rule and the gaps rule are one rule, the weights' rows carry the papers'
weights on the stated chain's fields and are the chain's posterior at those weights, computed again,
the claims and speed tables' cells are their rows', every table takes its labels (widths, weights,
rules) from its record, each measure set is timed as a rule cut to it, and every record names the
code it was made by. A rule cut to the seven names as the rule for all 32 with the rest masked out,
within 1e-12. The axis's rows are the same to the bit whatever order its jobs finish in. load_loops,
run first in a fresh process, leaves every pool at one thread while the speed's own work runs
inside the limit and compiles every layout of the loops the speed times, while without it that
work loads a pool the limit does not hold; and `run`, `axis` on two processes, `speed` and `pymc`,
each run alone in a fresh process, where nothing the test runner did before has loaded a pool,
record every pool at one thread. The PyMC table counts a field under the naming model's NUTS test
only where it passes all three of that test's checks. check finds a table that is stale, missing, written
twice, followed by rows of its own or by text with no blank line, or with no record, and records
that do not read the same columns, fields a column and seeds. The committed records: the README
carries their tables, they hold 9 bodies, each was made by committed code that did not change while
it ran, one commit for the four, they read the same fields, the speed timed each measure set on
its own measures with every pool at one thread, and the exact posteriors the PyMC models were set
against are chain.py's on `run`'s fields, with every thread pool at one thread. `pymc` at QUICK's
sampling gives every row its table reads, holds each model to the cut rule's exact posterior on
`run`'s fields and names pymc-extras' version.
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


class QuickPyMC(unittest.TestCase):
    """`pymc` at QUICK's sampling, on the seven, two fields of each type, each sampled alone, in
    this process."""

    @classmethod
    def setUpClass(cls):
        cls.record = CS.pymc_compare(Q["columns"], Q["pymc"], processes=1, subsets=("seven",), log=quiet)

    def test_every_row_is_there_and_the_table_reads_it(self):
        rows = {(r["type"], r["bodies"], r["subset"], r["model"]) for r in self.record["rows"]}
        want = {(k, B, "seven", m) for k in CH.TYPES for B in Q["pymc"]["widths"] for m in CS.PYMC_MODELS}
        self.assertEqual(rows, want)
        lines = CS.pymc_table(self.record).splitlines()
        self.assertEqual(len(lines), 2 + len(want))
        for r in self.record["rows"]:
            F = Q["pymc"]["fields"]
            for key in ("gap", "gap_mcse", "gap_in_errors", "same_name", "exact_top", "model_top", "rhat", "steps"):
                self.assertEqual(len(r[key]), F, key)
            self.assertTrue(all(s >= 1 for s in r["steps"]), r["steps"])
            self.assertTrue(np.all(np.isfinite(r["gap"])) and np.all(np.isfinite(r["rhat"])))
            self.assertTrue(np.all(np.asarray(r["gap_mcse"]) >= 0))
            self.assertLessEqual(r["fields_within"], F)
            self.assertEqual(len(r["within_each"]), F)
            self.assertEqual(sum(r["within_each"]), r["fields_within"])
            self.assertLessEqual(CS.naming_test(r), r["fields_within"])

    def test_the_exact_posteriors_are_the_cut_rules(self):
        pool, subsets, mu, sd, noise, power, nodes = CS.setting()
        mu_e, sd_e = CH.extended_table(mu, sd)
        drawn = CS.draw_all(pool, Q["columns"], Q["pymc"]["widths"])
        for r in self.record["rows"]:
            X, _, col = CS.pymc_fields(drawn, r["type"], r["bodies"], Q["pymc"]["fields"])
            self.assertEqual(col.tolist(), r["columns"])
            rule = CH.prepare(CH.paths_of(CS.chains(r["bodies"])["chain"]), mu_e, sd_e, subsets, noise, power, nodes)
            exact = CS.name_middle(rule, X, CS.S.target_offset(r["bodies"]))["seven"]
            np.testing.assert_allclose(exact.max(1), r["exact_top"], rtol=0, atol=1e-12)

    def test_every_job_lists_its_pools_and_pymc_extras_is_named(self):
        self.assertEqual(len(self.record["threads"]), len(CH.TYPES) * len(Q["pymc"]["widths"]))
        for job in self.record["threads"]:
            self.assertTrue(job["pools"], job)
        self.assertNotEqual(self.record["versions"]["pymc-extras"], "not installed")


class NamingTest(unittest.TestCase):
    ROW = {"type": "typical", "bodies": 3, "subset": "all", "model": "sampled", "fields_within": 4,
           "within_each": [True, True, True, True], "same_name": [True] * 4, "gap": [1e-10, 0.01, 1e-9, 0.002],
           "gap_mcse": [1e-11, 0.005, 1e-10, 0.001], "gap_in_errors": [6.7, 2.0, 1.0, 1.0],
           "rhat": [1.0, 1.01, 1.54, 1.019], "steps": [7.0] * 4, "divergences": 0, "sample_s": 1.0}

    def test_a_field_passes_only_where_it_passes_all_three_checks(self):
        """Over five errors at a name above 0.05, however small the gap, or an R-hat of 1.02 or
        more, fails the naming model's test though every name is within five errors plus 0.001;
        and the table prints the largest gap in errors as it is."""
        self.assertEqual(CS.naming_test(self.ROW), 2)
        row = dict(self.ROW, within_each=[True, False, True, True], fields_within=3)
        self.assertEqual(CS.naming_test(row), 1)
        cells = CS.pymc_table({"rows": [self.ROW]}).splitlines()[2].split(" | ")
        self.assertEqual(cells[4:6], ["4 of 4", "2 of 4"])
        self.assertEqual(cells[8], "6.7")

    def test_a_record_with_no_fields_own_within_is_read_only_where_all_are_within(self):
        row = {k: v for k, v in self.ROW.items() if k != "within_each"}
        self.assertEqual(CS.naming_test(row), 2)
        with self.assertRaises(ValueError):
            CS.naming_test(dict(row, fields_within=3))


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
        the order they are pooled, is the same to the bit whatever order the processes finish in.
        Three tables on three columns: at two tables on two columns, numpy's pairwise sum adds
        the same two halves last in either order, and the rows came out the same with no sort,
        while here, without it, reversing the results changed the log loss in 24 of the 48 rows
        and the predicted error in 8 more."""
        pool = MS.pool()
        worlds = {12: 3}
        tables = CS.axis_tables(pool, worlds)
        CS._AXIS.clear()
        _, subsets, _, _, noise, power, nodes = CS.setting()
        CS._AXIS.update({"tables": tables, "drawn": CS.draw_all(pool, 3, (3,)), "subsets": subsets, "noise": noise,
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
    THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "GOTO_NUM_THREADS", "MKL_NUM_THREADS",
               "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "NUMBA_NUM_THREADS")
    SCRIPT = """
import json, sys
sys.path.insert(0, %r)
from threadpoolctl import threadpool_limits
from schwingcheck import chain as CH, chain_study as CS, curve as CV
pool, subsets, mu, sd, noise, power, nodes = CS.setting()
mu_e, sd_e = CH.extended_table(mu, sd)
X = CS.draw_all(pool, 2, (1,))["typical", 1][0]

def name_with_every_rule(B, X):
    for sub in CS.SUBSETS:
        table, Xs = CS.cut(sub, subsets[sub], mu_e, sd_e, noise, power), X[:, subsets[sub], :]
        for rule in [CH.prepare(CH.paths_of(ch), *table, nodes) for ch in CS.chains(B).values()]:
            CS.name_middle(rule, Xs[:1], 0)
            CS.name_middle(rule, Xs, 0)
if sys.argv[1] == "first":
    CS.load_loops(subsets, mu_e, sd_e, noise, power, nodes, X)
if sys.argv[1] == "layouts":
    CS.load_loops(subsets, mu_e, sd_e, noise, power, nodes, X)
    before = [len(k.signatures) for k in CH._kernels()]
    for B in (1, 3):
        name_with_every_rule(B, CS.draw_all(pool, 2, (B,))["typical", B][0])
    print(json.dumps([before, [len(k.signatures) for k in CH._kernels()]]))
    raise SystemExit
with threadpool_limits(1):
    name_with_every_rule(1, X)
    print(json.dumps(CV.pools()))
"""

    def pools(self, when):
        import json
        import subprocess
        env = {k: v for k, v in os.environ.items() if k not in self.THREADS}     # each pool at its own default
        out = subprocess.run([sys.executable, "-c", self.SCRIPT % ROOT, when], capture_output=True, text=True, check=True,
                             env=env)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def test_compiled_first_every_pool_is_at_one_thread_in_a_fresh_process(self):
        """speed's own work, every rule it times naming one field and a batch, done inside the
        limit after load_loops, leaves every pool at one thread."""
        pools = self.pools("first")
        self.assertTrue(pools)
        for pool in pools:
            self.assertEqual(pool["threads"], 1, pool)

    def test_it_compiles_every_layout_the_speed_times(self):
        """A rule cut to one measure set hands the loops arrays of another layout than the rule of
        both sets, and Numba compiles a loop once a layout: after load_loops, naming one field and
        a batch with every rule `speed` times compiles nothing more, so no compile falls inside
        the thread limit."""
        before, after = self.pools("layouts")
        self.assertEqual(before, after)

    @unittest.skipIf(len(os.sched_getaffinity(0)) < 2, "one usable CPU: every pool has one thread whenever it loads")
    def test_without_load_loops_a_pool_escapes_the_limit(self):
        """The reason load_loops runs first: the same work with nothing compiled before the limit
        loads a pool the limit does not hold."""
        self.assertTrue(any(pool["threads"] > 1 for pool in self.pools("none")))


class FreshRecords(unittest.TestCase):
    """Each command's own work, run alone in a fresh process at a test's counts, records every
    pool at one thread. In the test runner's own process a test run before it has compiled the
    chain's loops and loaded scipy's BLAS outside any limit, so a limit entered later holds every
    pool whether or not the command compiles first; a fresh process has loaded nothing, so a
    command that entered its limit before compiling would record a pool at every thread (LoadLoops
    shows such a pool escapes)."""
    SCRIPT = """
import json, sys
sys.path.insert(0, %r)
from schwingcheck import chain_study as CS
quiet = lambda *a: None
which = sys.argv[1]
if which == "run":
    print(json.dumps(CS.run(2, (1,))["threads"]))
elif which == "axis":
    print(json.dumps([p for job in CS.axis(2, (1,), {12: 1}, processes=2, log=quiet)["threads"] for p in job]))
elif which == "speed":
    counts = {"calls": 1, "batch": 2, "batches": 1}
    print(json.dumps(CS.speed(2, (1,), counts, counts, log=quiet)["threads"]))
elif which == "pymc":
    sampling = {"widths": (3,), "fields": 1, "draws": 20, "tune": 20, "chains": 2, "batches": 2, "seed": 701}
    print(json.dumps([p for job in CS.pymc_compare(2, sampling, processes=1, subsets=("seven",), log=quiet)["threads"]
                      for p in job["pools"]]))
"""

    def pools(self, which):
        import json
        import subprocess
        env = {k: v for k, v in os.environ.items() if k not in LoadLoops.THREADS}
        out = subprocess.run([sys.executable, "-c", self.SCRIPT % ROOT, which], capture_output=True, text=True,
                             check=True, env=env)
        return json.loads(out.stdout.strip().splitlines()[-1])

    def assert_one_thread(self, which):
        pools = self.pools(which)
        self.assertTrue(pools, which)
        for pool in pools:
            self.assertEqual(pool["threads"], 1, (which, pool))

    def test_run(self):
        self.assert_one_thread("run")

    def test_axis_on_two_processes(self):
        self.assert_one_thread("axis")

    def test_speed(self):
        self.assert_one_thread("speed")

    def test_pymc(self):
        self.assert_one_thread("pymc")


class Check(unittest.TestCase):
    def test_check_finds_a_stale_a_missing_a_doubled_and_a_stray_table(self):
        want = CS.tables()
        text = "".join("<!-- %s -->\n%s<!-- /%s -->\n\n" % (k, v, k) for k, v in want.items())
        with tempfile.TemporaryDirectory() as tmp:
            readme = os.path.join(tmp, "README.md")
            with open(readme, "w") as fh:
                fh.write("# A README\n\n" + text + "More prose.\n")
            self.assertEqual(CS.check(readme, records=False), [])
            first, second, third, fourth = list(want)[:4]
            stale = text.replace(want[first], want[first].replace("|", "| ", 1), 1)
            stale = stale.replace("<!-- %s -->" % second, "<!-- chain:gone -->", 1)
            stale = stale.replace("<!-- /%s -->" % second, "<!-- /chain:gone -->", 1)
            stale += "<!-- %s -->\n%s<!-- /%s -->\n" % (third, want[third], third)
            stale = stale.replace(want[fourth], want[fourth] + "| a row | left over |\n\nA note.\n", 1)
            with open(readme, "w") as fh:
                fh.write(stale)
            problems = CS.check(readme, records=False)
            with open(readme, "w") as fh:          # a note below a table is the table's, as the README's are
                fh.write("# A README\n\n" + text.replace(want[first], want[first] + "\nA note.\n", 1))
            self.assertEqual(CS.check(readme, records=False), [])
            with open(readme, "w") as fh:          # with no blank line GitHub draws the note as a row
                fh.write("# A README\n\n" + text.replace(want[first], want[first] + "A note.\n", 1))
            self.assertEqual(CS.check(readme, records=False),
                             ["the README's %s has text right after the record's table" % first])
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
        want = {"seven": len(MS.SPINEPS_7), "all": len(MS.pool())}
        for r in record["rows"]:
            self.assertEqual(r["measures"], want[r["subset"]], (r["engine"], r["arm"], r["subset"], r["bodies"]))
        for pool in record["threads"]:
            self.assertEqual(pool["threads"], 1, pool)

    def test_the_pymc_record_ran_with_every_pool_at_one_thread(self):
        record = self.records["pymc"]
        self.assertIn("pymc-extras", record["versions"])
        for job in record["threads"]:
            for pool in job["pools"]:
                self.assertEqual(pool["threads"], 1, (job["type"], pool))

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
