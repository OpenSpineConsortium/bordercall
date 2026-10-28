"""Step e's build-up study (curve.py, curve_report.py) on columns small enough for a test.

Rung 0 is the record's: the seven's values in the study's columns are the values rescore draws
from seed 97, whatever the other 25 measures, so the seven's rates can be held to exact.json. The
subsets are what their names say: each prefix of the order holds as many measures as its number,
the ladder's first rung is the seven and the pedicles and its last all 32, and the families with
the seven make up the pool. The SD a predictive rule takes for a new person about twelve is
exact.py's. A field is floored only by a value at the floor in a measure that scales with the
size. One small study, seven arms of a few columns, is scored on one process; the share it names
exactly is the share rule.py's posterior names, counted here by hand; its record prints every
table, check_readme holds a README that carries them and finds one that is stale, missing or
doubled, and its figures, drawn twice, are the same files.

Each fix of the review of 28 October 2026 is held by a test that fails without it: the data
axis's standard errors that count its tables (crossed_se against an analysis of variance written
out, and the precision's against the ratio estimator on the cells) and its two tables at least at
every number of people; the count answered in every cell and the precision's exact lower bound
where no answered field is wrong; the narrowest jobs first; within one level on a T13 column as
the docstrings say; the table as printed scored on the axis's own columns and every table read
against it; the correlated arm and the supplement as the docstrings name them; the specimens drawn
with no floor; draw_pool's meta; the typical columns at five bodies; the curve commands run on a
record; the compiled rule's table built once; every thread pool at one thread inside the limit,
in a fresh interpreter; the batch timed after a warm-up at its own size; NUTS on every place and
on one field alone, its setup apart from its loop; the record's digests taken when the run began;
how the times were taken; and writes that leave the record whole.
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "archive", "bordercall"))

import exact as E                              # noqa: E402
import exact_supplement as ES                  # noqa: E402
from schwingcheck import LEVELS                # noqa: E402
from schwingcheck import __main__ as MAIN      # noqa: E402
from schwingcheck import columns as C          # noqa: E402
from schwingcheck import compiled as K         # noqa: E402
from schwingcheck import curve as CV           # noqa: E402
from schwingcheck import curve_report as CR    # noqa: E402
from schwingcheck import measures as MS        # noqa: E402
from schwingcheck import model as MD           # noqa: E402
from schwingcheck import records as REC        # noqa: E402
from schwingcheck import rule as R             # noqa: E402
from schwingcheck import score as S            # noqa: E402

TODO = os.path.join(ROOT, "TODO.md")


def quiet(*args):
    pass


def flat(text: str) -> str:
    """Text with its line breaks and runs of spaces made single spaces, so a phrase is found
    wherever a docstring wraps it."""
    return " ".join(text.split())


def two_way(cell: np.ndarray) -> float:
    """The two-way random-effects SE of a grand mean from (columns, tables) cell means, written out
    with loops: sqrt((MS_columns + max(MS_tables - MS_interaction, 0)) / (C T))."""
    a, b = cell.shape
    g = sum(cell[c, t] for c in range(a) for t in range(b)) / (a * b)
    row = [sum(cell[c, t] for t in range(b)) / b for c in range(a)]
    column = [sum(cell[c, t] for c in range(a)) / a for t in range(b)]
    ms_c = b * sum((row[c] - g) ** 2 for c in range(a)) / (a - 1)
    ms_t = a * sum((column[t] - g) ** 2 for t in range(b)) / (b - 1)
    ms_e = sum((cell[c, t] - row[c] - column[t] + g) ** 2 for c in range(a) for t in range(b)) / ((a - 1) * (b - 1))
    return math.sqrt((ms_c + max(ms_t - ms_e, 0.0)) / (a * b))


_QUICK = []


def quick_arms():
    """make_arms at the quick counts, drawn once for the tests that read them."""
    if not _QUICK:
        pool = MS.pool()
        _QUICK.extend(CV.make_arms(pool, list(CV.subsets(pool, list(range(len(pool))))), quick=True))
    return _QUICK


class Columns(unittest.TestCase):
    def test_the_sevens_values_are_the_records(self):
        pool = MS.pool()
        seven = MS.select(MS.SPINEPS_7)
        cols = CV.draw_pool(pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, 40)
        ref = C.draw_columns(MS.reference(seven), ["typical"], CV.SCORE_SEED, 40, [MS.archive_key(m) for m in seven])
        keys = [m.key for m in pool]
        self.assertEqual(cols.values.shape[2], 32)
        np.testing.assert_array_equal(cols.values[:, :, [keys.index(k) for k in MS.SPINEPS_7]], ref.values)

    def test_the_pools_meta_is_the_pools(self):
        """draw_pool's meta gives every measure of the pool its power and error, in the pool's
        order, so that columns.floor_hits reads its columns as floor_counts does."""
        pool = MS.pool()
        cols = CV.draw_pool(pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, 40, error_scale=2.0)
        self.assertEqual(cols.meta["power"], MS.powers(pool).tolist())
        self.assertEqual(cols.meta["noise_mm"], (MS.errors(pool) * 2.0).tolist())
        mu, sd = MS.arrays(pool)
        arm = CV.Arm("nominal", "typical", cols.values, cols.levels, mu, sd, MS.errors(pool), MS.powers(pool), (1,), [])
        self.assertEqual(C.floor_hits(cols), CV.floor_counts([arm], [m.key for m in pool])["nominal/typical"])

    def test_the_specimens_have_no_floor(self):
        """The data axis's specimens are drawn with no floor and the stream as it was, so that a
        2,000-person table's SD at interfacet_h:mean C4 is the printed one within 3 SE, where the
        same specimens with the floor hold it more than 3 SE below (seed 317)."""
        pool = MS.pool()
        mu, sd = MS.arrays(pool)
        i, j = [m.key for m in pool].index("interfacet_h:mean"), LEVELS.index("C4")
        se = 1.0 / math.sqrt(2.0 * 1999)                       # the relative SE of an SD from 2,000 people
        _, esd = CV.estimated_table(pool, 2000, np.random.default_rng(317))
        self.assertLess(abs(esd[i, j] / sd[i, j] - 1.0), 3 * se)
        seed = int(np.random.default_rng(317).integers(1 << 30))
        kw = dict(noise_mm=0.0, scale_sd=0.0, power=MS.powers(pool))
        bare = C.draw_columns(MS.reference(pool), ["typical"], seed, 2000, CV._keys(pool), floor=False, **kw)
        held = C.draw_columns(MS.reference(pool), ["typical"], seed, 2000, CV._keys(pool), **kw)
        self.assertLess(held.values[:, j, i].std(ddof=1) / sd[i, j], 1.0 - 3 * se)
        self.assertTrue((bare.values[:, j, i] < C.FLOOR).any())
        same = held.values > C.FLOOR
        np.testing.assert_array_equal(bare.values[same], held.values[same])
        self.assertEqual(C.floor_hits(bare)["values"], 0)


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


class Arms(unittest.TestCase):
    def test_the_typical_columns_are_scored_at_five_bodies_too(self):
        nominal = [a for a in quick_arms() if a.name == "nominal"]
        self.assertEqual({a.phenotype for a in nominal}, {"typical"} | set(CV.ANOMALOUS))
        self.assertEqual({a.widths for a in nominal}, {CV.NOMINAL_WIDTHS})
        self.assertIn(5, CV.NOMINAL_WIDTHS)
        row = small_study()["rows"][("nominal", "typical", "seven", 5)]
        self.assertEqual(row["n_fields"], 3 * (len(LEVELS) - 4))

    def test_the_correlated_arm_is_the_misspecified_world_and_measures_no_cost(self):
        """r 0.4 with every other setting as assumed is exact.py's misspecified world, not its
        combined one, which draws another error too; the docstring and TODO.md say what it shows."""
        self.assertEqual(CV.R_BETWEEN, E.MISSPEC["r_between"][0])
        self.assertEqual(E.COMBINED["r_between"], CV.R_BETWEEN)
        self.assertIn("noise_mm", E.COMBINED)
        pool = MS.pool()
        arm = next(a for a in quick_arms() if a.name == "correlated")
        np.testing.assert_array_equal(arm.noise, MS.errors(pool))
        np.testing.assert_array_equal(arm.mu, MS.arrays(pool)[0])
        doc = flat(CV.__doc__)
        self.assertIn("the archive's misspecified world r_between = 0.4, exact.MISSPEC", doc)
        self.assertIn("It does not measure what treating the measures as independent costs", doc)
        self.assertNotIn("(the archive's combined world)", doc)
        with open(TODO, encoding="ascii") as fh:
            todo = flat(fh.read())
        self.assertIn("does not measure what treating the measures as independent costs", todo)

    def test_the_supplement_drew_three_of_the_five_phenotypes(self):
        self.assertEqual(ES.ANOMALOUS_SEED, CV.ANOMALOUS_SEED)
        self.assertEqual(set(ES.ANOMALOUS), {"six_lumbar", "four_lumbar", "t13"})
        self.assertTrue(set(ES.ANOMALOUS) < set(CV.ANOMALOUS))
        doc = flat(CV.__doc__)
        self.assertIn("which drew six_lumbar, four_lumbar and t13", doc)
        self.assertIn("lumbar_rib and no_rib_t12 are new here", doc)
        self.assertIn("(the rib reading: a thirteenth rib-bearing body is T13)", doc)

    def test_the_narrowest_fields_go_first(self):
        widths = [j[1] for j in CV.jobs_of(small_study()["arms"])]
        self.assertEqual(widths, sorted(widths))
        self.assertIn("the narrowest fields first", flat(CV.jobs_of.__doc__))
        self.assertNotIn("widest", CV.jobs_of.__doc__)


class Truth(unittest.TestCase):
    def test_on_a_t13_column_t12_and_l1_are_within_one(self):
        """On the half-step scale a T12 called L1, or an L1 called T12, is within one level on a
        column that has a T13 between them, and the docstrings say so."""
        levels = list(LEVELS[:LEVELS.index("T12") + 1]) + ["T13"] + list(LEVELS[LEVELS.index("L1"):])
        for true, called in (("T12", "L1"), ("L1", "T12")):
            start = np.array([levels.index(true)])
            truth_at = CV.true_positions(start, np.array([0]), [levels], 1)
            post = np.zeros((1, len(LEVELS)))
            post[0, LEVELS.index(called)] = 1.0
            st = CV.field_stats(post, start, truth_at, 1, False)
            self.assertFalse(bool(st["hit"][0]))
            self.assertTrue(bool(st["within"][0]), (true, called))
            self.assertEqual(abs(levels.index(true) - levels.index(called)), 2)
        for doc in (CV.__doc__, CV.field_stats.__doc__):
            self.assertIn("two bodies apart", flat(doc))
        self.assertIn("two bodies apart", flat("\n".join(CR.table_anomalous(small_record()))))


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

    def test_every_number_of_people_has_two_tables_at_least(self):
        """So that every row of the axis carries the variation between tables."""
        for worlds in (CV.WORLDS, CV.QUICK_COUNTS["worlds"]):
            self.assertGreaterEqual(min(worlds.values()), 2)
        for p in CV.QUICK_COUNTS["worlds"]:
            self.assertEqual(len({a.world for a in quick_arms() if a.name == "people-%d-nominal" % p}), 2)

    def test_the_table_as_printed_is_scored_on_the_axis_columns(self):
        arms = quick_arms()
        names = [a.name for a in arms]
        printed = arms[names.index("people-printed")]
        mu, sd = MS.arrays(MS.pool())
        np.testing.assert_array_equal(printed.mu, mu)
        np.testing.assert_array_equal(printed.sd, sd)
        np.testing.assert_array_equal(printed.values, arms[0].values[:CV.QUICK_COUNTS["world_columns"]])
        for a in arms:
            if a.name.startswith("people-"):
                np.testing.assert_array_equal(a.values, printed.values)
                self.assertEqual(a.widths, printed.widths)
        self.assertLess(names.index("people-printed"), min(i for i, n in enumerate(names) if n.startswith("people-1")))
        self.assertEqual(CV.floor_counts([printed], [m.key for m in MS.pool()]), {})

    def test_the_crossed_se_is_the_two_way_analysis_of_variance(self):
        rng = np.random.default_rng(5)
        a, b, k = 6, 4, 3
        col = np.repeat(np.arange(a), b * k)
        world = np.tile(np.repeat(np.arange(b), k), a)
        v = (rng.random(a * b * k) < 0.2 + 0.12 * world + 0.03 * col).astype(float)
        cell = np.array([[v[(col == c) & (world == t)].mean() for t in range(b)] for c in range(a)])
        self.assertAlmostEqual(CV.crossed_se(v, col, world), two_way(cell), places=14)
        # the SE clustered by column is the columns' term alone, which the tables' term adds to here
        clustered = S.clustered_se(v, col)
        self.assertAlmostEqual(clustered, math.sqrt(b * np.var(cell.mean(1), ddof=1) / (a * b)), places=14)
        self.assertGreater(CV.crossed_se(v, col, world), clustered)
        self.assertTrue(math.isnan(CV.crossed_se(v, col, np.zeros_like(world))))
        self.assertTrue(math.isnan(CV.crossed_se(v[1:], col[1:], world[1:])))

    def test_the_axis_rates_count_the_tables(self):
        """pooled_rates on fields from four tables of the same columns: the SEs clustered by column
        as before, and beside them the SEs with the tables, the shares' by the two-way estimate and
        the precision's equal to the ratio estimator on the (column, table) cells written out."""
        a, b, k = 8, 4, 5
        rng = np.random.default_rng(11)
        parts = {"col": [], "world": [], "stats": []}
        for t in range(b):
            col = np.repeat(np.arange(a), k)
            hit = rng.random(a * k) < 0.55 + 0.1 * t
            top = np.where(rng.random(a * k) < 0.6, 0.995, 0.5)
            parts["col"].append(col)
            parts["world"].append(t)
            parts["stats"].append({"seven": {"hit": hit, "within": hit | (rng.random(a * k) < 0.5), "top": top,
                                             "logp": np.zeros(a * k), "size": np.ones(a * k, np.int16),
                                             "floored": np.zeros(a * k, bool)}})
        row = CV.pooled_rates(parts, "seven")
        col = np.concatenate(parts["col"])
        world = np.concatenate([np.full(len(c), w) for c, w in zip(parts["col"], parts["world"])])
        hit = np.concatenate([s["seven"]["hit"] for s in parts["stats"]]).astype(float)
        said = np.concatenate([s["seven"]["top"] for s in parts["stats"]]) >= CV.CLAIM
        self.assertAlmostEqual(row["exact_se"], S.clustered_se(hit, col), places=14)
        cells = np.zeros((a, b))
        np.add.at(cells, (col, world), hit / k)
        self.assertAlmostEqual(row["exact_se_tables"], two_way(cells), places=14)
        wrong, answered = np.zeros((a, b)), np.zeros((a, b))
        np.add.at(wrong, (col, world), said & (hit == 0))
        np.add.at(answered, (col, world), said)
        self.assertGreater(wrong.sum(), 0)
        ratio = wrong.sum() / answered.sum()
        resid = (wrong - ratio * answered) / (answered.sum() / (a * b))
        self.assertAlmostEqual(row["precision_se_tables"], two_way(resid), places=12)
        for s in CV.TABLE_TERMS:
            self.assertTrue(np.isfinite(row[s + "_se_tables"]), s)
        nominal = small_study()["rows"][("nominal", "typical", "seven", 3)]
        for s in CV.TABLE_TERMS:
            self.assertTrue(math.isnan(nominal[s + "_se_tables"]), s)
        axis = small_study()["rows"][("people-12-nominal", "typical", "seven", 3)]
        self.assertGreaterEqual(axis["exact_se_tables"], axis["exact_se"])
        doc = flat(CV.pooled_rates.__doc__)
        self.assertIn("7, 3, 1 and 1 at P = 12, 50, 200 and 2,000", doc)


