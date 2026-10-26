"""Naming a vertebra from its neighbours: the traps the brief names, pinned.

    python -m unittest discover -s tests -v

The three traps of docs/NEIGHBOUR_IDENTITY_STUDY.md each produce a plausible wrong answer and
raise nothing, so each has a test here. Position: the same neighbourhood moved to another
position of another column must give the same features and the same call, bit for bit, for
every arm and every normalisation. The count: the name a body gets is its position, whatever
its shape, and the rib reading moves the thoracolumbar bodies by exactly RIB_SHIFT. Chance: the
marginal the chance rates assume is the one the rows carry.

And the two closed-form pieces are checked against something outside the fit: the published-
means classifier must name every body of a noise-free column drawn at the table's means, and
the Newton softmax must agree with border.py's logistic regression on a two-class problem.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import neighbour as NB        # noqa: E402
import panjabi as P           # noqa: E402
import border as B            # noqa: E402

MEASURES = list(NB.REGIMES["both"])


def _ref():
    return P.load_reference(measures=MEASURES)


class TestNames(unittest.TestCase):
    def test_count_names_are_positions(self):
        ref = _ref()
        rng = np.random.default_rng(0)
        for ph in P.PHENOTYPES:
            col = P.synthesize(ref, ph, rng, measures=MEASURES)
            names = NB.count_names(col)
            self.assertEqual(len(names), len(col))
            self.assertEqual(names[:17], P.CERVICAL + P.THORACIC)
            self.assertEqual(names[17], "L1")
        six = P.synthesize(ref, "six_lumbar", rng, measures=MEASURES)
        self.assertEqual(NB.count_names(six)[-1], "L6")
        t13 = P.synthesize(ref, "t13", rng, measures=MEASURES)
        # the count names the thirteenth rib-bearing body L1 and the body below it L2
        self.assertEqual(t13.levels[17], "T13")
        self.assertEqual(NB.count_names(t13)[17], "L1")
        self.assertEqual(NB.count_names(t13)[18], "L2")

    def test_rib_ordinals_move_by_rib_shift(self):
        ref = _ref()
        rng = np.random.default_rng(0)
        for ph in ("typical", "four_lumbar", "six_lumbar"):
            col = P.synthesize(ref, ph, rng, measures=MEASURES)
            self.assertEqual(NB.rib_ordinals(col), list(range(len(col))))
        for ph in ("t13", "lumbar_rib"):
            col = P.synthesize(ref, ph, rng, measures=MEASURES)
            ro = NB.rib_ordinals(col)
            t = col.transitional_at
            self.assertIsNone(ro[t])
            self.assertEqual(ro[:t], list(range(t)))
            self.assertEqual(ro[t + 1:], [p - 1 for p in range(t + 1, len(col))])
            # the rib reading and the count agree with Column.cut's two truths
            self.assertEqual(col.cut("tl", "ribs") - col.cut("tl", "count"), P.RIB_SHIFT[ph])
        col = P.synthesize(ref, "no_rib_t12", rng, measures=MEASURES)
        ro = NB.rib_ordinals(col)
        t = col.transitional_at
        self.assertEqual(ro[t:], [p + 1 for p in range(t, len(col))])


class TestPosition(unittest.TestCase):
    """The brief's first trap: no absolute position may reach a model."""

    def _column_and_moved(self, rng, ref, arm, norm):
        offs = NB.ARMS[arm]
        reach = max(abs(d) for d in offs)
        if norm != "external" and norm[1] != "all":
            reach = max(reach, int(norm[1]))
        col = P.synthesize(ref, "typical", rng, measures=MEASURES)
        n = len(col)
        i = int(rng.integers(reach, n - reach))
        block = list(range(i - reach, i + reach + 1))
        others = [j for j in range(n) if j not in block]
        rng.shuffle(others)
        split = int(rng.integers(0, len(others) + 1))
        order = others[:split] + block + others[split:]
        moved = {m: col.values[m][order] for m in MEASURES}
        return col.values, i, moved, split + reach

    def test_features_do_not_move_with_the_window(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        rng = np.random.default_rng(3)
        norms = ["external"] + [("median", k) for k in NB.MEDIAN_BODIES]
        for arm in NB.ARMS:
            for norm in norms:
                moved_count = 0
                for _ in range(20):
                    values, i, moved, j = self._column_and_moved(rng, ref, arm, norm)
                    f0 = NB.features(values, i, arm, MEASURES, norm, constant)
                    f1 = NB.features(moved, j, arm, MEASURES, norm, constant)
                    moved_count += int(i != j)
                    np.testing.assert_allclose(f0, f1, rtol=0, atol=1e-12,
                                               err_msg="%s %s: the features moved with the window" % (arm, norm))
                # A trial where the block lands where it was tests nothing, so most must move.
                self.assertGreater(moved_count, 10, "%s %s: the window seldom moved" % (arm, norm))

    def test_fitted_models_do_not_move_with_the_window(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, ("typical",), 11, 40, MEASURES)
        rows = NB.rows_of(cols, "flank", MEASURES, "external", constant)
        model = NB.train_softmax(rows, "flank", MEASURES)
        disc = NB.train_discriminant(rows, "flank", MEASURES)
        pub = NB.build_published(ref, "flank", MEASURES, constant)
        for m in (model, disc, pub):
            r = NB.shuffle_invariance(ref, "flank", MEASURES, m, "external", constant, trials=30)
            self.assertEqual(r["identical"], r["trials"], m)

    def test_edge_levels_are_not_targets(self):
        self.assertEqual(NB.eligible(22, "below1"), list(range(21)))
        self.assertEqual(NB.eligible(22, "above1"), list(range(1, 22)))
        self.assertEqual(NB.eligible(22, "flank"), list(range(1, 21)))
        self.assertEqual(NB.eligible(22, "flank2"), list(range(2, 20)))
        self.assertEqual(NB.eligible(22, "with_target"), list(range(2, 20)))


class TestChance(unittest.TestCase):
    def test_marginal_is_uniform_over_the_visible_levels(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, P.PHENOTYPES, 97, 12, MEASURES)
        rows = NB.rows_of(cols, "flank", MEASURES, "external", constant)
        c = NB.chance(rows)
        self.assertEqual(c["k_names"], 20)
        self.assertEqual(set(c["marginal"].values()), {2})
        self.assertAlmostEqual(c["uniform_exact"], 1 / 20)
        self.assertAlmostEqual(c["majority_exact"], 1 / 20)
        self.assertAlmostEqual(c["uniform_within_one"], (3 * 20 - 2) / 400)


class TestPublished(unittest.TestCase):
    def test_names_a_column_drawn_at_the_means(self):
        """Noise-free, size 1: every body of a typical column is at the table's means, and the
        published-means classifier must name every eligible target, in every arm and regime."""
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        values = {m: np.array([ref[m][lv][0] for lv in P.LEVELS]) for m in MEASURES}
        for arm in NB.ARMS:
            for regime, ms in NB.REGIMES.items():
                pub = NB.build_published(ref, arm, ms, {m: constant[m] for m in ms})
                X = np.asarray([NB.features(values, i, arm, ms, "external", constant) for i in NB.eligible(22, arm)])
                pred = pub.predict(X)
                self.assertEqual(pred.tolist(), NB.eligible(22, arm), (arm, regime))

    def test_size_is_profiled_out(self):
        """The same column at 1.3 times the size names the same, since one log-size is free."""
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        pub = NB.build_published(ref, "flank2", MEASURES, constant)
        for s in (0.8, 1.3):
            values = {m: s * np.array([ref[m][lv][0] for lv in P.LEVELS]) for m in MEASURES}
            X = np.asarray([NB.features(values, i, "flank2", MEASURES, "external", constant) for i in NB.eligible(22, "flank2")])
            self.assertEqual(pub.predict(X).tolist(), NB.eligible(22, "flank2"))


class TestFit(unittest.TestCase):
    def test_newton_softmax_matches_the_logistic_regression_on_two_classes(self):
        rng = np.random.default_rng(1)
        X = rng.normal(size=(400, 3))
        y = (X @ np.array([1.5, -1.0, 0.3]) + 0.2 + rng.normal(scale=0.5, size=400) > 0).astype(int)
        W = NB.fit_softmax(X, y, k=2, l2=1e-3)
        # the reference class is the last: W is the log-odds of class 0 over class 1
        w = B.fit_logreg(X, y, iters=4000, lr=0.5, l2=1e-3)
        np.testing.assert_allclose(-W[:, 0], w, atol=0.02)

    def test_scalar_index_is_monotone_on_typical_columns(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, ("typical",), 11, 60, MEASURES)
        rows = NB.rows_of(cols, "flank", MEASURES, "external", constant)
        disc = NB.train_discriminant(rows, "flank", MEASURES)
        chk = NB.monotone_check(disc, rows)
        self.assertEqual(chk["classes"][0], "C4")
        self.assertGreater(chk["spearman"], 0.9)
        self.assertEqual(len(chk["class_means"]), 20)

    def test_score_counts_offsets(self):
        rows = NB.Rows(X=np.zeros((4, 1)), y=np.array([3, 4, 5, 6]), rib=np.array([3, 4, 4, -1]),
                       group=np.array([0, 0, 1, 1]), phenotype=np.array(["t13"] * 4), n_columns=2)
        per = NB.score(np.array([3, 4, 4, 7]), rows)["t13"]
        self.assertEqual(per["exact"], 2)
        self.assertEqual(per["within_one"], 4)
        self.assertEqual(per["offsets"], {"-1": 1, "0": 2, "1": 1})
        self.assertEqual(per["n_rib"], 3)
        self.assertEqual(per["exact_rib"], 3)
        self.assertEqual(per["mean_offset_by_level"], {"C6": 0.0, "C7": 0.0, "T1": -1.0, "T2": 1.0})


if __name__ == "__main__":
    unittest.main()


import neighbour_more as NM   # noqa: E402


class TestField(unittest.TestCase):
    """Solution G, the field decoded as a whole, with the target in it."""

    def test_field_features_do_not_move_with_the_window(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        rng = np.random.default_rng(7)
        for half in (0, 1, 2, 3):
            for with_target in (True, False):
                offs = NM.field_offsets(half, with_target)
                if not offs:
                    continue
                for _ in range(20):
                    col = P.synthesize(ref, "typical", rng, measures=MEASURES)
                    n = len(col)
                    i = int(rng.integers(half, n - half))
                    block = list(range(i - half, i + half + 1))
                    others = [j for j in range(n) if j not in block]
                    rng.shuffle(others)
                    split = int(rng.integers(0, len(others) + 1))
                    order = others[:split] + block + others[split:]
                    moved = {m: col.values[m][order] for m in MEASURES}
                    f0 = NM.field_features(col.values, i, offs, MEASURES, constant)
                    f1 = NM.field_features(moved, split + half, offs, MEASURES, constant)
                    np.testing.assert_allclose(f0, f1, rtol=0, atol=1e-12)

    def test_published_field_names_a_noise_free_column_exactly(self):
        """Nothing fitted: a column at the table's means, at any size, is named exactly at every
        eligible target for every half-width and regime, the size profiled out over the field."""
        ref = _ref()
        for regime, measures in NB.REGIMES.items():
            constant = NB.external_constant(ref, measures)
            pub = NM.build_published_self(ref, measures, constant)
            for size in (0.8, 1.0, 1.3):
                values = {m: np.asarray([size * ref[m][lv][0] for lv in P.LEVELS]) for m in measures}
                for half in (0, 1, 2, 4):
                    for with_target in (True, False):
                        offs = NM.field_offsets(half, with_target)
                        if not offs:
                            continue
                        model = NM.Field(offs=offs, p=len(measures), published=pub)
                        targets = NM.field_targets(len(P.LEVELS), offs)
                        X = np.asarray([NM.field_features(values, i, offs, measures, constant) for i in targets])
                        self.assertEqual(model.predict(X).tolist(), targets, (regime, size, half, with_target))

    def test_fitted_field_is_position_free_and_names_in_range(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, ("typical",), 11, 40, MEASURES)
        model = NM.train_self(NM.self_rows(cols, MEASURES, constant), MEASURES)
        for half in (1, 2):
            offs = NM.field_offsets(half, True)
            g = NM.Field(offs=offs, p=len(MEASURES), self_model=model)
            r = NM.field_shuffle_invariance(ref, offs, MEASURES, g, constant, trials=30)
            self.assertEqual(r["identical"], r["trials"])
            # the candidate set: the names whose implied bodies exist in the table
            self.assertEqual(NM.candidates(offs).tolist(), list(range(half, NB.K - half)))
            # a six-lumbar and a t13 column have a body beyond the table; the field still answers
            rng = np.random.default_rng(2)
            for ph in ("six_lumbar", "t13"):
                col = P.synthesize(ref, ph, rng, measures=MEASURES)
                rows = NM.field_rows([col], offs, MEASURES, constant)
                pred = g.predict(rows.X)
                self.assertTrue(((pred >= half) & (pred < NB.K - half)).all(), ph)

    def test_field_with_one_body_is_the_self_model(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, ("typical",), 11, 30, MEASURES)
        rows = NM.self_rows(cols, MEASURES, constant)
        model = NM.train_self(rows, MEASURES)
        g = NM.Field(offs=(0,), p=len(MEASURES), self_model=model)
        np.testing.assert_array_equal(g.predict(rows.X), model.predict(rows.X))


class TestNonlinear(unittest.TestCase):
    """Solution H, one hidden layer: deterministic from its seed, position-free, and at least as
    good as chance on what it was fitted on."""

    def test_mlp_is_deterministic_and_position_free(self):
        ref = _ref()
        constant = NB.external_constant(ref, MEASURES)
        cols = NB.draw_columns(ref, ("typical",), 11, 30, MEASURES)
        rows = NB.rows_of(cols, "flank", MEASURES, "external", constant)
        a = NM.train_mlp(rows, "flank", MEASURES, hidden=16, steps=200)
        b = NM.train_mlp(rows, "flank", MEASURES, hidden=16, steps=200)
        np.testing.assert_array_equal(a.predict(rows.X), b.predict(rows.X))
        self.assertGreater(float((a.predict(rows.X) == rows.y).mean()), 0.2)
        r = NB.shuffle_invariance(ref, "flank", MEASURES, a, "external", constant, trials=30)
        self.assertEqual(r["identical"], r["trials"])
