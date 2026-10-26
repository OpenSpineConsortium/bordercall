"""The Panjabi junction models: the decoder, the template, the twins and the real columns.

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import os
import shutil
import tempfile
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import junction as J          # noqa: E402
import panjabi as P           # noqa: E402



class Decoder(unittest.TestCase):
    def test_clean_step_is_cut_where_the_calls_flip(self):
        pl = J.decode(np.array([0.1, 0.2, 0.1, 0.9, 0.8, 0.95]))
        self.assertEqual(pl.cut, 3)
        self.assertTrue(pl.in_view)
        self.assertGreater(pl.margin, 0.0)

    def test_all_below_and_all_above_are_the_ends(self):
        self.assertEqual(J.decode(np.array([0.9, 0.9, 0.8])).cut, 0)
        self.assertEqual(J.decode(np.array([0.1, 0.1, 0.2])).cut, 3)
        self.assertFalse(J.decode(np.array([0.1, 0.1, 0.2])).in_view)


class Reference(unittest.TestCase):
    def test_every_level_of_every_measure_is_in_the_table(self):
        ref = P.load_reference()
        for m in P.MEASURES:
            for lv in P.LEVELS:
                mean, sd = ref[m][lv]
                self.assertGreater(mean, 0.0)
                self.assertGreater(sd, 0.0)

    def test_cuts_count_the_regions(self):
        ref = P.load_reference()
        rng = np.random.default_rng(0)
        col = P.synthesize(ref, "typical", rng)
        self.assertEqual(col.cut("ct"), 5)
        self.assertEqual(col.cut("tl"), 17)
        six = P.synthesize(ref, "six_lumbar", rng)
        self.assertEqual(six.cut("tl"), 17)
        self.assertEqual(len(six), 23)
        # the count names a thirteenth rib-bearing body L1, so its junction is above it; the
        # ribs put it below, one level apart, and the same for a rib on L1; no rib on T12 the other way
        t13 = P.synthesize(ref, "t13", rng)
        self.assertEqual(len(t13), 23)
        self.assertEqual((t13.cut("tl"), t13.cut("tl", truth="ribs")), (17, 18))
        rib = P.synthesize(ref, "lumbar_rib", rng)
        self.assertEqual((rib.cut("tl"), rib.cut("tl", truth="ribs")), (17, 18))
        norib = P.synthesize(ref, "no_rib_t12", rng)
        self.assertEqual((norib.cut("tl"), norib.cut("tl", truth="ribs")), (17, 16))
        self.assertEqual((norib.cut("ct"), norib.cut("ct", truth="ribs")), (5, 5))
        # a window without the transitional body has one truth
        sub = t13.window(5, 12)
        self.assertEqual((sub.cut("tl"), sub.cut("tl", truth="ribs")), (7, 7))
        sub = t13.window(14, 20)
        self.assertEqual((sub.cut("tl"), sub.cut("tl", truth="ribs")), (3, 4))


class TemplateModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ref = P.load_reference(measures=list(J.DEFAULT_MEASURES))

    def test_namings_cover_every_structure_once(self):
        t = J.Template("tl", self.ref)
        keyed = {(n, c["ct"], c["tl"]) for n, c in t.namings(6)}
        self.assertEqual(len(keyed), len(t.namings(6)))
        cuts = {}
        for n, c in t.namings(6):
            cuts.setdefault(n, set()).add(c["tl"])
        # the count's junction follows the position: above the thirteenth thoracic-shaped body
        self.assertEqual(cuts[("T10", "T11", "T12", "L1", "L2", "L3")], {3})
        self.assertEqual(cuts[("T11", "T12", "T13", "L1", "L2", "L3")], {2})
        # the same six lumbar names at two positions: the last six of a column, or the 18th body
        # of lumbar shape and the five below it
        self.assertEqual(cuts[("L1", "L2", "L3", "L4", "L5", "L6")], {0, 1})

    def test_the_posterior_is_flat_over_the_cut_before_the_data(self):
        # every naming equally likely gives every cut the same mass whatever its number of namings
        t = J.Template("tl", self.ref)
        n = 6
        rows = [{"cut": c["tl"]} for _, c in t.namings(n)]
        counts = {}
        for r in rows:
            counts[r["cut"]] = counts.get(r["cut"], 0) + 1
        self.assertGreater(max(counts.values()), min(counts.values()))
        flat = {m: np.exp(t.mu[m]["T8"]) * np.ones(n) for m in t.measures}
        t2 = J.Template("tl", self.ref)
        t2.loglik = lambda values, names: {m: 0.0 for m in t2.measures}
        ll, _ = t2.posterior(flat)
        finite = ll[np.isfinite(ll)]
        np.testing.assert_allclose(finite, finite[0], atol=1e-9)

    def test_a_noiseless_column_is_named_exactly(self):
        rng = np.random.default_rng(1)
        for j in J.JUNCTIONS:
            t = J.Template(j, self.ref, noise_mm=0.0)
            for ph in ("typical", "six_lumbar", "four_lumbar"):
                col = P.synthesize(self.ref, ph, rng, scale_sd=0.0, rho=1.0, noise_mm=0.0,
                                   measures=list(J.DEFAULT_MEASURES))
                # rho 1 with the offset draw still moves each level by its own sd: zero it
                for m in col.values:
                    col.values[m] = np.asarray([self.ref[m][lv][0] if lv in self.ref[m]
                                                else col.values[m][i] for i, lv in enumerate(col.levels)])
                sub = col.window(3, 21)
                pl = t.place(sub.values)
                self.assertEqual(pl.cut, col.cut(j) - 3, (j, ph, sub.levels, pl.cut))

    def test_the_cervicothoracic_call_survives_the_lumbosacral_twin(self):
        models = {"ct": J.Template("ct", self.ref)}
        tw = J.twin_invariance(models, self.ref, n=60, seed=2)
        for ph in P.LUMBOSACRAL:
            self.assertGreaterEqual(tw[ph]["ct"]["same_call_rate"], 0.95, (ph, tw[ph]))

    def test_explain_names_the_measure_that_decided(self):
        rng = np.random.default_rng(3)
        col = P.synthesize(self.ref, "typical", rng, measures=list(J.DEFAULT_MEASURES))
        t = J.Template("tl", self.ref)
        ex = t.explain(col.window(10, 20).values)
        self.assertEqual(set(ex["gap_by_measure"]), set(J.DEFAULT_MEASURES))
        self.assertEqual(len(ex["best_names"]), 10)


class LocalModel(unittest.TestCase):
    def test_trains_and_places(self):
        ref = P.load_reference(measures=list(J.DEFAULT_MEASURES))
        m = J.train(ref, "ct", n_columns=60, windows_per_column=1)
        self.assertEqual(len(m.names), len(m.w) - 1)
        rng = np.random.default_rng(4)
        col = P.synthesize(ref, "typical", rng, measures=list(J.DEFAULT_MEASURES))
        pl = m.place(col.window(2, 10).values)
        self.assertEqual(pl.n, 8)
        back = J.Model.from_json(m.to_json())
        np.testing.assert_allclose(back.w, m.w)

    def test_scores_abstain_below_the_margin(self):
        s = J.Score()
        s.add(J.Placement(cut=2, margin=0.01, loglik=np.zeros(4), p=np.zeros(3)), 2, margin=0.5)
        s.add(J.Placement(cut=2, margin=2.0, loglik=np.zeros(4), p=np.zeros(3)), 2, margin=0.5)
        self.assertEqual((s.n, s.abstained, s.exact, s.called), (2, 1, 1, 1))


class RealColumns(unittest.TestCase):
    """The corpus path, on a made-up corpus in the grid job's layout (synth_corpus), since the
    only real corpus the owner trusts is counted from C2 on the grid."""

    @classmethod
    def setUpClass(cls):
        import synth_corpus
        cls.tmp = tempfile.mkdtemp()
        synth_corpus.write(cls.tmp, n=120, seed=1)
        cls.levels = os.path.join(cls.tmp, "levels.csv")
        cls.phenotype = os.path.join(cls.tmp, "phenotype.csv")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_windows_are_whole_columns_with_every_measure(self):
        w = J.real_windows(self.levels, measures=("endplate", "h_post", "canal_w", "canal_ap"))
        self.assertEqual(len(w), 120)
        names, vals = w["synthetic__0000"]
        self.assertEqual(names[0], "C3")
        self.assertIn(names[-1], ("L4", "L5", "L6"))
        for m in ("endplate", "h_post", "canal_w", "canal_ap"):
            self.assertEqual(len(vals[m]), len(names))
            self.assertTrue((vals[m] > 0).all())

    def test_the_template_names_the_junctions_of_whole_columns(self):
        import phenotype as PH
        ref = P.load_reference(measures=list(J.DEFAULT_MEASURES))
        w = J.real_windows(self.levels)
        phen = {k: v["phenotype"] for k, v in PH.load(self.phenotype).items()}
        ct = J.real_check(J.Template("ct", ref), w, phen)["all"]
        tl = J.real_check(J.Template("tl", ref), w, phen)["all"]
        self.assertEqual((ct.n, tl.n), (120, 120))
        # a 22-level column has 23 cuts: chance is one in 23 exact
        self.assertGreater(ct.exact / ct.called, 0.8)
        self.assertGreater(tl.within_one / tl.called, 0.8)

    def test_the_local_rule_decodes_without_its_class_prior(self):
        ref = P.load_reference(measures=list(J.DEFAULT_MEASURES))
        m = J.train(ref, "tl", seed=0, n_columns=300)
        self.assertLess(m.prior, 0.3)                      # a fifth of a column is lumbar
        w = J.real_windows(self.levels)
        cuts = [m.place(vals).cut for names, vals in w.values()]
        # with the prior left in every uninformative level read as 'above' and the cut sat at
        # the column's end; divided out, the cut lands inside the column
        self.assertLess(sum(1 for c, (names, _) in zip(cuts, w.values()) if c >= len(names)) / len(cuts), 0.2)
        again = J.Model.from_json(m.to_json())
        self.assertEqual(again.prior, m.prior)

    def test_run_corpus_writes_both_junctions(self):
        out = os.path.join(self.tmp, "panjabi")
        r = J.run_corpus(self.levels, self.phenotype, outdir=out, n_columns=200)
        self.assertEqual(sorted(r["junctions"]), ["ct", "tl"])
        self.assertIn("fitted_on_corpus", r["junctions"]["tl"])
        self.assertTrue(os.path.exists(os.path.join(out, "panjabi_corpus.json")))


if __name__ == "__main__":
    unittest.main()
