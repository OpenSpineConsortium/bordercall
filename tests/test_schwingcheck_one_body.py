"""The one-vertebra evaluation (one_body.py) on a few columns, and its record as committed.

    python -m unittest tests.test_schwingcheck_one_body -v      # from the repository's root, in the PyMC venv

The one-body rule is the chain at one body: its posterior over the names, under every prior, is
chain.logev's at one body within 1e-12, and under the typical prior it is step d's rule (rule.name)
at one body. The prior over the names sums to one and puts nothing on an L6 or a T13 for the typical
column. The heights are centred on the specimens' mean with their spread, and the sizes on the
heights with the residual, keeping the generator's spread of size whole, so the rule with the size
unknown is still the generator's posterior; each size rule takes the mean and SD it says, and its
nodes hold its prior whole and centre it where the height puts it. Every body is a field of its
own under its own name, each type is drawn at its patients' sizes, and a given size multiplies every
length by its power. A prefix of the whole order is all 32. A coarse claim holds a name by where it
sits on curve.POSITION, as the coarse study's claim_truth holds C3 to L5, and a claim's rates count
what they say. A quick run gives every row, level and claim its tables read, a row is its own rule
scored afresh on its own fields, and its tables' cells are the rows'; check finds the README's
one-body tables. The figures, drawn twice, are the same files, and their CSVs hold the record's
numbers. The committed record: the README carries its tables, it was made by committed code that did
not change while it ran, and its figures, images included, are byte for byte what the code draws
from it.
"""
from __future__ import annotations

import csv
import math
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import chain as CH                              # noqa: E402
from schwingcheck import chain_study as CS                        # noqa: E402
from schwingcheck import columns as CL                            # noqa: E402
from schwingcheck import covariates as CO                         # noqa: E402
from schwingcheck import curve as CV                              # noqa: E402
from schwingcheck import figures as FG                            # noqa: E402
from schwingcheck import one_body as OB                           # noqa: E402
from schwingcheck import rule as R                                # noqa: E402

STEMS = ("one_body_levels", "one_body_buildup", "one_body_coarse", "one_body_size")
EXTENSIONS = (".pdf", ".png", ".csv", ".caption.txt")


def quiet(*args):
    pass


def setting():
    pool, subsets, mu, sd, noise, power, nodes = CS.setting()
    mu_e, sd_e = CH.extended_table(mu, sd)
    return pool, subsets, mu_e, sd_e, noise, power, nodes


