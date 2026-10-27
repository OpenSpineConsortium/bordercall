"""The command line of the package.

    python -m schwingcheck table write                 # the long CSV and the specimens from the provenance record
    python -m schwingcheck table check                 # the committed CSVs are what write would write
    python -m schwingcheck name FIELD.csv [--measures endplate h_post ...] [--offsets 0 1 2]
    python -m schwingcheck rescore --n 1 3 9 --outdir records/exact-rescore

`name` reads one field: a CSV with a column `body` (0, 1, 2 ... in order down the column), one
column per measure in millimetres (a blank where the value was not read) and, optionally, a
column `offset` giving each body's offset from the first (0, 2, 4 for every other body; the
bodies are consecutive without it), and prints the ranked places with their posteriors, the
99 per cent set and whether the top place reaches 0.99. With no body there is nothing to name
and it says so; with no measure the posterior is the prior and it says that too.

`rescore` draws the archive's 2,000 scoring columns from seed 97, scores every field of the
widths given under the three regimes (both planes, AP, lateral) and writes one InferenceData
per width and regime, with the rates in its attributes, so the record of 2026-10-26 can be
reproduced from this package (tests/test_schwingcheck_record.py holds the rates to it).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

import numpy as np

from . import LEVELS
from . import columns as C
from . import measures as MS
from . import records as REC
from . import rule as R
from . import score as S
from . import table as T

SCORE_SEED = 97
N_SCORE = 2000


def read_field(path: str, measures):
    """X (1, measures, bodies) and the offsets from a field CSV."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(line for line in fh if not line.startswith("#"))]
    if not rows:
        return np.zeros((1, len(measures), 0)), np.zeros(0, int)
    rows.sort(key=lambda r: int(r["body"]))
    offsets = np.array([int(r["offset"]) if r.get("offset") not in (None, "") else int(r["body"]) for r in rows])
    offsets = offsets - offsets[0]
    X = np.full((1, len(measures), len(rows)), np.nan)
    for b, r in enumerate(rows):
        for i, m in enumerate(measures):
            v = r.get(m, "")
            if v not in (None, ""):
                X[0, i, b] = float(v)
    return X, offsets


def cmd_name(args) -> int:
    keys = list(args.measures) if args.measures else list(MS.SPINEPS_7)
    X, offsets = read_field(args.field, keys)
    if X.shape[2] == 0:
        print("nothing to name: the field has no body")
        return 1
    if args.offsets:
        offsets = np.array(args.offsets, int)
    present = [k for i, k in enumerate(keys) if np.isfinite(X[0, i]).any()]
    if not present:
        print("no measure was read on any body: the posterior is the prior, 1/%d at every place" % R.places_of(len(LEVELS), offsets))
        return 1
    ms = MS.select(keys)
    mu, sd = MS.arrays(ms)
    post = R.name(X, offsets, mu, sd, R.SYNTH)["all"][0]
    order = np.argsort(-post)
    size, member = R.credible_sets(post[None, :], 0.99)
    print("field of %d bodies at offsets %s, measures %s" % (X.shape[2], list(map(int, offsets)), ", ".join(present)))
    print("place (level of the first body)  posterior")
    for k in order:
        if post[k] < 1e-6 and k != order[0]:
            continue
        print("  %-5s %.6f%s" % (LEVELS[k], post[k], "  <- named" if k == order[0] else ""))
    inset = [LEVELS[k] for k in range(len(post)) if member[0, k]]
    print("99%% set: {%s} (%d places)" % (", ".join(inset), int(size[0])))
    print("the top place reaches 0.99: %s" % ("yes" if post[order[0]] >= 0.99 else "no"))
    return 0


def cmd_table(args) -> int:
    targets = [(T.LONG_CSV, T.write_long_csv, T.check_long_csv),
               (T.SPECIMENS_CSV, T.write_specimens_csv, T.check_specimens_csv)]
    failed = 0
    for path, write, check in targets:
        name = os.path.relpath(path, T.ROOT)
        if args.what == "write":
            print("wrote %s (%d rows)" % (name, write()))
            continue
        problems = check()
        for p in problems:
            print("  " + p)
        print("%s: %s" % (name, "as written from the provenance" if not problems else "%d differences" % len(problems)))
        failed += bool(problems)
    return 1 if failed else 0


