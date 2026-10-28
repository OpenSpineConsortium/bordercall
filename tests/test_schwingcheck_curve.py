"""Step e's build-up study (curve.py, curve_report.py) on columns small enough for a test.

Rung 0 is the record's: the seven's values in the study's columns are the values rescore draws
from seed 97, whatever the other 25 measures, so the seven's rates can be held to exact.json. The
subsets are what their names say: each prefix of the order holds as many measures as its number,
the ladder's first rung is the seven and the pedicles and its last all 32, and the families with
the seven make up the pool. The five anomalous phenotypes' columns are the same patients, the same
at every body they share by name but the rib-bearing L1 and the ribless T12. The SD a predictive
rule takes for a new person about twelve is exact.py's. A field is floored only by a value at the
floor in a measure that scales with the size. One small study, seven arms of a few columns, is
scored on one process; the share it names exactly is the share rule.py's posterior names, counted
here by hand; its record prints every table, check_readme holds a README that carries them and
finds one that is stale, missing or doubled, and its figures, drawn twice, are the same files.

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

Each fix of the second review, the same day, is held the same way: the anomalous columns judged
by their own names, the rib reading on t13 and the count from C2 on lumbar_rib and no_rib_t12; the
widths the arms are scored at and the times taken at, as the docstrings and the README say; the
data axis's lower bound on the fewest fields one table answered; the prepared blocks' shape;
nuts_speed()'s thread pools in a fresh interpreter of its own; the batch's median told from its
mean, and what its warm-up keeps; each NUTS field's gap from its own exact posterior, the first
posterior call's compile in the setup and not in posterior_s, and the files each run added to
the Numba cache; the speed caption's counts read from the record; and captions and notes that
name what the record does not give, never a fixed one thread or a count's place filled with it.

The full run's record of 28 October 2026 is held as committed: the package's README carries its
tables; its figures' numbers and captions are what the code as it stands draws from it, and
FIGURES.md names that code; and the run changed no code it names. So is what the report gained
after that run: 100.0% and 100.00% mean every field and 0.0% none, a share short of all or above
none taking more places, up to six; counts with their thousands marked; the anomalous table's
answers at 0.99 and how often they are right, read against the record itself, with the standard
errors where a field was wrong; the floor table's measures and levels by count, in the other
tables' order, each row with its own counts; panel C drawing no share right on fewer than 1,000
fields, and its CSV giving the fields each share rests on; the speed figure's axes labelled 0.1, 1
and 10; and, as the README reads the anomalous table, with all 32 measures at nine bodies on the
first 30 columns of each spine, every field named wrong at 0.99 reaches a body no place names: on
six-lumbar spines exactly the fields that reach the L6, on T13 spines fields with the T11, T12 or
T13 in the middle.
"""
from __future__ import annotations

