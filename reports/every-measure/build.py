"""Write the page "Naming Vertebrae From Every Measure" from the five recorded runs.

    python reports/every-measure/build.py               # writes index.html beside this file

The page is the artifact the owner reads: every table on it is filled here from the records
(records/curve-2026-10-28/, records/chain-2026-10-28/, records/one-body-2026-10-29/ and
records/fixed-k-2026-10-29/), and every figure is the PNG the committed code drew into those
records, published beside the page under fig/ (FILES.md maps each to its source). The prose
quotes schwingcheck/README.md, whose numbers the tests hold to the same records. Nothing here
comes from a patient: the truth is the generator's, built from Panjabi's table.
"""
from __future__ import annotations

import csv
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CURVE = os.path.join(ROOT, "records", "curve-2026-10-28")
CHAIN = os.path.join(ROOT, "records", "chain-2026-10-28")
ONE = os.path.join(ROOT, "records", "one-body-2026-10-29")
FIXED = os.path.join(ROOT, "records", "fixed-k-2026-10-29")
SEVEN = ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post", "canal_w", "canal_ap"]
LEVELS = ["C3", "C4", "C5", "C6", "C7"] + ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)]
FIGURES = {
    "curve_accuracy": CURVE, "curve_data": CURVE, "curve_speed": CURVE,
    "chain_accuracy": CHAIN, "chain_answers": CHAIN, "chain_data": CHAIN, "chain_speed": CHAIN,
    "one_body_levels": ONE, "one_body_buildup": ONE, "one_body_size": ONE, "one_body_coarse": ONE,
    "fixed_k_forest": FIXED, "fixed_k_mixing": FIXED, "fixed_k_tail": FIXED,
}
# The measures as the papers name them, for the census table (schwingcheck/mnemonics.py).
PLAIN = {
    "spinous_length": "spinous process length", "endplate_lower_area": "lower end-plate area",
    "transverse_width": "transverse process width", "interfacet_w_sup": "upper interfacet width",
    "interfacet_h": "interfacet height", "facet_sag_inf": "inferior facet sagittal angle",
    "pedicle_w": "pedicle width", "pedicle_incl_trans": "pedicle transverse angle",
    "endplate_area": "upper end-plate area", "facet_area_inf": "inferior facet area",
    "endplate_depth": "upper end-plate depth", "facet_area_sup": "superior facet area",
    "endplate_lower_depth": "lower end-plate depth", "pedicle_h": "pedicle height",
    "endplate_lower": "lower end-plate width", "facet_w_sup": "superior facet width",
    "interfacet_w_inf": "lower interfacet width", "pedicle_incl_sag": "pedicle sagittal angle",
    "canal_w": "canal width", "endplate": "upper end-plate width", "facet_sag_sup": "superior facet sagittal angle",
    "canal_area": "canal area", "facet_trans_sup": "superior facet transverse angle",
    "endplate_incl": "upper end-plate inclination", "h_post": "posterior body height",
    "facet_h_inf": "inferior facet height", "canal_ap": "canal depth", "pedicle_area": "pedicle area",
    "facet_trans_inf": "inferior facet transverse angle", "facet_w_inf": "inferior facet width",
    "endplate_lower_incl": "lower end-plate inclination", "facet_h_sup": "superior facet height",
}


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def pct(x, places=1):
    return ("%." + str(places) + "f") % float(x)


def census_rows():
    """The greedy order with the share named exactly after each addition: one body (the
    one-body record, the chain's prior), three and nine bodies (the build-up record)."""
    one = json.load(open(os.path.join(ONE, "one_body.json")))
    order = one["order"]
    first = {r["measures"]: r for r in one["rows"]
             if r["type"] == "typical" and r["prior"] == "chain" and r["size"] == "unknown"}
    acc = read_csv(os.path.join(CURVE, "figures", "curve_accuracy.csv"))
    exact = {(r["subset"], r["bodies"]): r["percent"] for r in acc if r["panel"] == "Named exactly"}
    rows = []
    for i, key in enumerate(order, 1):
        name = key.split(":")[0]
        prefix = "prefix-%02d" % i
        rows.append({
            "rank": i, "key": name, "plain": PLAIN[name], "seven": name in SEVEN,
            "one": pct(100 * first["first %d" % i]["exact"]),
            "three": pct(exact[(prefix, "3")]), "nine": pct(exact[(prefix, "9")]),
        })
    return rows


