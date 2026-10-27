"""Coarse claims: each claim's mass is the posterior on its levels, and the committed record
keeps the rule's promise in the worlds where the rule is told the truth."""
import json
import os
import unittest

import numpy as np

from coarse import study as C

RECORD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "records", "coarse-2026-10-27", "coarse.json")


class Claims(unittest.TestCase):
    def test_a_certain_posterior_gives_each_claim_its_truth(self):
        L = len(C.EX.LEVELS)
        for k in range(L):
            tp = np.zeros((1, L))
            tp[0, k] = 1.0
            for c in C.CLAIMS:
                with self.subTest(level=C.EX.LEVELS[k], claim=c["name"]):
                    self.assertEqual(bool(C.claim_mass(tp, c)[0] == 1.0), bool(C.claim_truth(np.array([k]), c)[0]))

    def test_the_borders_sit_between_the_levels_they_name(self):
        lv = C.EX.LEVELS
        self.assertEqual(C.border_of({"below": "L1"}), lv.index("T12") + 0.5)
        self.assertEqual(C.border_of({"above": "T6"}), lv.index("T6") + 0.5)
        self.assertTrue(np.isnan(C.border_of({"interval": ["T11", "T12"]})))

    def test_every_claim_names_a_source_or_says_it_has_none(self):
        for c in C.CLAIMS:
            with self.subTest(claim=c["name"]):
                self.assertTrue(any(ch.isdigit() for ch in c["use"]) or "no source" in c["use"])


class Record(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RECORD) as fh:
            cls.record = json.load(fh)

    def test_the_record_claims_are_the_code_claims(self):
        self.assertEqual(self.record["claims"], C.CLAIMS)

    def test_claims_made_at_099_are_right_at_least_99_per_cent_where_the_rule_is_told_the_truth(self):
        for key, by_n in self.record["results"].items():
            if key.startswith("film, magnification wrong"):
                continue
            for n, rules in by_n.items():
                for rule, res in rules.items():
                    for name, row in res["claims"].items():
                        if row.get("settled_by_field_size") or not row["n_decided"]:
                            continue
                        with self.subTest(world=key, n=n, rule=rule, claim=name):
                            self.assertGreaterEqual(1.0 - row["errors"] / row["n_decided"], 0.99)

    def test_a_claim_the_window_decides_is_marked_settled(self):
        # nine bodies centred on the middle one reach from C7 to L1 at most, so the middle body is
        # never below L2
        row = self.record["results"]["nominal | all seven"]["9"]["exact rule"]["claims"]["below L2"]
        self.assertTrue(row["settled_by_field_size"])


if __name__ == "__main__":
    unittest.main()
