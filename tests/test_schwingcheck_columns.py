"""The generator is the archive's generator, bit for bit, and the fields are the archive's fields.

For the same seed, phenotypes, measures and settings, draw_columns gives every column the
archive's neighbour.draw_columns gives, value for value, with the stream consumed in the same
order (the size, the offsets, the level draws, the noise draws), at r_between 0 and 0.4; the
anomalous phenotypes keep their levels, their transitional position and their blend; every
column is padded to the widest phenotype listed, however few are drawn; and the fields cut with
consecutive offsets are exact.fields' in the same order, with the truth and the column of each.
Each kind is drawn with its own power of the size, an area with the square, an angle with none
and no floor, in the same stream; and columns drawn for sizes an earlier call drew take no size
from the stream, which starts at the offsets. The floor is the archive's, 0.5 for a length, held
on the archive's own fifth length, the pedicle, which reaches it, and floor_hits counts the
values it touched in the measures that scale with the size and nowhere else.
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

    def test_columns_are_padded_to_the_widest_phenotype_listed(self):
        """However few columns are drawn: one typical column drawn with six_lumbar listed but not
        drawn is six_lumbar's 23 bodies wide, its own 22 bodies those of a typical draw alone."""
        ref = P.load_reference(measures=MEASURES)
        one = C.draw_columns(ref, ["typical", "six_lumbar"], 3, 1, MEASURES)
        alone = C.draw_columns(ref, ["typical"], 3, 1, MEASURES)
        self.assertEqual(one.values.shape, (1, 23, len(MEASURES)))
        self.assertEqual(alone.values.shape, (1, 22, len(MEASURES)))
        self.assertTrue(np.array_equal(one.values[:, :22], alone.values))
        self.assertTrue(np.isnan(one.values[:, 22]).all())

    def test_a_length_at_the_floor_is_the_archives_floor(self):
        """The seven never reach the floor in these columns; the pedicle, the archive's fifth
        length, does, three times in seed 97's 50, and the same values come out bit for bit."""
        measures = MEASURES + ["pedicle"]
        ref = P.load_reference(measures=measures)
        a = NB.draw_columns(ref, ["typical"], 97, 50, measures)
        b = C.draw_columns(ref, ["typical"], 97, 50, measures)
        for i, col in enumerate(a):
            va = np.array([col.values[m] for m in measures]).T
            self.assertTrue(np.array_equal(va, b.values[i, :len(col.levels)]))
        self.assertEqual(int((b.values == 0.5).sum()), 3)
        self.assertEqual(int((b.values[:, :, :-1] == 0.5).sum()), 0)
        hits = C.floor_hits(b)
        self.assertEqual((hits["values"], hits["of"]), (3, 50 * 22 * 8))
        self.assertEqual(sum(hits["where"].values()), 3)
        self.assertTrue(all(k.startswith("pedicle ") for k in hits["where"]))
        self.assertLessEqual(hits["columns"], 3)

    def test_the_checked_table_draws_the_archives_columns(self):
        """Since page 892 was read the long table equals the archive's in every value of the
        seven measures, so the same seed draws the same columns from either."""
        seven = MS.select(MS.SPINEPS_7)
        keys = [MS.archive_key(m) for m in seven]
        checked = C.draw_columns(MS.reference(seven), ["typical"], 97, 20, keys)
        archived = C.draw_columns(MS.archive_reference(keys), ["typical"], 97, 20, keys)
        self.assertTrue(np.array_equal(checked.values, archived.values, equal_nan=True))


