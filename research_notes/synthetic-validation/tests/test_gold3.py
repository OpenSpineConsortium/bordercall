"""Gold tier 3 on the bounds card, held to what synthval/gold3.py says of it.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests -p test_gold3.py   # from the root

- the report's data lines parse into each sex's moments, a disc's level is its upper vertebra's,
  the range line keeps its name, prose is passed over and a data line of the wrong shape raises;
- the sexes pooled from their moments are the moments of the two samples put together, and so is
  the covariance of two levels from the within-sex correlations and the sexes' shift, so a step's
  sampling variance is the paired difference's;
- the age slope over each sex's SD is pooled by inverse variance;
- on a toy card, a cohort at the card's centre passes the mean, SD and step tests and one moved far
  off fails them, the sex sign is tested only where the card's contrast clears zero, a cell with
  fewer people than reference_n is left out and counted, and a cell the engine does not measure is
  never scored;
- a film cell is never scored against a CT cohort, nor a step read inside film papers alone, a
  cell whose one sex's mean the report withholds is counted apart, and what the report holds that
  is not scored is named with why;
- the written records are what the module makes from the committed report and card, and the report
  is the one gold3.json names by its digest.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(NOTE))
sys.path[:0] = [REPO, NOTE]

from synthval import bounds as B  # noqa: E402
from synthval import gold3 as G3  # noqa: E402

RECORDS = os.path.join(NOTE, "records", "gold3")
CARD = os.path.join(NOTE, "records", "bounds")


def line(member, key, level, men, women, g="0.500", var_g="0.00500", r=("-", "-", "-", "-"), a=("-",) * 6):
    return " ".join(["-", member, key, level, "M", str(men[0]), str(men[1]), str(men[2]), "F", str(women[0]),
                     str(women[1]), str(women[2]), "g", g, var_g, "r", *r, "a", *a])


def moments_of(x_m, x_f, r_m=float("nan"), r_f=float("nan"), level="L1"):
    return G3.Moments(level, len(x_m), x_m.mean(), x_m.std(ddof=1), len(x_f), x_f.mean(), x_f.std(ddof=1),
                      0.5, 0.005, r_m, r_f, float("nan"), float("nan"), float("nan"), float("nan"))


class ParseTest(unittest.TestCase):
    def test_lines_parse_and_discs_take_the_upper_level(self):
        text = "\n".join([
            "# morphometry covariates: a heading",
            "- fill autopet: persons 3; sex 3",
            line("autopet", "h_ant", "L1", (478, 28.97, 2.366), (376, 28.21, 2.453), r=("0.440", "478", "0.471", "375"),
                 a=("-0.1750", "0.07013", "478", "-0.1627", "0.08027", "376")),
            line("totalseg", "disc_h_ant", "L4-L5", (80, 6.7, 3.8), (70, 4.8, 5.0)),
            line("totalseg", "disc_h_ant", "T10-L5", (80, 5.3, 1.3), (70, 4.2, 1.2)),
            "- member autopet: persons 857, lines 271"])
        got = G3.parse(text)
        self.assertEqual(set(got), {("autopet", "h_ant", "L1"), ("totalseg", "disc_h_ant", "L4"),
                                    ("totalseg", "disc_h_ant", "T10-L5")})
        m = got["autopet", "h_ant", "L1"]
        self.assertEqual((m.n_m, m.mean_m, m.sd_m, m.n_f, m.r_m, m.r_f), (478, 28.97, 2.366, 376, 0.440, 0.471))
        self.assertEqual((m.slope_m, m.slope_se_f), (-0.1750, 0.08027))
        self.assertEqual(got["totalseg", "disc_h_ant", "L4"].level_printed, "L4-L5")
        self.assertTrue(math.isnan(got["totalseg", "disc_h_ant", "L4"].r_m))

    def test_a_data_line_of_the_wrong_shape_raises(self):
        with self.assertRaises(ValueError):
            G3.parse("- autopet h_ant L1 M 478 28.97 2.366 F 376 28.21")


class MomentsTest(unittest.TestCase):
    def test_pooled_is_the_two_samples_together(self):
        rng = np.random.default_rng(1)
        x_m, x_f = rng.normal(30.0, 2.5, 140), rng.normal(27.0, 2.0, 95)
        n, mean, sd = G3.pooled(moments_of(x_m, x_f))
        both = np.concatenate([x_m, x_f])
        self.assertEqual(n, len(both))
        self.assertAlmostEqual(mean, both.mean(), places=10)
        self.assertAlmostEqual(sd, both.std(ddof=1), places=10)

    def test_the_covariance_and_the_step_variance_are_the_paired_ones(self):
        rng = np.random.default_rng(2)

        def sex(n, mu_u, mu_l, rho):
            z = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], n)
            return mu_u + 2.0 * z[:, 0], mu_l + 2.5 * z[:, 1]
        um, lm = sex(150, 28.0, 30.0, 0.6)
        uf, lf = sex(110, 26.0, 27.5, 0.4)
        upper = moments_of(um, uf)
        lower = moments_of(lm, lf, np.corrcoef(um, lm)[0, 1], np.corrcoef(uf, lf)[0, 1])
        u, lo = np.concatenate([um, uf]), np.concatenate([lm, lf])
        self.assertAlmostEqual(G3.pooled_cov(upper, lower), np.cov(u, lo, ddof=1)[0, 1], places=9)
        self.assertAlmostEqual(G3.step_variance(upper, lower, 40.0), (lo - u).var(ddof=1) / 40.0, places=9)

    def test_an_unprinted_correlation_reads_as_unpaired(self):
        rng = np.random.default_rng(3)
        upper = moments_of(rng.normal(28, 2, 50), rng.normal(26, 2, 40))
        lower = moments_of(rng.normal(30, 2, 50), rng.normal(27, 2, 40))
        sd_u, sd_l = G3.pooled(upper)[2], G3.pooled(lower)[2]
        self.assertAlmostEqual(G3.step_variance(upper, lower, 40.0), (sd_u ** 2 + sd_l ** 2) / 40.0, places=12)

    def test_the_age_slope_is_pooled_by_inverse_variance(self):
        m = G3.Moments("L1", 100, 30.0, 2.0, 100, 28.0, 4.0, 0.5, 0.005, 0.5, 0.5, -0.4, 0.1, -0.4, 0.2)
        s, e = G3.age_slope(m)
        w_m, w_f = 1 / 0.05 ** 2, 1 / 0.05 ** 2
        self.assertAlmostEqual(s, (w_m * -0.2 + w_f * -0.1) / (w_m + w_f))
        self.assertAlmostEqual(e, 1 / math.sqrt(w_m + w_f))


def toy_card() -> B.Card:
    """Two measures at two levels and one step each; h_ant's contrast clears zero, canal_ap's does not."""
    def cell(measure, level, mean, sex_g, sex_low, sex_high, modality="bone and CT", papers="tan2004"):
        return {"kind": B.ALL, "measure": measure, "level": level, "modality": modality, "strata_list": papers, "mean": mean,
                "between": 1.0, "mean_low": mean - 1.96, "mean_high": mean + 1.96, "sd_log_centre": math.log(2.0),
                "sd_log_between": 0.1, "sd_low": 1.6, "sd_high": 2.4, "sex_g": sex_g, "sex_g_between": 0.2,
                "sex_g_new_low": sex_low, "sex_g_new_high": sex_high, "sex_g_papers": 2, "age_slope": float("nan")}
    cells = [cell("h_ant", "L1", 28.0, 1.0, 0.6, 1.4), cell("h_ant", "L2", 30.0, 1.0, 0.6, 1.4),
             cell("canal_ap", "L1", 15.0, 0.0, -0.4, 0.4), cell("canal_ap", "L2", 15.0, 0.0, -0.4, 0.4),
             cell("facet_angle_axial", "L1", 40.0, 0.0, -0.4, 0.4),
             cell("interpedicular", "L1", 22.0, 0.0, -0.4, 0.4, "film", "hinck1966"),
             cell("interpedicular", "L2", 22.0, 0.0, -0.4, 0.4, "film", "hinck1966")]
    steps = [{"kind": B.ALL, "measure": m, "upper": "L1", "lower": "L2", "step": s, "between": 0.3, "papers": p,
              "step_low": s - 0.6, "step_high": s + 0.6}
             for m, s, p in (("h_ant", 2.0, "tan2004"), ("canal_ap", 0.0, "tan2004"), ("interpedicular", 0.0, "hinck1966"))]
    return B.Card(cells=cells, steps=steps)


def toy_moments(shift: float = 0.0, n=(200, 150)) -> dict:
    def m(mean, level, r=0.5):
        return G3.Moments(level, n[0], mean + 0.5 + shift, 2.0, n[1], mean - 0.5 + shift, 2.0, 0.5, 0.0005,
                          r, r, float("nan"), float("nan"), float("nan"), float("nan"))
    return {("autopet", "h_ant", "L1"): m(28.0, "L1"), ("autopet", "h_ant", "L2"): m(30.0, "L2"),
            ("autopet", "canal_ap", "L1"): m(15.0, "L1"), ("autopet", "canal_ap", "L2"): m(15.0, "L2"),
            ("autopet", "facet_angle_axial", "L1"): m(40.0, "L1"),
            ("autopet", "interpedicular", "L1"): m(20.0, "L1"), ("autopet", "interpedicular", "L2"): m(20.0, "L2")}


class ScoreTest(unittest.TestCase):
    def test_a_cohort_at_the_centre_passes_and_one_far_off_fails(self):
        at = G3.score(toy_moments(), toy_card(), "autopet")
        self.assertEqual({r["measure"] for r in at["cells"]}, {"h_ant", "canal_ap"})
        self.assertTrue(all(r["mean_pass"] and r["sd_pass"] for r in at["cells"]))
        self.assertTrue(all(s["step_pass"] for s in at["steps"]))
        off = G3.score(toy_moments(shift=5.0), toy_card(), "autopet")
        self.assertFalse(any(r["mean_pass"] for r in off["cells"]))
        self.assertTrue(all(s["step_pass"] for s in off["steps"]))

    def test_the_sex_sign_is_tested_only_where_the_contrast_clears_zero(self):
        got = G3.score(toy_moments(), toy_card(), "autopet")
        tested = {r["measure"] for r in got["cells"] if "sex_pass" in r}
        inside = {r["measure"] for r in got["cells"] if "sex_inside" in r}
        self.assertEqual(tested, {"h_ant"})
        self.assertEqual(inside, {"h_ant", "canal_ap"})
        self.assertEqual(got["summary"]["tests"]["sex"]["made"], 2)

    def test_film_is_left_out_and_what_is_not_scored_is_named(self):
        moments = toy_moments()
        moments["autopet", "wedge", "L1"] = moments["autopet", "h_ant", "L1"]
        moments["autopet", "spinous_length", "L1"] = moments["autopet", "h_ant", "L1"]
        got = G3.score(moments, toy_card(), "autopet")
        self.assertNotIn("interpedicular", {r["measure"] for r in got["cells"]} | {s["measure"] for s in got["steps"]})
        self.assertEqual({s["measure"] for s in got["steps"]}, {"h_ant", "canal_ap"})
        left = got["summary"]["not_scored"]
        self.assertEqual(left["keys_not_on_card"], ["facet_angle_axial", "wedge"])
        self.assertEqual(set(left["definition_differs"]), {"spinous_length"})
        self.assertEqual(left["cells_not_ct"], [{"measure": "interpedicular", "modality": "film", "levels": ["L1", "L2"]}])

    def test_a_withheld_mean_is_counted_apart_and_named(self):
        moments = toy_moments()
        m = moments["autopet", "h_ant", "L2"]
        moments["autopet", "h_ant", "L2"] = G3.Moments(m.level_printed, m.n_m, float("nan"), float("nan"), m.n_f,
                                                       m.mean_f, m.sd_f, *[float("nan")] * 8)
        got = G3.score(moments, toy_card(), "autopet")
        self.assertEqual(got["summary"]["withheld_cells"], 1)
        self.assertEqual(got["summary"]["short_cells"], 0)
        self.assertEqual(got["summary"]["not_scored"]["withheld_cells"], ["h_ant L2"])
        self.assertNotIn("h_ant", {s["measure"] for s in got["steps"]})

    def test_a_cell_short_of_reference_n_is_left_out_and_counted(self):
        got = G3.score(toy_moments(n=(20, 15)), toy_card(), "autopet")
        self.assertEqual(got["cells"], [])
        self.assertEqual(got["steps"], [])
        self.assertEqual(got["summary"]["short_cells"], 4)
        self.assertEqual(got["summary"]["withheld_cells"], 0)


class RecordsTest(unittest.TestCase):
    def test_the_records_are_what_the_report_and_the_card_make(self):
        if not os.path.exists(os.path.join(RECORDS, "gold3.json")):
            self.skipTest("records/gold3 not written")
        with open(os.path.join(RECORDS, "gold3.json"), encoding="utf-8") as fh:
            rec = json.load(fh)
        path = os.path.join(RECORDS, "report.txt")
        with open(path, "rb") as fh:
            self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), rec["report_sha256"])
        with open(path, encoding="ascii") as fh:
            moments = G3.parse(fh.read())
        card = B.load(CARD)
        for member in G3.MEMBERS:
            got = G3.score(moments, card, member)
            self.assertEqual(got["summary"]["tests"], rec["members"][member]["summary"]["tests"])
            self.assertEqual(G3.covariate_record(got["cells"], "sex")["inside"], rec["members"][member]["sex"]["inside"])
        with open(os.path.join(RECORDS, "steps.csv"), encoding="utf-8", newline="") as fh:
            steps = list(csv.DictReader(fh))
        for member in G3.MEMBERS:
            made = rec["members"][member]["summary"]["tests"]["step"]
            mine = [s for s in steps if s["member"] == member]
            self.assertEqual((len(mine), sum(s["step_pass"] == "True" for s in mine)), (made["made"], made["passed"]))


if __name__ == "__main__":
    unittest.main()
