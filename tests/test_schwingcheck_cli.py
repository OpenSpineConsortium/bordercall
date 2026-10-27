"""`python -m schwingcheck name` names a field from a CSV, says so when there is nothing to name,
and `table check` holds the committed long CSV to the provenance.
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

    def test_an_area_is_refused_until_step_e(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [3, 4])
            with self.assertRaises(ValueError):
                run(["name", path, "--measures", "endplate", "canal_area"])


class Table(unittest.TestCase):
    def test_table_check_passes_on_the_committed_csv(self):
        code, out = run(["table", "check"])
        self.assertEqual(code, 0, out)
        self.assertIn("as written from the provenance", out)

    def test_the_module_runs_as_a_program(self):
        p = subprocess.run([sys.executable, "-m", "schwingcheck", "table", "check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
