"""Knowing the patient's sex while naming, held to what synthval/sex_naming.py's docstrings say.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- the two sexes' tables keep the table's mean and SD half and half, and their means sit g
  within-sex SDs apart;
- at d = 0 the sexes' tables are the sexless table, and rule B and the mixture A' gain nothing on
  any score, exactly with the shortcut and within rounding without it, every evidence computed;
- the mixture A' on the run's own path is log((p_men + p_women) / 2) of the two sexes' tables'
  evidences, and B each person's own sex's;
- at d = 1.5 rule B, on the generator it is exact for, beats rule A and the mixture A' on the log
  score by more than its SE, and names more;
- the shapes put d where they say: the same at every cell, by the profile's level, each measure's
  g, each cell's g else its measure's;
- the records' level profile is read from series complete over the run, each paper one vote,
  and has mean 1;
- the seeds are numpy SeedSequence streams, one per unit and stream, none shared, and one stream
  draws the same persons every time it is read;
- the tallies give select's calibration error and precision, and two identical rules differ by
  nothing, with no spread under the bootstrap;
- P's own rows never reach rule A's or rule B's table or g: moving every number P prints leaves
  both tables as they were, while B moves by the other papers' g alone, and P's own tables and
  ceilings do read P;
- on the snapshot, with the sexes the reread's series.py pooled away read beside it: the
  covariate records this reads are the snapshot's own; moving every number a scored paper prints,
  both sexes' means, SDs and counts and the sexes together's, leaves its rules' tables A and B and
  the g B reads as they were, for every paper scored; Bach 2019's persons are his whole cohort by
  sex, Chaudhary 2015's are drawn with each sex's printed SD, and a means-only paper (Eisenstein
  1977) is flagged as synthetic; Bach 2019's inner temperature is select.py's own, and a paper
  with no inner fold is named a fallback; each paper printing both sexes is read or says why not;
- pooled over populations, the headline SE is their SD over sqrt(k), with the persons' SE beside
  it, and the headline leaves out the papers whose persons' SD is borrowed from the rule's pool.
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

from synthval import covariates as CV  # noqa: E402
from synthval import literature as L  # noqa: E402
from synthval import papers_table as PT  # noqa: E402
from synthval import select as SEL  # noqa: E402
from synthval import sex_naming as SN  # noqa: E402
from synthval import strata as ST  # noqa: E402
from synthval.population import GENERATOR  # noqa: E402

LUMBAR = list(ST.LUMBAR)
VOC = {"canal_ap": {"kind": "length"}, "h_ant": {"kind": "length"}}
KEYS = ["canal_ap", "h_ant"]


def series(paper, key, level, mean, sd=2.0, n=30.0):
    return L.Series(paper=paper, cohort="c", technique="ct", modality="ct", group="", sex="all", key=key, level=level,
                    mean=mean, sd=sd, n=n, vs_panjabi="same", sd_uncertain=False)


def papers(shifts, scale=1.0):
    """Papers printing two measures at every lumbar level, each moved from a base by its own shift
    in SDs; `scale` multiplies every number of the papers given."""
    base = {"canal_ap": 17.0, "h_ant": 26.0}
    return [series(p, key, lv, scale * (base[key] + 0.5 * i + 2.0 * s), sd=2.0 * scale)
            for p, s in shifts.items() for key in KEYS for i, lv in enumerate(LUMBAR)]


def contrasts(paper, g_of_level, key="canal_ap", scale=1.0):
    """A paper's men and women at every lumbar level, men g within-sex SDs above."""
    return [CV.Contrast(paper, "c", key, lv, "", scale * (20.0 + 2.0 * g), 2.0 * scale, 100.0, scale * 20.0, 2.0 * scale, 100.0)
            for lv, g in zip(LUMBAR, g_of_level)]


def toy_table():
    cells = ST.strata_of(papers({"a": 0.0, "b": 0.5, "c": -0.5}))
    return cells, ST.others_table(cells, None, KEYS, VOC, SN.NO_SHIFT, False)


