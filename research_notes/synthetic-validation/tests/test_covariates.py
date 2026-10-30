"""Covariates both ways, held to what synthval/covariates.py's docstrings say.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- a contrast is read only where a paper prints both sexes of one stratum, with an SD and a count of
  its own, from its own people; g is Hedges' and its sign is men minus women;
- the bands are read as written, open bands span OPEN_SPAN, ordinal decades are the decade of life,
  and a child's band never enters an age gradient;
- a gradient's slope is in within-band SDs per unit and recovers a known line;
- a paper's strata at one cell combine by inverse variance, and its cells of one measure count as
  one paper;
- the effect for a held-out paper never reads that paper;
- the classifier given the population's own g reaches the population's own AUC, a reversed g
  gives one minus it, the log loss sits between the ceiling and ln 2, and R^2 out of sample is the
  own split's when the transferred effect is the own one;
- the whole cohort by sex stands for its strata (rule 5), a pair restated with the same means and
  counts is one, and a sex of fewer than MIN_PER_SEX gives no contrast, each drop recorded;
- on the snapshot: the sexes' snapshot pools back to the full snapshot's rows, every paper printing
  the sexes apart with SDs enters, Chaudhary 2015 reads each sex's own SD and is scored, Mitra
  2002's two women are dropped by the count rule, and every recorded g is made again from its row.
"""
from __future__ import annotations

import csv
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
from synthval import papers_table as PT  # noqa: E402

VOC = {"disc": {"kind": "length"}, "ratio": {"kind": "ratio"}}


def row(paper, sex, mean, sd=2.0, n=50.0, key="disc", level="L4", group="", source="this paper", species=""):
    return {"paper": paper, "cohort": "c", "technique": "ct", "key": key, "base_key": key, "level": level, "sex": sex,
            "group": group, "side": "", "definition": "d", "modality": "ct", "mean": float(mean), "sd": float(sd), "n": float(n),
            "source_of_values": source, "species": species}


