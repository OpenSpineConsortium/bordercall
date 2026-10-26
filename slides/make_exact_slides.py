"""Five slides on naming a vertebra exactly, for a CNS talk or a NeurIPS oral, from one builder.

    python slides/make_exact_slides.py                      # both decks into slides/exact/
    python slides/make_exact_slides.py --venue neurips      # one of them
    python slides/make_exact_slides.py --refresh-equations  # set the equations again with pandoc

The owner's ask of 2026-10-26 20:45 UTC: figures and five PowerPoint slides, with the figures,
the text and the LaTeX as separate elements, styled like Benzel with inspiration from Kevin
Murphy's chapter on Bayes' rule, ready for the Congress of Neurological Surgeons or a NeurIPS
main-conference oral. One builder makes both decks from the same record, figures and words:

  neurips   a plain 16:9 deck, white, the slide's whole width
  cns       the same slides on the CNS 2026 speaker template, read from the junction deck this
            folder already holds (slides/junction_slides.pptx, built on the owner's template),
            inside the template's band and with its navy titles

Every slide is a title, pictures, text boxes and equations, each its own element and named so
in the selection pane: a figure is one picture per panel (exact_slide_figures.py, drawn at the
size the slide gives it, its caption as the picture's alternative text); every word is a text
box; every equation is native PowerPoint mathematics (Office Math, editable in PowerPoint's
equation editor) set from its LaTeX by pandoc, with the LaTeX in the element's alternative
text, and a picture of the same equation drawn by matplotlib as the fallback an application
without Office Math shows. pandoc runs only when an equation is new or changed, or with
--refresh-equations: its output is kept beside the deck (slides/exact/equations/), so a build
needs no pandoc. Every number is read from records/exact-2026-10-26/exact.json and
supplement.json, never typed. Speaker notes are written for the venue: about a minute a slide
for the CNS, two to three for a NeurIPS oral. The build refuses a deck in which any word of the
confidential work appears (make_junction_slides.FORBIDDEN), as the junction deck's build does.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import Dict, List, Optional, Sequence, Tuple, Union

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "bordercall"))
sys.path.insert(0, HERE)
from make_junction_slides import CITATION, FORBIDDEN, NAVY      # noqa: E402

RECORD = os.path.join(ROOT, "records", "exact-2026-10-26")
OUT = os.path.join(HERE, "exact")
EQDIR = os.path.join(OUT, "equations")
CNS_TEMPLATE = os.path.join(HERE, "junction_slides.pptx")
INK, BLUE, GREY, RED = (RGBColor(0x11, 0x11, 0x11), RGBColor(0x1B, 0x4F, 0x8C), RGBColor(0x59, 0x59, 0x59),
                        RGBColor(0xA4, 0x26, 0x2C))
SERIF = "Cambria"
MATH = "Cambria Math"
BYLINE = ("Gregory Schwing, MD, PhD", "General Surgery, Wayne State University School of Medicine / Detroit Medical Center")
NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
      "a14": "http://schemas.microsoft.com/office/drawing/2010/main"}
M_, A_ = "{%s}" % NS["m"], "{%s}" % NS["a"]

# Every equation on the slides, as LaTeX, by the name its element carries. Each is set twice from
# this one source: by pandoc as Office Math, and by matplotlib's mathtext as the fallback picture,
# so it uses only what both read.
EQUATIONS = {
    "problem": r"x_{1:n} = (x_1, \ldots, x_n),\quad x_i \in \mathbb{R}^{7},\qquad k \in \{1, \ldots, 23-n\}",
    "bayes": r"p(k \mid x_{1:n}) = \dfrac{p(x_{1:n} \mid k)\, p(k)}{\sum_{k'=1}^{23-n} p(x_{1:n} \mid k')\, p(k')}",
    "likelihood": (r"p(x_{1:n} \mid k) = \int \prod_{m=1}^{7} \mathcal{N}\left(x_{m,1:n} \mid s\,\mu_{m,k},\;"
                   r"\Sigma_{m,k}(s)\right)\, p(s)\, ds"),
    "selective": (r"\Pr\left(\hat{k} = k \mid \hat{p} \geq 1-\varepsilon\right) = "
                  r"\mathbb{E}\left[\hat{p} \mid \hat{p} \geq 1-\varepsilon\right] \geq 1-\varepsilon"),
    "claim": r"\Pr(\ell \geq c \mid x_{1:n}) = \sum_{j \geq c} p(\ell = j \mid x_{1:n}) \geq 0.99",
    "honest": r"\tilde{\sigma}_{m,\ell} = \sigma_{m,\ell}\sqrt{1 + 1/12},\qquad \sigma_{\mathrm{error}} = 2\ \mathrm{mm}",
}

Para = Union[str, Sequence[Tuple[str, dict]]]


# ---- the record ------------------------------------------------------------------------------------

class Numbers:
    """Every number a slide or a note says, read from the record, with its formatting."""

    def __init__(self, record: str):
        with open(os.path.join(record, "exact.json"), encoding="utf-8") as fh:
            self.d = json.load(fh)
        with open(os.path.join(record, "supplement.json"), encoding="utf-8") as fh:
            self.s = json.load(fh)
        import exact as E
        import exact_figures as EF
        self.E, self.EF = E, EF

    def both(self, n: int) -> dict:
        return self.d["widths"][str(n)]["regimes"]["both"]

    def exact(self, n: int) -> float:
        return self.both(n)["exact"]

    def sure(self, n: int) -> dict:
        return self.both(n)["selective"]["0.99"]

    def classifier(self, n: int) -> float:
        return self.d["classifier"]["both"][str(n)]["exact"]

    def cut(self, n: int, name: str) -> dict:
        return self.both(n)["claims"]["cuts"][name]

    def regions(self, n: int) -> dict:
        return self.both(n)["claims"]["regions"]

    def region_far(self, n: int) -> dict:
        return self.s["region_split"]["generator"][str(n)]["far"]

    def world(self, key: str, rule: str, n: int = 3) -> dict:
        path = next(w[1] for w in self.EF.WORLDS if w[0] == key)
        return self.EF.world_numbers(self.EF.world_cells(self.d["robust"], path, rule)[str(n)])

    def called(self, rule: str, region: str, n: int = 3, world: str = "table_specimens") -> dict:
        return self.d["robust"][world][rule][str(n)]["selective_099_by_called_region"][region]

    @property
    def columns(self) -> int:
        return int(self.d["n_columns"])

    @property
    def levels(self) -> int:
        return len(self.d["levels"])

    @property
    def nodes(self) -> int:
        return int(self.d["gh_nodes"])

    @property
    def tau(self) -> float:
        return float(self.d["synth"]["scale_sd"])

    @property
    def table_n(self) -> int:
        return int(self.E.RULES["honest"]["table_n"])

    @property
    def honest_mm(self) -> float:
        return float(self.E.RULES["honest"]["noise_mm"])


def pct(x: float, digits: int = 0) -> str:
    return "%.*f%%" % (digits, 100.0 * x)


def count(k: int) -> str:
    return "{:,}".format(int(k))


# ---- equations ----------------------------------------------------------------------------------------

def cached_omml(name: str, tex: str, refresh: bool) -> etree._Element:
    """The equation as Office Math (m:oMathPara), from the cache beside the deck when it was set from
    this same LaTeX, else from pandoc, which converts LaTeX to Office Math in a Word file."""
    path = os.path.join(EQDIR, name + ".omml.xml")
    if not refresh and os.path.exists(path):
        root = etree.parse(path).getroot()
        if root.get("tex") == tex:
            return root[0]
    if not shutil.which("pandoc"):
        raise SystemExit("equation %r is new or changed and pandoc is not installed to set it" % name)
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "e.md"), "w", encoding="utf-8") as fh:
        fh.write("$$" + tex + "$$\n")
    subprocess.run(["pandoc", os.path.join(d, "e.md"), "-o", os.path.join(d, "e.docx")], check=True)
    doc = etree.fromstring(zipfile.ZipFile(os.path.join(d, "e.docx")).read("word/document.xml"))
    shutil.rmtree(d, ignore_errors=True)
    para = doc.find(".//m:oMathPara", NS)
    if para is None:
        raise SystemExit("pandoc gave no equation for %r" % name)
    keep = etree.Element("equation", tex=tex)
    keep.append(copy.deepcopy(para))
    os.makedirs(EQDIR, exist_ok=True)
    etree.ElementTree(keep).write(path, encoding="utf-8", xml_declaration=True, pretty_print=True)
    return para


def fallback_png(name: str, tex: str, size_pt: float, eqdir: str = EQDIR) -> str:
    """The same equation as a picture at the size it is set, 300 dpi, for an application with no
    Office Math (LibreOffice among them). It is drawn afresh on every build, into `eqdir`, while the
    Office Math is read from the cache beside the committed deck."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["mathtext.fontset"] = "cm"
    os.makedirs(eqdir, exist_ok=True)
    path = os.path.join(eqdir, "%s.png" % name)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, "$" + tex + "$", fontsize=size_pt, color="#111111")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.03, transparent=True)
    plt.close(fig)
    return path


