"""Step e's build-up study as tables and figures, from its record alone (curve.py writes it).

    python -m schwingcheck curve table --record schwingcheck/records/curve-2026-10-28/curve.nc
    python -m schwingcheck curve figures --record schwingcheck/records/curve-2026-10-28/curve.nc
    python -m schwingcheck curve check --record schwingcheck/records/curve-2026-10-28/curve.nc

`table` prints the README's tables, each between the markers <!-- curve:NAME --> and
<!-- /curve:NAME -->, and `check` says whether the README holds each as `table` prints it, so that
every number the README gives for the study is the record's. `figures` draws as the archive's
figures are drawn (archive/bordercall/junction_figures.py): black ink, serif type, an axis on two
sides, no grid, no colour, the widths of the field told apart by line and marker as
identify_figures.py sets them; each figure is written as PDF with no date inside, PNG at 300 dpi,
the CSV of every number drawn and its caption, under sixty words, and FIGURES.md names the record
and the code by sha256. Every number is about synthetic columns drawn from Panjabi's tables, never
a patient.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import re
from typing import Dict, List, Optional, Sequence

import numpy as np

from . import table as T

README = os.path.join(T.ROOT, "schwingcheck", "README.md")
TABLES = ("curve", "subsets", "arms", "data", "anomalous", "speed", "nuts", "floor")
WIDTHS = (1, 3, 9)
HEADLINE = 3                         # the width the one-width columns report, as the archive's figures do
INK = "#000000"
SERIF = ["Liberation Serif", "Times New Roman", "Nimbus Roman", "DejaVu Serif"]
PNG_DPI = 300
WIDTH_STYLE = {1: dict(linestyle=":", marker="^", markerfacecolor="white"),
               3: dict(linestyle="--", marker="s", markerfacecolor="white"),
               5: dict(linestyle="-", marker="o", markerfacecolor="white"),
               9: dict(linestyle="-", marker="o", markerfacecolor=INK)}
ENGINE_NAME = {"numpy-trapezoid": "rule.py, trapezoid", "numpy-gauss-hermite": "rule.py, Gauss-Hermite",
               "pytensor-trapezoid": "compiled rule, trapezoid"}
ENGINE_STYLE = {"numpy-trapezoid": dict(linestyle="-", marker="o", markerfacecolor=INK),
                "numpy-gauss-hermite": dict(linestyle="--", marker="s", markerfacecolor="white"),
                "pytensor-trapezoid": dict(linestyle=":", marker="^", markerfacecolor="white")}
SUBSET_NAME = {"seven": "the seven (rung 0)", "lengths": "the lengths", "seven+areas": "the seven and the areas",
               "seven+angles": "the seven and the angles", "ap": "what an AP view reads",
               "lateral": "what a lateral view reads", "ap+lateral": "both views", "all": "all 32"}
FAMILY_NAME = {"pedicles": "the pedicles", "processes": "the processes", "facets": "the facets",
               "interfacet": "the interfacet distances", "body": "the rest of the body and the canal"}
FAMILIES = ("pedicles", "processes", "facets", "interfacet", "body")
PHENOTYPE_NAME = {"typical": "Typical", "four_lumbar": "Four lumbar", "six_lumbar": "Six lumbar",
                  "t13": "Thirteenth rib-bearing body", "lumbar_rib": "Rib on L1", "no_rib_t12": "No rib on T12"}
ANOMALOUS = ("four_lumbar", "six_lumbar", "t13", "lumbar_rib", "no_rib_t12")
PEOPLE = (12, 50, 200, 2000)
SPEED_MEASURES = (1, 7, 16, 32)
CAPTIONS = {
    "curve_accuracy":
        "Naming a field as measures are added in the greedy order, typical synthetic columns: A, share "
        "named exactly; B, share named at posterior 0.99; C, share of those right, dotted at 99 per "
        "cent. Crosses, the seven SPINEPS measures. By the bodies in view; %d columns.",
    "curve_speed":
        "Time to name one field, single-threaded, as measures are added: A, rule.py on the trapezoid's "
        "nodes, one field at a time (median of 30), by the bodies in view; B, three bodies, each "
        "engine, one field at a time (lines) and per field in a batch of 128 (points).",
    "curve_data":
        "The rule's table re-estimated from P people of the population named, three bodies: A, share "
        "named exactly; B, share right of those named at 0.99, dotted at 99 per cent; the seven and "
        "all 32, the table taken as printed (nominal) or widened for a new person (predictive).",
}


# ---- reading the record ---------------------------------------------------------------------

def rates_of(tree):
    return tree["rates"].to_dataset()


def value(ds, stat: str, arm: str, phenotype: str, subset: str, width: int) -> float:
    """One rate of the record, NaN where the record is older than the statistic."""
    if stat not in ds:
        return float("nan")
    return float(ds[stat].sel(arm=arm, phenotype=phenotype, subset=subset, width=width))


def pool_of(tree) -> List[dict]:
    return json.loads(tree.attrs["pool"])


def order_of(tree) -> List[str]:
    return json.loads(tree.attrs["order"])


def counts_of(tree) -> dict:
    return json.loads(tree.attrs["counts"])


# ---- formatting -----------------------------------------------------------------------------

def pct(x: float, places: int = 1) -> str:
    """A share as a percentage, one place, or two where it rounds to 100.0 short of all."""
    if not np.isfinite(x):
        return "-"
    s = "%.*f%%" % (places, 100.0 * x)
    if s.startswith("100.0") and x < 1.0:
        s = "%.2f%%" % (100.0 * x)
    return s


def ms(x: float) -> str:
    if not np.isfinite(x):
        return "-"
    return "%.2f" % x if x < 10 else "%.1f" % x if x < 100 else "%.0f" % x


def se_range(xs: Sequence[float]) -> str:
    xs = [100.0 * x for x in xs if np.isfinite(x)]
    if not xs:
        return "not recorded"
    lo, hi = min(xs), max(xs)
    return "%.2f" % hi if abs(hi - lo) < 0.005 else "%.2f to %.2f" % (lo, hi)


def rows_md(header: Sequence[str], align: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(align) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


# ---- the tables -----------------------------------------------------------------------------

def table_curve(tree) -> List[str]:
    ds = rates_of(tree)
    kinds = {m["key"]: m["kind"] for m in pool_of(tree)}
    order = order_of(tree)
    rows, ses = [], []
    for k, key in enumerate(order, 1):
        sub = "prefix-%02d" % k
        cells = [str(k), "`%s`" % key, kinds[key]]
        cells += [pct(value(ds, "exact", "nominal", "typical", sub, n)) for n in WIDTHS]
        for n in (3, 9):
            cells += [pct(value(ds, "answered", "nominal", "typical", sub, n)),
                      pct(value(ds, "precision", "nominal", "typical", sub, n), 2)]
        cells.append(pct(value(ds, "floored", "nominal", "typical", sub, 9)))
        rows.append(cells)
        ses += [value(ds, "exact_se", "nominal", "typical", sub, n) for n in WIDTHS]
    out = rows_md(["Measures", "Added", "Kind", "Named exactly, 1 body", "3 bodies", "9 bodies",
                   "Named at 0.99, 3 bodies", "Right of those", "Named at 0.99, 9 bodies", "Right of those",
                   "Fields with a value at the floor, 9 bodies"],
                  ["---:", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:"], rows)
    n = value(ds, "n_columns", "nominal", "typical", "prefix-01", 1)
    out += ["", "%d typical columns; the standard errors of the shares named exactly, clustered by column, are %s points."
            % (n, se_range(ses))]
    return out


def members_of(tree, sub: str) -> frozenset:
    m = tree["subsets"].to_dataset()["member"].sel(subset=sub)
    return frozenset(np.asarray(m["measure"].values)[np.asarray(m.values, bool)].tolist())


def subset_order(tree) -> List[str]:
    """The named subsets in the table's order, less each rung of the ladder that is another row
    under its own name: the first rung is the seven and the pedicles, the last is all 32."""
    subs = tree["subsets"].to_dataset()["subset"].values.tolist()
    named = ["seven"] + ["seven+" + f for f in FAMILIES] + ["ladder-" + f for f in FAMILIES]
    named += ["lengths", "seven+areas", "seven+angles", "ap", "lateral", "ap+lateral", "all"]
    named = [s for s in named if s in subs]
    others = {members_of(tree, s) for s in named if not s.startswith("ladder-")}
    return [s for s in named if not (s.startswith("ladder-") and members_of(tree, s) in others)]


def joined(names: Sequence[str]) -> str:
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def subset_name(sub: str) -> str:
    if sub.startswith("seven+") and sub[6:] in FAMILY_NAME:
        return "the seven and %s" % FAMILY_NAME[sub[6:]]
    if sub.startswith("ladder-"):
        i = FAMILIES.index(sub[7:])
        return "the seven, " + joined([FAMILY_NAME[f] for f in FAMILIES[:i + 1]])
    return SUBSET_NAME[sub]


def table_subsets(tree) -> List[str]:
    ds = rates_of(tree)
    members = tree["subsets"].to_dataset()
    rows = []
    for sub in subset_order(tree):
        cells = [subset_name(sub), str(int(members["member"].sel(subset=sub).sum()))]
        cells += [pct(value(ds, "exact", "nominal", "typical", sub, n)) for n in WIDTHS]
        cells += [pct(value(ds, "answered", "nominal", "typical", sub, HEADLINE)),
                  pct(value(ds, "precision", "nominal", "typical", sub, HEADLINE), 2)]
        rows.append(cells)
    return rows_md(["Measures scored", "Count", "Named exactly, 1 body", "3 bodies", "9 bodies",
                    "Named at 0.99, 3 bodies", "Right of those"],
                   ["---", "---:", "---:", "---:", "---:", "---:", "---:"], rows)


def arm_names(ds) -> List[str]:
    return [a for a in ds["arm"].values.tolist()]


ARM_NAME = {"nominal": "As assumed", "errors-0.5": "Every error halved, in the columns and the rule",
            "errors-2": "Every error doubled, in the columns and the rule",
            "correlated": "Offsets correlated 0.4 between measures, the rule unaware"}


def table_arms(tree) -> List[str]:
    ds = rates_of(tree)
    rows = []
    for arm in ("nominal", "errors-0.5", "errors-2", "correlated"):
        if arm not in arm_names(ds):
            continue
        cells = [ARM_NAME[arm]]
        for sub in ("seven", "prefix-32"):
            for n in (3, 9):
                cells += [pct(value(ds, "exact", arm, "typical", sub, n)),
                          pct(value(ds, "precision", arm, "typical", sub, n), 2)]
        rows.append(cells)
    return rows_md(["Columns and rule", "Seven, named exactly, 3 bodies", "Right of those named at 0.99",
                    "Seven, 9 bodies", "Right at 0.99", "All 32, 3 bodies", "Right at 0.99", "All 32, 9 bodies",
                    "Right at 0.99"], ["---"] + ["---:"] * 8, rows)


def table_data(tree) -> List[str]:
    ds = rates_of(tree)
    if not any(a.startswith("people-") for a in arm_names(ds)):
        return ["The data axis is not in this record."]
    rows = []
    for people in PEOPLE:
        for rule in ("nominal", "predictive"):
            arm = "people-%d-%s" % (people, rule)
            if arm not in arm_names(ds):
                continue
            settings = json.loads(tree.attrs["settings"]).get(arm, {})
            cells = ["{:,}".format(people), rule, str(settings.get("tables", ""))]
            for sub in ("seven", "prefix-32"):
                cells += [pct(value(ds, "exact", arm, "typical", sub, HEADLINE)),
                          pct(value(ds, "precision", arm, "typical", sub, HEADLINE), 2)]
            sd = value(ds, "exact_table_sd", arm, "typical", "prefix-32", HEADLINE)
            cells.append("-" if not np.isfinite(sd) else "%.1f" % (100.0 * sd))
            rows.append(cells)
    first = next(a for a in arm_names(ds) if a.startswith("people-"))
    n = int(value(ds, "n_columns", first, "typical", "seven", HEADLINE))
    out = rows_md(["People", "Rule", "Tables", "Seven, named exactly, 3 bodies", "Right of those named at 0.99",
                   "All 32, 3 bodies", "Right at 0.99", "Spread of all 32's share between tables, points"],
                  ["---:", "---", "---:", "---:", "---:", "---:", "---:", "---:"], rows)
    out += ["", "Each table is scored on the same %d typical columns, the first of the nominal arm's." % n]
    return out


def table_anomalous(tree) -> List[str]:
    ds = rates_of(tree)
    rows = []
    for ph in ("typical",) + ANOMALOUS:
        cells = [PHENOTYPE_NAME[ph]]
        for sub in ("seven", "prefix-32"):
            for n in (3, 9):
                cells.append("%s / %s" % (pct(value(ds, "exact", "nominal", ph, sub, n)),
                                          pct(value(ds, "within_one", "nominal", ph, sub, n))))
        rows.append(cells)
    return rows_md(["Spine", "Seven, 3 bodies: exact / within one", "Seven, 9 bodies", "All 32, 3 bodies",
                    "All 32, 9 bodies"], ["---", "---:", "---:", "---:", "---:"], rows)


NOT_TIMED = ["The times are not in this record yet: `python -m schwingcheck curve speed --record` writes them."]


def timed(ds) -> bool:
    return bool(np.isfinite(np.asarray(ds[list(ds.data_vars)[0]].values, float)).any())


def table_speed(tree) -> List[str]:
    sp = tree["speed"].to_dataset()
    if not timed(sp):
        return NOT_TIMED
    ks = [k for k in SPEED_MEASURES if k in sp["measures"].values.tolist()]
    rows = []
    for e in sp["engine"].values.tolist():
        for n in sp["width"].values.tolist():
            cells = [ENGINE_NAME.get(e, e), str(n)]
            for k in ks:
                a = float(sp["median_ms"].sel(engine=e, measures=k, width=n))
                b = float(sp["batch_ms"].sel(engine=e, measures=k, width=n))
                cells.append("%s / %s" % (ms(a), ms(b)))
            rows.append(cells)
    return rows_md(["Engine", "Bodies"] + ["%d measure%s" % (k, "" if k == 1 else "s") for k in ks],
                   ["---", "---:"] + ["---:"] * len(ks), rows) + [
        "", "Milliseconds to name one field, single-threaded: alone, the median of 30 calls / per field in a batch of 128."]


def table_nuts(tree) -> List[str]:
    nu = tree["nuts"].to_dataset()
    if not timed(nu):
        return NOT_TIMED
    attrs = json.loads(tree.attrs.get("nuts", "{}"))
    rows = []
    for k in nu["measures"].values.tolist():
        rows.append([str(k), "%.2f" % float(nu["build_s"].sel(measures=k)), "%.1f" % float(nu["sample_s"].sel(measures=k)),
                     "%.2f" % float(nu["posterior_s"].sel(measures=k)), "%.1e" % float(nu["max_abs_diff"].sel(measures=k)),
                     "%.1e" % float(nu["max_mcse"].sel(measures=k))])
    out = rows_md(["Measures", "Build, s a field", "Sample, s a field", "Posterior, s a field",
                   "Largest gap from the exact posterior", "Largest Monte Carlo error"],
                  ["---:"] * 6, rows)
    if attrs:
        a = attrs[next(iter(attrs))]
        out += ["", "NUTS on the naming model, %d fields of %d bodies, %d chains of %d draws after %d tuning steps."
                % (a["fields"], a["width"], a["chains"], a["draws"], a["tune"])]
    return out


def table_floor(tree) -> List[str]:
    if "floor" not in tree.attrs:
        return ["The floor's counts are not in this record, which is older than they are."]
    fl = json.loads(tree.attrs["floor"])
    rows = []
    for key in sorted(fl, key=lambda k: (k.split("/")[1] != "typical", k)):
        arm, ph = key.split("/")
        f = fl[key]
        most = ", ".join("`%s` %d" % kv for kv in list(f["where"].items())[:3]) or "none"
        rows.append([ARM_NAME.get(arm, arm), PHENOTYPE_NAME[ph], "{:,}".format(f["values"]), "{:,}".format(f["of"]),
                     "{:,}".format(f["columns"]), most])
    return rows_md(["Columns", "Spine", "Values at the floor", "Of", "Columns touched", "Most at"],
                   ["---", "---", "---:", "---:", "---:", "---"], rows)


MAKERS = {"curve": table_curve, "subsets": table_subsets, "arms": table_arms, "data": table_data,
          "anomalous": table_anomalous, "speed": table_speed, "nuts": table_nuts, "floor": table_floor}


def block(tree, name: str) -> str:
    return "\n".join(["<!-- curve:%s -->" % name] + MAKERS[name](tree) + ["<!-- /curve:%s -->" % name])


def tables(tree) -> str:
    return "\n\n".join(block(tree, name) for name in TABLES)


def readme_blocks(text: str) -> Dict[str, str]:
    out = {}
    for m in re.finditer(r"<!-- curve:([a-z]+) -->\n.*?\n<!-- /curve:\1 -->", text, re.S):
        out[m.group(1)] = m.group(0)
    return out


def check_readme(tree, readme: str = README) -> List[str]:
    """What differs between the README's tables and the record's: one line per table missing,
    stale or written twice."""
    with open(readme, encoding="ascii") as fh:
        text = fh.read()
    have = readme_blocks(text)
    stale = []
    for name in TABLES:
        want = block(tree, name)
        if text.count("<!-- curve:%s -->" % name) > 1:
            stale.append("table %s: written more than once" % name)
        elif name not in have:
            stale.append("table %s: not in the README" % name)
        elif have[name] != want:
            stale.append("table %s: differs from the record's (python -m schwingcheck curve table)" % name)
    return stale


# ---- the figures ----------------------------------------------------------------------------

def style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "font.family": "serif", "font.serif": SERIF, "font.size": 9.5, "mathtext.fontset": "dejavuserif",
        "text.color": INK, "axes.edgecolor": INK, "axes.labelcolor": INK, "axes.linewidth": 0.8,
        "axes.titlesize": 9.5, "axes.titleweight": "normal", "axes.labelsize": 9,
        "xtick.color": INK, "ytick.color": INK, "xtick.direction": "out", "ytick.direction": "out",
        "xtick.major.width": 0.8, "ytick.major.width": 0.8, "xtick.major.size": 3.5, "ytick.major.size": 3.5,
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
        "legend.frameon": True, "legend.edgecolor": INK, "legend.fancybox": False, "legend.framealpha": 1.0,
        "legend.fontsize": 7.5, "legend.title_fontsize": 7.5,
        "lines.linewidth": 1.1, "lines.markersize": 4.5, "lines.markeredgewidth": 0.9, "lines.color": INK,
        "errorbar.capsize": 2.5, "figure.dpi": 100, "savefig.dpi": PNG_DPI,
        "axes.prop_cycle": matplotlib.cycler(color=[INK]),
    })
    return plt


def letter(ax, text: str, title: str = ""):
    ax.annotate(text, xy=(0, 1), xycoords="axes fraction", xytext=(-6, 5), textcoords="offset points",
                fontsize=12, fontweight="bold", ha="left", va="bottom")
    if title:
        ax.annotate(title, xy=(0, 1), xycoords="axes fraction", xytext=(10, 5), textcoords="offset points",
                    fontsize=9, ha="left", va="bottom")


def body_label(n: int) -> str:
    return "%d bod%s" % (n, "y" if n == 1 else "ies")


def save(fig, outdir: str, name: str, caption: str) -> List[str]:
    import matplotlib.pyplot as plt
    paths = [os.path.join(outdir, name + ".pdf"), os.path.join(outdir, name + ".png")]
    fig.savefig(paths[0], bbox_inches="tight", facecolor="white", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(paths[1], bbox_inches="tight", facecolor="white")
    plt.close(fig)
    p = os.path.join(outdir, name + ".caption.txt")
    with open(p, "w", encoding="ascii", newline="\n") as fh:
        fh.write(caption.strip() + "\n")
    return paths + [p]


def write_csv(outdir: str, name: str, rows: List[dict]) -> str:
    path = os.path.join(outdir, name + ".csv")
    with open(path, "w", encoding="ascii", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: format(v, ".6g") if isinstance(v, float) else v for k, v in r.items()})
    return path


def fig_accuracy(tree, outdir: str) -> List[str]:
    plt = style()
    ds = rates_of(tree)
    ks = list(range(1, len(order_of(tree)) + 1))
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), constrained_layout=True)
    rows = []
    for ax, stat, title in zip(axes, ("exact", "answered", "precision"),
                               ("Named exactly", "Named at 0.99", "Right of those named")):
        for n in WIDTHS:
            ys = [100 * value(ds, stat, "nominal", "typical", "prefix-%02d" % k, n) for k in ks]
            ax.plot(ks, ys, color=INK, label=body_label(n), markersize=2.6, **WIDTH_STYLE[n])
            seven = 100 * value(ds, stat, "nominal", "typical", "seven", n)
            ax.plot([7], [seven], linestyle="none", marker="x", color=INK, markersize=5)
            for k, y in zip(ks, ys):
                rows.append({"panel": title, "bodies": n, "measures": k, "subset": "prefix-%02d" % k, "percent": y})
            rows.append({"panel": title, "bodies": n, "measures": 7, "subset": "seven", "percent": seven})
        ax.set_xlabel("Measures")
        ax.set_xlim(0, ks[-1] + 1)
        letter(ax, "ABC"["exact answered precision".split().index(stat)], title)
        if stat == "precision":
            ax.axhline(99.0, color=INK, linewidth=0.5, linestyle=":")
    axes[0].set_ylabel("Per cent of fields")
    axes[1].set_ylabel("Per cent of fields")
    axes[2].set_ylabel("Per cent right")
    axes[0].plot([], [], linestyle="none", marker="x", color=INK, markersize=5, label="the seven")
    axes[0].legend(loc="lower right")
    name = "curve_accuracy"
    caption = CAPTIONS[name] % int(value(ds, "n_columns", "nominal", "typical", "prefix-01", 1))
    return save(fig, outdir, name, caption) + [write_csv(outdir, name, rows)]


def fig_speed(tree, outdir: str) -> List[str]:
    plt = style()
    sp = tree["speed"].to_dataset()
    ks = sp["measures"].values.tolist()
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.6), constrained_layout=True)
    rows = []
    for n in sp["width"].values.tolist():
        ys = [float(sp["median_ms"].sel(engine="numpy-trapezoid", measures=k, width=n)) for k in ks]
        a.plot(ks, ys, color=INK, label=body_label(n), markersize=2.6, **WIDTH_STYLE.get(n, {}))
        rows += [{"panel": "A", "engine": "numpy-trapezoid", "bodies": n, "measures": k, "how": "alone", "ms": y}
                 for k, y in zip(ks, ys)]
    for e in sp["engine"].values.tolist():
        ys = [float(sp["median_ms"].sel(engine=e, measures=k, width=HEADLINE)) for k in ks]
        zs = [float(sp["batch_ms"].sel(engine=e, measures=k, width=HEADLINE)) for k in ks]
        st = dict(ENGINE_STYLE[e])
        b.plot(ks, ys, color=INK, label=ENGINE_NAME[e], markersize=2.6, **st)
        b.plot(ks, zs, color=INK, linestyle="none", marker=st["marker"], markerfacecolor=st["markerfacecolor"], markersize=2.6)
        rows += [{"panel": "B", "engine": e, "bodies": HEADLINE, "measures": k, "how": "alone", "ms": y} for k, y in zip(ks, ys)]
        rows += [{"panel": "B", "engine": e, "bodies": HEADLINE, "measures": k, "how": "in a batch", "ms": z} for k, z in zip(ks, zs)]
    for ax in (a, b):
        ax.set_yscale("log")
        ax.set_xlabel("Measures")
        ax.set_ylabel("Milliseconds a field")
    letter(a, "A", "rule.py, one field at a time")
    letter(b, "B", "Three bodies, each engine")
    a.legend(loc="upper left")
    b.legend(loc="lower right")
    name = "curve_speed"
    return save(fig, outdir, name, CAPTIONS[name]) + [write_csv(outdir, name, rows)]


def fig_data(tree, outdir: str) -> List[str]:
    plt = style()
    ds = rates_of(tree)
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.6), layout="constrained")
    rows = []
    styles = {("seven", "nominal"): dict(linestyle="--", marker="s", markerfacecolor="white"),
              ("seven", "predictive"): dict(linestyle=":", marker="^", markerfacecolor="white"),
              ("prefix-32", "nominal"): dict(linestyle="-", marker="o", markerfacecolor=INK),
              ("prefix-32", "predictive"): dict(linestyle="-.", marker="D", markerfacecolor=INK, markersize=3)}
    people = [p for p in PEOPLE if "people-%d-nominal" % p in arm_names(ds)]
    for (sub, rule), st in styles.items():
        label = "%s, %s" % ("Seven" if sub == "seven" else "All 32", rule)
        for ax, stat in ((a, "exact"), (b, "precision")):
            ys = [100 * value(ds, stat, "people-%d-%s" % (p, rule), "typical", sub, HEADLINE) for p in people]
            ax.plot(people, ys, color=INK, label=label, **st)
            rows += [{"panel": "A" if stat == "exact" else "B", "subset": sub, "rule": rule, "people": p, "percent": y}
                     for p, y in zip(people, ys)]
    for ax in (a, b):
        ax.set_xscale("log")
        ax.set_xticks(people)
        ax.set_xticklabels(["{:,}".format(p) for p in people])
        ax.set_xlabel("People the table is estimated from")
    a.set_ylabel("Per cent named exactly")
    b.set_ylabel("Per cent right")
    b.axhline(99.0, color=INK, linewidth=0.5, linestyle=":")
    letter(a, "A", "Named exactly")
    letter(b, "B", "Right of those named at 0.99")
    fig.legend(*a.get_legend_handles_labels(), loc="outside right center")
    name = "curve_data"
    return save(fig, outdir, name, CAPTIONS[name]) + [write_csv(outdir, name, rows)]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_figures_md(outdir: str, record: str, written: List[str]) -> str:
    import matplotlib
    here = os.path.dirname(os.path.abspath(__file__))
    lines = ["# The build-up study's figures", "",
             "Built with `python -m schwingcheck curve figures --record %s --outdir %s`."
             % (os.path.relpath(record, T.ROOT), os.path.relpath(outdir, T.ROOT)), "",
             "- Record: `%s`, sha256 %s." % (os.path.relpath(record, T.ROOT), sha256(record))]
    for name in ("curve_report.py", "curve.py"):
        lines.append("- Code: `schwingcheck/%s`, sha256 %s." % (name, sha256(os.path.join(here, name))))
    lines += ["- Python %s, numpy %s, matplotlib %s; serif type %s, embedded in the PDF."
              % (platform.python_version(), np.__version__, matplotlib.__version__, SERIF[0]),
              "- The PDFs carry no creation date, so a rebuild with the same versions gives the same files; the CSVs "
              "beside them hold every number drawn.", "",
              "| Figure | Files | Caption |", "|---|---|---|"]
    names = list(dict.fromkeys(os.path.basename(p).split(".")[0] for p in written))
    for name in names:
        files = sorted(f for f in os.listdir(outdir) if f.split(".")[0] == name)
        with open(os.path.join(outdir, name + ".caption.txt"), encoding="ascii") as fh:
            caption = fh.read().strip().replace("|", "/")
        lines.append("| %s | %s | %s |" % (name, ", ".join("`%s`" % f for f in files), caption))
    path = os.path.join(outdir, "FIGURES.md")
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def draw_figures(tree, outdir: str, record: Optional[str] = None) -> List[str]:
    os.makedirs(outdir, exist_ok=True)
    written = fig_accuracy(tree, outdir)
    if timed(tree["speed"].to_dataset()):
        written += fig_speed(tree, outdir)
    if any(a.startswith("people-") for a in arm_names(rates_of(tree))):
        written += fig_data(tree, outdir)
    if record:
        written.append(write_figures_md(outdir, record, written))
    return written