class Covariates(unittest.TestCase):
    def test_a_contrast_needs_both_sexes_of_one_stratum_from_the_papers_own_people(self):
        rows = [row("a", "male", 12.0), row("a", "female", 10.0), row("b", "male", 12.0), row("b", "female", 10.0, source="Hou et al"),
                row("c", "male", 12.0, sd=float("nan")), row("c", "female", 10.0), row("d", "male", 12.0, key="ratio"),
                row("d", "female", 10.0, key="ratio"), row("e", "male", 12.0, species="pig"), row("e", "female", 10.0, species="pig"),
                row("f", "male", 12.0, group="25% largest"), row("f", "female", 10.0, group="25% largest")]
        got = CV.sex_contrasts(rows, VOC)
        self.assertEqual([c.paper for c in got], ["a"])
        c = got[0]
        j = 1.0 - 3.0 / (4.0 * 100 - 9.0)
        self.assertAlmostEqual(c.g, j * 1.0)
        self.assertGreater(c.g, 0)
        self.assertAlmostEqual(c.var_g, 100 / 2500 + c.g ** 2 / 200)

    def test_bands_are_read_as_written_and_children_stay_out(self):
        self.assertEqual(CV.age_band("decade 20"), (20.0, 29.0))
        self.assertEqual(CV.age_band("Third Decade"), (20.0, 29.0))
        self.assertEqual(CV.age_band("18-35"), (18.0, 35.0))
        self.assertEqual(CV.age_band("21-40 years"), (21.0, 40.0))
        self.assertEqual(CV.age_band("age 31-49 yr"), (31.0, 49.0))
        self.assertEqual(CV.age_band(">55"), (55.0, 55.0 + CV.OPEN_SPAN))
        self.assertEqual(CV.age_band("60+"), (60.0, 60.0 + CV.OPEN_SPAN))
        self.assertEqual(CV.age_band("age >=70 yr"), (70.0, 70.0 + CV.OPEN_SPAN))
        self.assertEqual(CV.age_band("age <=30 yr"), (CV.ADULT, 30.0))
        self.assertIsNone(CV.age_band("Part 1 cadavers, direct"))
        self.assertEqual(CV.size_band("body height 1601-1699 mm", "height"), (1601.0, 1699.0))
        self.assertEqual(CV.size_band("body weight <=45 kg", "weight"), (36.0, 45.0))
        self.assertIsNone(CV.size_band("body height 1601-1699 mm", "weight"))
        rows = [row("a", "all", 10.0, group="0-1.5"), row("a", "all", 11.0, group="1.5-12"), row("a", "all", 12.0, group="13-17")]
        self.assertEqual(CV.gradients(rows, VOC, "age"), [])

    def test_a_slope_is_in_within_band_sds_per_unit(self):
        rows = [row("a", "all", 20.0 - 0.5 * i, sd=2.0, group="decade %d" % (20 + 10 * i)) for i in range(5)]
        gr, = CV.gradients(rows, VOC, "age")
        b, v = gr.slope()
        self.assertAlmostEqual(b, -0.5 / 2.0)
        self.assertGreater(v, 0)
        np.testing.assert_allclose(gr.x, [24.5, 34.5, 44.5, 54.5, 64.5])

    def test_strata_combine_by_inverse_variance_and_cells_count_as_one_paper(self):
        rows = []
        for lv in ("L3", "L4"):
            # two bands of different people with the same g: the second's numbers doubled, so that
            # neither reads as the other printed again
            for g, scale in (("decade 20", 1.0), ("decade 50", 2.0)):
                rows += [row("a", "male", 12.0 * scale, sd=2.0 * scale, level=lv, group=g),
                         row("a", "female", 10.0 * scale, sd=2.0 * scale, level=lv, group=g)]
        rows += [row("b", "male", 13.0), row("b", "female", 10.0)]
        cs = CV.sex_contrasts(rows, VOC)
        cells = CV.by_paper_cell(cs)
        self.assertEqual(cells["a", "disc", "L4"][2], 2)
        one = next(c for c in cs if c.paper == "a")
        self.assertAlmostEqual(cells["a", "disc", "L4"][1], one.var_g / 2.0)
        values = CV.paper_values(cells, "disc")
        self.assertEqual(sorted(values), ["a", "b"])
        self.assertAlmostEqual(values["a"][1], one.var_g / 2.0)
        eff, = CV.effects(cs, "sex")
        self.assertEqual(eff["papers"], 2)
        self.assertEqual(eff["cells"], 3)
        self.assertEqual(eff["strata"], 5)

    def test_the_held_out_effect_never_reads_the_held_out_paper(self):
        rows = [row("a", "male", 12.0), row("a", "female", 10.0), row("b", "male", 14.0), row("b", "female", 10.0),
                row("c", "male", 10.0, level="L1"), row("c", "female", 10.0, level="L1")]
        cs = CV.sex_contrasts(rows, VOC)
        cells = CV.by_paper_cell(cs)
        g_b = next(c.g for c in cs if c.paper == "b")
        g, scope = CV.transfer(cells, "a", "disc", "L4")
        self.assertAlmostEqual(g, g_b, places=12)
        self.assertEqual(scope, "cell")
        g, scope = CV.transfer(cells, "c", "disc", "L1")
        self.assertEqual(scope, "measure")
        only = CV.sex_contrasts([row("z", "male", 12.0), row("z", "female", 10.0)], VOC)
        self.assertEqual(CV.held_out(only, "sex"), [])

    def test_the_classifier_reaches_the_populations_own_split_with_its_own_effect(self):
        c = CV.Contrast("a", "c", "disc", "L4", "", 12.0, 2.0, 200.0, 10.0, 2.0, 200.0)
        own = CV.sex_prediction(c, c.g / (1.0 - 3.0 / (4.0 * 400 - 9.0)))
        self.assertAlmostEqual(own["auc_transfer"], CV.binormal_auc(12.0, 2.0, 10.0, 2.0))
        self.assertAlmostEqual(own["auc_transfer"], own["auc_own"])
        self.assertAlmostEqual(own["r2_transfer"], own["r2_own"], places=6)
        self.assertAlmostEqual(own["log_loss_transfer"], own["log_loss_own"], places=6)
        self.assertLess(own["log_loss_own"], math.log(2.0))
        flipped = CV.sex_prediction(c, -c.g)
        self.assertAlmostEqual(flipped["auc_transfer"], 1.0 - own["auc_own"])
        self.assertGreater(flipped["log_loss_transfer"], math.log(2.0))
        self.assertLess(flipped["r2_transfer"], 0.0)
        none = CV.sex_prediction(c, 0.0)
        self.assertAlmostEqual(none["log_loss_transfer"], math.log(2.0), places=9)
        self.assertAlmostEqual(none["r2_transfer"], 0.0, places=12)

    def test_the_whole_cohort_by_sex_stands_for_its_strata_and_a_restated_pair_is_one(self):
        rows = [row("a", "male", 12.0), row("a", "female", 10.0),
                row("a", "male", 11.0, group="decade 20"), row("a", "female", 9.0, group="decade 20"),
                row("b", "male", 12.0, group="Zulu", n=40.0), row("b", "female", 10.0, group="Zulu", n=20.0),
                row("b", "male", 12.0, group="Sotho", n=30.0), row("b", "female", 10.0, group="Sotho", n=15.0),
                row("c", "male", 12.0, group="table I"), row("c", "female", 10.0, group="table I"),
                row("c", "male", 12.0, group="table II"), row("c", "female", 10.0, group="table II")]
        got, dropped = CV.sex_strata(rows, VOC)
        self.assertEqual(sorted((c.paper, c.group) for c in got), [("a", ""), ("b", "Sotho"), ("b", "Zulu"), ("c", "table I")])
        why = {(d["paper"], d["group"]): d["why"] for d in dropped}
        self.assertEqual(why, {("a", "decade 20"): CV.STRATUM_OF_WHOLE, ("c", "table II"): CV.PRINTED_TWICE})

    def test_a_sex_of_fewer_than_five_gives_no_contrast_and_is_recorded(self):
        rows = [row("a", "male", 12.0, n=18.0), row("a", "female", 10.0, n=4.0),
                row("b", "male", 12.0, n=18.0), row("b", "female", 10.0, n=5.0)]
        got, dropped = CV.sex_strata(rows, VOC)
        self.assertEqual([c.paper for c in got], ["b"])
        self.assertEqual([(d["paper"], d["n_female"], d["why"]) for d in dropped], [("a", 4.0, CV.FEW_PER_SEX)])