def run_rules(table, g, persons=400, seed=11, width=1, shortcut=True):
    men, women = SN.split_by_sex(table, g)
    seeds = SN.streams(seed, 1)[0]
    pops = SN.draw_sexes(men, women, GENERATOR, persons, seeds)
    weights = SN.resample_weights(SN.persons_of(pops), 50, np.random.default_rng(seeds["bootstrap"]))
    scored = SN.synthetic_rules(pops, table, men, women, width, GENERATOR, shortcut)
    return {(r["rule"], r["against"]): r for r in SN.compare(scored, SN.SYNTHETIC_COMPARISONS, weights)}, scored


class SexNaming(unittest.TestCase):
    def test_the_two_sexes_keep_the_tables_mean_and_sd_half_and_half(self):
        _, table = toy_table()
        g = np.linspace(0.0, 2.0, table.mu.size).reshape(table.mu.shape)
        men, women = SN.split_by_sex(table, g)
        np.testing.assert_allclose((men.mu + women.mu) / 2.0, table.mu, rtol=1e-12)
        np.testing.assert_allclose(men.sd, women.sd)
        np.testing.assert_allclose(men.sd ** 2 + ((men.mu - women.mu) / 2.0) ** 2, table.sd ** 2, rtol=1e-12)
        np.testing.assert_allclose((men.mu - women.mu) / men.sd, g, atol=1e-12)

    def test_d_zero_gives_zero_gain(self):
        _, table = toy_table()
        men, women = SN.split_by_sex(table, SN.common_shift(table, 0.0))
        self.assertTrue(SN.same_table(men, table) and SN.same_table(women, table))
        for width in (1, 2, 3):
            got, scored = run_rules(table, 0.0, persons=60, width=width)
            for key in ((SN.RULE_B, SN.RULE_A), (SN.RULE_MIX, SN.RULE_A), (SN.RULE_B, SN.RULE_MIX)):
                for m in SN.DIFFS:
                    d = got[key]["d_" + m]
                    none_answered = m == "precision" and got[key]["n_answered"] == 0
                    self.assertTrue(d == 0.0 or (none_answered and math.isnan(d)), (key, m, d))
            np.testing.assert_array_equal(scored[SN.RULE_B]["_lp"], scored[SN.RULE_A]["_lp"])
        # the mixture's own sum, without the shortcut, is the sexless evidence itself
        ev = np.random.default_rng(1).normal(size=(20, 5))
        np.testing.assert_allclose(SEL.mixture_evidence([ev, ev]), ev, rtol=1e-12, atol=1e-12)

    def test_d_zero_gives_zero_gain_through_the_whole_scorer_without_the_shortcut(self):
        _, table = toy_table()
        for width in (1, 2, 3):
            got, scored = run_rules(table, 0.0, persons=60, width=width, shortcut=False)
            np.testing.assert_array_equal(scored[SN.RULE_B]["_lp"], scored[SN.RULE_A]["_lp"])
            np.testing.assert_allclose(scored[SN.RULE_MIX]["_lp"], scored[SN.RULE_A]["_lp"], rtol=0, atol=1e-12)
            for key in ((SN.RULE_B, SN.RULE_A), (SN.RULE_MIX, SN.RULE_A), (SN.RULE_B, SN.RULE_MIX)):
                self.assertEqual(got[key]["d_exact"], 0.0, (key, width))
                self.assertEqual(got[key]["d_answered"], 0.0, (key, width))
                for m in ("log_score", "ece", "precision"):
                    d = got[key]["d_" + m]
                    none_answered = m == "precision" and got[key]["n_answered"] == 0
                    self.assertTrue(abs(d) <= 1e-12 or (none_answered and math.isnan(d)), (key, m, d))

    def test_the_mixture_on_the_runs_own_path_is_the_mean_of_the_two_sexes_likelihoods(self):
        _, table = toy_table()
        men, women = SN.split_by_sex(table, SN.common_shift(table, 1.0))
        pops = SN.draw_sexes(men, women, GENERATOR, 40, SN.streams(7, 1)[0])
        for width in (1, 3):
            ev, truth, group = SN.rule_evidence(pops, table, men, women, width, GENERATOR, shortcut=False)
            by_table = [[SEL.log_evidence(pop, t, width, GENERATOR)[0] for t in (men, women)] for pop in pops]
            # log((p_m + p_f) / 2), shifted by the larger so that no exp under- or overflows
            mixed = []
            for e_m, e_f in by_table:
                top = np.maximum(e_m, e_f)
                mixed.append(top + np.log(0.5 * np.exp(e_m - top) + 0.5 * np.exp(e_f - top)))
            np.testing.assert_allclose(ev[SN.RULE_MIX], np.concatenate(mixed), rtol=1e-12, atol=1e-12)
            np.testing.assert_array_equal(ev[SN.RULE_B], np.concatenate([by_table[0][0], by_table[1][1]]))
            sexless = np.concatenate([SEL.log_evidence(pop, table, width, GENERATOR)[0] for pop in pops])
            np.testing.assert_array_equal(ev[SN.RULE_A], sexless)
            # and the scores of synthetic_rules are those of these evidences
            scored = SN.synthetic_rules(pops, table, men, women, width, GENERATOR, shortcut=False)
            np.testing.assert_array_equal(scored[SN.RULE_MIX]["_lp"], SN.score_rule(ev[SN.RULE_MIX], truth, group)["_lp"])
            self.assertFalse(np.allclose(ev[SN.RULE_MIX], ev[SN.RULE_A]))

    def test_rule_b_on_its_own_generator_beats_rule_a_at_d_one_and_a_half(self):
        _, table = toy_table()
        for width in (1, 2):
            got, _ = run_rules(table, SN.common_shift(table, 1.5), persons=400, width=width)
            b_a, b_mix = got[SN.RULE_B, SN.RULE_A], got[SN.RULE_B, SN.RULE_MIX]
            self.assertGreater(b_a["d_log_score"], 2.0 * b_a["d_log_score_se"])
            self.assertGreater(b_mix["d_log_score"], 0.0)
            self.assertGreater(b_a["d_exact"], 0.0)
            self.assertGreater(got[SN.RULE_B, SN.RULE_A]["log_score"], got[SN.RULE_A, ""]["log_score"])

    def test_the_shapes_put_d_where_they_say(self):
        _, table = toy_table()
        np.testing.assert_array_equal(SN.common_shift(table, 0.8), np.full(table.mu.shape, 0.8))
        profile = dict(zip(LUMBAR, (1.4, 1.2, 1.0, 0.8, 0.6)))
        got = SN.level_shift(table, 0.5, profile)
        np.testing.assert_allclose(got, np.tile([0.7, 0.6, 0.5, 0.4, 0.3], (2, 1)))
        self.assertAlmostEqual(float(got.mean()), 0.5)
        base_of = {"canal_ap": "canal_ap", "h_ant": "h_ant"}
        per_measure = SN.measure_shift(table, base_of, {"canal_ap": 1.2})
        np.testing.assert_array_equal(per_measure, [[1.2] * 5, [0.0] * 5])
        per_cell = SN.cell_shift(table, base_of, {("canal_ap", "L2"): 0.4, ("h_ant", "L5"): 2.0}, {"canal_ap": 1.2})
        np.testing.assert_array_equal(per_cell, [[1.2, 0.4, 1.2, 1.2, 1.2], [0.0, 0.0, 0.0, 0.0, 2.0]])

    def test_the_level_profile_is_read_from_complete_series_each_paper_one_vote_and_has_mean_one(self):
        falling = (1.0, 0.8, 0.6, 0.4, 0.2)
        cells_g = SN.placed(contrasts("a", falling) + contrasts("a", (1.0,) * 5, key="h_ant")
                            + contrasts("b", (0.2, 0.4, 0.6, 0.8, 1.0), key="h_ant")
                            + contrasts("c", (2.0, 2.0, 2.0, 2.0, 2.0))[:3])
        profile, by_paper = SN.level_profile(cells_g)
        self.assertEqual(sorted(by_paper), ["a", "b"])
        self.assertEqual(by_paper["a"]["series"], ["canal_ap", "h_ant"])
        self.assertAlmostEqual(float(np.mean(list(profile.values()))), 1.0)
        # a's two series averaged first (its falling one over its mean g, 0.6, and its flat one), then
        # a and b one vote each, so a paper's many series weigh no more than b's one
        a = (np.array(falling) / 0.6 + 1.0) / 2.0
        b = np.array([0.2, 0.4, 0.6, 0.8, 1.0]) / 0.6
        np.testing.assert_allclose([by_paper["a"]["profile"][lv] for lv in LUMBAR], a, rtol=1e-6)
        np.testing.assert_allclose([profile[lv] for lv in LUMBAR], (a + b) / 2.0, rtol=1e-6)

    def test_the_seeds_are_streams_of_their_own_and_one_stream_draws_the_same_persons(self):
        units = SN.streams(SN.SEED_SYNTHETIC, 3) + SN.streams(SN.SEED_HELD_OUT, 3)
        states = [tuple(s.generate_state(4)) for u in units for s in u.values()]
        self.assertEqual(len(states), len(set(states)))
        self.assertEqual(sorted(units[0]), sorted(SN.STREAMS))
        _, table = toy_table()
        seeds = SN.streams(5, 1)[0]
        first = SN.draw_sexes(table, table, GENERATOR, 10, seeds)
        again = SN.draw_sexes(table, table, GENERATOR, 10, seeds)
        np.testing.assert_array_equal(first[0].measured, again[0].measured)
        self.assertFalse(np.array_equal(first[0].measured, first[1].measured[:first[0].measured.shape[0]]))

    def test_the_tallies_give_the_calibration_error_and_precision_and_identical_rules_differ_by_nothing(self):
        _, table = toy_table()
        _, scored = run_rules(table, 0.8, persons=80, width=1)
        a = scored[SN.RULE_A]
        t = SN.tallies(a, 80)
        one = np.ones((1, 80))
        self.assertAlmostEqual(float(SN.ece_of(t, one)[0]), a["ece"], places=12)
        if a["n_answered"]:
            self.assertAlmostEqual(float(SN.precision_of(t, one)[0]), a["precision"], places=12)
        weights = SN.resample_weights(np.arange(80) < 40, 30, np.random.default_rng(5))
        np.testing.assert_array_equal(weights[:, :40].sum(1), 40)
        np.testing.assert_array_equal(weights[:, 40:].sum(1), 40)
        same = SN.paired(a, a, weights)
        for m in SN.DIFFS:
            self.assertTrue(same["d_" + m] == 0.0 or (m == "precision" and a["n_answered"] == 0))
            self.assertTrue(same["d_%s_se" % m] == 0.0 or math.isnan(same["d_%s_se" % m]))

    def test_the_papers_own_rows_never_reach_its_own_tables(self):
        others = {"b": 0.5, "c": -0.5}
        g_b = (1.0, 0.8, 0.6, 0.4, 0.2)

        def tables(scale):
            cells = ST.strata_of(papers({"a": 0.3}, scale) + papers(others))
            cells_g = SN.placed(contrasts("a", (3.0 * scale,) * 5, scale=scale) + contrasts("b", g_b))
            return cells, SN.rule_tables(cells, cells_g, "a", KEYS, VOC)

        cells, first = tables(1.0)
        _, moved = tables(1.7)
        for name in ("A", "B_men", "B_women"):
            np.testing.assert_array_equal(first[name].mu, moved[name].mu)
            np.testing.assert_array_equal(first[name].sd, moved[name].sd)
        np.testing.assert_array_equal(first["g"], moved["g"])
        # B moves canal_ap by b's g alone, cell by cell, and leaves h_ant, which no other paper prints apart
        np.testing.assert_allclose(first["g"][0], g_b, rtol=0, atol=1e-2)
        self.assertTrue(all(s == "cell" for s in first["scope"][0]) and all(s == "none" for s in first["scope"][1]))
        np.testing.assert_array_equal(first["B_men"].mu[1], first["A"].mu[1])
        sw = SN.within_sd(first["A"].sd[0], first["g"][0])
        np.testing.assert_allclose(first["B_men"].mu[0] - first["A"].mu[0], 0.5 * first["g"][0] * sw)
        plain = ST.others_table(cells, "a", KEYS, VOC, SN.NO_SHIFT, False)
        np.testing.assert_array_equal(first["A"].mu, plain.mu)
        # with b's contrasts gone no other paper gives a g, and B is A
        alone = SN.rule_tables(cells, SN.placed(contrasts("a", (3.0,) * 5)), "a", KEYS, VOC)
        self.assertTrue(SN.same_table(alone["B_men"], alone["A"]) and not alone["g"].any())
        # P's own g, the ceiling's, is read from P alone
        own, _ = SN.effect_grid(first["A"], {"canal_ap": "canal_ap", "h_ant": "h_ant"},
                                SN.placed(contrasts("a", (3.0,) * 5) + contrasts("b", g_b)), "a", own=True)
        self.assertGreater(own[0].min(), 2.9)


