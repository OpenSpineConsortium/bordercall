"""Rescoring seed 97's 2,000 columns reproduces the record of 2026-10-26, and a record written
here reads back whole.

The record test is the slow one, a few minutes: it draws the archive's scoring columns, scores
every field of 1, 3 and 9 bodies under the three regimes on the checked table (which equals the
archive's in every value the record used, tests/test_schwingcheck_table.py) and holds every rate
exact.json records for the three regimes at those widths (`widths[n].regimes`), the claims
included, to what this package computes, the share named to the digit and the rest to 1e-9. The
127 subsets of the seven measures that exact.json also records at each width (`widths[n].subsets`)
are not rescored here. Set SCHWINGCHECK_RECORD_WIDTHS to run fewer widths while developing, never
in a pull request.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from schwingcheck import LEVELS                  # noqa: E402
from schwingcheck import __main__ as M           # noqa: E402
from schwingcheck import columns as C            # noqa: E402
from schwingcheck import measures as MS          # noqa: E402
from schwingcheck import records as REC          # noqa: E402
from schwingcheck import rule as R               # noqa: E402
from schwingcheck import score as S              # noqa: E402

EXACT_JSON = os.path.join(ROOT, "archive", "records", "exact-2026-10-26", "exact.json")
RECORD_KEYS = ["n_fields", "places", "exact", "se_cluster", "within_one", "errors", "bayes_error_predicted",
               "bayes_error_counted", "log_loss", "selective", "selective_099_by_called_region", "credible",
               "mapq", "calibration", "by_start", "by_centre", "landmarks", "confusion_offsets", "measures", "claims"]


class Record(unittest.TestCase):
    def test_seed_97_reproduces_the_rates_of_exact_json_at_1_3_and_9_bodies(self):
        with open(EXACT_JSON) as fh:
            rec = json.load(fh)
        self.assertEqual(rec["score_seed"], M.SCORE_SEED)
        self.assertEqual(rec["n_columns"], M.N_SCORE)
        self.assertEqual(rec["gh_nodes"], R.GH_NODES)
        self.assertEqual(rec["levels"], LEVELS)
        self.assertEqual(rec["measures"], MS.SPINEPS_7)
        self.assertEqual(rec["synth"], R.SYNTH)
        widths = [int(w) for w in os.environ.get("SCHWINGCHECK_RECORD_WIDTHS", "1 3 9").split()]
        got = M.rescore(widths, n_columns=rec["n_columns"], seed=rec["score_seed"])
        for n in widths:
            want = rec["widths"][str(n)]
            self.assertEqual(want["places"], got[str(n)]["places"])
            for regime in ("both", "ap", "lateral"):
                a = {k: want["regimes"][regime][k] for k in RECORD_KEYS if k in want["regimes"][regime]}
                b = {k: got[str(n)]["regimes"][regime][k] for k in a}
                diffs = S.compare(a, b, tol=1e-9)
                self.assertEqual(diffs, [], "n=%d %s: %s" % (n, regime, diffs[:10]))
                self.assertEqual(want["regimes"][regime]["exact"], got[str(n)]["regimes"][regime]["exact"])


class InferenceData(unittest.TestCase):
    def test_a_record_reads_back_whole(self):
        seven = MS.select(MS.SPINEPS_7)
        ref = MS.reference(seven)
        mu, sd = MS.arrays(seven)
        keys = [MS.archive_key(m) for m in seven]
        cols = C.draw_columns(ref, ["typical"], 5, 12, keys)
        offsets = [0, 2, 4]
        X, truth, grp = C.fields(cols.values, offsets)
        post = R.name(X, offsets, mu, sd, R.SYNTH)["all"]
        rates = S.summary(post, truth, grp, 3)
        rec = REC.build(post, truth, grp, X, offsets, keys, LEVELS, rates, command="python -m schwingcheck test",
                        seeds={"score": 5}, synth=R.SYNTH, mu=mu, sd=sd, digests={"x": "y"}, noise=MS.errors(seven))
        with tempfile.TemporaryDirectory() as d:
            path = REC.write(rec, os.path.join(d, "r.nc"))
            back = REC.read(path)
            self.assertEqual(sorted(back.children), ["constant_data", "observed_data", "posterior", "rates", "truth"])
            self.assertTrue(np.array_equal(back["posterior"].ds["p"].values, post))
            self.assertEqual(list(back["posterior"].ds["place"].values), LEVELS[:post.shape[1]])
            self.assertTrue(np.array_equal(back["truth"].ds["place"].values, truth))
            x = back["observed_data"].ds["x"].values
            self.assertTrue(np.array_equal(np.isnan(x), np.isnan(X)) and np.array_equal(x[~np.isnan(x)], X[~np.isnan(X)]))
            self.assertEqual(list(back["constant_data"].ds["offsets"].values), offsets)
            self.assertTrue(np.array_equal(back["constant_data"].ds["mu"].values, mu))
            self.assertEqual(back["constant_data"].ds["noise"].values.tolist(), [1.0] * len(keys))
            attrs = REC.attrs_of(back)
            self.assertEqual(attrs["command"], "python -m schwingcheck test")
            self.assertEqual(attrs["seeds"], {"score": 5})
            self.assertEqual(attrs["synth"], R.SYNTH)
            self.assertEqual(attrs["digests"]["x"], "y")
            self.assertEqual(attrs["digests"]["schwingcheck"], REC.code_digest())
            self.assertEqual(attrs["measures"], keys)
            self.assertEqual(REC.rates_of(back)["exact"], rates["exact"])
            self.assertEqual(back["rates"].ds["exact"].item(), rates["exact"])
            import arviz as az
            self.assertIsInstance(back, type(az.from_dict({"posterior": {"q": np.zeros((1, 2, 3))}})))
            back.close()


if __name__ == "__main__":
    unittest.main()
