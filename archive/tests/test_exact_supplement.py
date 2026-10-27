"""The exact study's supplement: each tally checked against the record's own way of counting.

    python -m unittest tests.test_exact_supplement -v

A robustness world drawn again here must give the region counts robust_task gives for the same
world; the bodies near a regional border must be the two above it and the two below; the
quadrature pooled over chunks of columns must equal the check run on all of them at once; and a
column of another length must have every one of its fields counted, with no place in the rule
for its L6.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "bordercall"))

import exact as E                 # noqa: E402
import exact_supplement as ES     # noqa: E402
import neighbour as NB            # noqa: E402
import panjabi as P               # noqa: E402

MEASURES = list(E.MEASURES7)
SYNTH = dict(rho=0.5, noise_mm=1.0, scale_sd=0.07)


def _ref():
    return P.load_reference(measures=MEASURES)


class TestRegionTally(unittest.TestCase):
    def test_near_a_border_is_the_two_above_and_the_two_below(self):
        cut = E.LEVELS.index("T1")
        near = [E.LEVELS[i] for i in range(E.L) if ES.near_border(np.array([i]), cut)[0]]
        self.assertEqual(near, ["C6", "C7", "T1", "T2"])
        cut = E.LEVELS.index("L1")
        near = [E.LEVELS[i] for i in range(E.L) if ES.near_border(np.array([i]), cut)[0]]
        self.assertEqual(near, ["T11", "T12", "L1", "L2"])

    def test_a_sure_posterior_claims_its_region_and_a_split_one_none(self):
        levels = np.array([E.LEVELS.index("C7"), E.LEVELS.index("T12"), E.LEVELS.index("L3")])
        tp = np.zeros((3, E.L))
        tp[0, E.LEVELS.index("T1")] = 1.0                 # sure, and wrong: a cervical body called thoracic
        tp[1, E.LEVELS.index("T12")] = 0.5                # split across T12/L1: no region claim
        tp[1, E.LEVELS.index("L1")] = 0.5
        tp[2, E.LEVELS.index("L3")] = 1.0                 # sure and right, far from both borders
        t = ES.region_tally(tp, levels)
        self.assertEqual(t["all"], [2, 1, 3])
        self.assertEqual(t["C7/T1"], [1, 1, 1])
        self.assertEqual(t["T12/L1"], [0, 0, 1])
        self.assertEqual(t["far"], [1, 0, 1])


class TestWorlds(unittest.TestCase):
    def test_a_world_drawn_again_gives_the_record_s_region_counts(self):
        ref = _ref()
        tasks = E.robust_tasks()
        for kind in ("specimens", "levels"):
            task = next(t for t in tasks if ES.world_kind(t) == kind)
            mine = ES.world_task_tally(task, ref, MEASURES, SYNTH, widths=(1,))
            _, theirs = E.robust_task(task, ref, MEASURES, SYNTH, widths=(1,))
            for rule in E.RULES:
                claims = theirs[rule]["1"]["claims"]
                self.assertEqual(mine[rule]["1"]["all"][0], claims["regions_decided"], (kind, rule))
                self.assertEqual(mine[rule]["1"]["all"][1], claims["regions_errors"], (kind, rule))


class TestMatchesRecord(unittest.TestCase):
    def test_the_record_s_share_and_count_are_matched_and_a_wrong_count_is_not(self):
        split = {"specimens": {"honest": {"1": {"all": {"made": 3, "wrong": 1, "bodies": 4}}}}}
        record = {"robust": {"table_specimens": {"honest": {"1": {"claims": {
            "regions_decided": 0.75, "regions_errors": 1}}}}}}
        self.assertEqual(ES.matches_record(split, record), {"specimens.honest.1": True})
        record["robust"]["table_specimens"]["honest"]["1"]["claims"]["regions_errors"] = 2
        self.assertEqual(ES.matches_record(split, record), {"specimens.honest.1": False})


class TestQuadrature(unittest.TestCase):
    def test_pooled_over_chunks_equals_the_check_on_all_columns(self):
        ref = _ref()
        mu, sd = E.table_arrays(ref, MEASURES)
        V = E.column_values(NB.draw_columns(ref, ["typical"], 97, 6, MEASURES), MEASURES)
        widths, nodes = (1, 9), (41, 161)
        whole = E.quadrature_check(V, mu, sd, SYNTH, widths=widths, nodes=nodes)
        parts = [E.quadrature_check(V[:2], mu, sd, SYNTH, widths=widths, nodes=nodes),
                 E.quadrature_check(V[2:], mu, sd, SYNTH, widths=widths, nodes=nodes)]
        pooled = ES.pool_quadrature(parts, {})
        self.assertEqual(pooled["max_abs_posterior_difference"], whole["max_abs_posterior_difference"])
        self.assertEqual(pooled["calls_changed"], whole["calls_changed"])


class TestAnomalous(unittest.TestCase):
    def test_every_field_is_counted_and_the_rule_has_no_place_for_an_l6(self):
        ref = _ref()
        mu, sd = E.table_arrays(ref, MEASURES)
        got = ES.anomalous(ref, MEASURES, mu, sd, SYNTH, phenotypes=("six_lumbar",), n_columns=3, widths=(1,))
        cols = NB.draw_columns(ref, ["six_lumbar"], ES.ANOMALOUS_SEED, 3, MEASURES)
        self.assertEqual(got["six_lumbar"]["1"]["fields"], sum(len(c.levels) for c in cols))
        self.assertNotIn("L6", E.LEVELS)
        self.assertIn("L6", cols[0].levels)
        self.assertLessEqual(got["six_lumbar"]["1"]["wrong"], got["six_lumbar"]["1"]["answered"])


class TestFirstColumns(unittest.TestCase):
    def test_all_columns_and_the_first_agree_when_they_are_the_same(self):
        ref = _ref()
        mu, sd = E.table_arrays(ref, MEASURES)
        V = E.column_values(NB.draw_columns(ref, ["typical"], 97, 5, MEASURES), MEASURES)
        got = ES.first_columns(V, mu, sd, SYNTH, list(range(len(MEASURES))), n_first=5, widths=(1, 3))
        for n in ("1", "3"):
            self.assertEqual(got[n]["first"], got[n]["all"])


if __name__ == "__main__":
    unittest.main()
