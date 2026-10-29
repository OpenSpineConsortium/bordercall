"""The evaluation's tables and figures from the papers' readings and a cross_naming record, as
markdown and figure files in git, so the numbers live in the repository and not only in a doc.

Usage (from the repository's root, in the environment schwingcheck runs in):
    python research_notes/paper-tables/tools/results.py <data folder> <cross_naming record> <notes folder> <out folder>

It writes <out>/README.md, the tables; and transport and profiles, each as .png, .pdf, .csv and
.caption.txt, the figures with every number they draw. Line graphs take the build-up study's form
(schwingcheck/curve_report.py: black ink, serif type, lettered panels, a line and a marker per
series), and the profiles Benzel's: the levels down the side, Panjabi's means with their SDs as
filled circles on a solid line, the junctions dotted.

One series per paper counts in a summary, so no paper weighs more for printing more subgroups: in
the transport part the series covering the most measures times levels (then the larger count, more
fields, the name), and in the profiles the series with the largest count whose definition is
Panjabi's or close to it. A paper whose text says it pools Panjabi's spines is shown apart and left
out of every summary, since its fields are partly his.
"""
import csv
import json
import os
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS  # noqa: E402
from schwingcheck import measures as MS  # noqa: E402
from schwingcheck.curve_report import INK, letter, save, style, write_csv  # noqa: E402

ARMS = ("panjabi", "source", "widened_source")
ARM_NAME = {"panjabi": "Panjabi's fields", "source": "the papers' fields, rule as built",
            "widened_source": "the papers' fields, rule widened"}
ARM_STYLE = {"panjabi": dict(linestyle="-", marker="o", markerfacecolor=INK),
             "source": dict(linestyle="--", marker="s", markerfacecolor="white"),
             "widened_source": dict(linestyle=":", marker="^", markerfacecolor="white")}
STATS = ("exact", "within_one", "named")
PANELS = ("pedicle_w", "pedicle_h", "pedicle_incl_sag", "h_post", "canal_ap", "canal_w", "endplate_depth", "endplate")
PANEL_NAME = {"pedicle_w": "Pedicle width (PDW), mm", "pedicle_h": "Pedicle height (PDH), mm",
              "pedicle_incl_sag": "Pedicle sagittal angle (PDIs), deg", "h_post": "Posterior body height (VBHp), mm",
              "canal_ap": "Canal depth (SCD), mm", "canal_w": "Canal width (SCW), mm",
              "endplate_depth": "Upper end-plate depth (EPDu), mm", "endplate": "Upper end-plate width (EPWu), mm"}
SAME = ("same", "close")
JUNCTIONS = (("C7", "T1"), ("T12", "L1"))


# ---- reading -----------------------------------------------------------------------------------

def names(notes):
    """{paper: (first author and year, what the paper is)} from each clinical note's heading."""
    out = {}
    for f in os.listdir(notes):
        if f.endswith(".md"):
            line = open(os.path.join(notes, f)).readline().lstrip("# ").strip()
            who, _, what = line.partition(":")
            out[f[:-3]] = (who.split(" (")[0].strip(), what.strip())
    return out


