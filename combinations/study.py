"""How much a combination variable adds to naming: measured, world by world.

    python -m combinations study --outdir combinations/records/combinations-2026-10-27
    python -m combinations pymc-check --outdir combinations/records/combinations-2026-10-27

The owner's queue of 27 October 2026, 09:44 UTC, item 6, second line: "evaluate for the power of
combination variables native to pymc". A combination variable is a quantity made from the
measures: a ratio (end-plate width over depth, canal over body, height over width), a product
(a body's size, width times depth times height), a difference between neighbours. In PyMC it is
written with pm.Deterministic, a named function of the model's variables that adds no term to
the joint density, or it is given a likelihood of its own and observed.

WHAT FOLLOWS BY CONSTRUCTION. A combination variable is a function of the measures, so a rule
that sees it and the measures sees no more than a rule that sees the measures (the data
processing inequality). The exact rule is the Bayes rule on the measures (archive/bordercall/
exact.py), so under the generator no combination variable can raise its accuracy, and a
pm.Deterministic, which changes no density, cannot change its posterior at all (pymc_check.py
shows both numerically). Two questions are left, and this file measures them:

1. Standalone power: a rule that sees only some combinations, and not the measures, loses what
   the combinations leave out. How much does each family keep? Every combination here is a
   linear combination of the log measures, so under the archive's log-normal approximation
   (exact.log_moments, the `formula` rule) a set of them, the rows of a matrix A, has mean A m_k
   and covariance A S_k A' at each place k, and the Bayes rule on them alone is one quadratic
   discriminant per place, in closed form, nothing fitted. The same rule with A the identity is
   the archive's formula rule, so each family is read against it and against the exact rule.
2. Robustness: the size enters every log measure as the same added constant, so a ratio, any
   row of A whose entries sum to zero, does not see it. Where the scale is wrong, a film whose
   magnification is not the one assumed, the ratios keep what the raw measures lose. The exact
   rule's own scale-free form, the size integrated under a flat prior on log s (the Bayes rule on
   every ratio at once, scanimport/bridge.py's unknown scale), is measured beside it.

THE WORLDS, each on the same 400 typical columns drawn at the archive's score seed:
- nominal: the generator is the truth and every rule assumes it;
- film: each column magnified by m, log m normal about log 1.15 with SD 0.08, and the rules told
  exactly that (m0 1.15, the spread added to the size's): correctly specified, only wider;
- film, magnification wrong: every column magnified by 1.35 while the rules assume 1.15 with SD
  0.08, two of their SDs off, as a C-arm's unrecorded geometry can be;
- pixels: each column in an arbitrary unit (multiplied by a factor between 3 and 12), where only
  scale-free rules can run.

Every number is about synthetic columns drawn from Panjabi's tables; nothing here is a patient.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "archive", "bordercall"))
import exact as EX                                                   # noqa: E402
import neighbour as NB                                               # noqa: E402
import panjabi as P                                                  # noqa: E402

SEVEN = ["endplate", "endplate_depth", "endplate_lower", "endplate_lower_depth", "h_post", "canal_w", "canal_ap"]
assert SEVEN == list(EX.MEASURES7)
L = len(EX.LEVELS)
WIDTHS = (1, 3, 5, 9)
N_COLUMNS = 400
WORLD_SEED = 20261027
M0, M_SD, M_WRONG = 1.15, 0.08, 1.35
FLAT_HALF_WIDTH, FLAT_NODES = 2.5, 2501
CHUNK = 400
IDX = {m: i for i, m in enumerate(SEVEN)}
DOUBLE = "exact rule with the aspect observed again (counted twice)"


# ---- the combination families, as rows over the field's log values (measure-major, m * n + i) ----

def row(nm: int, n: int, terms: Sequence[Tuple[str, int, float]]) -> np.ndarray:
    r = np.zeros(nm * n)
    for m, i, w in terms:
        r[IDX[m] * n + i] += w
    return r


def ratio(n: int, top: str, bottom: str) -> np.ndarray:
    return np.array([row(len(SEVEN), n, [(top, i, 1.0), (bottom, i, -1.0)]) for i in range(n)])


def contrasts(N: int) -> np.ndarray:
    """An orthonormal basis of every direction whose entries sum to zero: all ratios at once."""
    q, _ = np.linalg.qr(np.eye(N) - 1.0 / N)
    return q[:, :N - 1].T


def families(n: int) -> Dict[str, np.ndarray]:
    nm = len(SEVEN)
    fam = {
        "raw measures (the formula rule)": np.eye(nm * n),
        "every ratio (all scale-free contrasts)": contrasts(nm * n),
        "every within-body ratio": np.vstack([np.array([row(nm, n, [(m, i, 1.0), ("endplate", i, -1.0)])
                                                        for m in SEVEN[1:]]) for i in range(n)]),
        "aspect: EPWu / EPDu": ratio(n, "endplate", "endplate_depth"),
        "canal to body: SCW / EPWu and SCD / EPDu": np.vstack([ratio(n, "canal_w", "endplate"),
                                                              ratio(n, "canal_ap", "endplate_depth")]),
        "height to width: VBHp / EPWu": ratio(n, "h_post", "endplate"),
        "body size: EPWu x EPDu x VBHp": np.array([row(nm, n, [("endplate", i, 1.0), ("endplate_depth", i, 1.0),
                                                                ("h_post", i, 1.0)]) for i in range(n)]),
    }
    if n > 1:
        fam["neighbour ratios: each measure over the body above"] = np.array(
            [row(nm, n, [(m, i + 1, 1.0), (m, i, -1.0)]) for m in SEVEN for i in range(n - 1)])
    return fam


def is_scale_free(A: np.ndarray) -> bool:
    return bool(np.allclose(A.sum(1), 0.0))


# ---- the rules ------------------------------------------------------------------------------------

def formula_loglik(Y: np.ndarray, A: np.ndarray, mu: np.ndarray, sd: np.ndarray, n: int, synth: dict,
                   log_shift: float = 0.0) -> np.ndarray:
    """The log density of the combinations A y alone at every place under the log-normal
    approximation: one quadratic discriminant per place. Y is (fields, N) log values; log_shift
    is what the rule takes off every log value (log m0)."""
    Z = (Y - log_shift) @ A.T
    out = np.empty((len(Y), L - n + 1))
    for k in range(L - n + 1):
        mean, cov = EX.log_moments(mu, sd, k, n, synth)
        Lc = np.linalg.cholesky(A @ cov @ A.T)
        W = np.linalg.solve(Lc, (Z - A @ mean).T)
        out[:, k] = -0.5 * ((W * W).sum(0) + 2.0 * np.log(np.diag(Lc)).sum() + len(A) * EX.LOG2PI)
    return out


def formula_posterior(Y, A, mu, sd, n, synth, log_shift=0.0) -> np.ndarray:
    return EX.posterior(formula_loglik(Y, A, mu, sd, n, synth, log_shift))


def exact_logev(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, synth: dict, log_mean: float = 0.0,
                extra_sd: float = 0.0) -> np.ndarray:
    """The exact rule's log evidence on the raw measures, the size's spread widened by the
    study's own: (fields, places)."""
    sizes, logw = EX.trapezoid(math.sqrt(synth["scale_sd"] ** 2 + extra_sd ** 2))
    sizes = sizes * math.exp(log_mean)
    return np.concatenate([EX.evidence_lean(X[a:a + CHUNK], mu, sd, synth, sizes, logw) for a in range(0, len(X), CHUNK)])


