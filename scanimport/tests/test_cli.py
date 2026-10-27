"""The command line end to end: a CT's labels and a film's corners in, every file out, a
counted synthetic study scored."""
import contextlib
import csv
import io
import json
import os
import tempfile
import unittest

import numpy as np

from scanimport import RULE_LEVELS, SEVEN, schemes
from scanimport.__main__ import main
from scanimport.column import Body, Column, facts_from_levels, write_column
from scanimport.tests import phantom as PH
from scanimport.tests.test_radiograph import annotation, body
import exact as EX
import panjabi as P


def run(argv):
    out = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out):
        try:
            main(argv)
        except SystemExit as e:
            code = e.code or 0
    return code, out.getvalue()


class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def p(self, *a):
        return os.path.join(self.d, *a)

    def test_ct_and_film_of_one_person(self):
        levels = ["T12", "L1", "L2"]
        lab, aff, _, _ = PH.column(levels, {lv: v for v, lv in schemes.VERSE.items() if lv in levels}, margin=12.0,
                                   spacing=(1.2, 1.2, 1.8))
        PH.save(self.p("seg.nii.gz"), lab, aff)
        code, text = run(["ingest-ct", "--labels", self.p("seg.nii.gz"), "--scheme", "verse", "--study", "ct1",
                          "--subject", "p1", "--source", "phantom", "--annotation", "human", "--out", self.p("imp")])
        self.assertEqual(code, 0, text)
        self.assertIn("3 bodies (T12 L1 L2)", text)
        with open(self.p("fx.json"), "w") as fh:
            json.dump(annotation("ap", [body("L1", 0, 0, 230, 100), body("L2", 0, 120, 240, 100)]), fh)
        code, text = run(["ingest-xr", "--xr", self.p("fx.json"), "--study", "xr1", "--subject", "p1",
                          "--source", "phantom", "--annotation", "human", "--out", self.p("imp")])
        self.assertEqual(code, 0, text)
        for f in ("columns/ct1.json", "columns/xr1.json", "fields/ct1.csv", "bodies.csv", "studies.csv",
                  "tiers.csv", "MANIFEST.json"):
            self.assertTrue(os.path.exists(self.p("imp", f)), f)
        with open(self.p("imp", "tiers.csv")) as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tier_as_pair"], "silver 1")
        with open(self.p("imp", "MANIFEST.json")) as fh:
            man = json.load(fh)
        self.assertEqual(man["studies"], 2)
        self.assertEqual(len(man["runs"]), 2)
        self.assertEqual(run(["check", self.p("imp")])[0], 0)
        code, text = run(["compare", self.p("imp"), "--all", "--out", self.p("cmp")])
        self.assertEqual(code, 0, text)
        with open(self.p("cmp", "compare.csv")) as fh:
            self.assertEqual(fh.readline().strip(), "# bodies every_named_body")
            cmp = {(r["measure"], r["level"]): r for r in csv.DictReader(fh)}
        self.assertEqual(cmp[("endplate", "L1")]["bodies"], "2")
        code, text = run(["name", self.p("imp", "fields", "ct1.csv")])
        self.assertEqual(code, 0, text)
        self.assertIn("named", text)

    def test_check_fails_on_a_recorded_problem(self):
        with open(self.p("bad.json"), "w") as fh:
            json.dump(annotation("ap", [body("L9", 0, 0, 230, 100), body("L1", 0, 200, 230, 100)]), fh)
        code, text = run(["ingest-xr", "--xr", self.p("bad.json"), "--study", "b1", "--source", "t",
                          "--annotation", "human", "--out", self.p("badimp")])
        self.assertEqual(code, 0, text)
        code, text = run(["check", self.p("badimp")])
        self.assertEqual(code, 1, text)
        self.assertIn("problem:", text)

    def test_score_a_counted_study(self):
        ref = P.load_reference(P.DEFAULT_REFERENCE, SEVEN)
        rng = np.random.default_rng(3)
        V = EX.column_values([P.synthesize(ref, "typical", rng, measures=SEVEN)], SEVEN)[0]
        levels = ["C1", "C2"] + RULE_LEVELS + ["sacrum"]
        bodies = [Body(lv) for lv in levels]
        for j in range(len(RULE_LEVELS)):
            bodies[j + 2].values = {m: float(V[i, j]) for i, m in enumerate(SEVEN)}
        study = {"study_id": "syn1", "subject_id": "syn1", "source": "panjabi", "modality": "synthetic",
                 "annotation": "machine", "scale_log_mean": 0.0, "scale_log_sd": 0.0}
        study.update(facts_from_levels(levels, {"L6": True, "T13": True}))
        write_column(Column(study, bodies), self.p("syn"))
        code, text = run(["score", self.p("syn"), "--n", "1", "9", "--out", self.p("scores")])
        self.assertEqual(code, 0, text)
        self.assertIn("typical n=9", text)
        with open(self.p("scores", "scores.json")) as fh:
            res = json.load(fh)
        self.assertEqual({s["n"] for s in res["summary"]}, {1, 9})
        with open(self.p("scores", "RUNS.json")) as fh:
            self.assertEqual(json.load(fh)["runs"][0]["command"][3], "score")
        code, text = run(["name", self.p("syn", "fields", "syn1.csv"), "--json"])
        out = json.loads(text)
        self.assertEqual(out["bodies"], 22)
        self.assertEqual(out["names"][0], "C3")


if __name__ == "__main__":
    unittest.main()
