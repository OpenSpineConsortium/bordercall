"""The second part's code, every measure of the reread, held to what its docstrings say.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- variant_of splits a key only where VARIANTS names it, and refuses a paper no variant is written for;
- place puts a vertebra's measure at its own level, a disc or a foramen between two levels at the
  upper, and one printed against one vertebra nowhere unless the paper names the space below;
- the three tables have the shapes the handoff counts, every placed cell lands once, and the
  combined table carries Panjabi's measures with his own errors and the papers' with their kind's;
- draw_table on Panjabi's 32 is draw to the bit, and leaves NaN where the table has no cell;
- each relation flags a constructed population where it should and nowhere else;
- score on a complete subset names a drawn field and refuses an incomplete one;
- the full snapshot and its vocabulary are the ones SOURCE_ALL.json records.
"""
from __future__ import annotations

import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(NOTE))
sys.path[:0] = [REPO, NOTE]

from schwingcheck import LEVELS  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from synthval import all_measures as AM  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import relations as REL  # noqa: E402
from synthval.population import GENERATOR, Population, draw, draw_table  # noqa: E402


def tables():
    rows = PT.load_rows_all()
    series, _ = PT.select_all(rows)
    cells = PT.pooled_cells(series)
    a = PT.panjabi_table()
    b = PT.papers_table(cells, PT.load_vocabulary())
    return cells, a, b, PT.combined_table(a, b)


class Variants(unittest.TestCase):
    def test_a_key_with_no_variants_is_itself(self):
        self.assertEqual(PT.variant_of("h_post", "tan2004", "caliper"), "h_post")

    def test_a_paper_and_technique_pick_their_variant(self):
        self.assertEqual(PT.variant_of("disc_h_mean", "bach2019", "ct3d_midsagittal_disc_height"), "disc_h_mean [three points]")
        self.assertEqual(PT.variant_of("disc_h_mean", "kunkel2011", "anything"), "disc_h_mean [two rims]")

    def test_the_star_variant_takes_the_papers_not_named(self):
        self.assertEqual(PT.variant_of("pedicle_chord", "hou1993", "x"), "pedicle_chord [parallel to the midline]")
        self.assertEqual(PT.variant_of("pedicle_chord", "someone2030", "x"), "pedicle_chord [along the axis]")

    def test_a_split_key_refuses_a_paper_with_no_variant(self):
        with self.assertRaises(ValueError):
            PT.variant_of("disc_h_mean", "someone2030", "x")

    def test_base_key_takes_the_variant_off(self):
        self.assertEqual(PT.base_key("canal_index [areas]"), "canal_index")
        self.assertEqual(PT.base_key("h_post"), "h_post")


class Placing(unittest.TestCase):
    def test_a_vertebral_measure_sits_at_its_level(self):
        self.assertEqual(PT.place("h_post", "L3", "tan2004"), "L3")
        self.assertIsNone(PT.place("h_post", "S1", "tan2004"))

    def test_a_disc_between_two_levels_sits_at_the_upper(self):
        self.assertEqual(PT.place("disc_h_mean [two rims]", "L4-L5", "kunkel2011"), "L4")
        self.assertEqual(PT.place("disc_h_mean [two rims]", "L5-S1", "kunkel2011"), "L5")
        self.assertIsNone(PT.place("disc_h_mean [two rims]", "L3-L5", "kunkel2011"))

    def test_a_disc_against_one_vertebra_sits_nowhere_unless_the_paper_names_the_space(self):
        self.assertIsNone(PT.place("disc_h_mean [not defined]", "L4", "yadav2020"))
        self.assertEqual(PT.place("foramen_w [the notch]", "L4", "amonookuofi1985"), "L4")