class Floor(unittest.TestCase):
    def test_only_a_measure_that_scales_with_the_size_floors_a_field(self):
        X = np.full((3, 2, 2), 10.0)
        X[1, 0, 1] = C.FLOOR                 # a length at the floor
        X[2, 1, 0] = C.FLOOR                 # an angle, which has no floor, at 0.5
        power = np.array([1.0, 0.0])
        self.assertEqual(CV.floored_in(X, [0, 1], power).tolist(), [False, True, False])
        self.assertEqual(CV.floored_in(X, [1], power).tolist(), [False, False, False])


class Precision(unittest.TestCase):
    def stats(self, n=40, answered=18):
        return {"hit": np.ones(n, bool), "within": np.ones(n, bool),
                "top": np.r_[np.full(answered, 0.995), np.full(n - answered, 0.5)], "logp": np.zeros(n),
                "size": np.ones(n, np.int16), "floored": np.zeros(n, bool)}

    def test_a_precision_with_no_error_carries_its_exact_lower_bound(self):
        """18 right of 18 answered: a precision of 1 with a clustered SE of 0, and the exact
        two-sided 95 per cent lower bound, whose Beta(18, 1) tail below it is 0.025."""
        group = np.arange(40) % 10
        row = CV.rates(self.stats(), group)
        self.assertEqual((row["n_answered"], row["errors"], row["precision"], row["precision_se"]), (18, 0, 1.0, 0.0))
        self.assertAlmostEqual(row["precision_lower"], 0.025 ** (1.0 / 18), places=15)
        self.assertAlmostEqual(row["precision_lower"] ** 18, 0.025, places=14)
        wrong = self.stats()
        wrong["hit"][0] = False
        row = CV.rates(wrong, group)
        self.assertEqual(row["errors"], 1)
        self.assertTrue(math.isnan(row["precision_lower"]))
        self.assertGreater(row["precision_se"], 0.0)
        self.assertTrue(math.isnan(CV.rates(self.stats(answered=0), group)["precision_lower"]))

    def test_every_cell_records_its_count_answered(self):
        ds = small_record()["rates"].to_dataset()
        scored = np.isfinite(ds["exact"].values)
        np.testing.assert_array_equal(np.isfinite(ds["n_answered"].values), scored)
        np.testing.assert_allclose(ds["n_answered"].values[scored], (ds["answered"] * ds["n_fields"]).values[scored])

    def test_the_report_prints_the_bound_where_no_field_is_wrong(self):
        tree = small_record()
        ds = CR.rates_of(tree)
        lower = CR.value(ds, "precision_lower", "nominal", "typical", "prefix-32", 9)
        self.assertTrue(np.isfinite(lower))
        cell = CR.precision_cell(ds, "nominal", "typical", "prefix-32", 9)
        self.assertEqual(cell, "100.00%% (at least %s)" % CR.pct(lower, 2))
        text = "\n".join(CR.table_curve(tree))
        self.assertIn(cell, text)
        self.assertIn(CR.BOUND_NOTE, text)


