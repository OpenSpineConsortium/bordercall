"""Every place one of the four Panjabi papers disagrees with itself, from the provenance record.

    python contradictions.py     # writes CONTRADICTIONS.md beside this file

The owner asked on 27 October 2026 for a report of all the contradictions in the papers
between tables, to be used as a measure of how carefully the papers' numbers were carried from
the measurement tables into the rest of each paper. Three records feed it, all held by test to
the cell images (README.md): crosstable.csv, each comparison table's Present Study column
against the dimension tables it restates; prose.csv, every number the running text states
against the cells it speaks of; and the arithmetic inside the tables themselves, computed here
from provenance.csv, the printed ratio columns against the ratio of the printed means and the
printed sums (the thoracic wedge angle, the rib articulation totals) against the sum of their
parts, and one relation between two tables of the facets paper, its X-card angle against the
negative of its transverse-plane angle. A printed ratio, sum or relation is consistent when some
unrounded means inside the rounding of the printed ones give a value that rounds to it; the
report lists those that are not, with the size of the difference. Each contradiction of the first two records carries a kind, assigned by
hand in KINDS below from what the cells show, so the summary can count them by what happened.
Nothing here speaks of the measurements' accuracy, which no record of a paper can test.
"""
from __future__ import annotations

import csv
import os
import sys
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import check_prose  # noqa: E402

PAPERS = ["cervical", "thoracic", "lumbar", "facets"]
TITLES = {"cervical": "Cervical, Spine 1991;16(8):861-869", "thoracic": "Thoracic, Spine 1991;16(8):888-901",
          "lumbar": "Lumbar, Spine 1992;17(3):299-306", "facets": "Articular facets, Spine 1993;18(10):1298-1310"}

# a printed ratio column: the means it divides, each side the mean of the measures listed
RATIO_PARTS: Dict[str, Tuple[List[str], List[str]]] = {
    "EPWu/EPDu": (["EPWu"], ["EPDu"]), "EPWl/EPDl": (["EPWl"], ["EPDl"]), "SCW/SCD": (["SCW"], ["SCD"]),
    "PDHr/PDWr": (["PDHr"], ["PDWr"]), "PDHl/PDWl": (["PDHl"], ["PDWl"]),
    "PDH/PDWr": (["PDHr"], ["PDWr"]), "PDH/PDWl": (["PDHl"], ["PDWl"]),
    "FCW/FCHsr": (["FCWsr"], ["FCHsr"]), "FCW/FCHsl": (["FCWsl"], ["FCHsl"]),
    "FCW/FCHir": (["FCWir"], ["FCHir"]), "FCW/FCHil": (["FCWil"], ["FCHil"]),
    "IFWs/IFWi": (["IFWs"], ["IFWi"]), "IFW/IFH": (["IFWs", "IFWi"], ["IFHr", "IFHl"]),
}
# a printed sum: the terms it adds, each the mean of the measures listed (a pair printed as
# dashes, the lower costovertebral facets at T11 and T12 and the costotransverse at T12, adds
# nothing, since those ribs have no such facet)
SUM_PARTS: Dict[Tuple[str, str], List[List[str]]] = {
    ("thoracic-t3", "EPIt"): [["EPItu"], ["EPItl"]],
    ("thoracic-t6", "CVA"): [["CVAur", "CVAul"], ["CVAlr", "CVAll"]],
    ("thoracic-t6", "CVA + CTA"): [["CVA"], ["CTAr", "CTAl"]],
}
SUM_WORDS = {("thoracic-t3", "EPIt"): "EPItu + EPItl",
             ("thoracic-t6", "CVA"): "mean(CVAur, CVAul) + mean(CVAlr, CVAll)",
             ("thoracic-t6", "CVA + CTA"): "CVA + mean(CTAr, CTAl)"}
