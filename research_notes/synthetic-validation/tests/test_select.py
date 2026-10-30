"""Choosing the rule by held-out prediction, held to what synthval/select.py's docstrings say.

    python3 -m unittest discover -s research_notes/synthetic-validation/tests    # from the repository's root

- the log evidence gives strata.posterior's posterior at temperature 1, and a temperature above 1
  flattens it without moving the top;
- a mixture of one component is that component, and a mixture holds the true table's evidence no
  lower than the mean of its components' (Jensen);
- the calibration error is zero when every bin's accuracy is its confidence and the bins sum to
  the fields;
- a scaled table multiplies the SD alone, a component puts in the other paper's own cells alone, and
  a paper printing none of the keys has no component;
- dropping a paper takes its stratum out of every cell where strata.without keeps it, and the
  inner choice, which reads the dropped cells, never sees the held-out paper, picks from the grids,
  and on a toy pool whose populations spread wider than the within SD picks a factor above 1;
- the candidates are scored on the same fields, the own table loses nothing to itself, and the
  tempered candidate names exactly what plain names;
- leaving a paper out pools the cells over the rest, changes nothing on the fold that holds that
  paper out, and keeps plain's value where no third paper prints a cell, counted; one vote per
  population takes the geometric mean of the others' own SDs and keeps plain's means; each base's
  temperature is chosen on its own rule;
- summarise gives each population equal weight, the winner is the best mean log score, and the
  difference from plain is paired.
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
from synthval import select as SEL  # noqa: E402
from synthval import strata as ST  # noqa: E402
from synthval.population import GENERATOR, draw_table  # noqa: E402

LUMBAR = list(ST.LUMBAR)
VOC = {"canal_ap": {"kind": "length"}, "h_ant": {"kind": "length"}}


def series(paper, key, level, mean, sd=2.0, n=30.0, cohort="c"):
    return L.Series(paper=paper, cohort=cohort, technique="ct", modality="ct", group="", sex="all", key=key, level=level,
                    mean=mean, sd=sd, n=n, vs_panjabi="same", sd_uncertain=False)


def papers(shifts, keys=("canal_ap", "h_ant"), sd=2.0):
    """Papers printing two measures at every lumbar level, each paper's means moved from a base by
    its own shift in SDs."""
    base = {"canal_ap": 17.0, "h_ant": 26.0}
    out = []
    for p, s in shifts.items():
        for key in keys:
            for i, lv in enumerate(LUMBAR):
                out.append(series(p, key, lv, base[key] + 0.5 * i + sd * s, sd=sd))
    return out


class Select(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells = ST.strata_of(papers({"a": 0.0, "b": 1.2, "c": -1.2, "d": 2.0, "e": -2.0}))
        ST.set_between(cls.cells)
        cls.keys = ["canal_ap", "h_ant"]
        cls.own, _ = ST.paper_table(cls.cells, "a", cls.keys, VOC)
        cls.pop = draw_table(cls.own, GENERATOR, 30, 7)

    def test_the_log_evidence_gives_the_posterior_and_a_temperature_flattens_it(self):
        logev, truth, group = SEL.log_evidence(self.pop, self.own, 2, GENERATOR)
        call, top, truth2, group2 = ST.posterior(self.pop, self.own, 2, GENERATOR)
        post = SEL.tempered(logev, 1.0)
        np.testing.assert_array_equal(truth, truth2)
        np.testing.assert_array_equal(post.argmax(1), call)
        np.testing.assert_allclose(post.max(1), top, rtol=1e-10)
        flat = SEL.tempered(logev, 4.0)
        np.testing.assert_array_equal(flat.argmax(1), call)
        self.assertLess(flat.max(1).mean(), top.mean())
        np.testing.assert_allclose(flat.sum(1), 1.0)

    def test_a_mixture_of_one_is_itself_and_of_many_is_no_lower_than_their_mean_at_the_truth(self):
        a = SEL.log_evidence(self.pop, self.own, 1, GENERATOR)[0]
        b_table, _ = ST.paper_table(self.cells, "d", self.keys, VOC)
        b = SEL.log_evidence(self.pop, b_table, 1, GENERATOR)[0]
        np.testing.assert_allclose(SEL.mixture_evidence([a]), a)
        mix = SEL.mixture_evidence([a, b])
        self.assertTrue(np.all(mix >= (a + b) / 2.0 - 1e-9))
        self.assertTrue(np.all(mix <= np.maximum(a, b) + 1e-9))

    def test_the_calibration_error_is_zero_when_confidence_is_accuracy(self):
        top = np.array([0.95, 0.95, 0.95, 0.95, 0.25, 0.25, 0.25, 0.25])
        hit = np.array([1, 1, 1, 1, 1, 0, 0, 0], float)
        self.assertAlmostEqual(SEL.calibration_error(top, hit), 0.5 * 0.05 + 0.5 * 0.0, places=12)
        bins = SEL.reliability(top, hit)
        self.assertEqual(sum(b["fields"] for b in bins), 8)
        self.assertEqual([b["bin"] for b in bins], [2, 9])

    def test_a_scaled_table_multiplies_the_sd_alone(self):
        t = SEL.scaled(self.own, 1.5)
        np.testing.assert_allclose(t.sd, self.own.sd * 1.5)
        np.testing.assert_array_equal(t.mu, self.own.mu)
        self.assertEqual(t.keys, self.own.keys)

    def test_a_component_puts_in_the_other_papers_own_cells(self):
        comps = SEL.component_tables(self.cells, "a", self.keys, VOC)
        self.assertEqual(sorted(comps), ["b", "c", "d", "e"])
        plain = ST.others_table(self.cells, "a", self.keys, VOC, ST.median_f(ST.without(self.cells, "a")), False)
        d_own, _ = ST.paper_table(self.cells, "d", self.keys, VOC)
        np.testing.assert_allclose(comps["d"].mu, d_own.mu)
        self.assertFalse(np.allclose(comps["d"].mu, plain.mu))
        one = ST.strata_of(papers({"a": 0.0, "b": 1.0}) + papers({"z": 0.5}, keys=("canal_ap",)))
        comps = SEL.component_tables(one, "a", ["h_ant"], VOC)
        self.assertEqual(sorted(comps), ["b"])

    def test_dropping_a_paper_takes_its_stratum_out_and_pools_the_rest(self):
        dropped = SEL.drop_paper(self.cells, "a")
        self.assertNotIn("a", {s.paper for c in dropped for s in c.strata})
        kept = ST.without(self.cells, "a")
        self.assertIn("a", {s.paper for c in kept for s in c.strata})
        for d, k in zip(dropped, kept):
            self.assertAlmostEqual(d.pool.mean, k.pool.mean)
            self.assertEqual(d.pool.k, k.pool.k)
        one = ST.strata_of(papers({"a": 0.0, "b": 1.0}) + papers({"z": 0.5}, keys=("canal_ap",)))
        self.assertEqual(len(SEL.drop_paper(one, "z")), len(one))
        self.assertEqual(len(SEL.drop_paper(SEL.drop_paper(one, "a"), "b")), 5)

    def test_the_inner_choice_reads_the_training_papers_alone_and_picks_from_the_grids(self):
        choice = SEL.inner_choice(self.cells, "a", self.keys, VOC, (1, 2), columns=12, seed=3, k_grid=(0.7, 1.0, 1.75, 3.0), t_grid=(0.5, 1.0, 2.0))
        self.assertIn(choice["k"], (0.7, 1.0, 1.75, 3.0))
        self.assertEqual(sorted(choice["t"]), [1, 2])
        self.assertTrue(all(t in (0.5, 1.0, 2.0) for t in choice["t"].values()))
        self.assertEqual(sorted(f["paper"] for f in choice["folds"]), ["b", "c", "d", "e"])
        # populations two SDs apart spread far wider than the within SD, so the factor chosen is above 1
        self.assertGreater(choice["k"], 1.0)
        self.assertEqual(choice["k"], max(choice["k_curve"], key=lambda k: choice["k_curve"][k]))

    def test_the_candidates_share_their_fields_and_tempered_names_as_plain_does(self):
        choice = {"k": 1.75, "t": {1: 2.0, 2: 1.0}}
        rows, bins, k_rows, t_rows = SEL.score_paper(self.cells, "a", self.keys, VOC, 20, (1, 2), choice, seed=5,
                                                     k_grid=(1.0, 1.75), t_grid=(1.0, 2.0))
        self.assertEqual({r["candidate"] for r in rows}, {SEL.OWN} | set(SEL.CANDIDATES))
        self.assertEqual({r["fields"] for r in rows if r["width"] == 1}, {20 * 5})
        own = next(r for r in rows if r["candidate"] == SEL.OWN and r["width"] == 1)
        self.assertEqual(own["loss"], 0.0)
        self.assertEqual(own["regret"], 0.0)
        plain = next(r for r in rows if r["candidate"] == SEL.PLAIN and r["width"] == 1)
        temp = next(r for r in rows if r["candidate"] == SEL.TEMPERED and r["width"] == 1)
        self.assertEqual(temp["exact"], plain["exact"])
        self.assertEqual(temp["temperature"], 2.0)
        self.assertEqual(plain["log_score_vs_plain"], 0.0)
        scaled = next(r for r in rows if r["candidate"] == SEL.SCALED and r["width"] == 2)
        self.assertEqual(scaled["k"], 1.75)
        self.assertEqual(len(k_rows), 2 * 2)
        self.assertEqual(len(t_rows), 2 * 2)
        self.assertTrue(all(b["candidate"] in {SEL.OWN} | set(SEL.CANDIDATES) for b in bins))
        for cand in (SEL.OWN,) + SEL.CANDIDATES:
            self.assertEqual(sum(b["fields"] for b in bins if b["candidate"] == cand and b["width"] == 1), 100)

    def test_leaving_a_paper_out_pools_the_rest_and_keeps_plain_where_nothing_is_left(self):
        plain = ST.others_table(self.cells, "a", self.keys, VOC, ({}, float("nan")), False)
        gone, kept = SEL.without_table(self.cells, "a", self.keys, VOC, "d")
        self.assertEqual(kept, 0)
        dropped = ST.others_table(SEL.drop_paper(self.cells, "d"), "a", self.keys, VOC, ({}, float("nan")), False)
        np.testing.assert_allclose(gone.mu, dropped.mu)
        np.testing.assert_allclose(gone.sd, dropped.sd)
        self.assertFalse(np.allclose(gone.mu, plain.mu))
        same, kept = SEL.without_table(self.cells, "a", self.keys, VOC, "a")
        np.testing.assert_allclose(same.mu, plain.mu)
        np.testing.assert_allclose(same.sd, plain.sd)
        two = ST.strata_of(papers({"a": 0.0, "b": 1.0}) + papers({"z": 0.5}, keys=("canal_ap",)))
        alone, kept = SEL.without_table(two, "a", ["canal_ap", "h_ant"], VOC, "b")
        self.assertEqual(kept, len(LUMBAR))      # h_ant is printed by a and b alone: plain's value is kept
        np.testing.assert_allclose(alone.mu[1], ST.others_table(two, "a", ["h_ant"], VOC, ({}, float("nan")), False).mu[0])

    def test_one_vote_per_population_is_the_geometric_mean_of_the_others_sds(self):
        cells = ST.strata_of([series(p, "canal_ap", lv, 17.0 + i, sd=sd, n=n)
                              for p, sd, n in (("a", 2.0, 30.0), ("big", 4.0, 300.0), ("small", 1.0, 20.0))
                              for i, lv in enumerate(LUMBAR)])
        plain = ST.others_table(cells, "a", ["canal_ap"], VOC, ({}, float("nan")), False)
        vote, kept = SEL.one_vote_table(cells, "a", ["canal_ap"], VOC)
        self.assertEqual(kept, 0)
        np.testing.assert_allclose(vote.sd, 2.0)                 # sqrt(4 x 1), whatever the sizes
        np.testing.assert_allclose(vote.mu, plain.mu)
        self.assertEqual(SEL.base_table(cells, "a", ["canal_ap"], VOC, SEL.ONE_VOTE)[0].sd.tolist(), vote.sd.tolist())

    def test_every_base_gets_a_temperature_of_its_own_and_a_tempered_candidate(self):
        self.assertEqual(SEL.tempered_name(SEL.PLAIN), SEL.TEMPERED)
        self.assertEqual(set(SEL.CANDIDATES), set(SEL.CORE) | set(SEL.EXCLUSION))
        for base in SEL.BASES[1:]:
            self.assertIn(base, SEL.EXCLUSION)
            self.assertIn(SEL.tempered_name(base), SEL.EXCLUSION)
        cells = ST.strata_of(papers({"a": 0.0, "b": 1.2, "yadav2020": -1.2, "d": 2.0, "frontphys2026": -2.0}))
        choice = SEL.inner_choice(cells, "a", self.keys, VOC, (1,), columns=10, seed=3, k_grid=(1.0,), t_grid=(0.5, 1.0, 2.0))
        self.assertEqual(sorted(choice["t_by"]), sorted(SEL.BASES))
        self.assertEqual(choice["t_by"][SEL.PLAIN], choice["t"])
        for b in SEL.BASES:
            self.assertEqual(choice["t_by"][b][1], max((0.5, 1.0, 2.0), key=lambda t: choice["t_curves"][b, t, 1]))
        rows = SEL.score_paper(cells, "yadav2020", self.keys, VOC, 10, (1,), choice, seed=5, k_grid=(1.0,), t_grid=(1.0,))[0]
        by = {r["candidate"]: r for r in rows}
        self.assertEqual(by["without yadav2020"]["log_score"], by[SEL.PLAIN]["log_score"])   # held out, so never read anyway
        self.assertEqual(by["without yadav2020, tempered"]["exact"], by[SEL.PLAIN]["exact"])
        self.assertEqual(by["without frontphys2026, tempered"]["temperature"], choice["t_by"]["without frontphys2026"][1])

    def test_summarise_weighs_each_population_once_and_the_winner_is_the_best_log_score(self):
        def row(cand, w, paper, ls, ex, d_ls, d_ex):
            return {"candidate": cand, "width": w, "paper": paper, "log_score": ls, "exact": ex, "log_score_vs_plain": d_ls,
                    "exact_vs_plain": d_ex, "regret": 0.1, "loss": 1.0, "ece": 0.05, "answered": 0.1, "n_answered": 10, "errors": 1}
        rows = [row(SEL.PLAIN, 1, "p", -1.0, 0.5, 0.0, 0.0), row(SEL.PLAIN, 1, "q", -2.0, 0.4, 0.0, 0.0),
                row(SEL.WIDENED, 1, "p", -0.9, 0.5, 0.1, 0.0), row(SEL.WIDENED, 1, "q", -1.5, 0.45, 0.5, 0.05),
                row(SEL.MIXTURE, 1, "p", -1.2, 0.6, -0.2, 0.1), row(SEL.MIXTURE, 1, "q", -2.1, 0.5, -0.1, 0.1)]
        bins = [{"candidate": c, "width": 1, "paper": p, "bin": 9, "low": 0.9, "high": 1.0, "fields": 10, "sum_top": 9.5, "sum_hit": 9.0}
                for c in (SEL.PLAIN, SEL.WIDENED, SEL.MIXTURE) for p in ("p", "q")]
        summary = SEL.summarise(rows, bins, (1,))
        wid = next(r for r in summary if r["candidate"] == SEL.WIDENED)
        self.assertAlmostEqual(wid["log_score_mean"], -1.2)
        self.assertAlmostEqual(wid["log_score_vs_plain"], 0.3)
        self.assertEqual(wid["wins_vs_plain"], 2)
        self.assertEqual(wid["populations"], 2)
        self.assertAlmostEqual(wid["ece_pooled"], 0.05)
        won = SEL.winner(summary, (1,))
        self.assertEqual(won["by_log_score"], SEL.WIDENED)
        self.assertEqual(won["by_accuracy"], SEL.MIXTURE)
        self.assertEqual(won["by_log_score_vs_plain"][0]["wins"], 2)

    def test_a_rule_far_from_the_population_scores_under_its_own_table(self):
        far, _ = ST.paper_table(self.cells, "d", self.keys, VOC)
        logev_own, truth, group = SEL.log_evidence(self.pop, self.own, 2, GENERATOR)
        logev_far = SEL.log_evidence(self.pop, far, 2, GENERATOR)[0]
        s_own, s_far = SEL.scores(logev_own, truth, group), SEL.scores(logev_far, truth, group)
        self.assertGreater(s_own["log_score"], s_far["log_score"])
        self.assertTrue(math.isfinite(s_far["log_score_se"]))
        self.assertEqual(s_own["fields"], len(truth))


if __name__ == "__main__":
    unittest.main()
