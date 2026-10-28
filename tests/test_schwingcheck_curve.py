"""Step e's build-up study (curve.py, curve_report.py) on columns small enough for a test.

Rung 0 is the record's: the seven's values in the study's columns are the values rescore draws
from seed 97, whatever the other 25 measures, so the seven's rates can be held to exact.json. The
subsets are what their names say: each prefix of the order holds as many measures as its number,
the ladder's first rung is the seven and the pedicles and its last all 32, and the families with
the seven make up the pool. The SD a predictive rule takes for a new person about twelve is
exact.py's. A field is floored only by a value at the floor in a measure that scales with the
size. One small study, five arms of a few columns, is scored on one process; the share it names
exactly is the share rule.py's posterior names, counted here by hand; its record prints every
table, check_readme holds a README that carries them and finds one that is stale, missing or
doubled, and its figures, drawn twice, are the same files.
"""
from __future__ import annotations

import json
import math
import os
import shutil
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "archive", "bordercall"))

import exact as E                              # noqa: E402
from schwingcheck import LEVELS                # noqa: E402
from schwingcheck import columns as C          # noqa: E402
from schwingcheck import curve as CV           # noqa: E402
from schwingcheck import curve_report as CR    # noqa: E402
from schwingcheck import measures as MS        # noqa: E402
from schwingcheck import records as REC        # noqa: E402
from schwingcheck import rule as R             # noqa: E402


def quiet(*args):
    pass


class Columns(unittest.TestCase):
    def test_the_sevens_values_are_the_records(self):
        pool = MS.pool()
        seven = MS.select(MS.SPINEPS_7)
        cols = CV.draw_pool(pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, 40)
        ref = C.draw_columns(MS.reference(seven), ["typical"], CV.SCORE_SEED, 40, [MS.archive_key(m) for m in seven])
        keys = [m.key for m in pool]
        self.assertEqual(cols.values.shape[2], 32)
        np.testing.assert_array_equal(cols.values[:, :, [keys.index(k) for k in MS.SPINEPS_7]], ref.values)


class Subsets(unittest.TestCase):
    def setUp(self):
        self.pool = MS.pool()
        self.order = list(range(len(self.pool)))[::-1]
        self.index = CV.subsets(self.pool, self.order)

    def test_each_prefix_is_the_orders_start(self):
        for k in range(1, len(self.pool) + 1):
            self.assertEqual(self.index["prefix-%02d" % k], self.order[:k])
        self.assertEqual(sorted(self.index["prefix-32"]), self.index["all"])

    def test_the_seven_the_families_and_the_ladder(self):
        keys = [m.key for m in self.pool]
        seven = set(self.index["seven"])
        self.assertEqual(sorted(keys[i] for i in seven), sorted(MS.SPINEPS_7))
        families = [set(self.index["seven+" + f]) - seven for f in CV.FAMILIES]
        self.assertEqual(sum(len(f) for f in families) + len(seven), len(self.pool))
        self.assertEqual(set().union(seven, *families), set(range(len(self.pool))))
        self.assertEqual(self.index["ladder-pedicles"], self.index["seven+pedicles"])
        self.assertEqual(self.index["ladder-body"], self.index["all"])

    def test_the_table_names_each_set_once(self):
        """The report leaves out a rung of the ladder that another row holds under its own name."""
        tree = small_record()
        names = CR.subset_order(tree)
        sets = [CR.members_of(tree, s) for s in names]
        self.assertEqual(len(sets), len(set(sets)))
        self.assertNotIn("ladder-pedicles", names)
        self.assertNotIn("ladder-body", names)
        self.assertIn("ladder-facets", names)


class DataAxis(unittest.TestCase):
    def test_the_predictive_sd_is_exact_pys_for_twelve(self):
        ref = {"m": {lv: (10.0, 2.0) for lv in E.LEVELS}}
        table = E.rule_table(ref, ["m"], E.RULES["predictive"])
        self.assertAlmostEqual(CV.predictive_factor(12), table["m"]["L1"][1] / 2.0, places=14)

    def test_a_large_table_is_close_to_the_printed_one(self):
        pool = MS.pool()
        mu, sd = MS.arrays(pool)
        emu, esd = CV.estimated_table(pool, 2000, np.random.default_rng(3))
        self.assertEqual(emu.shape, mu.shape)
        self.assertLess(float(np.max(np.abs(emu - mu) / (sd / math.sqrt(2000)))), 6.0)
        self.assertLess(float(np.max(np.abs(esd / sd - 1.0))), 0.1)