MEN, WOMEN, TOGETHER = (1.03, 1.2, 1.3), (0.98, 0.9, 1.1), (1.01, 1.1, 1.2)
SMALL_MEN, SMALL_WOMEN = (1.002, 1.2, 1.3), (0.999, 0.9, 1.1)


def moved(rows, paper, men=MEN, women=WOMEN, together=TOGETHER):
    """The rows with every number `paper` prints moved, its men's, women's and the sexes together's
    mean, SD and count each by its own factor (mean, sd, n), so that its own g moves too; the
    sexes' snapshot's rows with the full snapshot's."""
    out = []
    for r in rows:
        if r["paper"] != paper:
            out.append(r)
            continue
        a, b, c = men if r["sex"] == "male" else women if r["sex"] == "female" else together
        out.append(dict(r, mean=r["mean"] * a, sd=r["sd"] * b, n=r["n"] * c))
    return out


class OnTheSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.voc = PT.load_rows_all(), PT.load_vocabulary()
        cls.with_sexes = cls.rows + PT.load_rows_sexes()
        cls.cells = ST.strata_of(PT.select_all(cls.rows)[0])
        records = os.path.join(NOTE, "records", "covariates")
        cls.recorded = SN.load_contrasts(os.path.join(records, "contrasts.csv"))
        cls.effects = SN.load_effects(os.path.join(records, "effects.csv"))
        cls.contrasts = CV.sex_contrasts(cls.with_sexes, cls.voc)
        cls.cover = SN.coverage(cls.cells, cls.contrasts, cls.voc)

    def test_the_covariate_records_are_the_snapshots_own(self):
        self.assertEqual(len(self.contrasts), len(self.recorded))
        for c, r in zip(self.contrasts, self.recorded):
            self.assertFalse(SN.contrast_differs(r, c), (c.paper, c.base_key, c.level, c.group))
        for e in CV.effects(self.contrasts, "sex"):
            self.assertAlmostEqual(self.effects[e["measure"]], e["mean"], places=9)

    def assert_rules_unmoved(self, paper, men=MEN, women=WOMEN, together=TOGETHER):
        first = SN.held_out_tables(self.cells, self.with_sexes, self.contrasts, paper, self.voc)
        rows = moved(self.with_sexes, paper, men, women, together)
        cells = ST.strata_of(PT.select_all([r for r in rows if not r.get("apart")])[0])
        again = SN.held_out_tables(cells, rows, CV.sex_contrasts(rows, self.voc), paper, self.voc)
        self.assertEqual(first["keys"], again["keys"])
        for name in ("A", "B_men", "B_women"):
            np.testing.assert_array_equal(first[name].mu, again[name].mu)
            np.testing.assert_array_equal(first[name].sd, again[name].sd)
        np.testing.assert_array_equal(first["g"], again["g"])
        # what P's own rows do reach: its own persons and the ceiling's g
        np.testing.assert_allclose(again["own_men"].mu, first["own_men"].mu * men[0], rtol=1e-9)
        np.testing.assert_allclose(again["own_women"].mu, first["own_women"].mu * women[0], rtol=1e-9)
        self.assertFalse(np.array_equal(first["g_own"], again["g_own"]))
        return first

    def test_moving_every_number_a_paper_prints_leaves_its_rules_tables_and_g_as_they_were(self):
        scored = [c["paper"] for c in self.cover if c["scored"]]
        self.assertGreaterEqual(len(scored), 15)
        for paper in scored:
            with self.subTest(paper=paper):
                tables = SN.held_out_tables(self.cells, self.with_sexes, self.contrasts, paper, self.voc)
                # a means-only stratum's difference must stay inside the pool's SD, so its means move little
                small = tables["synthetic_persons"]
                self.assert_rules_unmoved(paper, SMALL_MEN if small else MEN, SMALL_WOMEN if small else WOMEN)

    def test_bach_2019s_persons_are_his_whole_cohort_by_sex(self):
        first = self.assert_rules_unmoved("bach2019")
        self.assertEqual(first["keys"], ["disc_h_ant", "disc_h_mid", "disc_h_post", "foramen_h"])
        bach = [c for c in self.contrasts if c.paper == "bach2019"]
        self.assertTrue(bach and all(c.group == "" and c.sds_printed for c in bach))
        # his 109 men and 131 women as series.py reads them, the people the selection's Bach population pools
        self.assertEqual(first["counts"], {"male": 109.0, "female": 131.0})
        np.testing.assert_allclose(first["own"].mu, (first["own_men"].mu + first["own_women"].mu) / 2.0)
        self.assertTrue(np.all(first["own_men"].mu[0] > first["own_women"].mu[0]))
        self.assertFalse(first["synthetic_persons"])

    def test_chaudhary_2015s_persons_are_drawn_with_each_sexs_own_sd(self):
        t = SN.held_out_tables(self.cells, self.with_sexes, self.contrasts, "chaudhary2015", self.voc)
        self.assertEqual(t["keys"], ["interpedicular"])
        np.testing.assert_array_equal(t["own_men"].sd[0], [2.2, 2.2, 2.4, 3.9, 5.9])
        np.testing.assert_array_equal(t["own_women"].sd[0], [3.4, 2.4, 2.5, 2.4, 3.4])
        self.assertEqual((t["sd_from"], t["synthetic_persons"]), ([CV.PRINTED_SD], False))

    def test_a_means_only_paper_is_flagged_and_its_g_is_the_other_papers(self):
        first = self.assert_rules_unmoved("eisenstein1977", SMALL_MEN, SMALL_WOMEN)
        self.assertTrue(first["synthetic_persons"])
        self.assertEqual(first["persons_sd"], SN.PERSONS_BORROWED)
        # its mid-body depth is moved by the other papers' g, cell by cell
        j = first["keys"].index("body_d_mid")
        self.assertTrue(all(s == "cell" for s in first["scope"][j]) and first["g"][j].min() > 0)

    def test_bach_2019s_inner_temperature_is_select_pys_own(self):
        keys = ST.paper_measures(self.cells, "bach2019", self.voc)
        choice = SN.inner_temperatures(self.cells, "bach2019", keys, self.voc, (1, 2, 3), GENERATOR, SEL.INNER_COLUMNS,
                                       SN.streams(SN.SEED_HELD_OUT, 1)[0]["inner"])
        self.assertEqual(choice["seed_from"], "select.py's")
        self.assertEqual(choice["t_from"], SN.INNER_CHOICE)
        self.assertEqual(choice["t"], {1: 1.4, 2: 1.4, 3: 1.4})

    def test_a_paper_with_no_inner_fold_is_named_a_fallback(self):
        choice = SN.inner_temperatures(self.cells, "amonookuofi1985", ["body_d_mid"], self.voc, (1, 2, 3), GENERATOR,
                                       SEL.INNER_COLUMNS, SN.streams(SN.SEED_HELD_OUT, 1)[0]["inner"])
        self.assertEqual((choice["inner_folds"], choice["t_from"]), (0, SN.FALLBACK_T))
        self.assertEqual(choice["t"], {1: 1.0, 2: 1.0, 3: 1.0})

    def test_only_the_papers_printing_both_sexes_are_read_and_each_says_why_not(self):
        self.assertEqual([c["paper"] for c in self.cover], sorted({c.paper for c in self.contrasts}))
        for c in self.cover:
            self.assertEqual(c["scored"], not c["why_not"])
        population = {c["paper"]: c["population"] for c in self.cover if c["scored"]}
        self.assertEqual(population["bach2019"], SN.SELECTION_POPULATION)
        self.assertEqual(population["chaudhary2015"], SN.SELECTION_POPULATION)
        self.assertEqual(population["masharawi2021"], SN.SELECTION_POPULATION)
        self.assertEqual(population["eisenstein1977"], SN.APART_ONLY)
        self.assertEqual(population["abbas2021"], SN.PARTLY)