def styled_math(para: etree._Element, size_pt: float, colour: str = "111111") -> etree._Element:
    """Office Math runs in PowerPoint carry DrawingML run properties: Cambria Math at the size the
    slide sets, italic as mathematics is."""
    para = copy.deepcopy(para)
    for jc in para.iter(M_ + "jc"):
        jc.set(M_ + "val", "left")
    for r in para.iter(M_ + "r"):
        for old in r.findall(A_ + "rPr"):
            r.remove(old)
        rpr = etree.Element(A_ + "rPr", lang="en-US", i="1", sz=str(int(round(size_pt * 100))))
        fill = etree.SubElement(rpr, A_ + "solidFill")
        etree.SubElement(fill, A_ + "srgbClr", val=colour)
        etree.SubElement(rpr, A_ + "latin", typeface=MATH)
        etree.SubElement(rpr, A_ + "cs", typeface=MATH)
        t = r.find(M_ + "t")
        (t.addprevious if t is not None else r.append)(rpr)
    return para


def attr(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def add_equation(slide, name: str, x: Emu, y: Emu, size_pt: float, refresh: bool, max_w: Optional[Emu] = None,
                 eqdir: str = EQDIR):
    """The equation as one element: Office Math in a text box, with its picture as the fallback, the
    LaTeX in its alternative text. The box takes the picture's size, scaled down to `max_w`."""
    tex = EQUATIONS[name]
    png = fallback_png(name, tex, size_pt, eqdir)
    pic = slide.shapes.add_picture(png, x, y)
    if max_w is not None and pic.width > max_w:
        k = max_w / pic.width
        size_pt *= k
        pic.height = Emu(int(pic.height * k))
        pic.width = max_w
    cx, cy, rid = pic.width, pic.height, pic._element.blipFill.blip.rEmbed
    tree = pic._element.getparent()
    at = tree.index(pic._element)
    tree.remove(pic._element)
    sid = 1 + max(int(e.get("id")) for e in tree.iter("{%s}cNvPr" % NS["p"]))
    descr = attr("LaTeX: " + tex)
    xml = (
        '<mc:AlternateContent xmlns:mc="{mc}" xmlns:p="{p}" xmlns:a="{a}" xmlns:r="{r}">'
        '<mc:Choice xmlns:a14="{a14}" Requires="a14"><p:sp><p:nvSpPr>'
        '<p:cNvPr id="{sid}" name="Equation: {name}" descr="{descr}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        '<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"><a:noAutofit/></a:bodyPr>'
        '<a:lstStyle/><a:p><a:pPr algn="l"/><a14:m/><a:endParaRPr lang="en-US" sz="{sz}"/></a:p></p:txBody>'
        '</p:sp></mc:Choice><mc:Fallback><p:sp><p:nvSpPr>'
        '<p:cNvPr id="{sid}" name="Equation: {name}" descr="{descr}"/>'
        '<p:cNvSpPr txBox="1"><a:spLocks noRot="1" noChangeAspect="1" noMove="1" noResize="1" noEditPoints="1" '
        'noAdjustHandles="1" noChangeArrowheads="1" noChangeShapeType="1" noTextEdit="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/>'
        '</a:stretch></a:blipFill></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US"><a:noFill/>'
        '</a:rPr><a:t> </a:t></a:r></a:p></p:txBody></p:sp></mc:Fallback></mc:AlternateContent>'
    ).format(sid=sid, name=name, descr=descr, x=int(x), y=int(y), cx=int(cx), cy=int(cy), rid=rid,
             sz=int(round(size_pt * 100)), **NS)
    el = etree.fromstring(xml)
    el.find(".//{%s}m" % NS["a14"]).append(styled_math(cached_omml(name, tex, refresh), size_pt))
    tree.insert(at, el)
    return cx, cy


# ---- the deck ------------------------------------------------------------------------------------

class Venue:
    """Where a deck puts things: the content box's left edge and the scale from the plain deck's
    inches, the title's colour, the template and the layout."""

    def __init__(self, name: str):
        self.name = name
        if name == "cns":
            self.template, self.layout = CNS_TEMPLATE, 2
            self.x0, self.scale, self.title_colour = 1.914, 11.10 / 12.13, NAVY
        else:
            self.template, self.layout = None, 5
            self.x0, self.scale, self.title_colour = 0.60, 1.0, INK

    def x(self, inches: float) -> Emu:
        """A left edge given in the plain deck's inches, where the content box starts at 0.6."""
        return Inches(self.x0 + (inches - 0.60) * self.scale)

    def w(self, inches: float) -> Emu:
        return Inches(inches * self.scale)


class Deck:
    def __init__(self, venue: Venue, figures: str, refresh: bool, eqdir: str = EQDIR):
        self.v, self.figures, self.refresh, self.eqdir = venue, figures, refresh, eqdir
        if venue.template:
            self.prs = Presentation(venue.template)
            lst = self.prs.slides._sldIdLst
            for sid in list(lst):
                self.prs.part.drop_rel(sid.rId)
                lst.remove(sid)
        else:
            self.prs = Presentation()
            self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.layout = self.prs.slide_layouts[venue.layout]
        self.words: List[str] = []
        self.count = 0

    def slide(self, title: str):
        """A slide with the layout's own title box, set where the template sets it and anchored at its
        foot so a second line grows upward, every other placeholder removed."""
        s = self.prs.slides.add_slide(self.layout)
        self.count += 1
        t = s.shapes.title
        t.left, t.top, t.width, t.height = self.v.x(0.6), Inches(0.30), self.v.w(12.13), Inches(1.05)
        t.text_frame.text = title
        t.text_frame.word_wrap = True
        t.text_frame.vertical_anchor = MSO_ANCHOR.BOTTOM
        for para in t.text_frame.paragraphs:
            para.alignment = PP_ALIGN.LEFT
            for run in para.runs:
                run.font.size, run.font.bold, run.font.name = Pt(28), True, SERIF
                run.font.color.rgb = self.v.title_colour
        for ph in list(s.placeholders):
            if ph.placeholder_format.idx != 0:
                ph._element.getparent().remove(ph._element)
        self.words.append(title)
        return s

    def text(self, s, name: str, x: float, y: float, w: float, h: float, paras: Sequence[Para], size: float = 16,
             colour: RGBColor = INK, align=PP_ALIGN.LEFT, after: float = 6, anchor=MSO_ANCHOR.TOP, bold=False,
             line: Optional[float] = None):
        tb = s.shapes.add_textbox(self.v.x(x), Inches(y), self.v.w(w), Inches(h))
        tb.name = "Text: " + name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Inches(0.02)
        tf.margin_top = tf.margin_bottom = Inches(0.02)
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.space_after = Pt(after)
            if line:
                p.line_spacing = line
            runs = [(para, {})] if isinstance(para, str) else para
            for text, o in runs:
                r = p.add_run()
                r.text = text
                r.font.name = SERIF
                r.font.size = Pt(o.get("size", size))
                r.font.bold = o.get("bold", bold)
                r.font.italic = o.get("italic", False)
                r.font.color.rgb = o.get("colour", colour)
                self.words.append(text)
        return tb

    def stat(self, s, name: str, x: float, y: float, w: float, big: str, small: Para, colour: RGBColor = BLUE,
             big_size: float = 36, small_size: float = 14, h: float = 1.15):
        """A large number with its sentence beneath: one text box, two paragraphs."""
        small_runs = [(small, {"size": small_size})] if isinstance(small, str) else \
            [(t, dict(o, size=small_size)) for t, o in small]
        return self.text(s, "stat " + name, x, y, w, h, [[(big, {"size": big_size, "bold": True, "colour": colour})],
                                                          small_runs], after=1, line=0.95)

    def figure(self, s, name: str, x: float, y: float):
        """One panel, at the width it was drawn for (scaled with the venue), its caption as alt text."""
        png = os.path.join(self.figures, name + ".png")
        import exact_slide_figures as XS
        w = XS.SIZES[name][0]
        pic = s.shapes.add_picture(png, self.v.x(x), Inches(y), width=self.v.w(w))
        pic.name = "Figure: " + name
        with open(os.path.join(self.figures, name + ".caption.txt"), encoding="utf-8") as fh:
            caption = fh.read().strip()
        pic._element.nvPicPr.cNvPr.set("descr", caption)
        self.words.append(caption)
        return pic

    def equation(self, s, name: str, x: float, y: float, size: float, max_w: Optional[float] = None):
        self.words.append(EQUATIONS[name])
        return add_equation(s, name, self.v.x(x), Inches(y), size, self.refresh,
                            None if max_w is None else self.v.w(max_w), self.eqdir)

    def footer(self, s):
        self.text(s, "citation", 0.6, 6.92, 10.6, 0.4, [CITATION], size=9, colour=GREY, after=0)
        self.text(s, "slide number", 11.73, 6.92, 1.0, 0.4, ["%d / 5" % self.count], size=9, colour=GREY,
                  align=PP_ALIGN.RIGHT, after=0)

    def notes(self, s, text: str):
        s.notes_slide.notes_text_frame.text = text
        self.words.append(text)

    def check(self):
        """No word of the confidential work, and never the banned word for where data came from."""
        low = " ".join(self.words).lower()
        bad = [w for w in FORBIDDEN + ("prov" + "enance",) if w in low]
        if bad:
            raise SystemExit("refusing the deck: %s on a slide or in a note" % ", ".join(bad))


# ---- the five slides -------------------------------------------------------------------------------

def slide_problem(deck: Deck, N: Numbers, cns: bool):
    s = deck.slide("Can the bodies in view name a vertebra?")
    deck.figure(s, "exact_slide_view", 0.6, 1.45)
    deck.figure(s, "exact_slide_measures", 3.0, 1.55)
    x, w = 7.05, 5.68
    deck.text(s, "byline", x, 1.45, w, 0.62, [[(BYLINE[0], {"bold": True})], BYLINE[1]], size=12, colour=GREY, after=0)
    deck.text(s, "question", x, 2.35, w, 1.2,
              ["A view shows a few consecutive vertebral bodies, often with no C2 or sacrum to count from. "
               "Which levels are they?"], size=20)
    deck.equation(s, "problem", x, 3.75, 20, max_w=w)
    deck.text(s, "unknown", x, 4.35, w, 1.0,
              [[("Seven measures per body. The view's place ", {}), ("k", {"italic": True}),
                (" among the %d levels from C3 to L5 names every body in it." % N.levels, {})]], size=16)
    deck.text(s, "data", x, 5.45, w, 1.2,
              ["%s synthetic columns drawn from Panjabi's published means and spreads; every place of every "
               "column scored, so each rate below is over tens of thousands of fields." % count(N.columns)],
              size=14, colour=GREY)
    deck.footer(s)
    e1, e3 = N.exact(1), N.exact(3)
    if cns:
        deck.notes(s, (
            "Counting from C2 or the sacrum is how we name a level, and in the room the end we count from is often "
            "out of the picture. So the question is narrow: from the bodies we can see, and their measurements alone, "
            "can we say which levels they are? Each body gives seven measures a segmentation reads: the widths and "
            "depths of its upper and lower end plates, its posterior height, and the canal's width and depth. "
            "Everything here is synthetic: %s columns drawn from Panjabi's published morphometry, so the answer is "
            "about the anatomy those tables describe, not yet about our patients." % count(N.columns)))
    else:
        deck.notes(s, (
            "The task: given the measurements of n consecutive vertebral bodies, seven per body, recover which levels "
            "they are. Because the bodies are consecutive, the whole labelling is one discrete latent variable, the "
            "field's place k, with 23 minus n values over the %d levels from C3 to L5. Data come from a generative "
            "model fitted to nothing: Panjabi's published per-level means and spreads, with a patient-size factor, a "
            "within-column correlation and measurement noise. We score %s columns, every place of every column, and "
            "ask three questions: what is the best any function can do, can it say when it is right, and what can a "
            "single body say for certain. Headline numbers to come: %s named exactly from one body, %s from three."
            % (N.levels, count(N.columns), pct(e1), pct(e3))))


def slide_bayes(deck: Deck, N: Numbers, cns: bool):
    s = deck.slide("Bayes' rule over every place is the ceiling")
    x, w = 0.6, 5.75
    y = 1.5 + deck.equation(s, "bayes", x, 1.5, 24, max_w=w)[1] / 914400.0
    deck.text(s, "in words", x, y + 0.05, w, 0.5,
              [[("posterior", {"colour": BLUE, "bold": True}), ("  \u221d  likelihood  \u00d7  ", {}),
                ("prior", {"colour": GREY, "bold": True}), (",  over all 23 \u2212 n places", {})]], size=18)
    y += 0.75
    y += deck.equation(s, "likelihood", x, y, 20, max_w=w)[1] / 914400.0
    deck.text(s, "how", x, y + 0.2, w, 6.8 - y - 0.2, [
        "Every place is scored; nothing is fitted.",
        [("Given the patient's size ", {}), ("s", {"italic": True}),
         (", each measure's values are Gaussian with a diagonal-plus-rank-one covariance, inverted in closed form; ", {}),
         ("log s", {"italic": True}), (" ~ N(0, %.2f\u00b2) is integrated by %d-node Gauss\u2013Hermite quadrature."
                                       % (N.tau, N.nodes), {})],
        "So it is the Bayes rule for this generator: no formula or network on the same measures names more "
        "fields correctly on average."], size=15, after=8)
    deck.figure(s, "exact_slide_posterior", 6.45, 1.5)
    deck.footer(s)
    if cns:
        deck.notes(s, (
            "The method is the oldest rule in probability. Before looking, every level is equally likely, the grey "
            "row. Each candidate placement of the bodies predicts what their measurements should be; Bayes' rule "
            "weighs the placements by how well they predict what we measured. One body leaves the answer spread "
            "over the mid-thoracic spine; three bodies concentrate it on the true level; nine settle it. Nothing is "
            "trained, so no other formula or network on these measures can do better on average."))
    else:
        deck.notes(s, (
            "Exact inference by enumeration. For a field of n bodies there are 23 minus n places. Given the "
            "patient's size s, each measure's n values are jointly Gaussian with covariance Delta plus u u-transpose, "
            "so the likelihood needs no matrix inverse (Sherman-Morrison); measures are independent given s; log s is "
            "Gaussian with SD %.2f and is integrated by %d-node Gauss-Hermite quadrature, whose error we measured. "
            "Under a uniform prior the posterior is the normalised likelihood, shown right for one column chosen by a "
            "stated rule: the median three-body posterior at T12 among %s. Because this is the generator's own "
            "posterior it is the Bayes-optimal classifier: a network can match it, never beat it, which turns "
            "'can a network do this' into 'how far is this ceiling from one'." % (N.tau, N.nodes, count(N.columns))))


def slide_ceiling(deck: Deck, N: Numbers, cns: bool):
    e3, sure3, sure9, c3 = N.exact(3), N.sure(3), N.sure(9), N.classifier(3)
    s = deck.slide("Three bodies name %s exactly; when sure, the name is right %s"
                   % (pct(e3), pct(sure3["precision"], 1)))
    deck.figure(s, "exact_slide_ceiling", 0.6, 1.45)
    deck.figure(s, "exact_slide_calibration", 6.25, 1.5)
    x, w = 10.05, 2.68
    deck.stat(s, "three bodies", x, 1.5, w, pct(e3, 1), "of three-body fields named exactly (a fitted classifier: %s)"
              % pct(c3, 1))
    deck.stat(s, "precision", x, 2.85, w, pct(sure3["precision"], 2),
              "of names given at posterior 0.99 right (%s wrong of %s)" % (count(sure3["errors"]), count(sure3["n_answered"])))
    deck.stat(s, "nine bodies", x, 4.2, w, pct(N.exact(9), 1), "named exactly from nine bodies")
    deck.equation(s, "selective", 0.6, 5.72, 18, max_w=6.6)
    deck.text(s, "guarantee", 7.45, 5.6, 5.28, 1.2,
              [[("Answer only when the posterior ", {}), ("p\u0302", {"italic": True}),
                (" reaches 0.99, and the name is right at least 99% of the times it is given, while the generator "
                 "is the truth.", {})]], size=14)
    deck.footer(s)
    if cns:
        deck.notes(s, (
            "With one body in view the rule names %s of fields exactly; with three, %s; with nine, %s. A trained "
            "classifier on the same measures reaches %s from three. More useful at the table: the rule says how "
            "sure it is, and it is honest. When it says 99 per cent, it is right %s of the time: %s wrong of %s. "
            "When it is not sure, it says so, and we count."
            % (pct(N.exact(1)), pct(e3), pct(N.exact(9)), pct(c3), pct(sure3["precision"], 1),
               count(sure3["errors"]), count(sure3["n_answered"]))))
    else:
        deck.notes(s, (
            "Left: exact-match accuracy of the Bayes rule against the number of bodies, %s at one, %s at three, %s at "
            "nine; the crosses are a linear classifier fitted on separate synthetic columns, %s to %s points below on "
            "the same columns. Dashed: the share answered under selective prediction at posterior 0.99, %s at three "
            "bodies and %s at nine. Right: calibration on held-out draws, error predicted against error counted, on "
            "the diagonal down to one in ten thousand. The guarantee is one line: among answers with max posterior at "
            "least 1 minus epsilon, accuracy equals the mean posterior, hence at least 1 minus epsilon, and it holds "
            "within any group chosen by the measurements, not within groups chosen by the truth. Observed: %s at "
            "three bodies, %s at nine."
            % (pct(N.exact(1), 1), pct(e3, 1), pct(N.exact(9), 1),
               "%.1f" % (100 * (N.exact(1) - N.classifier(1))), "%.1f" % (100 * (N.exact(9) - N.classifier(9))),
               pct(sure3["answered"], 1), pct(sure9["answered"], 1), pct(sure3["precision"], 2),
               pct(sure9["precision"], 2))))


def slide_claims(deck: Deck, N: Numbers, cns: bool):
    s = deck.slide("One body tells its region and its side of C7/T1, rarely of T12/L1")
    deck.figure(s, "exact_slide_claims", 0.6, 1.45)
    ct, tl, tl9, reg, far = N.cut(1, "C7/T1"), N.cut(1, "T12/L1"), N.cut(9, "T12/L1"), N.regions(1), N.region_far(1)
    x, w = 6.25, 6.48
    deck.equation(s, "claim", x, 1.6, 18, max_w=w)
    deck.text(s, "claim rule", x, 2.25, w, 0.8,
              ["A border claim sums the same posterior, so a claim made at 0.99 is right at least 99% of the times it is "
               "made."], size=14)
    sw, gap = 3.1, 0.28
    deck.stat(s, "C7/T1", x, 3.2, sw, pct(ct["decided_within_two"]),
              "of single bodies within two levels of C7/T1 say which side; right %s (%s wrong of %s)"
              % (pct(ct["precision_within_two"], 2), count(ct["errors_within_two"]), count(ct["n_decided_within_two"])),
              h=1.5)
    deck.stat(s, "T12/L1", x + sw + gap, 3.2, sw, pct(tl["decided_within_two"]),
              "at T12/L1, right %s (%s wrong of %s): not near-certain"
              % (pct(tl["precision_within_two"], 1), count(tl["errors_within_two"]), count(tl["n_decided_within_two"])),
              colour=RED, h=1.5)
    deck.stat(s, "region", x, 4.85, sw, pct(reg["decided"]),
              "of single bodies say their region; right %s (%s wrong of %s), only %s of them far from both junctions"
              % (pct(1 - reg["errors"] / reg["n_decided"], 2), count(reg["errors"]), count(reg["n_decided"]),
                 count(far["wrong"])), h=1.5)
    deck.stat(s, "nine bodies", x + sw + gap, 4.85, sw, pct(tl9["decided_within_two"]),
              "near T12/L1 say which side from nine bodies (%s wrong of %s)"
              % (count(tl9["errors_within_two"]), count(tl9["n_decided_within_two"])), h=1.5)
    deck.footer(s)
    if cns:
        deck.notes(s, (
            "Short of a name, what can one body say for certain? Two things. Its region, cervical, thoracic or "
            "lumbar, for %s of bodies, wrong %s times in %s. And which side of the cervicothoracic junction it is "
            "on: near C7/T1 a single body says so %s of the time, right %s. The thoracolumbar junction is the hard "
            "one: a single body near T12/L1 commits only %s of the time and is right %s, which is not good enough to "
            "act on. Nine bodies say it for %s." % (
                pct(reg["decided"]), count(reg["errors"]), count(reg["n_decided"]), pct(ct["decided_within_two"]),
                pct(ct["precision_within_two"], 2), pct(tl["decided_within_two"]), pct(tl["precision_within_two"], 1),
                pct(tl9["decided_within_two"]))))
    else:
        deck.notes(s, (
            "Weaker statements inherit the guarantee: P(level at or below c) is a sum of the same posterior, so a "
            "claim made at 0.99 is right at least 99 per cent of the time, over all fields. The figure conditions on "
            "the truth, fields whose middle body lies within two levels of each border, where no guarantee applies, "
            "so these are measurements. One body: the side of C7/T1 for %s, precision %s; the side of T12/L1 for "
            "only %s, precision %s, below the nominal level because the group is chosen by the truth; the region for "
            "%s of all single bodies, %s wrong of %s, %s of them far from both junctions. Nine bodies settle T12/L1 "
            "for %s." % (
                pct(ct["decided_within_two"], 1), pct(ct["precision_within_two"], 2), pct(tl["decided_within_two"], 1),
                pct(tl["precision_within_two"], 2), pct(reg["decided"], 1), count(reg["errors"]),
                count(reg["n_decided"]), count(far["wrong"]), pct(tl9["decided_within_two"], 1))))


def slide_robust(deck: Deck, N: Numbers, cns: bool):
    s = deck.slide("The weak point is the table, not the mathematics")
    deck.figure(s, "exact_slide_robust", 0.6, 1.5)
    gen, spec_n, spec_h = N.world("none", "nominal"), N.world("table_specimens", "nominal"), N.world("table_specimens", "honest")
    err3_n, err3_h = N.world("noise_mm=3", "nominal"), N.world("noise_mm=3", "honest")
    lumbar = N.called("honest", "lumbar")
    x, w = 8.2, 4.53
    deck.stat(s, "twelve spines", x, 1.5, w, pct(spec_n["precision_099"], 1),
              "of names at 0.99 right when the rule's table is estimated from %d spines, as Panjabi's tables are"
              % N.table_n, colour=RED, h=1.25)
    deck.stat(s, "widened", x, 2.95, w, pct(spec_h["precision_099"], 1),
              "with spreads widened and %g mm of error, but %s of fields named, not %s, and lumbar names right %s"
              % (N.honest_mm, pct(spec_h["answered_099"], 1), pct(spec_n["answered_099"], 1),
                 pct(lumbar["precision"], 1)), h=1.4)
    deck.equation(s, "honest", x, 4.55, 16, max_w=w)
    deck.text(s, "next", 0.6, 5.62, 12.13, 1.2, [
        [("Next: ", {"bold": True}),
         ("measure the table on full-spine CTs counted from C2; carry a real series' prior over places; add the "
          "anomalous columns (four or six lumbar bodies, a thirteenth rib-bearing body) as places of their own.", {})]],
        size=16)
    deck.footer(s)
    if cns:
        deck.notes(s, (
            "Where can this go wrong? Not in the arithmetic: it is exact for the anatomy it assumes. The weak point "
            "is the anatomy table itself. Panjabi measured %d spines; a rule built on a table that small, scored on "
            "spines that differ from it, is right %s of the time when it says 99, not 99. Widening its spreads "
            "honestly restores %s but it then commits on %s of fields, and lumbar names are right %s. So the next "
            "step is a table measured on full-spine CTs, counted from C2, with the anomalous spines in it."
            % (N.table_n, pct(spec_n["precision_099"], 1), pct(spec_h["precision_099"], 1),
               pct(spec_h["answered_099"], 1), pct(lumbar["precision"], 1))))
    else:
        deck.notes(s, (
            "Robustness, three bodies. Under the generator the printed-table rule is right %s at 0.99. When the "
            "rule's table is itself estimated from %d specimens, the setting Panjabi's tables come from, precision "
            "drops to %s; with 3 mm of measurement error, %s. The fix that needs no new data inflates each spread by "
            "the root of 1 plus 1 over %d and assumes %g mm of error: precision returns to %s (and %s at 3 mm), at "
            "the cost of coverage, %s answered instead of %s, and unevenly, lumbar names %s. The posterior is only as "
            "good as the table, so the open problems are a table from full-spine CT counted from C2, a prior from a "
            "real series, and anomalous phenotypes as additional places." % (
                pct(gen["precision_099"], 2), N.table_n, pct(spec_n["precision_099"], 1),
                pct(err3_n["precision_099"], 1), N.table_n, N.honest_mm, pct(spec_h["precision_099"], 1),
                pct(err3_h["precision_099"], 1), pct(spec_h["answered_099"], 1), pct(spec_n["answered_099"], 1),
                pct(lumbar["precision"], 1))))


SLIDES = (slide_problem, slide_bayes, slide_ceiling, slide_claims, slide_robust)


def build(venue: str, out: str, record: str = RECORD, figures: Optional[str] = None, refresh: bool = False,
          eqdir: Optional[str] = None) -> str:
    """One deck. The equation pictures go beside it (`<outdir>/equations/`) unless `eqdir` says where."""
    figures = figures or os.path.join(record, "slide-figures")
    eqdir = eqdir or os.path.join(os.path.dirname(os.path.abspath(out)), "equations")
    N = Numbers(record)
    deck = Deck(Venue(venue), figures, refresh, eqdir)
    for make in SLIDES:
        make(deck, N, venue == "cns")
    deck.check()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    deck.prs.save(out)
    return out


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--venue", choices=("neurips", "cns", "both"), default="both")
    ap.add_argument("--outdir", default=OUT)
    ap.add_argument("--record", default=RECORD)
    ap.add_argument("--figures", default=None, help="the slide figures (default: <record>/slide-figures)")
    ap.add_argument("--refresh-equations", action="store_true", dest="refresh")
    a = ap.parse_args(argv)
    for v in (("neurips", "cns") if a.venue == "both" else (a.venue,)):
        print("wrote", build(v, os.path.join(a.outdir, "exact_slides_%s.pptx" % v), a.record, a.figures, a.refresh))
    return 0


if __name__ == "__main__":
    sys.exit(main())
