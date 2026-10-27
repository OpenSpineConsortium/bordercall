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
from unittest import mock

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
        from schwingcheck import model as MD
        keys, values = self._column()
        library, returned = MD.hypothesis_posterior, []

        def recorded(*args, **kwargs):
            post, se = library(*args, **kwargs)
            returned.append((post.copy(), se.copy()))       # as returned, whatever is done to them after
            return post, se
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [4, 6, 8], offsets=[0, 2, 4], drop={(1, "canal_w")})
            exact = {e: run(["name", path, "--engine", e]) for e in ("numpy", "pytensor")}
            with mock.patch.object(MD, "hypothesis_posterior", side_effect=recorded):
                code, out = run(["name", path, "--engine", "nuts", "--draws", "500", "--chains", "2", "--seed", "3"])
        self.assertEqual(exact["numpy"][0], 0)
        self.assertEqual(exact["numpy"], exact["pytensor"])
        self.assertEqual(code, 0)
        want = posteriors(exact["numpy"][1])
        got = posteriors(out)
        self.assertGreater(len(got), 1)
        self.assertEqual(named(out), named(exact["numpy"][1]))
        # every place, a place an engine does not print (below 1e-6) counting as 0, within a bound
        # that does not come from the output under test
        for place in LEVELS:
            self.assertLess(abs(got.get(place, (0.0, None))[0] - want.get(place, (0.0, None))[0]), 0.01, place)
        # and what it prints is what the model returned, every place at 1e-6 or more with its
        # posterior and its Monte Carlo error to the six places printed; the model's own tests hold
        # those errors to the sampler's spread (test_schwingcheck_model.py)
        (post, se), = returned
        shown = printed(out)
        self.assertEqual(set(shown), {LEVELS[k] for k in range(post.shape[1]) if post[0, k] >= 1e-6})
        for place, text in shown.items():
            k = LEVELS.index(place)
            self.assertEqual(text, ("%.6f" % post[0, k], "%.6f" % se[0, k]), place)
        self.assertIn("below 0.001 a place's estimate tends to run low", out)
        self.assertNotIn("Monte Carlo", exact["numpy"][1])

    def test_name_prints_each_place_at_1e6_or_more_as_the_engine_returned_it(self):
        """The printing alone, on a posterior made to sit at its edges, so it does not hang on what
        one run of the sampler draws: a place at exactly 1e-6 is printed and one just under it is
        not, every place at 1e-6 or more is printed, seventeen of the twenty, so a table cut
        short fails, the places in order of their posterior, each posterior and error to six
        decimals as the engine returned it, whatever is done to the arrays after."""
        keys, values = self._column()
        post = np.zeros(20)
        post[[4, 0, 7, 12, 17, 3, 19, 8, 15, 10, 14, 1, 9, 16, 18, 2, 11, 13]] = [
            0.52, 0.2, 0.1, 0.05, 0.03, 0.02, 0.01, 0.005, 0.002, 0.001, 4e-4, 1.5e-4, 6.04e-5, 2.2e-5, 3.3e-6,
            1e-6, 9.99e-7, 3e-7]
        post[5] = 1.0 - post.sum()
        se = 1e-4 * np.arange(1, 21) + 3.21e-7
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [3, 4, 5])
            with mock.patch.object(M, "name_with", return_value=(post.copy(), se.copy())):
                code, out = run(["name", path, "--engine", "nuts", "--draws", "500", "--chains", "2"])
        self.assertEqual(code, 0, out)
        shown = printed(out)
        self.assertEqual(list(shown), [LEVELS[k] for k in (4, 0, 7, 5, 12, 17, 3, 19, 8, 15, 10, 14, 1, 9, 16, 18, 2)], out)
        for place, text in shown.items():
            k = LEVELS.index(place)
            self.assertEqual(text, ("%.6f" % post[k], "%.6f" % se[k]), place)
        self.assertEqual(named(out), LEVELS[4])

    def test_a_measure_with_no_row_at_a_level_or_an_unknown_measure_is_refused(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [3, 4])
            for measures, why in ((["endplate", "pars_area:mean"],
                                   "pars_area:mean has no table row at C3, C4, C5, C6, C7, T1, T2"),
                                  (["endplate", "nonesuch"], "no measure 'nonesuch' is registered")):
                code, out = run(["name", path, "--measures"] + measures)
                self.assertEqual(code, 2, out)
                self.assertIn("refused: " + why, out)

    def test_a_file_not_utf8_or_without_body_is_refused_by_what_is_wrong(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [3, 4])
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            with open(path, "w", encoding="utf-8-sig") as fh:      # the mark a spreadsheet may write
                fh.write(text)
            code, out = run(["name", path])
            self.assertEqual(code, 0, out)
            self.assertIn("field of 2 bodies", out)
            with open(path, "w", encoding="utf-8") as fh:            # a blank line before the header
                fh.write("# read on 27 October 2026\n\n" + text)
            code, out = run(["name", path])
            self.assertEqual(code, 0, out)
            self.assertIn("field of 2 bodies", out)
            with open(path, "w", encoding="utf-8") as fh:            # whole numbers as numpy writes them
                fh.write("body,endplate\n1.000000000000000000e+00,10.4\n0.0,10.1\n")
            code, out = run(["name", path])
            self.assertEqual(code, 0, out)
            self.assertIn("field of 2 bodies at offsets [0, 1], measures endplate", out)
            for encoding, written, why in (
                    ("latin-1", "# read by Ren\xe9\n" + text, "is not UTF-8 text ('utf-8' codec can't decode byte 0xe9"),
                    ("utf-8", text.replace("body,", "vertebra,", 1), "the field has no column `body`: its columns are vertebra,"),
                    ("utf-8", "endplate,body\n10.1,0\n10.4\n", "row 2 of the field has no body number"),
                    ("utf-8", "body,endplate\n0,10.1\nfirst,10.4\n", "row 2 of the field has the body 'first', which is not a whole number"),
                    ("utf-8", "body,endplate\n0,10.1\n1.5,10.4\n", "row 2 of the field has the body '1.5', which is not a whole number")):
                with open(path, "w", encoding=encoding) as fh:
                    fh.write(written)
                code, out = run(["name", path])
                self.assertEqual(code, 2, out)
                self.assertIn("refused: ", out)
                self.assertIn(why, out)

    def test_nuts_is_refused_before_it_samples_when_it_cannot_give_its_error(self):
        keys, values = self._column()
        with tempfile.TemporaryDirectory() as d:
            path = self._write(d, keys, values, [3, 4])
            for extra, why in ((["--draws", "19"], "19 draws a chain make no 20 batches"),
                               (["--chains", "0"], "one chain at least")):
                # no model is built, so nothing is sampled
                with mock.patch("schwingcheck.model.naming", side_effect=AssertionError("a model was built")):
                    code, out = run(["name", path, "--engine", "nuts"] + extra)
                self.assertEqual(code, 2, out)
                self.assertIn(why, out)
                self.assertNotIn("posterior", out)


def named(out):
    """The place `name` names: the first word of the line it marks."""
    return next(line.split()[0] for line in out.splitlines() if line.endswith("<- named"))


def printed(out):
    """{place: (its posterior, its Monte Carlo error or None)} as `name` prints them, the text
    itself, in the order printed."""
    got = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in LEVELS:
            got[parts[0]] = (parts[1], parts[3] if len(parts) > 3 and parts[2] == "+-" else None)
    return got


def posteriors(out):
    """{place: (posterior, its Monte Carlo error or None)} from the lines `name` prints."""
    return {place: (float(p), None if e is None else float(e)) for place, (p, e) in printed(out).items()}


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