def level_rows():
    one = json.load(open(os.path.join(ONE, "one_body.json")))
    by = {(r["measures"], r["name"]): r for r in one["levels"]
          if r["type"] == "typical" and r["prior"] == "chain" and r["size"] == "unknown"}
    rows = []
    for lv in LEVELS:
        a, s = by[("all", lv)], by[("seven", lv)]
        rows.append({"level": lv, "seven": pct(100 * s["exact"]), "all": pct(100 * a["exact"]),
                     "within": pct(100 * a["within_one"]), "at99": pct(100 * a["answered"]),
                     "taken": a["most_taken_for"], "taken_share": pct(100 * a["most_taken_share"], 0)})
    extra = {(r["type"], r["name"], r["measures"]): r for r in one["levels"]
             if r["prior"] == "chain" and r["size"] == "unknown"}
    anomalies = []
    for typ, lv in (("six_lumbar", "L6"), ("t13", "T13")):
        a, s = extra[(typ, lv, "all")], extra[(typ, lv, "seven")]
        anomalies.append({"level": lv, "seven": pct(100 * s["exact"]), "all": pct(100 * a["exact"]),
                          "within": pct(100 * a["within_one"]), "at99": pct(100 * a["answered"]),
                          "taken": a["most_taken_for"], "taken_share": pct(100 * a["most_taken_share"], 0)})
    return rows, anomalies


def chain_rows():
    chain = json.load(open(os.path.join(CHAIN, "chain.json")))
    out = []
    for bodies in (3, 5, 9):
        for typ, label in (("typical", "typical"), ("six_lumbar", "six lumbar"), ("t13", "with a T13")):
            cells = {}
            for arm in ("consecutive", "gaps", "chain", "known gaps"):
                r = next(x for x in chain["rows"] if x["arm"] == arm and x["bodies"] == bodies
                         and x["type"] == typ and x["subset"] == "all")
                cells[arm] = (pct(100 * r["exact"]), pct(100 * r["precision"]) if r["precision"] == r["precision"] else "")
            seven = next(x for x in chain["rows"] if x["arm"] == "chain" and x["bodies"] == bodies
                         and x["type"] == typ and x["subset"] == "seven")
            out.append({"bodies": bodies, "type": label, "cells": cells, "seven": pct(100 * seven["exact"])})
    return out


def table(headers, rows, numeric_from=1, caption=None):
    head = "".join("<th%s>%s</th>" % (' class="n"' if i >= numeric_from else "", h) for i, h in enumerate(headers))
    body = []
    for row in rows:
        body.append("<tr>" + "".join("<td%s>%s</td>" % (' class="n"' if i >= numeric_from else "", c)
                                      for i, c in enumerate(row)) + "</tr>")
    cap = "<caption>%s</caption>" % caption if caption else ""
    return '<div class="tbl"><table>%s<thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        cap, head, "".join(body))


def figure(name, caption):
    folder = FIGURES[name]
    cap = open(os.path.join(folder, "figures", name + ".caption.txt")).read().strip()
    return ('<figure><img src="fig/%s.png" alt="%s" loading="lazy"><figcaption><b>%s</b> %s</figcaption></figure>'
            % (name, html.escape(cap), caption, html.escape(cap)))


