"""Every scheme's raw values resolve to the right level, and a volume read under the wrong
scheme says so."""
import unittest

from scanimport import schemes as S


class Schemes(unittest.TestCase):
    def test_verse_alphabet(self):
        self.assertEqual(S.level_of("verse", 1), "C1")
        self.assertEqual(S.level_of("verse", 8), "T1")
        self.assertEqual(S.level_of("verse", 19), "T12")
        self.assertEqual(S.level_of("verse", 20), "L1")
        self.assertEqual(S.level_of("verse", 25), "L6")
        self.assertEqual(S.level_of("verse", 26), "sacrum")
        self.assertEqual(S.level_of("verse", 28), "T13")
        self.assertIsNone(S.level_of("verse", 27))          # the coccyx is no body of the column
        self.assertEqual(S.level_of("spineps", 24), "L5")

    def test_ctspinopelvic_reads_29_as_sacrum_and_ribs(self):
        self.assertEqual(S.level_of("ctspinopelvic", 29), "sacrum")
        self.assertEqual(S.level_of("ctspinopelvic", 26), "sacrum")
        self.assertEqual(S.rib_of("ctspinopelvic", 34), 1)
        self.assertEqual(S.rib_of("ctspinopelvic", 59), 13)

    def test_moose_stored_ids(self):
        self.assertEqual(S.level_of("moose", 59), "C1")
        self.assertEqual(S.level_of("moose", 77), "T12")
        self.assertEqual(S.level_of("moose", 82), "L5")
        self.assertEqual(S.level_of("moose", 83), "L6")
        self.assertEqual(S.level_of("moose", 86), "sacrum")
        self.assertIsNone(S.level_of("moose", 20))          # a VerSe id means nothing to MOOSE
        self.assertEqual(S.rib_of("moose", 32), 1)

    def test_enhance_pet_ids(self):
        self.assertEqual(S.level_of("enhance", 2), "C2")
        self.assertEqual(S.level_of("enhance", 19), "T12")
        self.assertEqual(S.level_of("enhance", 25), "L6")
        self.assertEqual(S.level_of("enhance", 28), "sacrum")
        self.assertIsNone(S.level_of("enhance", 26))        # a hip
        self.assertFalse(S.EXPRESSES["enhance"]["T13"])
        self.assertEqual(S.problems("enhance", {2: 50, 28: 90, 26: 400, 27: 400}), [])

    def test_enhance_read_as_verse_is_reported(self):
        self.assertTrue(any("ENHANCE" in p for p in S.problems("verse", {2: 50, 24: 50, 26: 400, 27: 400, 28: 90})))

    def test_totalseg_by_name_and_label_map(self):
        self.assertEqual(S.TOTALSEG_FILES["vertebrae_L5"], "L5")
        self.assertEqual(S.TOTALSEG_FILES["vertebrae_S1"], "sacrum")
        self.assertNotIn("vertebrae_L6", S.TOTALSEG_FILES)
        self.assertEqual(S.level_of("totalseg", 31, {31: "vertebrae_L1"}), "L1")
        self.assertIsNone(S.level_of("totalseg", 5, {5: "liver"}))
        with self.assertRaises(ValueError):
            S.table_of("totalseg")

    def test_what_each_scheme_can_express(self):
        self.assertFalse(S.EXPRESSES["totalseg"]["L6"])
        self.assertFalse(S.EXPRESSES["moose"]["T13"])
        self.assertTrue(S.EXPRESSES["verse"]["T13"])

    def test_wrong_scheme_is_reported(self):
        moose_volume = {66: 100, 67: 100, 78: 100}
        self.assertTrue(any("no value" in p for p in S.problems("verse", {200: 5})))
        self.assertTrue(any("not VerSe" in p for p in S.problems("verse", {20: 10, 66: 5})))
        self.assertEqual(S.problems("moose", moose_volume), [])
        self.assertTrue(S.problems("nonsense", {}))


if __name__ == "__main__":
    unittest.main()
