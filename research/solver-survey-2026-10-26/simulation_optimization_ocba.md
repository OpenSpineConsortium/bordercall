# Discrete Optimization via Simulation and Ranking & Selection with Simulation-Budget Allocation (state as of October 2026)

Scope note for the report-writer: the problem shape assumed throughout is a finite enumerable
candidate set (128 to ~30,000 designs), a scalar value per design that is a probability estimable
only by Monte Carlo replication, a real per-replication compute cost, and a requirement to both
select the best design and report an honest, bias-corrected estimate of its value. Where a named
package could not be confirmed to exist and be installable, that is stated explicitly rather than
smoothed over.

---

## Q1. What is the canonical software for ranking and selection (R&S)? What R&S procedures does SimOpt actually ship?

### Takeaway

SimOpt is real, installable, MIT-licensed and actively maintained (simoptlib 1.2.4, 22 May 2026),
but — this is the central negative finding — **its solver library contains no ranking-and-selection
procedures at all**. The solver directory holds only continuous/derivative-free stochastic
optimisers. There is no OCBA, KN, Rinott, Paulson, Good Selection Procedure or Bonferroni
indifference-zone solver in SimOpt. There is no single canonical, production-grade R&S library in
any language; R&S remains a literature with scattered per-paper code.

### Cited Findings

