"""The house format for line graphs (figures.py) and the chain study's figures (chain_figures.py).

    python -m unittest tests.test_schwingcheck_chain_figures -v      # from the repository's root, in the PyMC venv

The build-up study's figures and the chain's are drawn by one style, figures.py's. The chain's four
figures, drawn twice from the same records, are the same files, PDF and PNG included; every
caption is under sixty words; each CSV holds the records' numbers, and a share right that rests on
fewer than ANSWERS_DRAWN fields named at 0.99 is not drawn. The committed figures are what the
code as it stands draws from the committed records, and FIGURES.md names both by sha256.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import chain as CH                              # noqa: E402
from schwingcheck import chain_figures as CF                      # noqa: E402
from schwingcheck import chain_study as CS                        # noqa: E402
from schwingcheck import curve_report as CR                       # noqa: E402
from schwingcheck import figures as FG                            # noqa: E402

Q = CS.QUICK
STEMS = ("chain_accuracy", "chain_answers", "chain_data", "chain_speed")
EXTENSIONS = (".pdf", ".png", ".csv", ".caption.txt")


def quiet(*args):
    pass


def read_csv(path: str):
    with open(path, encoding="ascii") as fh:
        return list(csv.DictReader(fh))


class OneFormat(unittest.TestCase):
    def test_the_build_up_study_and_the_chain_draw_in_one_format(self):
        for name in ("style", "letter", "save", "write_csv", "sha256", "INK", "SERIF", "WIDTH_STYLE"):
            self.assertIs(getattr(CR, name), getattr(FG, name), name)
        for name in ("style", "letter", "save", "write_csv", "sha256", "INK"):
            self.assertIs(getattr(CF, name), getattr(FG, name), name)
        plt = FG.style()
        self.assertEqual(plt.rcParams["font.family"], ["serif"])
        self.assertFalse(plt.rcParams["axes.grid"])
        self.assertFalse(plt.rcParams["axes.spines.top"])
        self.assertFalse(plt.rcParams["axes.spines.right"])


class QuickFigures(unittest.TestCase):
    """The figures of one quick run, axis and speed, drawn twice."""

    @classmethod
    def setUpClass(cls):
        cls.main = CS.run(Q["columns"], (1, CF.DATA_BODIES))
        cls.axis = CS.axis(Q["columns"], (CF.DATA_BODIES,), Q["worlds"], processes=1, log=quiet)
        cls.speed = CS.speed(Q["columns"], Q["speed_widths"], Q["speed"], Q["reference"], log=quiet)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dirs = [os.path.join(cls.tmp.name, d) for d in "ab"]
        cls.drawn = [CF.draw_figures(cls.main, cls.axis, cls.speed, d) for d in cls.dirs]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_drawn_twice_they_are_the_same_files(self):
        names = sorted(os.path.basename(p) for p in self.drawn[0])
        self.assertEqual(names, sorted(os.path.basename(p) for p in self.drawn[1]))
        self.assertEqual(names, sorted(s + e for s in STEMS for e in EXTENSIONS))
        for name in names:
            with open(os.path.join(self.dirs[0], name), "rb") as fa, open(os.path.join(self.dirs[1], name), "rb") as fb:
                self.assertEqual(fa.read(), fb.read(), name)

    def test_every_caption_is_under_sixty_words(self):
        for stem in STEMS:
            with open(os.path.join(self.dirs[0], stem + ".caption.txt"), encoding="ascii") as fh:
                caption = fh.read()
            self.assertLessEqual(FG.words(caption), FG.CAPTION_WORDS, stem)
            self.assertIn("synthetic", caption, stem)
        with open(os.path.join(self.dirs[0], "chain_speed.caption.txt"), encoding="ascii") as fh:
            caption = fh.read()
        c = Q["speed"]
        self.assertIn("median of %d calls) and per field in a batch of %d" % (c["calls"], c["batch"]), caption)

    def test_the_csvs_hold_the_records_numbers(self):
        key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in self.main["rows"]}
        rows = read_csv(os.path.join(self.dirs[0], "chain_accuracy.csv"))
        self.assertEqual(len(rows), len(CH.TYPES) * len(CS.SUBSETS) * len(CS.ARMS) * len(self.main["widths"]))
        for r in rows:
            want = 100 * key[r["type"], int(r["bodies"]), r["measures"], r["rule"]]["exact"]
            self.assertAlmostEqual(float(r["percent"]), want, places=3)
        ax = {(r["people"], r["rule"], r["type"], r["subset"]): r for r in self.axis["rows"] if r["arm"] == "chain"}
        for r in read_csv(os.path.join(self.dirs[0], "chain_data.csv")):
            if r["rule"] == "printed":
                cell = key[r["type"], CF.DATA_BODIES, r["measures"], "chain"]
            else:
                cell = ax[int(r["people"]), r["rule"], r["type"], r["measures"]]
            if r["percent"] != "nan":
                self.assertAlmostEqual(float(r["percent"]), 100 * cell[r["stat"]], places=3)
        sp = {(r["engine"], r["arm"], r["subset"], r["bodies"]): r for r in self.speed["rows"]}
        for r in read_csv(os.path.join(self.dirs[0], "chain_speed.csv")):
            cell = sp[r["engine"], r["rule"], r["measures"], int(r["bodies"])]
            self.assertAlmostEqual(float(r["ms"]), cell["median_ms" if r["how"] == "alone" else "batch_ms"],
                                   delta=1e-5 * cell["median_ms" if r["how"] == "alone" else "batch_ms"])

    def test_a_share_right_on_few_fields_is_not_drawn(self):
        for stem in ("chain_answers", "chain_data"):
            for r in read_csv(os.path.join(self.dirs[0], stem + ".csv")):
                if r.get("stat") in ("right of those", "precision"):
                    self.assertEqual(r["drawn"], "yes" if int(r["fields"]) >= CF.ANSWERS_DRAWN else "no", r)
                else:
                    self.assertEqual(r["drawn"], "yes", r)


class CommittedFigures(unittest.TestCase):
    """records/chain-2026-10-28/figures/ as committed."""

    def test_they_are_drawn_from_the_records_by_the_code_as_it_stands(self):
        with open(os.path.join(CF.OUTDIR, "FIGURES.md"), encoding="ascii") as fh:
            said = fh.read()
        for which in ("main", "axis", "speed"):
            self.assertIn("sha256 %s." % FG.sha256(CS.RECORDS[which]), said)
        for name in ("figures.py", "chain_figures.py", "chain_study.py"):
            self.assertIn("`schwingcheck/%s`, sha256 %s." % (name, FG.sha256(os.path.join(ROOT, "schwingcheck", name))), said)
        with tempfile.TemporaryDirectory() as tmp:
            drawn = sorted(os.path.basename(p) for p in CF.draw_figures(CS.load("main"), CS.load("axis"),
                                                                        CS.load("speed"), tmp))
            self.assertEqual(len(drawn), len(STEMS) * len(EXTENSIONS))
            for name in drawn:
                self.assertIn("`%s`" % name, said)
                if name.endswith((".csv", ".caption.txt")):   # the numbers drawn and the words; a PNG's bytes follow the fonts
                    with open(os.path.join(tmp, name), "rb") as fa, open(os.path.join(CF.OUTDIR, name), "rb") as fb:
                        self.assertEqual(fa.read(), fb.read(), name)

    def test_the_readme_shows_each_figure(self):
        with open(CS.README, encoding="ascii") as fh:
            text = fh.read()
        for stem in STEMS:
            self.assertIn('src="../records/chain-2026-10-28/figures/%s.png"' % stem, text)


if __name__ == "__main__":
    unittest.main()
