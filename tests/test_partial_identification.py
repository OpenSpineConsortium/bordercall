"""Partial identification: the identified set, the Imbens-Manski interval, and the sign.

    python -m unittest discover -s tests -v

r is UNIDENTIFIED, not merely unknown, so the honest report is an interval and a claim about
the sign of a difference rather than a point estimate. These tests pin the two places that
could silently go wrong.

The Imbens-Manski critical value is checked against its two analytic limits, because a
bisection on the wrong side of a monotone function returns a finite, plausible, wrong number
and raises nothing -- which is this project's recurring failure mode. The limits are: a set
of zero width must give 1.96, since the parameter is then point-identified and the interval
is an ordinary two-sided one; and a set far wider than the sampling error must give 1.645,
since only one end can bind.

The sign machinery is checked on constructed rows whose answer is known by hand, including
the case that must NOT be allowed to read as a result: a difference that crosses zero inside
the identified set, where the direction itself is unidentified.
"""
from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import covariance as CV       # noqa: E402


def rows(*pairs, se=0.01):
    """(r, value) pairs -> the dicts a sweep produces."""
    return [{"r": r, "acc": v, "se": se, "n": 1000} for r, v in pairs]


class TestImbensManski(unittest.TestCase):
    def test_zero_width_set_gives_two_sided_z(self):
        """A point-identified parameter: the interval is an ordinary two-sided one."""
        lo, hi, c = CV.imbens_manski(0.5, 0.5, 0.01, 0.01)
        self.assertAlmostEqual(c, 1.9599639845400545, places=5)
        self.assertAlmostEqual(lo, 0.5 - 1.95996 * 0.01, places=5)
        self.assertAlmostEqual(hi, 0.5 + 1.95996 * 0.01, places=5)

    def test_wide_set_tends_to_one_sided_z(self):
        """A set far wider than the sampling error: only one end can bind."""
        _, _, c = CV.imbens_manski(0.0, 10.0, 0.01, 0.01)
        self.assertAlmostEqual(c, 1.6448536269514722, places=5)

    def test_critical_value_is_between_the_two(self):
        for width in (0.0, 0.001, 0.01, 0.05, 0.2, 1.0, 100.0):
            _, _, c = CV.imbens_manski(0.0, width, 0.01, 0.01)
            self.assertGreaterEqual(c + 1e-9, 1.6448536269514722)
            self.assertLessEqual(c - 1e-9, 1.9599639845400545)

    def test_critical_value_decreases_as_the_set_widens(self):
        cs = [CV.imbens_manski(0.0, w, 0.01, 0.01)[2]
              for w in (0.0, 0.005, 0.01, 0.02, 0.05, 0.1)]
        for a, b in zip(cs, cs[1:]):
            self.assertGreaterEqual(a + 1e-12, b)

    def test_it_is_narrower_than_the_naive_interval(self):
        """The whole point: [min - 1.96 se, max + 1.96 se] over-covers."""
        lo, hi, c = CV.imbens_manski(0.40, 0.50, 0.01, 0.01)
        naive_lo, naive_hi = 0.40 - 1.95996 * 0.01, 0.50 + 1.95996 * 0.01
        self.assertGreater(lo, naive_lo)
        self.assertLess(hi, naive_hi)

    def test_interval_contains_the_identified_set(self):
        lo, hi, _ = CV.imbens_manski(0.40, 0.50, 0.01, 0.02)
        self.assertLess(lo, 0.40)
        self.assertGreater(hi, 0.50)

    def test_zero_standard_error_returns_the_set_itself(self):
        lo, hi, c = CV.imbens_manski(0.4, 0.5, 0.0, 0.0)
        self.assertEqual((lo, hi), (0.4, 0.5))


class TestIdentifiedSet(unittest.TestCase):
    def test_finds_both_ends_and_their_r(self):
        s = CV.identified_set(rows((0.0, 0.71), (0.4, 0.69), (0.9, 0.70)))
        self.assertAlmostEqual(s["lo"], 0.69)
        self.assertAlmostEqual(s["lo_at_r"], 0.4)
        self.assertAlmostEqual(s["hi"], 0.71)
        self.assertAlmostEqual(s["hi_at_r"], 0.0)
        self.assertAlmostEqual(s["width"], 0.02, places=9)


