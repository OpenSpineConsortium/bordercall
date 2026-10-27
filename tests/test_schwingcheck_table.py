"""The long table is written from the provenance record and nothing else, loads with named
dimensions, agrees with the archive's CSV in every value, and every registered measure can be
selected for the rule or is refused for a reason; the specimens table is the thoracic paper's
Table 1, cell for cell, and agrees with what the other three papers print about the same
twelve spines but for the one contradiction they share.
"""
from __future__ import annotations

import csv
import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS, LEVELS_C2, SIDES   # noqa: E402
from schwingcheck import measures as MS            # noqa: E402
from schwingcheck import mnemonics as MN           # noqa: E402
from schwingcheck import table as T                # noqa: E402

ARCHIVE_CSV = os.path.join(ROOT, "archive", "bordercall", "reference", "panjabi_full_spine.csv")
CANON = {"endplate": ("endplate", "whole"), "endplate_depth": ("endplate_depth", "whole"),
         "endplate_lower": ("endplate_lower", "whole"), "endplate_lower_depth": ("endplate_lower_depth", "whole"),
         "h_post": ("h_post", "whole"), "canal_w": ("canal_w", "whole"), "canal_ap": ("canal_ap", "whole"),
         "pedicle_w_right": ("pedicle_w", "right"), "pedicle_w_left": ("pedicle_w", "left"),
         "pedicle_h_right": ("pedicle_h", "right"), "pedicle_h_left": ("pedicle_h", "left")}


class LongCSV(unittest.TestCase):
    def test_the_committed_csv_is_what_write_would_write(self):
        self.assertEqual(T.check_long_csv(), [])

    def test_every_row_comes_from_a_cell_read_twice(self):
        rows = T.read_long_csv()
        prov = {r["id"]: r for r in T.read_csv(T.PROVENANCE_CSV)}
        self.assertEqual(len(rows), 2690)
        for r in rows:
            self.assertEqual(set(r), set(T.FIELDS))
            self.assertIn(r["level"], LEVELS_C2)
            self.assertIn(r["side"], SIDES)
            self.assertIn(r["kind"], ("length", "area", "angle"))
            self.assertIn(r["statistic"], ("mean", "sem"))
            float(r["value"])
            cell = prov[r["cell"]]
            self.assertEqual(cell["value"], r["value"])
            self.assertEqual(cell["pass1"], cell["pass2"])
            self.assertEqual(cell["measure"], r["mnemonic"])
            self.assertEqual(cell["table"], r["table"])
            self.assertEqual(cell["statistic"], r["statistic"])
            self.assertEqual(cell["level"], r["level"])
            self.assertIn(r["table"], MN.DIMENSION_TABLES)

    def test_table_3_is_read_from_page_892_like_every_other_table(self):
        rows = {(r["mnemonic"], r["level"], r["statistic"]): r for r in T.read_long_csv()}
        t3 = rows[("EPDl", "T3", "mean")]
        self.assertEqual(t3["value"], "23.3")
        self.assertEqual(t3["cell"], "thoracic-t3/r07_c02/mean")
        self.assertEqual(rows[("EPDl", "T3", "sem")]["table"], "thoracic-t3")
        self.assertEqual(rows[("EPWu", "T7", "mean")]["table"], "thoracic-t3")
        t3_rows = [r for r in rows.values() if r["table"] == "thoracic-t3"]
        # five lengths, two areas and two inclinations with their standard errors, and the wedge
        # angle's mean alone, at each of T1 to T12
        self.assertEqual(len(t3_rows), (5 * 2 + 2 * 2 + 2 * 2 + 1) * 12)
        prov = T.read_csv(T.PROVENANCE_CSV)
        self.assertEqual({r["printed_page"] for r in prov if r["table"] == "thoracic-t3"}, {"892"})
        # Table 8 restates 23.2 at T3: the paper's own contradiction, recorded by step b, which
        # the long table does not read
        t8 = [r for r in prov if r["table"] == "thoracic-t8a" and r["measure"] == "EPDl" and r["level"] == "T3"
              and r["study"] == "present" and r["statistic"] == "mean"]
        self.assertEqual([r["value"] for r in t8], ["23.2"])

    def test_the_archive_csv_agrees_in_every_value(self):
        ds = T.load()
        with open(ARCHIVE_CSV, newline="", encoding="utf-8") as fh:
            arch = list(csv.DictReader(line for line in fh if not line.startswith("#")))
        compared, diffs = 0, []
        for a in arch:
            if a["measure"] in CANON:
                m, s = CANON[a["measure"]]
                for stat in ("mean", "sem"):
                    v = ds[stat].sel(level=a["level"], measure=m, side=s).item()
                    compared += 1
                    if abs(v - float(a[stat])) > 1e-9:
                        diffs.append((a["measure"], a["level"], stat, a[stat], v))
            elif a["measure"] in ("pedicle", "pedicle_h"):
                m = {"pedicle": "pedicle_w", "pedicle_h": "pedicle_h"}[a["measure"]]
                r = ds["mean"].sel(level=a["level"], measure=m, side="right").item()
                l_ = ds["mean"].sel(level=a["level"], measure=m, side="left").item()
                sr = ds["sem"].sel(level=a["level"], measure=m, side="right").item()
                sl = ds["sem"].sel(level=a["level"], measure=m, side="left").item()
                compared += 2
                if abs((r + l_) / 2 - float(a["mean"])) > 1e-6 or abs((sr + sl) / 2 - float(a["sem"])) > 1e-6:
                    diffs.append((a["measure"], a["level"], a["mean"], (r + l_) / 2))
        self.assertEqual(compared, 592)
        self.assertEqual(diffs, [])