class KindsAndGivenSizes(unittest.TestCase):
    """Each kind with its own power of the size, and further measures drawn for patients whose
    sizes an earlier call drew (step e)."""

    KEYS = ["endplate", "canal_area", "endplate_incl", "facet_sag_sup:mean"]

    def _drawn(self, seed, n, scale=None):
        ms = MS.select(self.KEYS)
        cols = C.draw_columns(MS.reference(ms), ["typical"], seed, n, [MS.archive_key(m) for m in ms],
                              noise_mm=MS.errors(ms), power=MS.powers(ms), scale=scale)
        return ms, cols

    def test_each_kind_is_drawn_with_its_own_power_and_floor_in_the_archives_stream(self):
        ms, cols = self._drawn(61, 30)
        mu, sd = MS.arrays(ms)
        noise, power = MS.errors(ms), MS.powers(ms)
        rng = np.random.default_rng(61)
        index = [C.DRAW_LEVELS.index(lv) for lv in cols.levels[0]]
        for c in range(30):
            s = float(np.exp(rng.normal(0.0, C.SYNTH["scale_sd"])))
            z = rng.normal(size=len(ms))
            e = rng.normal(size=(len(ms), len(C.DRAW_LEVELS)))
            nz = rng.normal(size=(len(ms), len(C.DRAW_LEVELS)))
            for m in range(len(ms)):
                g = s ** power[m]
                v = g * (mu[m] + sd[m] * (0.5 * z[m] + np.sqrt(0.75) * e[m, index])) + noise[m] * nz[m, index]
                if power[m] > 0:
                    v = np.maximum(v, 0.5)
                self.assertLess(np.abs(cols.values[c, :, m] - v).max(), 1e-9, (c, ms[m].key))
            self.assertEqual(cols.scale[c], s)
        # an angle, which may be negative, is never floored; a length and an area are
        self.assertLess(np.nanmin(cols.values[:, :, 2]), 0.0)
        self.assertGreaterEqual(np.nanmin(cols.values[:, :, [0, 1]]), C.FLOOR)
        self.assertEqual(cols.meta["power"], [1.0, 2.0, 0.0, 0.0])

    def test_given_sizes_draw_no_size_and_leave_the_stream_to_the_offsets(self):
        _, first = self._drawn(62, 12)
        _, again = self._drawn(63, 12, scale=first.scale)
        self.assertTrue(np.array_equal(again.scale, first.scale))
        self.assertTrue(again.meta["scale_given"])
        self.assertFalse(first.meta["scale_given"])
        # the stream of a call given the sizes starts at the offsets: the same draws a call that
        # draws its own sizes makes after each size
        ms = MS.select(self.KEYS)
        mu, sd = MS.arrays(ms)
        rng = np.random.default_rng(63)
        index = [C.DRAW_LEVELS.index(lv) for lv in again.levels[0]]
        for c in range(12):
            z = rng.normal(size=len(ms))
            e = rng.normal(size=(len(ms), len(C.DRAW_LEVELS)))
            nz = rng.normal(size=(len(ms), len(C.DRAW_LEVELS)))
            g = first.scale[c] ** MS.powers(ms)
            v = g[:, None] * (mu + sd * (0.5 * z[:, None] + np.sqrt(0.75) * e[:, index])) + MS.errors(ms)[:, None] * nz[:, index]
            v = np.where(MS.powers(ms)[:, None] > 0, np.maximum(v, C.FLOOR), v)
            self.assertLess(np.abs(again.values[c].T - v).max(), 1e-9, c)
        with self.assertRaises(ValueError):
            self._drawn(63, 12, scale=first.scale[:5])
        for wrong in ([1.0, 2.0], [2.0]):
            with self.assertRaisesRegex(ValueError, "one power of the size per measure"):
                C.draw_columns(MS.reference(ms), ["typical"], 63, 2, self.KEYS, power=wrong)

    def test_floor_hits_counts_only_the_measures_that_scale_with_the_size(self):
        ms, cols = self._drawn(61, 30)
        hits = C.floor_hits(cols)
        floored = (cols.values == 0.5) & (MS.powers(ms) > 0)[None, None, :]
        self.assertEqual(hits["values"], int(floored.sum()))
        self.assertEqual(hits["of"], 30 * 22 * 2)
        # an angle's value at 0.5 is a value, not the floor
        cols.values[0, 0, 2] = 0.5
        self.assertEqual(C.floor_hits(cols)["values"], hits["values"])
        cols.values[0, 0, 0] = 0.5
        again = C.floor_hits(cols)
        self.assertEqual(again["values"], hits["values"] + 1)
        self.assertEqual(again["where"]["endplate C3"], hits["where"].get("endplate C3", 0) + 1)

    def test_every_power_one_and_no_sizes_given_is_the_archives_generator(self):
        ref = P.load_reference(measures=MEASURES)
        a = C.draw_columns(ref, ["typical"], 97, 20, MEASURES)
        b = C.draw_columns(ref, ["typical"], 97, 20, MEASURES, power=np.ones(len(MEASURES)))
        self.assertTrue(np.array_equal(a.values, b.values, equal_nan=True))
        self.assertTrue(np.array_equal(a.scale, b.scale))


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
