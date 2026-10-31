"""Build the private report page for a machine-learning reader (the owner's ask of 2026-10-30, 02:13
UTC: "i am a machine learning specialist so i need things to be presented in a bayesian or ML natural
way, you can keep these for like stats people but make a CS friendly report"). The page says the same
things as report/build.py's, in the words a classifier's evaluation is written in: the task, the model,
the training and test data, the protocol, the metrics, the result; then the figures that matter to that
reader, each with a note in the same words. Nothing here computes a number: the result table is read from
records/select/select.json, and every quoted number is the README's.

    python3 report/build_ml.py <branch or commit>     # from the note's folder, or anywhere

reads report/ml_notes.json (the prose and one note a figure), writes report/ml.html and copies the
figures beside it (both ignored by git); the page is then published to the owner's private artifact by
a session's Artifact tool, with the figures as its files, under a link of its own beside the stats
page's: https://claude.ai/artifact/13LehVRhuCUB4r4hNC2b3H (2026-10-30, symphony_3). A session of
another account publishes a new link and records it here."""
import html
import json
import os
import shutil
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.dirname(OUT)
COMMIT = sys.argv[1] if len(sys.argv) > 1 else "uncommitted"

notes = json.load(open(os.path.join(OUT, "ml_notes.json"), encoding="utf-8"))
select = json.load(open(os.path.join(NOTE, "records", "select", "select.json"), encoding="utf-8"))
sys.path.insert(0, OUT)
from markup import inline, blocks, caption  # noqa: E402  (the stats page's markdown helpers)


def figure(name, alt):
    note = notes["figures"][name]
    return ("<figure><img src='figures/%s.png' alt='%s' loading='lazy'>"
            "<figcaption><span class='fid'>%s</span> %s</figcaption></figure>"
            "<div class='note'><p><span class='lead'>How to read it.</span> %s</p>"
            "<p><span class='lead'>What it shows.</span> %s</p></div>"
            % (name, html.escape(alt, quote=True), name, inline(caption(name)),
               inline(note["how_to_read"].strip()), inline(note["what_it_shows"].strip())))


def result_table(order):
    """The candidates on the held-out populations, from the selection's record: one row a candidate
    and width, the mean over the populations with its SE."""
    rows = []
    for w in select["sizes"]["widths"]:
        for c in order:
            r = next(x for x in select["summary"] if x["candidate"] == c and x["width"] == w)
            d = "" if c in ("plain", "own table") else "%+.3f (%.3f)" % (-r["log_score_vs_plain"], r["log_score_vs_plain_se"])
            wins = "" if c in ("plain", "own table") else "%d / %d" % (r["wins_vs_plain"], r["populations"])
            rows.append("<tr><td>%s</td><td class='n'>%d</td><td class='n'>%.3f (%.3f)</td><td class='n'>%s</td><td class='n'>%s</td>"
                        "<td class='n'>%.1f (%.1f)</td><td class='n'>%.3f</td><td class='n'>%.1f%%</td><td class='n'>%s</td></tr>"
                        % (html.escape(c), w, -r["log_score_mean"], r["log_score_se"] or 0.0, d, wins,
                           100 * r["exact_mean"], 100 * (r["exact_se"] or 0.0), r["ece_pooled"], 100 * r["answered_mean"],
                           ("%.0f%%" % (100 * r["precision_pooled"])) if r["precision_pooled"] is not None else "-"))
    head = ("<tr><th>candidate</th><th class='n'>bodies</th><th class='n'>NLL, nats (SE)</th><th class='n'>NLL minus plain (SE)</th>"
            "<th class='n'>folds won vs plain</th><th class='n'>top-1 accuracy % (SE)</th><th class='n'>ECE</th>"
            "<th class='n'>coverage at 0.99</th><th class='n'>precision at 0.99</th></tr>")
    return "<div class='tbl'><table><thead>%s</thead><tbody>%s</tbody></table></div>" % (head, "".join(rows))


def glossary():
    rows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (inline(a), inline(b)) for a, b in notes["glossary"])
    return "<div class='tbl'><table><thead><tr><th>the stats page says</th><th>which means, in ML terms</th></tr></thead><tbody>%s</tbody></table></div>" % rows


os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
for f in os.listdir(os.path.join(NOTE, "figures")):
    if f.endswith(".png"):
        shutil.copy(os.path.join(NOTE, "figures", f), os.path.join(OUT, "figures", f))