class Pooled(unittest.TestCase):
    def rows(self):
        out = []
        for paper, d, se, synthetic in (("a", 0.10, 0.01, False), ("b", 0.02, 0.01, False), ("c", 0.06, 0.02, False),
                                        ("z", 0.50, 0.01, True)):
            row = {"paper": paper, "width": 1, "rule": SN.B_IN, "against": SN.A_IN, "fields": 10, "synthetic_persons": synthetic,
                   "population": SN.SELECTION_POPULATION}
            for m in ("exact", "log_score", "answered", "precision", "ece"):
                row[m], row["d_" + m], row["d_%s_se" % m] = 0.5, d, se
            out.append(row)
        return out

    def test_the_headline_se_is_between_populations_and_both_are_recorded(self):
        rows = self.rows()[:3]
        got, = SN.summarise(rows, ("width", "rule", "against"), "held out")
        ds = [r["d_log_score"] for r in rows]
        self.assertAlmostEqual(got["d_log_score_se"], float(np.std(ds, ddof=1) / math.sqrt(3)), places=12)
        self.assertAlmostEqual(got["d_log_score_se_between"], got["d_log_score_se"], places=15)
        self.assertAlmostEqual(got["d_log_score_se_persons"], math.sqrt(0.01 ** 2 + 0.01 ** 2 + 0.02 ** 2) / 3, places=12)
        self.assertEqual(got["se_of_headline"], SN.SE_BETWEEN)
        one, = SN.summarise(rows[:1], ("width", "rule", "against"), "held out")
        self.assertEqual((one["d_log_score_se"], one["se_of_headline"]), (0.01, SN.SE_PERSONS))

    def test_the_headline_leaves_out_the_papers_whose_persons_sd_is_borrowed(self):
        import run_sex_naming as RUN
        got = {r["paper"]: r for r in RUN.held_out_summary(self.rows())}
        self.assertEqual(got[RUN.HEADLINE]["populations"], 3)
        self.assertAlmostEqual(got[RUN.HEADLINE]["d_log_score"], 0.06, places=12)
        self.assertEqual(got[RUN.EVERY_PAPER]["populations"], 4)
        self.assertEqual(got[RUN.SELECTION]["populations"], 3)


if __name__ == "__main__":
    unittest.main()