class TheRule(unittest.TestCase):
    def test_it_is_the_chain_at_one_body_under_every_prior(self):
        pool, subsets, mu_e, sd_e, noise, power, nodes = setting()
        for ti, kind in enumerate(CH.TYPES):
            cols = CV.draw_pool(pool, kind, 11 + ti, 21 + ti, 2)
            X, names, _ = OB.every_body(cols)
            X[3, 0, 0] = np.nan                       # a value not read
            ev = OB.column_logev(X, nodes, mu_e, sd_e, noise, power, subsets)
            for prior in OB.PRIORS:
                if prior == "typical":
                    ch = CH.build(("typical",), (1.0,), (1.0,), 1)
                else:
                    w = None if prior == "chain" else OB.CS.WEIGHT_SETS[prior]
                    ch = CH.build(CH.TYPES, w, CH.step_law(), 1)
                rule = CH.prepare(CH.paths_of(ch), mu_e, sd_e, subsets, noise, power, nodes)
                want = CS.name_middle(rule, X, 0)
                with np.errstate(divide="ignore"):
                    lp = np.log(OB.prior_over_names(prior))
                for k in subsets:
                    got = R.posterior(ev[k], lp)
                    np.testing.assert_allclose(got, want[k], rtol=0, atol=1e-12, err_msg="%s, %s, %s" % (kind, prior, k))

    def test_the_typical_prior_is_step_ds_rule_at_one_body(self):
        pool, subsets, mu, sd, noise, power, nodes = CS.setting()
        mu_e, sd_e = CH.extended_table(mu, sd)
        X, _, _ = OB.every_body(CV.draw_pool(pool, "typical", 13, 23, 2))
        ev = OB.column_logev(X, nodes, mu_e, sd_e, noise, power, subsets)
        with np.errstate(divide="ignore"):
            lp = np.log(OB.prior_over_names("typical"))
        step_d = R.name(X, (0,), mu, sd, R.SYNTH, subsets=subsets, noise=noise, power=power, nodes=nodes)
        n = len(CH.type_levels("typical"))
        for k in subsets:
            got = R.posterior(ev[k], lp)
            np.testing.assert_array_equal(got[:, n:], 0.0)
            np.testing.assert_allclose(got[:, :n], step_d[k], rtol=0, atol=1e-12, err_msg=k)

    def test_the_prior_over_names_sums_to_one(self):
        for prior in OB.PRIORS:
            p = OB.prior_over_names(prior)
            self.assertAlmostEqual(p.sum(), 1.0, places=14)
            self.assertTrue(np.all(p >= 0))
        typical = OB.prior_over_names("typical")
        self.assertEqual(typical[CH.NAME_INDEX["L6"]], 0.0)
        self.assertEqual(typical[CH.NAME_INDEX["T13"]], 0.0)
        chain = OB.prior_over_names("chain")
        self.assertAlmostEqual(chain[CH.NAME_INDEX["L6"]], CH.WEIGHTS["six_lumbar"] / len(CH.type_levels("six_lumbar")))
        self.assertAlmostEqual(chain[CH.NAME_INDEX["T13"]], CH.WEIGHTS["t13"] / len(CH.type_levels("t13")))

    def test_a_prefix_of_the_whole_order_is_all_32(self):
        pool, subsets, mu_e, sd_e, noise, power, nodes = setting()
        order = OB.build_up_order()
        _, order_idx = OB.subsets_of(pool, order)
        self.assertEqual(sorted(order_idx), subsets["all"])
        X, _, _ = OB.every_body(CV.draw_pool(pool, "typical", 5, 6, 1))
        ev = OB.column_logev(X, nodes, mu_e, sd_e, noise, power, subsets, order_idx)
        np.testing.assert_allclose(ev["first %d" % len(order)], ev["all"], rtol=1e-12, atol=1e-9)
        np.testing.assert_allclose(ev["first 1"], R.log_evidence(R.loglik(X, (0,), mu_e, sd_e, R.SYNTH, sizes=nodes[0],
                                                                           noise=noise, power=power), nodes[1],
                                                                  [order_idx[0]]), rtol=0, atol=1e-9)


