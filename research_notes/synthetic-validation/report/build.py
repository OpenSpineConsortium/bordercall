"""Build the private report page from the note's README (its tables already checked against the
records by tables.py --check) and its committed figures. Nothing here computes a number; the four
tiles at the top repeat the README's answer and are changed by hand with it.

    python3 report/build.py <branch or commit>     # from the note's folder, or anywhere

writes report/index.html and copies the figures beside it (both ignored by git); the page is then
published to the owner's private artifact, https://claude.ai/artifact/H82v6B1drWmpjTJhrWrLxv, by a
session's Artifact tool with that url, so the link stays the same."""
import html
import os
import re
import shutil
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(OUT)
COMMIT = sys.argv[1] if len(sys.argv) > 1 else "uncommitted"

readme = open(os.path.join(NOTE, "README.md")).read()


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
    s = s.replace(" - ", " &minus; ") if False else s
    return s


NUM = re.compile(r"^[\s\-+0-9.,/%()<>=:;a-zA-Z ]*[0-9][\s\-+0-9.,/%()]*$")


def table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
    head, align, body = rows[0], rows[1], rows[2:]
    right = [a.endswith(":") for a in align]
    h = ["<div class='tbl'><table><thead><tr>"]
    for i, c in enumerate(head):
        h.append("<th%s>%s</th>" % (" class='n'" if right[i] else "", inline(c)))
    h.append("</tr></thead><tbody>")
    for r in body:
        lead = len(r[0]) - len(r[0].lstrip()) if r else 0
        h.append("<tr>")
        for i, c in enumerate(r):
            cls = "n" if i < len(right) and right[i] else ""
            raw = lines[2 + body.index(r)].strip().strip("|").split("|")[i] if i == 0 else c
            indent = len(raw) - len(raw.lstrip(" ")) - 1 if i == 0 else 0
            style = " style='padding-left:%.1fem'" % (0.6 + 0.9 * (indent // 2)) if indent >= 2 else ""
            h.append("<td%s%s>%s</td>" % (" class='%s'" % cls if cls else "", style, inline(c)))
        h.append("</tr>")
    h.append("</tbody></table></div>")
    return "".join(h)


def blocks(body):
    """The README's markdown: paragraphs, lists, tables, code and the notes under tables."""
    out, para, lst, code, tbl = [], [], [], None, []
    marked = [False]
    lines = body.split("\n")

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(x.strip() for x in para)))
            para.clear()

    def flush_list():
        if lst:
            tag = "ol" if lst[0][0] == "ol" else "ul"
            items = "".join("<li>%s</li>" % inline(t) for _, t in lst)
            out.append("<%s>%s</%s>" % (tag, items, tag))
            lst.clear()

    def flush_tbl():
        if tbl:
            out.append(table(tbl))
            tbl.clear()

    for l in lines:
        if code is not None:
            if l.startswith("```"):
                out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code)))
                code = None
            else:
                code.append(l)
            continue
        if l.startswith("```"):
            flush_para(); flush_list(); flush_tbl(); code = []; continue
        if l.startswith("<!--"):
            flush_para(); flush_list(); flush_tbl()
            marked[0] = l.startswith("<!-- table")
            continue
        if l.startswith("|"):
            flush_para(); flush_list(); tbl.append(l); continue
        flush_tbl()
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
        if marked[0]:
            out.append("<p class='tnote'>%s</p>" % inline(l.strip())); continue
        para.append(l)
    flush_para(); flush_list(); flush_tbl()
    return "\n".join(out)


def caption(name):
    return open(os.path.join(NOTE, "figures", name + ".caption.txt")).read().strip()


def figure(name, alt):
    return ("<figure><img src='figures/%s.png' alt='%s' loading='lazy'>"
            "<figcaption><span class='fid'>%s</span> %s</figcaption></figure>"
            % (name, html.escape(alt, quote=True), name, inline(caption(name))))


