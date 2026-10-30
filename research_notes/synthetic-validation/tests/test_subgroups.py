"""The population register and the subgroup meta-analysis against what their docstrings say:

- the register holds every cohort a usable series names, under the main selection and with the
  strata apart, places every country, holds a cohort's group counts to its people, and tags a
  series with every variable;
- the strata-apart selection keeps the main selection's whole series and adds strata and sexes,
  a sex printed apart within a group taking the count the register's group counts give where the
  paper prints none, and no sex-apart series without a count of its own;
- two subgroups far apart fail the test for subgroup differences and account for the spread,
  two alike do not; the test's Q and the spread within are what the hand computes under the
  common spread; a variable whose every subgroup is one series has neither;
- one paper against the rest reads Tan 2004 as tan.matched_spread does, to the bit;
- a within-paper contrast recovers a known difference, pairs only within a cohort's stratum, and
  reads a cohort's strata before its whole.
"""
from __future__ import annotations

import math
import os
import sys
import unittest

import numpy as np
from scipy import stats

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


def population(paper, cohort, country="not stated", ancestry="not stated", specimen="living", age_mean=None,
               n_people=None, n_men=None, n_women=None, group_counts="", year=None):
    return RG.Population(paper, cohort, country, "stated" if country != "not stated" else "not stated", ancestry,
                         ancestry, "stated" if ancestry != "not stated" else "not stated", specimen, "", age_mean,
                         None, None, n_people, n_men, n_women, "", "", "", "", group_counts, year)


SNAPSHOT_HEADER = ("paper,cohort,technique,source_of_values,key,level,sex,group,side,mean,sd,n,sd_from,n_from,units,"
                   "vs_panjabi,species,cohort_n")


