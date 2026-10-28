"""The column as a chain of levels: the first of step e's methods (TODO.md, item P, step e).

The owner's words of 27 October 2026. At 16:40 UTC, of pymc-extras' automatic marginalisation
of its `DiscreteMarkovChain`, the column as a chain of levels with a missed body and an L6 or a
T13 as its transitions: "i absolutely want this". At 16:43 UTC: "make sure to account for this
feature existing as well https://www.pymc.io/projects/extras/en/latest/developer/extending_marginalization.html
essentially i want reverse-ablation as you gradually try more features/sophisticated methods/to
see how well they improve the accuracy. further you can consider how each will improve with more
data ...". This module is the chain and its exact answer in NumPy; chain_pymc.py holds it as the
two PyMC models the owner's page leads to, and chain_study.py scores it.

The chain. A field is B bodies read in order down a column, and the hidden state of each read
body is (column type, level). The types are the typical column (C3 to L5, 22 levels), the
six-lumbar column (an L6 after L5, 23) and the column with a thirteenth rib-bearing body (a T13
between T12 and L1, 23), so the states number 22 + 23 + 23 = 68 and a path never changes type:
the type is drawn once per column, with prior weight w_T. From one read body to the next the
level moves on k = 1, 2, ... positions down the type's own column, k - 1 bodies missed between
them, with the base law g(k) (step_law: each step misses j bodies with probability (1 - q) q^j,
cut at max_step - 1 and renormalised). A path whose bodies would run off the end of the column is
not a field, so the chain is conditioned on fitting by the h-transform: with h_{B-1} = 1 and

    h_t(T, p) = sum_k g(k) [p + k < n_T] h_{t+1}(T, p + k),

the transitions are P_t(p -> p + k) = g(k) h_{t+1}(p + k) / h_t(p) and the start is
pi(T, p) = w_T h_0(T, p) / sum_p' h_0(T, p'), so that every path of the chain fits, each type
keeps its weight w_T, and a path's probability is w_T prod_t g(k_t) over the fitting (start,
pattern) pairs of its type, normalised. With one step (g(1) = 1) and the typical type alone it is
step d's prior, every place that fits equally likely, and with g uniform over 1 to K it is TODO.md
item 4c's, every fitting (pattern, place) pair equally likely; the tests hold both within 1e-12.

The emissions. Given the path and the patient's size s, a field's values have rule.py's closed
form: a measure's values at the path's levels are jointly normal with the table's means scaled by
s^p and the covariance of the patient's offset, shared by every body of the measure, beside each
body's own draw and the error. The offset is shared, so the likelihood does not factor along the
chain, and the forward algorithm alone cannot sum the path out; the exact answer here enumerates
the chain's support paths instead and integrates the size on rule.py's nodes, as step d's
enumerated patterns do. An L6 and a T13 take table columns made by the generator's own
construction (columns.profiles): L6 = L5 + 0.5 (L5 - L4) with L5's SD, T13 half-way (blend 0.5)
between T12 and L1 in mean and SD. That is the generator's, stated, and the exact rule's anomalous
places, item 6, which the owner's other account works on, replace it when they land.

The weights, the probability of a missed body and the longest step are stated choices, not
measured prevalences: SKIP, MAX_STEP and WEIGHTS below.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import LEVELS
from . import columns as C
from . import rule as R

TYPES = ("typical", "six_lumbar", "t13")
NAMES = list(C.DRAW_LEVELS)                 # the levels a body can be named: C3 to L5, then L6 and T13
NAME_INDEX = {n: i for i, n in enumerate(NAMES)}
WEIGHTS = {"typical": 0.9, "six_lumbar": 0.05, "t13": 0.05}     # the types' prior weights, a stated choice
SKIP = 0.2                                  # a step's probability of missing a body, a stated choice
MAX_STEP = 2                                # the longest step: one body missed at most between two read


def type_levels(kind: str) -> List[str]:
    """The level names down a column of this type, as the generator lays it out."""
    if kind not in TYPES:
        raise ValueError("the chain's types are %r, not %r" % (TYPES, kind))
    return list(C.phenotype_levels(kind)[0])


def extended_table(mu: np.ndarray, sd: np.ndarray, blend: float = C.SYNTH["blend"]) -> Tuple[np.ndarray, np.ndarray]:
    """The table (measures, 22 levels) extended to NAMES: the 22 as given, then L6 and T13 built
    as the generator builds them (columns._profile, columns.profiles), so a table estimated from
    people is extended the same way as the table as printed."""
    mu, sd = np.asarray(mu, float), np.asarray(sd, float)
    if mu.shape != sd.shape or mu.shape[1] != len(LEVELS):
        raise ValueError("the table is (measures, %d levels): mu %r, sd %r" % (len(LEVELS), mu.shape, sd.shape))
    i4, i5, i12, i1 = (LEVELS.index(l) for l in ("L4", "L5", "T12", "L1"))
    l6_mu = mu[:, i5] + 0.5 * (mu[:, i5] - mu[:, i4])
    t13_mu = (1 - blend) * mu[:, i12] + blend * mu[:, i1]
    t13_sd = (1 - blend) * sd[:, i12] + blend * sd[:, i1]
    return np.column_stack([mu, l6_mu, t13_mu]), np.column_stack([sd, sd[:, i5], t13_sd])


def step_law(skip: float = SKIP, max_step: int = MAX_STEP) -> np.ndarray:
    """g(k) for k = 1 to max_step: a step misses j bodies with probability (1 - skip) skip^j, cut
    at max_step - 1 missed and renormalised; skip 0 is a field of consecutive bodies."""
    if not 0.0 <= skip < 1.0 or max_step < 1:
        raise ValueError("skip is in [0, 1) and max_step at least 1: %r, %r" % (skip, max_step))
    g = (1.0 - skip) * skip ** np.arange(max_step)
    return g / g.sum()


def uniform_steps(max_step: int) -> np.ndarray:
    """Every step from 1 to max_step equally likely: TODO.md item 4c's prior over patterns."""
    return np.full(max_step, 1.0 / max_step)