# a column of one table that the printed values of another table of the same paper give: the
# facets paper's X-card angle CAX (its Table 8) is, cell for cell, the negative of its
# transverse-plane angle T (Tables 6 and 7) on the same side of the same facet, which is why the
# rule scores T and never CAX (TODO.md, item P step e); the check says where the cells break it
RELATION_PARTS: Dict[Tuple[str, str], Tuple[str, str, float]] = {
    ("facets-t8", "CAXsr"): ("facets-t6", "Tsr", -1.0), ("facets-t8", "CAXsl"): ("facets-t6", "Tsl", -1.0),
    ("facets-t8", "CAXir"): ("facets-t7", "Tir", -1.0), ("facets-t8", "CAXil"): ("facets-t7", "Til", -1.0),
}

ONE_SIDE = "one side of a right-left pair quoted as the value"
NO_SUCH = "a figure no table prints"
AVERAGE = "the average of the upper and lower increases given as one of them"
ROUND = "a round figure the table's value does not round to"
RANGE_END = "a range whose end is not the table's extreme"
DIGIT = "one digit off"
NOT_MEAN = "a restated mean that is not the mean of the printed sides"
# (paper, printed page, measure, level, printed) of each prose contradiction, and what the cells show
PROSE_KINDS = {
    ("lumbar", "301", "PDW", "L5", "18.9"): NO_SUCH,
    ("lumbar", "302", "PIA", "L5", "81"): NO_SUCH,
    ("thoracic", "890", "EPWl T12 over T1", "T1-T12", "55"): AVERAGE,
    ("thoracic", "890", "EPDu T12 over T1", "T1-T12", "73"): AVERAGE,
    ("thoracic", "890", "VBHp", "T1", "14.3"): NO_SUCH,
    ("thoracic", "891", "SCA", "T3", "189"): NO_SUCH,
    ("thoracic", "893", "PIA", "T3", "90"): ROUND,
    ("thoracic", "893", "PIA", "T12", "98"): ONE_SIDE,
    ("facets", "1298", "FCW", "C3-L5", "9.6"): RANGE_END,
    ("facets", "1298", "FCA", "C3-L5", "72.3"): RANGE_END,
    ("facets", "1298", "CAY", "C3-L5", "5.8"): RANGE_END,
    ("facets", "1305", "CAXs", "C2", "-41"): ONE_SIDE,
    ("facets", "1307", "CAYsr", "C5", "+9.8"): NO_SUCH,
    ("facets", "1307", "Ts", "C2-C7", "50"): RANGE_END,
    ("facets", "1307", "Ts", "L5", "80"): ROUND,
    # the summary of the twelve spines the three later papers print in their Methods, against the
    # thoracic paper's Table 1: the cervical paper names that study for its specimens' details, and
    # the lumbar and facets papers refer to it for their methods and print the same summary
    ("cervical", "861", "weight", "", "85"): RANGE_END,
    ("lumbar", "299", "weight", "", "85"): RANGE_END,
    ("facets", "1299", "weight", "", "85"): RANGE_END,
}
# the comparison-table cell of each disagreement between tables
CROSS_KINDS = {
    "thoracic-t8a/r03_c01/mean": DIGIT,
    "lumbar-t6/r40_c01/mean": NOT_MEAN,
    "facets-t9/r02_c01/mean": NOT_MEAN, "facets-t9/r03_c01/mean": NOT_MEAN, "facets-t9/r04_c01/mean": NOT_MEAN,
    "facets-t9/r05_c01/mean": NOT_MEAN, "facets-t9/r08_c01/mean": NOT_MEAN, "facets-t9/r11_c01/mean": NOT_MEAN,
}


