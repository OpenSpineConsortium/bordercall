"""What a combination variable is in PyMC, shown on the exact rule written as a PyMC model.

The model is the archive's rule for one field (archive/bordercall/exact.py): the size s is the
one continuous variable, log s normal with SD 0.07; the place k is marginalised in the
likelihood, the field's density at every place summed by a logsumexp under a uniform prior
(pm.Potential), so NUTS samples s alone and no discrete variable is ever sampled (no Metropolis
step). The posterior over places is a pm.Deterministic, softmax of the places' log densities,
and its mean over the draws of s is p(k | x), since p(k | x) is the average over p(s | x) of
p(k | x, s).

Three things are checked, and pymc_check.json records them:

1. The model is the rule: the mean over NUTS draws of the posterior over places equals the
   exact enumeration to within three of the draws' own Monte Carlo standard errors (ArviZ's,
   from the effective sample size), with the chains' divergences, R-hat and effective sample
   size recorded beside it.
2. A combination variable written as pm.Deterministic (here the end-plate aspect, the canal to
   body ratio and a body-size product, of the data and of the latent size) adds no term to the
   joint log density: the compiled log density is the same, to the last bit, at every value of
   log s tried. So it cannot change the posterior over places, which is the whole of its power
   in a model that already holds the measures.
3. The same combination given a likelihood of its own and observed beside the measures counts
   the same data twice: the posterior over places moves, and on many fields the rule becomes
   overconfident (study.py's "double counted" rule measures by how much).
"""
from __future__ import annotations

import json
import math
import os
import time
from typing import Dict, Optional, Sequence

import numpy as np

from .study import EX, L, NB, P, SEVEN, IDX


def field_model(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, synth: dict, combos: bool = False,
                observed_aspect: bool = False):
    import pymc as pm
    import pytensor.tensor as pt
    nm, n = X.shape
    K = L - n + 1
    MW = np.stack([mu[:, k:k + n] for k in range(K)])          # (K, nm, n)
    SW = np.stack([sd[:, k:k + n] for k in range(K)])
    rho, noise = synth["rho"], synth["noise_mm"]
    with pm.Model() as model:
        log_s = pm.Normal("log_s", 0.0, synth["scale_sd"])
        s = pt.exp(log_s)
        delta = s * s * (1.0 - rho * rho) * SW * SW + noise * noise
        d = 1.0 / delta
        u = s * rho * SW
        r = X[None] - s * MW
        a = (u * u * d).sum(-1)
        quad = (r * r * d).sum(-1) - (r * u * d).sum(-1) ** 2 / (1.0 + a)
        logdet = pt.log(delta).sum(-1) + pt.log1p(a)
        lp = (-0.5 * (quad + logdet + n * EX.LOG2PI)).sum(-1)    # (K,)
        if observed_aspect:
            lp = lp + aspect_loglik(X, mu, sd, synth)
        pm.Potential("field", pm.math.logsumexp(lp) - math.log(K))
        pm.Deterministic("p_place", pt.exp(lp - pm.math.logsumexp(lp)))
        if combos:
            pm.Deterministic("aspect", pt.as_tensor(X[IDX["endplate"]] / X[IDX["endplate_depth"]]))
            pm.Deterministic("canal_to_body", pt.as_tensor(X[IDX["canal_w"]] / X[IDX["endplate"]]))
            pm.Deterministic("expected_body_size", s ** 3 * (MW[:, IDX["endplate"]] * MW[:, IDX["endplate_depth"]]
                                                              * MW[:, IDX["h_post"]]))
    return model


def aspect_loglik(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, synth: dict) -> np.ndarray:
    """The log-normal log density of the field's end-plate aspects at every place: the ratio
    given a likelihood of its own (study.formula_posterior's moments)."""
    from .study import ratio
    n = X.shape[1]
    A = ratio(n, "endplate", "endplate_depth")
    z = A @ np.log(X).reshape(-1)
    out = []
    for k in range(L - n + 1):
        mean, cov = EX.log_moments(mu, sd, k, n, synth)
        Lc = np.linalg.cholesky(A @ cov @ A.T)
        w = np.linalg.solve(Lc, z - A @ mean)
        out.append(-0.5 * (w @ w + 2.0 * np.log(np.diag(Lc)).sum() + len(z) * EX.LOG2PI))
    return np.array(out)


