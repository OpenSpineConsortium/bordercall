"""The provenance of every printed value of the four Panjabi papers holds together.

    python -m unittest tests.test_provenance -v

reference/provenance/README.md says how the values were read. These tests hold the record
to the rules the owner set on 2026-10-27: the two reading passes agree on every cell, every
value a paper also states in prose agrees with its cells (or the record says, cell by cell,
that the paper contradicts itself), every value the reference CSVs carry was read from a
cell, the papers are the exact bytes the record names, every cell's image and box are there
to be looked at, the thoracic body table of printed page 892, which came later from a second
scan, was read from that one page alone, and the contradictions report is what its code
writes from the record.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REFERENCE = os.path.join(os.path.dirname(HERE), "bordercall", "reference")
PROV = os.path.join(REFERENCE, "provenance")
sys.path.insert(0, PROV)

import check_csv  # noqa: E402
import check_prose  # noqa: E402
import check_tables  # noqa: E402
import compile as compile_provenance  # noqa: E402
import contradictions  # noqa: E402
import tables  # noqa: E402

P892 = "Panjabi_1991_Thoracic_Spine_16-8_888-901_p892.pdf"
P892_SHA256 = "a1a43be91d80a5d5735bcd61fa0f07fee5b5bf73f8aeb6f3652e6dae00541a6a"
# the page record a table's cells were read from: its own source where it has one, else its paper's
SOURCE = {t.key: (t.source or t.paper) for t in tables.TABLES}


def rows_of(name: str) -> list[dict]:
    with open(os.path.join(PROV, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Provenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows_of("provenance.csv")
        cls.cells = rows_of("cells.csv")
        with open(os.path.join(PROV, "pages.json"), encoding="utf-8") as fh:
            cls.pages = json.load(fh)

    def test_the_two_passes_agree_on_every_cell(self):
        bad = [r["id"] for r in self.rows if r["agree"] != "yes"]
        self.assertEqual(bad, [], "cells the two reading passes read differently: %s" % bad[:20])

    def test_every_cell_was_read_by_both_passes(self):
        for which in ("pass1", "pass2"):
            reads = {(r["table"], r["cell"]) for r in rows_of(os.path.join("reads", which + ".csv"))}
            missing = [c for c in self.cells
                       if (c["table"], compile_provenance.cell_name(int(c["row"]), int(c["col"]))) not in reads]
            self.assertEqual(missing, [], "%s did not read %d cells" % (which, len(missing)))

    def test_every_cell_has_a_row_and_a_printed_string(self):
        by_cell = {}
        for r in self.rows:
            by_cell.setdefault(r["id"].rsplit("/", 1)[0], []).append(r)
        for c in self.cells:
            key = c["table"] + "/" + compile_provenance.cell_name(int(c["row"]), int(c["col"]))
            self.assertIn(key, by_cell)
            rs = by_cell[key]
            self.assertEqual(len(rs), 2 if c["fmt"] in ("pm", "paren") and rs[0]["printed"] != "-" else 1,
                             "%s: %d rows" % (key, len(rs)))
            for r in rs:
                self.assertNotEqual(r["printed"], "", key)
                self.assertFalse(r["note"].startswith("unparsed"), "%s: %s" % (key, r["note"]))

    def test_numeric_values_parse(self):
        for r in self.rows:
            if r["kind"] in ("text",) or r["value"] == "":
                continue
            float(r["value"])

    def test_a_dash_is_the_only_value_left_empty(self):
        for r in self.rows:
            if r["value"] == "":
                self.assertEqual(r["printed"], "-", "%s is empty but printed %r" % (r["id"], r["printed"]))

    def test_the_papers_are_the_bytes_the_record_names(self):
        for paper, rec in self.pages["papers"].items():
            path = os.path.join(REFERENCE, "papers", rec["file"])
            self.assertEqual(sha256(path), rec["sha256"], paper)
        for r in self.rows:
            rec = self.pages["papers"][SOURCE[r["table"]]]
            self.assertEqual(r["sha256"], rec["sha256"], r["id"])
            self.assertEqual(r["file"], rec["file"], r["id"])

    def test_every_image_exists_and_every_box_lies_on_its_page(self):
        for r in self.rows:
            self.assertTrue(os.path.exists(os.path.join(PROV, r["image"])), r["image"])
            w, h = self.pages["papers"][SOURCE[r["table"]]]["pages"][r["pdf_page"]]["size"]
            x0, y0, x1, y1 = (int(r[k]) for k in ("x0", "y0", "x1", "y1"))
            self.assertTrue(0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h, "%s box %s" % (r["id"], (x0, y0, x1, y1)))
            self.assertEqual(int(r["dpi"]), self.pages["dpi"])

    def test_every_table_at_hand_has_its_page_and_every_cell_is_on_it(self):
        for t in tables.TABLES:
            page = os.path.join(PROV, "tables", t.key + ".md")
            self.assertTrue(os.path.exists(page), page)
            with open(page, encoding="utf-8") as fh:
                text = fh.read()
            for r in self.rows:
                if r["table"] == t.key:
                    self.assertIn(r["image"], text, "%s is not on %s" % (r["image"], page))
            self.assertIn(self.pages["papers"][SOURCE[t.key]]["sha256"], text)

    def test_the_body_table_of_page_892_was_read_from_that_one_page(self):
        """The thoracic scan lacks printed page 892; the owner's second scan of 27 October 2026
        gave it, and only that page was read, from a one-page file of its own."""
        rec = self.pages["papers"]["thoracic-p892"]
        self.assertEqual((rec["file"], rec["sha256"], sorted(rec["pages"])), (P892, P892_SHA256, ["1"]))
        self.assertFalse(rec["pages"]["1"]["turned"])
        self.assertEqual(SOURCE["thoracic-t3"], "thoracic-p892")
        t3 = [r for r in self.rows if r["table"] == "thoracic-t3"]
        self.assertEqual(len(t3), 252)
        self.assertEqual(len({r["id"].rsplit("/", 1)[0] for r in t3}), 252)
        for r in t3:
            self.assertEqual((r["paper"], r["file"], r["printed_page"], r["pdf_page"], r["agree"]),
                             ("thoracic", P892, "892", "1", "yes"), r["id"])
        self.assertEqual(sorted({r["file"] for r in self.rows if r["paper"] == "thoracic" and r["table"] != "thoracic-t3"}),
                         [self.pages["papers"]["thoracic"]["file"]])
        for which in ("pass1", "pass2"):
            reads = [r for r in rows_of(os.path.join("reads", which + ".csv")) if r["table"] == "thoracic-t3"]
            self.assertEqual(len(reads), 252, which)
            self.assertEqual({r["source"] for r in reads}, {"%s session: the thread's own reading of the %s, 2026-10-27"
                                                            % (which, "strips" if which == "pass1" else "numbered crops")})

    def test_units_follow_the_mnemonic(self):
        for r in self.rows:
            if r["fmt"] in ("label", "text"):     # a printed label carries no units
                self.assertEqual((r["units"], r["kind"]), ("", "text"), r["id"])
                continue
            units, kind = compile_provenance.units_of(r["measure"])
            self.assertEqual(r["kind"], kind, r["id"])
            if kind != "text":
                self.assertEqual(r["units"], units, r["id"])


class Prose(unittest.TestCase):
    def test_every_prose_value_agrees_with_its_cells_or_is_recorded_as_a_contradiction(self):
        prov = rows_of("provenance.csv")
        prose = rows_of("prose.csv")
        self.assertGreater(len(prose), 0)
        problems = check_prose.check(prov, prose)
        self.assertEqual(problems, [], "\n".join(problems))

    def test_the_two_prose_passes_agree_on_every_value_kept(self):
        for p in rows_of("prose.csv"):
            self.assertEqual(p["passA"], p["passB"], "%s p.%s %r" % (p["paper"], p["printed_page"], p["quote"]))
            self.assertEqual(p["passA"], p["printed"], p["quote"])

    def test_the_body_text_of_the_thoracic_paper_is_held_to_table_3(self):
        """Page 890 speaks of Table 3 fourteen times; three of its numbers contradict the table
        (two percentages that match the mean of the upper and lower end-plates' increases, and
        the posterior height at T1), and no value is left with no cell but the two the tables
        do not print (the radiographic wedge angle and the rate per level)."""
        rows = [p for p in rows_of("prose.csv") if p["paper"] == "thoracic" and p["printed_page"] == "890"]
        self.assertEqual(len(rows), 14)
        self.assertEqual([(p["measure"], p["printed"]) for p in rows if p["agrees"] == "no"],
                         [("EPWl T12 over T1", "55"), ("EPDu T12 over T1", "73"), ("VBHp", "14.3")])
        self.assertEqual([p["measure"] for p in rows if not p["cells"]], ["wedge angle, radiographic", "VBHp per level"])
        for p in rows:
            if p["cells"]:
                self.assertTrue(all(c.startswith("thoracic-t3/") for c in p["cells"].split(";")), p["cells"])


class ReferenceCSVs(unittest.TestCase):
    def test_every_csv_value_was_read_from_a_cell_and_agrees_with_it(self):
        prov = check_csv.Provenance(check_csv.load_provenance())
        matched, changed, missing = check_csv.check(prov)
        self.assertEqual(missing, [], "CSV values in no cell: %s" % missing[:10])
        self.assertEqual(changed, [], "CSV values that differ from their cell: %s" % changed[:10])
        self.assertEqual(len(matched), 651)
        self.assertEqual(rows_of("changes.csv"), [])

    def test_table_3_prints_the_archives_EPDl_at_T3_and_table_8_contradicts_it(self):
        """The archive's 23.3 came from an earlier transcription of Table 3; Table 8's Present
        Study column prints 23.2. Page 892 shows Table 3 prints 23.3, so the archive's value
        stands and the paper's own disagreement is recorded in crosstable.csv."""
        prov = check_csv.Provenance(check_csv.load_provenance())
        self.assertEqual(prov.index[("thoracic", "thoracic-t3", "EPDl", "T3", "mean")]["value"], "23.3")
        self.assertEqual(prov.index[("thoracic", "thoracic-t8a", "EPDl", "T3", "mean")]["value"], "23.2")
        (row,) = [r for r in rows_of("crosstable.csv") if r["comparison"] == "thoracic-t8a/r03_c01/mean"]
        self.assertEqual((row["cells"], row["rule"], row["value"], row["restated"], row["agrees"]),
                         ("thoracic-t3/r07_c02/mean", "equal", "23.3", "23.2", "no"))


