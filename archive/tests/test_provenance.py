"""The provenance of every printed value of the four Panjabi papers holds together.

    python -m unittest tests.test_provenance -v

reference/provenance/README.md says how the values were read. These tests hold the record
to the rules the owner set on 2026-10-27: the two reading passes agree on every cell, every
value a paper also states in prose agrees with its cells (or the record says, cell by cell,
that the paper contradicts itself), every value the reference CSVs carry was read from a
cell or is listed as resting on a page the scan does not carry, the papers are the exact
bytes the record names, and every cell's image and box are there to be looked at.
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
import tables  # noqa: E402


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
            self.assertEqual(r["sha256"], self.pages["papers"][r["paper"]]["sha256"], r["id"])
            self.assertEqual(r["file"], self.pages["papers"][r["paper"]]["file"], r["id"])

    def test_every_image_exists_and_every_box_lies_on_its_page(self):
        for r in self.rows:
            self.assertTrue(os.path.exists(os.path.join(PROV, r["image"])), r["image"])
            w, h = self.pages["papers"][r["paper"]]["pages"][r["pdf_page"]]["size"]
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
            self.assertIn(self.pages["papers"][t.paper]["sha256"], text)

    def test_the_absent_table_is_named_and_nothing_is_read_from_it(self):
        self.assertIn("thoracic-t3", tables.ABSENT)
        self.assertEqual([r for r in self.rows if r["table"] == "thoracic-t3"], [])

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


class ReferenceCSVs(unittest.TestCase):
    def test_every_csv_value_was_read_from_a_cell_or_is_listed_absent(self):
        prov = check_csv.Provenance(check_csv.load_provenance())
        matched, changed, missing = check_csv.check(prov, check_csv.load_absent())
        self.assertEqual(missing, [], "CSV values in no cell and not listed absent: %s" % missing[:10])
        self.assertEqual(changed, [], "CSV values that differ from their cell: %s" % changed[:10])
        self.assertGreater(len(matched), 300)

    def test_the_absent_values_are_only_the_thoracic_body_table(self):
        absent = check_csv.load_absent()
        self.assertGreater(len(absent), 0)
        for a in absent:
            self.assertEqual(a["level"][0], "T", a)
            self.assertIn(a["panjabi_name"].split(" ")[0], ("EPWu", "EPDu", "EPWl", "EPDl", "VBHp"), a)
            self.assertIn(a["basis"].split(":")[0], ("thoracic-t8a", "thoracic-t8b", "earlier transcription", "prose"), a)

    def test_the_one_absent_mean_table_8_contradicts_is_recorded_as_such(self):
        """EPDl at T3: the transcription of the absent Table 3 reads 23.3, Table 8 prints 23.2;
        the archive's records were computed with 23.3 and hold it, and the record says so."""
        absent = check_csv.load_absent()
        unverified = [(a["panjabi_name"], a["level"]) for a in absent
                      if a["statistic"] == "mean" and a["panjabi_name"] in ("EPDl", "EPWl", "VBHp")
                      and a["basis"].startswith("earlier transcription")]
        self.assertEqual(unverified, [("EPDl", "T3")])
        (row,) = [a for a in absent if a["panjabi_name"] == "EPDl" and a["level"] == "T3" and a["statistic"] == "mean"]
        self.assertEqual(row["value"], "23.3")
        self.assertIn("Table 8's Present Study column prints 23.2", row["note"])
        prov = check_csv.Provenance(check_csv.load_provenance())
        table8 = prov.index[("thoracic", "thoracic-t8a", "EPDl", "T3", "mean")]
        self.assertEqual(table8["value"], "23.2")

    def test_an_absent_mean_that_rests_on_table_8_equals_table_8(self):
        prov = check_csv.Provenance(check_csv.load_provenance())
        bad = check_csv.absent_against_table8(prov, check_csv.load_absent())
        self.assertEqual(bad, [], "\n".join(bad))


class CrossTables(unittest.TestCase):
    def test_each_comparison_table_restates_its_dimension_tables_as_recorded(self):
        prov = rows_of("provenance.csv")
        record = rows_of("crosstable.csv")
        self.assertGreater(len(record), 0)
        problems = check_tables.check(prov, record)
        self.assertEqual(problems, [], "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