class TheSize(unittest.TestCase):
    def test_the_sizes_keep_the_generators_spread(self):
        height, size, resid = OB.draw_sizes(200_000, 3)
        spread = OB.specimen_log_height_sd()
        self.assertAlmostEqual(spread ** 2 + resid ** 2, R.SYNTH["scale_sd"] ** 2, places=15)
        log_s = np.log(size)
        se = R.SYNTH["scale_sd"] / math.sqrt(len(log_s))
        self.assertLess(abs(log_s.mean()), 5 * se)
        self.assertLess(abs(log_s.std() - R.SYNTH["scale_sd"]), 5 * se)
        self.assertLess(abs(np.std(np.log(size / height)) - resid), 5 * resid / math.sqrt(len(log_s)) * 2)
        dlogh = np.log(height / CO.HEIGHT_REF)
        self.assertLess(abs(dlogh.mean()), 5 * spread / math.sqrt(len(dlogh)))
        self.assertLess(abs(np.std(dlogh) - spread), 5 * spread / math.sqrt(len(dlogh)))
        self.assertLess(abs(np.mean(log_s - dlogh)), 5 * resid / math.sqrt(len(dlogh)))

    def test_each_rule_takes_the_size_as_it_says(self):
        height, size, resid = OB.draw_sizes(5, 4)
        priors = OB.size_priors(height, size, resid)
        self.assertEqual(set(priors), set(OB.SIZES))
        mean, sd = CO.CovariateModel().size_prior([CO.Covariates(height_cm=float(h)) for h in height])
        np.testing.assert_array_equal(priors["height, model"][0], mean)
        np.testing.assert_array_equal(priors["height, model"][1], sd)
        np.testing.assert_array_equal(priors["unknown"][0], 0.0)
        np.testing.assert_array_equal(priors["unknown"][1], R.SYNTH["scale_sd"])
        np.testing.assert_allclose(priors["height, generator"][0], np.log(height / CO.HEIGHT_REF))
        np.testing.assert_array_equal(priors["height, generator"][1], resid)
        np.testing.assert_array_equal(priors["size given"][1], 0.0)
        np.testing.assert_allclose(np.exp(priors["size given"][0]), size)

    def test_the_nodes_hold_the_prior_where_the_height_puts_it(self):
        for mean, sd in ((0.0, 0.07), (0.2, 0.08), (-0.3, 0.0567)):
            s, logw = OB.nodes_of(mean, sd)
            w = np.exp(logw)
            self.assertAlmostEqual(w.sum(), 1.0, places=12)
            self.assertAlmostEqual(float((w * np.log(s)).sum()), mean, places=12)
            self.assertAlmostEqual(float(np.sqrt((w * (np.log(s) - mean) ** 2).sum())), sd, places=6)
        s, logw = OB.nodes_of(0.1, 0.0)
        self.assertEqual(s.tolist(), [math.exp(0.1)])
        self.assertEqual(logw.tolist(), [0.0])


class TheFields(unittest.TestCase):
    def test_every_body_is_its_own_field_under_its_own_name(self):
        pool = CS.setting()[0]
        for kind in CH.TYPES:
            cols = CV.draw_pool(pool, kind, 31, 41, 3)
            X, names, col = OB.every_body(cols)
            i = 0
            for c in range(len(cols)):
                for p, level in enumerate(cols.levels[c]):
                    np.testing.assert_array_equal(X[i, :, 0], cols.values[c, p, :])
                    self.assertEqual((names[i], col[i]), (CH.NAME_INDEX[level], c))
                    i += 1
            self.assertEqual(i, len(names))

    def test_each_type_is_drawn_at_its_patients_sizes(self):
        pool = CS.setting()[0]
        for ti, kind in enumerate(CH.TYPES):
            d = OB.draw_type(pool, ti, 3)
            cols = CV.draw_pool(pool, kind, OB.SEED + ti, OB.EXTRA_SEED + ti, 3, scale=d["size"])
            np.testing.assert_allclose(cols.scale, d["size"], rtol=1e-15)
            np.testing.assert_array_equal(OB.every_body(cols)[0], d["X"])

    def test_a_given_size_multiplies_every_length(self):
        pool = CS.setting()[0]
        s = np.array([0.95, 1.0, 1.08])
        a = CV.draw_pool(pool, "typical", 5, 6, 3, error_scale=0.0, scale=s)
        b = CV.draw_pool(pool, "typical", 5, 6, 3, error_scale=0.0, scale=1.5 * s)
        np.testing.assert_allclose(b.scale, 1.5 * s, rtol=1e-15)
        free = np.isfinite(a.values) & (a.values > CL.FLOOR) & (b.values > CL.FLOOR)
        want = np.broadcast_to(1.5 ** np.asarray(a.meta["power"]), a.values.shape)
        np.testing.assert_allclose(b.values[free], a.values[free] * want[free], rtol=1e-12)
        self.assertGreater(free.mean(), 0.9)


