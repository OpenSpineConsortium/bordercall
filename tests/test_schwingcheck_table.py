"""The long table is written from the provenance record and nothing else, loads with named
dimensions, agrees with the archive's CSV in every value but the one step b found, and every
registered measure can be selected for the rule or is refused for a reason.
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

    def test_every_row_comes_from_a_cell_or_says_what_it_rests_on(self):
        rows = T.read_long_csv()
        prov = {r["id"]: r for r in T.read_csv(T.PROVENANCE_CSV)}
        self.assertGreater(len(rows), 2500)
        for r in rows:
            self.assertEqual(set(r), set(T.FIELDS))
            self.assertIn(r["level"], LEVELS_C2)
            self.assertIn(r["side"], SIDES)
            self.assertIn(r["kind"], ("length", "area", "angle"))
            self.assertIn(r["statistic"], ("mean", "sem"))
            float(r["value"])
            if r["cell"]:
                cell = prov[r["cell"]]
                self.assertEqual(cell["value"], r["value"])
                self.assertEqual(cell["pass1"], cell["pass2"])
                self.assertEqual(cell["measure"], r["mnemonic"])
            else:
                self.assertIn("transcription", r["basis"])
                self.assertEqual(r["table"], T.ABSENT_TABLE)

    def test_the_absent_table_takes_table_8_where_it_prints_the_mean(self):
        rows = {(r["mnemonic"], r["level"], r["statistic"]): r for r in T.read_long_csv()}
        t3 = rows[("EPDl", "T3", "mean")]
        self.assertEqual(t3["value"], "23.2")
        self.assertEqual(t3["cell"], "thoracic-t8a/r03_c01/mean")
        self.assertEqual(rows[("EPDl", "T3", "sem")]["basis"], "transcription of the absent Table 3 (provenance/absent.csv)")
        self.assertEqual(rows[("EPWu", "T7", "mean")]["table"], T.ABSENT_TABLE)
        n8 = sum(1 for r in rows.values() if r["basis"].startswith("table 8"))
        self.assertEqual(n8, 36)

    def test_the_archive_csv_agrees_in_every_value_but_EPDl_T3(self):
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
        self.assertEqual(diffs, [("endplate_lower_depth", "T3", "mean", "23.3", 23.2)])


class Dataset(unittest.TestCase):
    def test_dimensions_and_coordinates(self):
        ds = T.load()
        self.assertEqual(tuple(ds["mean"].dims), ("level", "measure", "side"))
        self.assertEqual(list(ds["level"].values), LEVELS_C2)
        self.assertEqual(list(ds["side"].values), SIDES)
        self.assertEqual(ds.sizes["measure"], 48)
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
        # the papers print these means with no spread (thoracic Table 6's totals per rib, facets
        # Table 8's card angles), so no rule can take them until a spread is found for them
        self.assertEqual(sorted(no_rows), sorted(
            ["costovertebral_area", "rib_articulation_area"]
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

    def test_the_archive_table_and_the_checked_table(self):
        seven = MS.select(MS.SPINEPS_7)
        a = MS.reference(seven, table="archive")
        b = MS.reference(seven, table="checked")
        self.assertEqual(set(a), set(b))
        diffs = [(k, lv) for k in a for lv in LEVELS if a[k][lv] != b[k][lv]]
        self.assertEqual(diffs, [("endplate_lower_depth", "T3")])
        self.assertEqual(a["endplate_lower_depth"]["T3"][0], 23.3)
        self.assertEqual(b["endplate_lower_depth"]["T3"][0], 23.2)
        with self.assertRaises(ValueError):
            MS.reference(seven, table="other")


if __name__ == "__main__":
    unittest.main()
