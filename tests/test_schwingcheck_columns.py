"""The generator is the archive's generator, bit for bit, and the fields are the archive's fields.

For the same seed, phenotypes, measures and settings, draw_columns gives every column the
archive's neighbour.draw_columns gives, value for value, with the stream consumed in the same
order (the size, the offsets, the level draws, the noise draws), at r_between 0 and 0.4; the
anomalous phenotypes keep their levels, their transitional position and their blend; and the
fields cut with consecutive offsets are exact.fields' in the same order, with the truth and the
column of each.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "archive", "bordercall"))

import exact as E                     # noqa: E402
import neighbour as NB                # noqa: E402
import panjabi as P                   # noqa: E402
from schwingcheck import columns as C  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402

MEASURES = list(E.MEASURES7)


class SameGenerator(unittest.TestCase):
    def _compare(self, ref, phenotypes, seed, n, r_between, **synth):
        a = NB.draw_columns(ref, phenotypes, seed, n, MEASURES, r_between=r_between, **synth)
        b = C.draw_columns(ref, phenotypes, seed, n, MEASURES, r_between=r_between, **synth)
        self.assertEqual(len(a), len(b))
        self.assertEqual(b.values.shape, (n, max(len(c.levels) for c in a), len(MEASURES)))
        for i, col in enumerate(a):
            self.assertEqual(col.levels, b.levels[i])
            self.assertEqual(col.phenotype, b.phenotype[i])
            self.assertEqual(col.transitional_at, b.transitional_at[i])
            self.assertEqual(col.meta["scale"], b.scale[i])
            va = np.array([col.values[m] for m in MEASURES]).T
            self.assertTrue(np.array_equal(va, b.values[i, :len(col.levels)]))
            self.assertTrue(np.isnan(b.values[i, len(col.levels):]).all())

    def test_typical_columns_from_seed_97_are_the_archives(self):
        ref = P.load_reference(measures=MEASURES)
        self._compare(ref, ["typical"], 97, 50, 0.0)

    def test_every_phenotype_and_a_correlated_offset(self):
        ref = P.load_reference(measures=MEASURES)
        self._compare(ref, list(C.PHENOTYPES), 11, 24, 0.0)
        self._compare(ref, list(C.PHENOTYPES), 23, 24, 0.4)
        self._compare(ref, ["six_lumbar", "t13"], 29, 8, 0.0, rho=0.3, noise_mm=2.0, scale_sd=0.14, blend=0.25)

    def test_the_stream_order_is_the_archives(self):
        """The same seed gives the same first column whatever the number of columns drawn, and the
        second column differs from the first: each column takes its draws after the one before."""
        ref = P.load_reference(measures=MEASURES)
        one = C.draw_columns(ref, ["typical"], 3, 1, MEASURES)
        two = C.draw_columns(ref, ["typical"], 3, 2, MEASURES)
        self.assertTrue(np.array_equal(one.values[0], two.values[0]))
        self.assertFalse(np.array_equal(two.values[0], two.values[1]))

    def test_the_checked_table_draws_the_archives_columns(self):
        """Since page 892 was read the long table equals the archive's in every value of the
        seven measures, so the same seed draws the same columns from either."""
        seven = MS.select(MS.SPINEPS_7)
        keys = [MS.archive_key(m) for m in seven]
        checked = C.draw_columns(MS.reference(seven), ["typical"], 97, 20, keys)
        archived = C.draw_columns(MS.archive_reference(keys), ["typical"], 97, 20, keys)
        self.assertTrue(np.array_equal(checked.values, archived.values, equal_nan=True))


class Fields(unittest.TestCase):
    def test_consecutive_fields_are_the_archives(self):
        ref = P.load_reference(measures=MEASURES)
        cols = NB.draw_columns(ref, ["typical"], 97, 15, MEASURES)
        V = E.column_values(cols, MEASURES)
        values = np.transpose(V, (0, 2, 1))
        for n in (1, 3, 9, 22):
            Xa, ta, ga = E.fields(V, n)
            Xb, tb, gb = C.fields(values, np.arange(n))
            self.assertTrue(np.array_equal(Xa, Xb) and np.array_equal(ta, tb) and np.array_equal(ga, gb))

    def test_gapped_fields_and_short_columns(self):
        values = np.full((2, 5, 1), np.nan)
        values[0, :, 0] = np.arange(5)
        values[1, :3, 0] = 10 + np.arange(3)           # a column of three bodies
        X, truth, grp = C.fields(values, [0, 2])
        self.assertEqual(sorted(zip(grp.tolist(), truth.tolist())), [(0, 0), (0, 1), (0, 2), (1, 0)])
        got = {(g, t): tuple(x[0]) for x, t, g in zip(X, truth, grp)}
        self.assertEqual(got[(0, 1)], (1.0, 3.0))
        self.assertEqual(got[(1, 0)], (10.0, 12.0))
        with self.assertRaises(ValueError):
            C.fields(values, [0, 5])


if __name__ == "__main__":
    unittest.main()