def build():
    census = census_rows()
    levels, anomalies = level_rows()
    chains = chain_rows()
    census_tbl = table(
        ["#", "Measure added", "1 body", "3 bodies", "9 bodies"],
        [[r["rank"], r["plain"] + (' <span class="v s">SPINEPS</span>' if r["seven"] else ""),
          r["one"], r["three"], r["nine"]] for r in census], numeric_from=2,
        caption="Per cent of synthetic typical fields named exactly after each measure is added, in the greedy order. "
                "One body: 11,000 fields, the chain's prior (records/one-body-2026-10-29). Three and nine bodies: "
                "the build-up record's 2,000 columns, a uniform prior over C3 to L5 (records/curve-2026-10-28). "
                "Marked, the seven measures a SPINEPS mask gives today.")
    level_tbl = table(
        ["Level", "Seven, exact", "All 32, exact", "All 32, within one", "All 32, named at 0.99", "Most taken for"],
        [[r["level"], r["seven"], r["all"], r["within"], r["at99"], "%s (%s%%)" % (r["taken"], r["taken_share"])]
         for r in levels] +
        [["<i>%s</i>, lone" % r["level"], r["seven"], r["all"], r["within"], r["at99"], "%s (%s%%)" % (r["taken"], r["taken_share"])]
         for r in anomalies],
        caption="A lone body named from its own measures, size unknown, the chain's prior, 500 synthetic fields a "
                "level (records/one-body-2026-10-29). The last two rows are a lone L6 on a six-lumbar column and a "
                "lone T13 on a column with a T13; the seven have no name for either.")
    chain_tbl = table(
        ["Bodies", "Column", "Consecutive rule", "Gaps summed", "Chain", "Chain, gaps known", "Chain, the seven"],
        [[c["bodies"], c["type"],
          "%s <span class=\"sub\">(%s)</span>" % c["cells"]["consecutive"],
          "%s <span class=\"sub\">(%s)</span>" % c["cells"]["gaps"],
          "%s <span class=\"sub\">(%s)</span>" % c["cells"]["chain"],
          "%s <span class=\"sub\">(%s)</span>" % c["cells"]["known gaps"], c["seven"]] for c in chains],
        numeric_from=2,
        caption="Per cent of middle bodies named exactly with all 32 measures, 200 synthetic fields a cell, each "
                "step missing a body with probability 0.167; in brackets, per cent right of the answers at 0.99 "
                "(records/chain-2026-10-28). The last column is the chain cut to the seven.")
    page = TEMPLATE.replace("{{CENSUS}}", census_tbl).replace("{{LEVELS}}", level_tbl).replace("{{CHAIN}}", chain_tbl)
    for name in FIGURES:
        page = page.replace("{{FIG:%s}}" % name, figure(name, CAPTION_LEAD[name]))
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page)
    with open(os.path.join(HERE, "FILES.md"), "w") as f:
        f.write("# Files published beside index.html\n\nEach `fig/<name>.png` is the PNG the committed code drew "
                "into the record named; nothing is copied here. Publish with these mappings from the repository root.\n\n")
        for name, folder in FIGURES.items():
            f.write("- fig/%s.png: %s/figures/%s.png\n" % (name, os.path.relpath(folder, ROOT), name))
    return len(page)


CAPTION_LEAD = {
    "curve_accuracy": "The build-up.", "curve_data": "What the table costs.", "curve_speed": "Time to name a field.",
    "chain_accuracy": "The chain against the rules before it.", "chain_answers": "The chain's answers at 0.99.",
    "chain_data": "The chain's table from P people.", "chain_speed": "The chain's speed.",
    "one_body_levels": "A lone body, level by level.", "one_body_buildup": "A lone body as measures are added.",
    "one_body_size": "What the size gives a lone body.", "one_body_coarse": "Coarse claims a lone body can make.",
    "fixed_k_forest": "NUTS against the closed form.", "fixed_k_mixing": "The discrete step.",
    "fixed_k_tail": "The naming model in the far tail.",
}

