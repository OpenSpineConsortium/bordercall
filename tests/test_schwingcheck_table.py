"""The long table is written from the provenance record and nothing else, loads with named
dimensions, agrees with the archive's CSV in every value, and every registered measure can be
selected for the rule, a length, an area or an angle each with its own error and power of the
size, or has no rows to select; the pool is every measure with a row and a spread at every level,
and the measures left out each say why; a mirrored pair's mean negates its right side; each
measure carries its table rows with their cells, its mnemonics, its measurers and its error,
which the rule reads, and a pair or a measure named twice is refused; the specimens table is the thoracic paper's Table 1, cell for cell, and
agrees with what the other three papers print about the same twelve spines but for the one
contradiction they share.
"""
from __future__ import annotations

import csv
import dataclasses
import math
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS, LEVELS_C2, SIDES   # noqa: E402
from schwingcheck import columns as C              # noqa: E402
from schwingcheck import measures as MS            # noqa: E402
from schwingcheck import rule as R                 # noqa: E402
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

    def test_the_check_compares_the_text_to_the_byte(self):
        with open(T.LONG_CSV, newline="", encoding="utf-8") as fh:
            text = fh.read()
        lines = text.split("\n")
        column_line = next(i for i, line in enumerate(lines) if not line.startswith("#"))
        cols = lines[column_line].split(",")
        cols[0], cols[1] = cols[1], cols[0]
        swapped = list(lines)
        swapped[column_line] = ",".join(cols)
        changed = list(lines)
        changed[column_line + 5] = changed[column_line + 5].replace(",mean,", ",sem,", 1)
        variants = {"a header line": "# an edit by hand\n" + text, "the columns' order": "\n".join(swapped),
                    "one value's row": "\n".join(changed), "CRLF": text.replace("\n", "\r\n"),
                    "the last newline": text[:-1]}
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "long.csv")
            for what, variant in variants.items():
                with open(path, "w", newline="", encoding="utf-8") as fh:
                    fh.write(variant)
                problems = T.check_long_csv(path)
                self.assertTrue(problems, what)
                self.assertRegex(problems[0], r"^\d+ committed lines differ", what)
            many = "\n".join(lines[:column_line + 1] + [line.replace(",mean,", ",sem,") for line in lines[column_line + 1:]])
            with open(path, "w", newline="", encoding="utf-8") as fh:
                fh.write(many)
            problems = T.check_long_csv(path)
            n = sum(",mean," in line for line in lines[column_line + 1:])
            self.assertEqual(problems[0], "%d committed lines differ from what write would write: %d to remove, %d to add" % (n, n, n))
            self.assertEqual(problems[-1], "and %d more lines" % (2 * n - 10))
            self.assertIn("does not exist", T.check_long_csv(os.path.join(tmp, "absent.csv"))[0])

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
                    # a NaN compares false with everything, so a value the table lacks is
                    # caught by its finiteness and not by the difference
                    if not math.isfinite(v) or abs(v - float(a[stat])) > 1e-9:
                        diffs.append((a["measure"], a["level"], stat, a[stat], v))
            elif a["measure"] in ("pedicle", "pedicle_h"):
                m = {"pedicle": "pedicle_w", "pedicle_h": "pedicle_h"}[a["measure"]]
                r = ds["mean"].sel(level=a["level"], measure=m, side="right").item()
                l_ = ds["mean"].sel(level=a["level"], measure=m, side="left").item()
                sr = ds["sem"].sel(level=a["level"], measure=m, side="right").item()
                sl = ds["sem"].sel(level=a["level"], measure=m, side="left").item()
                compared += 2
                if not all(map(math.isfinite, (r, l_, sr, sl))) or \
                        abs((r + l_) / 2 - float(a["mean"])) > 1e-6 or abs((sr + sl) / 2 - float(a["sem"])) > 1e-6:
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

    def test_the_summaries_are_what_both_prose_passes_read(self):
        """Every number of SPECIMEN_SUMMARIES, read by eye for step c, is one row of the
        provenance record's prose.csv that its two independent passes read alike, and the rows
        that record calls contradictions are SPECIMEN_CONTRADICTIONS."""
        names = {"specimens": "specimens", "males": "male", "females": "female", "age": "age_years",
                 "weight": "weight_kg", "height": "height_cm"}
        stats = {"count": "count", "mean": "mean", "range_low": "min", "range_high": "max"}
        found = {}
        with open(os.path.join(T.PROVENANCE_DIR, "prose.csv"), newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["where"] == "methods" and r["measure"] in names:
                    key = (r["paper"], int(r["printed_page"]), stats[r["statistic"]], names[r["measure"]])
                    found.setdefault(key, []).append(r)
        contradicted = []
        for paper, page, stat, cov, value in T.SPECIMEN_SUMMARIES:
            rows = found.get((paper, page, stat, cov), [])
            self.assertEqual(len(rows), 1, (paper, page, stat, cov))
            r = rows[0]
            self.assertEqual((r["passA"], r["passB"]), (r["printed"], r["printed"]), r)
            self.assertEqual(float(r["value"]), value, r)
            if r["agrees"] == "no":
                contradicted.append((paper, page, stat, cov, value))
        self.assertEqual(contradicted, T.SPECIMEN_CONTRADICTIONS)


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

    def test_a_mirrored_pair_has_opposite_signs_and_every_other_pair_one(self):
        # the facets paper prints the sagittal angle and the card angle about y of a right facet
        # with the opposite sign to the left's, at every level both are printed, so their mean
        # negates the right first; every other pair has one sign on both sides at every level
        ds = T.load()
        pairs = 0
        for measure in ds["measure"].values:
            r = ds["mean"].sel(measure=measure, side="right").values
            l_ = ds["mean"].sel(measure=measure, side="left").values
            both = ~np.isnan(r) & ~np.isnan(l_)
            if not both.any():
                continue
            pairs += 1
            product = np.sign(r[both]) * np.sign(l_[both])
            if measure in MN.MIRRORED:
                self.assertTrue(np.all(product < 0), measure)
                self.assertEqual(T.mirror(measure), -1.0)
            else:
                self.assertTrue(np.all(product > 0), measure)
                self.assertEqual(T.mirror(measure), 1.0)
        self.assertEqual(pairs, 26)
        ref = T.reference(ds, [("facet_sag_sup", "mean"), ("facet_trans_sup", "mean")], LEVELS)
        for lv in LEVELS:
            r = ds["mean"].sel(level=lv, measure="facet_sag_sup", side="right").item()
            l_ = ds["mean"].sel(level=lv, measure="facet_sag_sup", side="left").item()
            self.assertEqual(ref["facet_sag_sup:mean"][lv][0], (l_ - r) / 2.0)
            self.assertGreater(ref["facet_sag_sup:mean"][lv][0], min(abs(r), abs(l_)) - 1e-9)
            r = ds["mean"].sel(level=lv, measure="facet_trans_sup", side="right").item()
            l_ = ds["mean"].sel(level=lv, measure="facet_trans_sup", side="left").item()
            self.assertEqual(ref["facet_trans_sup:mean"][lv][0], (r + l_) / 2.0)


class Registry(unittest.TestCase):
    def test_every_registered_measure_is_scored_or_has_no_rows(self):
        reg = MS.registry()
        self.assertGreater(len(reg), 60)
        scored, no_rows = [], []
        for key, m in reg.items():
            try:
                MS.select([key], levels=m.levels or LEVELS)
                scored.append(key)
                self.assertIn(m.kind, ("length", "area", "angle"))
                self.assertGreater(m.error, 0)
                self.assertTrue(m.levels)
            except ValueError as e:
                self.assertFalse(m.levels, key)
                no_rows.append(key)
                self.assertIn("no table row", str(e))
        self.assertEqual(len(scored) + len(no_rows), len(reg))
        self.assertIn("pedicle_w:mean", scored)
        self.assertIn("facet_area_sup:right", scored)
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

    def test_each_kind_has_its_own_error_and_power(self):
        reg = MS.registry()
        for key, m in reg.items():
            if not m.levels:
                self.assertIsNone(m.error, key)
                continue
            self.assertEqual(m.size_power, {"length": 1, "area": 2, "angle": 0}[m.kind], key)
            self.assertEqual(m.units, {"length": "mm", "area": "mm2", "angle": "deg"}[m.kind], key)
            if m.kind == "length":
                self.assertEqual(m.error, 1.0, key)
            elif m.kind == "angle":
                self.assertEqual(m.error, 3.0, key)
            else:
                # the error of a circle's area whose diameter is read 1 mm off on each of two axes
                mean_area = float(np.mean([r.mean for r in m.rows]))
                self.assertAlmostEqual(m.error, math.sqrt(math.pi * mean_area / 2.0), places=12)
        self.assertAlmostEqual(reg["canal_area"].error, 19.6, delta=0.05)
        self.assertAlmostEqual(reg["endplate_area"].error, 31.1, delta=0.05)

    def test_the_pool_is_every_measure_with_a_row_and_a_spread_at_every_level(self):
        pool = MS.pool()
        kinds = [m.kind for m in pool]
        self.assertEqual(len(pool), 32)
        self.assertEqual((kinds.count("length"), kinds.count("area"), kinds.count("angle")), (18, 6, 8))
        # each measure once, in the papers' order, a left-right pair as its mean
        names = [m.name for m in pool]
        self.assertEqual(len(set(names)), 32)
        self.assertEqual(names, [n for n in MN.MEASURES if n in names])
        for m in pool:
            self.assertEqual(m.side, "mean" if "%s:right" % m.name in MS.registry() else "whole", m.key)
            self.assertTrue(set(LEVELS) <= set(m.levels), m.key)
        self.assertEqual([MS.archive_key(m) for m in pool[:5]],
                         ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post"])
        self.assertTrue(set(MS.SPINEPS_7) <= {MS.archive_key(m) for m in pool})
        # every other measure of the papers is left out, and says why
        out = MS.left_out()
        self.assertEqual(set(out) | set(names), set(MN.MEASURES))
        self.assertEqual(set(out) & set(names), set())
        spreadless = sorted(k for k, why in out.items() if "no spread" in why)
        regional = sorted(k for k, why in out.items() if "levels" in why)
        self.assertEqual(spreadless, sorted(["endplate_wedge", "costovertebral_area", "rib_articulation_area",
                                             "facet_card_x_sup", "facet_card_x_inf", "facet_card_y_sup",
                                             "facet_card_y_inf"]))
        self.assertEqual(len(regional), 10)
        self.assertEqual(len(out), 17)
        self.assertIn("printed at 15 of the 22 levels C3 to L5 (T3 to L5)", out["pars_area"])

    def test_the_seven_in_the_archives_order_and_names(self):
        seven = MS.select(MS.SPINEPS_7)
        self.assertEqual([MS.archive_key(m) for m in seven], MS.SPINEPS_7)
        for m in seven:
            self.assertEqual(m.error, 1.0)
            self.assertTrue(set(LEVELS) <= set(m.levels))
        self.assertEqual(MS.resolve("pedicle"), ("pedicle_w", "mean"))
        self.assertEqual(MS.resolve("pedicle_h:left"), ("pedicle_h", "left"))
        with self.assertRaises(KeyError):
            MS.select(["no_such_measure"])
        with self.assertRaises(ValueError):
            MS.select(["pars_area:mean"])                  # printed from T3 down only
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

    def test_each_measure_carries_its_table_rows_mnemonics_measurers_and_correlations(self):
        ds = T.load()
        prov = {r["id"]: r for r in T.read_csv(T.PROVENANCE_CSV)}
        reg = MS.registry()
        for key, m in reg.items():
            self.assertEqual([r.level for r in m.rows], list(m.levels), key)
            self.assertEqual(m.correlations, (), key)
            self.assertEqual(len(m.mnemonics), 2 if m.side == "mean" else 1, key)
            for r in m.rows:
                self.assertEqual(r.n, 12, key)
                self.assertEqual(len(r.cells), len(m.mnemonics), key)
                for cell in r.cells:
                    self.assertIn(cell, prov, key)
                if m.side != "mean":
                    self.assertEqual(r.mean, ds["mean"].sel(level=r.level, measure=m.name, side=m.side).item())
                    self.assertEqual(r.sd, ds["sd"].sel(level=r.level, measure=m.name, side=m.side).item())
        pedicle = reg["pedicle_w:mean"]
        self.assertEqual(pedicle.mnemonics, ("PDWr", "PDWl"))
        t12 = pedicle.row("T12")
        right, left = reg["pedicle_w:right"].row("T12"), reg["pedicle_w:left"].row("T12")
        self.assertEqual(t12.mean, (right.mean + left.mean) / 2.0)
        self.assertEqual(t12.cells, right.cells + left.cells)
        # every pair's mean is table.reference's to the bit, its mean and its SD at every level
        for key, m in reg.items():
            if m.side == "mean":
                want = T.reference(ds, [m.selection], list(m.levels))[m.key]
                self.assertEqual({r.level: (r.mean, r.sd) for r in m.rows}, want, key)
        # the archive's SPINEPS measurer reads the seven and refuses the pedicle
        self.assertEqual({k for k, m in reg.items() if m.measurers}, set(MS.SPINEPS_7))
        self.assertEqual(reg["endplate"].measurers, ("archive/bordercall/spineps_map.py",))
        self.assertTrue(os.path.exists(os.path.join(ROOT, reg["endplate"].measurers[0])))
        self.assertEqual(reg["endplate"].mnemonics, ("EPWu",))

    def test_the_rule_reads_each_measures_own_error(self):
        seven = MS.select(MS.SPINEPS_7)
        mu, sd = MS.arrays(seven)
        keys = [MS.archive_key(m) for m in seven]
        cols = C.draw_columns(MS.reference(seven), ["typical"], 9, 3, keys)
        X, _, _ = C.fields(cols.values, [0, 1, 2])
        plain = R.name(X, [0, 1, 2], mu, sd, R.SYNTH)["all"]
        self.assertTrue(np.array_equal(MS.name(X, [0, 1, 2], seven)["all"], plain))
        noisy = [dataclasses.replace(m, error=5.0) if m.name == "h_post" else m for m in seven]
        got = MS.name(X, [0, 1, 2], noisy)["all"]
        self.assertGreater(np.abs(got - plain).max(), 1e-3)
        want = R.name(X, [0, 1, 2], mu, sd, R.SYNTH, noise=MS.errors(noisy))["all"]
        self.assertTrue(np.array_equal(got, want))
        sizes, _ = R.quadrature(R.SYNTH["scale_sd"])
        dense = R.dense_loglik(X[:4], [0, 1, 2], mu, sd, R.SYNTH, sizes[::40], noise=MS.errors(noisy))
        closed = R.loglik(X[:4], [0, 1, 2], mu, sd, R.SYNTH, sizes=sizes[::40], noise=MS.errors(noisy))
        self.assertLess(np.abs(dense - closed).max(), 1e-9)

    def test_a_measure_enters_once_and_a_pair_as_one_side_or_its_mean(self):
        for keys in (["pedicle_w:right", "pedicle_w:left"], ["pedicle", "pedicle_w:right"], ["endplate", "endplate"],
                     ["pedicle", "pedicle_w:mean"], ["facet_w_sup:left", "facet_w_sup:mean"]):
            with self.assertRaises(ValueError) as cm:
                MS.select(keys)
            self.assertIn("selected twice", str(cm.exception))
        self.assertEqual([m.key for m in MS.select(["pedicle", "pedicle_h:left", "endplate"])],
                         ["pedicle_w:mean", "pedicle_h:left", "endplate"])


if __name__ == "__main__":
    unittest.main()
