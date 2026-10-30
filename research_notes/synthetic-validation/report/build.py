"""Build the private report page as figures with reading notes (the owner's ask of 2026-10-29, 22:58
UTC: plots with short notes on how to read them, not a wall of text). Every figure of figures/ is
shown with its caption, two to four sentences on how to read it and two or three on what it shows,
the numbers quoted from the README's answer; the tables stay in the README, where tables.py --check
holds them to the records. Nothing here computes a number; the four tiles at the top repeat the
README's answer, the first part's, and are changed by hand with it.

    python3 report/build.py <branch or commit>     # from the note's folder, or anywhere

reads report/notes.json, one entry a figure (how_to_read, what_it_shows), refusing a figure of
figures/ that has no note, writes report/index.html and copies the figures beside it (both ignored
by git); the page is then published to the owner's private artifact by a session's Artifact tool
with that url, so the link stays the same: https://claude.ai/artifact/VXV7NqZTv6gG1f4cXGhgd2 since
the strata (2026-10-30), published from the symphony_3 account with the figures as its files. The
two earlier links belong to other accounts, which a session of this one cannot republish, and show
the page as it was: https://claude.ai/artifact/NQSUQ6c1Edzra7bW6CWJx2 (the second part, 2026-10-29,
symphony_2) and https://claude.ai/artifact/H82v6B1drWmpjTJhrWrLxv (the first part). A session of
another account publishes a new link and records it here."""
import html
import json
import os
import re
import shutil
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(OUT)
COMMIT = sys.argv[1] if len(sys.argv) > 1 else "uncommitted"

readme = open(os.path.join(NOTE, "README.md")).read()
notes = json.load(open(os.path.join(OUT, "notes.json"), encoding="utf-8"))


def sections(text):
    """Heading -> body, for the README's level-two sections."""
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    out = {"_intro": parts[0]}
    for i in range(1, len(parts), 2):
        out[parts[i].strip()] = parts[i + 1]
    return out


S = sections(readme)


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return s


def blocks(body):
    """The README's markdown for the two prose sections kept: paragraphs, lists and code; a marked
    table is left out, since the tables live in the README."""
    out, para, lst, code = [], [], [], None
    skip = False

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(x.strip() for x in para)))
            para.clear()

    def flush_list():
        if lst:
            tag = "ol" if lst[0][0] == "ol" else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(t) for _, t in lst), tag))
            lst.clear()

    for l in body.split("\n"):
        if code is not None:
            if l.startswith("```"):
                out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code)))
                code = None
            else:
                code.append(l)
            continue
        if l.startswith("<!-- table"):
            flush_para(); flush_list(); skip = True; continue
        if l.startswith("<!-- end"):
            skip = False; continue
        if skip:
            continue
        if l.startswith("```"):
            flush_para(); flush_list(); code = []; continue
        if not l.strip():
            flush_para(); flush_list(); continue
        m = re.match(r"^(\d+)\.\s+(.*)$", l)
        b = re.match(r"^-\s+(.*)$", l)
        if m:
            flush_para(); lst.append(("ol", m.group(2))); continue
        if b:
            flush_para(); lst.append(("ul", b.group(1))); continue
        if lst and l.startswith("  "):
            lst[-1] = (lst[-1][0], lst[-1][1] + " " + l.strip()); continue
        para.append(l)
    flush_para(); flush_list()
    return "\n".join(out)


def caption(name):
    return open(os.path.join(NOTE, "figures", name + ".caption.txt")).read().strip()


def figure(name, alt):
    note = notes[name]
    return ("<figure><img src='figures/%s.png' alt='%s' loading='lazy'>"
            "<figcaption><span class='fid'>%s</span> %s</figcaption></figure>"
            "<div class='note'><p><span class='lead'>How to read it.</span> %s</p>"
            "<p><span class='lead'>What it shows.</span> %s</p></div>"
            % (name, html.escape(alt, quote=True), name, inline(caption(name)),
               inline(note["how_to_read"].strip()), inline(note["what_it_shows"].strip())))


os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
figures_present = set()
for f in os.listdir(os.path.join(NOTE, "figures")):
    if f.endswith(".png"):
        shutil.copy(os.path.join(NOTE, "figures", f), os.path.join(OUT, "figures", f))
        figures_present.add(f[:-4])