TEMPLATE = r"""<title>Naming Vertebrae From Every Measure</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,600;1,500&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: one reading column of about 70 characters; tables and figures step out to 1100px on white plates.
   The register is a quantitative-anatomy paper: a Garamond for titles, a legible humanist sans for the text,
   a mono for the numbers. */
:root{
  --paper:#f2f4f1; --plate:#ffffff; --ink:#1b2126; --ink-2:#4f5a60; --rule:#cfd6d2;
  --accent:#2f6e5a;   /* the rule's answers */
  --anom:#9c3b2e;     /* anomalies, wrong answers */
  --mark:#7a5c12;     /* the seven SPINEPS measures */
  --shade:#e4ebe6;
  --display:"EB Garamond",Garamond,"Times New Roman",serif;
  --body:"Atkinson Hyperlegible","Segoe UI",Helvetica,Arial,sans-serif;
  --mono:"JetBrains Mono",Consolas,Menlo,monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --paper:#14181a; --plate:#1d2326; --ink:#e4e8e6; --ink-2:#a3adb0; --rule:#2f393c;
  --accent:#7cc2a8; --anom:#e07d6c; --mark:#d8b45a; --shade:#223029; color-scheme:dark; }}
:root[data-theme="dark"]{
  --paper:#14181a; --plate:#1d2326; --ink:#e4e8e6; --ink-2:#a3adb0; --rule:#2f393c;
  --accent:#7cc2a8; --anom:#e07d6c; --mark:#d8b45a; --shade:#223029; color-scheme:dark; }
html,body{background:var(--paper);color:var(--ink)}
body{font-family:var(--body);font-size:16px;line-height:1.55;margin:0;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  padding-block:0 64px}
.wrap{max-width:70ch;margin:0 auto}
.full{max-width:1100px;margin:0 auto}
h1,h2,h3{font-family:var(--display);text-wrap:balance;line-height:1.15;margin:0}
h1{font-size:clamp(32px,5vw,48px);font-weight:600;letter-spacing:-.005em}
h2{font-size:clamp(24px,3vw,30px);font-weight:600;margin-top:2.8rem;padding-top:1.1rem;border-top:1px solid var(--rule)}
h3{font-size:19px;font-weight:600;margin-top:1.6rem}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
p{margin:.7rem 0}
a{color:var(--accent)}
.byline{color:var(--ink-2);font-size:14.5px;margin-top:.8rem}
.tally{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:1.6rem 0 0}
.tally div{background:var(--plate);border:1px solid var(--rule);padding:12px 14px;border-radius:4px;min-width:0}
.tally b{display:block;font-family:var(--mono);font-size:28px;font-weight:500;font-variant-numeric:tabular-nums;line-height:1.15;color:var(--accent)}
.tally .x b{color:var(--anom)}
.tally span{font-size:13px;color:var(--ink-2)}
.box{background:var(--plate);border:1px solid var(--rule);border-radius:4px;padding:16px 20px;margin-top:1.6rem}
.box p{margin:.5rem 0;font-size:15px}
.kp{margin:.6rem 0 0 1.1rem;padding:0;font-size:15px}
.kp li{margin:.4rem 0}
.callout{border-left:3px solid var(--anom);padding:4px 14px;margin:1.2rem 0;background:var(--shade)}
.callout.green{border-color:var(--accent)}
figure{margin:1.8rem 0}
figure img{width:100%;max-width:100%;height:auto;display:block;background:#fff;border:1px solid var(--rule);border-radius:3px}
figcaption{font-size:14px;color:var(--ink-2);margin-top:.6rem;max-width:90ch}
figcaption b{color:var(--ink)}
.tbl{overflow-x:auto;margin:1.2rem 0;border:1px solid var(--rule);border-radius:4px;background:var(--plate)}
table{border-collapse:collapse;font-size:14px;min-width:640px;width:100%;font-variant-numeric:tabular-nums}
caption{caption-side:bottom;text-align:left;font-size:13px;color:var(--ink-2);padding:10px 12px;line-height:1.45}
th,td{padding:7px 10px;text-align:left;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-family:var(--mono);font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-2);background:var(--shade);font-weight:500}
td.n,th.n{text-align:right;font-family:var(--mono);font-size:13px}
.sub{color:var(--ink-2);font-size:12px}
.v{font-family:var(--mono);font-weight:500;padding:1px 6px;border-radius:3px;font-size:11px;white-space:nowrap;vertical-align:middle}
.v.s{background:color-mix(in srgb,var(--mark) 18%,transparent);color:var(--mark)}
.repro{font-family:var(--mono);font-size:13px;background:var(--plate);border:1px solid var(--rule);border-radius:4px;padding:12px 14px;overflow-x:auto;white-space:pre;line-height:1.5}
.foot{font-size:13px;color:var(--ink-2);margin-top:3rem;border-top:1px solid var(--rule);padding-top:1rem}
@media (max-width:520px){ body{font-size:15px} .tally b{font-size:24px} }
@media (prefers-reduced-motion: reduce){ *{scroll-behavior:auto} }
</style>

<div class="wrap">
  <p class="eyebrow" style="margin-top:28px">bordercall &middot; schwingcheck &middot; confidential &middot; synthetic columns drawn from Panjabi's table &middot; 29 October 2026</p>
  <h1>Naming Vertebrae From Every Measure</h1>
  <p class="byline">The naming rule scored with every measure the four Panjabi papers print with a spread from C3 to L5, against the seven a SPINEPS mask gives today: the build-up, the chain of levels, a lone vertebra and the sampler review. bordercall pull requests 18 to 33, merged on main at 3722785.</p>

  <div class="tally">
    <div><b>98.3%</b><span>three-body fields named exactly with all 32 measures; the seven name 73.1%</span></div>
    <div><b>86.8%</b><span>a lone vertebra named exactly with all 32; the seven name 46.2%</span></div>
    <div><b>98.0%</b><span>middle bodies named by the chain at five bodies, all 32; the consecutive rule 88.0%</span></div>
    <div><b>99.59%</b><span>or more of the answers at posterior 0.99 right on the table as printed, at every count of measures and every width</span></div>
    <div class="x"><b>95.75%</b><span>right at 0.99 when the table comes from 12 people, as Panjabi's does, with the seven; from 50 people 99.36% or more</span></div>
  </div>

  <div class="box">
    <p class="eyebrow">What this page shows</p>
    <ul class="kp">
      <li>Of the 49 measures the four Panjabi papers print, 32 carry a mean and a spread at every level from C3 to L5, 18 lengths, 6 areas and 8 angles; the other 17 are printed with no spread or in one region only. The rule takes those 32, each with its own measurement error and its own power of the patient's size.</li>
      <li>Adding measures in a greedy order names more fields at every step, and the answers at 0.99 keep their promise throughout. The first seven of that order share none of the seven measures in use today and name 89.2% of three-body fields against 73.1%.</li>
      <li>The chain of levels, which sums out a missed body and gives an L6 and a T13 names of their own, names 97.5% to 99.0% of nine-body fields exactly where the rule before it names 70.0% to 74.0%, and its answers at 0.99 are right 99.4% of the time or more.</li>
      <li>A lone vertebra is named 86.8% of the time with all 32 and 46.2% with the seven; T4 to T8 are named least; a lone L6 is named one time in eight and a lone T13 half the time, where the seven can name neither.</li>
      <li>NUTS with every level known is the closed form within 1.9 Monte Carlo errors. PyMC's proportional categorical proposal samples the wrong law, so the discrete step was written here with Liu's acceptance; the PyMC issue is drafted.</li>
    </ul>
  </div>

  <div class="callout">
    <p><b>Every number here is synthetic.</b> The columns are drawn by bordercall's generator from the table the rule assumes, Panjabi's four papers on twelve fresh autopsy spines, with the measurement error the rule assumes (1 mm for a length, 3 degrees for an angle). The rule is scored against the truth it was built from. What a real spine does, and what a mask or a radiograph measures with what error, is not measured on this page; the gold tier 3 CT morphometrics and the comparison with the 39 other papers are the pieces that measure it.</p>
  </div>

  <h2>The 32 measures, in the order that adds most</h2>
  <p>The forward greedy order was chosen on 100 selection columns of seeds of its own by the log loss of the true place summed over 1, 3 and 9 bodies, and every prefix of it was then scored on columns that did not choose it. Each measure's place is what it adds given the measures before it, so the order separates the information the measures carry: a measure that repeats an earlier one lands late however strong it is alone. This is the census of these 32 as the lone-body and the three-body problem see it; the census per level, with the groups of independent information and the gold tier 3 table beside this one, follows as <code>schwingcheck census</code>.</p>
</div>
<div class="full">
  {{CENSUS}}
</div>
<div class="wrap">
  <p>Of the seven a SPINEPS mask gives today, none is among the first ten: the lower end-plate depth comes 13th, the upper end-plate depth 11th, the lower end-plate width 15th, the canal width 19th, the upper end-plate width 20th, the posterior height 25th and the canal depth 27th. The best seven, the spinous process length, the lower end-plate area, the transverse process width, two interfacet measures, the inferior facet's sagittal angle and the pedicle width, are measured by no code on a mask yet.</p>

  <h2>The build-up</h2>
  <p>One measure names 42.0% of three-body fields exactly; the seven, 73.1%; the first seven of the greedy order, 89.2%; 14 measures, 94.8%; 25, 97.6%; all 32, 98.3%. From 25 measures on every nine-body field of the 2,000 columns is named exactly. The share named at a posterior of 0.99 grows from 2.5% to 87.0% at three bodies, and of the fields named at 0.99, 99.59% or more were right at every count and every width scored; the least, 99.59%, is 9 wrong of 2,196, at two measures and three bodies.</p>
</div>
<div class="full">
  {{FIG:curve_accuracy}}
</div>
<div class="wrap">
  <p>The errors move the share named and not the promise. With every measure's error doubled, in the columns and the rule alike, the seven name 63.0% of three-body fields and all 32 name 95.3%; halved, 76.8% and 99.2%; with the offsets correlated at 0.4 between measures, which the rule takes as independent, 73.8% and 98.3%, against 73.1% and 98.3% as assumed. In every cell the answers at 0.99 are right 99.77% of the time or more.</p>

  <h2>What the table costs</h2>
  <p>A table estimated from 12 people, as many as Panjabi measured, names 13.2 points fewer three-body fields exactly with the seven and 5.2 fewer with all 32 than the table as printed, and its answers at 0.99 are right only 95.75% and 98.05% of the time, below the 99% the posterior promises. From 50 people on they are right 99.36% of the time or more, with all 32 99.82% at 50 people; from 200 people the share named is within 1.25 points of the printed table's. With the seven alone, tables from 50, 200 and 2,000 people stand 1.1 to 1.6 standard errors above 99%, and the table as printed is itself 99.54% on these columns, so with the seven these columns cannot tell whether a table from 50 people keeps the promise.</p>
</div>
<div class="full">
  {{FIG:curve_data}}
</div>
<div class="wrap">
  <p>The axis's people all have one size and are measured without error, so these rows give what the people's own variation costs a table and nothing more; whether real spines vary from person to person as the generator's people do is not measured here.</p>

  <h2>The chain of levels</h2>
  <p>The chain reads a field as a walk down the column, with pymc-extras' <code>DiscreteMarkovChain</code> as its PyMC form and an exact sum as its answer. Each step may miss a body, and a six-lumbar spine or a spine with a T13 is a state of the chain rather than an error, so an L6 and a T13 have names of their own. Against the consecutive rule of step d, on synthetic columns where a step misses a body with probability 0.167, the chain names more at every width and its answers at 0.99 keep their promise where the consecutive rule's do not.</p>
</div>
<div class="full">
  {{CHAIN}}
  {{FIG:chain_accuracy}}
  {{FIG:chain_answers}}
</div>
<div class="wrap">
  <p>The six-lumbar and T13 columns are the generator's own construction, so the chain is scored against the truth it was built from; replacing that construction with the real prevalence and the real shape of an L6 or a T13 is item 6 of the work list. Both PyMC models are held to the exact answer by the tests rather than trusted: sampled one field at a time they name all 18 of their three-body fields as the exact answer does, within 0.02 at every name but one, where a chain stuck far out in the size's prior and R-hat, not the Monte Carlo error, showed it.</p>
</div>
<div class="full">
  {{FIG:chain_data}}
</div>
<div class="wrap">
  <h2>A lone vertebra</h2>
  <p>One body, its own measures, no neighbour: with all 32 it is named exactly 86.8% of the time, within one level 96.9%, and 42.1% of the time at a posterior of 0.99, right 99.85% of the time when it is. With the seven, 46.2%, and almost never at 0.99. Knowing the patient's height adds 1.9 points with the seven and 0.2 with all 32; the size itself adds 9.5 and 2.9. The levels differ: C6, C7, T1, T2, T11, T12 and L5 are named 97% of the time or more, T4 to T8 63% to 70%.</p>
</div>
<div class="full">
  {{LEVELS}}
  {{FIG:one_body_levels}}
  {{FIG:one_body_buildup}}
</div>
<div class="wrap">
  <p>Coarse claims a lone body can decide at 0.99 either way, such as "below C7" or "in the lumbar spine", are decided for 90.6% of fields with the seven and right 99.97% of the time (3 wrong of 9,971); the exact name is the hard question, the region is not.</p>
</div>
<div class="full">
  {{FIG:one_body_size}}
  {{FIG:one_body_coarse}}
</div>
<div class="wrap">
  <h2>Speed</h2>
  <p>One three-body field, single-threaded, with each engine's table built once: the rule takes 0.31 ms with one measure, 1.12 ms with the seven and 9.68 ms with all 32 on the trapezoid's nodes (5.25 ms on the Gauss-Hermite nodes); NUTS on the same field takes 166 to 712 times as long, and at 16 measures was once silently wrong at R-hat 1.00. The chain, built once, takes 2.4 ms at three bodies, 6.6 ms at five and 79 ms at nine with all 32; the path form that rebuilds its blocks in every call takes 16 s at nine. These are batch means with the setup inside, not latency numbers by SchwingNet's rule, which needs ONNX parity and a p95 for the same file; the budget there is 97 ms.</p>
</div>
<div class="full">
  {{FIG:curve_speed}}
  {{FIG:chain_speed}}
</div>
<div class="wrap">
  <h2>The sampler review</h2>
  <p>With every level known, NUTS on the size is the closed form: 8 fields, |z| at most 1.9 Monte Carlo errors, R-hat 1.002, effective samples 2,941 and 6,698 for the seven and all 32. With the place free, PyMC's uniform categorical proposal switches between two likely places 0.15% to 2.9% of the time and its chains disagree (R-hat 1.314); its proportional proposal mixes (R-hat 1.001) but samples the stationary law of its own kernel, not the target, 3 to 37 Monte Carlo errors off: its acceptance ratio takes one less the renormalised proposal weight where Liu's takes one less the value's own probability. Summing the level out, as pymc-extras does, is exact except where NUTS leaves a chain in a far mode, which R-hat shows. The discrete step bordercall uses is <code>schwingcheck.categorical.MetropolisedGibbs</code>, Liu's acceptance written out; the report to the PyMC project is drafted with a reproduction that stands alone (pull request 34) and waits for the owner to post it.</p>
</div>
<div class="full">
  {{FIG:fixed_k_forest}}
  {{FIG:fixed_k_mixing}}
  {{FIG:fixed_k_tail}}
</div>
<div class="wrap">
  <h2>Against the 39 other papers</h2>
  <p>The 39 other papers of the owner's list give 209 paper-measure pairs, 106 distinct measures (57 not in Panjabi) and 4,477 series, nearly all lumbar or thoracolumbar; three papers reach C3 to L5 with a spread at every level. By the owner's rule of 28 October each paper is its own population and technique unless its text says otherwise, so they do not enter this table. Set beside it (the clinical reread's draft pull request 26, not yet on main): on three-body fields drawn from 25 papers' own series, Panjabi's rule names 23.7% exactly against 47.2% on fields from his own table, and its answers at 0.99 are right 88.8% of the time, 92.0% when the rule is widened by the papers' spread. That gap, not the mathematics, is where the rule is weak: the population behind the table.</p>

  <div class="callout green">
    <p><b>Limits.</b> Synthetic truth throughout. One table of twelve spines; no correlation between measures is known, and the rule takes them as independent. Most of the 32 are measured by no code on a mask or a radiograph yet, and the measurement errors are stated assumptions, not measured ones. The six-lumbar and T13 columns are the generator's construction. No latency number by SchwingNet's rule exists for any of this.</p>
  </div>

  <h3>Reproduce</h3>
  <div class="repro">python -m schwingcheck curve run --outdir records/curve-2026-10-28      # the build-up, then curve speed and figures
python -m schwingcheck.chain_study run                                  # the chain, records/chain-2026-10-28
python -m schwingcheck.one_body run --columns 500 --processes 3        # the lone body, records/one-body-2026-10-29
python -m schwingcheck.fixed_k run                                      # the sampler review, records/fixed-k-2026-10-29
python -m unittest tests/test_schwingcheck_*.py                        # 268 tests, 1,041 s, hold the README to the records
python reports/every-measure/build.py                                  # this page's tables, from the same records</div>

  <p class="foot">bordercall main 3722785 (pull requests 18 to 33); the README's sections "The build-up study", "The chain of levels", "The one-vertebra evaluation" and "The fixed-k NUTS review" carry every number with its record, and the tests hold them to the records' files. The figures are the records' own PNGs, drawn by schwingcheck/figures.py; their CSVs beside them hold every number drawn. Confidential, like everything in bordercall; nothing of the method is for the talk.</p>
</div>
"""

if __name__ == "__main__":
    print("wrote index.html, %d bytes" % build())