class Tables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells, cls.a, cls.b, cls.c = tables()

    def test_the_shapes_the_handoff_counts(self):
        self.assertEqual((len(self.a.keys), self.a.cells()), (42, 782))
        self.assertEqual((len(self.b.keys), self.b.cells()), (53, 694))
        self.assertEqual((len(self.c.keys), self.c.cells()), (75, 1054))
        for t in (self.a, self.b, self.c):
            self.assertEqual(t.mu.shape, (len(t.keys), len(LEVELS)))
            self.assertEqual(t.sd.shape, t.mu.shape)

    def test_every_placed_cell_lands_once(self):
        placed = [(c["measure"], c["placed_at"]) for c in self.cells if c["placed_at"]]
        self.assertEqual(len(placed), len(set(placed)))
        self.assertEqual(len(placed), self.b.cells())

    def test_the_combined_table_keeps_panjabis_errors_and_gives_the_papers_their_kinds(self):
        self.assertEqual(self.c.keys[:len(self.a.keys)], self.a.keys)
        np.testing.assert_array_equal(self.c.error[:len(self.a.keys)], self.a.error)
        for j in range(len(self.a.keys), len(self.c.keys)):
            kind, err = self.c.kinds[j], self.c.error[j]
            if kind == "length":
                self.assertEqual(err, MS.LENGTH_ERROR_MM)
            elif kind == "angle":
                self.assertEqual(err, MS.ANGLE_ERROR_DEG)
            elif kind == "area":
                self.assertGreater(err, 0.0)
            else:
                self.assertEqual(err, 0.0)

    def test_a_ratio_has_no_size_and_no_error(self):
        j = self.c.keys.index("canal_index [areas]")
        self.assertEqual(self.c.kinds[j], "ratio")
        self.assertEqual((self.c.power[j], self.c.error[j]), (0.0, 0.0))

    def test_complete_over_asks_for_a_mean_and_a_positive_sd_at_every_level(self):
        pool = [self.c.keys.index(MS.archive_key(m)) for m in MS.pool()]
        self.assertTrue(set(pool) <= set(self.c.complete_over(LEVELS)))
        lumbar = self.c.complete_over(AM.LUMBAR)
        self.assertTrue(set(self.c.complete_over(LEVELS)) <= set(lumbar))
        self.assertGreater(len(lumbar), len(self.c.complete_over(LEVELS)))


class DrawTable(unittest.TestCase):
    def test_equal_to_draw_on_panjabis_32(self):
        ms = MS.pool()
        a = PT.panjabi_table()
        idx = [a.keys.index(PT.panjabi_key(m)) for m in ms]
        pop_t = draw_table(a.subset(idx), GENERATOR, 300, 5)
        pop_d = draw(GENERATOR, 300, 5, ms)
        np.testing.assert_array_equal(pop_t.true, pop_d.true)
        np.testing.assert_array_equal(pop_t.measured, pop_d.measured)
        np.testing.assert_array_equal(pop_t.error, pop_d.error)

    def test_nan_where_the_table_has_no_cell(self):
        _, _, b, _ = tables()
        pop = draw_table(b, GENERATOR, 50, 3)
        empty = ~np.isfinite(b.mu)
        for j in range(len(b.keys)):
            for i in range(len(LEVELS)):
                if empty[j, i]:
                    self.assertTrue(np.isnan(pop.true[:, i, j]).all())
                    self.assertTrue(np.isnan(pop.measured[:, i, j]).all())
                else:
                    self.assertTrue(np.isfinite(pop.true[:, i, j]).all())


def population_of(values: dict, n: int = 4) -> Population:
    """A population of n identical people, one body, with the true values given per key."""
    keys = list(values)
    true = np.tile(np.array([values[k] for k in keys], float), (n, 1, 1))
    return Population(true=true, measured=true.copy(), scale=np.ones(n), levels=["L3"], keys=keys,
                      power=np.ones(len(keys)), error=np.ones(len(keys)), phenotype="typical",
                      settings=GENERATOR, seed=0, kinds=tuple("length" for _ in keys), table="made up")


