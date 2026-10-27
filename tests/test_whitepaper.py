"""The computations new to the white paper, each checked against something outside it.

    python -m unittest discover -s tests -v

The second-opinion counts must be recomputed from the exact study's own scoring columns and agree
with the committed record to the bit, by place as well as overall, and the share they name exactly
must be the exact study's; the tally must count shares the way its names say. The power simulation
must hit, in its own draws, the accuracy its quadrature calibrates to; must allocate half of each
stratum to each aid for every reader; its analysis must give, on a study small enough to work by
hand, the numbers worked by hand; and its committed record must be monotone where more readers or
cases can only help, with critical values that are the largest of the quantiles they are taken
from. The white paper's checks must agree with the exact study and its supplement wherever they
overlap, the within-one Bayes rule must never do worse than the likeliest place, and the count from
C2 must change nothing on columns where it names the bodies as the columns do.
"""
from __future__ import annotations

import json
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "bordercall"))

import exact as E                 # noqa: E402
import second_opinion as SO       # noqa: E402
import study_power as SP          # noqa: E402
import whitepaper_checks as W     # noqa: E402

RECORDS = os.path.join(ROOT, "records", "whitepaper-2026-10-26")
SETTINGS = ("none", "moderate", "large")


def _load(name):
    with open(os.path.join(RECORDS, name), encoding="utf-8") as fh:
        return json.load(fh)


class TallyTest(unittest.TestCase):
    def test_shares_follow_their_names(self):
        at_true = np.array([0.001, 0.02, 0.6, 0.95, 0.995])
        at_adjacent = np.array([0.004, 0.04, 0.3, 0.92])
        t = SO.tally(at_true, at_adjacent)
        self.assertEqual(t["fields"], 5)
        self.assertEqual(t["adjacent_answers"], 4)
        self.assertAlmostEqual(t["correct_below_0.01"], 1 / 5)
        self.assertAlmostEqual(t["correct_below_0.05"], 2 / 5)
        self.assertAlmostEqual(t["off_by_one_below_0.01"], 1 / 4)
        self.assertAlmostEqual(t["off_by_one_below_0.05"], 2 / 4)
        self.assertAlmostEqual(t["correct_at_least_0.99"], 1 / 5)
        self.assertAlmostEqual(t["off_by_one_at_least_0.9"], 1 / 4)


class SecondOpinionRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = _load("second_opinion.json")
        with open(SO.RECORD, encoding="utf-8") as fh:
            cls.exact = json.load(fh)

    def test_named_share_is_the_exact_studys(self):
        for n, row in self.rec["widths"].items():
            self.assertEqual(row["exact"], self.exact["widths"][n]["regimes"]["both"]["exact"])

    def test_nine_bodies_recomputed_to_the_bit(self):
        V, mu, sd, synth = SO.scoring_columns(self.exact)
        again = SO.summarise(*SO.posteriors_at(V, mu, sd, synth, 9))
        self.assertEqual(again, self.rec["widths"]["9"])

    def test_places_add_up_to_the_whole(self):
        for n, row in self.rec["widths"].items():
            parts = row["by_centre"].values()
            self.assertEqual(sum(p["fields"] for p in parts), row["fields"])
            self.assertEqual(sum(p["adjacent_answers"] for p in parts), row["adjacent_answers"])
            flagged = sum(p["off_by_one_below_0.01"] * p["adjacent_answers"] for p in parts)
            self.assertAlmostEqual(flagged / row["adjacent_answers"], row["off_by_one_below_0.01"], places=12)

    def test_more_bodies_catch_more_and_question_less(self):
        rows = [self.rec["widths"][str(n)] for n in (1, 3, 5, 9)]
        for a, b in zip(rows, rows[1:]):
            self.assertLess(a["off_by_one_below_0.01"], b["off_by_one_below_0.01"])
            self.assertGreater(a["correct_below_0.01"], b["correct_below_0.01"])

    def test_latency_is_a_three_body_timing(self):
        lat = self.rec["latency"]
        self.assertEqual((lat["bodies"], lat["calls"]), (3, 50))
        self.assertLessEqual(lat["median_ms"], lat["max_ms"])


class PowerModelTest(unittest.TestCase):
    def test_draws_hit_the_calibrated_accuracy(self):
        right, on_b = SP.draw(np.random.default_rng(11), 400, 30, 40, 0.90, 0.95, (0.25, 0.5), 2)
        self.assertAlmostEqual(right[~on_b].mean(), 0.90, delta=0.006)
        self.assertAlmostEqual(right[on_b].mean(), 0.95, delta=0.006)

    def test_quadrature_inverts_the_calibration(self):
        tau = SP.total_sd(0.25, 1.0)
        self.assertAlmostEqual(SP.marginal(SP.calibrate(0.95, tau), tau), 0.95, places=9)

    def test_each_reader_gets_half_of_each_stratum(self):
        on_b = SP.allocate(np.random.default_rng(3), 5, 7, 40, 2)
        per_stratum = on_b.reshape(5, 7, 2, 20).sum(-1)
        self.assertTrue((per_stratum == 10).all())

    def test_analysis_matches_a_study_worked_by_hand(self):
        # Four readers, four cases, each case read by two readers with each aid.
        on_b = np.array([[[True, False, True, False],
                          [False, True, False, True],
                          [True, False, True, False],
                          [False, True, False, True]]])
        right = np.array([[[1, 1, 1, 0],
                           [1, 1, 0, 1],
                           [1, 1, 0, 0],
                           [0, 1, 1, 1]]], dtype=bool)
        res = SP.analyse(right, on_b)
        # Readers' differences, B minus A: 1 - 1/2, 1 - 1/2, 1/2 - 1/2, 1 - 1/2.
        d = np.array([0.5, 0.5, 0.0, 0.5])
        m, v_readers, df = res["t_interval"]
        self.assertAlmostEqual(m[0], 0.375)
        self.assertAlmostEqual(v_readers[0], d.var(ddof=1) / 4)
        self.assertEqual(df[0], 3.0)
        # Cases' differences 1/2, 0, 0, 1, whose binomial variances average 3/16.
        s2 = np.var([0.5, 0.0, 0.0, 1.0], ddof=1)
        m2, total, _ = res["random"]
        self.assertAlmostEqual(m2[0], 0.375)
        self.assertAlmostEqual(total[0], d.var(ddof=1) / 4 + (s2 - 3 / 16) / 4)


class PowerRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = _load("study_power.json")
        cls.grid = {(r["readers"], r["primary_cases"]): r for r in cls.rec["grid"]}

    def test_record_is_this_code_s(self):
        self.assertEqual(self.rec["seed"], SP.SEED)
        self.assertEqual((self.rec["power_reps"], self.rec["size_reps"]), (SP.POWER_REPS, SP.SIZE_REPS))

    def test_critical_values_are_the_largest_quantiles(self):
        for r in self.rec["grid"]:
            ni = [v["pivot_975"] for k, v in r["size"].items() if k.startswith("noninferiority")]
            sup = [v["pivot_975"] for k, v in r["size"].items() if k.startswith("superiority")]
            self.assertEqual(r["critical_noninferiority"], max(ni))
            self.assertEqual(r["critical_superiority"], max(sup))

    def test_power_grows_with_readers_and_cases(self):
        for key in ("noninferiority_0.95_0.95_%s", "superiority_0.9_0.95_%s"):
            for s in SETTINGS:
                for readers in SP.GRID_READERS:
                    ps = [self.grid[(readers, c)]["power"][key % s]["calibrated"] for c in SP.GRID_CASES]
                    self.assertEqual(ps, sorted(ps))
                for cases in SP.GRID_CASES:
                    ps = [self.grid[(r, cases)]["power"][key % s]["calibrated"] for r in SP.GRID_READERS]
                    self.assertEqual(ps, sorted(ps))

    def test_power_falls_as_the_aid_effect_varies_more(self):
        for r in self.rec["grid"]:
            ps = [r["power"]["noninferiority_0.95_0.95_%s" % s]["calibrated"] for s in SETTINGS]
            self.assertEqual(ps, sorted(ps, reverse=True))

    def test_a_stratum_at_holm_s_first_level_never_beats_five_percent(self):
        for s in self.rec["strata"]:
            for v in s["power"].values():
                self.assertLessEqual(v["calibrated_at_holm_first"], v["calibrated_at_5"])
            self.assertGreater(s["critical_at_holm_first"], s["critical_at_5"])


class ChecksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rec = _load("checks.json")
        with open(SO.RECORD, encoding="utf-8") as fh:
            cls.exact = json.load(fh)
        with open(W.SUPPLEMENT, encoding="utf-8") as fh:
            cls.supplement = json.load(fh)

    def test_within_one_rule_on_a_posterior_worked_by_hand(self):
        post = np.array([[0.4, 0.0, 0.3, 0.3]])
        self.assertEqual(int(post.argmax(1)[0]), 0)
        best = W.best_within_one(post)
        self.assertEqual(int(best[0]), 1)
        self.assertAlmostEqual(float(W.run_mass(post, best)[0]), 0.7)

    def test_the_count_from_c2_names_a_typical_column_as_it_is(self):
        self.assertEqual(W.COUNT_FROM_C2[:len(E.LEVELS)], list(E.LEVELS))

    def test_within_one_agrees_with_the_record_and_never_does_worse(self):
        for n, row in self.rec["within_one"].items():
            both = self.exact["widths"][n]["regimes"]["both"]
            self.assertEqual(row["exact"], both["exact"])
            self.assertEqual(row["argmax_within_one"], both["within_one"])
            self.assertGreaterEqual(row["best_within_one"], row["argmax_within_one"])
            self.assertAlmostEqual(row["best_within_one_predicted"], row["best_within_one"], delta=0.005)

    def test_anomalous_columns_agree_with_the_supplement(self):
        for ph, widths in self.rec["anomalous"].items():
            for n, row in widths.items():
                rec = self.supplement["anomalous"][ph].get(n)
                if rec is not None:
                    self.assertEqual((row["fields"], row["answered"], row["wrong_own"]),
                                     (rec["fields"], rec["answered"], rec["wrong"]))

    def test_the_count_changes_nothing_where_it_agrees_with_the_names(self):
        for ph in ("six_lumbar", "four_lumbar"):
            for row in self.rec["anomalous"][ph].values():
                self.assertEqual(row["wrong_count"], row["wrong_own"])
                self.assertEqual(row["right_count_all"], row["right_own_all"])
        for row in self.rec["anomalous"]["t13"].values():
            self.assertGreaterEqual(row["wrong_count"], row["wrong_own"])


if __name__ == "__main__":
    unittest.main()