def rows_of(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def readings(data):
    folder = os.path.join(data, "readings")
    return {f[:-4]: rows_of(os.path.join(folder, f)) for f in sorted(os.listdir(folder)) if f.endswith(".csv")}


def cohorts(data):
    folder = os.path.join(data, "cohorts")
    out = {}
    for f in sorted(os.listdir(folder)):
        if f.endswith(".cohorts.json"):
            out[f.split(".")[0]] = json.load(open(os.path.join(folder, f)))
    return out


def stated(entry):
    """As cross_naming.stated: an entry the readers marked inferred, or not stated, is not the paper's word."""
    opening = entry.get("evidence", "").strip().lower()
    return not (opening.startswith("inference") or opening.startswith("not stated")
                or "inference" in entry.get("what", "").lower())


# ---- the tables --------------------------------------------------------------------------------

def num(n):
    return "{:,}".format(n)


def md_table(header, align, rows):
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---:" if a == "r" else "---" for a in align) + " |"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return out


def kinds(rows):
    tables = sorted({r["table"].split(":")[0].strip() for r in rows if r["table"]})
    t = sum(1 for n in tables if n.lower().startswith("table"))
    f = sum(1 for n in tables if n.lower().startswith("fig"))
    parts = ["%d table%s" % (t, "" if t == 1 else "s")] if t else []
    parts += ["%d figure%s" % (f, "" if f == 1 else "s")] if f else []
    return ", ".join(parts + (["text"] if len(tables) - t - f else [])) or "text"


def table_read(read, called):
    """One row a paper: its cells by how they were settled, and Panjabi's measures its own values give."""
    out = []
    for paper, rows in read.items():
        checks = [r["check"] for r in rows]
        same, differs = set(), set()
        for r in rows:
            if r["source_of_values"] == "this paper" and r["vs_panjabi"] != "none":
                (same if r["vs_panjabi"] in SAME else differs).add(r["key"])
        who, what = called.get(paper, (paper, ""))
        out.append(dict(paper=paper, name=who, what=what, read=kinds(rows), cells=len(rows),
                        agreed=checks.count("agreed"), resolved=checks.count("resolved"), once=checks.count("single"),
                        panjabi_same_or_close=len(same), panjabi_differs=len(differs - same)))
    out.sort(key=lambda r: (r["name"].split()[-1], r["name"]))
    return out


def sharing(coh, papers):
    """Every stated sharing of subjects, pooled data or a method between two papers of the list."""
    on_list = set(papers) | {"panjabi1991c", "panjabi1991t", "panjabi1992", "panjabi1993f"}
    out = []
    for paper, record in coh.items():
        for e in record.get("shared", []):
            if e.get("what") not in ("subjects", "data pooled", "method") or not stated(e):
                continue
            named = sorted(p for p in on_list if p != paper and p in e.get("with", ""))
            if named:
                out.append(dict(paper=paper, what=e["what"], with_=", ".join(named), page=e.get("page", "")))
    return sorted(out, key=lambda r: (r["what"] != "data pooled", r["what"], r["paper"], r["with_"]))


def disagreement(record):
    """Per measure, over its levels: the sources set beside Panjabi with a definition his or close to
    it, the median distance of their means from his in his SDs and in levels, and the median spread
    between the sources (tau) in his SDs."""
    holds = record.get("holds_subjects_of", {})
    by = {}
    for d in record["disagreement"]:
        s = [x for x in d["sources"] if x["vs_panjabi"] in SAME and x["paper"] not in holds]
        if not s:
            continue
        b = by.setdefault(d["key"], {"levels": set(), "papers": set(), "sd": [], "lev": [], "tau": []})
        b["levels"].add(d["level"])
        b["papers"].update(x["paper"] for x in s)
        b["sd"] += [abs(x["d_panjabi_sd"]) for x in s if x["d_panjabi_sd"] is not None]
        b["lev"] += [abs(x["d_levels"]) for x in s if x.get("d_levels") is not None]
        if d.get("pool_tau") is not None and d["pool_k"] >= 3 and d["panjabi_sd"]:
            b["tau"].append(d["pool_tau"] / d["panjabi_sd"])
    out = []
    for key, b in sorted(by.items(), key=lambda kv: (-len(kv[1]["papers"]), kv[0])):
        lv = sorted(b["levels"], key=LEVELS.index)
        out.append(dict(key=key, papers=len(b["papers"]), levels="%s to %s" % (lv[0], lv[-1]) if len(lv) > 1 else lv[0],
                        cells=len(b["sd"]), median_sd=statistics.median(b["sd"]) if b["sd"] else None,
                        median_levels=statistics.median(b["lev"]) if b["lev"] else None,
                        beyond_one_level=sum(1 for x in b["lev"] if x > 1) / len(b["lev"]) if b["lev"] else None,
                        tau_cells=len(b["tau"]), median_tau=statistics.median(b["tau"]) if b["tau"] else None))
    return out


def series_key(t):
    return (t["paper"], t["cohort"], t["technique"], t["sex"], t["group"])


def counts(record):
    n = {}
    for d in record["disagreement"]:
        for s in d["sources"]:
            key = (s["paper"], s["cohort"], s["technique"], s["sex"], s["group"])
            n[key] = max(n.get(key, 0), s["n"] or 0)
    return n


def pick_series(record):
    n = counts(record)
    by = {}
    for t in record["transport"]:
        by.setdefault(series_key(t), []).append(t)
    best = {}
    for key, rows in by.items():
        rank = (len(rows[0]["measures"]) * len(rows[0]["levels"]), n.get(key, 0),
                sum(r["source"]["fields"] for r in rows), key)
        if key[0] not in best or rank > best[key[0]][0]:
            best[key[0]] = (rank, rows)
    return {paper: sorted(rows, key=lambda r: r["width"]) for paper, (_, rows) in best.items()}


def label(t):
    bits = [t["cohort"]]
    if t["sex"] not in ("", "all", "pooled", "not stated"):
        bits.append(t["sex"])
    if t["group"] and t["group"] != t["cohort"]:
        bits.append(t["group"])
    return ", ".join(bits)


def transport(record, called):
    holds = record.get("holds_subjects_of", {})
    chosen = pick_series(record)
    by_paper, sums = [], {}
    for paper in sorted(chosen):
        pools = "panjabi" in holds.get(paper, [])
        for t in chosen[paper]:
            for arm in ARMS:
                a = t[arm]
                by_paper.append(dict(paper=paper, name=called.get(paper, (paper,))[0], series=label(t),
                                     measures=len(t["measures"]), span="%s to %s" % (t["levels"][0], t["levels"][-1]),
                                     bodies=t["width"], arm=arm, fields=a["fields"],
                                     exact=100 * a["exact"] / a["fields"], within_one=100 * a["within_one"] / a["fields"],
                                     named=100 * a["named"] / a["fields"], named_right=a["named_right"], answered=a["named"],
                                     pools_panjabi=int(pools)))
                if pools:
                    continue
                s = sums.setdefault((t["width"], arm), {"fields": 0, "papers": 0, "named_right": 0, **{k: 0 for k in STATS}})
                s["fields"] += a["fields"]
                s["papers"] += 1
                s["named_right"] += a["named_right"]
                for k in STATS:
                    s[k] += a[k]
    summary = []
    for (bodies, arm), s in sorted(sums.items()):
        row = dict(bodies=bodies, arm=arm, papers=s["papers"], fields=s["fields"])
        for k in STATS:
            row[k] = 100 * s[k] / s["fields"]
        row["answered"] = s["named"]
        row["right_of_named"] = 100 * s["named_right"] / s["named"] if s["named"] else None
        summary.append(row)
    return summary, by_paper


# ---- the figures -------------------------------------------------------------------------------

def fig_transport(summary, out, caption):
    plt = style()
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)
    for ax, stat, let, title in zip(axes, STATS, "ABC", ("Named exactly", "Within one level", "Named at 0.99")):
        for arm in ARMS:
            pts = [r for r in summary if r["arm"] == arm]
            ax.plot([r["bodies"] for r in pts], [r[stat] for r in pts], color=INK, label=ARM_NAME[arm], **ARM_STYLE[arm])
        ax.set_xticks([1, 3, 5])
        ax.set_xlim(0.6, 5.4)
        ax.set_ylim(0, 100 if stat != "named" else max(10, 5 * (1 + int(max(r["named"] for r in summary) // 5))))
        ax.set_xlabel("Bodies in view")
        ax.set_ylabel("Per cent of fields")
        letter(ax, let, title)
    axes[0].legend(loc="upper left", bbox_to_anchor=(0, -0.28), ncol=3, borderaxespad=0)
    rows = [{k: v for k, v in r.items()} for r in summary]
    return save(fig, out, "transport", caption) + [write_csv(out, "transport", rows)]


def panjabi_profile():
    pool = MS.pool()
    mu, sd = MS.arrays(pool)
    base = [m.key.split(":")[0] for m in pool]
    out = {}
    for i, key in enumerate(base):
        if key in PANELS and key not in out:
            out[key] = [(LEVELS[j], float(mu[i, j]), float(sd[i, j])) for j in range(len(LEVELS))]
    return out


def profile_rows(record):
    holds = record.get("holds_subjects_of", {})
    rows = []
    for d in record["disagreement"]:
        if d["key"] not in PANELS:
            continue
        best = {}
        for s in d["sources"]:
            if s["vs_panjabi"] in SAME and s["sd"] is not None and s["n"]:
                if s["paper"] not in best or s["n"] > best[s["paper"]]["n"]:
                    best[s["paper"]] = s
        for paper, s in sorted(best.items()):
            rows.append(dict(panel=d["key"], level=d["level"], who="pools_panjabi" if "panjabi" in holds.get(paper, []) else "paper",
                             paper=paper, series=label(s), mean=s["mean"], sd=s["sd"], n=int(s["n"])))
    return rows


def fig_profiles(record, out, caption):
    plt = style()
    papers = profile_rows(record)
    panjabi = panjabi_profile()
    fig, axes = plt.subplots(2, 4, figsize=(7.4, 6.4), constrained_layout=True)
    drawn = []
    for ax, key, let in zip(axes.flat, PANELS, "ABCDEFGH"):
        mine = [r for r in papers if r["panel"] == key]
        first = min((LEVELS.index(r["level"]) for r in mine), default=len(LEVELS) - 5)
        span = LEVELS[max(0, first - 1):]
        y = {lv: i for i, lv in enumerate(span)}
        pj = [(lv, m, s) for lv, m, s in panjabi[key] if lv in y]
        ax.errorbar([m for _, m, _ in pj], [y[lv] for lv, _, _ in pj], xerr=[s for _, _, s in pj], color=INK,
                    linestyle="-", marker="o", markerfacecolor=INK, markersize=3.6, elinewidth=0.8, capsize=1.8)
        drawn += [dict(panel=key, level=lv, who="panjabi", paper="panjabi", series="12 cadaver spines", mean=m, sd=s, n=12)
                  for lv, m, s in pj]
        names_here = sorted({r["paper"] for r in mine})
        for k, paper in enumerate(names_here):
            pts = [r for r in mine if r["paper"] == paper and r["level"] in y]
            off = 0.32 * ((k + 1) / (len(names_here) + 1) - 0.5)
            marker = "D" if pts and pts[0]["who"] == "pools_panjabi" else "o"
            ax.errorbar([r["mean"] for r in pts], [y[r["level"]] + off for r in pts], xerr=[r["sd"] for r in pts],
                        color=INK, linestyle="none", marker=marker, markerfacecolor="white", markersize=3.0,
                        elinewidth=0.5, capsize=0, alpha=0.9)
            drawn += pts
        for upper, lower in JUNCTIONS:
            if upper in y and lower in y:
                ax.axhline((y[upper] + y[lower]) / 2, color=INK, linestyle=":", linewidth=0.7)
        ax.set_yticks(range(len(span)))
        ax.set_yticklabels(span, fontsize=6.5)
        ax.set_ylim(len(span) - 0.5, -0.5)
        ax.set_xlabel(PANEL_NAME[key], fontsize=7.5)
        letter(ax, let)
    for r in drawn:
        r["mean"] = round(r["mean"], 3)
        r["sd"] = round(r["sd"], 3)
    return save(fig, out, "profiles", caption) + [write_csv(out, "profiles", drawn)]


# ---- the page ----------------------------------------------------------------------------------

def pct(x):
    return "" if x is None else "%.1f" % x


def page(record, read_rows, share, dis, summary, by_paper, cross_path):
    cells = {k: sum(r[k] for r in read_rows) for k in ("cells", "agreed", "resolved", "once")}
    left = record.get("left_out_not_human", [])
    lines = ["# The evaluation with every paper's tables", "",
             "Source: thread \"Finish the clinical reread\", project symphony_4, 2026-10-29, for the owner's ask of 2026-10-28",
             "22:10 UTC. Written by tools/results.py from data/ and the cross_naming record (%s); every number here is in" % os.path.basename(cross_path),
             "a file beside it. Confidential, like the rest of this repository.", "",
             "Each paper counts as its own people measured its own way, unless its text says it shares subjects or a",
             "method (the owner, 2026-10-28). Pig spines are left out of every comparison (%d cohorts of Busscher 2010 and" % len(left),
             "van der Houwen 2009), and so are the two end-plate angles, since the L1 to L5 row of Panjabi's lumbar paper",
             "reprints his cervical C3 to C7 row (../../panjabi-endplate-inclination.md). Measures: %s." % ", ".join(record.get("left_out_measures", []) or ["none left out"]),
             "", "## The papers read", "",
             "%d papers, %s cells: the two blind readings agreed on %s, a third reader settled %s on the page image, and %s"
             % (len(read_rows), num(cells["cells"]), num(cells["agreed"]), num(cells["resolved"]), num(cells["once"])),
             "were read by one reader and checked on the page. The last two columns count Panjabi's measures among the",
             "paper's own values (not values it quotes), by whether its definition is his or close to it, or differs.", ""]
    lines += md_table(["Paper", "What it is", "Read", "Cells", "Agreed", "Resolved", "Read once", "Panjabi's, same or close", "Differs"],
                      "lllrrrrrr",
                      [[r["name"], r["what"], r["read"], num(r["cells"]), num(r["agreed"]), num(r["resolved"]), num(r["once"]),
                        r["panjabi_same_or_close"], r["panjabi_differs"]] for r in read_rows])
    lines += ["", "## Who was measured, and what papers share", "",
              "Only what a paper's text states counts; an entry its readers inferred is listed in its cohorts file and not",
              "used. Between papers of the list the text states these:", ""]
    lines += md_table(["Paper", "Shares", "With"], "lll", [[r["paper"], r["what"], r["with_"]] for r in share])
    lines += ["", "A paper that pools Panjabi's spines (Bonczar 2024's meta-analysis, which takes in Panjabi 1992, Tan 2004 and",
              "Robertson 2000) is kept out of every pool that holds a source it took in. A shared method makes two papers'",
              "techniques one, not their people: Tan 2004, Chen 2011, Kunkel 2011 and Tang 2016 measured as Panjabi did, so",
              "where they differ from him the people differ, not the method.", "",
              "## How far the papers sit from Panjabi", "",
              "Per measure, over the levels the papers give: each paper's mean against Panjabi's, in his population SDs and in",
              "levels (the difference over how far his mean moves from one level to the next there), and the spread between",
              "the papers (tau of a random-effects pool, three papers or more, in his SDs). Definitions his or close to it.", ""]
    lines += md_table(["Measure", "Papers", "Levels", "Cells", "Median distance, SDs", "Median distance, levels",
                       "Cells over one level", "Median tau, SDs (cells)"], "lrlrrrrr",
                      [[r["key"], r["papers"], r["levels"], r["cells"], "%.2f" % r["median_sd"] if r["median_sd"] is not None else "",
                        "%.2f" % r["median_levels"] if r["median_levels"] is not None else "",
                        "%.0f%%" % (100 * r["beyond_one_level"]) if r["beyond_one_level"] is not None else "",
                        "%.2f (%d)" % (r["median_tau"], r["tau_cells"]) if r["median_tau"] is not None else ""] for r in dis])
    lines += ["", "<img src=\"profiles.png\" alt=\"Eight panels, levels down the side: Panjabi's means with SDs on a solid line, each paper's means as open markers\" width=\"740\">", "",
              open(os.path.join(OUT, "profiles.caption.txt")).read().strip(), "",
              "## Naming the papers' fields with Panjabi's rule", "",
              "Fields drawn from each paper's own means and SDs, at every place its series covers, named by the rule built on",
              "Panjabi's table on the measures that series has, beside the same count of fields drawn from Panjabi's own",
              "table at the same places; and the same fields named by a rule whose table is the random-effects pool of every",
              "paper but the series' own, widened by their spread. One series per paper; papers that pool Panjabi's spines",
              "left out.", ""]
    lines += md_table(["Bodies", "Fields from", "Papers", "Fields", "Named exactly %", "Within one level %", "Named at 0.99 %",
                       "Right of those named %"], "rlrrrrrr",
                      [[r["bodies"], ARM_NAME[r["arm"]], r["papers"], num(r["fields"]), pct(r["exact"]), pct(r["within_one"]),
                        pct(r["named"]), "%s of %s" % (pct(r["right_of_named"]), num(r["answered"])) if r["answered"] else "none named"]
                       for r in summary])
    lines += ["", "<img src=\"transport.png\" alt=\"Three panels against the bodies in view: share named exactly, within one level and at 0.99, for Panjabi's fields and the papers' with the rule as built and widened\" width=\"720\">", "",
              open(os.path.join(OUT, "transport.caption.txt")).read().strip(), "", "By paper, three bodies:", ""]
    three = [r for r in by_paper if r["bodies"] == 3]
    papers = sorted({r["paper"] for r in three}, key=lambda p: next(r["name"] for r in three if r["paper"] == p).split()[-1])
    rows = []
    for p in papers:
        arm = {r["arm"]: r for r in three if r["paper"] == p}
        a = arm["source"]
        rows.append([a["name"] + (" (pools Panjabi)" if a["pools_panjabi"] else ""), a["series"], a["measures"], a["span"],
                     pct(arm["panjabi"]["exact"]), pct(a["exact"]), pct(arm["widened_source"]["exact"]),
                     pct(a["within_one"])])
    lines += md_table(["Paper", "Series", "Measures", "Levels", "Exact on Panjabi's fields %", "Exact on the paper's %",
                       "Exact, widened %", "Paper's, within one %"], "llrlrrrr", rows)
    lines += ["", "## Files", "",
              "- README.md, this page; transport.* and profiles.*, the figures as PNG and PDF with their captions and a CSV of",
              "  every number drawn; transport_by_paper.csv, every series' fields by arm and bodies.",
              "- ../data/: the readings, cohorts and series the record was made from; the record is ../data/%s." % os.path.basename(cross_path),
              "- Made with: python research_notes/paper-tables/tools/cross_naming.py data/series.csv data/%s %s" % (
                  os.path.basename(cross_path), record["command"].split(".json", 2)[-1].strip()),
              "  and python research_notes/paper-tables/tools/results.py research_notes/paper-tables/data",
              "  research_notes/paper-tables/data/%s research_notes/clinical-reread/notes research_notes/paper-tables/results." % os.path.basename(cross_path)]
    return "\n".join(lines) + "\n"


OUT = ""


def main(argv):
    global OUT
    data, cross_path, notes, OUT = argv[1:5]
    os.makedirs(OUT, exist_ok=True)
    record = json.load(open(cross_path))
    called = names(notes)
    read = readings(data)
    read_rows = table_read(read, called)
    share = sharing(cohorts(data), list(read))
    dis = disagreement(record)
    summary, by_paper = transport(record, called)
    widths = sorted({r["bodies"] for r in summary})
    fields = record["transport"][0]["fields_per_place"] if record["transport"] else 0
    fig_transport(summary, OUT,
                  "Naming fields drawn from the papers' own tables with the rule built on Panjabi's, by bodies in view, "
                  "one series per paper, %d fields per place, papers that pool Panjabi's spines left out: A, share named "
                  "exactly; B, within one level; C, share named at a posterior of 0.99. Solid, filled circles: fields "
                  "drawn from Panjabi's table at the same places; dashed, open squares: the papers' fields; dotted, "
                  "open triangles: the papers' fields named by the widened rule. Widths %s." % (fields, ", ".join(map(str, widths))))
    fig_profiles(record, OUT,
                 "Each paper's means beside Panjabi's, one series per paper and measure (the largest count, a definition his "
                 "or close to it): filled circles on a solid line, Panjabi's 12 spines with one SD; open circles, each "
                 "paper's mean with one SD, spread a little up and down so they do not overlap; open diamonds, a paper "
                 "that pools Panjabi's spines. Dotted lines, the cervicothoracic and thoracolumbar junctions.")
    with open(os.path.join(OUT, "transport_by_paper.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(by_paper[0]), lineterminator="\n")
        w.writeheader()
        for r in by_paper:
            w.writerow({k: round(v, 3) if isinstance(v, float) else v for k, v in r.items()})
    with open(os.path.join(OUT, "README.md"), "w", newline="\n") as fh:
        fh.write(page(record, read_rows, share, dis, summary, by_paper, cross_path))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