class TheClaims(unittest.TestCase):
    def test_a_claim_holds_a_name_by_its_place(self):
        claims = {c["name"]: c for c in OB.claims()}
        t13, l6 = CH.NAME_INDEX["T13"], CH.NAME_INDEX["L6"]
        want = {"below C7": (True, True), "below T5": (True, True), "at or above T6": (False, False),
                "below T12": (False, True), "below L2": (False, True),
                "within the thoracolumbar junction, T11 to L2": (True, False)}
        self.assertEqual(set(want), set(claims))
        for name, (on_t13, on_l6) in want.items():
            holds = OB.claim_holds(claims[name])
            self.assertEqual(bool(holds[t13]), on_t13, name)
            self.assertEqual(bool(holds[l6]), on_l6, name)

    def test_on_c3_to_l5_they_are_the_coarse_studys(self):
        from coarse import study as coarse_study
        from combinations.study import EX
        typical = CH.type_levels("typical")
        for c in OB.claims():
            holds = OB.claim_holds(c)
            level = np.array([EX.LEVELS.index(n) for n in typical])
            np.testing.assert_array_equal(holds[[CH.NAME_INDEX[n] for n in typical]], coarse_study.claim_truth(level, c),
                                          err_msg=c["name"])

    def test_the_rates_count_what_the_claim_says(self):
        claim = {"name": "below T12", "below": "L1"}
        n = len(CH.NAMES)
        post = np.zeros((4, n))
        post[0, CH.NAME_INDEX["L3"]] = 1.0                   # said below, is below: right
        post[1, CH.NAME_INDEX["T4"]] = 1.0                   # said not below, is below: wrong
        post[2, CH.NAME_INDEX["T12"]] = 0.5                  # undecided
        post[2, CH.NAME_INDEX["L1"]] = 0.5
        post[3, CH.NAME_INDEX["T13"]] = 1.0                  # a T13 is not below T12: said not below, right
        truth = np.array([CH.NAME_INDEX[x] for x in ("L2", "L4", "L1", "T13")])
        r = OB.claim_rates(post, truth, np.arange(4), claim)
        self.assertEqual((r["n_decided"], r["errors"]), (3, 1))
        self.assertAlmostEqual(r["decided"], 0.75)
        self.assertAlmostEqual(r["precision"], 2 / 3)
        self.assertAlmostEqual(r["said_true"], 0.25)
        self.assertAlmostEqual(r["said_false"], 0.5)
        self.assertAlmostEqual(r["true_share"], 0.75)