class Specimens(unittest.TestCase):
    def test_the_committed_csv_is_what_write_would_write(self):
        self.assertEqual(T.check_specimens_csv(), [])

    def test_every_value_is_a_cell_of_table_1_read_twice(self):
        rows = T.read_specimens_csv()
        prov = {r["id"]: r for r in T.read_csv(T.PROVENANCE_CSV)}
        self.assertEqual(len(rows), 12)
        self.assertEqual(len({r["specimen"] for r in rows}), 12)
        cells = set()
        for r in rows:
            self.assertEqual(set(r), set(T.SPECIMEN_FIELDS))
            for _, name, _ in T.SPECIMEN_COLUMNS:
                cell = prov[r["%s_cell" % name]]
                self.assertEqual(cell["table"], "thoracic-t1")
                self.assertEqual(cell["printed"], r[name])
                self.assertEqual(cell["pass1"], cell["pass2"])
                cells.add(cell["id"])
        self.assertEqual(cells, {i for i, c in prov.items() if c["table"] == "thoracic-t1"})
        self.assertEqual(len(cells), 72)

    def test_the_dataset(self):
        sp = T.load_specimens()
        self.assertEqual(tuple(sp["age_years"].dims), ("specimen",))
        self.assertEqual(sp.sizes["specimen"], 12)
        self.assertEqual(list(sp["specimen"].values[:3]), ["S3", "S4", "S7"])
        self.assertEqual((float(sp["age_years"].min()), float(sp["age_years"].max())), (19.0, 59.0))
        self.assertEqual((float(sp["weight_kg"].min()), float(sp["weight_kg"].max())), (54.0, 84.0))
        self.assertEqual((float(sp["height_cm"].min()), float(sp["height_cm"].max())), (157.0, 178.0))
        self.assertAlmostEqual(float(sp["age_years"].mean()), 556 / 12, places=12)
        self.assertAlmostEqual(float(sp["weight_kg"].mean()), 814 / 12, places=12)
        self.assertAlmostEqual(float(sp["height_cm"].mean()), 2013 / 12, places=12)
        self.assertEqual(sorted(sp["sex"].values.tolist()).count("M"), 8)
        self.assertIn("no coefficient", sp.attrs["note"])
        self.assertEqual(sp.attrs["sha256"], T.sha256(T.SPECIMENS_CSV))

    def test_the_other_papers_summaries_agree_but_for_the_heaviest_weight(self):
        sp = T.load_specimens()
        stats = {"mean": lambda v: round(float(v.mean()), 1), "min": lambda v: float(v.min()),
                 "max": lambda v: float(v.max())}
        disagree = []
        for paper, page, stat, cov, value in T.SPECIMEN_SUMMARIES:
            if stat == "count":
                have = {"specimens": sp.sizes["specimen"], "male": int((sp["sex"] == "M").sum()),
                        "female": int((sp["sex"] == "F").sum())}[cov]
            else:
                have = stats[stat](sp[cov])
            if abs(have - value) > 1e-9:
                disagree.append((paper, page, stat, cov, value))
        self.assertEqual(len(T.SPECIMEN_SUMMARIES), 36)
        self.assertEqual(disagree, T.SPECIMEN_CONTRADICTIONS)