class Relations(unittest.TestCase):
    def rate(self, values, indicator):
        by, tests, rows = REL.relation_flags(population_of(values))
        return float(by[indicator].mean()), tests[indicator], rows

    def test_within_flags_an_inner_width_at_or_over_the_pedicle(self):
        self.assertEqual(self.rate({"pedicle_w_inner": 5.0, "pedicle": 8.0}, "within")[0], 0.0)
        self.assertEqual(self.rate({"pedicle_w_inner": 8.0, "pedicle": 8.0}, "within")[0], 1.0)

    def test_past_flags_a_chord_no_longer_than_the_pedicle(self):
        ok = {"pedicle_length [proper]": 10.0, "pedicle_chord [along the axis]": 45.0}
        bad = {"pedicle_length [proper]": 46.0, "pedicle_chord [along the axis]": 45.0}
        self.assertEqual(self.rate(ok, "past")[0], 0.0)
        self.assertEqual(self.rate(bad, "past")[0], 1.0)

    def test_outside_counts_both_pedicles(self):
        fits = {"interpedicular": 24.0, "pedicle": 8.0, "transverse_width": 41.0}
        self.assertEqual(self.rate(fits, "outside")[0], 0.0)
        self.assertEqual(self.rate(dict(fits, transverse_width=39.0), "outside")[0], 1.0)

    def test_box_and_convex_on_the_body_section(self):
        body = {"body_w": 40.0, "body_d [through the pedicles]": 30.0}
        self.assertEqual(self.rate(dict(body, body_area=1000.0), "box")[0], 0.0)
        self.assertEqual(self.rate(dict(body, body_area=1300.0), "box")[0], 1.0)
        self.assertEqual(self.rate(dict(body, body_area=500.0), "convex")[0], 1.0)
        self.assertEqual(self.rate(dict(body, body_area=1000.0), "convex")[0], 0.0)

    def test_the_foramen_has_no_convex_bound(self):
        values = {"foramen_area": 20.0, "foramen_w [body to facet]": 10.0, "foramen_h": 15.0}
        by, _, _ = REL.relation_flags(population_of(values))
        self.assertEqual(float(by["box"].mean()), 0.0)
        self.assertNotIn("convex", by)

    def test_positive_flags_a_ratio_at_or_below_zero(self):
        self.assertEqual(self.rate({"canal_index [areas]": 0.3}, "positive")[0], 0.0)
        self.assertEqual(self.rate({"canal_index [areas]": 0.0}, "positive")[0], 1.0)

    def test_a_relation_the_table_lacks_tests_nothing(self):
        rate, tested, rows = self.rate({"pedicle": 8.0}, "within")
        self.assertEqual((rate, tested), (0.0, 0))
        row = next(r for r in rows if r["relation"] == "inner width within the pedicle")
        self.assertTrue(math.isnan(row["flagged"]))
        self.assertEqual(row["missing"], "pedicle_w_inner")


class Scoring(unittest.TestCase):
    def test_score_on_a_complete_subset_names_better_than_chance(self):
        _, _, _, c = tables()
        pop = draw_table(c, GENERATOR, 40, 9)
        seven = [c.keys.index(MS.archive_key(m)) for m in MS.select(MS.SPINEPS_7)]
        got = AM.score(pop, c, seven, 3, list(LEVELS), GENERATOR)
        self.assertEqual(got["fields"], 40 * (len(LEVELS) - 2))
        self.assertEqual(got["places"], len(LEVELS) - 2)
        self.assertGreater(got["exact"], 2.0 / got["places"])

    def test_score_refuses_a_subset_that_is_not_complete(self):
        _, _, _, c = tables()
        pop = draw_table(c, GENERATOR, 5, 9)
        incomplete = c.complete_over(AM.LUMBAR)
        self.assertGreater(len(incomplete), len(c.complete_over(LEVELS)))
        with self.assertRaises(ValueError):
            AM.score(pop, c, incomplete, 1, list(LEVELS), GENERATOR)


class Snapshot(unittest.TestCase):
    def test_the_full_snapshot_is_the_one_recorded(self):
        self.assertEqual(PT.check_snapshot_all(), [])


if __name__ == "__main__":
    unittest.main()
