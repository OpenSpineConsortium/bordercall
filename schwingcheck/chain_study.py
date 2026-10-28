"""The chain of levels scored against step d's rule: the first rung of step e's methods (TODO.md,
item P, step e).

    python -m schwingcheck.chain_study run [--columns 100] [--out PATH]    # the record, about 10 minutes
    python -m schwingcheck.chain_study table [--out PATH]                  # its table, as Markdown

Fields are drawn by the chain's own law (chain.draw_fields: each step misses a body with
probability chain.SKIP, one missed at most) from the generator's columns of the three types,
typical, six-lumbar and with a T13, every measure of the pool drawn for the same patients
(curve.draw_pool). Four rules name the middle body of each, on the same fields:

- consecutive: step d's rule, which takes the bodies as consecutive on a typical column;
- gaps: the chain of the typical column alone, its missed bodies summed out;
- chain: the whole chain, its missed bodies and its three types summed out;
- known gaps: the rule told each field's true gaps, on the typical column (TODO.md item 4c).

Each is scored as curve.py scores (curve.rates: the name right, within one level on curve.POSITION's
scale, the answers at 0.99 with their precision, each with its SE clustered by column), at 1, 3
and 5 bodies, on the seven SPINEPS measures and on all 32, and timed per field. The exact answer
at 9 bodies takes about 2.6 s a field on all 32 (chain.py's paths), so 9 is left to the speed of
TODO.md's next rung. The chain's L6 and T13 columns are the generator's construction
(chain.extended_table), so on those columns it is scored against the truth it was built from.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, List

import numpy as np

from . import chain as CH
from . import curve as CV
from . import measures as MS
from . import rule as R
from . import score as S

WIDTHS = (1, 3, 5)
ARMS = ("consecutive", "gaps", "chain", "known gaps")
SEED, EXTRA_SEED, FIELD_SEED, PER_COLUMN = 401, 501, 601, 2
RECORD = os.path.join("archive", "records", "chain-2026-10-28", "chain.json")
NAME_POSITION = np.array([CV.POSITION[n] for n in CH.NAMES])


def name_stats(post: np.ndarray, truth: np.ndarray) -> Dict[str, np.ndarray]:
    """What a posterior over NAMES did on each field, in curve.field_stats' terms."""
    said_at, truth_at = NAME_POSITION[post.argmax(1)], NAME_POSITION[truth]
    size, _ = R.credible_sets(post, CV.CLAIM)
    return {"hit": said_at == truth_at, "within": np.abs(said_at - truth_at) <= 1.0, "top": post.max(1),
            "logp": np.log(np.maximum(post[np.arange(len(truth)), truth], 1e-300)), "size": size.astype(np.int16)}


def chains(n_bodies: int) -> Dict[str, CH.Chain]:
    return {"consecutive": CH.build(("typical",), (1.0,), (1.0,), n_bodies),
            "gaps": CH.build(("typical",), (1.0,), CH.step_law(), n_bodies),
            "chain": CH.build(CH.TYPES, None, CH.step_law(), n_bodies)}


def run(n_columns: int) -> dict:
    pool = MS.pool()
    keys = [m.key for m in pool]
    subsets = {"seven": [keys.index(k) for k in MS.SPINEPS_7], "all": list(range(len(pool)))}
    mu, sd = MS.arrays(pool)
    mu_e, sd_e = CH.extended_table(mu, sd)
    noise, power = MS.errors(pool), MS.powers(pool)
    nodes = R.trapezoid(R.SYNTH["scale_sd"])
    rows: List[dict] = []
    for ti, kind in enumerate(CH.TYPES):
        cols = CV.draw_pool(pool, kind, SEED + ti, EXTRA_SEED + ti, n_columns)
        for B in WIDTHS:
            X, names, offsets, col = CH.draw_fields(cols, CH.step_law(), B, PER_COLUMN, FIELD_SEED + 10 * ti + B)
            t = S.target_offset(B)
            truth = names[:, t]
            for arm in ARMS:
                t0 = time.perf_counter()
                if arm == "known gaps":
                    post = CH.known_pattern_posterior(X, offsets, mu, sd, subsets, noise, power, nodes, t)
                else:
                    ch = chains(B)[arm]
                    pa = CH.paths_of(ch)
                    ev = CH.path_logev(X, pa, ch, mu_e, sd_e, subsets, noise, power, nodes)
                    post = {k: CH.body_posterior(CH.posterior(v, pa.log_prior), pa.names, t) for k, v in ev.items()}
                seconds = (time.perf_counter() - t0) / len(X)
                for k, p in post.items():
                    stats = name_stats(p, truth)
                    stats["floored"] = CV.floored_in(X, subsets[k], power)
                    rows.append({"type": kind, "bodies": B, "arm": arm, "subset": k,
                                 "seconds_per_field_both_subsets": seconds, **CV.rates(stats, col)})
    return {"command": "python -m schwingcheck.chain_study run --columns %d" % n_columns, "columns_per_type": n_columns,
            "fields_per_column": PER_COLUMN, "seeds": [SEED, EXTRA_SEED, FIELD_SEED], "skip": CH.SKIP,
            "max_step": CH.MAX_STEP, "weights": CH.WEIGHTS, "rows": rows}


def table(record: dict) -> str:
    out = ["| column | bodies | measures | " + " | ".join(ARMS) + " |", "|---|---|---|" + "---|" * len(ARMS)]
    key = {(r["type"], r["bodies"], r["subset"], r["arm"]): r for r in record["rows"]}
    for kind in CH.TYPES:
        for B in WIDTHS:
            for k in ("seven", "all"):
                cells = ["%.1f (%.1f)" % (100 * key[kind, B, k, a]["exact"], 100 * key[kind, B, k, a]["exact_se"]) for a in ARMS]
                out.append("| %s | %d | %s | %s |" % (kind, B, k, " | ".join(cells)))
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m schwingcheck.chain_study")
    ap.add_argument("what", choices=("run", "table"))
    ap.add_argument("--columns", type=int, default=100)
    ap.add_argument("--out", default=RECORD)
    a = ap.parse_args(argv)
    if a.what == "run":
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        rec = run(a.columns)
        tmp = a.out + ".tmp"
        with open(tmp, "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        os.replace(tmp, a.out)
    else:
        with open(a.out) as f:
            print(table(json.load(f)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