def rescore(widths, n_columns: int = N_SCORE, seed: int = SCORE_SEED, outdir=None, command: str = "",
            regimes=None, chunk_columns: int = 100) -> dict:
    """The archive's scoring run on this package: every field of every width under each regime,
    on the checked table, which since page 892 was read equals the archive's in every value the
    record used, so it reproduces the record of 2026-10-26 to the bit."""
    regimes = MS.REGIMES if regimes is None else regimes
    seven = MS.select(MS.SPINEPS_7)
    ref = MS.reference(seven)
    mu, sd = MS.arrays(seven)
    cols = C.draw_columns(ref, ["typical"], seed, n_columns, [MS.archive_key(m) for m in seven])
    sizes, logw = R.quadrature(R.SYNTH["scale_sd"])
    keep = {name: sorted(MS.SPINEPS_7.index(k) for k in ks) for name, ks in regimes.items()}
    digests = {"panjabi_long.csv": T.sha256(T.LONG_CSV), "provenance.csv": T.sha256(T.PROVENANCE_CSV)}
    out = {}
    for n in widths:
        t0 = time.time()
        offsets = np.arange(n)
        blocks = R.table_blocks(offsets, mu, sd, R.SYNTH, sizes)
        posts = {name: [] for name in keep}
        truths, groups, xs = [], [], []
        for c0 in range(0, n_columns, chunk_columns):
            X, truth, grp = C.fields(cols.values[c0:c0 + chunk_columns], offsets)
            LL = R.loglik(X, offsets, mu, sd, R.SYNTH, sizes=sizes, blocks=blocks)
            for name, idx in keep.items():
                posts[name].append(R.posterior(R.log_evidence(LL, logw, idx)))
            truths.append(truth)
            groups.append(grp + c0)
            xs.append(X)
        truth, group, X = np.concatenate(truths), np.concatenate(groups), np.concatenate(xs)
        out[str(n)] = {"n": n, "places": int(len(LEVELS) - n + 1), "regimes": {}}
        for name, idx in keep.items():
            post = np.concatenate(posts[name])
            rates = S.summary(post, truth, group, n, detail=True)
            rates["measures"] = [MS.SPINEPS_7[i] for i in idx]
            if n in (1, 2, 3, 5, 9):
                rates["claims"] = S.claims(post, truth, n)
            out[str(n)]["regimes"][name] = rates
            if outdir:
                rec = REC.build(post, truth, group, X[:, idx, :], offsets, rates["measures"], LEVELS, rates,
                                command=command, seeds={"score": seed}, synth=R.SYNTH, mu=mu[idx], sd=sd[idx],
                                digests=digests, extra_attrs={"regime": name, "n_columns": n_columns, "width": n})
                REC.write(rec, os.path.join(outdir, "width-%02d-%s.nc" % (n, name)))
        out[str(n)]["seconds"] = round(time.time() - t0, 1)
        print("rescore: n=%d done in %.0f s (both planes %.4f)" % (n, out[str(n)]["seconds"], out[str(n)]["regimes"]["both"]["exact"]), flush=True)
    return out


def cmd_rescore(args) -> int:
    command = "python -m schwingcheck " + " ".join(sys.argv[1:])
    out = rescore(args.n, args.columns, args.seed, args.outdir, command)
    if args.outdir:
        with open(os.path.join(args.outdir, "rates.json"), "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m schwingcheck", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("name", help="name one field from its CSV")
    a.add_argument("field")
    a.add_argument("--measures", nargs="*", help="the measures to use, default the archive's seven")
    a.add_argument("--offsets", nargs="*", type=int, help="the bodies' offsets, default from the CSV or consecutive")
    a.set_defaults(fn=cmd_name)
    b = sub.add_parser("table", help="write or check the long CSV and the specimens CSV")
    b.add_argument("what", choices=["write", "check"])
    b.set_defaults(fn=cmd_table)
    c = sub.add_parser("rescore", help="rescore the archive's columns and write InferenceData records")
    c.add_argument("--n", nargs="+", type=int, default=[1, 3, 9])
    c.add_argument("--columns", type=int, default=N_SCORE)
    c.add_argument("--seed", type=int, default=SCORE_SEED)
    c.add_argument("--outdir", default=None)
    c.set_defaults(fn=cmd_rescore)
    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
