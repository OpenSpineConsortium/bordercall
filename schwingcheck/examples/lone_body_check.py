"""How far a lone L6 or T13 lies from the names it is taken for, against the chain's prior odds.

    PYTHONPATH=. python schwingcheck/examples/lone_body_check.py

At one body the chain names a lone L6 rarely and a lone T13 about half the time (one_body.py, its
record in records/one-body-2026-10-29/). This prints, for pairs of names on the extended table
(chain.extended_table, every measure of the pool), the squared standardised distance between the
two names' means summed over the measures: each measure's difference over its SD at the second
name and its error, the variance a lone body's value has about its name's mean, since a patient's
offset and the body's own residual together have the table's SD. Beside it, the same distance once
the patient's size may move, the best common shift of log s taken out by weighted least squares on
the first-order change each measure's power of the size gives it, and the shift itself. Half the
distance is what a body drawn at the first name gains, in log likelihood on average, over the
second when the size is given; the prior's log odds of the second name over the first, at the
chain's stated weights, are printed beside it. schwingcheck/README.md quotes what this printed on
29 October 2026.
"""
from __future__ import annotations

import math

import numpy as np

from schwingcheck import chain as CH
from schwingcheck import chain_study as CS
from schwingcheck import one_body as O

PAIRS = (("L6", "L5"), ("T13", "T12"), ("T13", "L1"), ("L5", "L4"), ("T12", "L1"), ("T5", "T6"))


def distances(mu: np.ndarray, sd: np.ndarray, noise: np.ndarray, power: np.ndarray, a: str, b: str):
    """The squared standardised distance of name a from name b, raw and with the size free, and the
    shift of log s that takes out the most of it."""
    i, j = CH.NAME_INDEX[a], CH.NAME_INDEX[b]
    d = mu[:, i] - mu[:, j]
    w = 1.0 / (sd[:, j] ** 2 + noise ** 2)
    g = mu[:, j] * power
    shift = float(np.sum(w * g * d) / np.sum(w * g * g))
    return float(np.sum(w * d ** 2)), float(np.sum(w * (d - shift * g) ** 2)), shift


def main() -> None:
    pool, _, mu, sd, noise, power, _ = CS.setting()
    mu_e, sd_e = (np.asarray(t, float) for t in CH.extended_table(mu, sd))
    prior = O.prior_over_names("chain")
    print("%d measures; the chain's stated weights %s" % (len(pool), CH.WEIGHTS))
    print("%-10s %9s %11s %9s %16s" % ("names", "distance", "size free", "shift", "prior log odds"))
    for a, b in PAIRS:
        raw, free, shift = distances(mu_e, sd_e, np.asarray(noise, float), np.asarray(power, float), a, b)
        odds = math.log(prior[CH.NAME_INDEX[b]] / prior[CH.NAME_INDEX[a]])
        print("%-10s %9.2f %11.2f %9.3f %16.2f" % ("%s, %s" % (a, b), raw, free, shift, odds))


if __name__ == "__main__":
    main()