def rows_from(lines):
    """Snapshot rows from csv lines in the snapshot's columns, through load_rows."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as fh:
        fh.write(SNAPSHOT_HEADER + "\n" + "\n".join(lines) + "\n")
        path = fh.name
    try:
        return L.load_rows(path)
    finally:
        os.unlink(path)


class Register(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = L.load_rows()
        cls.series, _ = L.select(cls.rows)
        cls.register = RG.load()
        cls.apart, cls.why_apart = L.select(cls.rows, strata=L.STRATA_APART, stratum_counts=RG.stratum_counts(cls.register))

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

    def test_check_holds_the_group_counts_to_the_cohorts_people(self):
        self.assertEqual(RG.check([], {("p", "c"): population("p", "c", n_people=16, group_counts="a:10;b:6")}), [])
        self.assertTrue(any("sum to 15" in x for x in RG.check([], {("p", "c"): population("p", "c", n_people=16, group_counts="a:10;b:5")})))
        self.assertTrue(any("group:n" in x for x in RG.check([], {("p", "c"): population("p", "c", group_counts="ten")})))

    def test_a_sex_printed_apart_takes_the_registers_group_counts_or_is_not_apart(self):
        # Duman 2026 prints each sex of each age band with an SD and no count, counts the bands
        # (198, 176, 143) and the sexes (277 men, 240 women) of its 517; nothing else prints a
        # sex apart with an SD
        counts = RG.stratum_counts(self.register)
        self.assertAlmostEqual(counts["duman2026", "izmir-mdct-517", "18-35", "male"][0], 198 * 277 / 517, places=9)
        self.assertEqual(counts["duman2026", "izmir-mdct-517", ">55", "female"][1], RG.GROUP_SHARE_NOTE)
        sex_apart = [s for s in self.apart if s.flag.startswith("sex apart")]
        self.assertEqual(len(sex_apart), 24)
        self.assertEqual({(s.paper, s.group) for s in sex_apart}, {("duman2026", g) for g in ("18-35", "36-55", ">55")})
        self.assertEqual(sum(1 for s in sex_apart if s.sex == "male"), 12)
        for s in sex_apart:
            self.assertEqual(s.n_note, RG.GROUP_SHARE_NOTE)
            self.assertAlmostEqual(s.n, counts[s.paper, s.cohort, s.group, s.sex][0], places=9)
            self.assertLess(s.n, 110.0)
        pairs = {(s.paper, s.cohort, s.technique, s.group, s.key, s.level) for s in sex_apart}
        self.assertEqual(len(pairs), 12)
        for pair in pairs:
            sexes = {s.sex for s in sex_apart if (s.paper, s.cohort, s.technique, s.group, s.key, s.level) == pair}
            self.assertEqual(sexes, {"male", "female"})
        without, why = L.select(self.rows, strata=L.STRATA_APART)
        self.assertFalse(any(s.flag.startswith("sex apart") for s in without))
        self.assertEqual(len(self.apart) - len(without), 12)   # Duman's 12 pairs pooled in place of apart
        # a pair not read apart is counted by _one_sex alone, so the left-out counts name no pair
        self.assertFalse(any("printed apart" in k for k in why))

    def test_a_sex_pair_printed_with_its_own_counts_is_read_apart(self):
        male = "ptest,c,mdct-axial-pedicle,this paper,pedicle_w,L1,male,20-40,both,9.0,1.5,30,sd,,mm,close,,50"
        female = "ptest,c,mdct-axial-pedicle,this paper,pedicle_w,L1,female,20-40,both,8.5,1.4,20,sd,,mm,close,,50"
        got, _ = L.select(rows_from([male, female]), strata=L.STRATA_APART)
        self.assertEqual([(s.sex, s.n, s.n_note, s.flag) for s in got],
                         [("male", 30.0, "", "sex apart"), ("female", 20.0, "", "sex apart")])
        # a count the cohort's people stand in for is not the row's own: not apart, pooled instead
        got, _ = L.select(rows_from([male, female.replace(",20,sd", ",,sd")]), strata=L.STRATA_APART)
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0].flag.startswith("sex apart"))

    def test_the_registers_counts_hold_to_the_snapshot_and_to_each_other(self):
        cohort_n = {}
        for r in self.rows:
            n = L._num(r.get("cohort_n", ""))
            if math.isfinite(n):
                cohort_n[r["paper"], r["cohort"]] = n
        for p in self.register.values():
            if p.n_people is not None and (p.paper, p.cohort) in cohort_n:
                self.assertEqual(p.n_people, cohort_n[p.paper, p.cohort], (p.paper, p.cohort))
            if None not in (p.n_people, p.n_men, p.n_women):
                self.assertEqual(p.n_men + p.n_women, p.n_people, (p.paper, p.cohort))
        bad = {("p", "c"): population("p", "c", n_people=10, n_men=5, n_women=6)}
        self.assertTrue(any("5 men and 6 women" in x for x in RG.check([], bad)))

    def test_the_year_column_gives_every_cohort_its_decade(self):
        usable = [s for s in self.series if L.usable(s)]
        self.assertFalse(any(RG.tag(s, self.register)["decade"] == RG.NOT_STATED for s in usable))
        italian = next(s for s in usable if s.paper == "italianmri")
        self.assertEqual(RG.tag(italian, self.register)["decade"], "2010s")
        self.assertEqual(population("nodigits", "c", year=1999).decade, "1990s")
        self.assertEqual(population("nodigits", "c").decade, RG.NOT_STATED)
        self.assertEqual(population("tan2004", "c").decade, "2000s")

    def test_six_cohorts_carry_the_count_weighted_mean_of_their_sexes_ages(self):
        for key, mean in ((("abbas2021", "control"), 62.4), (("cizmic2023", "bih-sarajevo-ct"), 43.81),
                          (("masharawi2021", "control"), 62.95), (("olsewski1990", "part1_cadavers"), 75.53),
                          (("olsewski1990", "part3_patients"), 36.65), (("tang2016", "utah_mri"), 30.3)):
            p = self.register[key]
            self.assertEqual(p.age_mean, mean, key)
            self.assertIn("count-weighted mean", p.notes, key)

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

    def test_a_variable_of_single_series_has_no_test_and_no_share(self):
        rows = [series("a%d" % i, "c", 30.0 + i) for i in range(4)]
        r = SG.analysis(rows, "paper", self.register | {("a3", "c"): population("a3", "c")})[0]
        self.assertEqual((r["groups_with_two_or_more"], r["df_within"], r["df"]), (0, 0, 3))
        self.assertTrue(math.isnan(r["r2"]) and math.isnan(r["p_between"]) and math.isnan(r["q_between"]))
        summary = SG.analysis_summary([r])["paper"]["all"]
        self.assertEqual((summary["cells_tested"], summary["r2"]["cells"]), (0, 0))
        # one pooled subgroup of two series is one degree of freedom, below LEAST_DF
        rows = [series("a0", "c", 30.0), series("a0", "d", 31.0), series("a1", "c", 36.0), series("a2", "c", 37.0)]
        reg = self.register | {("a0", "d"): population("a0", "d", country="X")}
        r = SG.analysis(rows, "paper", reg)[0]
        self.assertEqual((r["groups_with_two_or_more"], r["df_within"]), (1, 1))
        self.assertTrue(math.isnan(r["r2"]) and math.isnan(r["p_between"]))

    def test_the_test_and_the_spread_within_are_what_the_hand_computes(self):
        x = [series("a%d" % i, "c", 30.0 + i, sd=2.0, n=40.0) for i in range(3)]
        y = [series("b0", "c", 36.0, sd=2.0, n=40.0)]
        r = SG.analysis(x + y, "country", self.register)[0]
        tau2 = SG.pooled_or_one(x)["tau2"]
        self.assertEqual(r["df_within"], 2)
        self.assertAlmostEqual(r["tau2_within"], tau2, places=12)
        v = 4.0 / 40.0 + tau2
        se_x2, se_y2 = v / 3.0, v
        q = (31.0 - 36.0) ** 2 / (se_x2 + se_y2)
        self.assertAlmostEqual(r["q_between"], q, places=9)
        self.assertEqual(r["df"], 1)
        self.assertAlmostEqual(r["p_between"], float(stats.chi2.sf(q, 1)), places=12)
        self.assertAlmostEqual(r["r2"], max(0.0, 1.0 - tau2 / r["tau2_total"]), places=12)
        g = SG.common_tau_estimate(y, tau2)
        self.assertAlmostEqual(g["se"] ** 2, se_y2, places=12)
        # two pooled subgroups: tau^2 within is theirs averaged on their degrees of freedom
        z = [series("b0", "c", 36.0), series("b1", "c", 38.0)]
        sub = {"X": SG.pooled_or_one(x), "Y": SG.pooled_or_one(z)}
        tau2_within, groups, df = SG.spread_within(sub)
        self.assertEqual((groups, df), (2, 3))
        self.assertAlmostEqual(tau2_within, (2 * sub["X"]["tau2"] + sub["Y"]["tau2"]) / 3, places=12)

    def test_tan_against_the_rest_is_tan_py_reading(self):
        snapshot, _ = L.select(L.load_rows())
        register = RG.load()
        got = SG.against_rest(snapshot, "paper", "tan2004", register)
        want = T.matched_spread(snapshot)
        self.assertEqual([(r["measure"], r["level"]) for r in got], [(r["measure"], r["level"]) for r in want])
        np.testing.assert_allclose([r["distance_sd"] for r in got], [r["tan_distance_panjabi_sd"] for r in want], rtol=1e-12)
        np.testing.assert_allclose([r["f_apart"] for r in got], [r["f_panjabi_apart"] for r in want], rtol=1e-12)
        # and the inside flags are the prediction's, t and z
        pred = T.prediction_by_stratum(snapshot)
        self.assertEqual([(r["measure"], r["level"]) for r in pred], [(r["measure"], r["level"]) for r in got])
        self.assertEqual([r["inside_rest_t"] for r in got], [bool(r["tan_inside_rest"]) for r in pred])
        self.assertEqual([r["inside_rest_z"] for r in got], [bool(r["tan_inside_rest_plug"]) for r in pred])
        self.assertTrue(any(not r["inside_rest_z"] for r in got) and any(r["inside_rest_t"] for r in got))

    def test_a_value_of_several_series_is_held_to_the_interval_for_their_mean(self):
        from synthval.validate import literature_at
        rest = [series("a%d" % i, "c", 30.0 + 0.5 * i) for i in range(3)]
        own = [series("b0", "c", 32.0), series("b1", "c", 33.5)]
        r = SG.against_rest(rest + own, "country", "Y", self.register)[0]
        self.assertEqual((r["k_value"], r["k_rest"]), (2, 3))
        apart = literature_at(rest).mean
        distance = SG.pooled_or_one(own)["mean"] - apart.mean
        one = math.sqrt(apart.tau2 + apart.se ** 2)
        scale = math.sqrt(apart.tau2 / 2 + apart.se ** 2)
        self.assertLess(scale, one)
        t_multiplier = (apart.pi_high - apart.mean) / one
        self.assertEqual(r["inside_rest_t"], abs(distance) <= t_multiplier * scale)
        self.assertEqual(r["inside_rest_z"], abs(distance) <= SG.Z * scale)
        self.assertAlmostEqual(r["distance_sd"] * r["panjabi_sd"], distance, places=12)

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

    def test_a_paired_contrast_takes_both_sides_variances(self):
        reg = {("p", "c"): population("p", "c")}
        rows = [series("p", "c", 30.0, sd=2.0, n=40.0, sex="male", group="g"),
                series("p", "c", 27.0, sd=4.0, n=10.0, sex="female", group="g")]
        r = SG.paired_contrast(rows, "sex", ("male", "female"), reg)[0]
        se = math.sqrt(4.0 / 40.0 + 16.0 / 10.0)
        self.assertAlmostEqual(r["se"], se, places=12)
        self.assertAlmostEqual(r["z"], 3.0 / se, places=12)
        self.assertAlmostEqual(r["ci_high_sd"] * r["panjabi_sd"], 3.0 + SG.Z * se, places=9)
        self.assertAlmostEqual(r["p"], 2 * stats.norm.sf(3.0 / se), places=12)

    def test_a_paired_contrast_reads_a_cohorts_strata_before_its_whole(self):
        reg = {("p", "c"): population("p", "c")}
        whole = [series("p", "c", 30.0, n=80.0, sex="male"), series("p", "c", 28.0, n=80.0, sex="female")]
        strata = [series("p", "c", 30.0 + i, n=40.0, sex="male", group=g) for i, g in enumerate(("young", "old"))]
        strata += [series("p", "c", 28.0 + i, n=40.0, sex="female", group=g) for i, g in enumerate(("young", "old"))]
        alone = SG.paired_contrast(whole, "sex", ("male", "female"), reg)[0]
        both = SG.paired_contrast(whole + strata, "sex", ("male", "female"), reg)[0]
        self.assertEqual((alone["pairs"], both["pairs"]), (1, 2))
        self.assertEqual(set(both["within"].split(";")), {"p/c/t/young", "p/c/t/old"})
        self.assertAlmostEqual(both["se"], alone["se"], places=9)   # the same 160 people, counted once
        # the ancestries of one collection: the whole is the sex-pooled row
        reg = {("y", "c"): population("y", "c")}
        rows = [series("y", "c", 10.0, sex="all", group="A"), series("y", "c", 11.0, sex="all", group="B"),
                series("y", "c", 10.0, sex="male", group="A"), series("y", "c", 11.0, sex="male", group="B"),
                series("y", "c", 10.0, sex="female", group="A"), series("y", "c", 11.0, sex="female", group="B")]
        tag = RG.tag
        RG.GROUP_ANCESTRY.update({("y", "A"): "A", ("y", "B"): "B"})
        try:
            r = SG.paired_contrast(rows, "ancestry", ("A", "B"), reg)[0]
        finally:
            del RG.GROUP_ANCESTRY["y", "A"], RG.GROUP_ANCESTRY["y", "B"]
        self.assertEqual(r["pairs"], 2)
        self.assertEqual({w.split("/")[3] for w in r["within"].split(";")}, {"male", "female"})
        self.assertIs(tag, RG.tag)


if __name__ == "__main__":
    unittest.main()
