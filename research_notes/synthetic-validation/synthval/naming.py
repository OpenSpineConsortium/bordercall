"""How well the rule names fields drawn at one point of the state space.

The build-up study scored the rule on the generator's own columns, the truth the rule assumes.
Here the columns come from population.draw at any setting, and the rule is built either on the
generator's settings ("generator") or on the setting the columns were drawn at ("matched"), where
the rule can hold it: the size's spread, rho, the error scale, the loadings on size, the SDs'
scale and, for sd_mode "size_removed", the table it draws from. Two settings no rule here can hold, phi (an AR(1) chain of a person's offsets
down the column) and r_between (offsets correlated between measures), are scored with the
generator's rule, which is how a rule built on the generator meets a population that differs from
it. Every field is scored with rule.py on the Gauss-Hermite nodes, the reference.
"""
from __future__ import annotations

from typing import Dict, Sequence

import numpy as np

from schwingcheck import LEVELS
from schwingcheck import columns as C
from schwingcheck import measures as MS
from schwingcheck import rule as R
from schwingcheck import score as S

from .population import GENERATOR, Population, Settings, calibrated

CLAIM = 0.99
CHUNK = 250


def rule_for(measures: Sequence[MS.Measure], settings: Settings):
    """The table, synth settings, errors and powers of a rule built on these settings."""
    mu, sd = MS.arrays(list(measures), LEVELS)
    power = MS.powers(list(measures)) * np.array([settings.loading(m.key) for m in measures])
    mu, sd, _ = calibrated(mu, sd * settings.sd_scale, power, settings)
    synth = {"rho": settings.rho, "noise_mm": 1.0, "scale_sd": settings.scale_sd}
    return mu, sd, synth, MS.errors(list(measures)) * settings.error_scale, power


def score(pop: Population, measures: Sequence[MS.Measure], width: int, rule_settings: Settings = GENERATOR,
          table=None) -> Dict[str, float]:
    """The share named exactly, within one level, answered at 0.99 and right there, on every
    contiguous field of `width` bodies of every person's column (typical columns only), with the
    standard errors clustered by column. `table`, a (mu, sd) pair, replaces the rule's table, as a
    table taken from another population would (power.py)."""
    if pop.phenotype != "typical":
        raise ValueError("naming is scored here on typical columns only")
    keys = [MS.archive_key(m) for m in measures]
    idx = [pop.keys.index(k) for k in keys]
    X, truth, group = C.fields(pop.measured[:, :, idx], list(range(width)))
    mu, sd, synth, noise, power = rule_for(measures, rule_settings)
    if table is not None:
        mu, sd = table
    post = R.name(X, list(range(width)), mu, sd, synth, noise=noise, power=power, chunk=CHUNK)["all"]
    call, top = post.argmax(1), post.max(1)
    hit = (call == truth).astype(float)
    ans = top >= CLAIM
    groups = np.unique(group, return_inverse=True)[1]
    wrong = np.bincount(groups, weights=ans & (hit == 0))
    answered = np.bincount(groups, weights=ans)
    return {"fields": int(len(truth)), "columns": int(pop.true.shape[0]),
            "exact": float(hit.mean()), "exact_se": S.clustered_se(hit, group),
            "within_one": float((np.abs(call - truth) <= 1).mean()),
            "answered": float(ans.mean()), "answered_se": S.clustered_se(ans.astype(float), group),
            "n_answered": int(ans.sum()), "errors": int((ans & (hit == 0)).sum()),
            "precision": float(hit[ans].mean()) if ans.any() else float("nan"),
            "precision_se": S.ratio_se(wrong, answered) if ans.any() else float("nan"),
            "mean_top": float(top.mean()), "bayes_error_predicted": float((1.0 - top).mean()),
            "bayes_error_counted": float(1.0 - hit.mean())}