PAGE = [
    ("task", "The task, the model and the data", blocks(notes["task"])),
    ("protocol", "Evaluation protocol", blocks(notes["protocol"])),
    ("result", "Result: the candidates on held-out populations", blocks(notes["result"]) +
     result_table(["own table"] + list(select.get("core", select["candidates"]))) +
     figure("fig15_select", "Candidates on the held-out populations, calibration, the two knobs swept, and the winner against plain")),
    ("exclusion", "Dropping a training population, scored held out", blocks(notes["exclusion"]) +
     result_table(["plain", "tempered"] + list(select["exclusion"])) +
     figure("fig16_exclusion", "Each exclusion candidate against plain, per population, and calibration")),
    ("project", "Covariates, and where this sits in the project", blocks(notes["project"]) +
     figure("fig17_covariates", "Sex, age and body-size effects per measure, and each predicted from the other")),
    ("sex", "Naming told the patient's sex", blocks(notes["sex_naming"]) +
     figure("fig18_sex_naming", "Log-score gain from conditioning on sex, synthetic and held out by paper")),
    ("bounds", "Bounds for a generative model", blocks(notes["bounds"]) +
     figure("fig19_bounds", "The card's interval for an unseen domain, and each cohort's pass rates against the step threshold")),
    ("gold3", "Real CTs on the card", blocks(notes["gold3"]) +
     figure("fig20_gold3", "Two real cohorts on the card: pass rates by feature family, the sex effect, the engine's pedicle width, the age slope")),
    ("shift", "Distribution shift, measured", figure("fig14_strata", "Each paper held out: the rule built on the others, scored on it")),
    ("features", "Features and robustness", figure("fig12_naming_measures", "Accuracy against the number of measures the rule reads") +
     figure("fig5_naming", "Accuracy across the generator's hyperparameters")),
    ("simulator", "Is the simulator realistic?", figure("fig1_means", "The simulator's means against the published populations") +
     figure("fig2_spread", "The simulator's spread against the published series") +
     figure("fig7_quality", "Validity checks on the generated vertebrae")),
    ("verdict", "What to do", blocks(notes["verdict"])),
    ("glossary", "Glossary", glossary()),
    ("reproduce", "Reproduce", blocks(notes["reproduce"])),
]
unnoted = [n for _, _, body in PAGE for n in [] if n not in notes["figures"]]
for name in ("fig15_select", "fig16_exclusion", "fig17_covariates", "fig18_sex_naming", "fig19_bounds", "fig20_gold3", "fig14_strata", "fig12_naming_measures", "fig5_naming", "fig1_means", "fig2_spread", "fig7_quality"):
    if name not in notes["figures"]:
        raise SystemExit("figure with no note in report/ml_notes.json: %s" % name)

css = open(os.path.join(OUT, "style.css")).read() + """
:root { --accent: #0f766e; --accent-soft: #e0f2f0; --display: "Inter", "Segoe UI", system-ui, sans-serif; --body: "Inter", "Segoe UI", system-ui, sans-serif; --mono: "JetBrains Mono", ui-monospace, Menlo, monospace; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --accent: #5eead4; --accent-soft: #134e4a; } }
:root[data-theme="dark"] { --accent: #5eead4; --accent-soft: #134e4a; }
h1 { font-weight: 700; letter-spacing: -0.01em; }
h2 { font-weight: 650; font-size: 24px; }
.kv { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 8px 0 20px; }
@media (max-width: 760px) { .kv { grid-template-columns: 1fr; } }
"""
nav = "".join("<a href='#%s'>%s</a>" % (k, html.escape(t)) for k, t, _ in PAGE)
body = "".join("<section id='%s'><h2>%s</h2>%s</section>" % (k, html.escape(t), b) for k, t, b in PAGE)
won = select["winner"]
tiles = notes["tiles"]
tile_html = "".join(
    "<div class='tile'><div class='tl'>%s</div><div class='tv'><span>%s</span></div><div class='tn'>%s</div></div>"
    % (html.escape(l), html.escape(v), html.escape(n)) for l, v, n in tiles)

page = """<title>%s</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;650;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>%s</style>
<header class="top"><div class="wrap">
<p class="eyebrow">bordercall, research_notes/synthetic-validation &middot; pull request 38 &middot; confidential &middot; the ML view; the stats view is a page of its own</p>
<h1>%s</h1>
<p class="lede">%s</p>
<div class="tiles kv">%s</div>
<p class="meta">%s</p>
<p class="meta">Every figure is drawn by the note's committed code from the records on bordercall's branch or commit <code>%s</code>, and this page by report/build_ml.py from report/ml_notes.json and records/select/select.json.</p>
</div></header>
<nav class="toc"><div class="wrap">%s</div></nav>
<main class="wrap">%s</main>
<footer class="wrap"><p>Private to the owner. bordercall's research notes stay in bordercall; this page is a view of research_notes/synthetic-validation on the branch or commit above.</p></footer>
""" % (html.escape(notes["title"]), css, html.escape(notes["heading"]), inline(notes["lede"]), tile_html, inline(notes["meta"]), COMMIT, nav, body)

open(os.path.join(OUT, "ml.html"), "w").write(page)
print("wrote", os.path.join(OUT, "ml.html"), len(page), "winner", won["by_log_score"], won["by_accuracy"])
