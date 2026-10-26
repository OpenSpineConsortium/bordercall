"""The exact-rule slides and their figures build from the recorded run: the figures byte for byte
as delivered, the two decks with five slides each in which every figure, word and equation is an
element of its own, every equation native Office Math with its picture and its LaTeX beside it, and
the numbers on the slides the record's."""
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bordercall"))
sys.path.insert(0, os.path.join(ROOT, "slides"))
RECORD = os.path.join(ROOT, "records", "exact-2026-10-26")
DELIVERED = os.path.join(RECORD, "slide-figures")
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
      "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}


def quiet(fn, *args, **kwargs):
    with open(os.devnull, "w") as sink:
        stdout, sys.stdout = sys.stdout, sink
        try:
            return fn(*args, **kwargs)
        finally:
            sys.stdout = stdout


class ExactSlideFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import exact_slide_figures
        cls.F = exact_slide_figures
        cls.tmp = tempfile.mkdtemp()
        cls.written = quiet(exact_slide_figures.run, os.path.join(RECORD, "exact.json"), cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_panel_is_rebuilt_byte_for_byte_as_delivered(self):
        names = sorted(self.F.SIZES)
        self.assertEqual(len(names), 7)
        for name in names:
            for ext in ("pdf", "png", "csv", "caption.txt"):
                built = os.path.join(self.tmp, "%s.%s" % (name, ext))
                with open(built, "rb") as fh, open(os.path.join(DELIVERED, os.path.basename(built)), "rb") as gh:
                    self.assertEqual(fh.read(), gh.read(), built)

    def test_captions_stay_within_sixty_words(self):
        for name in self.F.SIZES:
            with open(os.path.join(self.tmp, name + ".caption.txt"), encoding="utf-8") as fh:
                self.assertLessEqual(len(fh.read().split()), 60, name)

    def test_the_record_of_the_figures_names_the_run_and_the_code(self):
        with open(os.path.join(self.tmp, "FIGURES.md"), encoding="utf-8") as fh:
            text = fh.read()
        self.assertIn(self.F.JF.sha256(os.path.join(RECORD, "exact.json")), text)
        for name in self.F.SIZES:
            self.assertIn("`%s.csv`" % name, text)


class ExactSlides(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import make_exact_slides
        cls.S = make_exact_slides
        cls.tmp = tempfile.mkdtemp()
        cls.decks = {v: make_exact_slides.build(v, os.path.join(cls.tmp, "exact_slides_%s.pptx" % v),
                                                eqdir=os.path.join(cls.tmp, "equations"))
                     for v in ("neurips", "cns")}
        cls.N = make_exact_slides.Numbers(RECORD)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def slides(self, venue):
        from lxml import etree
        with zipfile.ZipFile(self.decks[venue]) as z:
            names = sorted((n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")),
                           key=lambda n: int(n[len("ppt/slides/slide"):-4]))
            return [etree.fromstring(z.read(n)) for n in names]

    def test_each_deck_has_five_slides_with_a_title_and_speaker_notes(self):
        from pptx import Presentation
        for venue in self.decks:
            prs = Presentation(self.decks[venue])
            self.assertEqual(len(prs.slides), 5, venue)
            for s in prs.slides:
                self.assertTrue(s.shapes.title.text_frame.text.strip(), venue)
                self.assertGreater(len(s.notes_slide.notes_text_frame.text), 200, venue)

    def test_every_equation_is_office_math_with_its_picture_and_its_latex(self):
        for venue in self.decks:
            seen = set()
            for root in self.slides(venue):
                for alt in root.iter("{%s}AlternateContent" % NS["mc"]):
                    choice = alt.find("mc:Choice", NS)
                    name = choice.find(".//p:cNvPr", NS).get("name")
                    self.assertTrue(name.startswith("Equation: "), name)
                    key = name[len("Equation: "):]
                    self.assertIsNotNone(choice.find(".//a14:m/m:oMathPara", NS), name)
                    self.assertIsNotNone(alt.find("mc:Fallback//a:blip", NS), name)
                    descr = choice.find(".//p:cNvPr", NS).get("descr")
                    self.assertEqual(descr, "LaTeX: " + self.S.EQUATIONS[key], name)
                    seen.add(key)
            self.assertEqual(seen, set(self.S.EQUATIONS), venue)

    def test_shape_ids_are_unique_on_every_slide(self):
        for venue in self.decks:
            for root in self.slides(venue):
                ids = [e.get("id") for e in root.iter("{%s}cNvPr" % NS["p"])
                       if e.getparent().getparent().getparent().tag != "{%s}Fallback" % NS["mc"]]
                self.assertEqual(len(ids), len(set(ids)), venue)

    def test_every_figure_is_a_named_picture_with_its_caption_as_alternative_text(self):
        from pptx import Presentation
        import exact_slide_figures as F
        for venue in self.decks:
            used = set()
            for s in Presentation(self.decks[venue]).slides:
                for shape in s.shapes:
                    if shape.name.startswith("Figure: "):
                        key = shape.name[len("Figure: "):]
                        with open(os.path.join(DELIVERED, key + ".caption.txt"), encoding="utf-8") as fh:
                            caption = fh.read().strip()
                        self.assertEqual(shape._element.nvPicPr.cNvPr.get("descr"), caption, key)
                        used.add(key)
            self.assertEqual(used, set(F.SIZES), venue)

    def test_the_headline_numbers_on_the_slides_are_the_records(self):
        from pptx import Presentation
        texts = {}
        for venue in self.decks:
            words = []
            for s in Presentation(self.decks[venue]).slides:
                for shape in s.shapes:
                    if shape.has_text_frame:
                        words.append(shape.text_frame.text)
            texts[venue] = "\n".join(words)
        for venue, text in texts.items():
            self.assertIn("%.1f%%" % (100 * self.N.exact(3)), text, venue)
            self.assertIn("%.1f%%" % (100 * self.N.exact(9)), text, venue)
            self.assertIn("%.2f%%" % (100 * self.N.sure(3)["precision"]), text, venue)

    def test_the_build_refuses_a_forbidden_word(self):
        deck = self.S.Deck(self.S.Venue("neurips"), DELIVERED, False)
        deck.words.append("a note that says " + self.S.FORBIDDEN[0])
        with self.assertRaises(SystemExit):
            deck.check()

    def test_the_builders_are_ascii_with_lf_line_ends(self):
        for path in (os.path.join(ROOT, "slides", "make_exact_slides.py"),
                     os.path.join(ROOT, "bordercall", "exact_slide_figures.py")):
            with open(path, "rb") as fh:
                raw = fh.read()
            self.assertNotIn(b"\r", raw, path)
            raw.decode("ascii")


if __name__ == "__main__":
    unittest.main()
