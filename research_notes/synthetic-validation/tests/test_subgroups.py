"""The population register and the subgroup meta-analysis against what their docstrings say:

- the register holds every cohort a usable series names, under the main selection and with the
  strata apart, places every country, and tags a series with every variable;
- the strata-apart selection keeps the main selection's whole series and adds strata and sexes;
- two subgroups far apart fail the test for subgroup differences and account for the spread,
  two alike do not; a subgroup of one series gives no spread of its own;
- one paper against the rest reads Tan 2004 as tan.matched_spread does, to the bit;
- a within-paper contrast recovers a known difference and pairs only within a cohort's stratum.
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

from synthval import literature as L  # noqa: E402
from synthval import register as RG  # noqa: E402
from synthval import subgroups as SG  # noqa: E402
from synthval import tan as T  # noqa: E402


def series(paper, cohort, mean, sd=2.0, n=40.0, key="h_post", level="L1", sex="all", group="", technique="t"):
    return L.Series(paper, cohort, technique, "bone", group, sex, key, level, mean, sd, n, "same")


def population(paper, cohort, country="not stated", ancestry="not stated", specimen="living", age_mean=None):
    return RG.Population(paper, cohort, country, "stated" if country != "not stated" else "not stated", ancestry,
                         ancestry, "stated" if ancestry != "not stated" else "not stated", specimen, "", age_mean,
                         None, None, None, None, None, "", "", "", "")


class Register(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = L.load_rows()
        cls.series, _ = L.select(cls.rows)
        cls.apart, _ = L.select(cls.rows, strata=L.STRATA_APART)
        cls.register = RG.load()

    def test_the_register_holds_together_for_both_selections(self):
        self.assertEqual(RG.check(self.series, self.register), [])
        self.assertEqual(RG.check(self.apart, self.register), [])

    def test_every_usable_cohort_is_registered_once(self):
        pairs = {(s.paper, s.cohort) for s in self.series if L.usable(s)}
        self.assertTrue(pairs <= set(self.register))
        self.assertEqual(len(pairs), len(self.register))

    def test_a_series_is_tagged_with_every_variable(self):
        s = next(s for s in self.series if s.paper == "tan2004")
        tags = RG.tag(s, self.register)
        self.assertEqual(set(tags), set(RG.VARIABLES))
        self.assertEqual((tags["country"], tags["region"], tags["ancestry"], tags["specimen"]),
                         ("Singapore", "East Asia", "Chinese", "dry bone"))
        self.assertEqual(tags["decade"], "2000s")

    def test_a_stratums_ancestry_comes_from_its_group(self):
        s = series("yu2015", "hamann_todd_503", 10.0, group="African American")
        self.assertEqual(RG.tag(s, self.register)["ancestry"], "African American")
        self.assertEqual(RG.tag(series("yu2015", "hamann_todd_503", 10.0), self.register)["ancestry"],
                         "Caucasian and African American")

    def test_check_refuses_a_country_region_of_does_not_place(self):
        bad = {("p", "c"): population("p", "c", country="Atlantis")}
        self.assertTrue(any("Atlantis" in x for x in RG.check([], bad)))

    def test_the_apart_selection_keeps_the_whole_series_and_adds_strata(self):
        by = {(s.paper, s.cohort, s.key, s.level, s.group, s.sex): s.mean for s in self.apart}
        for s in self.series:
            if s.flag.startswith("sexes pooled"):
                continue
            self.assertEqual(by[s.paper, s.cohort, s.key, s.level, s.group, s.sex], s.mean)
        self.assertGreater(len(self.apart), len(self.series))
        self.assertTrue(any(s.flag.startswith("sex apart") for s in self.apart))
        with self.assertRaises(ValueError):
            L.select(self.rows, strata="sideways")


class Subgroups(unittest.TestCase):
    def setUp(self):
        self.register = {("a%d" % i, "c"): population("a%d" % i, "c", country="X") for i in range(3)}
        self.register.update({("b%d" % i, "c"): population("b%d" % i, "c", country="Y") for i in range(3)})

    def test_two_subgroups_far_apart_fail_the_test_and_account_for_the_spread(self):
        rows = [series("a%d" % i, "c", 30.0 + 0.1 * i) for i in range(3)] + [series("b%d" % i, "c", 36.0 + 0.1 * i) for i in range(3)]
        got = SG.analysis(rows, "country", self.register)
        self.assertEqual(len(got), 1)
        r = got[0]
        self.assertEqual((r["groups"], r["k"], r["df"]), (2, 6, 1))
        self.assertLess(r["p_between"], 0.001)
        self.assertGreater(r["r2"], 0.9)
        self.assertLess(r["f_within"], r["f_total"])
        self.assertAlmostEqual(r["widest_gap_sd"], (36.1 - 30.1) / r["panjabi_sd"], places=6)

    def test_two_subgroups_alike_pass_the_test_and_account_for_nothing(self):
        rows = [series("a%d" % i, "c", 30.0 + 0.5 * i) for i in range(3)] + [series("b%d" % i, "c", 30.0 + 0.5 * i) for i in range(3)]
        r = SG.analysis(rows, "country", self.register)[0]
        self.assertGreater(r["p_between"], 0.5)
        self.assertEqual(r["r2"], 0.0)

    def test_a_subgroup_of_one_series_gives_its_own_se_and_no_spread(self):
        one = SG.pooled_or_one([series("a0", "c", 30.0, sd=2.0, n=16.0)])
        self.assertEqual((one["k"], one["mean"], one["se"]), (1, 30.0, 0.5))
        self.assertTrue(math.isnan(one["tau2"]))
        rows = [series("a%d" % i, "c", 30.0 + i) for i in range(4)]
        r = SG.analysis(rows, "paper", self.register | {("a3", "c"): population("a3", "c")})[0]
        self.assertEqual(r["groups_with_two_or_more"], 0)
        self.assertTrue(math.isnan(r["r2"]))

    def test_tan_against_the_rest_is_tan_py_reading(self):
        snapshot, _ = L.select(L.load_rows())
        register = RG.load()
        got = SG.against_rest(snapshot, "paper", "tan2004", register)
        want = T.matched_spread(snapshot)
        self.assertEqual([(r["measure"], r["level"]) for r in got], [(r["measure"], r["level"]) for r in want])
        np.testing.assert_allclose([r["distance_sd"] for r in got], [r["tan_distance_panjabi_sd"] for r in want], rtol=1e-12)
        np.testing.assert_allclose([r["f_apart"] for r in got], [r["f_panjabi_apart"] for r in want], rtol=1e-12)

    def test_a_paired_contrast_recovers_a_known_difference_within_cohorts(self):
        rows = []
        for i in range(3):
            rows.append(series("p%d" % i, "c", 30.0 + i, sex="male", group="g"))
            rows.append(series("p%d" % i, "c", 28.0 + i, sex="female", group="g"))
        rows.append(series("p9", "c", 50.0, sex="male", group="h"))           # no partner in its stratum
        rows.append(series("p9", "c", 20.0, sex="female", group="i"))
        reg = {("p%d" % i, "c"): population("p%d" % i, "c") for i in range(3)} | {("p9", "c"): population("p9", "c")}
        got = SG.paired_contrast(rows, "sex", ("male", "female"), reg)
        self.assertEqual(len(got), 1)
        r = got[0]
        self.assertEqual(r["pairs"], 3)
        self.assertAlmostEqual(r["difference"], 2.0, places=9)
        self.assertLess(r["p"], 0.001)
        self.assertNotIn("p9", r["within"])


if __name__ == "__main__":
    unittest.main()
