# Bayesian optimization and derivative-free optimization software for noisy, discrete/combinatorial/mixed black-box objectives (state as of 26 October 2026)

All version numbers, upload dates, repository push dates and last-commit dates below were read
directly from the PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`) and the GitHub REST API
(`https://api.github.com/repos/<owner>/<repo>`) on **2026-10-26**. Where a fact came from an API
rather than a human-readable page, the citation points at the canonical project page for the same
object.

Target problem assumed throughout: maximize a noisy, expensive, simulation-evaluated objective whose
decision variable is a **subset = binary vector of length 7–30** (so 128 to ~10^9 candidates, with
the user's stated enumerable regime 128–30,000), optionally plus a few continuous nuisance
parameters, with a **known per-evaluation standard error** (exact binomial SE from Monte Carlo).

---

## Q1. Which Bayesian optimization frameworks are production-trusted in 2026? Last release, GPU, explicit noise modelling

### Takeaway
Four stacks are unambiguously alive and production-grade in October 2026: **Ax/BoTorch** (Meta, MIT,
Ax 1.3.1 / BoTorch 0.18.1, GPU via PyTorch, explicit per-observation noise), **Optuna 5.0** (Preferred
Networks, MIT), **SMAC3 2.4.1** (AutoML Freiburg, BSD-3) and **Ray Tune** (as an orchestration layer).
**Google OSS Vizier** has an active repository but **no PyPI release since 2025-02-01**. **HEBO** has
had **no release since 2024-11-04** and must be flagged as possibly stale. **GPyOpt, scikit-optimize,
Dragonfly, pySOT and SnobFit are dead or effectively unmaintained.**

### Cited Findings

**Alive and production-grade**

- **Ax** (Meta): latest `ax-platform` **1.3.1, uploaded 2026-06-09**; 10 releases in 2025–2026; MIT; requires Python ≥3.11 — [PyPI ax-platform](https://pypi.org/project/ax-platform/). Repository `facebook/Ax` pushed **2026-10-22**, 2,831 stars, MIT, last commit 2026-10-22 ("Preserve multi-metric outcome constraints through candidate generation") — [github.com/facebook/Ax](https://github.com/facebook/Ax).
- **BoTorch** (Meta): latest **0.18.1, uploaded 2026-06-08**; 11 releases in 2025–2026; Python ≥3.11 — [PyPI botorch](https://pypi.org/project/botorch/). Repository `pytorch/botorch` pushed **2026-10-16**, 3,634 stars, MIT — [github.com/pytorch/botorch](https://github.com/pytorch/botorch). The README states BoTorch is written "for highly parallelized modern hardware (e.g. GPUs) using device-agnostic code" — [BoTorch README](https://github.com/pytorch/botorch/blob/main/README.md).
- **GPyTorch** (the GP engine under BoTorch): **1.15.2, uploaded 2026-02-28**, MIT; repo `cornellius-gp/gpytorch` pushed 2026-10-02, 3,930 stars — [PyPI gpytorch](https://pypi.org/project/gpytorch/), [github.com/cornellius-gp/gpytorch](https://github.com/cornellius-gp/gpytorch). Its `FixedNoiseGaussianLikelihood` takes a per-point `noise` tensor and an optional `learn_additional_noise` flag — [GPyTorch likelihood docs](https://docs.gpytorch.ai/en/stable/likelihoods.html).
- **Optuna**: **5.0.0, uploaded 2026-09-07**; 14 releases in 2025–2026; MIT; repo `optuna/optuna` pushed 2026-10-23, 14,969 stars — [PyPI optuna](https://pypi.org/project/optuna/), [github.com/optuna/optuna](https://github.com/optuna/optuna). Optuna 5.0 makes multivariate TPE and the constant-liar strategy default for single-objective studies, makes TPE (not NSGA-II) the multi-objective default, moves constraints into the core Trial API (`trial.set_constraint()`), and **promotes `GPSampler` to a stable API**; Preferred Networks shipped a separate Rust engine, Rustuna 0.1, alongside it — [Optuna 5.0 / Rustuna 0.1 release write-up](https://aicybr.com/blog/optuna-5-rustuna-0-1-release-guide) (secondary source; the primary is the GitHub release page).
- **OptunaHub**: `optunahub` **0.5.0, uploaded 2026-09-09**, MIT; repo pushed 2026-10-23 (last commit "support-python-up-to-3.15") — [PyPI optunahub](https://pypi.org/project/optunahub/), [github.com/optuna/optunahub](https://github.com/optuna/optunahub).
- **SMAC3** (AutoML / Uni Freiburg): `smac` **2.4.1, uploaded 2026-09-10**; GitHub releases v2.4.0 (2026-04-10) and v2.4.1 (2026-09-10); BSD-3-Clause; repo pushed 2026-10-26, 1,262 stars — [PyPI smac](https://pypi.org/project/smac/), [github.com/automl/SMAC3/releases](https://github.com/automl/SMAC3/releases).
- **Ray / Ray Tune**: `ray` **2.59.0 (2026-10-02)**, with 2.57.1 and 2.58.1 also uploaded 2026-10-21; 33 releases in 2025–2026; Apache-2.0; repo pushed 2026-10-26, 44,123 stars — [PyPI ray](https://pypi.org/project/ray/), [github.com/ray-project/ray](https://github.com/ray-project/ray). Ray Tune is a scheduler/orchestrator that wraps other searchers rather than a surrogate-modelling library of its own.
- **SyneTune** (AWS): `syne-tune` **0.16.0, uploaded 2026-08-03**; Apache-2.0; repo pushed 2026-10-21, last commit 2026-09-18 ("feat: bbob functions"), 426 stars. **The repo has moved to `syne-tune/syne-tune`; `awslabs/syne-tune` now resolves to it** (both API paths return the same repository object) — [PyPI syne-tune](https://pypi.org/project/syne-tune/), [github.com/syne-tune/syne-tune](https://github.com/syne-tune/syne-tune). Its `extra` dependency group pulls in BoTorch — [SyneTune README](https://github.com/syne-tune/syne-tune/blob/main/README.md).
- **Trieste** (Secondmind): **4.6.1, uploaded 2026-10-02**; 8 releases in 2025–2026; Apache-2.0; repo pushed 2026-10-15, default branch `develop`, 254 stars — [PyPI trieste](https://pypi.org/project/trieste/), [github.com/secondmind-labs/trieste](https://github.com/secondmind-labs/trieste). Built on TensorFlow/GPflow; `gpflow` **2.11.2 (2026-10-14)** is itself current — [PyPI gpflow](https://pypi.org/project/gpflow/).
- **Nevergrad** (Meta): latest release **1.0.12, 2025-04-23** (GitHub release 1.0.12, published 2025-04-23); repo `facebookresearch/nevergrad` pushed 2026-10-20, last commit 2026-10-13, 4,217 stars, MIT — [PyPI nevergrad](https://pypi.org/project/nevergrad/), [github.com/facebookresearch/nevergrad/releases](https://github.com/facebookresearch/nevergrad/releases). So: **repo active, release cadence stalled ~18 months.**

**Active repo but stale distribution**

- **Google OSS Vizier**: `google-vizier` latest **0.1.24, uploaded 2025-02-01**; only 4 uploads in 2025–2026, none since — [PyPI google-vizier](https://pypi.org/project/google-vizier/). Repository `google/vizier` pushed **2026-10-20** (last commit "Suppress new Pyrefly findings before upgrading to v1.4.0"), 1,680 stars, Apache-2.0 — [github.com/google/vizier](https://github.com/google/vizier). The README describes it as "based on Google Vizier … one of the first hyperparameter tuning services designed to work at scale", offers `pip install google-vizier[jax]` for a "JAX-based Bayesian Optimizer", supports float/integer/discrete/categorical parameters via `add_float_param`, `add_int_param`, `add_discrete_param`, `add_categorical_param`, requires Python ≥3.10, and cites the 2024 paper "The Vizier Gaussian Process Bandit Algorithm". The README does **not** say OSS Vizier is the same service Google runs internally, does **not** mention GPU, and does **not** mention measurement noise — [Vizier README](https://github.com/google/vizier/blob/main/README.md).

**Possibly stale (flagged per the assignment constraint)**

- **HEBO** (Huawei Noah's Ark): `HEBO` latest **0.3.6, uploaded 2024-11-04**; **zero releases in 2025 or 2026** — [PyPI HEBO](https://pypi.org/project/HEBO/). The monorepo `huawei-noah/HEBO` is active (pushed 2026-10-12, 2,815 stars) but **commits touching the `HEBO/` subdirectory stop at 2025-08-08, and those were README link edits; the last functional commit there is "v0.3.6" on 2024-11-04** — [github.com/huawei-noah/HEBO commits for HEBO/](https://github.com/huawei-noah/HEBO/commits/master/HEBO). The repo has **no GitHub license object** (`license: None`), though PyPI classifies it MIT. HEBO was the winning submission to the NeurIPS 2020 Black-Box Optimisation Challenge — [HEBO README](https://github.com/huawei-noah/HEBO/blob/master/HEBO/README.md).

**Dead / unmaintained — do not build on these**

- **GPyOpt**: last release **1.2.6, 2020-03-19**; repository `SheffieldML/GPyOpt` is **archived (`archived: true`, verified)**, 944 stars, BSD-3-Clause, final commit 2023-01-17 with the message "Archival of the repo" — [PyPI GPyOpt](https://pypi.org/project/GPyOpt/), [github.com/SheffieldML/GPyOpt](https://github.com/SheffieldML/GPyOpt). **Deprecated; confirmed.**
- **scikit-optimize**: last release **0.10.2, 2024-06-04**, BSD-3; repository `scikit-optimize/scikit-optimize` is **archived (`archived: true`, verified)**, `pushed_at` 2024-02-23, and the last commit on `master` is **2021-10-12**; 2,830 stars — [PyPI scikit-optimize](https://pypi.org/project/scikit-optimize/), [github.com/scikit-optimize/scikit-optimize](https://github.com/scikit-optimize/scikit-optimize). Its README still advertises it as a library to "minimize (very) expensive and noisy black-box functions" — [skopt README](https://github.com/scikit-optimize/scikit-optimize/blob/master/README.rst). **Treat as unmaintained.**
- **Dragonfly**: `dragonfly-opt` last release **0.1.7, 2022-10-01**; repo `dragonfly/dragonfly` `pushed_at` 2023-06-19 (a side branch) but the **`master` branch's last commit is 2022-10-01** ("updated version"); 896 stars, MIT, not archived — [PyPI dragonfly-opt](https://pypi.org/project/dragonfly-opt/), [github.com/dragonfly/dragonfly](https://github.com/dragonfly/dragonfly). **No release since 2022 — stale.**
- **pySOT**: last release **0.3.3, 2020-06-22**; repo `dme65/pySOT` `pushed_at` and last commit both 2021-10-27, 217 stars, no SPDX licence detected, not archived — [PyPI pySOT](https://pypi.org/project/pySOT/), [github.com/dme65/pySOT](https://github.com/dme65/pySOT). **Stale.**
- **SnobFit** (`SQSnobFit`): last release **0.4.5, 2020-11-30**, PyPI license classifier "Other/Proprietary License" — [PyPI SQSnobFit](https://pypi.org/project/SQSnobFit/). **Stale, and the licence is not a standard OSI licence.**

**Adjacent packages that are current (context for the writer)**

- `bayesian-optimization` (fmfn): **3.4.0, 2026-10-02**, MIT, 9 releases in 2025–2026 — [PyPI bayesian-optimization](https://pypi.org/project/bayesian-optimization/). Continuous-only GP-UCB/EI library; simple.
- `emukit` **0.5.1 (2026-02-22)**, Apache-2.0 — [PyPI emukit](https://pypi.org/project/emukit/) (revived after a long gap; 0.5.0 was 2025-12-19).
- `hyperopt` **0.3.0, 2026-07-24** — [PyPI hyperopt](https://pypi.org/project/hyperopt/) (first non-rc release in years).
- `openbox` **0.9.0 (2026-03-27)**, MIT — [PyPI openbox](https://pypi.org/project/openbox/).
- `bofire` (BASF, BoTorch-based experimental design) **0.5.0, 2026-08-11**, BSD-3, 13 releases in 2025–2026 — [PyPI bofire](https://pypi.org/project/bofire/). This is the clearest example of an industrial (chemicals) production wrapper over BoTorch.
- `sambo` ("Sequential And Model-Based Optimization") **1.25.2, 2025-07-10**, **AGPL-3.0** — [PyPI sambo](https://pypi.org/project/sambo/). AGPL is a hard blocker for many industrial users.

### Inferences
- For this problem the defensible production choices are **Ax/BoTorch** (if you want explicit noise and real discrete machinery) and **Optuna** (if you want the lowest-friction API and good study management). SMAC3 is a strong third because its random-forest surrogate is natively categorical.
- Vizier is usable but you would be installing from GitHub, not PyPI; that is a maintenance cost and a reproducibility hazard for a paper.
- HEBO's monorepo activity is misleading: the repo is a Huawei multi-project monorepo, and the activity is in other subprojects. Pinning HEBO 0.3.6 means pinning a 2024 artifact.

### Gaps
- I could not verify "who uses it in industry" from primary sources for most packages. The only industrial-adoption evidence I verified is: BoTorch/Ax are published by Meta (`facebook/Ax`, `pytorch/botorch`), Vizier by Google, SyneTune by AWS (now in its own org), HEBO by Huawei Noah's Ark, Trieste by Secondmind, Optuna by Preferred Networks, and BoFire by BASF-affiliated authors. Claims like "Ax is used for Meta's internal ranking experiments" are widely repeated but I did not verify them in this pass.
- I did not find a 2025–2026 independent benchmark or survey of BO libraries (Bayesmark/HPOBench-style) in this pass. The search for a head-to-head library benchmark returned nothing usable.

---

## Q2. Combinatorial Bayesian optimization: what is actually implementable in 2026

### Takeaway
**Every named combinatorial-BO method from the literature is research code, and almost all of it is
abandoned.** BOCS (2019), COMBO (2020), CoCaBO (2019), SAASBO reference code (2021), TuRBO (2020),
Casmopolitan (2023), BODi (2023) and Bounce (2024) all have last commits in the years shown — none
has been touched in 2025 or 2026. The only maintained, installable, library-grade implementations of
this family are **inside BoTorch**: SAAS fully-Bayesian GPs, the mixed/categorical kernel model, and
the discrete and mixed acquisition optimizers. `pip install bounce` installs an **unrelated package**.

### Cited Findings

All rows below were checked on **2026-10-26** against the authenticated GitHub REST API, recording
both `pushed_at` (last commit to **any** branch) and the last commit on the **default** branch. These
diverge for several of these repos, and the divergence is itself informative: a 2024 `pushed_at` on
COMBO, TuRBO and BODi reflects a touch to a side branch, while the code a `pip install` or `git clone`
would get has not moved since 2020, 2020 and 2023 respectively.

| Method | Repository | `pushed_at` (any branch) | Last commit (default branch) | Archived | Stars | Licence | Status |
|---|---|---|---|---|---|---|---|
| BOCS (Baptista & Poloczek, ICML 2018) | [baptistar/BOCS](https://github.com/baptistar/BOCS) | 2019-10-25 | **2019-10-24** ("categorical variable support") | No | 105 | GPL-3.0 | Research code, abandoned; MATLAB-centric |
| COMBO (Oh et al., NeurIPS 2019; graph/diffusion kernels) | [QUVA-Lab/COMBO](https://github.com/QUVA-Lab/COMBO) | 2024-07-25 | **2020-11-01** ("compatiable with pytorch 1.6.0") | No | 52 | NOASSERTION (no SPDX licence detected) | Research code, abandoned; pinned to PyTorch 1.6 |
| CoCaBO (Ru et al., ICML 2020) | [rubinxin/CoCaBO_code](https://github.com/rubinxin/CoCaBO_code) | 2019-08-20 | **2019-08-20** | No | 55 | MIT | Research code, abandoned |
| TuRBO (Eriksson et al., NeurIPS 2019; trust regions) | [uber-research/TuRBO](https://github.com/uber-research/TuRBO) | 2024-07-25 | **2020-02-19** ("Updated citation key") | No | 239 | NOASSERTION | Reference code abandoned — **but TuRBO is reimplemented and maintained inside BoTorch/Ax** (see inference) |
| SAASBO (Eriksson & Jankowiak, UAI 2021) | [martinjankowiak/saasbo](https://github.com/martinjankowiak/saasbo) | 2021-09-16 | **2021-08-22** | No | 54 | none | Reference code abandoned — **but shipped in BoTorch as `SaasFullyBayesianSingleTaskGP`**, which the BoTorch docs cite to "High-Dimensional Bayesian Optimization with Sparse Axis-Aligned Subspaces" and describe as fully Bayesian inference over hyperparameters via NUTS — [BoTorch models API](https://botorch.readthedocs.io/en/stable/models.html) |
| Casmopolitan (Wan et al., ICML 2021; mixed trust regions + Hamming) | [xingchenwan/Casmopolitan](https://github.com/xingchenwan/Casmopolitan) | 2023-02-03 | **2023-02-03** (README only) | No | 36 | MIT | Research code, no 2024–2026 activity |
| BODi (Deshwal et al., AISTATS 2023; dictionary/binary embeddings) | [aryandeshwal/BODi](https://github.com/aryandeshwal/BODi) | 2024-03-17 | **2023-03-16** ("AISTATS code upload") | No | 13 | none | Research code, abandoned |
| Bounce (Papenmeier et al., NeurIPS 2023) | **moved** — `LeoIV/bounce` 301-redirects to [lpapenme/bounce](https://github.com/lpapenme/bounce) | 2024-04-30 | **2024-04-30** | No | 19 | MIT | Research code. **`pip install bounce` gets the wrong thing**: PyPI `bounce` 0.7.1 (2026-10-14) is "a Python keyword search redirect engine" by Jay Marcyes — [PyPI bounce](https://pypi.org/project/bounce/) |
| MerCBO (Deshwal et al., Mercer features for combinatorial BO) | [aryandeshwal/MerCBO](https://github.com/aryandeshwal/MerCBO) | 2021-06-14 | **2021-06-14** | No | 10 | NOASSERTION | Research code, abandoned |
| Probabilistic reparameterization (Daulton et al., NeurIPS 2022, discrete/mixed BO) | [facebookresearch/bo_pr](https://github.com/facebookresearch/bo_pr) | 2022-10-18 | **2022-10-18** ("update pdf") | No | 79 | MIT | Research code, abandoned. The paper is the clearest statement of the regime boundary (see Q7) — [arXiv 2210.10199](https://arxiv.org/pdf/2210.10199) |
| ALEBO (linear embeddings) | [facebookresearch/alebo](https://github.com/facebookresearch/alebo) | 2021-09-07 | **2021-01-14** | **Yes — archived** | 45 | NOASSERTION | Dead |
| BORE | [ltiao/bore](https://github.com/ltiao/bore) | 2022-12-26 | **2022-10-04** | No | 23 | none | Stale |

- Named methods with **no maintained standalone package on PyPI** as of 2026-10-26: BOCS, COMBO, Casmopolitan, BODi, Bounce, CoCaBO, MerCBO. (For Bounce specifically the PyPI name is taken by an unrelated project — [PyPI bounce](https://pypi.org/project/bounce/).)
- **Installability verdict, stated plainly for the report:** none of these eleven repositories is archived, so all can still be cloned, but **none is distributed on PyPI and none has a default-branch commit in 2025 or 2026**. The newest is Bounce (2024-04-30) and the oldest is CoCaBO (2019-08-20). A colleague in late 2026 would be installing an unversioned clone against whatever Python/PyTorch pins the authors left — COMBO's final commit message is literally "compatiable with pytorch 1.6.0", a 2020 PyTorch. Three of them (BODi, saasbo, BORE) have **no licence at all**, which makes reuse legally ambiguous regardless of maintenance; COMBO, TuRBO and MerCBO carry a non-standard licence GitHub cannot identify (`NOASSERTION`). Verified via the GitHub REST API on 2026-10-26 — repository links in the table above.
- CatMADS (Audet et al., 2025) is a **direct-search**, not BO, categorical method; its implementation is "built on top of the NOMAD software … a C++ implementation of the MADS algorithm" — [CatMADS, arXiv 2506.06937](https://arxiv.org/pdf/2506.06937).

### Inferences
- If a combinatorial-BO *method* is required, the realistic options are (a) use BoTorch's own discrete/mixed machinery, which is the only maintained implementation of this family, or (b) vendor a research repo and accept that you now own it. For a 7–30-bit binary vector, (a) is adequate: `optimize_acqf_discrete` over an enumerated candidate set *is* the exact acquisition maximizer that BOCS/COMBO approximate.
- TuRBO and SAASBO are the two methods from this list that effectively survived by being absorbed into BoTorch; the standalone repos are of historical interest only. I verified SAASBO's presence in BoTorch's model docs; I did **not** verify a maintained `TurboState` in the BoTorch *library* (see gaps).
- Casmopolitan and BODi are the two methods whose published benchmarks are closest to this problem (binary/categorical trust regions, binary dictionaries), and both are unmaintained research code. That is a real finding, not a shortfall of the search.

### Gaps
- I did not verify whether BoTorch ships TuRBO as library code or only as a tutorial notebook. My recollection is "tutorial", but I could not confirm it in this pass, so treat TuRBO-in-BoTorch as unverified.
- I did not verify whether any OptunaHub package implements a combinatorial-BO method (e.g. a Casmopolitan or BODi sampler). OptunaHub is active (0.5.0, 2026-09-09) and is the most likely place for such a contribution to live, but I did not enumerate its registry.

---

## Q3. Does BoTorch/Ax support binary and categorical variables well in 2026? Specific machinery and limits

### Takeaway
Yes, and the machinery is explicit, documented and current in BoTorch 0.18.x: a Hamming-distance
`CategoricalKernel` inside `MixedSingleTaskGP`, and three acquisition optimizers —
**`optimize_acqf_discrete` (full enumeration of a candidate tensor), `optimize_acqf_discrete_local_search`
(explicitly built and "thoroughly tested" for `{0,1}^d`), and `optimize_acqf_mixed_alternating`
(integer/categorical/continuous alternating search)**. Discrete enumeration of 30,000 candidates is
directly exposed as a one-line call. The known limits are real: `q>1` is sequential-greedy, not joint;
discrete dimensions with more than 20 values get continuously relaxed; and the general-lattice local
search is self-described as alpha.

### Cited Findings

**Enumerating an acquisition function over a candidate set — exposed directly**

- `optimize_acqf_discrete(acq_function, q, choices, max_batch_size=2048, unique=True, return_acq_values=True, X_avoid=None, inequality_constraints=None)`. `choices` is a `num_choices x d` tensor enumerating the candidate set; `X_avoid` points are removed; infeasible choices under `inequality_constraints` are removed; `max_batch_size` caps how many choices are scored at once and "large values can use a lot of memory when the model has a large training set"; for `q>1` candidates are built by **sequential conditioning, not joint optimization**, because the joint set `choices^q` "quickly explodes" — [BoTorch optim API, v0.18.1](https://botorch.readthedocs.io/en/v0.18.1/optim.html); source wording confirmed in [botorch/optim/optimize.py](https://github.com/pytorch/botorch/blob/main/botorch/optim/optimize.py).
- `optimize_acqf_discrete_local_search(acq_function, discrete_choices, q, num_restarts=20, raw_samples=4096, inequality_constraints=None, X_avoid=None, batch_initial_conditions=None, max_batch_size=2048, max_tries=100, unique=True, return_acq_values=True)` — `discrete_choices` is a list of allowed values per dimension; it exists for "large `d` where enumerating the full search space is not feasible"; `q>1` is always sequential greedy with conditioning. **Its own note says arbitrary lattices are supported but it is only "thoroughly tested for `{0, 1}^d`", and the general case is "alpha stage"** — [BoTorch optim API](https://botorch.readthedocs.io/en/v0.18.1/optim.html), [source](https://github.com/pytorch/botorch/blob/main/botorch/optim/optimize.py).
- `optimize_acqf_mixed(acq_function, bounds, q, num_restarts, fixed_features_list, …)` — one `{feature_index: value}` map per optimization run; `q>1` is always sequential greedy; **inter-point constraints are not supported**; `return_best_only=False` is allowed only when `q=1` — [BoTorch optim API](https://botorch.readthedocs.io/en/v0.18.1/optim.html).
- `optimize_acqf_list(acq_function_list, bounds, …)` does sequential-greedy with `X_pending`, has no `q` argument, and delegates to `optimize_acqf_mixed` when `fixed_features_list` is given — [BoTorch optim API](https://botorch.readthedocs.io/en/v0.18.1/optim.html).

**The mixed alternating optimizer and its hard-coded thresholds**

- `optimize_acqf_mixed_alternating(acq_function, bounds, discrete_dims=None, cat_dims=None, options=None, q=1, raw_samples=1024, num_restarts=20, post_processing_func=None, sequential=True, fixed_features=None, inequality_constraints=None, equality_constraints=None, return_acq_values=True)`. It scores initial candidates, picks restarts, then alternates discrete/categorical local search with continuous L-BFGS — [botorch.optim.optimize_mixed source](https://botorch.readthedocs.io/en/stable/_modules/botorch/optim/optimize_mixed.html).
- Module constants: `MAX_ITER_ALTER=64`, `MAX_ITER_DISCRETE=4`, `MAX_ITER_CONT=8`, **`MAX_DISCRETE_VALUES=20`**, `RAW_SAMPLES=1024`, `NUM_RESTARTS=20`, `MAX_BATCH_SIZE=2048`, `MAX_ITER_INIT=100`, `CONVERGENCE_TOL=1e-8`, `DUPLICATE_TOL=1e-6`, **`ALTERNATING_OPTIMIZER_THRESHOLD=10`**, `STD_CONT_PERTURBATION=0.1`, plus `MAX_CHOICES_ENUMERATE=10000` and `MAX_CARDINALITY_FOR_LOCAL_SEARCH=100` which are defined but unused in that file — [optimize_mixed source](https://botorch.readthedocs.io/en/stable/_modules/botorch/optim/optimize_mixed.html).
- `discrete_dims` (ordinal **and binary**): values sorted; the first and last value must equal the dimension's bounds or a `ValueError` is raised; local search moves one step up/down. `cat_dims` (unordered): local search changes one categorical dimension to another allowed value — a **1-Hamming move**; if a dimension has more than `MAX_DISCRETE_VALUES` values the search samples a random subset — [optimize_mixed source](https://botorch.readthedocs.io/en/stable/_modules/botorch/optim/optimize_mixed.html).
- **Continuous relaxation is automatic above the threshold**: in `_setup_continuous_relaxation`, a discrete dimension with more than `max_discrete_values` (default 20) values is treated as continuous and rounded afterwards; dimensions appearing in a constraint are never relaxed; categorical dimensions are not relaxed but subsampled. `should_use_mixed_alternating_optimizer` returns `True` when the product of discrete/categorical value counts exceeds 10, otherwise the caller uses `optimize_acqf_mixed`, which enumerates the discrete combinations — [optimize_mixed source](https://botorch.readthedocs.io/en/stable/_modules/botorch/optim/optimize_mixed.html).
- **Equality constraints may only involve continuous dimensions**: "Equality constraints can only be used with continuous degrees of freedom" — [optimize_mixed source](https://botorch.readthedocs.io/en/stable/_modules/botorch/optim/optimize_mixed.html). This matters for a fixed-cardinality subset constraint (sum of bits = k).
- Helpers: `get_nearest_neighbors` (all unique ±1 index steps), `get_categorical_neighbors` (all single-dimension categorical changes), `get_spray_points`, `discrete_step` (greedy local search, `maxiter_discrete` rounds), `continuous_step` (L-BFGS with discrete dims fixed), `round_discrete_dims` — [optimize_mixed source](https://botorch.readthedocs.io/en/stable/_modules/botorch/optim/optimize_mixed.html).
- `optimize_acqf_homotopy` selects `optimize_acqf_mixed_alternating` when `discrete_dims` and `cat_dims` yield more than 10 combinations — [BoTorch optim API](https://botorch.readthedocs.io/en/v0.18.1/optim.html).

**The mixed-space model**

- `MixedSingleTaskGP(train_X, train_Y, cat_dims, train_Yvar=None, cont_kernel_factory=None, likelihood=None, outcome_transform=DEFAULT, input_transform=None)`. Docstring: "A single-task exact GP model for mixed search spaces." Kernel structure, quoted: `K((x1,c1),(x2,c2)) = K_cont_1(x1,x2) + K_cat_1(c1,c2) + K_cont_2(x1,x2) * K_cat_2(c1,c2)` — a sum-plus-product form, each term with its own lengthscales. The categorical part is a **`CategoricalKernel`, "based on Hamming distances"**. `cat_dims` is "a list of indices corresponding to the columns of the input `X` that should be considered categorical features" (negative indices allowed). Because the model "does not provide gradients for the categorical features", the docstring says acquisition optimization must treat categoricals as discrete and "we recommend using `optimize_acqf_mixed`". Only input transforms that do not transform the categorical dimensions are allowed — [botorch/models/gp_regression_mixed.py](https://github.com/pytorch/botorch/blob/main/botorch/models/gp_regression_mixed.py).
- `MixedSingleTaskGP` accepts `train_Yvar`: "An optional `batch_shape x n x m` tensor of observed measurement noise" — [same source](https://github.com/pytorch/botorch/blob/main/botorch/models/gp_regression_mixed.py).

**Ax 1.x surface for binary variables**

- `ChoiceParameterConfig` docstring: "Allows specifying a discrete dimension of an experiment's search space and internally validates the inputs. Choice parameters can be either ordinal or categorical; this is controlled via the `is_ordered` flag." Allowed `parameter_type` values are `float`, `int`, `str`, **`bool`**; `RangeParameterConfig` allows only `float` and `int`; `ChoiceParameterConfig` also has `dependent_parameters: Mapping[TParameterValue, Sequence[str]] | None` — [ax/api/configs.py](https://github.com/facebook/Ax/blob/main/ax/api/configs.py).
- `TParameterValue = int | float | str | bool`; `TParameterization = Mapping[str, TParameterValue]` — [ax/api/types.py](https://github.com/facebook/Ax/blob/main/ax/api/types.py).
- Third-party criticism to weigh: the CatMADS paper states that BoTorch "does not explicitly distinguish categorical and integer variables" and that integer variables are continuously relaxed then rounded — [CatMADS, arXiv 2506.06937](https://arxiv.org/pdf/2506.06937). **This conflicts with the BoTorch source**, which has separate `discrete_dims`/`cat_dims` paths, a dedicated `CategoricalKernel`, and relaxation only above a 20-value threshold. The criticism is better read as applying to default Ax/BoTorch behaviour on high-cardinality integers, not to the library's full capability.

### Inferences
- For a length-7–30 binary vector the right BoTorch combination is: `SingleTaskGP` with `train_Yvar` (or `MixedSingleTaskGP` with all bit columns in `cat_dims`, which gives the Hamming kernel) plus **`optimize_acqf_discrete` over the enumerated candidate tensor** when the space is ≤30,000, and `optimize_acqf_discrete_local_search` when it is not. The latter is the one function in this ecosystem that was built specifically for `{0,1}^d`.
- The `ALTERNATING_OPTIMIZER_THRESHOLD=10` and `MAX_DISCRETE_VALUES=20` constants mean a 30-bit space will not be enumerated by `optimize_acqf_mixed` by default; but a binary dimension has only 2 values, so no relaxation is triggered per dimension — relaxation risk here is low, and the real risk is the local search's greedy 1-Hamming neighbourhood.
- `q>1` batch selection is everywhere sequential-greedy in the discrete paths. If the user wants a batch of subsets per round, they will get greedy-conditioned batches, not jointly optimal ones. For a noisy simulation objective that is usually acceptable, but it should be stated.
- The "equality constraints only on continuous dimensions" restriction means a hard cardinality constraint (|subset| = k) cannot be passed as an equality constraint to the mixed optimizer; it must be imposed by **pre-filtering the enumerated `choices` tensor** — which is trivial in the enumerable regime and is an argument for `optimize_acqf_discrete`.

### Gaps
- I did not confirm from primary docs whether Ax 1.x automatically routes a `bool`/2-value `ChoiceParameterConfig` to `MixedSingleTaskGP`/`CategoricalKernel` or to one-hot plus a continuous kernel. **`OneHotToNumeric` was named in the assignment and I did not verify its current existence, module path or behaviour in BoTorch 0.18.x** — treat it as unverified.
- I did not verify Ax's `Models`/`GenerationStrategy`-level control over which acquisition optimizer is used for a discrete space, nor whether Ax exposes `optimize_acqf_discrete` to users of the `Client` API.

---

## Q4. Noise handling: which packages let you declare a known per-evaluation observation standard error?

### Takeaway
**Two do it cleanly: BoTorch (`train_Yvar`) and Ax (`(mean, sem)` in `raw_data`).** Optuna does
**not** accept a per-observation noise value — its GP learns one homoscedastic noise unless you pin it
to the floor with `deterministic_objective=True`. SMAC3 handles noise by **repeating evaluations with
different seeds**, not by accepting a declared SE. BoTorch ships the noise-aware acquisition
functions the assignment asked about, including `qLogNoisyExpectedImprovement`, `qKnowledgeGradient`,
MES variants and (in a submodule) `qJointEntropySearch`.

### Cited Findings

**BoTorch — exact per-point known noise**

- `SingleTaskGP` is documented as "A single-task exact GP model, supporting both known and inferred noise levels"; "noise levels can be provided to `SingleTaskGP` as `train_Yvar`"; `train_Yvar` is "An optional `batch_shape x n x m` tensor of observed measurement noise"; and the likelihood is "a `GaussianLikelihood` with inferred noise level if `train_Yvar` is None, and a **`FixedNoiseGaussianLikelihood` with the given noise observations if `train_Yvar` is not None**". The docstring's own examples are `inferred_noise_model = SingleTaskGP(train_X, train_Y)`, `observed_noise_model = SingleTaskGP(train_X, train_Y, train_Yvar)` with `train_Yvar = torch.full_like(train_Y, 0.2)`, and a noise-free variant with `train_Yvar = torch.full_like(train_Y, 1e-6)` — [botorch/models/gp_regression.py](https://github.com/pytorch/botorch/blob/main/botorch/models/gp_regression.py).
- So `FixedNoiseGaussianLikelihood` is **not removed — it is the mechanism `train_Yvar` switches on.** What was deprecated is the separate *model* classes: BoTorch marks `FixedNoiseMultiTaskGP` deprecated with "Please use `MultiTaskGP` with `train_Yvar` instead. Will be removed in a future release (~v0.10)", and a changelog entry reads "Deprecate `FixedNoiseMultiTaskGP`; allow `train_Yvar` optionally in `MultiTaskGP`" — [BoTorch model source](https://botorch.readthedocs.io/en/stable/_modules/botorch/models/model.html), [BoTorch changelog](https://github.com/pytorch/botorch/blob/main/CHANGELOG.md). **The idiom in 2026 is `train_Yvar=`, not a `FixedNoise*` class.**
- `SACGP` documents "If None, we use an inferred noise likelihood" and `LCEMGP` documents that a `FixedNoiseGaussianLikelihood` is used when `train_Yvar` is provided — [BoTorch models API](https://botorch.readthedocs.io/en/v0.18.1/models.html).
- SAAS helper takes "Optional tensor of shape n x 1 with observed noise, inferred if None" — [BoTorch fit API](https://botorch.readthedocs.io/en/latest/fit.html).

**BoTorch — noise-aware acquisition functions exported in 0.18.x**

- From `botorch.acquisition.__all__`: analytic `ExpectedImprovement`, `LogExpectedImprovement`, **`NoisyExpectedImprovement`, `LogNoisyExpectedImprovement`**, `ConstrainedExpectedImprovement`, `PosteriorMean`, `PosteriorStandardDeviation`, `ProbabilityOfImprovement`, `UpperConfidenceBound`, `qAnalyticProbabilityOfImprovement`; MC `qExpectedImprovement`, **`qNoisyExpectedImprovement`**, `qProbabilityOfImprovement`, `qUpperConfidenceBound`, `qLowerConfidenceBound`, `qSimpleRegret`, `qPosteriorStandardDeviation`; LogEI `qLogExpectedImprovement`, **`qLogNoisyExpectedImprovement`**; knowledge gradient **`qKnowledgeGradient`, `qMultiFidelityKnowledgeGradient`**; entropy search **`qMaxValueEntropy`, `qLowerBoundMaxValueEntropy`, `qMultiFidelityMaxValueEntropy`, `qMultiFidelityLowerBoundMaxValueEntropy`**; active learning `qNegIntegratedPosteriorVariance`, `qBayesianActiveLearningByDisagreement`; plus `qMultiStepLookahead`, `FixedFeatureAcquisitionFunction`, `PriorGuidedAcquisitionFunction`, `ProximalAcquisitionFunction`, `OneShotAcquisitionFunction` — [botorch/acquisition/__init__.py](https://github.com/pytorch/botorch/blob/main/botorch/acquisition/__init__.py).
- **`qJointEntropySearch` is not in the top-level `__all__` but exists** as `class qJointEntropySearch(AcquisitionFunction, MCSamplerMixin)` in `botorch/acquisition/joint_entropy_search.py` — import it from the submodule — [botorch/acquisition/joint_entropy_search.py](https://github.com/pytorch/botorch/blob/main/botorch/acquisition/joint_entropy_search.py).
- No Thompson-sampling class and no discrete-specific acquisition function are exported at top level — [botorch/acquisition/__init__.py](https://github.com/pytorch/botorch/blob/main/botorch/acquisition/__init__.py).

**Ax — a first-class SEM field**

- `TOutcome = Mapping[str, float | tuple[float, float]]`, with the comment `# Metric name => mean | (mean, sem)`. So `client.complete_trial(trial_index, raw_data={"objective": (mean, sem)})` declares a known standard error per evaluation — [ax/api/types.py](https://github.com/facebook/Ax/blob/main/ax/api/types.py).
- `Client.complete_trial(trial_index: int, raw_data: TOutcome | None = None, progression: int | None = None)` and `Client.attach_data(trial_index, raw_data: TOutcome, progression=None)`; `attach_data`'s docstring notes "Missing metrics are allowed, and unexpected metric values will be added to the Experiment as tracking metrics" — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- `Client.predict(points) -> list[dict[str, tuple[float, float]]]` returns a predicted **mean and SEM per metric** — useful for the "select on one seed, score on another" workflow in Q8 — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).

**Optuna — no declared noise, one learned noise**

- Optuna's internal GP marks categorical dimensions with an `is_categorical` flag and converts their squared difference to a 0/1 indicator — "if x1[i] is categorical, sqd(x1, x2)[i] = int(x1[i] != x2[i])" and "Note that the distance for categorical parameters is the Hamming distance" — then applies the same Matérn 5/2 kernel to the weighted sum: `Matern52Kernel.apply(sqdist) * self.kernel_scale` — [optuna/_gp/gp.py](https://github.com/optuna/optuna/blob/master/optuna/_gp/gp.py).
- Noise is **learned** by default; with `deterministic_objective=True` it is pinned to `minimum_noise`: `self.noise_var = torch.tensor(minimum_noise) if deterministic_objective else minimum_noise + torch.exp(raw_params_opt_tensor[n_params + 1])`. `minimum_noise` is a function argument, not a user-facing per-observation value, and there is no user-facing argument to set the noise value — [optuna/_gp/gp.py](https://github.com/optuna/optuna/blob/master/optuna/_gp/gp.py).
- `GPSampler.__init__(self, *, seed: int | None = None, independent_sampler: BaseSampler | None = None, n_startup_trials: int = 10, deterministic_objective: bool = False, …)`. Its docs say the acquisition function is **q-batch log expected improvement (qLogEI)** for single-objective optimization, and that acquisition optimization uses "gradient ascent using l-BFGS-B for continuous parameters, and line search or exhaustive search for each discrete parameter independently" — [optuna/samplers/_gp/sampler.py](https://github.com/optuna/optuna/blob/master/optuna/samplers/_gp/sampler.py), [GPSampler docs](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.GPSampler.html). The published kernel description is "Matérn kernel with nu=2.5" with ARD, hyperparameters by marginal-likelihood maximization.

**SMAC3 — noise by repetition, not by declaration**

- `Scenario.deterministic: bool = False`, docstring: "If True, only one seed is passed to the target function, assuming deterministic (noise-free) behavior. Otherwise, multiple seeds are passed (if `n_seeds` > 1) to enable repeated evaluations. For non-deterministic functions, users must specify intensification parameters (e.g. `max_config_calls`, `n_seeds`) to ensure reliable performance estimates and optionally model noise in the Gaussian Process surrogate." Also `n_trials: int = 100`, `seed: int = 0` ("If seed is -1, SMAC will generate a random seed"), `instances`, `min_budget`/`max_budget`, `objectives: str | list[str] = "cost"` — [smac/scenario.py](https://github.com/automl/SMAC3/blob/main/smac/scenario.py).
- Older SMAC documentation states the same mechanism: a non-deterministic target means "SMAC will then execute promising configurations multiple times, using different seeds" — [SMAC v2 quickstart, UBC](https://www.cs.ubc.ca/labs/algorithms/Projects/SMAC/v2.10.02/quickstart.html). The random-forest surrogate is chosen because "Random Forests natively handle larger, categorical and conditional configuration spaces" — [HPO survey, arXiv 2007.15745](https://arxiv.org/pdf/2007.15745).

**Nevergrad — noise is a first-class regime, but not a declared SE**

- Nevergrad's docs recommend TBPSA, which is "excellent for problems corrupted by noise, in particular overparametrized (neural) ones"; in the noisy setting TBPSA "usually recommends, at the end of the run, the center of the Gaussian as an approximation of the optimum" — [Nevergrad optimization docs](https://github.com/facebookresearch/nevergrad/blob/main/docs/optimization.md), [Versatile Black-Box Optimization, arXiv 2004.14014](https://arxiv.org/pdf/2004.14014).
- Discrete variables are handled "through the softmax function (which converts a discrete problem into a noisy, continuous one) or through discretization of continuous variables", with `SoftmaxCategorical` suggested when unsure; an "ordered" choice maps to `TransitionChoice` — [Nevergrad optimization docs](https://github.com/facebookresearch/nevergrad/blob/main/docs/optimization.md), [Hydra Nevergrad sweeper docs](https://hydra.cc/docs/plugins/nevergrad_sweeper).

**HEBO — typed design space including `bool`**

- `DesignSpace` registers parameter types `num`, `pow`, `pow_int`, `int_exponent`, `int`, `step_int`, **`cat`**, **`bool`**, and users can register their own — [HEBO design_space.py](https://github.com/huawei-noah/HEBO/blob/master/HEBO/hebo/design_space/design_space.py). API is `opt.suggest(n_suggestions=k)` / `opt.observe(rec, y)` with pandas DataFrames — [HEBO README](https://github.com/huawei-noah/HEBO/blob/master/HEBO/README.md).

**Trieste — explicit categorical search spaces**

- `CategoricalSearchSpace` subclasses `GeneralDiscreteSearchSpace` and `HasOneHotEncoder`; categories are given as a count (`5`) or as name lists (`["Red","Green","Blue"]`), stored as **numeric indices, not one-hot**; one-hot encoding happens only via the `one_hot_encoder` property, where "binary categories are left unchanged instead of adding an unnecessary second feature" and >2-category dimensions use `tf_keras.layers.CategoryEncoding(output_mode="one_hot")`. `DiscreteSearchSpace` is a finite set of D-dimensional points with a Cartesian `product`. `TaggedProductSearchSpace` combines `Box`/`DiscreteSearchSpace`/`CategoricalSearchSpace` subspaces and is "useful for defining mixed search spaces"; helpers include `one_hot_encoder(space)`, `one_hot_encoded_space(space)`, `cast_encoder` — [trieste/space.py](https://github.com/secondmind-labs/trieste/blob/develop/trieste/space.py).

### Inferences
- The exact-binomial-SE workflow the user described maps one-to-one onto BoTorch's `train_Yvar` and Ax's `(mean, sem)`. Everything else in this landscape either learns one noise level or averages repeats. That is the single strongest reason to pick Ax/BoTorch for this problem.
- `qNoisyExpectedImprovement` / `qLogNoisyExpectedImprovement` are the right default acquisition here: they are defined against the noisy observed data rather than a noise-free incumbent, so they do not need an `f_best` that the noise makes meaningless. `qKnowledgeGradient` is the theoretically correct choice for a terminal-recommendation ("pick the best subset at the end") objective but is a one-shot/nested optimization and far more expensive.
- Optuna's GP uses a Hamming distance for categoricals, which is the same geometry COMBO/Casmopolitan argue for — so Optuna's GPSampler is a reasonable, cheap second implementation for a cross-check, but it cannot consume the known SE.

### Gaps
- I did not verify how Ax propagates a user-supplied SEM into the BoTorch model (i.e. whether it becomes `train_Yvar` directly, or is transformed by `StandardizeY`/winsorization first). This matters: if Ax rescales outcomes, the SEM scaling must follow, and I did not confirm it does.
- I did not verify whether `qKnowledgeGradient` can be used with `optimize_acqf_discrete` (one-shot acquisition functions have internal `q`-augmented candidate structure, which may be incompatible with pure enumeration). Treat KG-over-enumerated-candidates as unverified.

---

## Q5. Derivative-free and trust-region optimization for noisy objectives: binary and noise support

### Takeaway
**NOMAD is the only one of these with genuine binary-variable support plus a maintained 2026
release** (`PyNomadBBO` 4.6.0, 2026-08-26; types R/B/I; categorical only via the new NomadBBO
interface). **Py-BOBYQA and DFO-LS have the best explicit noise handling** (`objfun_has_noise`,
`nsamples` averaging, noise-aware restarts) but are **continuous-only**. **RBFOpt handles
mixed-integer** variables and had a 2025 release. **pySOT and SnobFit are stale.** `scipy`'s
`differential_evolution` has an `integrality` argument, which is the cheapest off-the-shelf way to
optimize a binary vector, but it has no noise model.

### Cited Findings

**NOMAD 4 (MADS)**

- Licence **LGPL-3.0**; "NOMAD is a C++ implementation of the Mesh Adaptive Direct Search (MADS) algorithm, designed for constrained optimization of black-box functions", based on Audet & Hare, *Derivative-Free and Blackbox Optimization* (Springer 2017), with **"A second edition of the book has been released in 2026"** — [NOMAD README](https://github.com/bbopt/nomad/blob/master/README.md). Repo `bbopt/nomad` pushed **2026-10-16**, 163 stars — [github.com/bbopt/nomad](https://github.com/bbopt/nomad).
- Variable types: "Input types `t` are values in `R, B, I`. `R` is for real/continuous variables, **`B` for binary variables**, and `I` for integer variables." Granularity: "For integers and binary variables the granularity is automatically set to one"; real variables have granularity 0; `GRANULARITY` can be set per coordinate or by range — [NOMAD usage guide](https://nomad-4-user-guide.readthedocs.io/en/latest/HowToUseNomad.html), [NOMAD advanced functionalities](https://nomad-4-user-guide.readthedocs.io/en/latest/AdvancedFunctionalities.html).
- **Categorical variables — two conflicting statements in the same documentation set.** `HowToUseNomad.rst` (current master) says: "Categorical variables are supported in NOMAD 4 only through the **NomadBBO** python interface [AuDiHHLeDTr2025]" — [NOMAD usage guide source](https://github.com/bbopt/nomad/blob/master/doc/user_guide/source/HowToUseNomad.rst). The published `AdvancedFunctionalities` page still says "Categorical variables are not yet supported in NOMAD 4 but are available in NOMAD 3. Some work by a PhD student is currently being done to reintroduce this feature in NOMAD 4" — [NOMAD advanced functionalities](https://nomad-4-user-guide.readthedocs.io/en/master/AdvancedFunctionalities.html). The master-branch statement is the newer one.
- NomadBBO is described as "a Python framework for constrained mixed-variable blackbox optimization" that "aims to bridge … the accessibility and flexibility of a Python library with the algorithmic guarantees and performance of Nomad", with categorical-variable support, a compiled backend and inequality constraints in its feature table — [NomadBBO, arXiv 2609.19333](https://arxiv.org/pdf/2609.19333).
- **Installation, verified:** `PyNomadBBO` **4.6.0, uploaded 2026-08-26**, "Python interface to Nomad 4", homepage `github.com/bbopt/nomad`, 4 releases total (4.5.0 2025-01-29, 4.5.1 2025-05-26, 4.6.0 2026-08-26) — [PyPI PyNomadBBO](https://pypi.org/project/PyNomadBBO/). **Trap: the PyPI package named `PyNomad` (0.1.7.post1, 2016-03-23) is unrelated — "Routines for accessing a self-hosted local copy of the USNO NOMAD stellar catalog"** — [PyPI PyNomad](https://pypi.org/project/PyNomad/). A third-party alternative interface, `nomadlad` 1.1.0 (2025-09-02, LGPL-3.0), describes itself as "an alternative to the PyNomadBBO package" — [PyPI nomadlad](https://pypi.org/project/nomadlad/).
- Constraint types: `EB` (extreme barrier, always-satisfied), `PB`/`F`/`CSTR` (progressive barrier / filter, relaxable), and since version 4.6 `EQPB` equality constraints, where "With EQPB, Mads-PIP works better than Mads-PB" — [NOMAD usage guide](https://nomad-4-user-guide.readthedocs.io/en/latest/HowToUseNomad.html).
- **Noise:** I found **no** documented stochastic/noisy-objective algorithm or option in the NOMAD 4 pages I read (no StoMADS, no repeated-evaluation option, no noise-aware surrogate). `SEED` controls poll directions, not noise. The closest feature, DiscoMADS, targets hidden constraints and discontinuities, not noise — [NOMAD advanced functionalities](https://nomad-4-user-guide.readthedocs.io/en/latest/AdvancedFunctionalities.html).
- CatMADS (the categorical MADS extension) is "built on top of the NOMAD software … a C++ implementation of the MADS algorithm with many extensions such as G-MADS" — [CatMADS, arXiv 2506.06937](https://arxiv.org/pdf/2506.06937). A further 2026 paper covers surrogate-based categorical neighbourhoods for mixed-variable blackbox optimization — [arXiv 2603.27839](https://arxiv.org/pdf/2603.27839).

**Py-BOBYQA**

- Latest release **1.5.0, 2024-09-16**; **GPL-3.0-or-later**; repo `numericalalgorithmsgroup/pybobyqa` pushed 2026-07-22 (last commit a dependabot merge), 99 stars — [PyPI Py-BOBYQA](https://pypi.org/project/Py-BOBYQA/), [github.com/numericalalgorithmsgroup/pybobyqa](https://github.com/numericalalgorithmsgroup/pybobyqa). **No release since 2024 — flagged.**
- Noise options: `objfun_has_noise=True` tells it repeated calls at the same point may differ and "sets some sensible default parameters (including using multiple restarts)"; with noise the default number of interpolation points becomes `(n+1)(n+2)/2` instead of `2n+1`, and "larger values are particularly useful for noisy problems"; `nsamples(delta, rho, iter, nrestarts)` sets how many times to evaluate at each point and is "only applicable for objectives with stochastic noise"; `soln.nf` and `soln.nx` differ when sample averaging is used. `seek_global_minimum` is a separate restart heuristic requiring both bounds, with no guarantee. The documented worked example uses 1% multiplicative Gaussian noise: without the flag it fails to reach the solution, with the flag it recovers it. **No numerical noise-tolerance threshold is stated.** The user guide describes only continuous variables with bounds and convex constraints — **it says nothing about integer, binary or categorical variables** — [Py-BOBYQA user guide](https://numericalalgorithmsgroup.github.io/pybobyqa/build/html/userguide.html).

**DFO-LS**

- Latest release **1.6.5, 2026-03-23** (7 releases in 2025–2026); **GPL-3.0-or-later**; repo pushed 2026-10-19, 49 stars — [PyPI DFO-LS](https://pypi.org/project/DFO-LS/), [github.com/numericalalgorithmsgroup/dfols](https://github.com/numericalalgorithmsgroup/dfols). **Actively maintained.**
- `dfols.solve(..., nsamples=None, user_params=None, objfun_has_noise=False, ...)`. `objfun_has_noise` is "a flag to indicate whether or not `objfun` has stochastic noise; i.e. will calling `objfun(x)` multiple times at the same value of `x` give different results? This is used to set some sensible default parameters (including using multiple restarts)". `nsamples` is "only applicable for objectives with stochastic noise, when averaging multiple evaluations at the same point produces a more accurate value"; default is no averaging. The docs state "derivative-free algorithms such as DFO-LS are particularly useful when `objfun` has noise", and their 1%-Gaussian-noise example shows SciPy's derivative-based solver "unable to make any progress" where DFO-LS succeeds — [DFO-LS user guide](https://github.com/numericalalgorithmsgroup/dfols/blob/master/docs/userguide.rst). DFO-LS solves nonlinear **least-squares** problems, which is a structural mismatch with a scalar subset-selection objective unless the objective can be written as a sum of squared residuals.

**RBFOpt**

- Latest release **4.3.0, 2025-03-30**, Revised BSD; repo `coin-or/rbfopt` pushed/last commit 2025-03-30, 196 stars — [PyPI rbfopt](https://pypi.org/project/rbfopt/), [github.com/coin-or/rbfopt](https://github.com/coin-or/rbfopt). The README describes solving "nonconvex mixed-integer nonlinear programs" with subproblems where variables are "constrained to be integer", solved with open-source solvers (e.g. Ipopt), and cites a paper on methods "for mixed-variable problems" — [RBFOpt README](https://github.com/coin-or/rbfopt/blob/master/README.rst). **Integer (hence binary) variables are supported.** Only one release in 2025–2026, none in 2026 — borderline, not yet stale.

**pySOT, SnobFit**

- pySOT: last release **0.3.3, 2020-06-22**, repo last commit 2021-10-27 — **stale** — [PyPI pySOT](https://pypi.org/project/pySOT/).
- SnobFit (`SQSnobFit`): last release **0.4.5, 2020-11-30**, PyPI licence classifier "Other/Proprietary License" — **stale and licence-encumbered** — [PyPI SQSnobFit](https://pypi.org/project/SQSnobFit/).

**SciPy and NLopt**

- `scipy` **1.18.1, 2026-08-21** (18 releases in 2025–2026) — [PyPI scipy](https://pypi.org/project/scipy/).
- `scipy.optimize.differential_evolution(..., rng=None, workers=1, constraints=(), x0=None, *, integrality=None, vectorized=False)` — `integrality` is a 1-D array, and the docs refer to "bounds, any constraints (**including integrality constraints**)"; `workers` parallelizes population evaluation (forcing `updating='deferred'`); the old `seed` parameter is being transitioned to `rng` via `@_transition_to_rng("seed", position_num=9)` — [scipy/optimize/_differentialevolution.py](https://github.com/scipy/scipy/blob/main/scipy/optimize/_differentialevolution.py). **So a binary vector is expressible as `bounds=[(0,1)]*d, integrality=[True]*d`.** No noise model, and differential evolution needs many evaluations.
- `scipy.optimize.direct` exposes `locally_biased` and standard DIRECT options; **its source contains no integer, discrete or noise handling** — [scipy/optimize/_direct_py.py](https://github.com/scipy/scipy/blob/main/scipy/optimize/_direct_py.py). DIRECT is continuous-only and assumes a deterministic objective.
- `nlopt` **2.11.0, 2026-07-17**, MIT, repo `stevengj/nlopt` pushed 2026-10-17, last commit 2026-10-17, 2,287 stars — **actively maintained** — [PyPI nlopt](https://pypi.org/project/nlopt/), [github.com/stevengj/nlopt](https://github.com/stevengj/nlopt). Its README contains **no mention of integer, discrete or noisy-objective support** — [NLopt README](https://github.com/stevengj/nlopt/blob/master/README.md).

### Inferences
- The DFO family splits cleanly for this problem: **noise-aware but continuous** (Py-BOBYQA, DFO-LS) versus **discrete-capable but noise-agnostic** (NOMAD binary variables, RBFOpt integers, `differential_evolution` integrality). Nothing in the DFO column does both well. That asymmetry is the main argument for BO over DFO here.
- MADS on `{0,1}^d` degenerates toward coordinate/pattern search over bits: with granularity 1 on a binary variable the mesh is the vertex set, so NOMAD's poll becomes a Hamming-neighbourhood search. That is a reasonable, cheap local method and a sensible baseline, but it has no mechanism to exploit a declared SE.
- Py-BOBYQA/DFO-LS `nsamples` averaging is conceptually the same move as raising the Monte Carlo sample count per evaluation. If the user controls the MC budget per evaluation, they already have this lever and do not need the solver to provide it.

### Gaps
- NOMAD's handling of a genuinely stochastic objective is **unverified**. I read the usage and advanced-functionality pages and found no noise feature; I did not read the full NOMAD parameter list, and the StoMADS line of work (Audet, Dzahini, Kokkolaras, Le Digabel) may be implemented under a name I did not search for.
- Py-BOBYQA's licence is GPL-3.0-or-later per its PyPI classifier; I did not find a licence statement in the user guide itself. Same for DFO-LS. **GPL is a distribution constraint if any of this is to ship inside a product.**
- NLopt's lack of integer support is inferred from the absence of any mention in its README, not from a positive statement. Unverified.

---

## Q6. GPU: who actually uses it, and does it matter at this size?

### Takeaway
Only the PyTorch stack (BoTorch/GPyTorch, and Ax through it) and Vizier's JAX backend are
GPU-capable in any real sense, and **at 10^2–10^4 candidates with 10^1–10^3 observations the GPU is
irrelevant to wall-clock**: a 30,000 × 30 acquisition evaluation against a GP with a few hundred
training points is milliseconds on CPU.

### Cited Findings
- BoTorch is written "for highly parallelized modern hardware (e.g. GPUs) using device-agnostic code" — [BoTorch README](https://github.com/pytorch/botorch/blob/main/README.md). It is built on GPyTorch (MIT, 1.15.2, 2026-02-28) and `linear-operator` (0.6.1, 2026-02-27) — [PyPI gpytorch](https://pypi.org/project/gpytorch/), [PyPI linear-operator](https://pypi.org/project/linear-operator/).
- Ax exposes device selection at the generation-strategy level: `Client.configure_generation_strategy(..., torch_device=None, ...)` — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- BoTorch's discrete optimizers expose the memory/throughput knob rather than a device knob: `max_batch_size=2048` caps how many choices are scored at once, and "large values can use a lot of memory when the model has a large training set"; `return_acq_values=False` avoids "a memory-intensive joint acquisition evaluation" — [BoTorch optim API](https://botorch.readthedocs.io/en/v0.18.1/optim.html).
- Vizier's quick start is `pip install google-vizier[jax]` for a "JAX-based Bayesian Optimizer"; the README **does not mention GPU** — [Vizier README](https://github.com/google/vizier/blob/main/README.md).
- Trieste is TensorFlow/GPflow-based (`gpflow` 2.11.2, 2026-10-14), so it inherits TensorFlow's GPU support — [PyPI trieste](https://pypi.org/project/trieste/), [PyPI gpflow](https://pypi.org/project/gpflow/).
- Optuna's GP path is implemented in Torch (`optuna/_gp/gp.py` uses `torch.float64` tensors and L-BFGS-B) but is written for small-n CPU use; the `GPSampler` docs describe no device option — [optuna/_gp/gp.py](https://github.com/optuna/optuna/blob/master/optuna/_gp/gp.py), [GPSampler docs](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.GPSampler.html).
- SMAC3 (random forest), Nevergrad, NOMAD, Py-BOBYQA, DFO-LS, RBFOpt, pySOT, SnobFit, NLopt and SciPy are CPU-only by construction — none of their documentation above mentions GPU use.

### Inferences
- GPU matters for BoTorch when the training set reaches thousands of points, when fully Bayesian (NUTS/SAAS) models are refit each round, or when `num_restarts × raw_samples` for continuous acquisition optimization is large. None of those apply to a 7–30-bit subset problem with an expensive simulator, where the evaluation budget is the bottleneck by orders of magnitude.
- The one place a GPU could pay for itself is `qKnowledgeGradient` or fully Bayesian SAAS refits, both of which are 10–100× more expensive than `qLogNEI` with MAP hyperparameters. Even then, the simulator will dominate.
- I found **no** evidence of a new 2025–2026 GPU-accelerated GP library displacing GPyTorch. Absence of evidence here, not evidence of absence (see gaps).

### Gaps
- I did not search specifically for 2025–2026 GPU GP libraries beyond the GPyTorch/GPflow/JAX ecosystem (e.g. GPJax, or any newer entrant). Unverified.

---

## Q7. Where does BO beat plain enumeration with a good budget-allocation rule, at 128–30,000 candidates?

### Takeaway
**I found no primary source that benchmarks BO against enumeration-plus-budget-allocation on a small
noisy discrete space.** What the literature does establish is that (a) when the space is small enough
to score the acquisition function everywhere, acquisition optimization is trivial — so the *only*
thing BO is contributing is the surrogate's ability to pool information across candidates; and (b)
this exact setting is the classical **ranking-and-selection / best-arm-identification** problem, for
which Optimal Computing Budget Allocation and its relatives are the established rules. The crossover
is therefore governed by whether the surrogate's borrowing of strength across candidates is worth more
than the simplicity of allocating replications directly.

### Cited Findings
- Daulton et al. state the regime boundary explicitly: "If the discrete search space has low enough cardinality that the AF can be evaluated at every discrete element, then acquisition optimization can be solved trivially" — [Bayesian Optimization over Discrete and Mixed Spaces via Probabilistic Reparameterization, arXiv 2210.10199](https://arxiv.org/pdf/2210.10199).
- BO's own literature frames the small-finite-domain case as equivalent to ranking and selection: a BO review notes that with Bayesian surrogate models "this is equivalent to performing Bayesian optimization on a finite, discrete domain", and includes a terminal recommendation step — [Recent Advances in Bayesian Optimization, ACM CSUR](https://dl.acm.org/doi/10.1145/3582078).
- Optimal Computing Budget Allocation "uses a fixed allocation ratio that asymptotically optimizes the Large Deviation rate" to allocate budget across alternatives; the same source notes GP-based methods "can struggle when the noise is heteroscedastic" — [Optimizing Input Data Collection for Ranking and Selection, arXiv 2502.16659](https://arxiv.org/pdf/2502.16659).
- The counterpart justification for BO is explicitly the infeasibility of enumeration: in a large discrete compression space, "the search space is large and fully discrete, making exhaustive enumeration infeasible" — [AutoQRA, arXiv 2602.22268](https://arxiv.org/html/2602.22268).
- An AI-for-ranking-and-selection line of work exists and treats the finite-alternative noisy-selection problem as its own field — [AlphaRank, arXiv 2402.00907](https://arxiv.org/pdf/2402.00907).
- BoTorch's own API makes the enumeration branch first-class rather than a fallback: `optimize_acqf_discrete(choices=...)` with `max_batch_size=2048` is the documented way to handle an enumerable candidate set — [BoTorch optim API](https://botorch.readthedocs.io/en/v0.18.1/optim.html).

### Inferences (clearly marked — these are reasoning, not sourced results)
- **The crossover condition is a ratio, not a cardinality.** Let `N` be the number of candidates, `B` the total number of simulator evaluations affordable, and `r` the replications needed per candidate to resolve the differences that matter (`r ≈ (z·σ/Δ)²` for a target gap `Δ` and per-evaluation SD `σ`). Plain enumeration with a budget rule needs `B ≳ N·r₀` with a small screening `r₀`, then concentrates the rest. **BO is only interesting when `B < N`** — when you cannot afford even one evaluation per candidate. At `N = 128` and any realistic simulation budget, `B ≫ N` and enumeration with OCBA-style allocation (or sequential halving) will beat BO, be simpler, and give an unbiased final estimate. At `N = 30,000` with `B` in the low thousands, `B ≪ N` and the surrogate is doing real work.
- **The second condition is smoothness in Hamming space.** BO's advantage is entirely the surrogate's ability to predict an unevaluated subset from its neighbours. If the objective is roughly additive or low-order in the bits (which a Hamming/`CategoricalKernel` GP captures), BO generalizes across the space and `B ≪ N` is fine. If the objective is adversarial in the bits (strong high-order interactions, near-random over Hamming neighbourhoods), the GP learns nothing transferable and BO degenerates to sampling with extra machinery and extra bias risk.
- **A hybrid dominates both in the middle band.** Score all `N` candidates with the GP posterior (free, by enumeration), take the top `m` (say 20–100), then run an explicit ranking-and-selection budget rule over that shortlist to pick the winner with a stated confidence. This uses the surrogate for screening and a clean allocation rule for the terminal decision, and avoids relying on a GP posterior for the final claim.
- **Noise makes the final claim, not the search, the hard part.** With a declared binomial SE, the "winner's curse" at the selection step is the dominant bias; see Q8.

### Gaps
- **No primary source gives a numeric crossover.** I searched for a head-to-head benchmark of BO versus enumeration on small noisy discrete spaces and found none. The quantitative statements above are inference, and the report should label them as such.
- I did not find a 2025–2026 empirical paper comparing OCBA-style allocation against GP-based BO on finite discrete alternatives. If the report needs that, it is an open search target.

---

## Q8. Reproducibility and seeding: selecting on one seed and scoring on another

### Takeaway
**Ax is the best-instrumented for this**: a client-level `random_seed`, a separate
`initialization_random_seed`, an `attach_trial`/`attach_data` path that lets you feed in results
computed however you like, and a `predict()` that returns mean and SEM for arbitrary points — so the
select/score split can be built explicitly. Optuna's `GPSampler(seed=...)` and SMAC's
`Scenario(seed=...)` are reproducible but assume one objective stream. **No library I found has a
built-in "select on seed A, evaluate on seed B" facility**; it has to be constructed by the user.

### Cited Findings
- `Client.__init__(storage_config=None, random_seed: int | None = None)`; the docstring says that if it is not provided "the random seed will not be set, leading to potentially different results on different runs", and `get_next_trials` applies it when generating candidates — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- `Client.configure_generation_strategy(method="fast", initialization_budget=None, initialization_random_seed=None, initialize_with_center=True, use_existing_trials_for_initialization=True, min_observed_initialization_trials=None, allow_exceeding_initialization_budget=False, torch_device=None, simplify_parameter_changes=False, fit_tracking_metrics=True)` — `initialization_random_seed` is documented as "Random seed for initialization. If None, no seed will be set" — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- `Client.attach_trial(parameters, arm_name=None) -> int` and `Client.attach_baseline(...)` let arbitrary externally chosen points be registered; `Client.attach_data(trial_index, raw_data, progression=None)` attaches results separately from trial completion — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- `Client.get_best_parameterization(use_model_predictions=True)` — the flag controls whether the reported best point comes from the **model prediction** or from the raw observed data; it raises `UnsupportedError` for multi-objective problems. `Client.predict(points) -> list[dict[str, tuple[float, float]]]` returns mean and SEM per metric — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- `Client.save_to_json_file(filepath="ax_client_snapshot.json")` / `load_from_json_file` / `load_from_database` give full experiment state serialization — [ax/api/client.py](https://github.com/facebook/Ax/blob/main/ax/api/client.py).
- Optuna: `GPSampler(*, seed=None, independent_sampler=None, n_startup_trials=10, deterministic_objective=False, ...)` with "Random seed to initialize internal random number generator. Defaults to `None` (a seed is picked randomly)" and "Sampler used for initial sampling (for the first `n_startup_trials` trials) … (a random sampler with the same `seed` is used)" — [optuna/samplers/_gp/sampler.py](https://github.com/optuna/optuna/blob/master/optuna/samplers/_gp/sampler.py).
- SMAC: `Scenario.seed: int = 0`, "The seed is used to make results reproducible. If seed is -1, SMAC will generate a random seed"; and `deterministic=False` passes **multiple seeds** per configuration so repeated evaluations are stored separately — the seed is part of the run-history key, so repeated noisy runs of one configuration are distinguishable — [smac/scenario.py](https://github.com/automl/SMAC3/blob/main/smac/scenario.py), [SMAC3 issue thread on run history](https://bitbucket.org/aadfreiburg/smac3/issue/4).
- SciPy: `differential_evolution` is migrating `seed` → `rng` via `@_transition_to_rng("seed", position_num=9)`, and `rng` accepts a `numpy.random.Generator` or anything `default_rng` accepts — [scipy/optimize/_differentialevolution.py](https://github.com/scipy/scipy/blob/main/scipy/optimize/_differentialevolution.py).
- NOMAD: `SEED` controls poll directions — [NOMAD advanced functionalities](https://nomad-4-user-guide.readthedocs.io/en/latest/AdvancedFunctionalities.html).
- Py-BOBYQA/DFO-LS: `nsamples` averaging changes the relationship between evaluations and points, so "`soln.nf` and `soln.nx` can differ when sample averaging is used" — relevant to accounting for how many simulator draws went into a reported solution — [Py-BOBYQA user guide](https://numericalalgorithmsgroup.github.io/pybobyqa/build/html/userguide.html).

### Inferences
- The clean pattern in Ax: run the loop with simulator seed stream A (optimizer `random_seed` fixed for reproducibility), then take the shortlist (from `summarize()` or by enumerating `predict()` over all candidates), and **evaluate the shortlist on an independent seed stream B in a second, separate experiment** — using `attach_trial` + `attach_data` so the scoring run is recorded but never feeds the selection model. `get_best_parameterization(use_model_predictions=False)` on the scoring experiment then gives a selection-free estimate.
- `use_model_predictions=True` is exactly the optimistic path the user wants to avoid: the GP posterior at the arg-max is conditioned on the same noise realization that made it the arg-max. This is the library-level handle on the winner's-curse problem.
- Optuna's `study` objects are cheap to create, so the same split is easy there (study A to select, study B of fixed `enqueue_trial` candidates to score) — but Optuna cannot consume the known SE in either study, so the scoring run has to carry its own uncertainty accounting outside Optuna.

### Gaps
- I did not verify Ax's `enqueue`-style equivalent naming, nor Optuna's `study.enqueue_trial` signature in 5.0, in this pass; the select/score construction above is inferred from the verified `attach_trial`/`attach_data` API in Ax and from Optuna's general design.
- I found no library with documented first-class support for "select on one seed, evaluate on another". Reported as an absence, not a failure to search: the concept belongs to the ranking-and-selection and post-selection-inference literatures rather than to BO library APIs.

---

## Cross-cutting summary table (all dates verified 2026-10-26)

| Package | Latest release | Repo last commit | Licence | Binary/categorical inputs | Declared per-obs. noise | GPU | Verdict |
|---|---|---|---|---|---|---|---|
| BoTorch | 0.18.1 (2026-06-08) | 2026-10-16 | MIT | Yes — `CategoricalKernel`, `discrete_dims`/`cat_dims`, `{0,1}^d` local search | **Yes — `train_Yvar`** | Yes (PyTorch) | **Primary choice** |
| Ax | 1.3.1 (2026-06-09) | 2026-10-22 | MIT | Yes — `ChoiceParameterConfig` incl. `bool` | **Yes — `(mean, sem)`** | Yes (`torch_device`) | **Primary choice** |
| Optuna | 5.0.0 (2026-09-07) | 2026-10-23 | MIT | Yes — categorical w/ Hamming distance in GP | No (learned; `deterministic_objective` pins to floor) | Not exposed | Strong second / cross-check |
| SMAC3 | 2.4.1 (2026-09-10) | 2026-09-10 | BSD-3 | Yes — RF surrogate, native categorical | No — repeats seeds instead | No | Good noisy-HPO fit, no SE input |
| OSS Vizier | 0.1.24 (**2025-02-01**) | 2026-10-20 | Apache-2.0 | Yes — `add_categorical_param`, `add_discrete_param` | Not documented | JAX; GPU not documented | Repo alive, **PyPI stale** |
| Trieste | 4.6.1 (2026-10-02) | 2026-10-02 | Apache-2.0 | Yes — `CategoricalSearchSpace`, `TaggedProductSearchSpace` | Unverified | TF/GPflow | Maintained, smaller community (254 stars) |
| Nevergrad | 1.0.12 (**2025-04-23**) | 2026-10-13 | MIT | Yes — `SoftmaxCategorical`, `TransitionChoice` | No — noise-robust algorithms (TBPSA) | No | Repo alive, release cadence stalled |
| SyneTune | 0.16.0 (2026-08-03) | 2026-09-18 | Apache-2.0 | Unverified | Unverified | via BoTorch extra | Maintained; moved to `syne-tune/syne-tune` |
| Ray Tune | ray 2.59.0 (2026-10-02) | 2026-10-26 | Apache-2.0 | Via wrapped searchers | Via wrapped searchers | Yes (for training) | Orchestration layer, not a surrogate library |
| HEBO | 0.3.6 (**2024-11-04**) | HEBO/ dir: 2024-11-04 | MIT (PyPI) / none on GitHub | Yes — `cat`, `bool` types | Unverified | Unverified | **Possibly stale — flagged** |
| GPyOpt | 1.2.6 (2020-03-19) | 2023-01-17, **archived** | BSD-3 | — | — | — | **Dead** |
| scikit-optimize | 0.10.2 (2024-06-04) | 2021-10-12, **archived** | BSD-3 | — | — | — | **Unmaintained** |
| Dragonfly | 0.1.7 (2022-10-01) | 2022-10-01 | MIT | — | — | — | **Stale** |
| NOMAD (PyNomadBBO) | 4.6.0 (2026-08-26) | 2026-10-16 | LGPL-3.0 | **Binary `B` + integer `I`**; categorical only via NomadBBO | Not documented | No | **Best DFO option for bits** |
| Py-BOBYQA | 1.5.0 (**2024-09-16**) | 2026-07-22 | GPL-3.0+ | **No** (continuous only) | Partly — `objfun_has_noise`, `nsamples` | No | Noise-aware, wrong variable type |
| DFO-LS | 1.6.5 (2026-03-23) | 2026-10-19 | GPL-3.0+ | **No** (continuous, least-squares) | Partly — `objfun_has_noise`, `nsamples` | No | Noise-aware, wrong problem shape |
| RBFOpt | 4.3.0 (2025-03-30) | 2025-03-30 | BSD (revised) | **Yes — mixed-integer** | Not documented | No | Viable discrete DFO baseline |
| pySOT | 0.3.3 (2020-06-22) | 2021-10-27 | — | — | — | — | **Stale** |
| SnobFit | 0.4.5 (2020-11-30) | — | "Other/Proprietary" | — | — | — | **Stale + licence risk** |
| SciPy `differential_evolution` | scipy 1.18.1 (2026-08-21) | — | BSD-3 | **Yes — `integrality`** | No | No (`workers` for CPU) | Cheapest discrete baseline |
| SciPy `direct` | scipy 1.18.1 | — | BSD-3 | No | No | No | Continuous, deterministic only |
| NLopt | 2.11.0 (2026-07-17) | 2026-10-17 | MIT | Not documented | Not documented | No | Maintained, but no evidence of discrete/noise support |

### Flagged as possibly stale per the assignment's constraint (no release since 2023)
GPyOpt (2020), pySOT (2020), SnobFit (2020), Dragonfly (2022), and — for research code — BOCS (2019), CoCaBO (2019), COMBO (2020), TuRBO (2020), MerCBO (2021), SAASBO reference (2021), `bo_pr` (2022), BORE (2022), ALEBO (archived 2021), Casmopolitan (2023), BODi (2023), Bounce (2024).
Borderline (last release 2024–2025, repo still alive): HEBO (2024-11), Py-BOBYQA (2024-09), scikit-optimize (2024-06, repo archived), Nevergrad (2025-04), RBFOpt (2025-03), `google-vizier` on PyPI (2025-02), `sambo` (2025-07).
