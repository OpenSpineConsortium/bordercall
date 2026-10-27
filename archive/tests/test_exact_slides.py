"""The exact-rule slides and their figures build from the recorded run: both figure sets byte for
byte as delivered, each panel at the inches its venue's deck gives it; the two decks with five
slides each in which every figure, word and equation is an element of its own; the NeurIPS deck
with every equation as native Office Math beside its picture and its LaTeX; the CNS deck results
only, with no equation and no method word anywhere in the saved file, and a build that refuses one;
the confidentiality marking until --public; the file's properties the speaker's; the numbers on
the slides the record's; each deck rebuilt byte for byte as committed, its equation cache current
and never written by a build into another folder, and its plain mathematics upright."""
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bordercall"))
sys.path.insert(0, os.path.join(ROOT, "slides"))
RECORD = os.path.join(ROOT, "records", "exact-2026-10-26")
DELIVERED = {"neurips": os.path.join(RECORD, "slide-figures"), "cns": os.path.join(RECORD, "slide-figures", "cns")}
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

    def built(self, venue):
        return self.F.venue_dir(self.tmp, venue)

    def test_both_sets_are_rebuilt_byte_for_byte_as_delivered(self):
        self.assertEqual(len(self.F.SIZES["neurips"]), 7)
        self.assertEqual(len(self.F.SIZES["cns"]), 6)
        self.assertNotIn("exact_slide_calibration", self.F.SIZES["cns"])
        for venue in self.F.VENUES:
            for name in sorted(self.F.SIZES[venue]):
                for ext in ("pdf", "png", "csv", "caption.txt"):
                    f = "%s.%s" % (name, ext)
                    with open(os.path.join(self.built(venue), f), "rb") as fh, \
                            open(os.path.join(DELIVERED[venue], f), "rb") as gh:
                        self.assertEqual(fh.read(), gh.read(), (venue, f))

    def test_the_posterior_panel_refuses_a_record_it_does_not_reproduce(self):
        import copy
        with open(os.path.join(RECORD, "exact.json")) as fh:
            d = json.load(fh)
        other = copy.deepcopy(d)
        other["gh_nodes"] = 81
        with self.assertRaises(ValueError):
            self.F.centred_posteriors(other)
        other = copy.deepcopy(d)
        other["widths"]["1"]["regimes"]["both"]["by_centre"][self.F.CENTRE]["answered_099"] += 0.001
        with self.assertRaisesRegex(ValueError, "answered_099"):
            self.F.centred_posteriors(other)

    def test_each_panel_is_drawn_at_the_inches_its_deck_gives_it(self):
        from PIL import Image
        for venue in self.F.VENUES:
            for name, (w, h) in self.F.SIZES[venue].items():
                with Image.open(os.path.join(DELIVERED[venue], name + ".png")) as im:
                    dpi = im.info.get("dpi", (100, 100))[0]
                    self.assertAlmostEqual(im.size[0] / dpi, w, delta=0.02, msg=(venue, name))
                    self.assertAlmostEqual(im.size[1] / dpi, h, delta=0.02, msg=(venue, name))
        self.assertAlmostEqual(self.F.SIZES["cns"]["exact_slide_posterior"][0],
                               round(self.F.SIZES["neurips"]["exact_slide_posterior"][0] * 11.10 / 12.13, 2))

    def test_captions_stay_within_sixty_words(self):
        for venue in self.F.VENUES:
            for name in self.F.SIZES[venue]:
                with open(os.path.join(self.built(venue), name + ".caption.txt"), encoding="utf-8") as fh:
                    self.assertLessEqual(len(fh.read().split()), 60, (venue, name))

    def test_the_cns_captions_hold_no_method_word(self):
        import make_exact_slides as S
        for name in self.F.SIZES["cns"]:
            with open(os.path.join(self.built("cns"), name + ".caption.txt"), encoding="utf-8") as fh:
                text = fh.read()
            self.assertIsNone(S.CNS_REFUSED.search(text), (name, text))
            self.assertNotIn("%%", text, name)

    def test_the_record_of_each_set_names_the_run_and_the_code(self):
        for venue in self.F.VENUES:
            with open(os.path.join(self.built(venue), "FIGURES.md"), encoding="utf-8") as fh:
                text = fh.read()
            self.assertIn(self.F.JF.sha256(os.path.join(RECORD, "exact.json")), text)
            self.assertIn(self.F.JF.sha256(os.path.join(ROOT, "bordercall", "exact_slide_figures.py")), text)
            # The committed record names the code as it now stands.
            with open(os.path.join(DELIVERED[venue], "FIGURES.md"), encoding="utf-8") as fh:
                named = re.findall(r"- Code: `([^`]+)`, sha256 ([0-9a-f]{64})", fh.read())
            self.assertIn("bordercall/exact_slide_figures.py", dict(named))
            for path, digest in named:
                self.assertEqual(self.F.JF.sha256(os.path.join(ROOT, path)), digest, (venue, path))
            for name in self.F.SIZES[venue]:
                self.assertIn("`%s.csv`" % name, text)