@dataclass(frozen=True)
class Chain:
    """The chain of levels for fields of n_bodies: its states (type, position in the type's
    column, name), its start law init (S,) and its transitions P (n_bodies - 1, S, S), block
    diagonal by type, each row summing to one."""
    types: Tuple[str, ...]
    weights: Tuple[float, ...]
    steps: Tuple[float, ...]
    n_bodies: int
    state_type: np.ndarray
    state_pos: np.ndarray
    state_name: np.ndarray
    init: np.ndarray
    P: np.ndarray

    @property
    def n_states(self) -> int:
        return len(self.state_type)


def _fit(n: int, steps: np.ndarray, B: int) -> np.ndarray:
    """h (B, n): h[t, p] the base law's probability that a path at position p after body t still
    fits the column with its remaining bodies."""
    h = np.zeros((B, n))
    h[B - 1] = 1.0
    for t in range(B - 2, -1, -1):
        for k, g in enumerate(steps, start=1):
            h[t, :n - k] += g * h[t + 1, k:]
    return h


def build(types: Sequence[str] = TYPES, weights: Optional[Sequence[float]] = None,
          steps: Sequence[float] = (1.0,), n_bodies: int = 3) -> Chain:
    """The chain for fields of n_bodies over these types, with these prior weights (WEIGHTS's,
    renormalised over the types, by default) and this base law of steps, conditioned on fitting
    by the h-transform (the module's docstring)."""
    types = tuple(types)
    g = np.asarray(steps, float)
    if g.ndim != 1 or len(g) == 0 or np.any(g < 0) or abs(g.sum() - 1.0) > 1e-12:
        raise ValueError("steps is a law over 1 to K: %r" % (list(g),))
    w = np.array([WEIGHTS[t] for t in types] if weights is None else weights, float)
    if w.shape != (len(types),) or np.any(w <= 0):
        raise ValueError("one positive weight per type: %r for %r" % (list(w), types))
    w = w / w.sum()
    B = int(n_bodies)
    if B < 1:
        raise ValueError("a field has at least one body")
    st, sp, sn, init, blocks = [], [], [], [], []
    for ti, kind in enumerate(types):
        names = type_levels(kind)
        n = len(names)
        h = _fit(n, g, B)
        if h[0].sum() <= 0:
            raise ValueError("no field of %d bodies fits a %s column" % (B, kind))
        st += [ti] * n
        sp += list(range(n))
        sn += [NAME_INDEX[x] for x in names]
        init.append(w[ti] * h[0] / h[0].sum())
        Pt = np.zeros((max(B - 1, 0), n, n))
        for t in range(B - 1):
            for p in range(n):
                if h[t, p] <= 0:
                    Pt[t, p, p] = 1.0           # a state no fitting path reaches at t: any row will do
                    continue
                for k, gk in enumerate(g, start=1):
                    if p + k < n:
                        Pt[t, p, p + k] = gk * h[t + 1, p + k] / h[t, p]
        blocks.append(Pt)
    S = len(st)
    P = np.zeros((max(B - 1, 0), S, S))
    o = 0
    for Pt in blocks:
        n = Pt.shape[1]
        P[:, o:o + n, o:o + n] = Pt
        o += n
    return Chain(types=types, weights=tuple(w.tolist()), steps=tuple(g.tolist()), n_bodies=B,
                 state_type=np.array(st), state_pos=np.array(sp), state_name=np.array(sn),
                 init=np.concatenate(init), P=P)