def read_csv(name: str) -> List[dict]:
    with open(os.path.join(HERE, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def decimals_of(printed: str, value: str) -> int:
    """How many decimals the number was printed with: those of the token of the printed string
    that is this value (a `mean +/- SEM` cell prints two numbers)."""
    for tok in printed.replace("+/-", " ").replace("(", " ").replace(")", " ").replace(",", " ").split():
        try:
            if abs(float(tok) - float(value)) < 1e-9:
                return len(tok.split(".")[1]) if "." in tok else 0
        except ValueError:
            continue
    return len(value.split(".")[1]) if "." in value else 0


def half_unit(row: dict) -> float:
    return 0.5 * 10.0 ** -decimals_of(row["printed"], row["value"])


def fmt(x: float, decimals: int = 2) -> str:
    s = "%.*f" % (decimals, x)
    return s.rstrip("0").rstrip(".") if "." in s else s


def table_name(key: str) -> str:
    paper, t = key.split("-t")
    return "%s Table %s" % (paper, t.upper() if t[-1].isalpha() else t)


def image(cell_id: str) -> str:
    table, cell = cell_id.rsplit("/", 1)[0].split("/")
    return "[%s](cells/%s/%s.png)" % (cell, table, cell)


# ---- the arithmetic inside the tables ------------------------------------------------------------

class Interval:
    """A printed number as the range of unrounded numbers that print as it."""
    def __init__(self, lo: float, hi: float):
        self.lo, self.hi = lo, hi

    @staticmethod
    def of(row: dict) -> "Interval":
        v, h = float(row["value"]), half_unit(row)
        return Interval(v - h, v + h)

    def __add__(self, o: "Interval") -> "Interval":
        return Interval(self.lo + o.lo, self.hi + o.hi)

    def scale(self, c: float) -> "Interval":
        return Interval(self.lo * c, self.hi * c)

    def over(self, o: "Interval") -> "Interval":
        return Interval(self.lo / o.hi, self.hi / o.lo)

    def meets(self, o: "Interval") -> bool:
        return self.lo <= o.hi + 1e-9 and o.lo <= self.hi + 1e-9


def mean_of(rows: List[dict]) -> Tuple[float, Interval]:
    v = sum(float(r["value"]) for r in rows) / len(rows)
    iv = Interval(0.0, 0.0)
    for r in rows:
        iv = iv + Interval.of(r).scale(1.0 / len(rows))
    return v, iv


def cells_at(index: Dict[tuple, dict], table: str, measures: List[str], level: str) -> List[dict]:
    out = []
    for m in measures:
        r = index.get((table, m, level, "mean"))
        if r is not None and r["value"] != "":
            out.append(r)
    return out


def derived(prov: List[dict]) -> List[dict]:
    """Every printed ratio and sum beside what its own table's means give."""
    index = {(r["table"], r["measure"], r["level"], r["statistic"]): r for r in prov if r["study"] == "present"}
    out = []
    for r in prov:
        if r["study"] != "present" or r["value"] == "":
            continue
        if r["statistic"] == "ratio":
            num, den = RATIO_PARTS[r["measure"]]
            a, b = cells_at(index, r["table"], num, r["level"]), cells_at(index, r["table"], den, r["level"])
            if not a or not b:
                continue
            va, ia = mean_of(a)
            vb, ib = mean_of(b)
            computed, iv = va / vb, ia.over(ib)
            parts = "%s / %s" % (" and ".join("%s %s" % (c["measure"], c["value"]) for c in a),
                                 " and ".join("%s %s" % (c["measure"], c["value"]) for c in b))
            kind = "ratio"
        elif (r["table"], r["measure"]) in SUM_PARTS and r["statistic"] == "mean":
            computed, iv, words = 0.0, Interval(0.0, 0.0), []
            for term in SUM_PARTS[(r["table"], r["measure"])]:
                cs = cells_at(index, r["table"], term, r["level"])
                if not cs:
                    words.append("no %s" % "/".join(term))
                    continue
                v, i = mean_of(cs)
                computed, iv = computed + v, iv + i
                words.append(" and ".join("%s %s" % (c["measure"], c["value"]) for c in cs))
            parts = " + ".join(words)
            kind = "sum"
        elif (r["table"], r["measure"]) in RELATION_PARTS and r["statistic"] == "mean":
            table, measure, factor = RELATION_PARTS[(r["table"], r["measure"])]
            cs = cells_at(index, table, [measure], r["level"])
            if not cs:
                continue
            v, i = mean_of(cs)
            computed = factor * v
            iv = Interval(min(factor * i.lo, factor * i.hi), max(factor * i.lo, factor * i.hi))
            parts = "%s %s of %s" % (measure, cs[0]["value"], table_name(table))
            kind = "relation"
        else:
            continue
        printed = float(r["value"])
        out.append({"kind": kind, "table": r["table"], "measure": r["measure"], "level": r["level"], "cell": r["id"],
                    "printed": printed, "half": half_unit(r), "computed": computed, "lo": iv.lo, "hi": iv.hi,
                    "difference": printed - computed, "parts": parts,
                    "agrees": "yes" if iv.meets(Interval(printed - half_unit(r), printed + half_unit(r))) else "no"})
    return out


def relation_words(table: str, measure: str) -> str:
    """How the report names a relation's other column, or nothing for a column that is not one."""
    if (table, measure) not in RELATION_PARTS:
        return ""
    other_table, other, factor = RELATION_PARTS[(table, measure)]
    return "%s%s of %s" % ("minus " if factor < 0 else "", other, table_name(other_table))


def consistent(c: dict) -> bool:
    return Interval(c["lo"], c["hi"]).meets(Interval(c["printed"] - c["half"], c["printed"] + c["half"]))


# ---- the report ----------------------------------------------------------------------------------

def prose_computed(prov_index: Dict[str, dict], p: dict) -> float:
    return check_prose.evaluate(p["rule"], check_prose.cell_values(prov_index, p["cells"], p["rule"]))


def says(p: dict) -> str:
    """What a prose row says, as measure, level and the number printed; a specimen's age or weight
    speaks of no level."""
    return " ".join(x for x in (p["measure"], p["level"], p["printed"]) if x)


def paper_of_cross(r: dict) -> str:
    return r["comparison"].split("-")[0]


def relative(d: float, base: float) -> str:
    return "%.1f%%" % (100.0 * abs(d) / abs(base)) if base else "-"


def report() -> str:
    prov = read_csv("provenance.csv")
    prov_index = {r["id"]: r for r in prov}
    prose = read_csv("prose.csv")
    cross = read_csv("crosstable.csv")
    checks = derived(prov)
    out: List[str] = []
    w = out.append

    w("# Where the four Panjabi papers contradict themselves\n")
    w("Written by `python3 contradictions.py` from the provenance record of 27 October 2026 (README.md), for the owner's")
    w("ask of that day: a report of all the contradictions in the papers between tables, as a measure of how carefully")
    w("the numbers were carried from the measurement tables into the rest of each paper. Three records feed it, each")
    w("held by test to the images of the cells: [crosstable.csv](crosstable.csv), the Present Study column of every")
    w("comparison table against the dimension tables it restates; [prose.csv](prose.csv), every number the running")
    w("text states against the cells it speaks of; and the arithmetic inside the tables, computed here, the printed")
    w("ratio columns against the ratio of the printed means, the printed sums against their parts and the facets")
    w("paper's X-card angle against its transverse-plane angle. A ratio, a sum or a relation is consistent when some")
    w("unrounded means inside the rounding of the printed ones give a value that rounds to the printed one, so a")
    w("difference that rounding alone explains is not a contradiction. Nothing here speaks of")
    w("the measurements' accuracy, which no record of a paper can test; it speaks of the papers' internal")
    w("consistency, which is what a reader has.\n")

    # summary
    w("## Summary\n")
    w("| paper | cells read | text values | held to cells | contradict | within a stated tolerance only | restated by a comparison table | disagree | ratios, sums and relations checked | inconsistent |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    totals = [0] * 9
    loose: List[Tuple[dict, float]] = []
    for paper in PAPERS:
        cells = len({r["id"].rsplit("/", 1)[0] for r in prov if r["paper"] == paper})
        ps = [p for p in prose if p["paper"] == paper]
        held = [p for p in ps if p["cells"]]
        contra = [p for p in held if p["agrees"] == "no"]
        approx = []
        for p in held:
            if p["agrees"] != "yes":
                continue
            got = prose_computed(prov_index, p)
            h = 0.5 * 10.0 ** -(len(p["printed"].split(".")[1]) if "." in p["printed"] else 0)
            if abs(got - float(p["value"])) > h + 1e-9:
                approx.append(p)
                loose.append((p, got))
        cs = [r for r in cross if paper_of_cross(r) == paper and r["agrees"] != ""]
        dis = [r for r in cs if r["agrees"] == "no"]
        ds = [c for c in checks if c["table"].startswith(paper + "-")]
        inc = [c for c in ds if c["agrees"] == "no"]
        row = [cells, len(ps), len(held), len(contra), len(approx), len(cs), len(dis), len(ds), len(inc)]
        totals = [t + x for t, x in zip(totals, row)]
        w("| %s | %s |" % (TITLES[paper], " | ".join(str(x) for x in row)))
    w("| all four | %s |\n" % " | ".join(str(x) for x in totals))
    kinds: Dict[str, int] = {}
    for p in prose:
        if p["agrees"] == "no":
            k = PROSE_KINDS[(p["paper"], p["printed_page"], p["measure"], p["level"], p["printed"])]
            kinds[k] = kinds.get(k, 0) + 1
    for r in cross:
        if r["agrees"] == "no":
            k = CROSS_KINDS[r["comparison"]]
            kinds[k] = kinds.get(k, 0) + 1
    w("The %d contradictions of the text and the comparison tables, by what the cells show:\n" % sum(kinds.values()))
    w("| what happened | count |")
    w("|---|---|")
    for k, n in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0])):
        w("| %s | %d |" % (k, n))
    w("")

    # between tables
    w("## Between tables: the comparison tables against the dimension tables\n")
    w("Each paper's comparison table restates its own means beside earlier studies' (cervical Table 7, thoracic Table 8,")
    w("lumbar Table 6, facets Tables 9 and 10). crosstable.csv holds every restated value to the dimension table it comes")
    w("from: a single-sided dimension to the digit, a paired one as the mean of right and left to the comparison table's")
    w("rounding. Those that do not hold:\n")
    w("| comparison table | level | measure | prints | the dimension table gives | difference | what happened | cells |")
    w("|---|---|---|---|---|---|---|---|")
    for r in cross:
        if r["agrees"] != "no":
            continue
        d = float(r["restated"]) - float(r["value"])
        w("| %s | %s | %s | %s | %s (%s) | %s (%s) | %s | %s; %s |" % (
            table_name(r["comparison"].split("/")[0]), r["level"], r["measure"], r["restated"], fmt(float(r["value"])),
            r["rule"].replace("lr_mean", "mean of right and left").replace("equal", "the cell"),
            fmt(d, 2), relative(d, float(r["value"])), CROSS_KINDS[r["comparison"]],
            image(r["comparison"]), " ".join(image(c) for c in r["cells"].split(";"))))
    unheld = [r for r in cross if r["agrees"] == ""]
    for r in unheld:
        w("\nNot held to anything: %s at %s, %s (%s)." % (table_name(r["comparison"].split("/")[0]), r["level"], r["measure"], r["note"]))
    w("")

    # text against tables
    w("## The text against the tables\n")
    w("prose.csv holds every number the four papers state in their abstracts, results, discussions and figure labels")
    w("to the cells the sentence speaks of, under the rule the sentence states (one cell's value, the mean of right and")
    w("left, the end of a run, a ratio, a percentage, a count of rows) and a tolerance set for the sentence's own")
    w("rounding. The summary of the twelve spines that the cervical, lumbar and facets papers each print in their")
    w("Methods is held to the thoracic paper's Table 1, since the cervical paper names that study for its specimens'")
    w("details and the lumbar and facets papers refer to it for their methods and print the same summary to the")
    w("decimal, so the one number of it that does not hold, printed alike in all three, contradicts the first paper")
    w("rather than its own tables. Those that do not hold:\n")
    w("| paper, page | the sentence | says | the table gives | difference | what happened | cells |")
    w("|---|---|---|---|---|---|---|")
    for p in prose:
        if p["agrees"] != "no":
            continue
        got = prose_computed(prov_index, p)
        d = float(p["value"]) - got
        w("| %s, %s | %s | %s | %s (%s) | %s (%s) | %s | %s |" % (
            p["paper"], p["printed_page"], p["quote"].replace("|", "/"), says(p),
            fmt(got, 2), p["rule"], fmt(d, 2), relative(d, got),
            PROSE_KINDS[(p["paper"], p["printed_page"], p["measure"], p["level"], p["printed"])],
            " ".join(image(c) for c in p["cells"].split(";"))))
    w("")
    w("Numbers the text rounds or approximates, held by the tolerance stated in prose.csv and not by the rounding of")
    w("the digits printed (%d):\n" % len(loose))
    w("| paper, page | the sentence | says | the table gives | difference |")
    w("|---|---|---|---|---|")
    for p, got in loose:
        w("| %s, %s | %s | %s | %s (%s) | %s |" % (p["paper"], p["printed_page"], p["quote"].replace("|", "/"),
                                                  says(p), fmt(got, 2), p["rule"], fmt(float(p["value"]) - got, 2)))
    w("")

    # inside the tables
    w("## Inside the tables: the printed ratios, sums and relations against their parts\n")
    w("Every ratio column (end-plate width to depth, canal width to depth, pedicle height to width, facet width to height,")
    w("the interfacet ratios) and every printed sum (the thoracic wedge angle EPIt = EPItu + EPItl, Table 6's")
    w("costovertebral area per rib as the mean of the two upper facets plus the mean of the two lower, and its total")
    w("with the costotransverse area) is computed from the printed means of its own table. One column is held to")
    w("another table of its paper: the facets paper's X-card angle CAX (Table 8) is, cell for cell, the negative of its")
    w("transverse-plane angle T (Tables 6 and 7) on the same side of the same facet, which is why the rule scores T and")
    w("never CAX. Consistent means that unrounded means inside the printed ones' rounding can give the printed value.\n")
    w("| table | column | computed from | checked | consistent | not | largest difference |")
    w("|---|---|---|---|---|---|---|")
    groups: Dict[Tuple[str, str], List[dict]] = {}
    for c in checks:
        groups.setdefault((c["table"], c["measure"]), []).append(c)
    for (table, measure), cs in groups.items():
        bad = [c for c in cs if c["agrees"] == "no"]
        largest = max(cs, key=lambda c: abs(c["difference"]))
        words = SUM_WORDS.get((table, measure)) or relation_words(table, measure) or \
            "mean(%s) / mean(%s)" % tuple(", ".join(s) for s in RATIO_PARTS[measure])
        w("| %s | %s | %s | %d | %d | %d | %s at %s |" % (table_name(table), measure, words.replace("mean(", "").replace(")", "") if "," not in words else words,
                                                         len(cs), len(cs) - len(bad), len(bad), fmt(largest["difference"], 3), largest["level"]))
    w("")
    bad = [c for c in checks if c["agrees"] == "no"]
    w("The %d that rounding does not explain:\n" % len(bad))
    w("| table | column | level | prints | its parts give | difference | from | cell |")
    w("|---|---|---|---|---|---|---|---|")
    for c in bad:
        w("| %s | %s | %s | %s | %s | %s (%s) | %s | %s |" % (table_name(c["table"]), c["measure"], c["level"], fmt(c["printed"], 3),
                                                            fmt(c["computed"], 3), fmt(c["difference"], 3), relative(c["difference"], c["computed"]),
                                                            c["parts"], image(c["cell"])))
    w("")

    # what the counts say
    n_held, n_contra, n_cross, n_dis, n_checked, n_inc = totals[2], totals[3], totals[5], totals[6], totals[7], totals[8]
    w("## What the counts say\n")
    arith = [c for c in bad if c["kind"] != "relation"]
    worst = max(arith, key=lambda c: abs(c["difference"])) if arith else None
    n_arith = sum(1 for c in checks if c["kind"] != "relation")
    w("- The dimension tables are arithmetically whole but for %d entries: of the %d ratios and sums they print, %d" % (len(arith), n_arith, n_arith - len(arith)))
    w("  are what their own printed means give once rounding is allowed for, which is what columns computed from the")
    w("  unrounded means look like, since a ratio of two means printed to one decimal cannot be read back exactly.")
    if worst:
        w("  The %d that are not differ by %s to %s, the largest %s at %s, printed %s where %s gives %s." % (
            len(arith), fmt(min(abs(c["difference"]) for c in arith), 3), fmt(abs(worst["difference"]), 3), worst["measure"],
            table_name(worst["table"]) + " " + worst["level"], fmt(worst["printed"], 3), worst["parts"], fmt(worst["computed"], 3)))
    rel = [c for c in checks if c["kind"] == "relation"]
    rel_bad = [c for c in rel if c["agrees"] == "no"]
    w("- The facets paper's X-card angle is the negative of its transverse-plane angle at %d of the %d cells where both" % (len(rel) - len(rel_bad), len(rel)))
    w("  are printed, to the printed digit or within the two cells' rounding.%s" % ("" if not rel_bad else " Where it is not:"))
    for c in rel_bad:
        w("  %s %s at %s, printed %s where %s gives %s, %s degrees apart, the paper's own contradiction." % (
            table_name(c["table"]), c["measure"], c["level"], fmt(c["printed"], 1), c["parts"], fmt(c["computed"], 1), fmt(abs(c["difference"]), 1)))
    w("- The comparison tables restate %d values and get %d wrong (%.1f%%): one digit in the thoracic Table 8, and" % (n_cross, n_dis, 100.0 * n_dis / n_cross))
    w("  %d right-and-left means the lumbar Table 6 and the facets Table 9 print that are not the mean of the" % (n_dis - 1))
    w("  sides their own tables print, with no word on how they were formed; the largest is %s mm." % (
        fmt(max(abs(float(r["restated"]) - float(r["value"])) for r in cross if r["agrees"] == "no"), 2)))
    w("- The running text states %d numbers the tables also hold and contradicts them %d times (%.1f%%): a side of a" % (n_held, n_contra, 100.0 * n_contra / n_held))
    w("  pair given as the value, a range whose end is not the table's extreme, an average given as one of its parts,")
    w("  a round figure past rounding, and figures no table prints, as the kinds above count them. No contradiction")
    w("  changes a table's value: the tables are the record of the measurements and the text restates them, so")
    w("  where the two differ the table stands.")
    w("- What this can be used for: these rates are the papers' own record of how often a number was carried wrongly")
    w("  from a measurement table into a sentence or a comparison table, and so a prior on the error of any hand copy")
    w("  of such a table, including the transcriptions this repository checks (README.md). They say nothing about the")
    w("  measurements: the standard errors in the tables are the papers' own statement of that, from twelve")
    w("  specimens, and only a re-measurement could test them.")
    w("")
    return "\n".join(out)


def main() -> int:
    text = report()
    with open(os.path.join(HERE, "CONTRADICTIONS.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    checks = derived(read_csv("provenance.csv"))
    print("CONTRADICTIONS.md: %d ratios, sums and relations checked, %d inconsistent" % (len(checks), sum(1 for c in checks if c["agrees"] == "no")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
