"""The command line of the package.

    python -m schwingcheck table write                 # the long CSV and the specimens from the provenance record
    python -m schwingcheck table check                 # the committed CSVs are what write would write
    python -m schwingcheck name FIELD.csv [--measures endplate h_post ...] [--offsets 0 1 2] [--engine nuts]
    python -m schwingcheck rescore --n 1 3 9 --outdir records/exact-rescore [--engine pytensor|pymc]
    python -m schwingcheck graph write                 # the three PyMC models' graphs, graphs/*.mmd
    python -m schwingcheck graph check                 # the committed graphs are what write would write

`name` reads one field: a CSV with a column `body` (0, 1, 2 ... in order down the column), one
column per measure in millimetres (a blank where the value was not read) and, optionally, a
column `offset` giving each body's offset from the first (0, 2, 4 for every other body; the
bodies are consecutive without it, whatever their numbers), and prints the ranked places with
their posteriors, the 99 per cent set and whether the top place reaches 0.99. --offsets gives
the offsets on the command line instead, one per body, counted from the first as the column's
are. With no body there is nothing to name and it says so; with no measure the posterior is the
prior and it says that too; offsets for some bodies and not others, a number of them other than
the bodies', or offsets that do not rise down the column are refused. The engine is numpy
(rule.py, the reference), pytensor (compiled.py, the same rule as one compiled function) or nuts
(model.py's naming model: the place summed out, the size sampled by NUTS, the posterior averaged
over the draws), which also prints each place's Monte Carlo error.

`rescore` draws the archive's 2,000 scoring columns from seed 97, scores every field of the
widths given under the three regimes (both planes, AP, lateral) and writes one InferenceData
per width and regime, with the rates in its attributes, so the record of 2026-10-26 can be
reproduced from this package (tests/test_schwingcheck_record.py holds the rates to it), with
either engine of the exact rule or with pymc, the naming model integrated over the size on the
same nodes from its own graph.

`graph` writes or checks graphs/*.mmd, the three PyMC models' graphs as Mermaid text, which the
README draws.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
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
    """X (1, measures, bodies) and the offsets from a field CSV: the column `offset` where every
    body has one, 0, 1, 2 ... where none has, refused where some have and some do not."""
    with open(path, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(line for line in fh if not line.startswith("#"))]
    if not rows:
        return np.zeros((1, len(measures), 0)), np.zeros(0, int)
    rows.sort(key=lambda r: int(r["body"]))
    given = [r.get("offset") not in (None, "") for r in rows]
    if all(given):
        offsets = np.array([int(r["offset"]) for r in rows])
    elif not any(given):
        offsets = np.arange(len(rows))
    else:
        raise ValueError("the field gives an offset for %d of its %d bodies" % (sum(given), len(rows)))
    X = np.full((1, len(measures), len(rows)), np.nan)
    for b, r in enumerate(rows):
        for i, m in enumerate(measures):
            v = r.get(m, "")
            if v not in (None, ""):
                X[0, i, b] = float(v)
    return X, offsets


def counted_from_first(offsets, n_bodies: int) -> np.ndarray:
    """One offset per body, rising down the column, counted from the first body."""
    offsets = np.asarray(offsets, int)
    if len(offsets) != n_bodies:
        raise ValueError("%d offsets for a field of %d bodies" % (len(offsets), n_bodies))
    if np.any(np.diff(offsets) <= 0):
        raise ValueError("the offsets %s do not rise down the column" % list(map(int, offsets)))
    return offsets - offsets[0] if len(offsets) else offsets


def cmd_name(args) -> int:
    keys = list(args.measures) if args.measures else list(MS.SPINEPS_7)
    try:
        X, offsets = read_field(args.field, keys)
        if X.shape[2] and args.offsets:
            offsets = args.offsets
        offsets = counted_from_first(offsets, X.shape[2])
    except ValueError as err:
        print("refused: %s" % err)
        return 2
    if X.shape[2] == 0:
        print("nothing to name: the field has no body")
        return 1
    present = [k for i, k in enumerate(keys) if np.isfinite(X[0, i]).any()]
    if not present:
        print("no measure was read on any body: the posterior is the prior, 1/%d at every place" % R.places_of(len(LEVELS), offsets))
        return 1
    ms = MS.select(keys)
    post, se = name_with(args, X, offsets, ms)
    order = np.argsort(-post)
    size, member = R.credible_sets(post[None, :], 0.99)
    print("field of %d bodies at offsets %s, measures %s" % (X.shape[2], list(map(int, offsets)), ", ".join(present)))
    print("place (level of the first body)  posterior")
    for k in order:
        if post[k] < 1e-6 and k != order[0]:
            continue
        err = "" if se is None else " +- %.4f" % se[k]
        print("  %-5s %.6f%s%s" % (LEVELS[k], post[k], err, "  <- named" if k == order[0] else ""))
    inset = [LEVELS[k] for k in range(len(post)) if member[0, k]]
    print("99%% set: {%s} (%d places)" % (", ".join(inset), int(size[0])))
    print("the top place reaches 0.99: %s" % ("yes" if post[order[0]] >= 0.99 else "no"))
    return 0


def name_with(args, X, offsets, ms):
    """One field's posterior over places by the engine asked for, and its Monte Carlo error
    where the engine samples (None where it computes exactly)."""
    if args.engine == "numpy":
        return MS.name(X, offsets, ms)["all"][0], None
    from . import compiled as K
    mu, sd = MS.arrays(ms)
    noise = MS.errors(ms)
    if args.engine == "pytensor":
        return K.ExactRule(mu, sd, noise=noise).name(X, offsets)["all"][0], None
    from . import model as MD
    m = MD.naming(X, K.hypotheses(len(LEVELS), [offsets]), mu, sd, [x.key for x in ms], noise=noise)
    idata = MD.sample(m, draws=args.draws, chains=args.chains, seed=args.seed)
    post, se = MD.hypothesis_posterior(m, idata)
    return post[0], se[0]


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
        print("%s: %s" % (name, "as written from the provenance" if not problems else "differs, as above"))
        failed += bool(problems)
    return 1 if failed else 0


def rescore(widths, n_columns: int = N_SCORE, seed: int = SCORE_SEED, outdir=None, command: str = "",
            regimes=None, chunk_columns: int = 100, engine: str = "numpy") -> dict:
    """The archive's scoring run on this package: every field of every width under each regime,
    on the checked table, which since page 892 was read equals the archive's in every value the
    record used, so it reproduces the record of 2026-10-26: every rate to within 1e-12 (rounding
    in a different order of sums) and the share named exactly identically. Each measure's error is
    its own, 1 mm for all seven as in the archive. The engine is numpy (rule.py), pytensor
    (compiled.py), which gives the same posteriors to within 1e-10, or pymc, model.py's naming
    model over each regime's measures integrated over log s on rule.py's nodes from its own graph
    (quadrature_evidence), one model per width and regime."""
    if engine not in ("numpy", "pytensor", "pymc"):
        raise ValueError("the engine is numpy, pytensor or pymc, not %r" % (engine,))
    regimes = MS.REGIMES if regimes is None else regimes
    seven = MS.select(MS.SPINEPS_7)
    ref = MS.reference(seven)
    mu, sd = MS.arrays(seven)
    noise = MS.errors(seven)
    cols = C.draw_columns(ref, ["typical"], seed, n_columns, [MS.archive_key(m) for m in seven])
    sizes, logw = R.quadrature(R.SYNTH["scale_sd"])
    keep = {name: sorted(MS.SPINEPS_7.index(k) for k in ks) for name, ks in regimes.items()}
    digests = {"panjabi_long.csv": T.sha256(T.LONG_CSV), "provenance.csv": T.sha256(T.PROVENANCE_CSV)}
    if engine in ("pytensor", "pymc"):
        from . import compiled as K
    if engine == "pytensor":
        exact = K.ExactRule(mu, sd, noise=noise)
    if engine == "pymc":
        from . import model as MD
        chunk_columns = n_columns           # one model per width and regime: a build per chunk costs more than it saves
    out = {}
    for n in widths:
        t0 = time.time()
        offsets = np.arange(n)
        if engine == "numpy":
            blocks = R.table_blocks(offsets, mu, sd, R.SYNTH, sizes, noise)
        else:
            hyp = K.hypotheses(len(LEVELS), [offsets])
        posts = {name: [] for name in keep}
        truths, groups, xs = [], [], []
        for c0 in range(0, n_columns, chunk_columns):
            X, truth, grp = C.fields(cols.values[c0:c0 + chunk_columns], offsets)
            if engine == "numpy":
                LL = R.loglik(X, offsets, mu, sd, R.SYNTH, sizes=sizes, blocks=blocks)
                for name, idx in keep.items():
                    posts[name].append(R.posterior(R.log_evidence(LL, logw, idx)))
            elif engine == "pytensor":
                for name, res in exact.evaluate(X, hyp, subsets=keep).items():
                    posts[name].append(res["post"])
            else:
                for name, idx in keep.items():
                    m = MD.naming(X[:, idx, :], hyp, mu[idx], sd[idx], [MS.SPINEPS_7[i] for i in idx], noise=noise[idx])
                    posts[name].append(R.posterior(MD.quadrature_evidence(m)))
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
                                noise=noise[idx], digests=digests,
                                extra_attrs={"regime": name, "n_columns": n_columns, "width": n, "engine": engine})
                REC.write(rec, os.path.join(outdir, "width-%02d-%s.nc" % (n, name)))
        out[str(n)]["seconds"] = round(time.time() - t0, 1)
        print("rescore (%s): n=%d done in %.0f s (both planes %.4f)" % (engine, n, out[str(n)]["seconds"],
                                                                     out[str(n)]["regimes"]["both"]["exact"]), flush=True)
    return out


def cmd_rescore(args) -> int:
    command = "python -m schwingcheck " + shlex.join(args.argv)
    out = rescore(args.n, args.columns, args.seed, args.outdir, command, engine=args.engine)
    if args.outdir:
        with open(os.path.join(args.outdir, "rates.json"), "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
    return 0


def cmd_graph(args) -> int:
    from . import model as MD
    if args.what == "write":
        for path in MD.write_graphs():
            print("wrote %s" % os.path.relpath(path, T.ROOT))
        return 0
    stale = MD.check_graphs()
    for name in stale:
        print("  graphs/%s.mmd differs from the model" % name)
    print("graphs: %s" % ("as the models draw them" if not stale else "%d stale" % len(stale)))
    return 1 if stale else 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m schwingcheck", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("name", help="name one field from its CSV")
    a.add_argument("field")
    a.add_argument("--measures", nargs="*", help="the measures to use, default the archive's seven")
    a.add_argument("--offsets", nargs="*", type=int, help="the bodies' offsets, default from the CSV or consecutive")
    a.add_argument("--engine", choices=["numpy", "pytensor", "nuts"], default="numpy")
    a.add_argument("--draws", type=int, default=2000, help="NUTS draws per chain (engine nuts)")
    a.add_argument("--chains", type=int, default=4, help="NUTS chains (engine nuts)")
    a.add_argument("--seed", type=int, default=0, help="NUTS seed (engine nuts)")
    a.set_defaults(fn=cmd_name)
    b = sub.add_parser("table", help="write or check the long CSV and the specimens CSV")
    b.add_argument("what", choices=["write", "check"])
    b.set_defaults(fn=cmd_table)
    c = sub.add_parser("rescore", help="rescore the archive's columns and write InferenceData records")
    c.add_argument("--n", nargs="+", type=int, default=[1, 3, 9])
    c.add_argument("--columns", type=int, default=N_SCORE)
    c.add_argument("--seed", type=int, default=SCORE_SEED)
    c.add_argument("--outdir", default=None)
    c.add_argument("--engine", choices=["numpy", "pytensor", "pymc"], default="numpy")
    c.set_defaults(fn=cmd_rescore)
    g = sub.add_parser("graph", help="write or check the PyMC models' graphs")
    g.add_argument("what", choices=["write", "check"])
    g.set_defaults(fn=cmd_graph)
    # the arguments parsed, which the records carry as their command, whether they came from
    # the shell or from a caller of main
    argv = sys.argv[1:] if argv is None else [str(a) for a in argv]
    args = p.parse_args(argv)
    args.argv = argv
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