import contextlib
import csv
import hashlib
import inspect
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
import neighbour as NB                         # noqa: E402
import panjabi as P                            # noqa: E402
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
PACKAGE_README = os.path.join(ROOT, "schwingcheck", "README.md")


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
        # and the README says so: the nominal arm at 1, 3, 5 and 9 bodies, every other arm at 1, 3 and 9
        self.assertEqual({a.widths for a in quick_arms() if a.name != "nominal"}, {CV.WIDTHS})
        self.assertEqual((CV.NOMINAL_WIDTHS, CV.WIDTHS), ((1, 3, 5, 9), (1, 3, 9)))
        with open(PACKAGE_README, encoding="ascii") as fh:
            readme = flat(fh.read())
        self.assertIn("The nominal arm scores every subset at 1, 3, 5 and 9 bodies, the others the prefixes and the "
                      "seven at 1, 3 and 9.", readme)

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
        # each column is judged by its own names: by the archive's two conventions, the rib reading
        # on t13 and the count from C2 on lumbar_rib and no_rib_t12, the two agreeing elsewhere
        for ph in CV.ANOMALOUS:
            levels, t, _, _ = C.phenotype_levels(ph)
            column = P.Column(levels=list(levels), values={}, phenotype=ph, transitional_at=t)
            ribs = ["T13" if o is None else NB.COUNT_NAMES[o] for o in NB.rib_ordinals(column)]
            self.assertEqual(levels == ribs, ph in ("t13", "six_lumbar", "four_lumbar"), ph)
            self.assertEqual(levels == NB.COUNT_NAMES[:len(levels)], ph != "t13", ph)
        for ph, name in (("t13", "T13"), ("lumbar_rib", "L1"), ("no_rib_t12", "T12")):
            levels, t, _, _ = C.phenotype_levels(ph)
            self.assertEqual(CV.true_positions(np.array([t]), np.array([0]), [levels], 1)[0], CV.POSITION[name], ph)
        self.assertIn("by its own column's name for it", flat(CV.true_positions.__doc__))
        self.assertNotIn("count", CV.true_positions.__doc__)          # the count from C2 is one convention of two
        report = flat("\n".join(CR.table_anomalous(small_record())))
        on_t13 = ("the rib reading, which calls the thirteenth rib-bearing body T13 where the count from C2 "
                  "calls it L1")
        on_the_new = ("the count from C2, under which the rib-bearing L1 stays L1 and the ribless T12 stays T12 "
                      "where the rib reading calls them T13 and L1")
        for text in (doc, report):
            self.assertNotIn("(the rib reading: a thirteenth rib-bearing body is T13)", text)
            self.assertIn(on_t13, text)
            self.assertIn(on_the_new, text)
            self.assertIn("the two agree", text)
        self.assertIn("on a lumbar_rib or no_rib_t12 column the count from C2", doc)
        self.assertIn("with a rib on L1 or no rib on T12 they are the count from C2", report)

    def test_the_five_anomalous_phenotypes_are_drawn_for_the_same_patients(self):
        """The study's anomalous columns of every phenotype are the same patients as the typical
        columns of their seeds, as the README and TODO.md say: the same sizes, and the same values
        at every body they share by name but the rib-bearing L1 and the ribless T12, which the
        generator draws half-way between T12 and L1, so the five rows are paired, not independent
        samples."""
        pool = MS.pool()
        n = CV.study_counts(False)["anomalous"]
        typical = CV.draw_pool(pool, "typical", CV.ANOMALOUS_SEED, CV.ANOMALOUS_EXTRA_SEED, n)
        odd = {"lumbar_rib": "L1", "no_rib_t12": "T12"}
        for ph in CV.ANOMALOUS:
            cols = CV.draw_pool(pool, ph, CV.ANOMALOUS_SEED, CV.ANOMALOUS_EXTRA_SEED, n)
            np.testing.assert_array_equal(cols.scale, typical.scale)
            for k in range(n):
                names = list(typical.levels[k])
                for i, name in enumerate(cols.levels[k]):
                    if name in names:
                        same = np.array_equal(cols.values[k, i], typical.values[k, names.index(name)], equal_nan=True)
                        self.assertEqual(same, name != odd.get(ph), (ph, k, name))

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

    def test_the_fields_wrong_at_099_are_the_ones_no_place_names(self):
        """With all 32 measures at nine bodies, on the first 30 of the study's columns of each spine
        (seeds 99 and 314), every six-lumbar field is named at 0.99 and the wrong ones are exactly
        the fields that reach the L6, one a column, since the rule has no place below L5; on a T13
        spine every field whose middle body is the T13 is wrong, named or not, and every field
        wrong at 0.99 has the T13 or one of the two bodies above it in the middle. The README
        reads the anomalous table by this."""
        pool = MS.pool()
        mu, sd = MS.arrays(pool)
        noise, power = MS.errors(pool), MS.powers(pool)
        offsets, nodes = np.arange(9), R.trapezoid(R.SYNTH["scale_sd"])
        for ph in ("six_lumbar", "t13"):
            c = CV.draw_pool(pool, ph, CV.ANOMALOUS_SEED, CV.ANOMALOUS_EXTRA_SEED, 30)
            X, start, col = C.fields(c.values, offsets)
            LL = R.loglik(X, offsets, mu, sd, R.SYNTH, sizes=nodes[0], noise=noise, power=power)
            post = R.posterior(R.logsumexp(LL.sum(2) + nodes[1], 2))
            st = CV.field_stats(post, start, CV.true_positions(start, col, c.levels, 9), 9, False)
            named = st["top"] >= CV.CLAIM
            middle = np.array([c.levels[k][s + 4] for s, k in zip(start, col)])
            bottom = np.array([c.levels[k][s + 8] for s, k in zip(start, col)])
            wrong = named & ~st["hit"]
            with self.subTest(ph):
                if ph == "six_lumbar":
                    self.assertTrue(named.all())
                    self.assertEqual(wrong.tolist(), (bottom == "L6").tolist())
                    self.assertEqual(int(wrong.sum()), 30)
                else:
                    self.assertFalse(st["hit"][middle == "T13"].any())
                    self.assertTrue(wrong.any())
                    self.assertTrue(set(middle[wrong]) <= {"T11", "T12", "T13"}, set(middle[wrong]))


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

    def test_the_data_axis_bounds_the_precision_on_the_fewest_one_table_answered(self):
        """The data axis's tables answer the same fields: a table pooled with itself has the one
        table's bound, 0.025 ** (1 / 18), not 0.025 ** (1 / 36), and pooled with a table that
        answered 10 of the same fields, that table's; a table that answered none adds nothing,
        and an error in either table leaves no bound."""
        group = np.arange(40) % 10
        one = self.stats()
        parts = {"col": [group, group], "world": [0, 1], "stats": [{"s": one}, {"s": one}]}
        row = CV.pooled_rates(parts, "s")
        self.assertEqual((row["n_answered"], row["errors"], row["precision"]), (36, 0, 1.0))
        self.assertEqual(row["precision_lower"], CV.rates(one, group)["precision_lower"])
        self.assertAlmostEqual(row["precision_lower"], 0.025 ** (1.0 / 18), places=15)
        parts["stats"][1] = {"s": self.stats(answered=10)}
        row = CV.pooled_rates(parts, "s")
        self.assertEqual(row["n_answered"], 28)
        self.assertAlmostEqual(row["precision_lower"], 0.025 ** (1.0 / 10), places=15)
        parts["stats"][1] = {"s": self.stats(answered=0)}
        self.assertAlmostEqual(CV.pooled_rates(parts, "s")["precision_lower"], 0.025 ** (1.0 / 18), places=15)
        wrong = self.stats()
        wrong["hit"][0] = False
        parts["stats"][1] = {"s": wrong}
        self.assertTrue(math.isnan(CV.pooled_rates(parts, "s")["precision_lower"]))
        self.assertIn("over the count of the table that answered fewest", flat(CV.__doc__))
        self.assertIn("the one that answered fewest", CR.DATA_BOUND_NOTE)

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
        self.assertEqual(cell, "100.00%% (at least %s)" % CR.pct_down(lower, 2))
        self.assertLessEqual(float(CR.pct_down(lower, 2)[:-1]), 100.0 * lower)
        text = "\n".join(CR.table_curve(tree))
        self.assertIn(cell, text)
        self.assertIn(CR.BOUND_NOTE, text)
        self.assertIn("rounded down", CR.BOUND_NOTE)

    def test_the_lower_bound_is_rounded_down(self):
        """The bound beside a precision with no field wrong never reads above the bound: with none
        wrong of 27,970 answered it is 99.9868%, printed at least 99.98%, where rounding to the
        nearest would print 99.99%."""
        for n, printed in ((27970, "99.98%"), (515, "99.28%"), (18, "81.46%"), (1000, "99.63%")):
            self.assertEqual(CR.pct_down(0.025 ** (1.0 / n)), printed, n)
        self.assertEqual(CR.pct_down(float("nan")), "-")
        ds = CR.rates_of(small_record())
        cell = dict(arm="nominal", phenotype="typical", subset="prefix-32", width=9)
        ds["precision"].loc[cell] = 1.0
        ds["precision_lower"].loc[cell] = 0.025 ** (1.0 / 27970)
        self.assertEqual(CR.precision_cell(ds, "nominal", "typical", "prefix-32", 9), "100.00% (at least 99.98%)")


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
    """NUTS's numbers shaped as nuts_speed() gives them: twenty fields together, one alone, the
    first run alone adding files to the Numba cache, as a run that compiled its graph does."""
    places = list(LEVELS[:len(LEVELS) - CV.NUTS_WIDTH + 1])

    def run(k, at, cache_files):
        return {"fields": len(at), "build_s": 0.05 * k, "setup_s": 5.0 + 0.1 * k, "sample_s": 0.1 * k,
                "posterior_s": 0.01 * k, "gap": [1e-6 * (i + 1) for i in at], "mcse": [2e-6] * len(at),
                "rhat": [1.0 + 0.001 * i for i in at], "max_gap": 1e-6 * (max(at) + 1), "max_mcse": 2e-6,
                "max_rhat": 1.0 + 0.001 * max(at), "divergences": 0, "n_steps": 3000 + k, "at": list(at),
                "places": [places[i] for i in at], "columns": list(at), "cache_files": cache_files}
    return {k: {"together": run(k, list(range(len(places))), 3 if k == 7 else 0), "alone": run(k, [len(places) // 2], 0)}
            for k in (7, 16, 32)}


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
        prepared = rule.prepare(hyp)
        b = rule.evaluate(X, hyp, subsets, chunk=7, prepared=prepared)
        # (measures, 3 x bodies, 4 x nodes x hypotheses), as prepare's docstring says
        self.assertEqual(prepared.shape, (4, 3 * 3, 4 * rule.scaled.shape[1] * len(hyp)))
        self.assertIn("(measures, 3 x bodies, 4 x nodes x hypotheses)", flat(K.ExactRule.prepare.__doc__))
        for name in subsets:
            np.testing.assert_array_equal(a[name]["logev"], b[name]["logev"])
            np.testing.assert_array_equal(a[name]["post"], b[name]["post"])

    def test_every_thread_pool_is_at_one_thread_inside_the_limit(self):
        """In a fresh interpreter, where nothing has loaded scipy yet, speed() with the compiled
        rule finds every pool at one thread inside the limit, scipy's own BLAS among them, which
        compiling loads; the limit entered first would leave it at every CPU's thread. So does
        nuts_speed(), in a fresh interpreter of its own: in this one the tests before it have
        loaded scipy, and the NUTS test's own check of the pools passes whatever it compiles
        before its limit."""
        calls = {"speed": ["times, how = CV.speed(pool, list(range(len(pool))), values, widths=(1,), ks=[2],",
                           "                      engines=('pytensor-trapezoid',), calls=1, batch=2, batches=1,",
                           "                      log=lambda *a: None)"],
                 "nuts_speed": ["out, how = CV.nuts_speed(pool, list(range(len(pool))), values, ks=(2,), draws=40,",
                                "                         tune=40, log=lambda *a: None)"]}
        env = {k: v for k, v in os.environ.items() if not k.endswith("_NUM_THREADS")}
        for name, call in calls.items():
            script = "\n".join([
                "import json, sys",
                "sys.path.insert(0, %r)" % ROOT,
                "from schwingcheck import curve as CV, measures as MS",
                "pool = MS.pool()",
                "values = CV.draw_pool(pool, 'typical', CV.SCORE_SEED, CV.EXTRA_SEED, 2).values"]
                + call + ["print(json.dumps(how['threads']))"])
            with self.subTest(name):
                done = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=1200,
                                      env=env)
                self.assertEqual(done.returncode, 0, done.stderr[-3000:])
                found = json.loads(done.stdout.strip().splitlines()[-1])
                self.assertTrue(found)
                self.assertEqual([p for p in found if p["threads"] != 1], [], found)

    def test_the_batch_is_timed_after_a_warm_up_at_its_own_size(self):
        """A namer slow at the first call of each size, and at the third of the batch's five warmed
        calls: the batch's time is the median of the warmed calls, which that one slow call leaves
        at the fast calls' time where a mean would not, and its largest is that slow call, not the
        cold call's. The docstring says what the warm-up keeps out of the times, and that it keeps
        almost none of the batch's memory."""
        seen = {}

        def namer(X):
            seen[len(X)] = seen.get(len(X), 0) + 1
            first, third = seen[len(X)] == 1, len(X) == 8 and seen[8] == 4
            time.sleep(0.2 if first else 0.05 if third else 0.002)
        t = CV.time_engine(namer, np.zeros((20, 1, 1)), calls=3, batch=8, batches=5)
        self.assertEqual(seen, {1: 4, 8: 6})
        self.assertLess(t["batch_ms"], 1e3 * 0.05 / 8 / 5)          # a mean of the five is at least 1.25 ms a field
        self.assertGreaterEqual(t["batch_max_ms"], 1e3 * 0.05 / 8)  # the slow warmed call, 6.25 ms a field
        self.assertLess(t["batch_max_ms"], 0.5 * 200.0 / 8)         # the cold call alone gives 25 ms a field
        self.assertLess(t["max_ms"], 0.5 * 200.0)
        doc = flat(CV.time_engine.__doc__)
        self.assertIn("keeps that size's first call out of the times", doc)
        self.assertIn("every timed batch call takes that memory afresh", doc)
        self.assertNotIn("warms the caches and the memory", doc)

    def test_the_record_says_how_its_times_were_taken(self):
        s = small_study()
        values = self.values[:2]
        times, how = CV.speed(s["pool"], s["order"], values, widths=(1, 3), ks=[1, 7], engines=("numpy-trapezoid",),
                              calls=2, batch=4, batches=3, log=quiet)
        self.assertEqual((how["calls"], how["batch"], how["batches"], how["columns"]), (2, 4, 3, 2))
        self.assertEqual(how["fields"]["3"]["single"], {"places": ["C3", "C3"], "columns": [0, 1]})
        self.assertEqual(how["fields"]["3"]["batch"], {"places": ["C3", "C3", "C4", "C4"], "columns": [0, 1, 0, 1]})
        for name in ("python", "numpy", "scipy", "pytensor", "pymc", "numba"):
            self.assertIn(name, how["versions"])
        self.assertEqual(how["machine"]["cpu_count"], os.cpu_count())
        self.assertEqual([p for p in how["threads"] if p["threads"] != 1], [])
        self.assertEqual(set(times[("numpy-trapezoid", 7, 3)]), {"median_ms", "max_ms", "batch_ms", "batch_max_ms"})
        tree = small_record(times, {}, {"speed": how}, n_select=8)
        self.assertEqual(json.loads(tree.attrs["speed"])["batches"], 3)
        note = CR.table_speed(tree)[-1]
        self.assertIn("the median of 2 calls / per field in a batch of 4, the median of 3 such calls", note)
        self.assertIn("Every thread pool was at one thread inside the limit", note)
        self.assertEqual(json.loads(tree.attrs["counts"]),
                         {"score": 3, "select": 8, "anomalous": 2, "world_columns": 2, "worlds": {"12": 2}, "quick": True})
        for name in ("python", "scipy", "pytensor", "pymc", "numba"):
            self.assertIn(name, tree.attrs)
        # the study's times are taken at speed()'s own widths, 1, 3 and 9 bodies, as the docstring says
        self.assertEqual(inspect.signature(CV.speed).parameters["widths"].default, (1, 3, 9))
        asked = []
        with mock.patch.object(CV, "speed", lambda *a, **kw: asked.append((a, kw)) or ({}, {})), \
                mock.patch.object(CV, "nuts_speed", lambda *a, **kw: ({}, {})):
            CV.timings(s["pool"], s["order"], values, quick=True, log=quiet)
        self.assertEqual((len(asked), len(asked[0][0])), (1, 3))
        self.assertNotIn("widths", asked[0][1])
        doc = flat(CV.__doc__)
        self.assertIn("is measured at every prefix of the order and at 1, 3 and 9 bodies", doc)
        self.assertNotIn("every prefix of the order and every width", doc)

    def test_nuts_runs_on_every_place_and_on_one_field_alone(self):
        """One field at each place, the i-th from the i-th column, sampled together, and the middle
        one alone; each run's setup apart from its loop, each field's gap from its own exact
        posterior, its R-hat, the files the run added to PyTensor's Numba cache, and every pool at
        one thread; the record's NUTS table names both runs and every place, and which run compiled
        its graph. A second of setup added before the sampler's own loop goes to setup_s and none
        of it to the loop's sample_s, which a field alone, 40 draws and 40 tuning steps of two
        chains, takes far less than. A second added to each model's first hypothesis_posterior
        call, the one that compiles p(h | x, s), goes to setup_s too and none of it to posterior_s,
        the second call's time a field. The second call returns the first's answer at once here: a
        real one does the work again, and on a busy machine can take as long as the first with its
        added second, when no bound on the times tells which call posterior_s was taken from. The
        exact posterior is asked of the trapezoid's nodes, the rule's throughout, since no gap at two
        measures tells it from the Gauss-Hermite rule's, which differs from it there by under 1e-14."""
        values = CV.draw_pool(self.pool, "typical", CV.SCORE_SEED, CV.EXTRA_SEED, CV.SPEED_COLUMNS).values
        delay, real, posterior = 1.0, MD.sample, MD.hypothesis_posterior
        own, answered, returned = [], [], []      # pm.sample's time less its loop; each model with its answer
        cache = iter([5, 5, 9, None, 9])          # the cache's files: when NUTS begins, then before and after each run

        def slow_setup(*a, **kw):
            time.sleep(delay)
            t = time.perf_counter()
            idata = real(*a, **kw)
            own.append(time.perf_counter() - t - idata.posterior.attrs["sampling_time"])
            return idata

        def slow_first_posterior(model, *a, **kw):
            # by the model itself, not its id, which a later object may reuse
            got = next((got for m, got in answered if m is model), None)
            if got is None:
                time.sleep(delay)                  # in its first call, the one that compiles p(h | x, s)
                got = posterior(model, *a, **kw)
                answered.append((model, got))
            returned.append(got[0])
            return got
        kinds, nodes = [], CV._nodes

        def asked_nodes(kind):
            kinds.append(kind)
            return nodes(kind)
        with mock.patch.object(MD, "sample", slow_setup), \
                mock.patch.object(MD, "hypothesis_posterior", slow_first_posterior), \
                mock.patch.object(CV, "numba_cache_files", lambda: next(cache)), \
                mock.patch.object(CV, "_nodes", asked_nodes):
            out, how = CV.nuts_speed(self.pool, list(range(len(self.pool))), values, ks=(2,), draws=40, tune=40,
                                     log=quiet)
        together, alone = out[2]["together"], out[2]["alone"]
        self.assertEqual(kinds, ["trapezoid"])                          # once for the one count of measures
        places = list(LEVELS[:len(LEVELS) - CV.NUTS_WIDTH + 1])
        self.assertEqual((together["places"], together["columns"]), (places, list(range(len(places)))))
        self.assertEqual(how["places"], places)
        self.assertEqual(len(together["gap"]), len(places))
        self.assertTrue(np.all(np.isfinite(together["gap"])))
        self.assertEqual(together["max_gap"], max(together["gap"]))
        self.assertEqual((alone["fields"], alone["places"], how["alone"]), (1, [places[10]], places[10]))
        # Each field's gap is from that field's own exact posterior, so a field compared with
        # another's, or the gap taken over the fields, fails: the i-th place's field of the i-th
        # column, picked by its place and column, named by rule.py on the trapezoid at the order's
        # first two measures, against the answer of the second hypothesis_posterior call.
        offsets, idx = np.arange(CV.NUTS_WIDTH), [0, 1]
        X, start, col = C.fields(values, offsets)
        rows = [int(np.flatnonzero((start == i) & (col == i))[0]) for i in range(len(places))]
        sizes, logw = R.trapezoid(R.SYNTH["scale_sd"])
        LL = R.loglik(X[rows][:, idx, :], offsets, self.mu[idx], self.sd[idx], R.SYNTH, sizes=sizes,
                      noise=self.noise[idx], power=self.power[idx])
        exact = R.posterior(R.log_evidence(LL, logw))
        self.assertEqual((len(answered), len(returned)), (2, 4))
        for run, post in ((together, returned[1]), (alone, returned[3])):
            np.testing.assert_allclose(run["gap"], np.abs(post - exact[run["at"]]).max(1), rtol=0, atol=1e-12)
        for run, setup in zip((together, alone), own):
            for key in ("build_s", "setup_s", "sample_s", "posterior_s", "max_rhat", "divergences", "n_steps"):
                self.assertTrue(np.isfinite(run[key]), key)
            self.assertGreater(run["setup_s"] - setup, 1.5 * delay)          # both added seconds, not one
            self.assertLess(run["posterior_s"] * run["fields"], delay / 4)     # and neither in posterior_s
        self.assertLess(alone["sample_s"], delay)
        self.assertEqual([p for p in how["threads"] if p["threads"] != 1], [])
        # the cache held 5 files when NUTS began; the together run added 4, and the alone run's
        # count could not be read before it began, so it is not recorded
        self.assertEqual((how["cache_files"], together["cache_files"]), (5, 4))
        self.assertTrue(math.isnan(alone["cache_files"]))
        tree = small_record(nuts=out, how={"nuts": how})
        lines = CR.table_nuts(tree)
        self.assertTrue(any(line.startswith("| 2 | together | 20 |") and line.endswith(" | 4 |") for line in lines))
        self.assertTrue(any(line.startswith("| 2 | alone, at T6 | 1 |") and line.endswith(" | - |") for line in lines))
        self.assertIn("Files added to the Numba cache", lines[0])
        for place in places:
            self.assertTrue(any(line.startswith("| %s | " % place) for line in lines), place)
        self.assertIn("Compiled: 2 measures together; compiled already: none. The cache's files are not recorded "
                      "for 2 measures alone.", lines[-1])

    def test_the_numba_cache_is_counted_where_pytensor_keeps_it(self):
        """numba_cache_files counts the files of PyTensor's Numba cache, base_compiledir/numba,
        and gives None where the folder cannot be read; the docstring says which flag moves it, and
        a record whose runs do not say whether they compiled says so."""
        from pytensor.link.numba import cache
        folder = os.path.join(tempfile.mkdtemp(prefix="curve-test-"), "numba")
        try:
            os.makedirs(os.path.join(folder, "a folder"))
            for i in range(3):
                with open(os.path.join(folder, "f%d.nbc" % i), "w", encoding="ascii") as fh:
                    fh.write("x")
            with mock.patch.object(cache, "NUMBA_CACHE_PATH", folder):
                self.assertEqual(CV.numba_cache_files(), 3)
            with mock.patch.object(cache, "NUMBA_CACHE_PATH", os.path.join(folder, "missing")):
                self.assertIsNone(CV.numba_cache_files())
        finally:
            shutil.rmtree(os.path.dirname(folder), ignore_errors=True)
        from pytensor import config
        self.assertEqual(str(cache.NUMBA_CACHE_PATH), os.path.join(str(config.base_compiledir), "numba"))
        self.assertIn("base_compiledir, not compiledir", flat(CV.__doc__))
        nuts = fake_nuts()
        for k in nuts:
            for run in nuts[k].values():
                del run["cache_files"]
        lines = CR.table_nuts(small_record(fake_times(small_study()["order"]), nuts, fake_how()))
        self.assertTrue(lines[2].endswith(" | - |"), lines[2])
        self.assertIn("Whether each run compiled its graph or found it compiled already is not recorded.", lines[-1])


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

    def test_a_share_reads_100_only_when_all_and_0_only_when_none(self):
        """A share short of all reads short of 100, and one above none above 0, with as many places
        as that takes, up to six, so that 100.0% and 100.00% mean every field and 0.0% none; within
        5e-9 of all or of none, closer than six places show, it still reads 100 or 0. A count
        carries its thousands marks."""
        self.assertEqual([CR.pct(1.0), CR.pct(1.0, 2), CR.pct(0.0), CR.pct(float("nan"))],
                         ["100.0%", "100.00%", "0.0%", "-"])
        self.assertEqual([CR.pct(0.9996), CR.pct(27999 / 28000), CR.pct(27999 / 28000, 2), CR.pct(0.731)],
                         ["99.96%", "99.996%", "99.996%", "73.1%"])
        self.assertEqual([CR.pct(1 / 28000), CR.pct(0.0004), CR.pct(0.0004, 2)], ["0.004%", "0.04%", "0.04%"])
        self.assertEqual(CR.pct(1 - 1e-12), "%.*f%%" % (CR.PCT_MOST_PLACES, 100.0))
        self.assertEqual([CR.count(2000), CR.count(200.0), CR.count(float("nan"))], ["2,000", "200", "-"])

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
        self.assertEqual(lines[-1], CR.DATA_BOUND_NOTE)          # its tables answer the same fields

    def test_the_arms_and_anomalous_tables_say_what_they_hold(self):
        tree = small_record()
        self.assertIn("not what treating the measures as independent costs", flat("\n".join(CR.table_arms(tree))))
        lines = CR.table_anomalous(tree)
        self.assertIn("Seven, 5 bodies", lines[0])
        typical = next(line for line in lines if line.startswith("| Typical |"))
        ds = CR.rates_of(tree)
        self.assertIn("%s / %s" % (CR.pct(CR.value(ds, "exact", "nominal", "typical", "seven", 5)),
                                   CR.pct(CR.value(ds, "within_one", "nominal", "typical", "seven", 5))), typical)

    def test_the_anomalous_table_says_whether_the_answers_at_099_stay_right(self):
        """Beside each spine's shares named exactly and within one level, the anomalous table gives
        the share named at 0.99 and the share of those right, for the seven and all 32, judged by
        the column's own names, and says on how many columns and, where a field named at 0.99 was
        wrong, the standard error of the share right; a spine the record did not score is named as
        such."""
        tree = small_record()
        lines = CR.table_anomalous(tree)
        at = next(i for i, line in enumerate(lines) if "named at 0.99 / right of those" in line)
        self.assertGreater(at, 2)
        ds = CR.rates_of(tree)
        six = next(line for line in lines[at:] if line.startswith("| Six lumbar |")).strip("| ").split(" | ")
        for cell, sub in ((1, "seven"), (4, "prefix-32")):
            answered = float(ds["answered"].sel(arm="nominal", phenotype="six_lumbar", subset=sub, width=3))
            self.assertEqual(six[cell], "%s / %s" % (CR.pct(answered),
                                                     CR.precision_cell(ds, "nominal", "six_lumbar", sub, 3)))
        self.assertEqual(six[2], "- / -")                  # six lumbar is scored at three bodies alone here
        typical = next(line for line in lines[at:] if line.startswith("| Typical |")).strip("| ").split(" | ")
        for j, sub in enumerate(("seven", "prefix-32")):
            for w, n in enumerate(CR.ANOMALOUS_WIDTHS):
                answered = float(ds["answered"].sel(arm="nominal", phenotype="typical", subset=sub, width=n))
                self.assertEqual(typical[1 + 3 * j + w], "%s / %s" % (CR.pct(answered), CR.precision_cell(
                    ds, "nominal", "typical", sub, n)), (sub, n))
        self.assertGreater(CR.value(ds, "errors", "nominal", "six_lumbar", "prefix-32", 3), 0)
        se = CR.value(ds, "precision_se", "nominal", "six_lumbar", "prefix-32", 3)
        text = flat("\n".join(lines[at:]))
        self.assertIn("where a field named at 0.99 was wrong, are %s points" % CR.se_range([se]), text)
        self.assertIn("on 3 typical columns and 2 columns of each anomalous spine scored", text)
        self.assertIn("not scored, a dash in every cell: Four lumbar, Thirteenth rib-bearing body, Rib on L1 and "
                      "No rib on T12", text)

    def test_a_share_right_on_few_fields_is_not_drawn(self):
        """The accuracy figure draws a share right only where PRECISION_DRAWN fields or more were
        named at 0.99, its CSV keeping every share with the fields it rests on and whether it is
        drawn, and its caption says so; the small study's every share right rests on fewer, so
        panel C draws none of them; with no such floor it draws each one the record has, and with a
        floor of 20, among its counts named and below its fewest fields, the ones resting on 20 or
        more, each count read at its own width."""
        tree = small_record()
        ds = CR.rates_of(tree)
        real = CR.save

        def panel_c(floor):
            plotted = []

            def keep(fig, outdir, name, caption):
                for line in fig.axes[2].get_lines():
                    if list(line.get_xdata()) != [0, 1]:            # the dotted line at 99 per cent spans the axes
                        plotted.extend(y for y in line.get_ydata() if np.isfinite(y))
                return real(fig, outdir, name, caption)
            with mock.patch.object(CR, "save", keep), mock.patch.object(CR, "PRECISION_DRAWN", floor):
                CR.fig_accuracy(tree, self.tmp)
            return plotted
        self.assertEqual(panel_c(CR.PRECISION_DRAWN), [])
        everything = [100 * CR.value(ds, "precision", "nominal", "typical", s, n) for n in CR.WIDTHS
                      for s in ["prefix-%02d" % k for k in range(1, 33)] + ["seven"]]
        self.assertEqual(sorted(panel_c(0)), sorted(y for y in everything if np.isfinite(y)))
        # 20 is among the small study's counts named at 0.99, a share resting on it exactly, and below its
        # fewest fields, so that the floor tells the count named from the count of fields, >= from > and one
        # width's count from another's
        cells = [(s, n) for n in CR.WIDTHS for s in ["prefix-%02d" % k for k in range(1, 33)] + ["seven"]]
        answered = {c: CR.value(ds, "n_answered", "nominal", "typical", *c) for c in cells}
        self.assertIn(20.0, answered.values())
        self.assertLess(20, min(CR.value(ds, "n_fields", "nominal", "typical", *c) for c in cells))
        some = [100 * CR.value(ds, "precision", "nominal", "typical", *c) for c in cells if answered[c] >= 20]
        drawn = panel_c(20)
        self.assertTrue(0 < len(drawn) < len([y for y in everything if np.isfinite(y)]), len(drawn))
        self.assertEqual(sorted(drawn), sorted(some))
        panel_c(CR.PRECISION_DRAWN)
        with open(os.path.join(self.tmp, "curve_accuracy.csv"), encoding="ascii") as fh:
            rows = list(csv.DictReader(fh))
        stats = {"Named exactly": "exact", "Named at 0.99": "answered", "Right of those named": "precision"}
        for r in rows:
            stat = stats[r["panel"]]
            fields = CR.value(ds, "n_answered" if stat == "precision" else "n_fields", "nominal", "typical", r["subset"],
                              int(r["bodies"]))
            self.assertEqual(r["fields"], str(int(fields)))
            self.assertEqual(r["drawn"], "no" if stat == "precision" and fields < CR.PRECISION_DRAWN else "yes")
        self.assertEqual({r["drawn"] for r in rows if stats[r["panel"]] == "precision"}, {"no"})
        with open(os.path.join(self.tmp, "curve_accuracy.caption.txt"), encoding="ascii") as fh:
            self.assertIn("share of those right, where 1,000 or more were named", fh.read())

    def test_the_floor_table_gives_the_most_first_in_the_tables_order(self):
        """Most at gives the measures and levels that hold the most values at the floor, the most
        first and by name among equals, though the record keeps them as JSON sorted by name; and
        the rows come in the order the arms' and the anomalous tables give them, not by name, each
        with its own counts."""
        tree = small_record()
        where = {"canal_ap C3": 1, "canal_area C3": 40, "interfacet_h:mean C4": 174, "pedicle_area:mean C4": 85,
                 "pedicle_area:mean C3": 85}
        keys = ["%s/typical" % arm for arm in ("correlated", "errors-0.5", "errors-2", "nominal")]
        keys += ["nominal/%s" % ph for ph in sorted(CR.ANOMALOUS)]
        tree.attrs["floor"] = json.dumps({k: {"values": 400 + i, "of": 1000, "columns": 9, "where": where}
                                          for i, k in enumerate(keys)}, sort_keys=True)
        lines = CR.table_floor(tree)
        rows = [line.strip("| ").split(" | ") for line in lines[2:] if line.startswith("| ")]
        self.assertEqual([(r[0], r[1]) for r in rows],
                         [(CR.ARM_NAME[arm], "Typical") for arm in ("nominal", "errors-0.5", "errors-2", "correlated")]
                         + [(CR.ARM_NAME["nominal"], CR.PHENOTYPE_NAME[ph]) for ph in CR.ANOMALOUS])
        for r in rows:
            self.assertEqual(r[5], "`interfacet_h:mean C4` 174, `pedicle_area:mean C3` 85, `pedicle_area:mean C4` 85")
        order = ["%s/typical" % arm for arm in ("nominal", "errors-0.5", "errors-2", "correlated")]
        order += ["nominal/%s" % ph for ph in CR.ANOMALOUS]
        for r, key in zip(rows, order):
            self.assertEqual(r[2:5], ["{:,}".format(400 + keys.index(key)), "1,000", "9"], key)
        self.assertEqual(lines[-1], CR.FLOOR_NOTE % (C.FLOOR, C.FLOOR))
        self.assertIn("Columns touched counts the columns that hold at least one such value", flat(lines[-1]))
        self.assertIn("by count, the first by name among equal counts", flat(lines[-1]))

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

    def test_the_speed_caption_and_notes_name_what_the_record_lacks(self):
        """The speed figure's caption and the tables' notes read the counts and the threads from
        the record: a record with a pool off one thread is never captioned single-threaded, a count
        the record lacks is named as not recorded and never printed in a count's place, and the
        caption stays within sixty words whatever the record lacks."""
        full = fake_how()["speed"]
        off = dict(full, threads=[{"library": "libblas-test.so", "api": "openblas", "threads": 4}])
        lacking = {k: v for k, v in full.items() if k != "batches"}
        for name, how in (("full", full), ("off", off), ("lacking", lacking), ("empty", {})):
            with self.subTest(name):
                caption, note = CR.speed_caption(how), CR.speed_note(how)
                self.assertLessEqual(len(caption.split()), 60)
                for text in (caption, note):
                    self.assertNotIn("not recorded calls", text)
                    self.assertNotIn("of not recorded", text)
                self.assertEqual("one thread" in caption, name in ("full", "lacking"))
                self.assertEqual("Every thread pool was at one thread" in note, name in ("full", "lacking"))
                self.assertEqual(note.count("one thread"), 1 if name != "empty" else 0)
        self.assertIn("one field alone (median of 30 calls)", CR.speed_caption(full))
        self.assertNotIn("Not recorded", CR.speed_caption(full))
        self.assertIn("Time to name one field, not single-threaded, as measures", CR.speed_caption(off))
        self.assertIn("Not at one thread inside the limit: libblas-test.so at 4.", CR.speed_note(off))
        self.assertIn("(points, median of its calls). Not recorded: batch calls.", CR.speed_caption(lacking))
        self.assertIn("The number of batch calls is not recorded.", CR.speed_note(lacking))
        self.assertIn("Not recorded: the threads, single calls, batch size and batch calls.", CR.speed_caption({}))
        self.assertIn("The number of single calls, the batch's size, the number of batch calls and the number of "
                      "columns are not recorded.", CR.speed_note({}))
        note = CR.table_nuts(small_record(fake_times(small_study()["order"]), fake_nuts(), {"speed": full}))[-1]
        self.assertIn("NUTS on the naming model, chains of draws after tuning steps, on one field at each place",
                      note)
        self.assertIn("The number of chains, the number of draws, the number of tuning steps, the seed, the bodies "
                      "in a field, the number of columns and the field sampled alone are not recorded.", note)
        self.assertNotIn("not recorded chains", note)

    def test_the_speed_axes_read_0_1_1_and_10(self):
        """The speed figure's two axes, on a log scale, label their ticks 0.1, 1 and 10, as the
        README says, and not as powers of ten."""
        tree = small_record(fake_times(small_study()["order"]), fake_nuts(), fake_how())
        real, read = CR.save, []

        def keep(fig, outdir, name, caption):
            read.extend([ax.yaxis.get_major_formatter()(v, 0) for v in (0.1, 1.0, 10.0)] for ax in fig.axes[:2])
            return real(fig, outdir, name, caption)
        with mock.patch.object(CR, "save", keep):
            CR.fig_speed(tree, self.tmp)
        self.assertEqual(read, [["0.1", "1", "10"]] * 2)

    def test_the_figures_are_the_same_files_when_drawn_twice(self):
        how = fake_how()
        # neither the full run's counts (curve.SPEED_CALLS, SPEED_BATCH, SPEED_BATCHES: 30, 128, 5) nor
        # --quick's (curve.QUICK_COUNTS: 3, 8, 2), which a caption could print without reading the record
        how["speed"].update(calls=7, batch=16, batches=3)
        tree = small_record(fake_times(small_study()["order"]), fake_nuts(), how)
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
        self.assertIn("one field alone (median of 7 calls)", caption)
        self.assertIn("a batch of 16 (points, median of 3 calls)", caption)
        with open(os.path.join(self.tmp, "a", "curve_data.csv"), encoding="ascii") as fh:
            printed = [r for r in csv.DictReader(fh) if r["rule"] == "printed"]
        self.assertEqual(sorted((r["panel"], r["subset"]) for r in printed),
                         [("A", "prefix-32"), ("A", "seven"), ("B", "prefix-32"), ("B", "seven")])
        tree.close()


RECORD = os.path.join(ROOT, "records", "curve-2026-10-28", "curve.nc")
FIGURES = os.path.join(ROOT, "records", "curve-2026-10-28", "figures")


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class CommittedRecord(unittest.TestCase):
    """The full run's record of 28 October 2026 as committed: the package's README carries its
    tables; FIGURES.md names it and the code as it stands, and the CSVs and captions beside it are
    what `curve figures` draws from it with that code; and the run changed no code it names while it
    scored or timed."""

    @classmethod
    def setUpClass(cls):
        cls.tree = REC.read(RECORD)
        cls.tree.load()

    @classmethod
    def tearDownClass(cls):
        cls.tree.close()

    def test_the_readme_carries_its_tables(self):
        self.assertEqual(CR.check_readme(self.tree, PACKAGE_README), [])

    def test_the_figures_are_drawn_from_it_by_the_code_as_it_stands(self):
        with open(os.path.join(FIGURES, "FIGURES.md"), encoding="ascii") as fh:
            said = fh.read()
        self.assertIn("sha256 %s." % sha256(RECORD), said)
        for name in ("curve_report.py", "curve.py"):
            self.assertIn("`schwingcheck/%s`, sha256 %s." % (name, sha256(os.path.join(ROOT, "schwingcheck", name))), said)
        with tempfile.TemporaryDirectory() as tmp:
            drawn = sorted(os.path.basename(p) for p in CR.draw_figures(self.tree, tmp))
            self.assertEqual(len(drawn), 12)              # three figures, four files each
            for name in drawn:
                self.assertIn("`%s`" % name, said)
                self.assertTrue(os.path.exists(os.path.join(FIGURES, name)), name)
                if name.endswith((".csv", ".caption.txt")):   # the numbers drawn and the words; a PNG's bytes follow the fonts
                    with open(os.path.join(tmp, name), "rb") as fa, open(os.path.join(FIGURES, name), "rb") as fb:
                        self.assertEqual(fa.read(), fb.read(), name)

    def test_the_run_changed_no_code_it_names(self):
        attrs = self.tree.attrs
        for key in ("changed_during_run", "speed_changed_during_run"):
            self.assertEqual(json.loads(attrs[key]), {}, key)
        for key in ("git", "speed_git"):
            self.assertFalse(json.loads(attrs[key])["package_changed"], key)
        self.assertEqual(json.loads(attrs["git"])["commit"], json.loads(attrs["speed_git"])["commit"])


if __name__ == "__main__":
    unittest.main()
