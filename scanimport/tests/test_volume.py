"""A label volume read from NIfTI files under each scheme gives the same column."""
import math
import os
import tempfile
import unittest

import numpy as np

from scanimport import schemes, volume as V
from scanimport.tests import phantom as PH

LEVELS = ["T12", "L1", "L2"]


def ids_for(table):
    return {lv: v for v, lv in table.items() if lv in LEVELS}


class Ingest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        d = cls.tmp.name
        kw = dict(margin=12.0, spacing=(1.1, 1.1, 1.6))
        lab, cls.aff, sub, _ = PH.column(LEVELS, ids_for(schemes.VERSE), subregions=True, **kw)
        PH.save(os.path.join(d, "verse.nii.gz"), lab, cls.aff)
        PH.save(os.path.join(d, "sub.nii.gz"), sub, cls.aff)
        moose = np.zeros_like(lab)
        for lv, v in ids_for(schemes.VERSE).items():
            moose[lab == v] = ids_for(schemes.MOOSE)[lv]
        PH.save(os.path.join(d, "moose.nii.gz"), moose, cls.aff)
        os.makedirs(os.path.join(d, "ts"))
        for lv, v in ids_for(schemes.VERSE).items():
            PH.save(os.path.join(d, "ts", "vertebrae_%s.nii.gz" % lv), (lab == v).astype(np.uint8), cls.aff)
        PH.save(os.path.join(d, "ts", "liver.nii.gz"), np.zeros_like(lab, np.uint8), cls.aff)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def path(self, *p):
        return os.path.join(self.tmp.name, *p)

    def test_every_scheme_gives_the_same_chords(self):
        verse = V.ingest(self.path("verse.nii.gz"), "verse", "s1", "test", "human", "phantom")
        moose = V.ingest(self.path("moose.nii.gz"), "moose", "s1", "test", "machine", "phantom")
        ts = V.ingest(self.path("ts"), "totalseg", "s1", "test", "human", "phantom")
        for col in (verse, moose, ts):
            self.assertEqual(col.levels, LEVELS)
        for a, b, c in zip(verse.bodies, moose.bodies, ts.bodies):
            for m in a.values:
                self.assertAlmostEqual(a.values[m], b.values[m], places=6)
                self.assertAlmostEqual(a.values[m], c.values[m], places=6)
        self.assertEqual(verse.study["phenotype"], "unknown")
        self.assertFalse(verse.study["countable"])
        self.assertEqual(ts.study["expresses"]["L6"], False)
        self.assertEqual(verse.study["spacing_mm"], [1.1, 1.1, 1.6])

    def test_subregions(self):
        col = V.ingest(self.path("verse.nii.gz"), "spineps", "s1", "test", "machine", "SPINEPS", subregion=self.path("sub.nii.gz"))
        self.assertTrue(all(abs(b.values["endplate"] - 44.0) < 1.2 for b in col.bodies))
        self.assertIn("subregions", col.bodies[0].methods["endplate"])

    def test_the_wrong_scheme_names_nothing_and_says_so(self):
        col = V.ingest(self.path("moose.nii.gz"), "verse", "s1", "test", "machine", "phantom")
        self.assertEqual(col.levels, [])
        self.assertTrue(col.study["problems"])

    def test_annotation_is_stated_never_inferred(self):
        with self.assertRaises(SystemExit):
            V.ingest(self.path("verse.nii.gz"), "verse", "s1", "test", "unsure", "phantom")


if __name__ == "__main__":
    unittest.main()