def exact_posterior(X: np.ndarray, mu: np.ndarray, sd: np.ndarray, synth: dict) -> np.ndarray:
    sizes, logw = EX.trapezoid(synth["scale_sd"])
    return EX.posterior(EX.evidence_lean(X[None], mu, sd, synth, sizes, logw))[0]


def logp_same(X, mu, sd, synth, points=(-0.2, -0.07, 0.0, 0.05, 0.21)) -> float:
    """The largest difference between the compiled log densities of the model with and without
    the Deterministic combinations, over values of log s."""
    f0 = field_model(X, mu, sd, synth).compile_logp()
    f1 = field_model(X, mu, sd, synth, combos=True).compile_logp()
    return float(max(abs(f0({"log_s": v}) - f1({"log_s": v})) for v in points))


def check(n_fields: int = 2, n: int = 3, draws: int = 1000, chains: int = 4, seed: int = 7) -> dict:
    import arviz as az
    import pymc as pm
    ref = P.load_reference(P.DEFAULT_REFERENCE, SEVEN)
    mu, sd = EX.table_arrays(ref, SEVEN)
    synth = dict(NB.SYNTH)
    V = EX.column_values(NB.draw_columns(ref, ["typical"], seed, n_fields, SEVEN), SEVEN)
    rng = np.random.default_rng(seed)
    out = {"n": n, "draws": draws, "chains": chains, "fields": []}
    for c in range(n_fields):
        k_true = int(rng.integers(0, L - n + 1))
        X = V[c, :, k_true:k_true + n]
        exact = exact_posterior(X, mu, sd, synth)
        t0 = time.time()
        with field_model(X, mu, sd, synth, combos=True):
            idata = pm.sample(draws=draws, chains=chains, cores=1, random_seed=seed + c, progressbar=False,
                              compute_convergence_checks=False)
        p = idata.posterior["p_place"].values.reshape(-1, L - n + 1)
        # the Monte Carlo standard error of each place's mean from the draws' effective sample
        # size (ArviZ), and three of them as the bound, with a floor for places of no mass
        mcse = np.asarray(az.mcse(idata, var_names=["p_place"])["p_place"].values)
        bound = np.maximum(3.0 * mcse, 2e-3)
        with field_model(X, mu, sd, synth, observed_aspect=True):
            idata2 = pm.sample(draws=draws, chains=chains, cores=1, random_seed=seed + c, progressbar=False,
                               compute_convergence_checks=False)
        p2 = idata2.posterior["p_place"].values.reshape(-1, L - n + 1).mean(0)
        out["fields"].append({
            "true_place": EX.LEVELS[k_true], "seconds": round(time.time() - t0, 1),
            "divergences": int(idata.sample_stats["diverging"].values.sum()),
            "r_hat_log_s": round(float(az.rhat(idata, var_names=["log_s"])["log_s"].values), 4),
            "ess_log_s": round(float(az.ess(idata, var_names=["log_s"])["log_s"].values), 1),
            "max_abs_difference_from_exact": float(np.abs(p.mean(0) - exact).max()),
            "largest_mcse": float(mcse.max()),
            "within_monte_carlo_error": bool(np.all(np.abs(p.mean(0) - exact) <= bound)),
            "exact_top": [EX.LEVELS[int(np.argmax(exact))], round(float(exact.max()), 4)],
            "pymc_top": [EX.LEVELS[int(np.argmax(p.mean(0)))], round(float(p.mean(0).max()), 4)],
            "double_counted_top": [EX.LEVELS[int(np.argmax(p2))], round(float(p2.max()), 4)],
            "deterministic_logp_difference": logp_same(X, mu, sd, synth)})
    return out


def write(outdir: str, record: dict) -> None:
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "pymc_check.json"), "w", newline="\n") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
        fh.write("\n")