class Dataset(unittest.TestCase):
    def test_dimensions_and_coordinates(self):
        ds = T.load()
        self.assertEqual(tuple(ds["mean"].dims), ("level", "measure", "side"))
        self.assertEqual(list(ds["level"].values), LEVELS_C2)
        self.assertEqual(list(ds["side"].values), SIDES)
        self.assertEqual(ds.sizes["measure"], 49)
        self.assertNotIn("basis", ds)
        self.assertEqual(set(ds["kind"].values), {"length", "area", "angle"})
        for m in ds["measure"].values:
            self.assertEqual(MN.MEASURE_INFO[m].kind, ds["kind"].sel(measure=m).item())
        sd = ds["sd"].sel(level="L3", measure="endplate", side="whole").item()
        sem = ds["sem"].sel(level="L3", measure="endplate", side="whole").item()
        self.assertAlmostEqual(sd, sem * math.sqrt(12), places=12)
        self.assertTrue(np.isnan(ds["mean"].sel(level="C2", measure="endplate", side="whole").item()))
        self.assertTrue(np.isnan(ds["mean"].sel(level="T4", measure="facet_w_sup", side="whole").item()))
        self.assertFalse(np.isnan(ds["mean"].sel(level="T4", measure="facet_w_sup", side="left").item()))
        self.assertEqual(ds["mnemonic"].sel(measure="pedicle_w", side="right").item(), "PDWr")
        self.assertEqual(ds.attrs["sha256"], T.sha256(T.LONG_CSV))

    def test_reference_in_the_archives_shape(self):
        ds = T.load()
        ref = T.reference(ds, [("endplate", "whole"), ("pedicle_w", "mean"), ("pedicle_w", "right")], LEVELS)
        self.assertEqual(set(ref), {"endplate", "pedicle_w:mean", "pedicle_w:right"})
        self.assertEqual(set(ref["endplate"]), set(LEVELS))
        r = ds["mean"].sel(level="L4", measure="pedicle_w", side="right").item()
        l_ = ds["mean"].sel(level="L4", measure="pedicle_w", side="left").item()
        self.assertAlmostEqual(ref["pedicle_w:mean"]["L4"][0], (r + l_) / 2, places=12)
        with self.assertRaises(ValueError):
            T.reference(ds, [("facet_w_sup", "whole")], LEVELS)


class Registry(unittest.TestCase):
    def test_every_registered_measure_is_scored_or_refused_for_a_reason(self):
        reg = MS.registry()
        self.assertGreater(len(reg), 60)
        scored, refused, no_rows = [], [], []
        for key, m in reg.items():
            try:
                MS.select([key], levels=m.levels or LEVELS)
                scored.append(key)
                self.assertEqual(m.kind, "length")
                self.assertGreater(m.error_mm, 0)
                self.assertTrue(m.levels)
            except ValueError as e:
                if not m.levels:
                    no_rows.append(key)
                    self.assertTrue("no table row" in str(e) or "step e" in str(e), str(e))
                else:
                    refused.append(key)
                    self.assertIn(m.kind, ("area", "angle"))
                    self.assertIn("step e", str(e))
        self.assertTrue(all(reg[k].kind == "length" for k in scored))
        self.assertEqual(len(scored) + len(refused) + len(no_rows), len(reg))
        self.assertIn("pedicle_w:mean", scored)
        self.assertIn("facet_area_sup:right", refused)
        # the papers print these means with no spread (thoracic Table 3's wedge angle, Table 6's
        # totals per rib, facets Table 8's card angles), so no rule can take them until a spread
        # is found for them
        self.assertEqual(sorted(no_rows), sorted(
            ["costovertebral_area", "rib_articulation_area", "endplate_wedge"]
            + ["facet_card_%s_%s:%s" % (ax, pos, side) for ax in ("x", "y") for pos in ("sup", "inf") for side in ("right", "left", "mean")]))
        # a length with no rows at the levels asked is refused by name
        with self.assertRaises(ValueError) as cm:
            MS.select(["spinous_length"], levels=["C2", "C3"] if "C2" not in reg["spinous_length"].levels else ["L6"])
        self.assertIn("no table row", str(cm.exception))

    def test_the_seven_in_the_archives_order_and_names(self):
        seven = MS.select(MS.SPINEPS_7)
        self.assertEqual([MS.archive_key(m) for m in seven], MS.SPINEPS_7)
        for m in seven:
            self.assertEqual(m.error_mm, 1.0)
            self.assertTrue(set(LEVELS) <= set(m.levels))
        self.assertEqual(MS.resolve("pedicle"), ("pedicle_w", "mean"))
        self.assertEqual(MS.resolve("pedicle_h:left"), ("pedicle_h", "left"))
        with self.assertRaises(KeyError):
            MS.select(["no_such_measure"])
        with self.assertRaises(ValueError):
            MS.select(["canal_area"])
        with self.assertRaises(ValueError):
            MS.select(["endplate"], levels=LEVELS_C2)       # C2 has no upper end-plate

    def test_the_archive_table_and_the_checked_table_are_one(self):
        seven = MS.select(MS.SPINEPS_7)
        a = MS.archive_reference([MS.archive_key(m) for m in seven])
        b = MS.reference(seven)
        self.assertEqual(set(a), set(b))
        diffs = [(k, lv) for k in a for lv in LEVELS if a[k][lv] != b[k][lv]]
        self.assertEqual(diffs, [])
        self.assertEqual(b["endplate_lower_depth"]["T3"][0], 23.3)

if __name__ == "__main__":
    unittest.main()