class ExactSlides(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import make_exact_slides
        cls.S = make_exact_slides
        cls.tmp = tempfile.mkdtemp()
        cls.eqdir = os.path.join(cls.tmp, "equations")
        cls.decks = {v: make_exact_slides.build(v, os.path.join(cls.tmp, "exact_slides_%s.pptx" % v), eqdir=cls.eqdir)
                     for v in ("neurips", "cns")}
        cls.N = make_exact_slides.Numbers(RECORD)
        cls.EQ = make_exact_slides.equations(cls.N)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def slides(self, venue, path=None):
        from lxml import etree
        with zipfile.ZipFile(path or self.decks[venue]) as z:
            names = sorted((n for n in z.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")),
                           key=lambda n: int(n[len("ppt/slides/slide"):-4]))
            return [etree.fromstring(z.read(n)) for n in names]

    def words(self, venue, path=None):
        from pptx import Presentation
        out = []
        for s in Presentation(path or self.decks[venue]).slides:
            for shape in s.shapes:
                if shape.has_text_frame:
                    out.append(shape.text_frame.text)
        return "\n".join(out)

    def test_each_deck_has_five_slides_with_a_title_and_speaker_notes(self):
        from pptx import Presentation
        for venue in self.decks:
            prs = Presentation(self.decks[venue])
            self.assertEqual(len(prs.slides), 5, venue)
            for s in prs.slides:
                self.assertTrue(s.shapes.title.text_frame.text.strip(), venue)
                self.assertGreater(len(s.notes_slide.notes_text_frame.text), 200, venue)

    def test_every_neurips_equation_is_office_math_with_its_picture_and_its_latex(self):
        seen = set()
        for root in self.slides("neurips"):
            for alt in root.iter("{%s}AlternateContent" % NS["mc"]):
                choice = alt.find("mc:Choice", NS)
                name = choice.find(".//p:cNvPr", NS).get("name")
                self.assertTrue(name.startswith("Equation: "), name)
                key = name[len("Equation: "):]
                self.assertIsNotNone(choice.find(".//a14:m/m:oMathPara", NS), name)
                self.assertIsNotNone(alt.find("mc:Fallback//a:blip", NS), name)
                descr = choice.find(".//p:cNvPr", NS).get("descr")
                self.assertEqual(descr, "LaTeX: " + self.EQ[key], name)
                seen.add(key)
        self.assertEqual(seen, set(self.EQ))
        self.assertIn("covariance", seen)
        self.assertIn("estimate", seen)

    def test_each_deck_is_rebuilt_byte_for_byte_as_committed(self):
        import hashlib
        for venue, path in self.decks.items():
            with open(path, "rb") as fh, open(os.path.join(ROOT, "slides", "exact", os.path.basename(path)), "rb") as gh:
                self.assertEqual(hashlib.sha256(fh.read()).hexdigest(), hashlib.sha256(gh.read()).hexdigest(), venue)

    def test_the_committed_equation_cache_is_current_and_a_build_elsewhere_writes_none(self):
        from lxml import etree
        for name, tex in self.EQ.items():
            root = etree.parse(os.path.join(self.S.EQDIR, name + ".omml.xml")).getroot()
            self.assertEqual(root.get("tex"), tex, name)
            self.assertFalse(os.path.exists(os.path.join(self.eqdir, name + ".omml.xml")), name)

    def test_plain_math_runs_are_upright_and_letters_italic(self):
        upright = italic = 0
        for root in self.slides("neurips"):
            for run in root.iter("{%s}r" % NS["m"]):
                rpr = run.find("a:rPr", NS)
                plain = self.S.upright(run)
                self.assertEqual(rpr.get("i"), "0" if plain else "1")
                upright, italic = upright + plain, italic + (not plain)
        self.assertGreater(upright, 0)
        self.assertGreater(italic, 0)

    def test_the_equations_take_their_constants_from_the_record(self):
        d = self.N.d
        self.assertIn(r"\mu_{m,k:k+n-1}", self.EQ["likelihood"])
        self.assertIn(r"\sum_{k'}", self.EQ["bayes"])
        self.assertIn(r"\mathcal{N}(0,\, %g^2)" % d["synth"]["scale_sd"], self.EQ["size"])
        self.assertIn(r"\rho = %g" % d["synth"]["rho"], self.EQ["size"])
        h = d["robust"]["rules"]["honest"]
        self.assertIn(r"\sqrt{1 + 1/%d}" % h["table_n"], self.EQ["honest"])
        self.assertIn(r"%g\ \mathrm{mm}" % h["noise_mm"], self.EQ["honest"])
        self.assertIn(r"\lfloor (n-1)/2 \rfloor", self.EQ["middle"])

    def test_the_cns_deck_has_no_equation_and_no_method_word_anywhere(self):
        for root in self.slides("cns"):
            self.assertEqual(len(list(root.iter("{%s}AlternateContent" % NS["mc"]))), 0)
            self.assertEqual(len(list(root.iter("{%s}oMathPara" % NS["m"]))), 0)
        self.assertEqual(self.S.refusals(self.decks["cns"], cns=True), [])
        self.assertEqual(self.S.refusals(self.decks["neurips"], cns=False), [])
        # The anatomical measure stays allowed; the method word does not.
        self.assertIsNone(self.S.CNS_REFUSED.search("the posterior body height and the posterior height"))
        for word in ("posterior", "prior", "Likelihood", "Gauss-Hermite", "1/12", "LaTeX", "generator"):
            self.assertIsNotNone(self.S.CNS_REFUSED.search("a %s here" % word), word)

    def test_a_method_word_planted_in_a_cns_note_makes_the_build_refuse(self):
        out = os.path.join(self.tmp, "planted.pptx")
        notes = self.S.Deck.notes

        def planted(deck, s, text):
            notes(deck, s, text + " The likelihood is exact.")
        self.S.Deck.notes = planted
        try:
            with self.assertRaises(SystemExit):
                self.S.build("cns", out, eqdir=self.eqdir)
        finally:
            self.S.Deck.notes = notes
        self.assertFalse(os.path.exists(out))

    def test_the_cns_deck_refuses_an_equation(self):
        deck = self.S.Deck(self.S.Venue("cns"), DELIVERED["cns"], False, self.eqdir, self.EQ)
        s = deck.slide("A slide")
        with self.assertRaises(SystemExit):
            deck.equation(s, "bayes", 0.6, 1.5, 20)

    def test_the_marking_is_on_every_slide_until_public(self):
        public = self.S.build("neurips", os.path.join(self.tmp, "public.pptx"), eqdir=self.eqdir, public=True)
        for venue in self.decks:
            from pptx import Presentation
            for s in Presentation(self.decks[venue]).slides:
                texts = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame]
                self.assertTrue(any(self.S.MARKING in t for t in texts), venue)
                self.assertTrue(any("no patient data" in t for t in texts), venue)
        self.assertNotIn(self.S.MARKING, self.words("neurips", public))
        self.assertIn("no patient data", self.words("neurips", public))

    def test_the_file_properties_are_the_speakers(self):
        import datetime
        from pptx import Presentation
        for venue in self.decks:
            cp = Presentation(self.decks[venue]).core_properties
            self.assertEqual(cp.author, "Gregory Schwing", venue)
            self.assertEqual(cp.last_modified_by, "Gregory Schwing", venue)
            self.assertEqual(cp.title, "Can the bodies in view name a vertebra?", venue)
            self.assertEqual(cp.revision, 1, venue)
            self.assertEqual(cp.created, datetime.datetime(2026, 10, 26), venue)
            self.assertEqual(cp.modified, datetime.datetime(2026, 10, 26), venue)
            self.assertFalse(cp.comments, venue)
            with zipfile.ZipFile(self.decks[venue]) as z:
                app = z.read("docProps/app.xml").decode("utf-8")
            self.assertIn("<Slides>5</Slides>", app, venue)
            self.assertNotIn("PowerPoint Presentation", app, venue)

    def test_every_figure_is_a_named_picture_at_its_drawn_width_with_its_caption(self):
        from pptx import Presentation
        import exact_slide_figures as F
        for venue in self.decks:
            used = set()
            for s in Presentation(self.decks[venue]).slides:
                for shape in s.shapes:
                    if shape.name.startswith("Figure: "):
                        key = shape.name[len("Figure: "):]
                        with open(os.path.join(DELIVERED[venue], key + ".caption.txt"), encoding="utf-8") as fh:
                            caption = fh.read().strip()
                        self.assertEqual(shape._element.nvPicPr.cNvPr.get("descr"), caption, key)
                        self.assertAlmostEqual(shape.width / 914400.0, F.SIZES[venue][key][0], places=3, msg=key)
                        used.add(key)
            self.assertEqual(used, set(F.SIZES[venue]), venue)

    def test_the_headline_numbers_on_the_slides_are_the_records(self):
        pct = self.S.pct
        sure3 = self.N.sure(3)
        for venue in self.decks:
            text = self.words(venue)
            self.assertIn("Three bodies name %s; when sure, %s are right" % (pct(self.N.exact(3)),
                                                                            pct(sure3["precision"], 1)), text)
            self.assertIn("%s wrong of %s; named for %s of fields" % (sure3["errors"], "{:,}".format(sure3["n_answered"]),
                                                                       pct(sure3["answered"])), text)
            self.assertIn(pct(self.N.exact(9)), text)
            self.assertIn("a linear classifier: %s; a fitted network: %s"
                          % (pct(self.N.classifier(3), 1), pct(self.N.challenger("network"), 1)), text)
            tl = self.N.cut(1, "T12/L1")
            self.assertIn("%s, %s wrong of %s" % (pct(tl["precision"], 2), tl["errors"], "{:,}".format(tl["n_decided"])),
                          text)
            self.assertIn("of fields with middle body T11 to L1", text)
            self.assertIn("most rates below", text)
        cns = self.words("cns")
        for n in (1, 3, 9):
            self.assertIn(pct(self.N.by_centre(n)), cns)
        self.assertEqual(pct(self.N.by_centre(9)), "95%")
        self.assertIn("No formula or network on these measures names more fields correctly on average.", cns)
        self.assertIn("Next: test the rule on real full-spine CT.", cns)
        self.assertIn("Corrected rule".lower(), cns.lower())
        neurips = self.words("neurips")
        self.assertIn("Next: measure the table on full-spine CTs counted from C2, and carry a real series' prior over "
                      "places.", neurips)
        self.assertNotIn("anomalous", neurips + cns)

    def test_the_classifier_gap_is_on_the_same_columns(self):
        lo, hi = self.N.gap_range()
        self.assertEqual(("%.1f" % lo, "%.1f" % hi), ("10.8", "15.3"))
        self.assertEqual(self.N.first_columns(), 1000)
        from pptx import Presentation
        note = Presentation(self.decks["neurips"]).slides[2].notes_slide.notes_text_frame.text
        self.assertIn("10.8 to 15.3 points below on the same first 1,000 columns", note)

    def test_every_cns_number_sentence_in_the_notes_says_synthetic(self):
        import re
        from pptx import Presentation
        for s in Presentation(self.decks["cns"]).slides:
            for sentence in re.split(r"(?<=[.?])\s+", s.notes_slide.notes_text_frame.text):
                # A number, not a level's name such as C2, T12 or C7/T1.
                if re.search(r"(?<![A-Za-z/])\d", sentence):
                    self.assertIn("synthetic", sentence, sentence)

    def test_the_build_refuses_a_forbidden_word(self):
        deck = self.S.Deck(self.S.Venue("neurips"), DELIVERED["neurips"], False)
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