class CrossTables(unittest.TestCase):
    def test_each_comparison_table_restates_its_dimension_tables_as_recorded(self):
        prov = rows_of("provenance.csv")
        record = rows_of("crosstable.csv")
        self.assertGreater(len(record), 0)
        problems = check_tables.check(prov, record)
        self.assertEqual(problems, [], "\n".join(problems))


class Contradictions(unittest.TestCase):
    def test_the_report_is_what_its_code_writes_from_the_record(self):
        with open(os.path.join(PROV, "CONTRADICTIONS.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), contradictions.report())

    def test_the_arithmetic_checks_cover_every_derived_column_and_hold_their_verdicts(self):
        prov = rows_of("provenance.csv")
        checks = contradictions.derived(prov)
        self.assertEqual({c["kind"] for c in checks}, {"ratio", "sum"})
        ratio_measures = {(r["table"], r["measure"]) for r in prov if r["statistic"] == "ratio" and r["value"] != ""}
        self.assertEqual({(c["table"], c["measure"]) for c in checks if c["kind"] == "ratio"}, ratio_measures)
        self.assertEqual({(c["table"], c["measure"]) for c in checks if c["kind"] == "sum"},
                         {("thoracic-t3", "EPIt"), ("thoracic-t6", "CVA"), ("thoracic-t6", "CVA + CTA")})
        for c in checks:
            self.assertIn(c["agrees"], ("yes", "no"))
            self.assertEqual(c["agrees"] == "yes", contradictions.consistent(c), c)


if __name__ == "__main__":
    unittest.main()
