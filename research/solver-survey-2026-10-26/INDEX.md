# Solver survey, 2026-10-26

What mathematical problem this package's measure-set search actually is, and what software
exists to solve it. Six parallel literature surveys, then seven adversarial verifiers whose
job was to **refute** the decision-changing claims the surveys produced.

**All seven claims came back needing correction.** Nothing here should be read without
`adversarial-verification.txt` beside it, because the corrections overturn parts of the notes.

## Read in this order

| File | What it is |
|---|---|
| `REPORT.md` | **Start here.** The synthesis, with the verifiers' corrections already folded in. Answers the naming question and gives a prioritised adopt/ignore list |
| `adversarial-verification.txt` | The seven verdicts verbatim: what was checked, what was wrong, what is still open. The authority wherever it conflicts with a notes file |
| `simulation_optimization_ocba.md` | Discrete optimisation via simulation, ranking and selection, OCBA, best-arm identification, the winner's curse |
| `exact_mip_solvers.md` | Mixed-integer linear, quadratic, conic and semidefinite solvers; best-subset selection; academic licences; GPU |
| `robust_and_minimax.md` | Robust optimisation, distributionally robust optimisation, semi-infinite programming, sensitivity analysis, partial identification |
| `submodular_and_design.md` | Submodular maximisation and its guarantees, sensor selection, optimal experimental design, class separability |
| `bayesian_and_dfo.md` | Bayesian optimisation over discrete and mixed spaces, derivative-free optimisation, noise handling |
| `neural_surrogates.md` | Set-function learning, amortised optimisation, GFlowNets, differentiable subset relaxations, simulation-based inference |

## The answer in six lines

- The problem is **robust (maximin) discrete optimisation via simulation**, and inside it a
  **fixed-budget ranking-and-selection problem over an enumerable candidate set**. The inner
  continuum over `r` is a one-variable **semi-infinite program**; the reporting frame is
  **Manski partial identification**.
- One evaluation of `A(S, r)` costs **7.24 s**, measured. So enumeration is free to `m = 9`,
  one night at `m = 12`, and infeasible at `m = 17`.
- **At the 7 measures in use there is no optimisation problem.** Enumerate.
- Above about `m = 12`, adopt **`sim-tools` 1.3.0** (MIT) for OCBA/OCBA-m/KN/KN++ — and pin the
  commit and write your own tests, because its `ovs` module is 2021 code under a 2026 version
  string with no tests of its own.
- **Do not claim a `(1 - 1/e)` guarantee.** Value of information is not submodular even in
  Naive Bayes models, and measured submodularity ratios for this objective were 0.017-0.086.
- The deficit was never in the optimiser. It was in the inference, and it is now fixed in
  `covariance.py`: identified set, Imbens-Manski interval, a claim about the **sign**, a
  measured grid error, and a measured coverage check.

## What this survey changed in the code

| Commit | What |
|---|---|
| `cc8360f` | identified set, Imbens-Manski interval, sign-invariance with a crossing point |
| `bdcfd5b` | measure the grid's error instead of asserting monotonicity -- which turned out false |
| `01ad082`/`7844707` | measure the interval's coverage; a 0.02 hidden dip takes it from 0.95 to 0.42 |
| `400e73a` | the 7.24 s per-evaluation measurement and the enumeration table |

## Method, and its limits

Each survey was told to prioritise industry-trusted software first and to flag research code as
such, to give a maintenance date for everything named, and to say "I could not verify this"
rather than guess. Dates come from the authenticated GitHub REST API, the GitLab API, the PyPI
JSON API and crandb, queried through WSL on 2026-10-26 — Windows-side DNS stalls on these hosts,
which initially made several live packages look dead.

Two limits worth knowing. A repository's `pushed_at` is **not** evidence the submodule you
import is maintained; use path-filtered commit queries. And several of these conclusions rest on
a single verifier's own numerical experiment rather than on a published source — those are
labelled as such in `adversarial-verification.txt` and should be reproduced before they go into
a manuscript.