class OnTheSnapshot(unittest.TestCase):
    """The sexes the reread's series.py pooled away, read beside the full snapshot."""

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.voc = PT.load_rows_all(), PT.load_vocabulary()
        cls.apart = PT.load_rows_sexes()
        cls.contrasts, cls.dropped = CV.sex_strata(cls.rows + cls.apart, cls.voc)

    def test_the_sexes_snapshot_pools_back_to_the_full_snapshots_rows(self):
        self.assertEqual(PT.check_snapshot_sexes(), [])
        self.assertTrue(all(r["sex"] in ("male", "female") and r["apart"] in (PT.POOLED_AWAY, PT.BESIDE_WHOLE) for r in self.apart))
        self.assertFalse(any(r.get("apart") for r in self.rows))

    def test_every_paper_printing_the_sexes_apart_with_sds_enters(self):
        papers = {c.paper for c in self.contrasts if c.sds_printed}
        for paper in ("masharawi2021", "amonookuofi1982", "yadav2020", "abbas2021", "olsewski1990", "ahmed2019", "alonge2021",
                      "amonookuofi1985", "cizmic2023", "griffith2016", "tang2016", "yu2015", "bach2019", "chaudhary2015"):
            self.assertIn(paper, papers)
        foramen = [c for c in self.contrasts if c.paper == "masharawi2021" and c.base_key == "foramen_h"]
        self.assertEqual(len(foramen), 5)
        self.assertTrue(all(c.sds_printed for c in foramen))

    def test_chaudhary_2015_reads_each_sexs_own_sd_and_is_scored(self):
        mine = sorted((c for c in self.contrasts if c.paper == "chaudhary2015"), key=lambda c: c.level)
        self.assertEqual([c.level for c in mine], ["L1", "L2", "L3", "L4", "L5"])
        self.assertTrue(all(c.sd_from == CV.PRINTED_SD and c.group == "" for c in mine))
        self.assertEqual((mine[0].sd_m, mine[0].sd_f, mine[0].n_m, mine[0].n_f), (2.2, 3.4, 150.0, 150.0))
        held = CV.held_out(self.contrasts, "sex")
        self.assertEqual(sorted(r["level"] for r in held if r["paper"] == "chaudhary2015"), ["L1", "L2", "L3", "L4", "L5"])
        # its Table II, the same means without SDs under the district's name, is its whole's again
        self.assertEqual({d["why"] for d in self.dropped if d["paper"] == "chaudhary2015"}, {CV.STRATUM_OF_WHOLE})

    def test_mitra_2002s_two_women_are_dropped_by_the_count_rule(self):
        self.assertFalse([c for c in self.contrasts if c.paper == "mitra2002"])
        few = [d for d in self.dropped if d["paper"] == "mitra2002" and d["why"] == CV.FEW_PER_SEX]
        self.assertTrue(few and all(d["n_female"] == 2.0 for d in few))

    def test_every_recorded_g_is_made_again_from_its_row(self):
        with open(os.path.join(NOTE, "records", "covariates", "contrasts.csv"), encoding="utf-8") as fh:
            recorded = list(csv.DictReader(fh))
        self.assertEqual(len(recorded), len(self.contrasts))
        for r in recorded:
            n_m, n_f, sd = float(r["n_male"]), float(r["n_female"]), float(r["sd_within"])
            if r["sd_from"] == CV.PRINTED_SD:
                s_m, s_f = float(r["sd_male"]), float(r["sd_female"])
                self.assertAlmostEqual(sd, math.sqrt(((n_m - 1) * s_m ** 2 + (n_f - 1) * s_f ** 2) / (n_m + n_f - 2)), places=9)
            j = 1.0 - 3.0 / (4.0 * (n_m + n_f) - 9.0)
            g = j * (float(r["mean_male"]) - float(r["mean_female"])) / sd
            self.assertTrue(math.isclose(g, float(r["g"]), rel_tol=1e-9, abs_tol=1e-12), r)
            self.assertTrue(r["count_from"] is not None and r["sd_from"])


if __name__ == "__main__":
    unittest.main()