def support_paths(init: np.ndarray, P: np.ndarray) -> np.ndarray:
    """Every state path of positive probability, (N, B): from each start of positive probability,
    every move of positive probability, body by body."""
    paths = [[int(s)] for s in np.flatnonzero(init > 0)]
    for t in range(P.shape[0]):
        paths = [p + [int(n)] for p in paths for n in np.flatnonzero(P[t, p[-1]] > 0)]
    return np.array(paths, dtype=np.int64).reshape(len(paths), P.shape[0] + 1)


def path_log_prior(init: np.ndarray, P: np.ndarray, paths: np.ndarray) -> np.ndarray:
    """log p(path) of each state path (N,)."""
    lp = np.log(init[paths[:, 0]])
    for t in range(paths.shape[1] - 1):
        lp = lp + np.log(P[t, paths[:, t], paths[:, t + 1]])
    return lp


@dataclass(frozen=True)
class Paths:
    """The chain's paths as the rule sees them: each distinct path of names (H, B), indices into
    NAMES, its prior (the chain's probability summed over the state paths that read so, since a
    body's values depend on its name alone), the mass of each type in it (H, types), and for each
    one state path that reads so, the type, the start and the offsets down the type's own column,
    which say where rule.py finds its likelihood."""
    names: np.ndarray
    log_prior: np.ndarray
    type_mass: np.ndarray
    rep_type: np.ndarray
    rep_start: np.ndarray
    rep_offsets: Tuple[Tuple[int, ...], ...]

    def __len__(self) -> int:
        return len(self.log_prior)


