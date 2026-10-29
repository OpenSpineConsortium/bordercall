"""The statistics against hand counts, numpy and an independent ranking implementation of the AUC."""
from __future__ import annotations

import random
import unittest

import numpy as np

from screening.contracts import ViolationError
from screening import stats as S


def auc_by_ranks(neg, pos):
    """The helper thread's AUC: average ranks over all values, the negatives' rank sum."""
    allv = np.concatenate([np.asarray(pos, float), np.asarray(neg, float)])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv))
    sv = allv[order]
    i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1
        i = j + 1
    r_neg = ranks[len(pos):].sum()
    return (r_neg - len(neg) * (len(neg) + 1) / 2) / (len(neg) * len(pos))


class PercentileTest(unittest.TestCase):
    def test_hand_values(self):
        self.assertEqual(S.percentile([1.0, 2.0, 3.0, 4.0], 50.0), 2.5)
        self.assertEqual(S.percentile([4.0, 1.0, 3.0, 2.0], 0.0), 1.0)
        self.assertEqual(S.percentile([4.0, 1.0, 3.0, 2.0], 100.0), 4.0)
        self.assertEqual(S.percentile([7.0], 95.0), 7.0)

    def test_equals_numpy_linear(self):
        rng = random.Random(3)
        for _ in range(20):
            values = [rng.uniform(-50, 50) for _ in range(rng.randint(1, 40))]
            for p in (2.5, 5.0, 25.0, 50.0, 75.0, 95.0, 97.5):
                self.assertAlmostEqual(S.percentile(values, p), float(np.percentile(values, p)), places=9)

    def test_median(self):
        self.assertEqual(S.median([3.0, 1.0, 2.0]), 2.0)
        self.assertEqual(S.median([4.0, 1.0, 3.0, 2.0]), 2.5)

    def test_refuses_a_percentile_outside_0_to_100_and_no_values(self):
        with self.assertRaises(ViolationError):
            S.percentile([1.0], 101.0)
        with self.assertRaises(ViolationError):
            S.median([])

    def test_quartiles(self):
        self.assertEqual(S.quartiles([]), {})
        self.assertEqual(S.quartiles([1.0, 2.0, 3.0, 4.0, 5.0]), {"n": 5, "q1": 2.0, "median": 3.0, "q3": 4.0})


class AucTest(unittest.TestCase):
    def test_hand_case_with_a_tie_counted_half(self):
        # pairs (neg, pos): (0.9, 0.7) below, (0.9, 0.85) below, (0.85, 0.7) below, (0.85, 0.85) a tie
        self.assertEqual(S.auc([0.9, 0.85], [0.7, 0.85]), 3.5 / 4)

    def test_separated_reversed_and_all_tied(self):
        self.assertEqual(S.auc([0.9, 0.95], [0.5, 0.6]), 1.0)
        self.assertEqual(S.auc([0.5, 0.6], [0.9, 0.95]), 0.0)
        self.assertEqual(S.auc([0.8, 0.8], [0.8]), 0.5)

    def test_equals_the_rank_formula_on_random_data_with_ties(self):
        rng = random.Random(11)
        for _ in range(30):
            neg = [round(rng.uniform(0.5, 1.1), 2) for _ in range(rng.randint(1, 30))]
            pos = [round(rng.uniform(0.4, 1.0), 2) for _ in range(rng.randint(1, 30))]
            self.assertAlmostEqual(S.auc(neg, pos), auc_by_ranks(neg, pos), places=12)

    def test_refuses_an_empty_class(self):
        with self.assertRaises(ViolationError):
            S.auc([], [0.5])


class BootTest(unittest.TestCase):
    def test_identity_picks_give_the_whole_auc_at_both_ends(self):
        groups = [([0.9, 0.85], [0.7]), ([0.95], [0.6, 0.85])]
        whole = S.auc([0.9, 0.85, 0.95], [0.7, 0.6, 0.85])
        low, high = S.boot_interval(groups, [[0, 1], [0, 1], [1, 0]])
        self.assertEqual((low, high), (whole, whole))

    def test_no_resample_with_both_classes_gives_no_interval(self):
        self.assertEqual(S.boot_interval([([0.9], []), ([], [0.7])], [[0, 0], [1, 1]]), (None, None))

    def test_refuses_a_pick_outside_the_groups(self):
        with self.assertRaises(ViolationError):
            S.boot_interval([([0.9], [0.7])], [[1]])


class KappaTest(unittest.TestCase):
    def test_perfect_agreement_is_one(self):
        kappa, matrix = S.weighted_kappa([0, 1, 2, 3, 3], [0, 1, 2, 3, 3])
        self.assertEqual(kappa, 1.0)
        self.assertEqual(matrix, [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 2]])

    def test_chance_agreement_is_zero(self):
        kappa, matrix = S.weighted_kappa([0, 0, 1, 1], [0, 1, 0, 1], k=2)
        self.assertEqual(kappa, 0.0)
        self.assertEqual(matrix, [[1, 1], [1, 1]])

    def test_quadratic_weights_forgive_a_near_miss_more_than_a_far_one(self):
        near, _ = S.weighted_kappa([0, 3, 0, 3], [0, 2, 0, 3])
        far, _ = S.weighted_kappa([0, 3, 0, 3], [0, 0, 0, 3])
        self.assertGreater(near, far)

    def test_refuses_a_grade_outside_the_scale(self):
        with self.assertRaises(ViolationError):
            S.weighted_kappa([0, 4], [0, 0])

    def test_share(self):
        self.assertEqual(S.share(1, 3), 0.3333)
        self.assertIsNone(S.share(0, 0))
        with self.assertRaises(ViolationError):
            S.share(2, 1)


if __name__ == "__main__":
    unittest.main()
