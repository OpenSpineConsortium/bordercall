"""The junction figures build from the recorded run, write their numbers beside them, and build
the same twice, so the folder a reader rebuilds compares file for file with the one delivered."""
import csv
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bordercall"))
RECORD = os.path.join(ROOT, "records", "panjabi-2026-10-26", "three-measures", "panjabi_junction.json")
NAMES = ["junction_profile", "junction_posterior", "junction_width", "junction_twins", "junction_blend"]


def rows_of(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


class JunctionFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import json
        import junction_figures
        cls.F = junction_figures
        cls.tmp = tempfile.mkdtemp()
        cls.out = os.path.join(cls.tmp, "first")
        with open(os.devnull, "w") as sink:
            stdout, sys.stdout = sys.stdout, sink
            try:
                cls.written = junction_figures.run(RECORD, cls.out)
            finally:
                sys.stdout = stdout
        with open(RECORD, encoding="utf-8") as fh:
            cls.d = json.load(fh)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_figure_has_its_four_files_under_a_megabyte_and_the_record_names_the_run(self):
        for name in NAMES:
            for ext in ("pdf", "png", "csv", "caption.txt"):
                path = os.path.join(self.out, "%s.%s" % (name, ext))
                self.assertTrue(os.path.exists(path), path)
                self.assertLess(os.path.getsize(path), 1 << 20, path)
        with open(os.path.join(self.out, "FIGURES.md"), encoding="utf-8") as fh:
            record = fh.read()
        self.assertIn(self.F.sha256(RECORD), record)
        self.assertIn(self.F.sha256(self.F.P.DEFAULT_REFERENCE), record)
        for name in NAMES:
            self.assertIn("`%s.csv`" % name, record)

    def test_the_width_csv_holds_the_numbers_the_run_recorded(self):
        rows = {(r["junction"], int(r["width"]), r["metric"]): r for r in rows_of(os.path.join(self.out, "junction_width.csv"))}
        for j in ("ct", "tl"):
            for w, table in self.d["by_width"]["%s/profile" % j].items():
                for key in ("exact", "within_one"):
                    r = rows[(j, int(w), key)]
                    self.assertEqual(int(r["k"]), table[key])
                    self.assertEqual(int(r["called"]), table["called"])
                    self.assertAlmostEqual(float(r["rate"]), table[key] / table["called"], places=5)
                    self.assertLessEqual(float(r["wilson_lo"]), float(r["rate"]))
                    self.assertGreaterEqual(float(r["wilson_hi"]), float(r["rate"]) - 1e-9)

    def test_the_blend_csv_scores_one_set_of_calls_both_ways(self):
        rows = {(r["phenotype"], float(r["blend"]), r["truth"]): r for r in rows_of(os.path.join(self.out, "junction_blend.csv"))}
        for rec in self.d["blend_sweep"]["profile"]:
            self.assertEqual(int(rows[(rec["phenotype"], rec["blend"], "count")]["k"]), rec["exact"])
            self.assertEqual(int(rows[(rec["phenotype"], rec["blend"], "ribs")]["k"]), rec["exact_ribs"])

    def test_the_twins_csv_holds_the_twins_and_the_phenotypes(self):
        rows = {(r["panel"], r["junction"], r["class"]): r for r in rows_of(os.path.join(self.out, "junction_twins.csv"))}
        for k in ("four_lumbar", "six_lumbar"):
            for j in ("ct", "tl"):
                t = self.d["twins"]["profile"][k][j]
                self.assertEqual((int(rows[("twin", j, k)]["k"]), int(rows[("twin", j, k)]["n"])), (t["same_call"], t["n"]))
        for ph in self.F.PHENOTYPE_ORDER:
            for j in ("ct", "tl"):
                t = self.d["by_phenotype"]["%s/profile" % j][ph]
                self.assertEqual(int(rows[("phenotype", j, ph)]["k"]), t["exact"])

    def test_the_profile_csv_is_the_reference_table(self):
        ref = self.F.P.load_reference(measures=self.d["measures"])
        for r in rows_of(os.path.join(self.out, "junction_profile.csv")):
            if r["measure"] in ref:
                self.assertAlmostEqual(float(r["mean_mm"]), ref[r["measure"]][r["level"]][0], places=4)
                self.assertAlmostEqual(float(r["sd_mm"]), ref[r["measure"]][r["level"]][1], places=4)

    def test_the_posterior_csv_sums_to_one_and_marks_one_truth_per_junction(self):
        rows = rows_of(os.path.join(self.out, "junction_posterior.csv"))
        for j in ("ct", "tl"):
            mine = [r for r in rows if r["junction"] == j]
            self.assertAlmostEqual(sum(float(r["posterior"]) for r in mine), 1.0, places=4)
            self.assertEqual(sum(int(r["truth"]) for r in mine), 1)
            self.assertEqual(sum(int(r["called"]) for r in mine), 1)

    def test_the_style_draws_in_one_ink(self):
        plt = self.F.style()
        self.assertEqual(plt.rcParams["axes.prop_cycle"].by_key()["color"], [self.F.INK])
        self.assertFalse(plt.rcParams["axes.grid"])
        self.assertEqual(plt.rcParams["font.family"], ["serif"])

    def test_two_builds_give_the_same_files(self):
        second = os.path.join(self.tmp, "second")
        with open(os.devnull, "w") as sink:
            stdout, sys.stdout = sys.stdout, sink
            try:
                self.F.run(RECORD, second)
            finally:
                sys.stdout = stdout
        for f in sorted(os.listdir(self.out)):
            with open(os.path.join(self.out, f), "rb") as a, open(os.path.join(second, f), "rb") as b:
                left, right = a.read(), b.read()
            if f == "FIGURES.md":
                left = left.replace(self.out.encode(), b"<out>")
                right = right.replace(second.encode(), b"<out>")
            self.assertEqual(left, right, f)


if __name__ == "__main__":
    unittest.main()