class QuickRun(unittest.TestCase):
    """One run on a few columns a type, scored, tabled, checked and drawn twice."""

    @classmethod
    def setUpClass(cls):
        cls.record = OB.run(OB.QUICK["columns"], processes=1, log=quiet)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = os.path.join(cls.tmp.name, "one_body.json")
        CS.write(cls.record, cls.path)
        cls.dirs = [os.path.join(cls.tmp.name, d) for d in "ab"]
        cls.drawn = [OB.draw_figures(cls.record, d) for d in cls.dirs]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_every_body_is_a_field(self):
        n = OB.QUICK["columns"]
        want = {k: n * len(CH.type_levels(k)) for k in CH.TYPES}
        self.assertEqual(self.record["fields_per_type"], want)
        for r in self.record["rows"]:
            self.assertEqual(r["n_fields"], want[r["type"]], r)
            self.assertEqual(r["n_columns"], n, r)

    def test_a_row_is_its_rule_on_its_own_fields(self):
        pool, _, mu, sd, noise, power, _ = CS.setting()
        mu_e, sd_e = CH.extended_table(mu, sd)
        sets, order_idx = OB.subsets_of(pool, self.record["order"])
        rows = OB.keyed(self.record["rows"], "type", "prior", "size", "measures")
        cases = (("chain", "size given", "all", sets["all"]), ("chain", "unknown", "first 5", order_idx[:5]),
                 ("typical", "height, generator", "seven", sets["seven"]), ("papers, low", "unknown", "ap", sets["ap"]))
        for ti, kind in enumerate(CH.TYPES):
            d = OB.draw_type(pool, ti, OB.QUICK["columns"])
            priors = OB.size_priors(d["height"], d["size"], d["resid"])
            for prior, size, k, idx in cases:
                ev = np.concatenate([OB.column_logev(d["X"][d["col"] == c], OB.nodes_of(priors[size][0][c], priors[size][1][c]),
                                                     mu_e, sd_e, noise, power, sets, order_idx)[k]
                                     for c in range(OB.QUICK["columns"])])
                with np.errstate(divide="ignore"):
                    post = R.posterior(ev, np.log(OB.prior_over_names(prior)))
                want = CV.rates(OB.stats_of(post, d["names"], d["X"], idx, power), d["col"])
                got = rows[kind, prior, size, k]
                for stat in ("exact", "within_one", "set_size", "answered", "n_answered", "errors"):
                    self.assertAlmostEqual(got[stat], want[stat], places=12, msg=(kind, prior, size, k, stat))

    def test_every_row_is_there(self):
        rows = {(r["type"], r["prior"], r["size"], r["measures"]) for r in self.record["rows"]}
        order = ["first %d" % (i + 1) for i in range(len(self.record["order"]))]
        for kind in CH.TYPES:
            for prior in OB.PRIORS:
                for k in list(OB.VIEWS) + order:
                    self.assertIn((kind, prior, "unknown", k), rows)
            for prior in ("typical", "chain"):
                for size in OB.SIZES:
                    for k in OB.VIEWS:
                        self.assertIn((kind, prior, size, k), rows)
        levels = {(r["type"], r["prior"], r["size"], r["measures"], r["name"]) for r in self.record["levels"]}
        for kind in CH.TYPES:
            for prior, size in OB.LEVEL_RULES:
                for k in OB.VIEWS:
                    for name in CH.type_levels(kind):
                        self.assertIn((kind, prior, size, k, name), levels)
        coarse = {(r["type"], r["prior"], r["size"], r["measures"], r["claim"]) for r in self.record["coarse"]}
        for kind in CH.TYPES:
            for c in self.record["claims"]:
                for k in order:
                    self.assertIn((kind, "chain", "unknown", k, c), coarse)

    def test_the_levels_add_up_to_the_types_rows(self):
        rows = OB.keyed(self.record["rows"], "type", "prior", "size", "measures")
        parts: dict = {}
        for r in self.record["levels"]:
            parts.setdefault((r["type"], r["prior"], r["size"], r["measures"]), []).append(r)
        for key, levels in parts.items():
            n = sum(r["n_fields"] for r in levels)
            self.assertEqual(n, rows[key]["n_fields"], key)
            exact = sum(r["exact"] * r["n_fields"] for r in levels) / n
            self.assertAlmostEqual(exact, rows[key]["exact"], places=12, msg=key)
            answered = sum(r["n_answered"] for r in levels)
            self.assertEqual(answered, rows[key]["n_answered"], key)

    def test_the_confusion_counts_are_the_levels(self):
        lv = OB.keyed(self.record["levels"], "type", "prior", "size", "measures", "name")
        for c in self.record["confusion"]:
            m = np.array(c["counts"])
            for i, name in enumerate(CH.NAMES):
                if m[i].sum() == 0:
                    continue
                r = lv[c["type"], c["prior"], c["size"], c["measures"], name]
                self.assertEqual(m[i].sum(), r["n_fields"])
                self.assertAlmostEqual(m[i, i] / m[i].sum(), r["exact"], places=12)

    def test_the_typical_rule_never_names_an_l6_or_a_t13(self):
        for c in self.record["confusion"]:
            if c["prior"] == "typical":
                m = np.array(c["counts"])
                self.assertEqual(m[:, CH.NAME_INDEX["L6"]].sum(), 0)
                self.assertEqual(m[:, CH.NAME_INDEX["T13"]].sum(), 0)

    def test_the_tables_are_the_rows(self):
        rows = OB.keyed(self.record["rows"], "type", "prior", "size", "measures")
        sets = OB.sets_table(self.record).splitlines()
        r = rows["typical", "chain", "unknown", "seven"]
        self.assertIn("| typical | the seven | chain | %s (%s) | %s | %.2f | %s |" % (
            CS.pct(r["exact"]), CS.pct(r["exact_se"]), CS.pct(r["within_one"]), r["set_size"], OB.answered_cell(r)), sets)
        size = OB.size_table(self.record)
        r = rows["t13", "chain", "size given", "all"]
        self.assertIn("%s (%s); %.2f; %s / %s |" % (CS.pct(r["exact"]), CS.pct(r["exact_se"]), r["set_size"],
                                                     CS.pct(r["answered"]), CS.pct(r["precision"], 2)), size)
        co = OB.keyed(self.record["coarse"], "type", "prior", "size", "measures", "claim")
        c = co["six_lumbar", "chain", "unknown", "ap", "below T12"]
        self.assertIn("%s / %s (%d of %d)" % (CS.pct(c["decided"]), CS.pct(c["precision"], 2), c["n_decided"] - c["errors"],
                                              c["n_decided"]), OB.coarse_table(self.record))
        lv = OB.keyed(self.record["levels"], "type", "prior", "size", "measures", "name")
        s, a = lv["typical", "chain", "unknown", "seven", "T6"], lv["typical", "chain", "unknown", "all", "T6"]
        self.assertTrue(any(line.startswith("| T6 | %s | %.2f | %s |" % (CS.pct(s["exact"]), s["set_size"], OB.answered_cell(s)))
                            and line.endswith("| %s | %.2f | %s |" % (CS.pct(a["exact"]), a["set_size"], OB.answered_cell(a)))
                            for line in OB.levels_table(self.record).splitlines()))
        five = " | ".join("%s / %s / %s" % (CS.pct(r["exact"]), CS.pct(r["answered"]), CS.pct(r["precision"], 2))
                          for r in (rows[t, "chain", "unknown", "first 5"] for t in CH.TYPES))
        self.assertIn("| first 5 | %s | %s |" % (self.record["order"][4], five), OB.buildup_table(self.record).splitlines())
        l6, t13 = lv["six_lumbar", "papers, low", "unknown", "all", "L6"], lv["t13", "papers, low", "unknown", "all", "T13"]
        line = next(x for x in OB.weights_table(self.record).splitlines() if x.startswith("| all 32 | papers, low |"))
        self.assertTrue(line.endswith("| %s / %s | %s / %s |" % (CS.pct(l6["exact"]), CS.pct(l6["answered"]), CS.pct(t13["exact"]),
                                                                 CS.pct(t13["answered"]))), line)
        r = rows["six_lumbar", "papers, low", "unknown", "all"]
        self.assertIn("| %s (%s) |" % (CS.pct(r["exact"]), CS.pct(r["exact_se"])), line)
        for name, fn in OB.TABLES.items():
            text = fn(self.record)
            lines = text.splitlines()
            self.assertTrue(all(line.startswith("|") and line.endswith("|") for line in lines), name)
            self.assertEqual(len({line.count("|") for line in lines}), 1, name)

    def test_check_finds_the_readmes_tables(self):
        want = OB.tables(self.path)
        text = "".join("<!-- %s -->\n%s<!-- /%s -->\n\n" % (k, v, k) for k, v in want.items())
        readme = os.path.join(self.tmp.name, "README.md")
        with open(readme, "w") as fh:
            fh.write("# A README\n\n" + text)
        self.assertEqual(OB.check(readme, self.path), [])
        first = next(iter(want))
        with open(readme, "w") as fh:
            fh.write("# A README\n\n" + text.replace(want[first], want[first].replace("|", "| ", 1), 1))
        self.assertEqual(OB.check(readme, self.path), ["the README's %s is not the record's" % first])

    def test_drawn_twice_the_figures_are_the_same_files(self):
        names = sorted(os.path.basename(p) for p in self.drawn[0])
        self.assertEqual(names, sorted(s + e for s in STEMS for e in EXTENSIONS))
        for name in names:
            with open(os.path.join(self.dirs[0], name), "rb") as fa, open(os.path.join(self.dirs[1], name), "rb") as fb:
                self.assertEqual(fa.read(), fb.read(), name)

    def test_every_caption_is_under_sixty_words(self):
        for stem in STEMS:
            with open(os.path.join(self.dirs[0], stem + ".caption.txt"), encoding="ascii") as fh:
                caption = fh.read()
            self.assertLessEqual(FG.words(caption), FG.CAPTION_WORDS, stem)
            self.assertIn("synthetic", caption.replace("Synthetic", "synthetic"), stem)

    def test_the_csvs_hold_the_records_numbers(self):
        rows = OB.keyed(self.record["rows"], "type", "prior", "size", "measures")
        lv = OB.keyed(self.record["levels"], "type", "prior", "size", "measures", "name")
        co = OB.keyed(self.record["coarse"], "type", "prior", "size", "measures", "claim")

        def read(stem):
            with open(os.path.join(self.dirs[0], stem + ".csv"), encoding="ascii") as fh:
                return list(csv.DictReader(fh))

        def near(got, want):
            if np.isnan(want):
                self.assertEqual(got, "nan")
            else:
                self.assertAlmostEqual(float(got), want, delta=1e-5 * max(1.0, abs(want)))
        for r in read("one_body_levels"):
            v = lv["typical", "chain", "unknown", r["measures"], r["level"]][r["stat"]]
            near(r["value"], v if r["stat"] == "set_size" else 100 * v)
        for r in read("one_body_buildup"):
            near(r["percent"], 100 * rows[r["type"], "chain", "unknown", "first %s" % r["measures"]][r["stat"]])
        for r in read("one_body_coarse"):
            c = co["typical", "chain", "unknown", "first %s" % r["measures"], r["claim"]]
            near(r["percent"], 100 * c["decided" if r["panel"] == "A" else "precision"])
        for r in read("one_body_size"):
            near(r["percent"], 100 * rows["typical", "chain", r["size"], r["measures"]][r["stat"]])

    def test_the_record_names_the_code_and_the_order_it_was_made_by(self):
        made = self.record["made_by"]
        self.assertIn("git", made)
        self.assertIn("digests", made)
        self.assertEqual(self.record["order"], OB.build_up_order())
        self.assertEqual(self.record["order_from"]["sha256"], FG.sha256(OB.CURVE_RECORD))