def invariant_loglik(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, start: int, sizes: np.ndarray,
                     rho: float, noise_mm: float) -> np.ndarray:
    """exact.place_loglik with the measurement error carried by the size, as it is when the unit
    is unknown: (fields, measures, nodes)."""
    nf, nm, n = X.shape
    out = np.empty((nf, nm, len(sizes)))
    s = sizes[:, None]
    for m in range(nm):
        mw, sw = mu[m, start:start + n], sd[m, start:start + n]
        delta = s * s * ((1.0 - rho * rho) * sw * sw + noise_mm * noise_mm)
        d = 1.0 / delta
        u = s * rho * sw
        a = (u * u * d).sum(1)
        x = X[:, m, :]
        q1 = (x * x) @ d.T - 2.0 * x @ (s * mw * d).T + (s * s * mw * mw * d).sum(1)
        q2 = x @ (u * d).T - (s * mw * u * d).sum(1)
        out[:, m, :] = -0.5 * (q1 - q2 * q2 / (1.0 + a) + np.log(delta).sum(1) + np.log1p(a) + n * EX.LOG2PI)
    return out


def invariant_posterior(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, synth: dict) -> np.ndarray:
    """The exact rule with the size under a flat prior on log s: each field divided first by its
    own size estimate (the rule is equivariant, so this changes nothing but where the window
    sits), then integrated over one window shared by every place."""
    n = X.shape[2]
    centre = np.median(np.log(X).reshape(len(X), -1), axis=1) - np.median(np.log(mu))
    Xn = X / np.exp(centre)[:, None, None]
    t = np.linspace(-FLAT_HALF_WIDTH, FLAT_HALF_WIDTH, FLAT_NODES)
    logw = np.full(len(t), math.log((t[1] - t[0]) / (2.0 * FLAT_HALF_WIDTH)))
    logw[[0, -1]] += math.log(0.5)
    sizes = np.exp(t)
    out = []
    for a in range(0, len(Xn), CHUNK):
        part = Xn[a:a + CHUNK]
        out.append(np.stack([EX.logsumexp(invariant_loglik(part, mu, sd, k, sizes, synth["rho"], synth["noise_mm"])
                                          .sum(1) + logw, axis=1) for k in range(L - n + 1)], axis=1))
    return EX.posterior(np.concatenate(out))