class Floor(unittest.TestCase):
    def test_only_a_measure_that_scales_with_the_size_floors_a_field(self):
        X = np.full((3, 2, 2), 10.0)
        X[1, 0, 1] = C.FLOOR                 # a length at the floor
        X[2, 1, 0] = C.FLOOR                 # an angle, which has no floor, at 0.5
        power = np.array([1.0, 0.0])
        self.assertEqual(CV.floored_in(X, [0, 1], power).tolist(), [False, True, False])
        self.assertEqual(CV.floored_in(X, [1], power).tolist(), [False, False, False])


_SMALL = {}


def small_study():
    """Five arms of a few columns: the nominal typical one at 1, 3 and 9 bodies with every subset,
    six lumbar at 3, and the data axis's twelve people, two tables, nominal and predictive."""
    if _SMALL:
        return _SMALL
    pool = MS.pool()
    keys = [m.key for m in pool]
    order = [keys.index(k) for k in MS.SPINEPS_7] + [i for i in range(len(pool)) if keys[i] not in MS.SPINEPS_7]
    index = CV.subsets(pool, order)
    names = list(index)
    mu, sd = MS.arrays(pool)
    noise, power = MS.errors(pool), MS.powers(pool)
    typical = CV.draw_pool(pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, 3)
    six = CV.draw_pool(pool, "six_lumbar", CV.ANOMALOUS_SEED, CV.ANOMALOUS_EXTRA_SEED, 2)
    arms = [CV.Arm("nominal", "typical", typical.values, typical.levels, mu, sd, noise, power, (1, 3, 9), names),
            CV.Arm("nominal", "six_lumbar", six.values, six.levels, mu, sd, noise, power, (3,), names)]
    rng = np.random.default_rng(CV.WORLD_SEED)
    robust = CV.prefixes_and_seven(names)
    for world in range(2):
        emu, esd = CV.estimated_table(pool, 12, rng)
        for rule, factor in (("nominal", 1.0), ("predictive", CV.predictive_factor(12))):
            arms.append(CV.Arm("people-12-%s" % rule, "typical", typical.values[:2], typical.levels[:2], emu, esd * factor,
                               noise, power, (3,), robust, world=world,
                               settings={"people": 12, "rule": rule, "sd_factor": factor, "tables": 2}))
    rows = CV.run_arms(arms, index, processes=1, log=quiet)
    trace = [{"measure": pool[i].key, "loss": 1.0 / (k + 1), "loss_by_width": {str(n): 1.0 / (k + 1) for n in CV.WIDTHS}}
             for k, i in enumerate(order)]
    _SMALL.update(pool=pool, order=order, index=index, arms=arms, rows=rows, trace=trace)
    return _SMALL


def small_record(times=None, nuts=None):
    s = small_study()
    return CV.build_record(s["rows"], s["pool"], s["order"], s["trace"], s["index"], s["arms"], times or {}, nuts or {},
                           "python -m schwingcheck curve run (a test)", True)


def fake_times(order):
    """Times shaped as speed() gives them, for drawing and printing, not for reading."""
    out = {}
    for e, engine in enumerate(CV.ENGINES):
        for k in (1, 7, 16, 32):
            for n in CV.WIDTHS:
                out[(engine, k, n)] = {"median_ms": 0.1 * (e + 1) * k * n, "max_ms": 0.2 * (e + 1) * k * n,
                                       "batch_ms": 0.05 * (e + 1) * k * n}
    return out


def fake_nuts():
    return {k: {"fields": 4, "width": 3, "draws": 500, "tune": 500, "chains": 2, "build_s": 0.05 * k, "sample_s": 0.1 * k,
                "posterior_s": 0.01 * k, "max_abs_diff": 1e-6, "max_mcse": 2e-6} for k in (7, 16, 32)}