os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
for f in os.listdir(os.path.join(NOTE, "figures")):
    if f.endswith(".png"):
        shutil.copy(os.path.join(NOTE, "figures", f), os.path.join(OUT, "figures", f))

intro = S["_intro"]
snapshot = re.search(r"\*\*What the snapshot is\.\*\*(.*)", intro, re.S).group(1)

PAGE = [
    ("summary", "The answer", [S["The answer"]], []),
    ("state-space", "State space", [S["State space"]], [("fig4_state_space", "State space, one axis at a time and the grid")]),
    ("naming", "Naming across the state space", [S["Naming across the state space"]], [("fig5_naming", "Exact naming at points of the state space")]),
    ("quality", "Population quality and curation", [S["Quality and curation"]], [("fig7_quality", "Quality indicators by measure and level")]),
    ("compared", "What was compared", ["**What the snapshot is.**" + snapshot, S["What was compared"]], []),
    ("means", "Against the published means", [S["Means"]], [("fig1_means", "Panjabi's means against the pooled papers")]),
    ("spread", "Spread", [S["Spread"]], [("fig2_spread", "The synthetic SDs against the papers'")]),
    ("structure", "Structure", [S["Structure"]], [("fig3_structure", "Correlations and the sexes' differences")]),
    ("power", "Power, rerun", [S["Power, rerun"]], []),
    ("gold", "What gold persons can test", [S["What gold persons can test"]], [("fig6_power", "The spread between series, part C and the gold persons")]),
    ("assumptions", "The assumptions beside the papers", [S["The assumptions beside the papers"]], [("fig8_assumptions", "The generator's errors and prevalences beside the papers'")]),
    ("renders", "Renders", [S["Figures and renders"].split("\n- ")[0]], [("render1_axial", "L3 from above"), ("render2_column", "The lumbar column from in front"), ("render3_solid", "The column as solids")]),
    ("limits", "What this does not do", [S["What this note does not do"]], []),
    ("reproduce", "Reproduce", [S["Run it"]], []),
]


css = open(os.path.join(OUT, "style.css")).read()
nav = "".join("<a href='#%s'>%s</a>" % (k, html.escape(t)) for k, t, _, _ in PAGE)
body = []
for key, title, texts, figs in PAGE:
    body.append("<section id='%s'><h2>%s</h2>" % (key, html.escape(title)))
    for t in texts:
        body.append(blocks(t))
    for name, alt in figs:
        body.append(figure(name, alt))
    body.append("</section>")

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
<p class="eyebrow">bordercall, research_notes/synthetic-validation &middot; draft pull request 29 &middot; confidential</p>
<h1>The synthetic spines against the published populations</h1>
<p class="lede">schwingcheck's generator draws whole spines from Panjabi's twelve cadavers. This report holds that population to the 39 papers of the clinical reread, explores the generator's state space, scores every synthetic vertebra against quality indicators drawn from the measures' own geometry, and reruns the power calculations on the papers' own series. Everything is synthetic but the papers' numbers: no grid, no WSU data, no scan, and a synthetic result raises no evidence tier.</p>
<div class="tiles">%s</div>
<p class="meta">The papers are the reread's series at its commit 401aaee; What was compared says what that snapshot fixed.</p>
<p class="meta">Every table below is the note's README on bordercall's branch or commit <code>%s</code>, which <code>tables.py --check</code> holds to the records one run writes; every figure is drawn by the note's committed code, and the page by report/build.py.</p>
</div></header>
<nav class="toc"><div class="wrap">%s</div></nav>
<main class="wrap">%s</main>
<footer class="wrap"><p>Private to the owner. bordercall's research notes stay in bordercall; this page is a view of research_notes/synthetic-validation/README.md and figures/ on the branch or commit above.</p></footer>
""" % (css, tile_html, COMMIT, nav, "\n".join(body))

open(os.path.join(OUT, "index.html"), "w").write(page)
print("wrote", os.path.join(OUT, "index.html"), len(page))