PAGE = [
    ("validation", "The synthetic population against the papers", [
        ("fig1_means", "Panjabi's means against the pooled papers"),
        ("fig2_spread", "The synthetic SDs against the papers'"),
        ("fig3_structure", "Correlations and the sexes' differences")]),
    ("state-space", "The state space and naming across it", [
        ("fig4_state_space", "State space, one axis at a time and the grid"),
        ("fig5_naming", "Exact naming at points of the state space")]),
    ("quality", "Population quality", [("fig7_quality", "Quality indicators by measure and level")]),
    ("power", "Power and the gold persons", [("fig6_power", "The spread between series, part C and the gold persons")]),
    ("assumptions", "The assumptions beside the papers", [("fig8_assumptions", "The generator's errors and prevalences beside the papers'")]),
    ("measures", "Every measure of the reread", [
        ("fig9_tables", "Every measure of the reread and the three tables"),
        ("fig11_state_space_all", "The state space read on the three tables"),
        ("fig10_relations", "Quality indicators on every measure"),
        ("fig12_naming_measures", "Exact naming by the rule built on more measures"),
        ("fig13_spread_all", "The spread between published series on every measure")]),
    ("strata", "Every paper its own population", [("fig14_strata", "The rule built on the other papers, scored on each")]),
    ("renders", "Renders", [
        ("render1_axial", "L3 from above"),
        ("render2_column", "The lumbar column from in front"),
        ("render3_solid", "The column as solids")]),
]
PROSE = [("limits", "What this does not do", S["What this note does not do"]), ("reproduce", "Reproduce", S["Run it"])]

listed = {name for _, _, figs in PAGE for name, _ in figs}
missing = sorted(figures_present - listed)
if missing:
    raise SystemExit("figures with no place on the page: %s" % ", ".join(missing))
unnoted = sorted(n for n in listed if n not in notes)
if unnoted:
    raise SystemExit("figures with no note in report/notes.json: %s" % ", ".join(unnoted))

css = open(os.path.join(OUT, "style.css")).read()
nav = "".join("<a href='#%s'>%s</a>" % (k, html.escape(t)) for k, t, _ in PAGE) + \
      "".join("<a href='#%s'>%s</a>" % (k, html.escape(t)) for k, t, _ in PROSE)
body = []
for key, title, figs in PAGE:
    body.append("<section id='%s'><h2>%s</h2>" % (key, html.escape(title)))
    for name, alt in figs:
        body.append(figure(name, alt))
    body.append("</section>")
for key, title, text in PROSE:
    body.append("<section id='%s'><h2>%s</h2>%s</section>" % (key, html.escape(title), blocks(text)))

tiles = [
    ("SD ratio, true anatomy", "1.71", "0.98", "generator, then the nearest point; 1.00 is the papers'"),
    ("Vertebrae failing an indicator", "42%", "7%", "any indicator, the generator's floor included"),
    ("One body named exactly", "47.5%", "57.1%", "the exact rule on the seven SPINEPS measures"),
    ("Spread between papers", "0.83", "SD", "of Panjabi's, over 57 cells; part B read 0.39"),
]
tile_html = "".join(
    "<div class='tile'><div class='tl'>%s</div><div class='tv'><span>%s</span>%s</div><div class='tn'>%s</div></div>"
    % (l, a, ("<span class='arrow'>to</span><span>%s</span>" % b) if b != "SD" else "<span class='unit'>SD</span>", n)
    for l, a, b, n in tiles)

page = """<title>SchwingCheck Population Report</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>%s</style>
<header class="top"><div class="wrap">
<p class="eyebrow">bordercall, research_notes/synthetic-validation &middot; pull requests 29 and 38 &middot; confidential</p>
<h1>The synthetic spines against the published populations</h1>
<p class="lede">schwingcheck's generator draws whole spines from Panjabi's twelve cadavers. These figures hold that population to the 39 papers of the clinical reread, explore the generator's state space, score every synthetic vertebra against quality indicators, rerun the power calculations on the papers' own series, read every measure of the reread, and keep each paper a population of its own. Everything is synthetic but the papers' numbers: no grid, no WSU data, no scan, and a synthetic result raises no evidence tier.</p>
<div class="tiles">%s</div>
<p class="meta">Each figure carries its caption, a note on how to read it and a note on what it shows, the numbers quoted from the note's answer. The tables are in the README, held to the records by <code>tables.py --check</code>; the papers are the reread's series at its commit 401aaee, the second part reads the whole reread at main 6409164, and the strata are read on the same snapshot.</p>
<p class="meta">Every figure is drawn by the note's committed code from the records on bordercall's branch or commit <code>%s</code>, and the page by report/build.py.</p>
</div></header>
<nav class="toc"><div class="wrap">%s</div></nav>
<main class="wrap">%s</main>
<footer class="wrap"><p>Private to the owner. bordercall's research notes stay in bordercall; this page is a view of research_notes/synthetic-validation/figures/ and README.md on the branch or commit above.</p></footer>
""" % (css, tile_html, COMMIT, nav, "\n".join(body))

open(os.path.join(OUT, "index.html"), "w").write(page)
print("wrote", os.path.join(OUT, "index.html"), len(page))