class SmallStudy(unittest.TestCase):
    def test_the_share_named_exactly_is_rule_pys(self):
        s = small_study()
        arm = s["arms"][0]
        sizes, logw = R.trapezoid(R.SYNTH["scale_sd"])
        for sub in ("seven", "prefix-09", "all"):
            idx = s["index"][sub]
            for n in (1, 3, 9):
                offsets = np.arange(n)
                X, start, _ = C.fields(arm.values, offsets)
                LL = R.loglik(X[:, idx, :], offsets, arm.mu[idx], arm.sd[idx], R.SYNTH, sizes=sizes,
                              noise=arm.noise[idx], power=arm.power[idx])
                post = R.posterior(R.log_evidence(LL, logw))
                row = s["rows"][("nominal", "typical", sub, n)]
                self.assertEqual(row["n_fields"], len(start))
                self.assertEqual(row["n_columns"], 3)
                self.assertEqual(round(row["exact"] * len(start)), int((post.argmax(1) == start).sum()), (sub, n))
                said = post.max(1) >= CV.CLAIM
                self.assertEqual(round(row["answered"] * len(start)), int(said.sum()), (sub, n))

    def test_the_data_axis_pools_its_tables(self):
        s = small_study()
        row = s["rows"][("people-12-nominal", "typical", "seven", 3)]
        self.assertEqual(row["n_columns"], 2)
        self.assertEqual(row["n_fields"], 2 * 2 * (len(LEVELS) - 2))
        self.assertTrue(np.isfinite(row["exact_table_sd"]))

    def test_the_record_holds_every_arm_and_the_floor(self):
        tree = small_record()
        ds = tree["rates"].to_dataset()
        self.assertEqual(ds["arm"].values.tolist(), ["nominal", "people-12-nominal", "people-12-predictive"])
        self.assertEqual(ds["width"].values.tolist(), [1, 3, 9])
        self.assertTrue(np.isnan(float(ds["exact"].sel(arm="people-12-nominal", phenotype="typical", subset="all",
                                                        width=3))))
        floor = json.loads(tree.attrs["floor"])
        self.assertEqual(sorted(floor), ["nominal/six_lumbar", "nominal/typical"])


class Report(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="curve-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_check_readme_holds_the_tables_and_finds_what_differs(self):
        tree = small_record(fake_times(small_study()["order"]), fake_nuts())
        text = CR.tables(tree)
        for name in CR.TABLES:
            self.assertIn("<!-- curve:%s -->" % name, text)
        readme = os.path.join(self.tmp, "README.md")
        with open(readme, "w", encoding="ascii") as fh:
            fh.write("# A README\n\nSome prose.\n\n" + text + "\n\nMore prose.\n")
        self.assertEqual(CR.check_readme(tree, readme), [])
        stale = text.replace("| 1 | `endplate`", "| 1 | `endplate_lower`", 1)
        self.assertNotEqual(stale, text)
        with open(readme, "w", encoding="ascii") as fh:
            fh.write(stale.replace("<!-- curve:floor -->", "<!-- curve:flor -->") + "\n" + CR.block(tree, "arms") + "\n")
        problems = CR.check_readme(tree, readme)
        self.assertIn("table curve: differs from the record's (python -m schwingcheck curve table)", problems)
        self.assertIn("table floor: not in the README", problems)
        self.assertIn("table arms: written more than once", problems)
        self.assertEqual(len(problems), 3)

    def test_a_record_without_times_says_so(self):
        tree = small_record()
        self.assertEqual(CR.table_speed(tree), CR.NOT_TIMED)
        self.assertEqual(CR.table_nuts(tree), CR.NOT_TIMED)

    def test_the_figures_are_the_same_files_when_drawn_twice(self):
        tree = small_record(fake_times(small_study()["order"]), fake_nuts())
        record = os.path.join(self.tmp, "curve.nc")
        REC.write(tree, record)
        tree = REC.read(record)
        first = CR.draw_figures(tree, os.path.join(self.tmp, "a"), record)
        second = CR.draw_figures(tree, os.path.join(self.tmp, "b"), record)
        names = sorted(os.path.basename(p) for p in first)
        self.assertEqual(names, sorted(os.path.basename(p) for p in second))
        for stem in ("curve_accuracy", "curve_speed", "curve_data"):
            for ext in (".pdf", ".png", ".csv", ".caption.txt"):
                self.assertIn(stem + ext, names)
        for name in names:
            if name == "FIGURES.md":
                continue
            with open(os.path.join(self.tmp, "a", name), "rb") as fa, open(os.path.join(self.tmp, "b", name), "rb") as fb:
                self.assertEqual(fa.read(), fb.read(), name)
        for stem in ("curve_accuracy", "curve_speed", "curve_data"):
            with open(os.path.join(self.tmp, "a", stem + ".caption.txt"), encoding="ascii") as fh:
                self.assertLessEqual(len(fh.read().split()), 60, stem)


if __name__ == "__main__":
    unittest.main()