_SMALL = {}


def small_study():
    """Seven arms of a few columns: the nominal typical one at 1, 3, 5 and 9 bodies with every
    subset, six lumbar at 3, and the data axis at 3: the table as printed and twelve people's,
    two tables, each nominal and predictive, all on the same two columns."""
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
    robust = CV.prefixes_and_seven(names)
    arms = [CV.Arm("nominal", "typical", typical.values, typical.levels, mu, sd, noise, power, CV.NOMINAL_WIDTHS, names),
            CV.Arm("nominal", "six_lumbar", six.values, six.levels, mu, sd, noise, power, (3,), names),
            CV.Arm("people-printed", "typical", typical.values[:2], typical.levels[:2], mu, sd, noise, power, (3,), robust,
                   settings={"people": None, "rule": "printed", "sd_factor": 1.0, "tables": 1})]
    rng = np.random.default_rng(CV.WORLD_SEED)
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


def small_record(times=None, nuts=None, how=None, made_by=None, n_select=None):
    s = small_study()
    return CV.build_record(s["rows"], s["pool"], s["order"], s["trace"], s["index"], s["arms"], times or {}, nuts or {},
                           "python -m schwingcheck curve run (a test)", True, made_by=made_by, how=how, n_select=n_select)


def fake_times(order):
    """Times shaped as speed() gives them, for drawing and printing, not for reading."""
    out = {}
    for e, engine in enumerate(CV.ENGINES):
        for k in (1, 7, 16, 32):
            for n in CV.WIDTHS:
                out[(engine, k, n)] = {"median_ms": 0.1 * (e + 1) * k * n, "max_ms": 0.2 * (e + 1) * k * n,
                                       "batch_ms": 0.05 * (e + 1) * k * n, "batch_max_ms": 0.06 * (e + 1) * k * n}
    return out