# ---- the worlds -------------------------------------------------------------------------------------

def worlds(V: np.ndarray, seed: int = WORLD_SEED) -> Dict[str, dict]:
    """Each world's columns and what the rules are told about the scale."""
    rng = np.random.default_rng(seed)
    m_film = np.exp(rng.normal(math.log(M0), M_SD, len(V)))
    unit = rng.uniform(3.0, 12.0, len(V))
    return {
        "nominal": {"V": V, "log_mean": 0.0, "extra_sd": 0.0, "known": True},
        "film": {"V": V * m_film[:, None, None], "log_mean": math.log(M0), "extra_sd": M_SD, "known": True},
        "film, magnification wrong": {"V": V * M_WRONG, "log_mean": math.log(M0), "extra_sd": M_SD, "known": True},
        "pixels": {"V": V * unit[:, None, None], "log_mean": None, "extra_sd": None, "known": False},
    }


def brief(post: np.ndarray, truth: np.ndarray, group: np.ndarray, n: int) -> dict:
    s = EX.summary(post, truth, group, n, detail=False)
    sel = s["selective"]["0.99"]
    return {"exact": round(s["exact"], 4), "se": round(s["se_cluster"], 4), "within_one": round(s["within_one"], 4),
            "answered_099": round(sel["answered"], 4),
            "precision_099": None if math.isnan(sel["precision"]) else round(sel["precision"], 4),
            "log_loss": round(s["log_loss"], 4), "n_fields": s["n_fields"]}


def run(n_columns: int = N_COLUMNS, widths: Sequence[int] = WIDTHS, log=print) -> dict:
    ref = P.load_reference(P.DEFAULT_REFERENCE, SEVEN)
    mu, sd = EX.table_arrays(ref, SEVEN)
    synth = dict(NB.SYNTH)
    V0 = EX.column_values(NB.draw_columns(ref, ["typical"], NB.SCORE_SEED, n_columns, SEVEN), SEVEN)
    out = {"columns": n_columns, "seed": NB.SCORE_SEED, "world_seed": WORLD_SEED, "synth": synth,
           "measures": SEVEN, "widths": list(widths), "worlds": {}}
    for wname, w in worlds(V0).items():
        out["worlds"][wname] = {}
        for n in widths:
            X, truth, group = EX.fields(w["V"], n)
            Y = np.log(X.reshape(len(X), -1))
            rules = {}
            t0 = time.time()
            rsynth = dict(synth, scale_sd=math.sqrt(synth["scale_sd"] ** 2 + (w["extra_sd"] or 0.0) ** 2))
            if w["known"]:
                ev = exact_logev(X, mu, sd, synth, w["log_mean"], w["extra_sd"])
                rules["exact rule, raw measures"] = brief(EX.posterior(ev), truth, group, n)
                twice = ev + formula_loglik(Y, ratio(n, "endplate", "endplate_depth"), mu, sd, n, rsynth, w["log_mean"])
                rules[DOUBLE] = brief(EX.posterior(twice), truth, group, n)
            rules["exact rule, scale-free (every ratio)"] = brief(invariant_posterior(X, mu, sd, synth), truth, group, n)
            for fname, A in families(n).items():
                if not w["known"] and not is_scale_free(A):
                    continue
                rules[fname] = brief(formula_posterior(Y, A, mu, sd, n, rsynth, w["log_mean"] or 0.0), truth, group, n)
            out["worlds"][wname][str(n)] = rules
            log("%-26s n=%d  %d rules  %.1fs" % (wname, n, len(rules), time.time() - t0))
    return out


def table(record: dict) -> str:
    """The record as one Markdown table per world: exact rate, and precision and share answered
    at posterior 0.99, by width."""
    lines = []
    for wname, by_n in record["worlds"].items():
        widths = list(by_n)
        lines += ["", "**%s**" % wname, "",
                  "| Rule | " + " | ".join("n = %s" % n for n in widths) + " |",
                  "| --- |" + " --- |" * len(widths)]
        names = []
        for n in widths:
            names += [r for r in by_n[n] if r not in names]
        for rule in names:
            cells = []
            for n in widths:
                r = by_n[n].get(rule)
                if r is None:
                    cells.append("")
                else:
                    p = "-" if r["precision_099"] is None else "%.3f" % r["precision_099"]
                    cells.append("%.3f (%.2f at %s)" % (r["exact"], r["answered_099"], p))
            lines.append("| %s | %s |" % (rule, " | ".join(cells)))
    return "\n".join(lines)


def write(outdir: str, record: dict) -> None:
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "combinations.json"), "w", newline="\n") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
        fh.write("\n")
    with open(os.path.join(outdir, "TABLE.md"), "w", newline="\n") as fh:
        fh.write("Exact rate, then in brackets the share answered at posterior 0.99 and the precision there.\n")
        fh.write(table(record) + "\n")
