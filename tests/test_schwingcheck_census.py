"""The census of the measures (census.py) on small sources, and its record as committed.

    python -m unittest tests.test_schwingcheck_census -v      # from the repository's root, in the PyMC venv

The information a measure gives about a lone body is read in nats against log K: a measure whose
means stand far apart gives nearly log K at every level and names nearly every body, a measure the
same at every level gives nothing and names one body in K, and no measure gives more than log K.
A measure is drawn by the generator's law for its kind, an angle never scaled by the size. The
greedy order adds the largest conditional gain, its cumulative information never falls, and a
measure that adds little once a separating one is in is listed under the measure it shares most
with, the pair's redundancy I(m) + I(m') - I({m, m'}). Panjabi's four papers are one source whose
32 measures with rows at every level form one group and whose 7 printed with no spread are listed
as unranked; the other papers' series become one source per (paper, cohort, technique, sex,
group), quoted values, figure examples, pig cohorts, rows outside C3 to L5 and rows with no spread
left out with their reasons, a disc's row counted to the body above it and the sides averaged; a
table in the morphometrics schema reads its own error column and its correlation table. A run on
a small series writes a record whose four tables the check finds in a README and whose changed
cell it catches. The committed record: the README carries its tables, it was made by committed
code that did not change while it ran, its inputs are the committed copies by sha256, its sources
are what the committed series give, every key of the vocabulary is ranked or listed once, and no
information stands above log K.
"""
from __future__ import annotations

import csv
import math
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS                                   # noqa: E402
from schwingcheck import census as CE                             # noqa: E402
from schwingcheck import chain_study as CS                        # noqa: E402
from schwingcheck import measures as MS                           # noqa: E402
from schwingcheck import rule as R                                # noqa: E402
from schwingcheck.mnemonics import MEASURES                       # noqa: E402

NODES = R.quadrature(R.SYNTH["scale_sd"])
FOUR = ("T10", "T11", "T12", "L1")
SERIES_HEADER = ["paper", "cohort", "technique", "source_of_values", "key", "level", "sex", "group", "side",
                 "mean", "sd", "n", "sd_from", "n_from", "units", "vs_panjabi", "definition", "tables", "pages"]


def series(key, kind, means, sds, levels=FOUR, error=None, n=12):
    error = CE.error_for(kind, means) if error is None else error
    return CE.Series(key, kind, float(error), tuple(levels), tuple(float(m) for m in means),
                     tuple(float(s) for s in sds), tuple([n] * len(levels)))


def separating(key="far", kind="length"):
    return series(key, kind, [10.0, 40.0, 70.0, 100.0], [1.0] * 4)


def flat(key="same", kind="length"):
    return series(key, kind, [30.0] * 4, [3.0] * 4)


def quiet(*args):
    pass


def write_series(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SERIES_HEADER)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in SERIES_HEADER})


def row(paper="smith2020", cohort="ct_adults", technique="ct", key="body_w", level="L1", mean="40", sd="3", n="30",
        units="mm", source="this paper", sex="all", group="", side=""):
    return {"paper": paper, "cohort": cohort, "technique": technique, "source_of_values": source, "key": key,
            "level": level, "sex": sex, "group": group, "side": side, "mean": mean, "sd": sd, "n": n, "units": units}