- SimOpt is a public testbed of simulation-optimization problems and solvers, created because no
  testbed existed for comparing solver performance empirically; it is described as comprising
  roughly 50 problems and 10 solvers — [Eckman/Henderson/Shashaani WSC paper](https://www.informs-sim.org/wsc19papers/374.pdf); [SimOpt docs](https://simopt.readthedocs.io/en/latest/)
- The SimOpt repository is MIT-licensed; the GitHub Releases section is empty (no tagged releases);
  the master branch shows 1,626 commits — [github.com/simopt-admin/simopt](https://github.com/simopt-admin/simopt)
- **GitHub API, queried 2026-10-26:** `simopt-admin/simopt` has `pushed_at` 2026-10-15, `created_at`
  2019-06-27, 79 stars, `archived: false`. Last commit to any branch was 11 days before this
  research — SimOpt is unambiguously alive and under active development — [api.github.com/repos/simopt-admin/simopt](https://api.github.com/repos/simopt-admin/simopt)
- The full file listing of `simopt/solvers/` is: `__init__.py`, `_dasso.py`, `adam.py`, `aloe.py`,
  `astrodf.py`, `dasso.py`, `fcsa.py`, `neldmd.py`, `randomsearch.py`, `spsa.py`, `strong.py`,
  `utils.py`. No R&S solver file of any kind appears — [simopt/solvers directory](https://github.com/simopt-admin/simopt/tree/master/simopt/solvers)
- The documented solver set is ADAM; ALOE (Adaptive Line-search with Oracle Estimations); ASTRODF
  (Adaptive Sampling Trust-Region Optimization for Derivative-Free Simulations); FCSA (Fully
  Cooperative Stochastic Approximation); NELDMD (Nelder-Mead); RNDSRCH (Random Search); SPSA;
  STRONG (Stochastic Trust-Region Response-Surface Method) — [SimOpt docs](https://simopt.readthedocs.io/en/latest/)
- PyPI package `simoptlib`: latest 1.2.4, released 22 May 2026; prior releases 1.2.3 (4 May 2026),
  1.2.2.post0 (6 Dec 2025), 1.2.2 (2 Dec 2025), 1.2.1 (25 Nov 2025), 1.2.0 (13 Nov 2025), 1.1.1
  (13 Dec 2024), 1.0.0 (23 Aug 2022). Requires Python >=3.11, <3.14. MIT License — [PyPI simoptlib](https://pypi.org/project/simoptlib/)
- Python API: `pip install simoptlib`; `from simopt import models, solvers, experiment_base`;
  `experiment_base.ProblemSolver("RNDSRCH", "CNTNEWS-1")` then `.run(n_macroreps=10)`,
  `.post_replicate(n_postreps=200)`, `experiment_base.post_normalize([...])`,
  `plot_progress_curves(...)`. There is also a web interface (`simopt web`) and a GUI
  (`python -m simopt`) — [github.com/simopt-admin/simopt](https://github.com/simopt-admin/simopt)
- The R&S code by the same group lives in separate single-paper repositories, not in SimOpt:
  `daveckman/plausible-screening`, `daveckman/posterior-stopping-rules` (Posterior Stopping Rules
  for Bayesian Ranking & Selection), `daveckman/RS_after_Search` (Ranking and Selection after
  Search). The same page lists no OCBA implementation — [Eckman software page](https://eckman.engr.tamu.edu/software-and-code)
- The authoritative modern survey is Hong, Fan & Luo, "Review on ranking and selection: A new
  perspective," *Frontiers of Engineering Management* 8(3):321-343, 2021. It reviews ~70 years of
  R&S and replaces the older frequentist/Bayesian split with a **fixed-precision vs fixed-budget**
  taxonomy, noting the two rest on hypothesis testing and dynamic programming respectively;
  fixed-precision procedures deliver a statistical guarantee on the selected alternative, while
  fixed-budget procedures allocate a given budget optimally or near-optimally — [arXiv 2008.00249](https://arxiv.org/pdf/2008.00249); [journal page](https://academic.hep.com.cn/fem/EN/10.1007/s42524-021-0152-6)
- A companion utility that *is* maintained and matters for R&S correctness: `mrg32k3a`, a Python
  implementation of the MRG32k3a generator extended with streams, substreams and subsubstreams
  (optional Rust extension), from the same authors — [PyPI mrg32k3a](https://pypi.org/project/mrg32k3a/); [Eckman software page](https://eckman.engr.tamu.edu/software-and-code)

### Inferences

- The premise that SimOpt is "the" R&S library should be corrected in the report. SimOpt is a
  **benchmarking testbed for simulation optimisation over (mostly continuous) decision spaces**,
  not an R&S procedure library. Using it for a 128-to-30,000-design fixed-set selection problem
  would mean writing the R&S solver oneself against SimOpt's Problem/Solver interface.
- SimOpt's real transferable value to this project is (a) the Problem/Solver/Experiment harness and
  its macroreplication + post-replication bookkeeping, which is exactly the machinery needed to
  separate selection from honest re-estimation, and (b) `mrg32k3a`'s stream/substream structure,
  which is the standard way to implement common random numbers across designs. CRN is what makes
  0.01-level discrimination affordable when designs share a simulator.
- Any procedure named in the brief (OCBA, KN, Rinott, Paulson, GSP, Bonferroni IZ) must be assumed
  to require reimplementation from the paper unless listed under Q2 below.

### Gaps

- SimOpt's parallelism is undocumented on both its GitHub landing page and its PyPI page; neither
  mentions multiprocessing or parallel macroreplications. I could not confirm whether `ProblemSolver`
  can fan macroreplications across cores. This needs a source read of `experiment_base.py`.
- No 2024-2026 update to the Hong/Fan/Luo review was found.
- Whether `simopt` ever shipped R&S solvers in the older MATLAB-era version was not checked.

---

## Q2. What actually implements OCBA (Chen & Lee)? Is there a maintained Python or R implementation?

### Takeaway

There is **no maintained, production-grade OCBA package in any language**. Two real Python
implementations exist: a standalone GitHub repo that was created and last committed on the same day
in **March 2019** and has 1 star, and a single function inside `spotpython` (last release
2025-11-20). OCBA is, in practice, reimplemented from the paper — which is tractable, because the
allocation rule is a closed-form ratio.

### Cited Findings

- `czhhbp/OCBA` on GitHub is a standalone Python implementation. Its API is
  `continue_bool, needed_budget = OCBA(design_mean, design_var, design_used, addiction_budget)`.
  The README states the first round is not handled by the function and must be run by the user.
  The repo shows **9 commits, no releases, and no published packages** — it is not on PyPI — [github.com/czhhbp/OCBA](https://github.com/czhhbp/OCBA)
- **GitHub API, queried 2026-10-26:** `czhhbp/OCBA` has `created_at` 2019-03-23T06:31Z and
  `pushed_at` 2019-03-23T10:38Z — **created and last committed within four hours of each other on
  23 March 2019**, with 1 star. It is a single-sitting code dump, not a project; `archived: false`
  only means the owner never bothered to archive it. **Seven and a half years dormant** — [api.github.com/repos/czhhbp/OCBA](https://api.github.com/repos/czhhbp/OCBA)
- `spotpython` ships `get_ocba(means, vars, delta)`, returning budget recommendations as a NumPy
  array, with a worked example taken from the Chen & Lee book (the documented example uses
  delta = 50 and reproduces p. 49 of the book) — [spotPython get_ocba reference](https://www.gm.th-koeln.de/~bartz/site/reference/spotPython/budget/ocba)
- `spotpython` (Sequential Parameter Optimization in Python) shows releases up to 0.36.2, dated
  2025-11-20, with the 0.33-0.36 series clustered in Oct-Nov 2025 — [piwheels spotpython](https://www.piwheels.org/project/spotpython/)
- **PyPI JSON API, queried 2026-10-26:** `spotpython` current version is **0.36.2, uploaded
  2025-11-20T13:11:18**, confirming the mirror listing and confirming **no 2026 release**. The PyPI
  `license` field is null — [pypi.org/pypi/spotpython/json](https://pypi.org/pypi/spotpython/json)
- The method's three inputs are fixed by Chen et al. (2000): n0 >= 2 initial replications per design
  for mean/variance estimation; Delta >= 1, the budget increment per iteration; and T >= K*n0, the
  total budget. The procedure estimates means and variances from n0 samples, then at each iteration
  raises the working budget by Delta and recomputes the allocation fractions — [Analyzing and provably improving fixed budget ranking and selection algorithms, arXiv 1811.12183](https://arxiv.org/pdf/1811.12183)
- A documented failure mode of the original rule: because Chen et al. (2000) allocates as many
  observations as each alternative requires, **the total number of new observations per iteration can
  be much larger than Delta, particularly when the number of alternatives is large** — [arXiv 1811.12183](https://arxiv.org/pdf/1811.12183)
- OCBA remains an active research line in 2024-2026, with published variants: additive OCBA for
  robust R&S — [arXiv 2412.06020](https://arxiv.org/pdf/2412.06020); and optimal budget allocation
  under unknown sampling variance — [arXiv 2509.02138](https://arxiv.org/pdf/2509.02138)
- The canonical reference is Chen & Lee, *Stochastic Simulation Optimization: An Optimal Computing
  Budget Allocation*, World Scientific — [World Scientific](https://worldscientific.com/doi/10.1142/7437)

### Inferences

- For this project, OCBA should be treated as **~50 lines of code to write, not a dependency to
  install**. The verified dates make this conclusion stronger, not weaker: the standalone repo is a
  one-afternoon artefact from 2019 that nobody has touched since, so vendoring it would import
  unreviewed code with no maintainer. The `spotpython.get_ocba(means, vars, delta)` signature is the
  better reference implementation to check one's own against — it sits inside a package that was
  released in late 2025 and documents a worked example from the Chen & Lee book, giving a published
  numerical target. That satisfies the project's standing rule of testing a computation against an
  independent implementation rather than trusting internal consistency.
- The "overshoot of Delta" defect above is directly relevant at 30,000 designs: a naive Delta-per-
  iteration loop over 30,000 alternatives will blow its own budget. Either cap the per-iteration
  allocation or use a fixed-budget procedure designed for large K (see Q7/Q8).

### Gaps

- I found no CRAN package implementing OCBA. I did not run an exhaustive CRAN search, so this is
  "not found", not "confirmed absent".
- The specific n0 and Delta recommendations in the Chen & Lee book could not be retrieved. Only
  third-party usages were found: one study used 20% of the total budget for initial estimation with
  a budget increment of 20; another used n0 = 10 throughout — [arXiv 1811.12183](https://arxiv.org/pdf/1811.12183)

---

## Q3. Industry-trusted commercial and national-lab tools: OptQuest, Dakota, libEnsemble, SAS/JMP

### Takeaway

Of the four, **libEnsemble and Dakota are the credible, free, auditable choices for a research-
medical setting** — both are actively released in 2025-2026, both are open-source with clear
licences, and both are designed to drive expensive simulations across HPC resources. OptQuest is
industry-trusted but is a black-box metaheuristic sold only embedded inside commercial simulation
suites with no public pricing, and it is the wrong tool for a fixed enumerable design set. JMP's
"Simulator" is a Monte Carlo add-on to its profilers, not a simulation-optimisation or R&S engine.

### Cited Findings

**Dakota (Sandia National Laboratories)**

- Dakota 6.23 was announced available for download on 26 November 2025; the Dakota homepage lists
  6.24 above 6.23 in its news section, so 6.24 is the current release (no release post or date for
  6.24 was found) — [dakota.sandia.gov news](https://dakota.sandia.gov/category/news/); [dakota.sandia.gov](https://dakota.sandia.gov/)
- Licence: Dakota 5.0 and newer are under the **GNU LGPL**; the Dakota GUI is under the Eclipse
  Public License; bundled third-party packages carry their own LGPL-compatible terms (3.0-4.2 were
  GPL) — [dakota.sandia.gov](https://dakota.sandia.gov/?p=184). An Anaconda distribution lists the
  licence as LGPL-2.1 — [anaconda.org/csdms-stack/dakota](https://anaconda.org/channels/csdms-stack/packages/dakota/overview)
- Scope: Dakota links simulation codes to analysis methods; its algorithms span gradient and
  non-gradient optimisation, uncertainty quantification and sensitivity analysis, and it supports
  surrogate-based optimisation, **mixed integer nonlinear programming**, and optimisation under
  uncertainty — [Sandia publication page](https://www.sandia.gov/research/publications/details/dakota-a-multilevel-parallel-object-oriented-framework-for-design-optimizat-2021-11-01/)
- Dakota 6.23's headline feature was improved statistics from imported samples via the
  `import_points` method, which reads samples from a tabular file and computes moments, correlation
  coefficients and optionally level mappings and Sobol indices — [dakota.sandia.gov news](https://dakota.sandia.gov/category/news/)

**libEnsemble (Argonne National Laboratory)**

- Release 1.6.1, dated **20 July 2026**; the only change is removal of the gest-api dependency
  upper bound. Tested on Linux and macOS with Python 3.10-3.14 — [libEnsemble release notes](https://libensemble.readthedocs.io/en/main/release_notes.html)
- Release 1.6.0, dated **4 March 2026**: added support for gest-api generators including any Xopt
  (v3.0+) and Optimas generators; added dictionary-style (Xopt-style) simulator functions and
  simulation container support; gest-api became a required dependency; Pydantic v1 and Balsam
  support were dropped — [libEnsemble release notes](https://libensemble.readthedocs.io/en/main/release_notes.html)
- libEnsemble v1.6.0 is listed among the FASTMath institute's 2026 software release highlights —
  [SciDAC FASTMath](https://scidac-fastmath.lbl.gov/software-release-highlights)

**OptTek OptQuest and its embeddings**

- An OR/MS Today Simulation Software Survey records that the FlexSim Healthcare optimisation engine
  is **powered by OptQuest and sold as an add-on** — [INFORMS OR/MS Today simulation software survey](https://deca.informs.org/ORMS-Today/OR-MS-Today-Software-Survey/Page-6)
- Simul8 does not publish list prices; OptQuest is a separate paid add-on whose price is not
  disclosed — [rfp.wiki Simul8 comparison](https://www.rfp.wiki/supply-chain-logistics-transportation/supply-chain-planning-solutions/supply-chain-simulation-software/simul8/anylogistix)
- Simio has no public price list; commercial editions require contacting sales, but a 30-day trial
  and **no-cost academic licences** are available — [rfp.wiki Simio](https://www.rfp.wiki/supply-chain-logistics-transportation/supply-chain-planning-solutions/supply-chain-simulation-software/simul8/simio)
- AnyLogic pricing is quote-based; a third-party aggregator lists the Professional edition at
  roughly **$18,990 per seat**, with training at ~$1,500/person online or ~$1,750 in person, and
  notes a free Personal Learning Edition that cannot be used commercially — [checkthat.ai AnyLogic pricing](https://checkthat.ai/brands/anylogic/pricing) (third-party aggregator, self-labelled as estimates)
- FlexSim (now sold by Autodesk) is quote-based; a reseller cites roughly **$6,000/year** for a
  standalone subscription, with optional support at $195 or $595 per user per year — [rfp.wiki FlexSim](https://www.rfp.wiki/supply-chain-logistics-transportation/supply-chain-planning-solutions/supply-chain-simulation-software/enterprise-dynamics/flexsim) (reseller figures, not a vendor price list)

**SAS / JMP**

- JMP's **Simulator** is a red-triangle menu option inside the Prediction Profiler, Contour Profiler
  and Custom Profiler. The user sets factor and response parameters, a histogram is added beside
  each response, and clicking Simulate generates response values; in the Contour and Custom
  profilers results go to a data table via a "Simulate to Table" report — [JMP 18.1 documentation, Launch the Simulator](https://origin-www.jmp.com/support/help/en/18.1/jmp/launch-the-simulator.shtml)

### Inferences

- For a research-medical setting the licence and auditability question decides this. libEnsemble
  (Argonne, 3-clause-style open source, releases in March and July 2026) and Dakota (Sandia, LGPL,
  release Nov 2025 + a newer 6.24) are both defensible in a methods section and both are free. A
  commercial OptQuest embedding is not defensible for a published method, because OptQuest's search
  is proprietary and its allocation rule cannot be described in a paper.
- Neither Dakota nor libEnsemble is an R&S library. Their role in this project is the **replication
  workload manager** (fan 30,000 x n replications across cores/nodes and collect them), with the
  selection rule supplied by the user's own OCBA/KN code as a libEnsemble generator function.
- JMP's Simulator does not address this problem: it propagates input distributions through an
  existing fitted model, rather than allocating a finite replication budget across a finite design
  set. Treat it as out of scope rather than as a weak option.
- Simio's no-cost academic licence is the only confirmed academic-pricing route found among the
  commercial suites; note it, but it buys an OptQuest metaheuristic the project does not need.

### Gaps

- No official OptQuest price for Simio, AnyLogic, Arena or FlexSim could be found; all figures above
  are reseller/aggregator estimates and should be reported as such. Written vendor quotes are the
  only reliable route.
- No evidence was found that Arena still embeds OptQuest in current versions (Arena's OptQuest
  bundling is historical; the 2026 state was not verified).
- Dakota 6.24's release date and feature list were not found.
- Academic licence availability for AnyLogic/FlexSim/Simul8 was not confirmed beyond AnyLogic's
  non-commercial Personal Learning Edition.
- SAS proper (as distinct from JMP) has a simulation-optimisation offering that I did not locate;
  I found no evidence either way.

---

## Q4. Best-arm identification (BAI) software: fixed-budget and fixed-confidence

### Takeaway

BAI is the same problem as fixed-budget/fixed-confidence R&S, but **its software situation is worse,
not better**. `banditpylib` is the only library found with real BAI procedure coverage, and its
**last commit was 21 July 2022** — over four years dormant, no releases, not on PyPI. `SMPyBandits`
is the opposite case and my first pass got it wrong: its **repository is alive (last commit 19 June
2026, 426 stars)** while its PyPI release is frozen at 2019, so it is installable only from source.
The only production-grade, maintained implementation of any BAI-family algorithm is **Ray Tune's
ASHA** (asynchronous successive halving) — and it is built for early-stopping hyperparameter search,
not for honest selection guarantees. Track-and-Stop and Top-Two Thompson Sampling have no maintained
package; they exist as paper code. `rliable` is **archived and is not a BAI tool** (see Gaps).

### Cited Findings

- `banditpylib` (github.com/Alanthink/banditpylib) is a lightweight Python library for comparing
  bandit algorithms. Its BAI coverage is explicit: **fixed budget** — Uniform, SR (Successive
  Rejects), SH (Sequential Halving); **fixed confidence** — ExpGap (Exponential-Gap Elimination),
  LilUCBHeuristic. MIT licence. 454 commits. **The Releases section is empty and it is not on PyPI**;
  installation is by cloning and running `make install` — [github.com/Alanthink/banditpylib](https://github.com/Alanthink/banditpylib)
- **GitHub API, queried 2026-10-26:** `Alanthink/banditpylib` has `pushed_at` **2022-07-21**,
  `created_at` 2018-11-05, 29 stars, `archived: false`. **No commit to any branch in over four
  years.** Not archived, but dormant by any reasonable reading — [api.github.com/repos/Alanthink/banditpylib](https://api.github.com/repos/Alanthink/banditpylib)
- `SMPyBandits` is MIT-licensed and publicly available, but its most recent PyPI release is **0.9.7,
  2019-10-25** — [PyPI SMPyBandits](https://pypi.org/project/SMPyBandits/0.9.3); [SMPyBandits docs](https://smpybandits.readthedocs.io/)
- **GitHub API, queried 2026-10-26 — this corrects an earlier finding in these notes:**
  `SMPyBandits/SMPyBandits` has `pushed_at` **2026-06-19**, `created_at` 2016-11-17, **426 stars**,
  `archived: false`. The repository received a commit four months before this research. The earlier
  "last updated 30 April 2024" figure, taken from a GitHub topics listing page, was a stale snapshot
  and should not be used. **SMPyBandits is an actively committed repository with a seven-year-old
  PyPI release** — [api.github.com/repos/SMPyBandits/SMPyBandits](https://api.github.com/repos/SMPyBandits/SMPyBandits)
- A PyPI package named `best-arm` exists, described as a modular multi-armed bandit framework with
  algorithms, trackers and stopping rules, MIT-licensed, last updated **2025-08-06**. A third-party
  tracker gives it a health score of 38/100 and advises considering alternatives — [depscope best-arm](https://mcp.depscope.dev/pkg/pypi/best-arm) (aggregator signal, treat as rough)
- Ray Tune: **ASHA is an alias of Ray's asynchronous HyperBand implementation**, and Ray's docs
  recommend it over the synchronous `HyperBandScheduler` because it gives better parallelism and
  avoids straggler issues during elimination rounds. Ray uses **one bracket by default** (the ASHA
  paper describes three), a choice the docs attribute to discussion with the paper's authors. Key
  parameters are `grace_period` (before the first halving) and `reduction_factor` — [Ray Tune scheduler docs](https://docs.ray.io/en/latest/tune-schedulers.html)
- Ray's synchronous `HyperBandScheduler` remains available, with defaults `max_t=81`,
  `reduction_factor=3` — [Ray 2.49.0 hyperparameter tuning docs](https://tessl.io/registry/tessl/pypi-ray/2.49.0/files/docs/hyperparameter-tuning.md)
- The ASHA paper's own framing: synchronous successive halving and Hyperband make decisions in
  lockstep, which is their main drawback at scale; the asynchronous variant makes stopping decisions
  as results arrive — [ASHA paper, arXiv 1810.05934](https://arxiv.org/pdf/1810.05934v3)
- A small utility exists for the BAI sample-complexity lower bound: `rssalessio/py-lower-bound-bai`,
  "Python utilities to compute a lower bound of the expected sample complexity to identify the best
  arm in a bandit model" — [github.com/rssalessio/py-lower-bound-bai](https://github.com/rssalessio/py-lower-bound-bai)

### Inferences

- `banditpylib` is the single most directly relevant BAI codebase found, because Successive Rejects
  and Sequential Halving are exactly the fixed-budget procedures the user's problem calls for, and
  because SR/SH need no variance estimates and no indifference-zone parameter. But with no releases,
  no PyPI distribution and **no commit since July 2022**, it must be treated as **dormant research
  code to read and reimplement**, not as a dependency to install. Successive Rejects and Sequential
  Halving are each a few dozen lines; reading `banditpylib`'s versions as a correctness reference and
  writing one's own is the defensible route, and it mirrors the conclusion reached independently for
  OCBA in Q2.
- The verified dates invert the ranking between the two bandit libraries. **`SMPyBandits` is the live
  repository (commit June 2026, 426 stars) and `banditpylib` is the dormant one** — the opposite of
  what the PyPI release dates alone suggest. If a bandit codebase is to be used at all, SMPyBandits
  installed from a git checkout is the better-maintained bet, with the caveat that its documented
  BAI coverage was not separately verified in this session (see Gaps).
- Ray Tune's ASHA is the pragmatic production answer for the *compute orchestration* of a
  halving-style budget allocation at 30,000 candidates, because the scheduler and the parallel
  execution engine come together. The caveat for this project is that ASHA offers no probability of
  correct selection and no bias correction — it is an engineering heuristic.
- Sequential Halving over 30,000 designs needs about log2(30,000) ~ 15 rounds and spends budget
  B/15 per round; that is a budget profile that fits the project's "cheap-ish simulator" description
  far better than a fully sequential KN-style procedure, which needs pairwise comparisons across all
  surviving designs at every stage.

### Gaps

- **No maintained implementation of Track-and-Stop (Garivier & Kaufmann) or Top-Two Thompson
  Sampling (Russo) was found.** The only concrete lead was a Towards Data Science article containing
  a Python example for the Bernoulli case, which claims Top-Two Thompson needed 35% fewer trials to
  identify the best arm — [Towards Data Science, "Why not to use Thompson sampling for best arm identification"](https://towardsdatascience.com/why-not-to-use-thompson-sampling-for-best-arm-identification-8ed458428126) (blog post; the 35% figure is the author's own experiment, not a peer-reviewed result)
- **`rliable` — now settled on both counts, and it should be dropped from the BAI section of the
  report.** It exists and is installable (PyPI `rliable` 1.2.0, uploaded 2024-08-12), but its
  GitHub repository `google-research/rliable` is **`archived: true`** with `pushed_at` 2024-08-12
  and 878 stars. Archival by the owner is decisive evidence the project is closed to further work.
  Its own description settles the second question: "[NeurIPS'21 Outstanding Paper] Library for
  reliable evaluation on RL and ML benchmarks, even with only a handful of seeds," and the PyPI
  summary reads "Reliable evaluation on reinforcement learning and machine learning benchmarks."
  **It is a benchmark-evaluation statistics toolkit, not a best-arm-identification allocator** — it
  tells you how confident to be in a reported comparison, not how to spend a replication budget.
  My earlier caution was correct — [pypi.org/pypi/rliable/json](https://pypi.org/pypi/rliable/json); [api.github.com/repos/google-research/rliable](https://api.github.com/repos/google-research/rliable)
- `SMPyBandits`' specific best-arm-identification procedure coverage was not enumerated. Its
  repository is alive, but I confirmed only that it is a bandit library — **not which BAI
  procedures it ships**. This is the one worthwhile remaining lookup in this section.
- LUCB specifically: `banditpylib` ships LilUCBHeuristic, not LUCB. No maintained LUCB
  implementation was found.
- No BAI survey code repository (Jamieson & Nowak; Kaufmann, Cappe & Garivier) was located.

---

## Q5. Racing and algorithm-configuration tools: irace, SMAC3, ParamILS, GGA

### Takeaway

`irace` and SMAC3 are the two production-trusted tools here, and both have 2026 releases — irace
4.5 on CRAN (15 September 2026) and a SMAC3 release dated 22 April 2026. Both solve "pick the best
configuration under a noisy objective and a budget," and irace's iterated racing is the closest
thing to an off-the-shelf, battle-tested R&S engine that a user can install today. ParamILS and GGA
were not verified.

### Cited Findings

- irace: the CRAN reference manual lists **version 4.5, published 2026-09-15**; the package
  implements iterated racing for automatic algorithm configuration, citing Lopez-Ibanez et al.
  (2016) — [CRAN irace reference manual](https://cran.rstudio.com/web/packages/irace/refman/irace.html)
- **Version conflict resolved.** The r-universe mirror listed v4.4.3 dated 2026-04-23 — [r-universe irace](https://mlopez-ibanez.r-universe.dev/api/packages/irace) — but the CRAN
  metadata database, queried directly on 2026-10-26, returns **irace 4.5 with Date/Publication
  2026-09-15 09:50:08 UTC**. CRAN is authoritative and the r-universe figure was mirror lag. irace
  is the most recently released tool in this entire survey — [crandb.r-pkg.org/irace](https://crandb.r-pkg.org/irace)
- irace's documented entry point is `irace_main` / the `irace` package on CRAN — [rdrr.io irace_main](https://rdrr.io/cran/irace/man/irace_main.html)
- **SMAC3 version confirmed:** the PyPI JSON API, queried 2026-10-26, gives current version
  **2.4.1, uploaded 2026-09-10T15:12:24**. The 22 April 2026 date from the maintainer profile was an
  earlier release in the same series — [pypi.org/pypi/smac/json](https://pypi.org/pypi/smac/json)
- SMAC3: a PyPI maintainer profile shows a SMAC3 release dated **22 April 2026**; the project's
  documented scope is Bayesian optimisation combined with **aggressive racing**, supporting algorithm
  configuration as well as hyperparameter optimisation — [PyPI user page](https://pypi.org/user/ddeng/); [PyPI smac](https://pypi.org/project/smac/2.0.0a1); [SMAC3 JMLR paper, arXiv 2109.09831](https://arxiv.org/pdf/2109.09831)
- A curated comparison of automatic algorithm configuration tools is maintained in the `up-ac`
  documentation — [up-ac: Automatic algorithm configuration tools](https://up-ac.readthedocs.io/en/latest/ac_tools.html)

### Inferences

- irace is the most defensible "install it and use it" option for the user's problem among all tools
  surveyed, with two caveats: it is R, not Python (callable via `subprocess` or `rpy2`), and it is
  designed for configuration *spaces* rather than an explicit enumerated list — though an enumerated
  list is representable as a single categorical parameter with 128 levels, and is awkward at 30,000.
- irace's racing elimination is statistical (Friedman test / t-test based) rather than an
  indifference-zone guarantee, so it selects well but does not by itself deliver a PCS statement or
  a bias-corrected value for the winner.

### Gaps

- **ParamILS and GGA were not researched.** No claim should be made about their 2026 maintenance
  status. ParamILS in particular is widely believed to be dormant, but that was not verified here.
- No source was found comparing irace and SMAC3 head-to-head for 2026 use.

---

## Q6. The winner's curse: what software corrects the optimistic bias of the selected best?

### Takeaway

This is the best-served part of the brief in terms of *methods* and the worst-served in terms of
*maintained general-purpose software*. One package is directly usable and installable today:
**`winnerscurse`** (R, MIT), which takes nothing but (effect estimate, standard error) pairs and
applies a menu of published winner's-curse corrections — exactly the input shape the user has;
note it is **not on CRAN** (verified) and has not been committed to since March 2024.
`selectiveInference` (R, CRAN 1.2.5) covers the **many-means problem**, which is literally
"select the largest of k noisy means and do inference on it", but its last release is 2019.
Andrews-Kitagawa-McCloskey "Inference on Winners," the most cited econometric treatment, has
**no package** that I could find. A 2026 paper reports that **no correction method dominates**.

### Cited Findings

**Directly installable software**

- `winnerscurse` (R): applies several published winner's-curse adjustment methods to summary
  statistics. **Users need only each variant's effect-size estimate and its standard error.** Works
  for quantitative and binary traits. Version **0.1.1, MIT licence**, maintainer Amanda Forde;
  docs at amandaforde.github.io/winnerscurse; source at github.com/amandaforde/winnerscurse —
  [R-universe winnerscurse manual](https://mrcieu.r-universe.dev/winnerscurse/doc/manual.html)
- **`winnerscurse` is confirmed NOT on CRAN.** The CRAN metadata database, queried directly on
  2026-10-26, returns `{"error":"not_found","reason":"document not found"}` for this package name.
  It is distributable only from GitHub or the MRC-IEU R-universe. For comparison, the same endpoint
  returned valid records for `selectiveInference`, `ashr` and `irace`, so the query itself is
  sound — [crandb.r-pkg.org/winnerscurse](https://crandb.r-pkg.org/winnerscurse)
- **GitHub API, queried 2026-10-26:** `amandaforde/winnerscurse` has `pushed_at` **2024-03-07**,
  `created_at` 2021-02-03, 5 stars, `archived: false`. Last commit about two and a half years before
  this research — not stale by the brief's "no release since 2023" threshold, but dormant, and the
  low star count means little outside review has been applied to it — [api.github.com/repos/amandaforde/winnerscurse](https://api.github.com/repos/amandaforde/winnerscurse)
- `winnerscurse` method menu includes a **parametric bootstrap** method (Forde et al. 2023), which
  the authors' own review reported as competitive, and **conditional likelihood** methods, which the
  same review found tended to perform poorly — [bioRxiv/PLOS Genetics review full text](https://www.biorxiv.org/content/10.1101/2022.11.28.518299v2.full-text)
- `winnerscurse` has a second mode for the case where **both discovery and replication statistics**
  are available; adjustments apply only to variants significant in the discovery data — [R-universe discovery/replication vignette](https://mrcieu.r-universe.dev/winnerscurse/doc/discovery_replication.html)
- The companion peer-reviewed paper is Forde, Hemani & Ferguson, "Review and further developments in
  statistical corrections for Winner's Curse in genetic association studies," *PLOS Genetics* (2023) —
  [IDEAS/RePEc record](https://ideas.repec.org/a/plo/pgen00/1010546.html); [bioRxiv preprint](https://www.biorxiv.org/content/10.1101/2022.11.28.518299.full.pdf)
- **CRAN metadata confirmed directly, 2026-10-26:** `selectiveInference` is **1.2.5, Date/Publication
  2019-09-07 07:00:02 UTC**; `ashr` is **2.2-63, Date/Publication 2023-08-21 23:50:03 UTC**. Both
  figures below are verified against the CRAN database rather than a mirror page — [crandb.r-pkg.org/selectiveInference](https://crandb.r-pkg.org/selectiveInference); [crandb.r-pkg.org/ashr](https://crandb.r-pkg.org/ashr)
- `selectiveInference` (R, CRAN): version **1.2.5, published 2019-09-07**, maintainer Rob Tibshirani.
  Provides tools for post-selection inference for forward stepwise regression, least angle
  regression, the lasso, **and the many means problem**. Its p-values are exactly uniform under the
  null in finite samples, giving exact type I error control — [CRAN selectiveInference](https://cran.r-project.org/web/packages/selectiveInference/); [arXiv 1401.3889](https://arxiv.org/abs/1401.3889)
- `selectiveInference` is still passing CRAN checks: **11 OK / 1 NOTE as of 2026-06-08**, with NOTEs
  on r-devel Debian clang and gcc flavours (a WARNING on 2026-06-07 cleared the next day) — [R Observatory selectiveInference](https://r-observatory.thecoatlessprofessor.com/packages/selectiveInference)
- `ashr` (Adaptive Shrinkage using Empirical Bayes, R): current CRAN release **2.2-63, published
  2023-08-21**. Implements empirical Bayes shrinkage from Stephens (2016) "False discovery rates: a
  new deal". It applies **whenever estimated effects and their standard errors are available**, much
  as `qvalue` works on precomputed p-values. Entry points `ash()` and `ash.workhorse()`. `ebnm` is
  listed among the packages that import `ashr` — [CRAN ashr](https://search.r-project.org/CRAN/packages/ashr/index.html)
- Multiple comparisons with the best (MCB): `multcomp` (R) provides general linear hypothesis tests
  and simultaneous intervals, with many procedures hard-coded — **Dunnett, Tukey, sequential pairwise
  contrasts, comparisons with the average, changepoint analysis, Williams', Marcus', McDermott's and
  tetrad contrasts. Hsu's MCB is not in that list.** A free input interface for the contrast matrix
  allows more general comparisons, so the standard route is to build a contrast matrix comparing each
  group to the best and pass it to `glht()` — [multcomp glht documentation](https://www.rdocumentation.org/packages/multcomp/versions/1.4-20/topics/glht); [Bretz, Hothorn & Westfall, "On Multiple Comparisons in R"](https://www.r-project.org/conferences/useR-2004/abstracts/Bretz+Hothorn+Westfall.pdf)
- `multcomp` is maintained: r-universe listings show versions 1.4-26 and 1.4-30 — [thothorn.r-universe.dev multcomp](https://thothorn.r-universe.dev/multcomp)
- A commercial statistics vendor documents an Hsu MCB procedure as simultaneous one-sided intervals
  with a lower bound built from a one-sided Dunnett critical value, implemented via
  `multcomp::glht` with single-step adjustment, where treatments whose intervals include zero form
  the "best set" that cannot be statistically separated from the best — [MetricGate Hsu MCB docs](https://metricgate.com/docs/hsu-mcb-multiple-comparisons-best/) (vendor documentation; the glht-equivalence and critical-value claims are unverified against Hsu 1984/1996)

**Methods with no package found**

- Andrews, Kitagawa & McCloskey, "Inference on Winners," *Quarterly Journal of Economics*
  139(1):305-358 (2024), develops estimators and confidence intervals that remove the upward bias
  in the selected option's estimate. A follow-up, "Inference for losers," appeared in *AEA Papers and
  Proceedings* (2022), DOI 10.1257/pandp.20221065 — [Adam McCloskey publication list, IDEAS/RePEc](https://ideas.repec.org/e/c/pmc156.html); [University of Colorado record](https://experts.colorado.edu/display/pubid_362977)
- Zrnic & Fithian propose a "zoom correction" for valid inference on the winner — [arXiv 2411.18569](https://arxiv.org/html/2411.18569v1)
- "Flexible Inference for Winners with Conditional Validity" (2026) — [arXiv 2607.18545](https://arxiv.org/pdf/2607.18545)
- **"Valuing Winners: When and How to Correct for Selection Bias in Randomized Experiments"
  (arXiv 2605.18887, 2026)** compares plug-in, cross-fitting, resampling, and an adaptive empirical
  likelihood method, and finds that **no method dominates**: the plug-in estimator does best when
  treatment differences are large, cross-fitting does best when treatments are similar, and
  resampling has low error at moderate differences. It also distinguishes a "global" from a
  "selective" winner's curse, which determines which correction is appropriate — [arXiv 2605.18887](https://arxiv.org/pdf/2605.18887); [EmergentMind summary](https://www.emergentmind.com/papers/2605.18887)
- A CUHK Business School marketing paper proposes a non-continuous bootstrap correction for the
  winner's curse in A/B testing and related settings — [CUHK Business School](https://www.bschool.cuhk.edu.hk/?p=44530)

### Inferences

- The cleanest, lowest-risk design for this project is the one that needs no post-selection
  machinery at all: **split the replication budget into a selection stage and an evaluation stage,
  select on the first, and report the winner's value from fresh independent replications of only the
  winner.** With a cheap simulator and a probability-valued objective this costs almost nothing, and
  it sidesteps every unresolved question in the 2024-2026 winner's-curse literature. Post-selection
  corrections are the fallback for when re-simulation is impossible, which is not this situation.
- `winnerscurse` is a genomics-framed package, but nothing about its methods is genomic: its input
  is (estimate, SE) per candidate, which is exactly what a per-design Monte Carlo mean and its
  standard error give. It is the one package in this whole survey that can be pointed at the user's
  output table with no reformulation. Its version number (0.1.1) and the absence of a confirmed CRAN
  listing argue for cross-checking its output against the simple data-splitting estimate above.
- `selectiveInference`'s **many-means problem** is the correct formal home for "I picked the largest
  of k noisy means." The 2019 release date is a maturity concern, not a correctness one, and the
  2026-06-08 CRAN check results show it still builds. Under the brief's "flag stale" rule it should
  be flagged as no release since 2019 while noting it is still CRAN-installable and passing checks.
- MCB should be reported as a **method available through `multcomp`'s contrast interface, not as a
  shipped procedure**. Any report sentence saying "`multcomp` implements Hsu's MCB" would be wrong.
- Empirical-Bayes shrinkage of the winner is available via `ashr`, and it is the natural tool when
  the user wants the whole ranked table de-biased rather than just the top design. Flag `ashr` as
  having no release since 2023-08-21.

### Gaps

- **No replication code or package for Andrews-Kitagawa-McCloskey "Inference on Winners" was found.**
  Their QJE supplementary materials or a personal-site replication archive are the next place to
  look; I could not confirm one exists.
- `winnerscurse`'s absence from CRAN is now confirmed rather than merely unestablished, which is a
  real caveat for a clinical-methods paper: the package has had no CRAN review, sits at version
  0.1.1 with 5 stars, and has not been committed to since March 2024. Its underlying methods are
  peer-reviewed (PLOS Genetics 2023); its implementation is not independently vetted. **Any number
  it produces should be cross-checked against the data-splitting estimate described in the
  Inferences below before it reaches a manuscript.**
- No Python package for post-selection inference was located. The Python `selectinf`/`selection`
  codebase from the same research group was not verified in this session and should not be asserted
  to exist without a check.
- Benjamini-Hochberg-style correction specifically *for the selection step* (as distinct from FDR
  control across all candidates) was not found as a named implementation.
- Dimmery et al. (2019) and Lee & Shen (2018) were cited second-hand in a preprint's reference list;
  their contents were not retrieved and should not be characterised.

---

## Q7. Practical guidance: at 128 to 30,000 candidates with a cheap simulator, is full enumeration plus OCBA better than a search heuristic? What budget per design separates designs differing by 0.01?

### Takeaway

At 128 candidates, full enumeration plus a budget-allocation rule is clearly right and no search
heuristic is justified. At 30,000 it is still right *in principle* — the parallel R&S literature
explicitly makes this case — but a single-processor sequential procedure will not do it; the modern
answer is a divide-and-conquer or knockout-tournament procedure. On budget: nothing in the sources
gives a per-design replication count for a 0.01 indifference zone, and the elementary Bernoulli
arithmetic says the requirement is severe (order 10^4-10^5 replications per design under equal
allocation), which is the single most important number for the user to confront.

### Cited Findings

- Barry Nelson's framing of the parallel R&S case: cheap multi-core hardware makes it practical to
  **simulate every alternative even when there are tens of thousands**, but most R&S procedures were
  built for a single processor, and running them naively in parallel can make them **statistically
  invalid** — [CUHK seminar abstract, "Large-Scale Ranking and Selection in Parallel Computing Environments"](https://seminar.se.cuhk.edu.hk/node/85); [CUHK Business School event page](https://www.bschool.cuhk.edu.hk/events/large-scale-ranking-and-selection-in-parallel-computing-environments)
- Knockout-tournament procedures modelled on tennis brackets are reported to make the expected total
  sample size grow **at the lowest possible rate in the number of alternatives**, with little
  inter-processor communication — [CUHK Business School event page](https://www.bschool.cuhk.edu.hk/events/large-scale-ranking-and-selection-in-parallel-computing-environments)
- The named large-scale procedures in this literature are knockout-tournament (Zhong & Hong, 2022),
  fixed-budget variants (Hong et al., 2022), and parallel adaptive survivor selection, PASS
  (Pei et al., 2022); the same source states these methods have pushed solvable problem sizes
  **from thousands to millions of alternatives** — [arXiv 2303.02951v2](https://arxiv.org/pdf/2303.02951v2)
- "Clustering and Conquer" (Zhang & Peng) adds a correlation-based clustering step to the standard
  divide-and-conquer framework, achieving an **O(p) sample-complexity reduction** without needing
  highly accurate clustering; a screening-free version is reported to beat fully sequential
  benchmarks on sample efficiency in neural architecture search — [arXiv 2402.02196](https://arxiv.org/html/2402.02196v2); [Moonlight literature review](https://themoonlight.io/review/clustering-and-conquer-procedures-for-parallel-large-scale-ranking-and-selection)
- Fixed-budget and fixed-precision are the two correct formulations to choose between, built on
  dynamic programming and hypothesis testing respectively — [Hong, Fan & Luo, arXiv 2008.00249](https://arxiv.org/pdf/2008.00249)
- On OCBA's sequential structure: sequential updating matters for finite-sample performance, and the
  adaptive scheme makes OCBA "particularly robust against estimation noise" — [WSC 2012 paper](https://www.informs-sim.org/wsc12papers/includes/files/con371.pdf)
- Observed OCBA parameter choices in the literature: 20% of the total budget for initial estimation
  with a per-iteration increment of 20; and n0 = 10 — [arXiv 1811.12183](https://arxiv.org/pdf/1811.12183)

### Inferences

- **Budget arithmetic for a 0.01 indifference zone (my own calculation, not from a source, and it
  should be labelled as such in the report).** If the objective is a probability near 0.5, a single
  replication has variance p(1-p) = 0.25. The standard error of a difference between two designs
  each with n replications is sqrt(2 x 0.25 / n) = sqrt(0.5/n). To make a 0.01 difference detectable
  at a Bonferroni-corrected two-sided level across k = 128 designs (alpha = 0.05/127, z ~ 3.48)
  requires sqrt(0.5/n) <= 0.01/3.48, i.e. **n ~ 60,000 replications per design**, or ~7.7 million
  replications total under equal allocation. For a single pairwise comparison at z ~ 2.8 the figure
  is ~39,000 per design. At p near 0.9 the variance drops to 0.09 and the requirement falls by
  roughly 2.8x, to ~22,000 per design. **Common random numbers across designs is the one lever that
  changes this by an order of magnitude**, because it cancels the shared variance component in the
  paired difference; this is why `mrg32k3a`'s substream structure (Q1) is not a nicety.
- The practical consequence: a 0.01 indifference zone at 30,000 candidates is almost certainly
  unaffordable by brute force, and the honest options are (a) widen the indifference zone and report
  a "best set" rather than a single winner (which is exactly what MCB intervals deliver, Q6), (b) use
  paired/CRN differences rather than independent estimates, or (c) use a screening-then-refine
  design: a cheap uniform or Sequential-Halving pass to cut 30,000 to tens, then OCBA or KN with a
  tight zone on the survivors. Option (c) matches the Clustering-and-Conquer and knockout-tournament
  structure in the cited literature.
- Enumeration-plus-allocation beats a search heuristic here for a reason specific to this problem:
  the design space is subsets of measurements, so the objective is not smooth in any coordinate a
  heuristic could exploit, and a heuristic would give no probability of correct selection and no
  clean basis for post-selection inference. The argument for a heuristic only begins when K is large
  enough that even one replication per design is unaffordable, which at 30,000 and a "cheap-ish"
  simulator is probably not the case.
- At 128 candidates the whole problem is small enough that the statistically cleanest design —
  equal allocation for screening, OCBA for refinement, and a held-out replication budget for the
  winner's reported value — is also computationally trivial. The user should not reach for anything
  more sophisticated at the low end of their range.

### Gaps

- **No source gives a recommended replication budget per design for a 0.01 difference in a
  probability.** The arithmetic above is elementary but is my own; the report should present it as a
  calculation to be checked, not as a literature recommendation.
- I found no published head-to-head comparison of full-enumeration-plus-OCBA against search
  heuristics at K in the 10^2-10^4 range for a Bernoulli objective.
- No source was found quantifying OCBA's budget saving over equal allocation. The commonly repeated
  claim that OCBA needs a fraction of equal allocation's budget could not be sourced in this
  session and should not be stated with a number.
- Whether any of the large-scale parallel procedures (knockout tournament, PASS,
  Clustering-and-Conquer) has **installable code** was not established; all evidence found is
  papers. Treat them as methods to implement, not packages to install, unless verified otherwise.

---

## Q8. Parallel and GPU: which tools exploit many cores or a GPU for the replication workload?

### Takeaway

libEnsemble is the clear answer for HPC-scale replication workloads and is the only tool surveyed
with documented, automatic GPU and MPI-runner detection. Ray is the clear answer for a single
multi-core workstation or a small cluster, and its ASHA scheduler couples allocation to execution.
Dakota has long-standing multilevel parallelism. SimOpt's parallel capability is undocumented.

### Cited Findings

- libEnsemble performs substantial automatic system detection: scheduler details, **MPI runners
  (mpirun, srun, jsrun, aprun)**, nodes, core counts and **GPU counts**; it detects NVIDIA, AMD and
  Intel GPUs and sets variables such as `CUDA_VISIBLE_DEVICES` or `ROCR_VISIBLE_DEVICES` — [Portable, heterogeneous ensemble workflows at scale using libEnsemble, arXiv 2403.03709](https://arxiv.org/pdf/2403.03709)
- libEnsemble queries the scheduler for available nodes and **by default equally divides available
  compute resources among workers**; GPU resource sets are maintained separately so that CPU-only
  applications do not block GPU use by other workers — [libEnsemble Platform Specs](https://libensemble.readthedocs.io/en/main/data_structures/platform_specs.html)
- Manual override is supported via `platform_specs` or a named `platform`, with fields `mpi_runner`
  (mpich, openmpi, aprun, srun, jsrun, msmpi, custom), `cores_per_node`, `logical_cores_per_node`,
  `gpus_per_node`; anything not defined is auto-detected — [libEnsemble Platform Specs](https://libensemble.readthedocs.io/en/main/data_structures/platform_specs.html)
- `disable_resource_manager` turns off automatic resource detection and/or assignment, and
  `resource_info` overrides auto-detected resources — [libEnsemble libE_specs documentation](https://libensemble.readthedocs.io/en/latest/data_structures/libE_specs/libE_specs_resources.html)
- libEnsemble 1.6.0 (4 March 2026) added support for gest-api generators, including any Xopt (v3.0+)
  and Optimas generators, plus dictionary-style simulator functions and **simulation container
  support** — [libEnsemble release notes](https://libensemble.readthedocs.io/en/main/release_notes.html)
- Dakota is described in Sandia's own publication title as "a multilevel parallel object-oriented
  framework for design optimization" — [Sandia publication record](https://www.sandia.gov/research/publications/details/dakota-a-multilevel-parallel-object-oriented-framework-for-design-optimizat-2021-11-01/)
- Ray Tune's ASHA is recommended over synchronous HyperBand specifically because it **gives better
  parallelism and avoids straggler issues during eliminations** — [Ray Tune scheduler docs](https://docs.ray.io/en/latest/tune-schedulers.html)

### Inferences

- For this project's stated compute environment (Wayne State grid, Slurm, `reqp` partition for CPU
  work), libEnsemble's automatic `srun` detection and per-worker resource division is the lowest-
  friction way to turn a replication loop into a Slurm job that uses a whole node or several. The
  project's own CLAUDE.md constraints apply unchanged: `#SBATCH --output` resolves against the
  submit directory, and IPC must go under `/dev/shm` rather than `/tmp` — libEnsemble's worker
  communication is exactly the kind of thing the node `/tmp` sweeper has destroyed before.
- GPU is largely irrelevant to this workload unless the simulator itself is a GPU model. The
  replication workload described (Monte Carlo over subsets of tabular morphology measurements) is
  embarrassingly parallel across cores, and `joblib` or Ray would saturate a node with far less
  setup than libEnsemble. libEnsemble earns its complexity only at multi-node scale.
- The ordering for this project: `joblib`/`multiprocessing` for 128 designs; Ray for a single large
  node; libEnsemble when the job must span Slurm nodes.

### Gaps

- **SimOpt's parallelism is undocumented** on its GitHub landing page, its PyPI page and the
  readthedocs index. No claim should be made that SimOpt parallelises macroreplications.
- Dask was named in the brief and was not researched in this session.
- No source was found on GPU acceleration of any R&S or OCBA procedure specifically.
- libEnsemble's licence was not confirmed in this session (it is open source and Argonne-hosted, but
  the specific licence text was not retrieved).

---

## Cross-cutting staleness flags (for the report's "flag stale" requirement)

All dates in the first three tables below were verified on **2026-10-26** against primary metadata
endpoints — the GitHub REST API (`pushed_at`, the last commit to any branch, and `archived`), the
CRAN metadata database `crandb.r-pkg.org` (`Date/Publication`), and the PyPI JSON API — rather than
against listing or mirror pages. Two of my own earlier figures were wrong and are corrected here.

**Confirmed actively maintained (commit or release within the last 12 months):**

| Package | Version / last activity | Verified via |
|---|---|---|
| `simopt-admin/simopt` | commit **2026-10-15**, 79 stars; `simoptlib` 1.2.4, 22 May 2026 | [GitHub API](https://api.github.com/repos/simopt-admin/simopt); [PyPI](https://pypi.org/project/simoptlib/) |
| libEnsemble | 1.6.1, **20 July 2026** | [release notes](https://libensemble.readthedocs.io/en/main/release_notes.html) |
| irace | **4.5, 2026-09-15** (resolves the r-universe 4.4.3 conflict in CRAN's favour) | [crandb](https://crandb.r-pkg.org/irace) |
| SMAC3 | **2.4.1, 2026-09-10** | [PyPI JSON](https://pypi.org/pypi/smac/json) |
| `SMPyBandits/SMPyBandits` | commit **2026-06-19**, 426 stars (PyPI frozen at 2019) | [GitHub API](https://api.github.com/repos/SMPyBandits/SMPyBandits) |
| Dakota | 6.23, 26 Nov 2025, with 6.24 listed as newer | [Dakota news](https://dakota.sandia.gov/category/news/) |
| `spotpython` | **0.36.2, 2025-11-20** (confirmed; no 2026 release) | [PyPI JSON](https://pypi.org/pypi/spotpython/json) |
| `multcomp` | 1.4-26 / 1.4-30 | [r-universe](https://thothorn.r-universe.dev/multcomp) |

**Stale or dormant, flagged per the brief:**

| Package | Last activity | Note | Verified via |
|---|---|---|---|
| `czhhbp/OCBA` | commit **2019-03-23** (same day as creation), 1 star | A single-sitting dump, **7.5 years dormant**. Do not vendor. | [GitHub API](https://api.github.com/repos/czhhbp/OCBA) |
| `google-research/rliable` | **`archived: true`**, 2024-08-12, 878 stars | Dead by owner's choice, **and not a BAI tool** — it is a benchmark-evaluation statistics library | [GitHub API](https://api.github.com/repos/google-research/rliable); [PyPI JSON](https://pypi.org/pypi/rliable/json) |
| `selectiveInference` | CRAN **1.2.5, 2019-09-07** | No release in 7 years, but CRAN-installable and passing checks 2026-06-08 | [crandb](https://crandb.r-pkg.org/selectiveInference) |
| `Alanthink/banditpylib` | commit **2022-07-21**, 29 stars | **4+ years dormant**, no releases, not on PyPI. The only library found with real BAI coverage. | [GitHub API](https://api.github.com/repos/Alanthink/banditpylib) |
| `ashr` | CRAN **2.2-63, 2023-08-21** | Borderline at the brief's threshold | [crandb](https://crandb.r-pkg.org/ashr) |
| `amandaforde/winnerscurse` | commit **2024-03-07**, 5 stars, v0.1.1 | **Confirmed not on CRAN.** Dormant, unvetted implementation of peer-reviewed methods. | [GitHub API](https://api.github.com/repos/amandaforde/winnerscurse); [crandb returns not_found](https://crandb.r-pkg.org/winnerscurse) |
| `daveckman/posterior-stopping-rules` | commit **2021-08-24**, 0 stars, no licence | Frozen single-paper code | [GitHub API](https://api.github.com/repos/daveckman/posterior-stopping-rules) |

**Corrections to earlier findings in these notes, both caused by trusting listing pages over the API:**

- `SMPyBandits` was recorded as "repo last updated 30 April 2024" from a GitHub topics listing. The
  API gives `pushed_at` **2026-06-19**. The repository is alive; only its PyPI release is frozen.
  The practical consequence is that **SMPyBandits, not `banditpylib`, is the live bandit codebase**,
  which is the reverse of what the PyPI dates alone imply.
- `spotpython` 0.36.2 / 2025-11-20 was flagged as possibly lagging. The PyPI JSON API confirms it
  exactly: that is the current release and there is no 2026 one.

**Unverified maintenance status (no API check performed):**
- `best-arm` (PyPI) — MIT, last updated 2025-08-06, third-party health score 38/100 — [depscope](https://mcp.depscope.dev/pkg/pypi/best-arm)
- `daveckman/RS_after_Search`, `daveckman/plausible-screening` — single-paper code — [Eckman software page](https://eckman.engr.tamu.edu/software-and-code)

Method only, no software located:
- OCBA as a packaged library in R
- Track-and-Stop; Top-Two Thompson Sampling; LUCB
- Andrews-Kitagawa-McCloskey "Inference on Winners"
- Knockout-tournament R&S; PASS; Clustering-and-Conquer
- KN (Kim-Nelson), Rinott, Paulson, Good Selection Procedure, Bonferroni indifference-zone — **none
  of these were found in any installable package in this session**

## What the verified dates change about the recommendation

The date checks did not overturn the survey's shape; they hardened it in one direction. **Every tool
in this space that is alive is an orchestration or configuration tool, and every tool that
implements a selection procedure proper is dormant, unreleased, or both.** libEnsemble (July 2026),
SimOpt's harness (commit 11 days before this research), irace (Sept 2026) and SMAC3 (Sept 2026) are
all current. The actual R&S and BAI procedure code — `czhhbp/OCBA` (March 2019),
`banditpylib` (July 2022), the single-paper R&S repos (2021) — is uniformly dormant, and `rliable`
is formally archived.

The practical conclusion for this project is therefore stronger than "pick a package": **there is no
package to pick for the selection rule itself.** The defensible build is a live orchestration layer
(libEnsemble on Slurm, or Ray/joblib on one node) driving a short, self-written OCBA or Sequential
Halving routine, checked against `spotpython.get_ocba` and against the Chen & Lee book's worked
example, with the winner's reported value coming from held-out replications rather than from any
post-selection correction package. That last point matters most given that the one directly usable
correction package, `winnerscurse`, turns out to be off-CRAN, at v0.1.1, with 5 stars and no commit
since March 2024 — an unvetted implementation is exactly the wrong thing to put between this
project and a published number.

## Note on metadata sources

An earlier draft of these notes recorded several commit dates as unretrievable because
`api.github.com` failed to resolve from Windows (`getaddrinfo ENOTFOUND`). That was the known
IPv6 DNS stall, not a block: the same requests succeed immediately through
`wsl -e bash -lc 'curl -4 ...'`, which is the project's standing rule for network work. All GitHub,
CRAN and PyPI figures in this file were then verified that way on 2026-10-26 against the REST/JSON
APIs directly. Two earlier figures taken from HTML listing pages proved wrong (see the Corrections
subsection above), which is a reminder worth carrying: **a GitHub topics page or a CRAN mirror can
be years out of date, and for a staleness judgement the API field `pushed_at` is the only reliable
source.**
