"""Set what the two reading passes read beside every cell, and write the provenance.

    python compile.py            # provenance.csv, reads/pass1.csv, reads/pass2.csv, tables/*.md
    python compile.py disagree   # the cells the two passes read differently, as re-read jobs

The cells come from layout.py (cells.csv, one box per run of ink inside a table), the
strings from the reading passes (README.md: rendered pages read by eye, twice, never by text
extraction). Pass 1 read strips of whole rows with the column headings above them; pass 2
read sheets of numbered cell crops with no headings, so it could not be led by a neighbour.
Each pass's reads are kept as they were made, round by round, in reads/pass1.csv and
reads/pass2.csv; a cell the passes disagreed on was cut out again and read again by fresh
readers of both kinds, and the later round stands beside the earlier one, so the record
shows what was read first and what settled it.

A cell holds one printed value, or two where the paper prints "mean +/- SEM" or "mean (SEM)"
in one cell: provenance.csv carries one row per value, both rows pointing at the same box.
A dash is a printed symbol and not a value; it keeps its row with an empty value, since the
papers print it where a dimension does not exist (C2's upper end-plate) and a reader of the
CSVs needs to know that the absence was read, not missed.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tables  # noqa: E402
from render import OUT, PAPERS  # noqa: E402

READS_IN = os.path.join(OUT, "reads")          # what the reading agents wrote (scratch)
READS = os.path.join(HERE, "reads")            # the record kept in git
TABLES_MD = os.path.join(HERE, "tables")

CELL_FIELDS = ["table", "row", "col", "row_label", "col_label", "measure", "level",
               "statistic", "fmt", "x0", "y0", "x1", "y1", "image"]
PROVENANCE_FIELDS = ["id", "paper", "file", "sha256", "pdf_page", "printed_page", "table",
                     "title", "row", "col", "row_label", "col_label", "study", "measure",
                     "level", "statistic", "fmt", "printed", "value", "units", "kind",
                     "dpi", "x0", "y0", "x1", "y1", "image", "pass1", "pass2", "agree", "note"]
READ_FIELDS = ["table", "cell", "round", "read", "source"]

NUMBER = r"[-+]?\d+(?:\.\d+)?"
RE_NUM = re.compile(r"^(%s)(.*)$" % NUMBER)
RE_PM = re.compile(r"^(%s)\s*\+/-\s*(%s)(.*)$" % (NUMBER, NUMBER))
# a dagger, with or without the levels it refers to, printed between the mean and its +/-,
# as the lumbar tables set it: "46.6^ (L1) +/- 1.20"; the mark goes into the note
RE_PM_MARKED = re.compile(r"^(%s)\s*(\^\s*(?:\([^)]*\))?|\([^)]*\))\s*\+/-\s*(%s)(.*)$" % (NUMBER, NUMBER))
RE_PAREN = re.compile(r"^(%s)\s*\((%s)\)(.*)$" % (NUMBER, NUMBER))

MM = ("EPW", "EPD", "VBH", "SCW", "SCD", "PDW", "PDH", "SPL", "TPW", "FCW", "FCH", "IFW", "IFH")
MM2 = ("EPA", "SCA", "PDA", "UJA", "PIA", "CVA", "CTA", "FCA")
DEG = ("EPI", "PDI", "UJI", "CAX", "CAY")
TEXT_COLUMNS = {"Specimen No.": ("", "text"), "Sex": ("", "text"), "Cause of death": ("", "text"),
                "Age": ("years", "count"), "Weight (kg)": ("kg", "mass"), "Height (cm)": ("cm", "length"),
                "Level": ("", "text")}


def units_of(measure: str) -> tuple[str, str]:
    """The units a mnemonic is printed in, and the kind of quantity it is."""
    if measure in TEXT_COLUMNS:
        return TEXT_COLUMNS[measure]
    if "/" in measure:
        return "", "ratio"
    if measure.startswith(MM):
        return "mm", "length"
    if measure.startswith(MM2) or measure.startswith("CVA + CTA"):
        return "mm2", "area"
    if measure.startswith(DEG) or measure[:1] in ("T", "S"):
        return "deg", "angle"
    raise SystemExit("no units known for %r" % measure)


def normal(s: str) -> str:
    """Two reads are the same when they differ only in spacing."""
    s = " ".join(s.split())
    s = re.sub(r"\s*\+/-\s*", " +/- ", s)
    s = re.sub(r"\s*\(\s*", " (", s)
    s = re.sub(r"\s*\)", ")", s)
    return s.strip()


def parse(fmt: str, statistic: str, printed: str) -> list[tuple[str, str, str]]:
    """The values a printed string holds: (statistic, value, note) for each."""
    s = normal(printed)
    if s in ("", "-"):
        return [(statistic if statistic != "mean+sem" else "mean", "", "")]
    if fmt in ("label", "text"):
        return [(statistic, s, "")]
    if fmt == "pm":
        m = RE_PM.match(s)
        if m:
            return [("mean", m.group(1), m.group(3).strip()), ("sem", m.group(2), m.group(3).strip())]
        m = RE_PM_MARKED.match(s)
        if m:
            note = (m.group(2) + " " + m.group(4)).strip()
            return [("mean", m.group(1), note), ("sem", m.group(3), note)]
        return [("mean", "", "unparsed: " + s)]
    if fmt == "paren":
        m = RE_PAREN.match(s)
        if m:
            return [("mean", m.group(1), m.group(3).strip()), ("sem", m.group(2), m.group(3).strip())]
        return [("mean", "", "unparsed: " + s)]
    m = RE_NUM.match(s)
    if m:
        return [(statistic, m.group(1), m.group(2).strip())]
    return [(statistic, "", "unparsed: " + s)]


def load_cells() -> list[dict]:
    with open(os.path.join(HERE, "cells.csv"), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_pages() -> dict:
    with open(os.path.join(OUT, "pages.json"), encoding="utf-8") as fh:
        return json.load(fh)


# ---- the reads, as the agents wrote them -----------------------------------------------

def strips_index(which: str) -> dict[str, dict]:
    with open(os.path.join(OUT, "strips", which + ".json"), encoding="utf-8") as fh:
        return {s["file"]: s for s in json.load(fh)}


SOURCES: dict[str, str] = {}      # "table/cell" -> who read it, where a pass file says ("source")


def collect_pass1(cells: list[dict]) -> tuple[dict[str, str], list[str]]:
    """Pass 1 reads keyed by table and cell name; and what it read where no box was found."""
    index = strips_index("pass1")
    by_table = tables.by_key()
    boxes = {(c["table"], int(c["row"]), int(c["col"])): c for c in cells}
    reads: dict[str, str] = {}
    stray: list[str] = []
    for path in sorted(glob.glob(os.path.join(READS_IN, "pass1-*.json"))):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for strip in data.get("strips", []):
            meta = index[os.path.basename(strip["file"])]
            table = by_table[meta["table"]]
            col_labels = [c.label for c in table.cols]
            first = col_labels.index(meta["cols"][0])
            for row in strip.get("rows", []):
                for k, s in enumerate(row.get("cells", [])):
                    col = first + k
                    key = (meta["table"], int(row["row"]), col)
                    if key in boxes:
                        reads[meta["table"] + "/" + cell_name(key[1], key[2])] = s
                        if data.get("source"):
                            SOURCES["pass1:" + meta["table"] + "/" + cell_name(key[1], key[2])] = data["source"]
                    elif normal(s) not in ("",):
                        stray.append("%s row %d col %d (%s): pass 1 read %r where no box was cut"
                                     % (meta["table"], key[1], col, col_labels[col] if col < len(col_labels) else "?", s))
    return reads, stray


def collect_pass2() -> dict[str, str]:
    index = strips_index("pass2")
    reads: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(READS_IN, "pass2-*.json"))):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for sheet in data.get("sheets", []):
            meta = index[os.path.basename(sheet["file"])]
            names = meta["cells"]
            got = sheet.get("cells", [])
            for name, s in zip(names, got):
                reads[meta["table"] + "/" + name] = s
                if data.get("source"):
                    SOURCES["pass2:" + meta["table"] + "/" + name] = data["source"]
            if len(got) != len(names):
                print("pass 2 sheet %s: %d cells expected, %d read" % (sheet["file"], len(names), len(got)))
    return reads


def collect_rereads(which: str) -> dict[str, list[tuple[int, str, str]]]:
    """Later rounds: reads/reread-<which>-<round>.json, {"cells": {"table/name": "read"}}."""
    rounds: dict[str, list[tuple[int, str, str]]] = {}
    for path in sorted(glob.glob(os.path.join(READS_IN, "reread-%s-*.json" % which))):
        n = int(os.path.basename(path).split("-")[-1].split(".")[0])
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        for key, s in data.get("cells", {}).items():
            rounds.setdefault(key, []).append((n, s, os.path.basename(path)))
    return rounds


def cell_name(row: int, col: int) -> str:
    return "r%02d_c%02d" % (row, col)


def write_reads(which: str, first: dict[str, str], later: dict[str, list[tuple[int, str, str]]]) -> dict[str, str]:
    """reads/<which>.csv, every round; returns the read that stands (the last round's)."""
    os.makedirs(READS, exist_ok=True)
    standing: dict[str, str] = {}
    with open(os.path.join(READS, which + ".csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=READ_FIELDS, lineterminator="\n")
        w.writeheader()
        for key in sorted(first):
            table, name = key.split("/")
            w.writerow({"table": table, "cell": name, "round": 1, "read": first[key],
                        "source": SOURCES.get(which + ":" + key, which + " agents")})
            standing[key] = first[key]
            for n, s, src in sorted(later.get(key, [])):
                w.writerow({"table": table, "cell": name, "round": n, "read": s, "source": src})
                standing[key] = s
    return standing


# ---- the provenance ------------------------------------------------------------------

def study_of(table: tables.Table, col_label: str) -> str:
    if table.axis == "rows" and table.cols and table.cols[0].label == "Level":
        return "present" if col_label == "Present Study" else col_label
    return "present"


def provenance_rows(cells: list[dict], pass1: dict[str, str], pass2: dict[str, str], pages: dict) -> list[dict]:
    by_table = tables.by_key()
    rows = []
    for c in cells:
        key = c["table"] + "/" + cell_name(int(c["row"]), int(c["col"]))
        table = by_table[c["table"]]
        paper = pages["papers"][table.source or table.paper]
        p1, p2 = pass1.get(key, ""), pass2.get(key, "")
        agree = normal(p1) == normal(p2)
        printed = normal(p1) if agree else ""
        measure = c["measure"]
        units, kind = units_of(measure)
        if c["fmt"] in ("label", "text"):   # a printed label (a level, a study's name) carries no units
            units, kind = "", "text"
        for statistic, value, note in parse(c["fmt"], c["statistic"], printed) if agree else [(c["statistic"], "", "the passes disagree")]:
            rows.append({
                "id": "%s/%s/%s" % (c["table"], cell_name(int(c["row"]), int(c["col"])), statistic),
                "paper": table.paper, "file": paper["file"], "sha256": paper["sha256"],
                "pdf_page": table.page, "printed_page": table.printed, "table": c["table"],
                "title": table.title, "row": c["row"], "col": c["col"],
                "row_label": c["row_label"], "col_label": c["col_label"],
                "study": study_of(table, c["col_label"]), "measure": measure, "level": c["level"],
                "statistic": statistic, "fmt": c["fmt"], "printed": printed, "value": value,
                "units": units if kind not in ("text",) else "", "kind": kind,
                "dpi": pages["dpi"], "x0": c["x0"], "y0": c["y0"], "x1": c["x1"], "y1": c["y1"],
                "image": c["image"], "pass1": p1, "pass2": p2, "agree": "yes" if agree else "no",
                "note": note,
            })
    return rows


def write_provenance(rows: list[dict]) -> None:
    with open(os.path.join(HERE, "provenance.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=PROVENANCE_FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---- the pages GitHub shows ------------------------------------------------------------

def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def write_table_pages(rows: list[dict], pages: dict) -> None:
    os.makedirs(TABLES_MD, exist_ok=True)
    by_table = tables.by_key()
    grouped: dict[str, list[dict]] = {}
    for r in rows:
        grouped.setdefault(r["table"], []).append(r)
    for key, table in by_table.items():
        rs = grouped.get(key, [])
        paper = pages["papers"][table.source or table.paper]
        lines = ["# %s" % table.title, "",
                 "%s, PDF page %d, printed page %d; %s (sha256 %s), rendered at %d dpi by render.py."
                 % (table.paper.capitalize(), table.page, table.printed, paper["file"], paper["sha256"], pages["dpi"]),
                 ""]
        if table.note:
            lines += [table.note, ""]
        lines += ["Every cell below is the box layout.py cut from the rendered page, and the two strings "
                  "are what the two reading passes read in it (README.md). A dash is printed where the "
                  "paper prints one. The value column is what provenance.csv carries.", "",
                  "| cell | row | column | measure | level | printed | value | pass 1 | pass 2 | image |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        seen = set()
        for r in rs:
            cell = r["id"].rsplit("/", 1)[0]
            if cell in seen:
                continue
            seen.add(cell)
            values = [x for x in rs if x["id"].rsplit("/", 1)[0] == cell]
            vtext = "; ".join("%s %s%s" % (v["statistic"], v["value"], (" " + v["units"]) if v["units"] else "")
                              for v in values if v["value"] != "")
            if not vtext:
                vtext = "(none)" if r["agree"] == "yes" else "(disagree)"
            lines.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | ![](../%s) |" % (
                cell.split("/")[1], md_escape(r["row_label"]), md_escape(r["col_label"]), md_escape(r["measure"]),
                r["level"], md_escape(r["printed"]), md_escape(vtext), md_escape(r["pass1"]), md_escape(r["pass2"]),
                r["image"]))
        with open(os.path.join(TABLES_MD, key + ".md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines) + "\n")


# ---- the disagreements -----------------------------------------------------------------

def disagreements(rows: list[dict]) -> list[dict]:
    out, seen = [], set()
    for r in rows:
        cell = r["id"].rsplit("/", 1)[0]
        if r["agree"] == "no" and cell not in seen:
            seen.add(cell)
            out.append(r)
    return out


def main(argv: list[str]) -> int:
    cells = load_cells()
    pages = load_pages()
    pass1_first, stray = collect_pass1(cells)
    pass2_first = collect_pass2()
    pass1 = write_reads("pass1", pass1_first, collect_rereads("pass1"))
    pass2 = write_reads("pass2", pass2_first, collect_rereads("pass2"))
    missing = [c for c in cells if c["table"] + "/" + cell_name(int(c["row"]), int(c["col"])) not in pass1
               or c["table"] + "/" + cell_name(int(c["row"]), int(c["col"])) not in pass2]
    rows = provenance_rows(cells, pass1, pass2, pages)
    bad = disagreements(rows)
    if argv[1:] == ["disagree"]:
        for r in bad:
            print("%s %s %s/%s: pass 1 %r, pass 2 %r" % (r["id"].rsplit("/", 1)[0], r["measure"], r["level"],
                                                       r["col_label"], r["pass1"], r["pass2"]))
        for s in stray:
            print(s)
        print("%d cells disagree, %d stray reads, %d cells unread" % (len(bad), len(stray), len(missing)))
        return 0
    write_provenance(rows)
    write_table_pages(rows, pages)
    with open(os.path.join(HERE, "pages.json"), "w", encoding="utf-8") as fh:
        json.dump(pages, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("provenance.csv: %d rows from %d cells; %d cells disagree; %d stray reads; %d cells unread"
          % (len(rows), len(cells), len(bad), len(stray), len(missing)))
    for s in stray:
        print("  " + s)
    for c in missing[:20]:
        print("  unread: %s %s" % (c["table"], cell_name(int(c["row"]), int(c["col"]))))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