class TheInformation(unittest.TestCase):
    def group(self, measures, n=200, seed=3):
        return CE.census_group(measures, n, seed, NODES, {})

    def test_a_measure_whose_means_stand_apart_gives_nearly_log_k_and_names_nearly_every_body(self):
        g = self.group([separating()])
        m = g["measures"][0]
        for info, exact in zip(m["standalone"], m["standalone_exact"]):
            self.assertGreater(info, math.log(4) - 0.05)
            self.assertGreater(exact, 0.98)

    def test_a_measure_the_same_at_every_level_gives_nothing_and_names_one_body_in_k(self):
        g = self.group([flat()], n=400)
        m = g["measures"][0]
        for info, se, exact in zip(m["standalone"], m["standalone_se"], m["standalone_exact"]):
            self.assertLess(abs(info), 4 * se + 0.02)
        self.assertLess(abs(np.mean(m["standalone_exact"]) - 0.25), 0.08)

    def test_no_measure_gives_more_than_log_k(self):
        g = self.group([separating(), flat(), separating("angle", "angle"), series("ratio", "ratio", [0.5, 0.6, 0.7, 0.8], [0.02] * 4)])
        for m in g["measures"]:
            self.assertLessEqual(max(m["standalone"]), math.log(4) + 1e-9)
        for e in g["order"]:
            self.assertLessEqual(max(e["cumulative"]), math.log(4) + 1e-9)

    def test_each_kind_is_drawn_by_the_generators_law(self):
        n = 20000
        length, angle = series("len", "length", [50.0] * 4, [2.0] * 4), series("ang", "angle", [50.0] * 4, [2.0] * 4)
        X, truth = CE.draw([length, angle], n, 5)
        self.assertEqual(X.shape, (4 * n, 2, 1))
        self.assertEqual(list(np.bincount(truth)), [n] * 4)
        # an angle is never scaled by the size: its spread is the table's with the error, a length's is wider
        sd_angle = math.sqrt(2.0 ** 2 + angle.error ** 2)
        sd_length = math.sqrt((math.exp(R.SYNTH["scale_sd"] ** 2) - 1) * 50.0 ** 2 + 2.0 ** 2 + length.error ** 2)
        self.assertLess(abs(X[:, 1, 0].std() - sd_angle), 0.05 * sd_angle)
        self.assertLess(abs(X[:, 0, 0].std() - sd_length), 0.05 * sd_length)
        self.assertEqual(length.power, 1)
        self.assertEqual(angle.power, 0)
        self.assertEqual(series("a", "area", [100.0] * 4, [5.0] * 4).power, 2)
        self.assertEqual(series("r", "ratio", [0.5] * 4, [0.05] * 4).power, 0)

    def test_the_greedy_order_adds_the_largest_gain_and_never_falls(self):
        a, b, c = separating("far"), series("near", "length", [30.0, 33.0, 36.0, 39.0], [2.0] * 4), flat("same")
        g = self.group([c, b, a])
        order = g["order"]
        self.assertEqual([e["rank"] for e in order], [1, 2, 3])
        self.assertEqual(order[0]["key"], "far")
        self.assertEqual(order[1]["key"], "near")
        self.assertEqual(sorted(e["key"] for e in order), ["far", "near", "same"])
        sums = [sum(e["cumulative"]) for e in order]
        for before, after in zip(sums, sums[1:]):
            self.assertGreaterEqual(after, before - 0.02)
        for e in order:
            self.assertAlmostEqual(e["conditional_sum"], sum(e["conditional"]), places=9)
        self.assertEqual(order[0]["repeats"], None)
        self.assertEqual(order[0]["conditional"], order[0]["cumulative"])

    def test_a_measure_that_adds_little_is_listed_under_the_one_it_shares_most_with(self):
        a, twin, other = separating("far"), separating("twin"), series("other", "length", [30.0, 33.0, 36.0, 39.0], [2.0] * 4)
        g = self.group([other, twin, a])
        order = {e["key"]: e for e in g["order"]}
        first = g["order"][0]["key"]
        self.assertIn(first, ("far", "twin"))
        second = "twin" if first == "far" else "far"
        e = order[second]
        self.assertLess(e["conditional_sum"], CE.REPEAT_SHARE * e["standalone_sum"])
        self.assertEqual(e["repeats"], first)
        # the pair's redundancy is nearly the whole of what each gives alone: both name the body
        self.assertGreater(e["redundancy"], 0.8 * e["standalone_sum"])
        self.assertEqual(order["other"]["repeats"] in (first, second, None), True)

    def test_the_correlation_table_lists_sharing_pairs_at_the_threshold(self):
        a, b = separating("far"), flat("same")
        corr = {("far", "same"): 0.71, ("far", "zzz"): 0.9, ("same", "far"): 0.5}
        g = CE.census_group([a, b], 50, 1, NODES, corr)
        self.assertEqual(g["shared_by_correlation"], [{"a": "far", "b": "same", "r": 0.71}])
        g = CE.census_group([a, b], 50, 1, NODES, {("far", "same"): 0.69})
        self.assertEqual(g["shared_by_correlation"], [])


