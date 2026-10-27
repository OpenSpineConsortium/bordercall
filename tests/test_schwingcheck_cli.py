"""`python -m schwingcheck name` names a field from a CSV with any of its three engines, says so
when there is nothing to name, `rescore` gives the same rates with each of its three, `table
check` holds the committed long CSV to the provenance and `graph check` the committed graphs to the
models.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS                  # noqa: E402
from schwingcheck import __main__ as M           # noqa: E402
from schwingcheck import columns as C            # noqa: E402
from schwingcheck import measures as MS          # noqa: E402
from schwingcheck import score as S              # noqa: E402


def run(argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = M.main(argv)
    return code, out.getvalue()


class Name(unittest.TestCase):
    def _column(self, seed=8):
        seven = MS.select(MS.SPINEPS_7)
        keys = [MS.archive_key(m) for m in seven]
        cols = C.draw_columns(MS.reference(seven), ["typical"], seed, 1, keys)
        return keys, cols.values[0]

    def _write(self, d, keys, values, bodies, offsets=None, drop=()):
        path = os.path.join(d, "field.csv")
        with open(path, "w") as fh:
            fh.write("body," + ("offset," if offsets else "") + ",".join(keys) + "\n")
            for i, b in enumerate(bodies):
                vals = ["" if (i, k) in drop else "%.3f" % values[b, j] for j, k in enumerate(keys)]
                fh.write("%d," % i + ("%d," % offsets[i] if offsets else "") + ",".join(vals) + "\n")
        return path

    def test_a_field_of_three_consecutive_bodies(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [10, 11, 12])
            code, out = run(["name", path])
        self.assertEqual(code, 0)
        self.assertIn("field of 3 bodies at offsets [0, 1, 2]", out)
        self.assertIn("<- named", out)
        self.assertIn("99% set:", out)
        self.assertIn("the top place reaches 0.99:", out)
        named = [line.split()[0] for line in out.splitlines() if "<- named" in line][0]
        self.assertIn(named, LEVELS)

    def test_gaps_and_missing_values(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [4, 6, 8], offsets=[0, 2, 4], drop={(1, "canal_w"), (2, "h_post")})
            code, out = run(["name", path, "--measures", "endplate", "h_post", "canal_w"])
        self.assertEqual(code, 0)
        self.assertIn("offsets [0, 2, 4]", out)
        self.assertIn("measures endplate, h_post, canal_w", out)

    def test_no_body_and_no_measure(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [])
            code, out = run(["name", path])
            self.assertEqual(code, 1)
            self.assertIn("nothing to name", out)
            path = self._write(d, keys, values, [3, 4], drop={(i, k) for i in range(2) for k in keys})
            code, out = run(["name", path])
            self.assertEqual(code, 1)
            self.assertIn("the posterior is the prior", out)

    def test_offsets_follow_the_docstring(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "numbered.csv")
            with open(path, "w") as fh:
                # bodies numbered 4, 6, 8 with no offset column are consecutive bodies all the same
                fh.write("body," + ",".join(keys) + "\n")
                for b in (4, 6, 8):
                    fh.write("%d," % b + ",".join("%.3f" % values[10 + (b - 4) // 2, j] for j in range(len(keys))) + "\n")
            code, out = run(["name", path])
            self.assertEqual(code, 0)
            self.assertIn("offsets [0, 1, 2]", out)
            code, out = run(["name", path, "--offsets", "3", "5", "7"])
            self.assertEqual(code, 0)
            self.assertIn("offsets [0, 2, 4]", out)
            for bad, why in ((["3", "5"], "2 offsets for a field of 3 bodies"),
                             (["0", "2", "2"], "do not rise down the column")):
                code, out = run(["name", path, "--offsets"] + bad)
                self.assertEqual(code, 2)
                self.assertIn(why, out)
            path = self._write(d, keys, values, [4, 5, 6], offsets=[0, 1, 2])
            with open(path) as fh:
                lines = fh.read().splitlines()
            lines[2] = lines[2].replace("1,1,", "1,,", 1)
            with open(path, "w") as fh:
                fh.write("\n".join(lines) + "\n")
            code, out = run(["name", path])
            self.assertEqual(code, 2)
            self.assertIn("an offset for 2 of its 3 bodies", out)

    def test_every_engine_names_the_field(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [4, 6, 8], offsets=[0, 2, 4], drop={(1, "canal_w")})
            exact = {e: run(["name", path, "--engine", e]) for e in ("numpy", "pytensor")}
            code, out = run(["name", path, "--engine", "nuts", "--draws", "500", "--chains", "2", "--seed", "3"])
        self.assertEqual(exact["numpy"][0], 0)
        self.assertEqual(exact["numpy"], exact["pytensor"])
        self.assertEqual(code, 0)
        want = posteriors(exact["numpy"][1])
        got = posteriors(out)
        self.assertGreater(len(got), 1)
        for place, (p, se) in got.items():
            self.assertIsNotNone(se, place)
            if place in want:
                self.assertLess(abs(p - want[place][0]), 4.0 * se + 0.01, place)

    def test_an_area_is_refused_until_step_e(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [3, 4])
            with self.assertRaises(ValueError):
                run(["name", path, "--measures", "endplate", "canal_area"])


def posteriors(out):
    """{place: (posterior, its Monte Carlo error or None)} from the lines `name` prints."""
    got = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in LEVELS:
            got[parts[0]] = (float(parts[1]), float(parts[3]) if len(parts) > 3 and parts[2] == "+-" else None)
    return got


class Rescore(unittest.TestCase):
    def test_the_three_engines_give_the_same_rates(self):
        rates = {e: M.rescore([3], n_columns=4, seed=97, engine=e) for e in ("numpy", "pytensor", "pymc")}
        for e in ("pytensor", "pymc"):
            for regime in ("both", "ap", "lateral"):
                a, b = rates["numpy"]["3"]["regimes"][regime], rates[e]["3"]["regimes"][regime]
                self.assertEqual(S.compare(a, b, tol=1e-9), [], (e, regime))
                self.assertEqual(a["exact"], b["exact"], (e, regime))

    def test_an_unknown_engine_is_refused(self):
        with self.assertRaises(ValueError):
            M.rescore([1], n_columns=1, engine="stan")


class Graph(unittest.TestCase):
    def test_graph_check_passes_on_the_committed_graphs(self):
        code, out = run(["graph", "check"])
        self.assertEqual(code, 0, out)
        self.assertIn("graphs: as the models draw them", out)


class Table(unittest.TestCase):
    def test_table_check_passes_on_the_committed_csv(self):
        code, out = run(["table", "check"])
        self.assertEqual(code, 0, out)
        self.assertIn("panjabi_long.csv: as written from the provenance", out)
        self.assertIn("panjabi_specimens.csv: as written from the provenance", out)

    def test_the_module_runs_as_a_program(self):
        p = subprocess.run([sys.executable, "-m", "schwingcheck", "table", "check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
