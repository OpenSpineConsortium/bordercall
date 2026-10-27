"""The owner's tiers, person by person."""
import unittest

from scanimport import tiers as T
from scanimport.column import Column


def study(sid, subject, modality, whole, annotation):
    return Column(study={"study_id": sid, "subject_id": subject, "modality": modality, "countable": whole,
                         "has_sacrum": whole, "annotation": annotation, "source": "t", "phenotype": "typical"},
                  bodies=[])


class Tiers(unittest.TestCase):
    def tier(self, *cols):
        return T.person_tiers(cols)[0]

    def test_common_spellings_of_x_ray_are_x_rays(self):
        for m in ("xray", "x-ray", "XR", "radiography"):
            self.assertEqual(self.tier(study("a", "p", m, True, "human"))["tier"], "gold 3", m)

    def test_a_whole_pair_with_a_person_annotating_one_is_gold_1(self):
        r = self.tier(study("a", "p", "ct", True, "machine"), study("b", "p", "film", True, "human"))
        self.assertEqual(r["tier"], "gold 1")

    def test_a_whole_pair_no_person_is_gold_2(self):
        self.assertEqual(self.tier(study("a", "p", "ct", True, "machine"), study("b", "p", "film", True, "machine"))["tier"],
                         "gold 2")

    def test_a_whole_ct_and_a_partial_film_report_both(self):
        r = self.tier(study("a", "p", "ct", True, "human"), study("b", "p", "fluoro", False, "machine"))
        self.assertEqual(r["tier_alone"], "gold 3")
        self.assertEqual(r["tier_as_pair"], "silver 1")
        self.assertEqual(r["tier"], "gold 3")

    def test_machine_masks_never_raise(self):
        self.assertEqual(self.tier(study("a", "p", "ct", True, "machine"))["tier"], "gold 4")

    def test_a_drr_is_not_an_x_ray(self):
        r = self.tier(study("a", "p", "ct", False, "human"), study("b", "p", "drr", True, "human"))
        self.assertEqual(r["tier_as_pair"], "none")
        self.assertEqual(r["tier"], "silver 3")

    def test_different_people_never_pair(self):
        rows = T.person_tiers([study("a", "p", "ct", True, "human"), study("b", "q", "film", True, "human")])
        self.assertEqual([r["tier"] for r in rows], ["gold 3", "gold 3"])


if __name__ == "__main__":
    unittest.main()