def fake_nuts():
    """NUTS's numbers shaped as nuts_speed() gives them: twenty fields together, one alone."""
    places = list(LEVELS[:len(LEVELS) - CV.NUTS_WIDTH + 1])

    def run(k, at):
        return {"fields": len(at), "build_s": 0.05 * k, "setup_s": 5.0 + 0.1 * k, "sample_s": 0.1 * k,
                "posterior_s": 0.01 * k, "gap": [1e-6 * (i + 1) for i in at], "mcse": [2e-6] * len(at),
                "rhat": [1.0 + 0.001 * i for i in at], "max_gap": 1e-6 * (max(at) + 1), "max_mcse": 2e-6,
                "max_rhat": 1.0 + 0.001 * max(at), "divergences": 0, "n_steps": 3000 + k, "at": list(at),
                "places": [places[i] for i in at], "columns": list(at)}
    return {k: {"together": run(k, list(range(len(places)))), "alone": run(k, [len(places) // 2])} for k in (7, 16, 32)}


def fake_how():
    """How the fake times were taken, fixed, so that the tables and figures drawn from them are."""
    pools = [{"library": "libblas-test.so", "api": "openblas", "threads": 1}]
    where = {"machine": {"platform": "Linux-test", "machine": "x86_64", "cpu_count": 4, "python": "3.13"},
             "versions": {"python": "3.13", "numpy": "2", "scipy": "1", "pytensor": "3", "pymc": "6", "numba": "0"},
             "threads": pools}
    places = list(LEVELS[:len(LEVELS) - CV.NUTS_WIDTH + 1])
    return {"speed": dict(where, calls=30, batch=128, batches=5, columns=20),
            "nuts": dict(where, width=3, draws=500, tune=500, chains=2, seed=7, columns=20, places=places,
                         alone=places[len(places) // 2])}


class SmallStudy(unittest.TestCase):
    def test_the_share_named_exactly_is_rule_pys(self):
        s = small_study()
        arm = s["arms"][0]
        sizes, logw = R.trapezoid(R.SYNTH["scale_sd"])
        for sub in ("seven", "prefix-09", "all"):
            idx = s["index"][sub]
            for n in (1, 3, 5, 9):
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
                self.assertEqual(row["n_answered"], int(said.sum()), (sub, n))

    def test_the_data_axis_pools_its_tables(self):
        s = small_study()
        row = s["rows"][("people-12-nominal", "typical", "seven", 3)]
        self.assertEqual(row["n_columns"], 2)
        self.assertEqual(row["n_fields"], 2 * 2 * (len(LEVELS) - 2))
        self.assertTrue(np.isfinite(row["exact_table_sd"]))
        self.assertTrue(np.isfinite(row["exact_se_tables"]))
        printed = s["rows"][("people-printed", "typical", "seven", 3)]
        self.assertEqual(printed["n_fields"], 2 * (len(LEVELS) - 2))
        self.assertTrue(math.isnan(printed["exact_se_tables"]))

    def test_the_record_holds_every_arm_and_the_floor(self):
        tree = small_record()
        ds = tree["rates"].to_dataset()
        self.assertEqual(ds["arm"].values.tolist(), ["nominal", "people-printed", "people-12-nominal", "people-12-predictive"])
        self.assertEqual(ds["width"].values.tolist(), [1, 3, 5, 9])
        self.assertTrue(np.isnan(float(ds["exact"].sel(arm="people-12-nominal", phenotype="typical", subset="all",
                                                        width=3))))
        floor = json.loads(tree.attrs["floor"])
        self.assertEqual(sorted(floor), ["nominal/six_lumbar", "nominal/typical"])


class Speed(unittest.TestCase):
    def setUp(self):
        self.pool = MS.pool()
        self.mu, self.sd = MS.arrays(self.pool)
        self.noise, self.power = MS.errors(self.pool), MS.powers(self.pool)
        self.values = CV.draw_pool(self.pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, 4).values

    def test_the_compiled_rule_builds_its_table_once(self):
        """The compiled namer builds its blocks once and names each field from the fields' side
        alone, as the numpy namer does, with the numpy rule's posterior."""
        idx, offsets, nodes = [0, 5, 11], np.arange(3), CV._nodes("trapezoid")
        X = C.fields(self.values, offsets)[0][:, idx, :]
        built, named = [], []

        def counting(real, calls):
            def make():
                f = real()

                def call(*a):
                    calls.append(1)
                    return f(*a)
                return call
            return make
        with mock.patch.object(K, "table_function", counting(K.table_function, built)), \
                mock.patch.object(K, "fields_function", counting(K.fields_function, named)):
            namer = CV._compiled_namer(self.mu[idx], self.sd[idx], self.noise[idx], self.power[idx], offsets, nodes)
            posts = [namer(X[i:i + 1]) for i in range(3)]
        self.assertEqual((len(built), len(named)), (1, 3))
        exact = CV._numpy_namer(self.mu[idx], self.sd[idx], self.noise[idx], self.power[idx], offsets, nodes)
        for i, post in enumerate(posts):
            np.testing.assert_allclose(post, exact(X[i:i + 1]), rtol=0, atol=1e-12)

    def test_the_prepared_rule_is_the_rule_to_the_bit(self):
        idx, offsets = [0, 5, 11, 20], np.arange(3)
        X = C.fields(self.values, offsets)[0][:, idx, :]
        X[3, 1, 2] = np.nan
        rule = K.ExactRule(self.mu[idx], self.sd[idx], noise=self.noise[idx], power=self.power[idx],
                           nodes=CV._nodes("trapezoid"))
        hyp = K.hypotheses(rule.n_levels, [offsets])
        subsets = {"all": [0, 1, 2, 3], "two": [1, 3]}
        a = rule.evaluate(X, hyp, subsets, chunk=7)
        b = rule.evaluate(X, hyp, subsets, chunk=7, prepared=rule.prepare(hyp))
        for name in subsets:
            np.testing.assert_array_equal(a[name]["logev"], b[name]["logev"])
            np.testing.assert_array_equal(a[name]["post"], b[name]["post"])

    def test_every_thread_pool_is_at_one_thread_inside_the_limit(self):
        """In a fresh interpreter, where nothing has loaded scipy yet, speed() with the compiled
        rule finds every pool at one thread inside the limit, scipy's own BLAS among them, which
        compiling loads; the limit entered first would leave it at every CPU's thread."""
        script = "\n".join([
            "import json, sys",
            "sys.path.insert(0, %r)" % ROOT,
            "from schwingcheck import curve as CV, measures as MS",
            "pool = MS.pool()",
            "values = CV.draw_pool(pool, 'typical', CV.SCORE_SEED, CV.EXTRA_SEED, 2).values",
            "times, how = CV.speed(pool, list(range(len(pool))), values, widths=(1,), ks=[2],",
            "                      engines=('pytensor-trapezoid',), calls=1, batch=2, batches=1, log=lambda *a: None)",
            "print(json.dumps(how['threads']))"])
        env = {k: v for k, v in os.environ.items() if not k.endswith("_NUM_THREADS")}
        done = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=1200, env=env)
        self.assertEqual(done.returncode, 0, done.stderr[-3000:])
        found = json.loads(done.stdout.strip().splitlines()[-1])
        self.assertTrue(found)
        self.assertEqual([p for p in found if p["threads"] != 1], [], found)

    def test_the_batch_is_timed_after_a_warm_up_at_its_own_size(self):
        """A namer slow at the first call of each size: the batch's time is the warmed one, the
        median and the largest of its calls, not the cold call's."""
        seen = {}

        def namer(X):
            first = len(X) not in seen
            seen[len(X)] = seen.get(len(X), 0) + 1
            time.sleep(0.2 if first else 0.002)
        t = CV.time_engine(namer, np.zeros((20, 1, 1)), calls=3, batch=8, batches=3)
        self.assertEqual(seen, {1: 4, 8: 4})
        self.assertLess(t["batch_max_ms"], 0.5 * 200.0 / 8)      # the cold call alone gives 25 ms a field
        self.assertLessEqual(t["batch_ms"], t["batch_max_ms"])
        self.assertLess(t["max_ms"], 0.5 * 200.0)

    def test_the_record_says_how_its_times_were_taken(self):
        s = small_study()
        values = self.values[:2]
        times, how = CV.speed(s["pool"], s["order"], values, widths=(1, 3), ks=[1, 7], engines=("numpy-trapezoid",),
                              calls=2, batch=4, batches=2, log=quiet)
        self.assertEqual((how["calls"], how["batch"], how["batches"], how["columns"]), (2, 4, 2, 2))
        self.assertEqual(how["fields"]["3"]["single"], {"places": ["C3", "C3"], "columns": [0, 1]})
        self.assertEqual(how["fields"]["3"]["batch"], {"places": ["C3", "C3", "C4", "C4"], "columns": [0, 1, 0, 1]})
        for name in ("python", "numpy", "scipy", "pytensor", "pymc", "numba"):
            self.assertIn(name, how["versions"])
        self.assertEqual(how["machine"]["cpu_count"], os.cpu_count())
        self.assertEqual([p for p in how["threads"] if p["threads"] != 1], [])
        self.assertEqual(set(times[("numpy-trapezoid", 7, 3)]), {"median_ms", "max_ms", "batch_ms", "batch_max_ms"})
        tree = small_record(times, {}, {"speed": how}, n_select=8)
        self.assertEqual(json.loads(tree.attrs["speed"])["batches"], 2)
        note = CR.table_speed(tree)[-1]
        self.assertIn("the median of 2 calls / per field in a batch of 4, the median of 2 such calls", note)
        self.assertIn("Every thread pool was at one thread inside the limit", note)
        self.assertEqual(json.loads(tree.attrs["counts"]),
                         {"score": 3, "select": 8, "anomalous": 2, "world_columns": 2, "worlds": {"12": 2}, "quick": True})
        for name in ("python", "scipy", "pytensor", "pymc", "numba"):
            self.assertIn(name, tree.attrs)

    def test_nuts_runs_on_every_place_and_on_one_field_alone(self):
        """One field at each place, the i-th from the i-th column, sampled together, and the middle
        one alone; each run's setup apart from its loop, each field's gap and R-hat, and every pool
        at one thread; the record's NUTS table names both runs and every place. A second of setup
        added before the sampler's own loop goes to setup_s and none of it to the loop's sample_s,
        which a field alone, 40 draws and 40 tuning steps of two chains, takes far less than."""
        values = CV.draw_pool(self.pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, CV.SPEED_COLUMNS).values
        delay, real = 1.0, MD.sample

        def slow_setup(*a, **kw):
            time.sleep(delay)
            return real(*a, **kw)
        with mock.patch.object(MD, "sample", slow_setup):
            out, how = CV.nuts_speed(self.pool, list(range(len(self.pool))), values, ks=(2,), draws=40, tune=40,
                                     log=quiet)
        together, alone = out[2]["together"], out[2]["alone"]
        places = list(LEVELS[:len(LEVELS) - CV.NUTS_WIDTH + 1])
        self.assertEqual((together["places"], together["columns"]), (places, list(range(len(places)))))
        self.assertEqual(how["places"], places)
        self.assertEqual(len(together["gap"]), len(places))
        self.assertTrue(np.all(np.isfinite(together["gap"])))
        self.assertEqual(together["max_gap"], max(together["gap"]))
        self.assertEqual((alone["fields"], alone["places"], how["alone"]), (1, [places[10]], places[10]))
        for run in (together, alone):
            for key in ("build_s", "setup_s", "sample_s", "posterior_s", "max_rhat", "divergences", "n_steps"):
                self.assertTrue(np.isfinite(run[key]), key)
            self.assertGreater(run["setup_s"], delay)
        self.assertLess(alone["sample_s"], delay)
        self.assertEqual([p for p in how["threads"] if p["threads"] != 1], [])
        tree = small_record(nuts=out, how={"nuts": how})
        lines = CR.table_nuts(tree)
        self.assertTrue(any(line.startswith("| 2 | together | 20 |") for line in lines))
        self.assertTrue(any(line.startswith("| 2 | alone, at T6 | 1 |") for line in lines))
        for place in places:
            self.assertTrue(any(line.startswith("| %s | " % place) for line in lines), place)


class Record(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="curve-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_record_names_the_code_the_run_began_with(self):
        began = {"digests": {"panjabi_long.csv": "a" * 64, "schwingcheck": "b" * 64},
                 "git": {"commit": "c" * 40, "package_changed": True}}
        tree = small_record(made_by=began)
        self.assertEqual(json.loads(tree.attrs["digests"]), began["digests"])
        self.assertEqual(json.loads(tree.attrs["git"]), began["git"])
        now = CV.code_state()
        moved = json.loads(tree.attrs["changed_during_run"])
        self.assertEqual({k: moved[k] for k in now["digests"]}, now["digests"])
        self.assertEqual(moved["git"], now["git"])
        self.assertEqual(json.loads(small_record().attrs["changed_during_run"]), {})

    def test_a_write_that_fails_leaves_the_record_that_was_there(self):
        record = os.path.join(self.tmp, "curve.nc")
        REC.write(small_record(), record)
        with open(record, "rb") as fh:
            before = fh.read()
        bad = small_record()
        bad["nuts"].attrs["unwritable"] = {"a": 1}             # HDF5 holds no dict: the write fails part way
        with self.assertRaises(Exception):
            REC.write(bad, record)
        with open(record, "rb") as fh:
            self.assertEqual(fh.read(), before)
        self.assertEqual(os.listdir(self.tmp), ["curve.nc"])

    def test_run_writes_the_scoring_before_the_times(self):
        """A run whose timing fails keeps its scoring on disk, named by the code it began with:
        the code's state is taken before the order is chosen, and the record carries that one."""
        s = small_study()
        began = {"digests": {"panjabi_long.csv": "1" * 64, "schwingcheck": "2" * 64},
                 "git": {"commit": "3" * 40, "package_changed": False}}
        events = []
        real = CV.code_state

        def state():
            events.append("state")
            return began if events.count("state") == 1 else real()

        def order(pool, cols, log=print):
            events.append("order")
            return s["order"], s["trace"]

        def no_times(*a, **kw):
            raise RuntimeError("the timing failed")
        outdir = os.path.join(self.tmp, "run")
        with mock.patch.object(CV, "code_state", state), \
                mock.patch.object(CV, "greedy_order", order), \
                mock.patch.object(CV, "make_arms", lambda pool, names, quick=False: s["arms"]), \
                mock.patch.object(CV, "run_arms", lambda arms, index, processes=1, log=print: s["rows"]), \
                mock.patch.object(CV, "timings", no_times):
            with self.assertRaises(RuntimeError):
                CV.run(outdir, "python -m schwingcheck curve run (a test)", quick=True, processes=1, log=quiet)
        self.assertEqual(events[:2], ["state", "order"])
        tree = REC.read(os.path.join(outdir, "curve.nc"))
        try:
            self.assertEqual(json.loads(tree.attrs["digests"]), began["digests"])
            self.assertEqual(json.loads(tree.attrs["counts"])["select"], CV.QUICK_COUNTS["select"])
            self.assertFalse(CR.timed(tree["speed"].to_dataset()))
            self.assertEqual(tree["rates"].to_dataset()["arm"].values.tolist()[0], "nominal")
        finally:
            tree.close()

    def test_add_speed_writes_its_times_through_records_write(self):
        record = os.path.join(self.tmp, "curve.nc")
        REC.write(small_record(), record)
        times, nuts, how = fake_times(small_study()["order"]), fake_nuts(), fake_how()
        written, events = [], []
        real, real_state = REC.write, CV.code_state

        def spy(tree, path):
            written.append(path)
            return real(tree, path)

        def state():
            events.append("state")
            return real_state()

        def timed(pool, order, values, quick=False, log=print):
            events.append("timings")
            return times, nuts, how
        with mock.patch.object(CV, "timings", timed), mock.patch.object(CV, "code_state", state), \
                mock.patch.object(REC, "write", spy):
            CV.add_speed(record, "python -m schwingcheck curve speed (a test)", quick=True, log=quiet)
        self.assertEqual(written, [record])
        self.assertEqual(events, ["state", "timings", "state"])     # taken before the timing, and after it
        tree = REC.read(record)
        try:
            self.assertEqual(json.loads(tree.attrs["speed"])["calls"], 30)
            self.assertEqual(json.loads(tree.attrs["nuts"])["alone"], "T6")
            self.assertEqual(set(json.loads(tree.attrs["speed_digests"])), {"panjabi_long.csv", "schwingcheck"})
            self.assertIn("commit", json.loads(tree.attrs["speed_git"]))
            self.assertEqual(json.loads(tree.attrs["speed_changed_during_run"]), {})
            self.assertTrue(CR.timed(tree["speed"].to_dataset()))
            self.assertTrue(CR.timed(tree["nuts"].to_dataset()))
        finally:
            tree.close()


class Report(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="curve-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_check_readme_holds_the_tables_and_finds_what_differs(self):
        tree = small_record(fake_times(small_study()["order"]), fake_nuts(), fake_how())
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

    def test_the_data_table_reads_every_table_against_the_printed_one(self):
        tree = small_record()
        lines = CR.table_data(tree)
        self.assertTrue(lines[2].startswith("| as printed | - | 1 | "), lines[2])
        ds = CR.rates_of(tree)
        x = CR.value(ds, "exact", "people-12-nominal", "typical", "seven", 3)
        ref = CR.value(ds, "exact", "people-printed", "typical", "seven", 3)
        row = next(line for line in lines if line.startswith("| 12 | nominal |"))
        self.assertEqual(row.split(" | ")[4], CR.points(x - ref))
        se, se_tables = (CR.value(ds, s, "people-12-nominal", "typical", "seven", 3) for s in ("exact_se", "exact_se_tables"))
        self.assertEqual(row.split(" | ")[3], "%s (%s / %s)" % (CR.pct(x), CR.se_points(se), CR.se_points(se_tables)))
        text = flat("\n".join(lines))
        self.assertIn("against which every other row is read", text)
        self.assertIn("1 at 12 people", text)

    def test_the_arms_and_anomalous_tables_say_what_they_hold(self):
        tree = small_record()
        self.assertIn("not what treating the measures as independent costs", flat("\n".join(CR.table_arms(tree))))
        lines = CR.table_anomalous(tree)
        self.assertIn("Seven, 5 bodies", lines[0])
        typical = next(line for line in lines if line.startswith("| Typical |"))
        ds = CR.rates_of(tree)
        self.assertIn("%s / %s" % (CR.pct(CR.value(ds, "exact", "nominal", "typical", "seven", 5)),
                                   CR.pct(CR.value(ds, "within_one", "nominal", "typical", "seven", 5))), typical)

    def test_the_curve_commands_run_on_a_record(self):
        tree = small_record(fake_times(small_study()["order"]), fake_nuts(), fake_how())
        record = os.path.join(self.tmp, "curve.nc")
        REC.write(tree, record)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            self.assertEqual(MAIN.main(["curve", "table", "--record", record]), 0)
        text = printed.getvalue()
        for name in CR.TABLES:
            self.assertIn("<!-- curve:%s -->" % name, text)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(MAIN.main(["curve", "figures", "--record", record, "--outdir", os.path.join(self.tmp, "fig")]), 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "fig", "FIGURES.md")))
        readme = os.path.join(self.tmp, "README.md")
        with open(readme, "w", encoding="ascii") as fh:
            fh.write("# A README\n\n" + text)
        with mock.patch.object(CR, "README", readme), contextlib.redirect_stdout(io.StringIO()) as said:
            self.assertEqual(MAIN.main(["curve", "check", "--record", record]), 0)
        self.assertIn("the README's tables are the record's", said.getvalue())
        with open(readme, "w", encoding="ascii") as fh:
            fh.write("# A README with no tables\n")
        with mock.patch.object(CR, "README", readme), contextlib.redirect_stdout(io.StringIO()) as said:
            self.assertEqual(MAIN.main(["curve", "check", "--record", record]), 1)
        self.assertIn("table curve: not in the README", said.getvalue())

    def test_the_figures_are_the_same_files_when_drawn_twice(self):
        tree = small_record(fake_times(small_study()["order"]), fake_nuts(), fake_how())
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
        with open(os.path.join(self.tmp, "a", "curve_speed.caption.txt"), encoding="ascii") as fh:
            caption = fh.read()
        self.assertIn("median of 30 calls", caption)
        self.assertIn("a batch of 128 (points, median of 5 calls)", caption)
        with open(os.path.join(self.tmp, "a", "curve_data.csv"), encoding="ascii") as fh:
            printed = [r for r in csv.DictReader(fh) if r["rule"] == "printed"]
        self.assertEqual(sorted((r["panel"], r["subset"]) for r in printed),
                         [("A", "prefix-32"), ("A", "seven"), ("B", "prefix-32"), ("B", "seven")])
        tree.close()


if __name__ == "__main__":
    unittest.main()