class TheSources(unittest.TestCase):
    def test_panjabis_four_papers_are_one_source_of_42_measures_with_7_unranked(self):
        src, left = CE.panjabi_source()
        self.assertEqual(src.id, "panjabi")
        self.assertEqual(len(src.measures), 42)
        self.assertEqual(len({m.key for m in src.measures}), 42)
        self.assertEqual(len(src.measures) + len(left), len(MEASURES))
        self.assertEqual({u["reason"] for u in left}, {"printed as a mean with no spread"})
        groups = CE.groups_of(src)
        self.assertEqual([len(g[0].levels) for g in groups], [22, 15, 12, 11, 10, 5])
        self.assertEqual(len(groups[0]), 32)
        self.assertEqual(sorted(m.key for m in groups[0]), sorted(m.key.split(":")[0] for m in MS.pool()))
        reg = MS.registry()
        for m in src.measures:
            self.assertIn(m.kind, CE.KIND_POWER)
            self.assertEqual(m.error, reg[MS._pool_key(m.key, reg)].error)
            self.assertEqual(list(m.levels), [lv for lv in LEVELS if lv in m.levels])

    def test_a_disc_counts_to_the_body_above_it_and_nothing_outside_c3_to_l5(self):
        self.assertEqual(CE.body_level("L4-L5"), "L4")
        self.assertEqual(CE.body_level("T12-L1"), "T12")
        self.assertEqual(CE.body_level(" L3 "), "L3")
        self.assertEqual(CE.body_level("L5-S1"), "L5")
        for outside in ("C2", "S1", "L6", "T13", "C2-C3", ""):
            self.assertIsNone(CE.body_level(outside), outside)

    def test_the_errors_are_the_rules_own_by_kind(self):
        self.assertEqual(CE.error_for("length", [40.0]), MS.LENGTH_ERROR_MM)
        self.assertAlmostEqual(CE.error_for("area", [100.0, 300.0]), math.sqrt(math.pi * 200.0 / 2.0) * MS.LENGTH_ERROR_MM)
        self.assertEqual(CE.error_for("angle", [30.0]), MS.ANGLE_ERROR_DEG)
        self.assertEqual(CE.error_for("ratio", [0.5]), CE.RATIO_ERROR)
        with self.assertRaises(ValueError):
            CE.error_for("count", [1.0])

    def test_the_other_papers_series_become_sources_and_reasons(self):
        rows = []
        for lv, m in zip(("L1", "L2", "L3", "L4", "L5"), (40, 41, 42, 43, 44)):
            rows.append(row(level=lv, mean=str(m)))
        rows.append(row(key="body_w", level="L1", mean="70", sd="4", sex="male"))           # another sex: its own source
        rows.append(row(key="body_w", level="L2", mean="71", sd="4", sex="male"))
        rows.append(row(key="disc_h", level="L4-L5", mean="10", sd="1"))                      # a disc, counted to L4
        rows.append(row(key="disc_h", level="L3-L4", mean="9", sd="1"))
        rows.append(row(key="disc_h", level="L5-S1", mean="11", sd="1", side="right"))        # L5, the mean of the sides
        rows.append(row(key="disc_h", level="L5-S1", mean="13", sd="3", side="left"))
        rows.append(row(key="quoted", level="L1", mean="1", sd="1", source="Jones et al [3]"))
        rows.append(row(key="quoted", level="L2", mean="1", sd="1", source="Jones et al [3]"))
        rows.append(row(key="pig", level="L1", mean="1", sd="1", cohort="porcine_landrace"))
        rows.append(row(key="pig", level="L2", mean="1", sd="1", cohort="porcine_landrace"))
        rows.append(row(key="s1_only", level="S1", mean="1", sd="1"))
        rows.append(row(key="s1_only", level="C2", mean="1", sd="1"))
        rows.append(row(key="no_sd", level="L1", mean="1", sd=""))
        rows.append(row(key="no_sd", level="L2", mean="1", sd=""))
        rows.append(row(key="zero_sd", level="L1", mean="1", sd="0"))
        rows.append(row(key="zero_sd", level="L2", mean="1", sd="0"))
        rows.append(row(key="one_level", level="L3", mean="1", sd="1"))
        rows.append(row(key="in_cm", level="L1", mean="1", sd="1", units="cm"))
        rows.append(row(key="in_cm", level="L2", mean="1", sd="1", units="cm"))
        rows.append(row(key="canal_index", level="L1", mean="0.5", sd="0.05", units="ratio"))
        rows.append(row(key="canal_index", level="L2", mean="0.6", sd="0.05", units="ratio"))
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "series.csv")
            write_series(path, rows)
            sources, left = CE.series_sources(path)
        by = {s.id: s for s in sources}
        self.assertEqual(sorted(by), ["smith2020 | ct_adults | ct | all", "smith2020 | ct_adults | ct | male"])
        main = by["smith2020 | ct_adults | ct | all"]
        keys = {m.key: m for m in main.measures}
        self.assertEqual(sorted(keys), ["body_w", "canal_index", "disc_h"])
        self.assertEqual(keys["body_w"].levels, ("L1", "L2", "L3", "L4", "L5"))
        self.assertEqual(keys["body_w"].mean, (40.0, 41.0, 42.0, 43.0, 44.0))
        self.assertEqual(keys["body_w"].n, (30, 30, 30, 30, 30))
        self.assertEqual(keys["body_w"].kind, "length")
        self.assertEqual(keys["disc_h"].levels, ("L3", "L4", "L5"))
        self.assertEqual(keys["disc_h"].mean, (9.0, 10.0, 12.0))
        self.assertEqual(keys["disc_h"].sd, (1.0, 1.0, 2.0))
        self.assertEqual(keys["canal_index"].kind, "ratio")
        self.assertEqual(keys["canal_index"].error, CE.RATIO_ERROR)
        male = by["smith2020 | ct_adults | ct | male"]
        self.assertEqual([m.key for m in male.measures], ["body_w"])
        self.assertEqual(male.measures[0].levels, ("L1", "L2"))
        reasons = {u["key"]: u["reason"] for u in left}
        self.assertEqual(reasons["quoted"], "values quoted from another paper")
        self.assertEqual(reasons["pig"], "a quoted value, a figure's example or a pig cohort")
        self.assertEqual(reasons["s1_only"], "printed outside C3 to L5 only")
        self.assertEqual(reasons["no_sd"], "printed as a mean with no spread")
        self.assertEqual(reasons["zero_sd"], "printed with a spread of zero")
        self.assertEqual(reasons["one_level"], "printed at one level only, which names nothing")
        self.assertEqual(reasons["in_cm"], "not a length, area, angle or ratio (cm)")
        self.assertEqual(set(reasons), {"quoted", "pig", "s1_only", "no_sd", "zero_sd", "one_level", "in_cm"})
        self.assertTrue(all(u["source"] == "papers" for u in left))

    def test_a_table_in_the_morphometrics_schema_reads_its_error_and_its_correlation(self):
        with tempfile.TemporaryDirectory() as tmp:
            table = os.path.join(tmp, "levels.csv")
            with open(table, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["level", "measure", "kind", "n", "mean", "sd", "error"])
                for lv, m, e in zip(("L1", "L2", "L3"), (40, 42, 44), (0.7, 0.8, 0.9)):
                    w.writerow([lv, "body_w", "length", 228, m, 3.0, e])
                for lv, m in zip(("L1", "L2", "L3"), (30, 31, 32)):
                    w.writerow([lv, "pedicle_angle", "angle", 228, m, 2.0, ""])
                w.writerow(["L1", "alone", "length", 228, 1, 1, ""])
                w.writerow(["L4", "no_sd", "length", 228, 1, "", ""])
                w.writerow(["L5", "no_sd", "length", 228, 1, 0, ""])
            corr = os.path.join(tmp, "correlation.csv")
            with open(corr, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["level", "measure_a", "measure_b", "n", "r"])
                w.writerow(["L1", "body_w", "pedicle_angle", 228, -0.8])
                w.writerow(["L2", "pedicle_angle", "body_w", 228, 0.6])
                w.writerow(["L3", "body_w", "pedicle_angle", 228, 0.75])
                w.writerow(["L1", "body_w", "body_w", 228, 1.0])
                w.writerow(["L1", "body_w", "alone", 228, ""])
            src = CE.table_source(table, "gold3", corr)
        self.assertEqual(src.id, "gold3")
        keys = {m.key: m for m in src.measures}
        self.assertEqual(sorted(keys), ["body_w", "pedicle_angle"])
        self.assertEqual(keys["body_w"].error, 0.8)
        self.assertEqual(keys["body_w"].n, (228, 228, 228))
        self.assertEqual(keys["pedicle_angle"].error, MS.ANGLE_ERROR_DEG)
        self.assertEqual(keys["pedicle_angle"].kind, "angle")
        self.assertEqual(src.correlation, {("body_w", "pedicle_angle"): 0.75})
        with tempfile.TemporaryDirectory() as tmp:
            table = os.path.join(tmp, "levels.csv")
            with open(table, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["level", "measure", "kind", "n", "mean", "sd", "error"])
                w.writerow(["L1", "x", "count", 1, 1, 1, ""])
                w.writerow(["L2", "x", "count", 1, 1, 1, ""])
            with self.assertRaises(ValueError):
                CE.table_source(table, "gold3")