@unittest.skipUnless(os.path.exists(OB.RECORD), "the record is not made yet")
class CommittedRecord(unittest.TestCase):
    """records/one-body-2026-10-29/ as committed."""

    @classmethod
    def setUpClass(cls):
        cls.record = OB.load()

    def test_the_readme_carries_its_tables(self):
        self.assertEqual(OB.check(), [])

    def test_it_was_made_by_committed_code_that_did_not_change(self):
        self.assertEqual(self.record["changed_during_run"], {})
        self.assertFalse(self.record["made_by"]["git"]["package_changed"])
        self.assertEqual(self.record["columns_per_type"], OB.COLUMNS)

    def test_its_figures_are_what_the_code_draws_from_it(self):
        with open(os.path.join(OB.OUTDIR, "FIGURES.md"), encoding="ascii") as fh:
            said = fh.read()
        self.assertIn("sha256 %s." % FG.sha256(OB.RECORD), said)
        for name in ("figures.py", "one_body.py"):
            self.assertIn("`schwingcheck/%s`, sha256 %s." % (name, FG.sha256(os.path.join(ROOT, "schwingcheck", name))), said)
        with tempfile.TemporaryDirectory() as tmp:
            drawn = sorted(os.path.basename(p) for p in OB.draw_figures(self.record, tmp))
            self.assertEqual(len(drawn), len(STEMS) * len(EXTENSIONS))
            for name in drawn:
                self.assertIn("`%s`" % name, said)
                with open(os.path.join(tmp, name), "rb") as fa, open(os.path.join(OB.OUTDIR, name), "rb") as fb:
                    self.assertEqual(fa.read(), fb.read(), name)

    def test_the_readme_shows_each_figure(self):
        with open(OB.README, encoding="ascii") as fh:
            text = fh.read()
        for stem in STEMS:
            self.assertIn('src="../records/one-body-2026-10-29/figures/%s.png"' % stem, text)


if __name__ == "__main__":
    unittest.main()