def paths_of(chain: Chain) -> Paths:
    """The chain's distinct name paths in NumPy's sorted order, each with its prior, its types'
    mass and a state path of the first type in the chain's order that reads so."""
    sp = support_paths(chain.init, chain.P)
    lp = path_log_prior(chain.init, chain.P, sp)
    names = chain.state_name[sp]
    uniq, first, inv = np.unique(names, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    prob = np.zeros(len(uniq))
    np.add.at(prob, inv, np.exp(lp))
    mass = np.zeros((len(uniq), len(chain.types)))
    np.add.at(mass, (inv, chain.state_type[sp[:, 0]]), np.exp(lp))
    order = np.lexsort((np.arange(len(sp)), chain.state_type[sp[:, 0]]))      # the first type wins
    rep = np.full(len(uniq), -1)
    for i in order:
        if rep[inv[i]] < 0:
            rep[inv[i]] = i
    pos = chain.state_pos[sp[rep]]
    return Paths(names=uniq, log_prior=np.log(prob), type_mass=mass / prob[:, None],
                 rep_type=chain.state_type[sp[rep, 0]], rep_start=pos[:, 0],
                 rep_offsets=tuple(tuple(int(o) for o in row - row[0]) for row in pos))


def _groups(paths: Paths) -> Dict[Tuple[int, Tuple[int, ...]], List[int]]:
    """The paths by (type, offsets), the unit rule.py scores at every start at once."""
    out: Dict[Tuple[int, Tuple[int, ...]], List[int]] = {}
    for h in range(len(paths)):
        out.setdefault((int(paths.rep_type[h]), paths.rep_offsets[h]), []).append(h)
    return out


def path_logev(X: np.ndarray, paths: Paths, chain: Chain, mu_ext: np.ndarray, sd_ext: np.ndarray,
               subsets: Dict[str, Sequence[int]], noise: np.ndarray, power: np.ndarray,
               nodes: Tuple[np.ndarray, np.ndarray], block: int = 128) -> Dict[str, np.ndarray]:
    """log p(field | path), the size integrated on the nodes, (fields, paths) under each subset of
    the measures: rule.py's loglik for every (type, offsets) the paths hold, on the type's own
    column of the extended table cut to the starts needed, its blocks built once and the fields
    put through them `block` at a time."""
    X = np.asarray(X, float)
    F = X.shape[0]
    sizes, logw = nodes
    out = {k: np.full((F, len(paths)), np.nan) for k in subsets}
    for (ti, offsets), hs in _groups(paths).items():
        cols = [NAME_INDEX[x] for x in type_levels(chain.types[ti])]
        starts = paths.rep_start[hs]
        lo, hi = int(starts.min()), int(starts.max())
        sub = cols[lo:hi + offsets[-1] + 1]
        mu, sd = np.ascontiguousarray(mu_ext[:, sub]), np.ascontiguousarray(sd_ext[:, sub])
        blocks = R.table_blocks(offsets, mu, sd, R.SYNTH, sizes, noise, power)
        at = starts - lo
        for f0, f1, ll in R.loglik_blocks(X, blocks, len(sizes), hi - lo + 1, block):     # (M, f, J, K)
            ll = ll[..., at]
            for k, idx in subsets.items():
                out[k][f0:f1, hs] = R.logsumexp(ll[list(idx)].sum(0) + logw[None, :, None], 1)
    return out


def posterior(logev: np.ndarray, log_prior: np.ndarray) -> np.ndarray:
    """The posterior over paths (fields, paths)."""
    return R.posterior(logev, log_prior)


def body_posterior(post: np.ndarray, names: np.ndarray, t: int) -> np.ndarray:
    """The posterior of body t's name, (fields, NAMES), summed over the paths."""
    out = np.zeros((post.shape[0], len(NAMES)))
    np.add.at(out.T, names[:, t], post.T)
    return out


def known_pattern_posterior(X: np.ndarray, offsets: np.ndarray, mu: np.ndarray, sd: np.ndarray,
                            subsets: Dict[str, Sequence[int]], noise: np.ndarray, power: np.ndarray,
                            nodes: Tuple[np.ndarray, np.ndarray], t: int) -> Dict[str, np.ndarray]:
    """The rule that knows each field's gaps (item 4c's third rule): the typical column's places
    under the field's own offsets, every place that fits equally likely, as body t's name
    posterior (fields, NAMES)."""
    X, offsets = np.asarray(X, float), np.asarray(offsets, int)
    out = {k: np.zeros((len(X), len(NAMES))) for k in subsets}
    pats, inv = np.unique(offsets, axis=0, return_inverse=True)
    for i, pat in enumerate(pats):
        f = np.flatnonzero(inv.reshape(-1) == i)
        post = R.name(X[f], pat, mu, sd, R.SYNTH, subsets=subsets, noise=noise, power=power, nodes=nodes)
        for k, p in post.items():
            out[k][f[:, None], (np.arange(p.shape[1]) + pat[t])[None, :]] = p
    return out


# ---- fields drawn by the chain's own law ----------------------------------------------------

def draw_paths(kind: str, steps: Sequence[float], n_bodies: int, n: int, rng) -> np.ndarray:
    """n paths of positions down a column of this type, (n, B), by the chain's law given the type:
    a start that fits, then each step by the conditioned transitions."""
    ch = build((kind,), (1.0,), steps, n_bodies)
    start = rng.choice(ch.n_states, size=n, p=ch.init)
    out = np.empty((n, ch.n_bodies), np.int64)
    out[:, 0] = start
    for t in range(ch.n_bodies - 1):
        for i in range(n):
            out[i, t + 1] = rng.choice(ch.n_states, p=ch.P[t, out[i, t]])
    return ch.state_pos[out]


def draw_fields(cols: C.Columns, steps: Sequence[float], n_bodies: int, per_column: int, seed: int):
    """per_column fields from each column, drawn by the chain's law given the column's type, which
    is its phenotype: X (fields, measures, bodies), the names read (fields, bodies) as indices into
    NAMES by the column's own names, the offsets (fields, bodies) and the column of each field."""
    rng = np.random.default_rng(seed)
    X, names, offsets, col = [], [], [], []
    for c in range(len(cols)):
        pos = draw_paths(cols.phenotype[c], steps, n_bodies, per_column, rng)
        for row in pos:
            X.append(cols.values[c, row, :].T)
            names.append([NAME_INDEX[cols.levels[c][p]] for p in row])
            offsets.append(row - row[0])
            col.append(c)
    return np.array(X), np.array(names), np.array(offsets), np.array(col)


# ---- the forward algorithm, given the offsets ---------------------------------------------

def state_loglik(X: np.ndarray, chain: Chain, mu_ext: np.ndarray, sd_ext: np.ndarray, log_s: np.ndarray,
                 z: np.ndarray, rho: float, noise: np.ndarray, power: np.ndarray) -> np.ndarray:
    """log p(body's values | state, size, offsets), (draws, fields, B, S): given the patient's size
    and offsets the bodies are independent, each measure's value normal about s^p (mu + rho sd z)
    with variance s^2p (1 - rho^2) sd^2 + noise^2. log_s is (draws, fields), z (draws, fields, M);
    a value not read adds nothing."""
    X = np.asarray(X, float)
    read = np.isfinite(X)
    x = np.where(read, X, 0.0)                                              # (F, M, B)
    lvl = chain.state_name
    mu, sd = mu_ext[:, lvl], sd_ext[:, lvl]                                 # (M, S)
    s = np.exp(np.asarray(power, float)[None, None, :] * np.asarray(log_s, float)[..., None])   # (D, F, M)
    mean = s[..., None] * (mu[None, None] + rho * sd[None, None] * np.asarray(z, float)[..., None])   # (D, F, M, S)
    var = (s * s)[..., None] * (1 - rho * rho) * sd[None, None] ** 2 + (np.asarray(noise, float) ** 2)[None, None, :, None]
    r = x[None, :, :, :, None] - mean[:, :, :, None, :]                     # (D, F, M, B, S)
    ll = -0.5 * (r * r / var[:, :, :, None, :] + np.log(2 * np.pi * var)[:, :, :, None, :])
    return (ll * read[None, :, :, :, None]).sum(2)                          # (D, F, B, S)


def forward_backward(log_e: np.ndarray, init: np.ndarray, P: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """The forward-backward algorithm in log space over the last two axes (..., B, S): each body's
    state marginals (..., B, S) and the log evidence (...)."""
    with np.errstate(divide="ignore"):
        logP, log_init = np.log(P), np.log(init)
    B = log_e.shape[-2]
    a = [log_init + log_e[..., 0, :]]
    for t in range(1, B):
        a.append(_lse(a[-1][..., :, None] + logP[t - 1], -2) + log_e[..., t, :])
    b = [np.zeros_like(a[-1])]
    for t in range(B - 2, -1, -1):
        b.insert(0, _lse(logP[t] + (log_e[..., t + 1, :] + b[0])[..., None, :], -1))
    alpha, beta = np.stack(a, -2), np.stack(b, -2)
    logev = _lse(alpha[..., -1, :], -1)
    return np.exp(alpha + beta - logev[..., None, None]), logev


def _lse(a: np.ndarray, axis: int) -> np.ndarray:
    top = np.max(a, axis=axis, keepdims=True)
    top = np.where(np.isfinite(top), top, 0.0)
    with np.errstate(divide="ignore"):
        return np.squeeze(top, axis) + np.log(np.exp(a - top).sum(axis))


def state_body_posterior(marg: np.ndarray, chain: Chain, t: int) -> np.ndarray:
    """Body t's name posterior (..., NAMES) from the state marginals (..., B, S)."""
    out = np.zeros(marg.shape[:-2] + (len(NAMES),))
    for s, n in enumerate(chain.state_name):
        out[..., n] += marg[..., t, s]
    return out