class ARunAndItsTables(unittest.TestCase):
    """A run on Panjabi's table and one small series, with few bodies, so that the record's shape,
    its tables and the check are tested as the committed record is made."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        rows = []
        for lv, m in zip(("L1", "L2", "L3", "L4", "L5"), (40, 42, 44, 46, 48)):
            rows.append(row(level=lv, mean=str(m), sd="2"))
            rows.append(row(key="canal_ap", level=lv, mean=str(m / 2), sd="1.5"))
        rows.append(row(key="quoted", level="L1", mean="1", sd="1", source="Jones et al [3]"))
        rows.append(row(key="quoted", level="L2", mean="1", sd="1", source="Jones et al [3]"))
        cls.series = os.path.join(cls.tmp.name, "series.csv")
        write_series(cls.series, rows)
        cls.vocabulary = os.path.join(cls.tmp.name, "vocabulary.csv")
        with open(cls.vocabulary, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["key", "kind", "units", "panjabi", "mnemonic", "definition"])
            w.writerow(["body_w", "length", "mm", "no", "", "the body's width"])
            w.writerow(["canal_ap", "length", "mm", "yes", "SCD", "the canal's depth"])
            w.writerow(["quoted", "length", "mm", "no", "", "a quoted measure"])
            w.writerow(["never_tabled", "angle", "deg", "no", "", "named, no table"])
            w.writerow(["subject_age", "years", "years", "no", "", "the subjects' age"])
            for name in MEASURES:
                w.writerow([name, "length", "mm", "yes", "", ""])
        cls.out = os.path.join(cls.tmp.name, "census.json")
        cls.record = CE.run(cls.series, cls.vocabulary, n_per_level=3, seed=11, log=quiet)
        CS.write(cls.record, cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_record_says_how_it_was_made(self):
        r = self.record
        self.assertEqual(r["fields_per_level"], 3)
        self.assertEqual(r["seed"], 11)
        self.assertEqual(r["levels"], list(LEVELS))
        self.assertEqual(r["nodes"], "Gauss-Hermite %d" % len(NODES[0]))
        self.assertEqual(r["ratio_error"], CE.RATIO_ERROR)
        self.assertEqual(set(r["inputs"]), {"series", "vocabulary"})
        self.assertEqual(r["inputs"]["series"]["sha256"], CE.sha256(self.series))
        self.assertIn("--fields 3", r["command"])
        self.assertEqual(set(r["made_by"]), {"digests", "git"})
        self.assertEqual(r["changed_during_run"], {})
        self.assertEqual([s["id"] for s in r["sources"]], ["panjabi", "smith2020 | ct_adults | ct | all"])
        small = r["sources"][1]
        self.assertEqual(small["n_measures"], 2)
        self.assertEqual(len(small["groups"]), 1)
        self.assertEqual(small["groups"][0]["levels"], ["L1", "L2", "L3", "L4", "L5"])
        self.assertEqual(sorted(e["key"] for e in small["groups"][0]["order"]), ["body_w", "canal_ap"])
        self.assertEqual(small["groups"][0]["seed"], 11 + 104729)

    def test_every_key_of_the_vocabulary_is_ranked_or_listed_once(self):
        ranked = {m["key"] for s in self.record["sources"] for g in s["groups"] for m in g["measures"]}
        unranked = [u["key"] for u in self.record["unranked"]]
        self.assertEqual(len(unranked), len(set(unranked)))
        self.assertEqual(ranked & set(unranked), set())
        vocabulary = {v["key"] for v in self.record["vocabulary"]}
        self.assertEqual(vocabulary, ranked | set(unranked))
        reasons = {u["key"]: u["reason"] for u in self.record["unranked"]}
        self.assertEqual(reasons["quoted"], "values quoted from another paper")
        self.assertEqual(reasons["never_tabled"], "named in the reread, no paper prints a table of it")
        self.assertEqual(reasons["subject_age"], "not a measure of a vertebra (years)")
        self.assertEqual(reasons["endplate_wedge"], "printed as a mean with no spread")
        self.assertIn("canal_ap", ranked)
        self.assertIn("body_w", ranked)

    def test_the_tables_and_the_check(self):
        tables = CE.tables(self.out)
        self.assertEqual(sorted(tables), ["census:order", "census:papers", "census:ranking", "census:unranked"])
        ranking = tables["census:ranking"].splitlines()
        self.assertEqual(len(ranking), 2 + len(LEVELS))
        self.assertTrue(ranking[2].startswith("| C3 |"))
        self.assertIn(", of 1.61", tables["census:ranking"])             # a five-level source against its own log K
        order = tables["census:order"].splitlines()
        self.assertEqual(len(order), 2 + 32)
        self.assertTrue(order[2].startswith("| 1 | "))
        papers = tables["census:papers"].splitlines()
        self.assertEqual(len(papers), 2 + 2)
        self.assertIn("| canal_ap | yes | 1 | L1 to L5 (5) |", tables["census:papers"])
        self.assertIn("| body_w | no | 1 | L1 to L5 (5) |", tables["census:papers"])
        self.assertIn("| never_tabled | named in the reread, no paper prints a table of it |", tables["census:unranked"])
        readme = os.path.join(self.tmp.name, "README.md")
        with open(readme, "w") as f:
            f.write("# A README\n\n")
            for key, text in tables.items():
                f.write("<!-- %s -->\n%s<!-- /%s -->\n\n" % (key, text, key))
        self.assertEqual(CE.check(readme, self.out), [])
        with open(readme) as f:
            text = f.read()
        with open(readme, "w") as f:
            f.write(text.replace("| never_tabled |", "| never_tabled_changed |"))
        self.assertNotEqual(CE.check(readme, self.out), [])

    def test_the_command_line_prints_a_table_and_checks(self):
        import io
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            code = CE.main(["table", "--out", self.out, "--which", "unranked"])
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), CE.tables(self.out)["census:unranked"])


@unittest.skipUnless(os.path.exists(CE.RECORD), "the record is not made yet")
class CommittedRecord(unittest.TestCase):
    """records/census-2026-10-29/ as committed."""

    @classmethod
    def setUpClass(cls):
        cls.record = CE.load()

    def test_the_readme_carries_its_tables(self):
        self.assertEqual(CE.check(), [])

    def test_it_was_made_by_committed_code_that_did_not_change(self):
        self.assertEqual(self.record["changed_during_run"], {})
        self.assertFalse(self.record["made_by"]["git"]["package_changed"])
        self.assertEqual(self.record["fields_per_level"], CE.FIELDS)
        self.assertEqual(self.record["seed"], CE.SEED)

    def test_its_inputs_are_the_committed_copies(self):
        for name, info in self.record["inputs"].items():
            path = os.path.join(CE.ROOT, info["path"])
            self.assertTrue(os.path.exists(path), path)
            self.assertEqual(CE.sha256(path), info["sha256"], name)
        self.assertEqual(set(self.record["inputs"]), {"series", "vocabulary"})

    def test_its_sources_are_what_the_committed_series_give(self):
        sources, _ = CE.series_sources(os.path.join(CE.ROOT, self.record["inputs"]["series"]["path"]))
        self.assertEqual([s["id"] for s in self.record["sources"]], ["panjabi"] + [s.id for s in sources])
        for want, got in zip(sources, self.record["sources"][1:]):
            self.assertEqual(got["n_measures"], len(want.measures))
            self.assertEqual(sorted(m["key"] for g in got["groups"] for m in g["measures"]), sorted(m.key for m in want.measures))
        panjabi = self.record["sources"][0]
        self.assertEqual(panjabi["n_measures"], 42)
        self.assertEqual(sorted(len(g["levels"]) for g in panjabi["groups"]), [5, 10, 11, 12, 15, 22])
        whole = next(g for g in panjabi["groups"] if len(g["levels"]) == 22)
        self.assertEqual(sorted(m["key"] for m in whole["measures"]), sorted(m.key.split(":")[0] for m in MS.pool()))

    def test_every_key_of_the_vocabulary_is_ranked_or_listed_once(self):
        ranked = {m["key"] for s in self.record["sources"] for g in s["groups"] for m in g["measures"]}
        unranked = [u["key"] for u in self.record["unranked"]]
        self.assertEqual(len(unranked), len(set(unranked)))
        self.assertEqual(ranked & set(unranked), set())
        self.assertEqual({v["key"] for v in self.record["vocabulary"]}, ranked | set(unranked))
        self.assertEqual(len(self.record["vocabulary"]), 106)

    def test_no_information_stands_above_log_k(self):
        for s in self.record["sources"]:
            for g in s["groups"]:
                top = math.log(len(g["levels"])) + 1e-9
                for m in g["measures"]:
                    self.assertLessEqual(max(m["standalone"]), top, (s["id"], m["key"]))
                    self.assertTrue(all(0.0 <= x <= 1.0 for x in m["standalone_exact"]))
                for e in g["order"]:
                    self.assertLessEqual(max(e["cumulative"]), top, (s["id"], e["key"]))
                self.assertEqual([e["rank"] for e in g["order"]], list(range(1, len(g["measures"]) + 1)))


if __name__ == "__main__":
    unittest.main()