class TestSignInvariance(unittest.TestCase):
    def test_constant_sign_clear_of_zero_is_certified(self):
        a = rows((0.0, 0.71), (0.4, 0.70), (0.9, 0.70))
        b = rows((0.0, 0.42), (0.4, 0.42), (0.9, 0.41))
        v = CV.sign_invariance(a, b)
        self.assertTrue(v["sign_constant"])
        self.assertTrue(v["sign_certified"])
        self.assertIsNone(v["crossing_r"])
        self.assertGreater(v["margin_in_se"], 10)

    def test_a_crossing_is_reported_and_not_certified(self):
        """The case that must never read as a result."""
        a = rows((0.0, 0.60), (0.5, 0.50), (1.0, 0.40))
        b = rows((0.0, 0.50), (0.5, 0.50), (1.0, 0.50))
        v = CV.sign_invariance(a, b)
        self.assertFalse(v["sign_certified"])
        self.assertIsNotNone(v["crossing_r"])
        self.assertAlmostEqual(v["crossing_r"], 0.5, places=6)

    def test_crossing_is_interpolated_between_grid_points(self):
        a = rows((0.0, 0.52), (1.0, 0.48))
        b = rows((0.0, 0.50), (1.0, 0.50))
        v = CV.sign_invariance(a, b)
        self.assertAlmostEqual(v["crossing_r"], 0.5, places=6)

    def test_constant_sign_inside_the_noise_is_not_certified(self):
        a = rows((0.0, 0.5010), (0.9, 0.5005), se=0.01)
        b = rows((0.0, 0.5000), (0.9, 0.5000), se=0.01)
        v = CV.sign_invariance(a, b)
        self.assertTrue(v["sign_constant"])
        self.assertFalse(v["sign_certified"])

    def test_worst_case_is_the_one_nearest_zero(self):
        a = rows((0.0, 0.80), (0.5, 0.60), (0.9, 0.90))
        b = rows((0.0, 0.50), (0.5, 0.50), (0.9, 0.50))
        v = CV.sign_invariance(a, b)
        self.assertAlmostEqual(v["worst_case"]["r"], 0.5)
        self.assertAlmostEqual(v["worst_case"]["acc"], 0.10, places=9)

    def test_mismatched_grids_use_the_shared_r_values(self):
        a = rows((0.0, 0.70), (0.4, 0.70), (0.9, 0.70))
        b = rows((0.0, 0.40), (0.9, 0.40))
        v = CV.sign_invariance(a, b)
        self.assertEqual([d["r"] for d in v["diffs"]], [0.0, 0.9])

    def test_no_shared_r_returns_none(self):
        self.assertIsNone(CV.sign_invariance(rows((0.0, 0.7)), rows((0.5, 0.4))))


class TestOnTheRecordedRun(unittest.TestCase):
    """The committed sweep must come out sign-certified at both junctions."""

    def setUp(self):
        import json
        p = os.path.join(os.path.dirname(HERE), "records", "covariance-sweep.json")
        if not os.path.exists(p):
            self.skipTest("records/covariance-sweep.json not present")
        with open(p) as fh:
            self.rec = json.load(fh)

    def test_seven_beats_three_at_every_r_at_both_junctions(self):
        for key in ("ct", "tl"):
            v = CV.sign_invariance(self.rec["results"]["spineps_7"][key],
                                   self.rec["results"]["baseline_3"][key])
            self.assertTrue(v["sign_constant"], "%s: the sign is not constant" % key)
            self.assertTrue(v["sign_certified"],
                            "%s: the interval does not exclude zero" % key)
            self.assertIsNone(v["crossing_r"], "%s: there is a crossing" % key)
            self.assertGreater(v["set"]["ci_lo"], 0.0)

    def test_the_accuracy_itself_is_only_an_interval(self):
        """The headline number is NOT point-identified, and the record must show that."""
        for key in ("ct", "tl"):
            s = CV.identified_set(self.rec["results"]["spineps_7"][key])
            self.assertGreater(s["width"], 0.0)
            self.assertLess(s["lo"], s["hi"])


if __name__ == "__main__":
    unittest.main()
