# Stop shopping: this is robust ranking-and-selection

Maximizing `A(S, r)` over subsets `S` of anatomical measurements while taking the worst case over an
unidentified correlation `r` is a **robust (maximin) discrete optimization-via-simulation problem**, and
within that literature specifically a **fixed-budget ranking-and-selection (R&S) problem over an
enumerable candidate set**, where each candidate subset is an "alternative" whose value is a probability
estimable only by replication ([Hong, Fan & Luo, *Frontiers of Engineering Management* 8(3):321-343,
2021](https://arxiv.org/pdf/2008.00249)). The outer worst-case layer makes it **robust R&S**; the inner
continuum over `r` makes it a **semi-infinite program in one variable**, which your grid sweep
discretizes; and the reporting frame — the one you adopted today — is **partial identification**, where
`A(S)` has identified set `[min_r A(S,r), max_r A(S,r)]` and the Imbens-Manski construction gives an
interval covering the *true value* rather than the identified set ([Imbens & Manski, *Econometrica*
72(6):1845-1857, 2004](https://econometricsociety.org/publications/econometrica/2004/11/01/confidence-intervals-partially-identified-parameters)).

**`A` IS THE SIMULATOR. This was measured, not left to the reader.** An earlier draft of this report
forked on "what is `A`?" and told you to resolve it. That was the wrong instruction: `A` is defined in
`bordercall/covariance.py`, and timing the function the sweep actually calls settles it. One evaluation
of `A(S, r)` — train the junction model on 600 synthetic columns, then score six phenotypes at 400
windows each — costs **7.24 seconds** on this machine (2.40 s train, 4.84 s evaluate, `n = 2400`,
`m = 7`). So:

| `m` | subsets, both junctions | enumeration cost |
|---|---|---|
| 7 | 127 | **0.5 h** — free |
| 9 | 511 | 2.1 h — free overnight |
| 12 | 4,095 | 16.5 h — one night |
| 17 | 131,071 | **22 days** — not enumerable |

That resolves every branch below. The closed-form Mahalanobis or Bhattacharyya separability of the
published Gaussians runs at about 25 microseconds per subset, so it is **290,000 times cheaper** and is
*not the same function* — it is a surrogate. Use it as a screen, never as the answer: rank all subsets by
the closed form in seconds, then spend simulator budget only on the top candidates, and report the final
accuracy from the simulator on held-out draws. The two numbers must never be quoted interchangeably.

The operational consequence: **at the 7 measures currently in use, enumeration is half an hour and there
is no optimization problem to solve.** OCBA and `sim-tools` earn their keep at `m` of roughly 12 and
above, which is where this is heading if the ground set grows to every SPINEPS-measurable quantity. Adopt
it then, or now to have it tested before you need it — but do not let it displace enumeration at `m = 7`,
where exhaustive search is exact, returns the whole ranked distribution rather than an argmax, and is the
natural outside check on anything a procedure returns.

On either branch the software answer is small: **one package supplies the missing component; the rest of
the table is cross-checks and plumbing.** Everything else is inapplicable (robust and distributionally
robust optimization packages, mixed-integer conic solvers, submodular greedy libraries, optimal-design
packages) or a bias channel you do not need (Bayesian optimization, GFlowNets, differentiable
relaxations). Your architecture is right; the deficit is in the sweep's inference, and one of its defects
is one the obvious sanity check actively hides.

## The practice has three names, and a published precedent

The reason this question is hard to search is that four distinct literatures each claim a piece of it,
and the one that owns the whole thing is the one a surgeon would never think to search.

**The right name for the whole problem: discrete optimization via simulation, and inside it, ranking and
selection.** The defining features are a finite enumerable candidate set, a scalar value per candidate
estimable only by Monte Carlo, a real per-replication cost, and a requirement to both pick the best and
report an honest estimate of its value. Hong, Fan and Luo's review replaces the older
frequentist/Bayesian split with a **fixed-precision versus fixed-budget** taxonomy: fixed-precision
procedures (KN, Rinott, Paulson) deliver a statistical guarantee on the selected alternative, while
fixed-budget procedures (OCBA and relatives) spend a given budget optimally ([arXiv
2008.00249](https://arxiv.org/pdf/2008.00249)). You are in the fixed-budget regime. The machine-learning
name for the identical problem is **best-arm identification**, fixed-budget or fixed-confidence; the OR
name is the one with the mature procedures. Your worst-case layer puts you in the **robust R&S**
sub-branch, where the goal is "the alternative with the best worst-case mean performance," and if you
ever put a prior on `r` instead, the exact formal object is the **most probable best** — the solution
whose probability of being optimal is largest, a nested R&S problem with an inner procedure per input
model and an outer preference-probability comparison ([Kim, Kim & Song, *Operations Research*, 2024, DOI
10.1287/opre.2022.0343](https://arxiv.org/pdf/2207.07533)).

**The method itself — enumerate every subset and score it — has three names and no settled one.** In
remote sensing it is *band selection by exhaustive search with a separability criterion*; in pattern
recognition it is *feature selection by divergence or separability criteria*; in the design literature it
is *exact discrete optimal design by complete enumeration*. Give all three rather than invent a label,
and note that the first of them supplies the citation you will need when a reviewer asks why a `for` loop
counts as a method: exhaustive search over all combinations of one to four bands with a separability
criterion is standard, accepted practice in a field that has been doing this for decades ([EARSeL
2006](https://www.fc.up.pt/pessoas/andre.marcal/papers/EARSeL2006_265.pdf); the metric comparison in
[SPIE JARS 11(4)
046010](https://astronomicaltelescopes.spiedigitallibrary.org/journals/journal-of-applied-remote-sensing/volume-11/issue-04/046010/Spectral-region-identification-versus-individual-channel-selection-in-supervised-dimensionality/10.1117/1.JRS.11.046010.full)
covers Euclidean, Mahalanobis, divergence, Bhattacharyya, transformed divergence and
Jeffries-Matusita, which is a ready-made menu for a criterion-sensitivity check).

**The near miss worth knowing: cardinality-constrained maximin class-separability selection.** If your
objective is the *closed-form* separability of the published Gaussians rather than a simulated
classifier's accuracy, the problem has a second name and a completely different answer. The published OR
name for the structure that formulation lands in is **semi-continuous quadratic programming**, the class
for which perspective and lift-and-convexification tightenings were developed. This matters because it is
the only version of your problem a commercial solver can prove anything about.

**The near misses to discard, with reasons.** *Submodular maximization* is the first thing anyone reaches
for, and it does not apply: Krause and Guestrin prove that "decision-theoretic value of information is not
submodular, even in Naive Bayes models" (Proposition 9, stated p. 584, proved p. 588, [JAIR
35:557-591](https://arxiv.org/pdf/1401.3474)), and their Theorem 3 goes further — in Naive Bayes models
merely *evaluating* that objective is #P-complete and "hard to approximate to any factor unless P = NP." A
class-separability criterion such as minimum pairwise Mahalanobis distance is non-submodular for two
further, independent reasons: squared Mahalanobis distance for a single fixed class pair is monotone but
non-submodular through the classic suppressor-variable effect, and the minimum over pairs destroys
submodularity by itself, even when its components are modular. Both were reproduced numerically during
verification of these notes (with `delta=(1,0)` and `Sigma=[[1,rho],[rho,1]]`, the gain from adding
coordinate 2 is 0 on its own and 4.26 once coordinate 1 is present, at `rho=0.9`). So **do not report a
(1 - 1/e) guarantee for this objective** — not from `apricot`, not from `submodlib`, not from anything. The
honest fallback, Das and Kempe's `(1 - e^(-gamma))` bound ([JMLR 19, paper
16-534](https://jmlr.org/papers/v19/16-534.html), Theorem 6), formally applies but reports almost nothing
here: `gamma` is a minimum over exponentially many set pairs that can only be bounded, the published bounds
are for the linear-regression `R^2` objective, and measured `gamma` for min-pairwise Mahalanobis on random
instances was **0.017 to 0.086**, i.e. a guarantee of 2 to 9 percent of optimum. For a plain Bayes-error
instance with a skewed prior, measured `gamma` was exactly 0 and the bound is vacuous rather than weak. For
the general robust max-min problem there is no polynomial-time multiplicative guarantee at all unless
P = NP ([Krause, McMahan, Guestrin & Gupta, JMLR 9:2761-2801,
2008](https://www.jmlr.org/beta/papers/v9/krause08b.html), Theorem 3); only SATURATE's bicriteria
guarantee survives. *Distributionally robust optimization* does not apply either, for a reason sharper than
the one usually given: `r` is a single fixed population constant, so there is no distribution of `r` to be
ambiguous about, and the DRO layer is inapplicable rather than merely redundant. *Best-subset selection*
in the Bertsimas-King-Mazumder sense ([*Annals of Statistics* 44(2),
2016](https://arxiv.org/pdf/1507.03133)) is a different objective — sparse regression, not class
separability — and its claimed scale, "n in the 1000s and p in the 100s to provable optimality in minutes,"
is an order of magnitude above your `m`.

## Four numbers decide this report; one is now measured and three are still asserted

`m` (the ground set), `k` (the subset size), `C` (the number of classes) and the per-evaluation cost
decide everything downstream. The per-evaluation cost is now **measured at 7.24 s** (see the lede), which
settles the fork. The research notes still disagree with themselves on `m`, `k` and `C` — fix those
before quoting any figure below.

**Per-evaluation cost — RESOLVED at 7.24 s for the simulator.** The two regimes below are kept because
the cheap one is the right *screen* for the expensive one, not because the choice is still open. *Closed
form, about 25 microseconds per subset*: measured
single-core on this machine with BLAS threads pinned to one, **all 511 subsets at `m=9` in 0.006 s; all
131,071 subsets at `m=17` in 1.75 s**; `m=20`, all 1,048,575 subsets in 15.95 s. Even the worst fixed-`k`
case in a 7-to-17 range, `C(17,8)=24,310`, is well under a second. Scaling further: `C(25,12)=5,200,300`
in 93 s and `C(30,15)=155,117,520` at a measured 40,028 subsets/s, about 65 minutes. In that regime you
need a `for` loop, not a solver, and what enumeration buys that no solver does is **exactness by
construction** (no relaxation, big-M, tolerance or optimality gap) plus the **entire ranked score
distribution**, which is worth more to a project with your error history than an argmax. One correction
worth carrying: do not quote the all-subset-sizes figure for `m=30` (previously stated as 8 hours
single-core; the arithmetic is right, 7.8 h by independent extrapolation). It prices a computation nobody
needs, because the closed-form score is monotone non-decreasing in `S`, so the unconstrained argmax over
all sizes is the full set. *Simulator, measured at 7.24 s per evaluation*: the same enumeration,
scored at both junctions, costs **0.5 h at `m=7`, 2.1 h at `m=9`, 16.5 h at `m=12` and 22 days at
`m=17`** — and those figures already include the six `r` grid points and the 2,400 evaluation windows,
because the 7.24 s is the whole `train`-plus-`evaluate` cycle the sweep calls. So the crossover is sharp
and it is not where the earlier draft guessed: **enumeration is free up to `m = 9`, survivable overnight
at `m = 12`, and infeasible at `m = 17`.** Above roughly `m = 12` the binding constraint becomes simulator
throughput and the discipline is budget allocation, not branch-and-bound.

**`m` — the notes say 7 to 17 in one place and 30 in another, and the difference is qualitative.** The
MIP notes price `m=30`; the DFO notes assume length 7 to 30. At `m=30` the all-sizes simulator
enumeration is 2^30 - 1 evaluations, about 34 years at 1 s/eval, and even fixed `k=15` is 155 million
evaluations, about 4.9 years — decades, not 91 days. At `m=30` on the *closed-form* branch, an exact
mixed-integer sensor-selection formulation reports optimal solutions "for systems with 30 to 50 states in
seconds" ([Dutta, Wilde & Smith, arXiv 2304.02692](https://ar5iv.labs.arxiv.org/html/2304.02692)) —
which means a solver is plausibly *faster* than enumeration there, so the earlier claim that enumeration
"beats every optimization solver and it is not close" must come out. No solver has been run on this
objective in either direction; the comparison is unmeasured.

**`C` — the notes say 6 classes in the MIP derivation and 12 to 24 vertebral classes in the design
notes.** Every number downstream scales as `C(C-1)/2`: 15 pair blocks at 6 classes, 66 at 12, 276 at 24.
The MIQCP's continuous `w` variables are pairs x `m`, so 450 at 6 classes and `m=30` becomes 8,280 at 24
classes. The per-subset enumeration cost rises with the pair count too, since the `k x k` solve is shared
across pairs but each quadratic form is not — so the timings above are 6-class timings and should be
scaled before being quoted at 24 classes.

**`k` is the one your sweep already treats as a variable, and whether it is a real question depends on
the fork.** For the population Mahalanobis score, no: monotonicity makes the full set optimal (0
violations in 2,000 random coordinate additions). But for a classifier accuracy estimated with finite
synthetic training data, monotonicity can fail, because adding a measurement can lower cross-validated
accuracy through variance. If your `A` is an estimated accuracy rather than a population separability,
the all-`k` sweep is a genuine problem and an interior optimum is real. Check it empirically on the sweep
you already have; it also determines whether Das and Kempe's bound applies at all, since Theorem 6
requires a monotone objective and the authors state the non-monotone extension is unlikely to carry over.

**At `m=30` the binding problem is statistical, not computational — and that is where the compute should
go.** With 10^8 subsets scored against a `Sigma` estimated from a finite sample, the maximum of the score
is badly upward-biased by selection; Flusser and Suk observed in 1998 that the separability gain flattens
and then the chosen features "become too noise-sensitive" ([Kybernetika 34(4),
1998](https://www.kybernetika.cz/content/1998/4/411/paper.pdf)). Nested cross-validation or a bootstrap
over the whole enumeration is feasible at these timings and is the thing to spend compute on — not a
solver licence.

**GPU: no, and the reason is specific.** GPU acceleration arrived in 2026 for **LP and SDP first-order
methods and for MIP primal heuristics only**. Mittelmann now runs a GPU column in the LP-feasibility
benchmark where the GPU codes are at or ahead of the best CPU codes
([plato.asu.edu/ftp/lpfeas.html](https://plato.asu.edu/ftp/lpfeas.html)), but NVIDIA's own FAQ says cuOpt's
MILP is still beta, that "full MIP optimality remains in active development," and that cuOpt's design runs
primal heuristics on the GPU with the **dual bound computed on the CPU** ([NVIDIA cuOpt
FAQ](https://perspectives.nvidia.com/cuopt/task/faq/milp-tools-gpu-primal-heuristics-fast-solutions/)).
Nothing proves MIP optimality on a GPU, and at 7 to 30 binaries the models are tiny regardless. The only
honest GPU case is if the *simulator itself* is GPU-bound, which is a question about `gmsap`/`gvohp`
throughput and has nothing to do with any solver in this report. **Exact or approximate: exact, by
enumeration.** **Deep learning or pure statistics: pure statistics**, decisively — see the dismissals
below.

## The exact convex program exists, and it is the wrong program for your objective

This is the part of your question with a clean, surprising, technically satisfying answer — and a caveat
that disqualifies it.

If the score is the closed-form max-min Mahalanobis separability, the problem is **exactly a convex
mixed-integer quadratically constrained program (MIQCP), equivalently a mixed-integer second-order cone
program (MISOCP)** — no semidefinite program required. The mechanism is the variational identity
`dMu_S^T (Sigma_SS)^-1 dMu_S = max_w { 2 w^T dMu - w^T Sigma w : w_i = 0 for i not in S }`, whose maximizer
is `w* = (Sigma_SS)^-1 dMu_S`. Verification confirmed this identity to machine precision (4.9e-16 relative
over 300 random draws, and 9.6e-14 against an independent L-BFGS-B maximization), and confirmed that it
yields the *marginal* precision `(Sigma_SS)^-1` — the statistically correct object, since
`X_S ~ N(mu_S, Sigma_SS)` — and not the plausible-looking alternative `(Sigma^-1)_SS`, which differed by up
to 120 percent (22.05 against 32.57 in one instance). The program is

```
maximize   t
s.t.       t + w_p^T Sigma w_p <= 2 w_p^T dMu_p      for each class pair p
           z_i = 0  ->  w_{p,i} = 0                   for all p, i   (indicator / SOS1)
           sum_i z_i = k,   z in {0,1}^m
```

Each pair constraint is Gurobi's always-recognized-convex form `x^T Q x + q^T x <= b` with `Q = Sigma` PSD
([Gurobi constraint
documentation](https://docs.gurobi.com/projects/optimizer/en/current/concepts/modeling/constraints.html)).
At 6 classes that is 15 pair blocks, so at `m=30` the model is 30 binaries plus 450 continuous `w`
variables plus one epigraph variable, rising to roughly 916 continuous if the cones are written out
explicitly as `u_p = L^T w_p` — and to 8,280 `w` variables at 24 classes, which is the unresolved
parameter above. Verification solved the formulation by exhaustive enumeration over `z` at `m=9`,
`C(9,4)=126` subsets, and reproduced the brute-force optimum and argmax exactly.

**Four repairs that the obvious statement of this gets wrong, each of which produces a finite, plausible,
wrong answer — your project's named failure mode.** First, the cardinality constraint `sum_i z_i = k` is
mandatory, not cosmetic: the objective is monotone non-decreasing in `S`, so without a budget the optimum
is trivially the full measurement set. Second, `Sigma` must be **strictly** positive definite, not merely
PSD: if `dMu_S` has any component outside `range(Sigma_SS)` the per-pair inner maximum is `+infinity`
(verified by direct ray evaluation, the objective growing 4e0 to 4e6 along the null direction), so a
rank-deficient pooled covariance makes the program unbounded rather than wrong. Third, and most important,
**impose `w_{p,i}=0` with indicator or SOS1 constraints, never a hand-chosen big-M.** A too-small `M`
truncates `w`, understates every subset's score, and changes the winner silently: in a sweep of 60 random
instances with deliberately small `M`, **44 returned the wrong argmax with a finite plausible value and no
error** (one seed reported 2.07 at the wrong subset when the true optimum was 7.42). A rigorous
subset-independent bound does exist, `M = max_p ||dMu_p||_2 / lambda_min(Sigma)` by Cauchy eigenvalue
interlacing, but on an ill-conditioned `Sigma` it measured 5.8e6 against a true requirement of 13.6 — weak
enough that branch-and-bound would trickle rather than converge. Quote it as a fallback only. Fourth, the
trick is **direction-specific**: it works because the outer problem is a *maximum* of a *minimum*, the pair
blocks are independent, and `min_p max_{w_p} = max_w min_p` holds exactly with no duality gap (verified to
9e-15). The same identity would *not* produce a convex program for minimizing the maximum over pairs. Do
not present it as a general device.

**Which solvers, and on what licence — read the licence clause before you plan around it.** For
MIQCP/MISOCP there is no independent 2026 head-to-head including the best-known commercial codes: IBM and
FICO demanded removal from Mittelmann's benchmarks in 2018 and Gurobi withdrew in August 2024, so the
tables measure "best among participants"
([plato.asu.edu/bench.html](https://plato.asu.edu/bench.html)). Among participants, **COPT 9.0.0 solves 47
of 47 MISOCP instances** with times from 1 s to 3,321 s and a median of 16 s, while MOSEK 11.2.3 times out
on 10 of 47, SCIP 10.0.0 on 8 of 47 and KNITRO 16.0.0 on 14 of 47
([plato.asu.edu/ftp/misocp.html](https://plato.asu.edu/ftp/misocp.html), page dated 2026-10-23). The
practical choice is licensing, and the licence detail decides it for your environment: **Gurobi 13.0**
(released 2025-11-18, supported to November 2028; `gurobipy` 13.0.3 on PyPI 2026-08-25) reports MIQCP 13.2
percent faster than 12.0 overall and 25.8 percent on models over 100 s, and offers two free academic
licences that are not interchangeable — the *Named-User* licence is unlimited in quantity but is **one
user, one machine, no containers, one year, activated on the academic network**, while the
container-capable *Academic WLS* licence is **90 days and two concurrent sessions** ([Gurobi
newsroom](https://www.gurobi.com/company/newsroom/gurobi-releases-version-13-0-with-improved-performance-and-new-solving-capabilities);
[academic program](https://www.gurobi.com/academia/academic-program-and-licenses/)). Your compute is
Apptainer inside Slurm, so the named-user licence does not work there; plan on Academic WLS and its 90-day
clock, or run the model on a workstation. **MOSEK 11.2** (`mosek` 11.2.6 on PyPI 2026-10-08) gives a free,
size-unrestricted Personal Academic License ([mosek.com](https://www.mosek.com/products/academic-licenses/)).
For a third solver with no licence at all, **SCIP 10.1 (Apache-2.0, released 2026-09-18) solves MIQCP** and
appears in Mittelmann's convex-discrete table at 14 of 31 — in that run driven with CPLEX as its LP solver,
so a pure open-source build is untimed
([plato.asu.edu/ftp/convex.html](https://plato.asu.edu/ftp/convex.html)). COPT's 9.x binary is not on PyPI.
Write the model once in **CVXPY** (1.9.3, PyPI 2026-09-19; repository pushed 2026-10-24) and solve it with
two of these — two independent solvers on one model is a one-argument change and exactly the outside check
your project's history demands. **Mixed-integer semidefinite programming is not the binding capability**,
which is fortunate: there is no MISDP table on Mittelmann's site at all, MOSEK is confirmed not to support
it, **whether COPT 9.0 added MISDP was not verified either way** (its user guide's mixed-integer list omits
it, which is suggestive but not a statement), and the only verified open routes are SCIP-SDP 4.4.0
(November 2025) and Pajarito.jl 0.8.3 (2026-07-08). Note also that the common claim "E-optimality requires
an SDP" is true only of the *continuous relaxation* over weights on the simplex (Boyd & Vandenberghe,
*Convex Optimization*, section 7.5, eq. 7.27); the discrete k-subset problem is NP-hard and A- and
D-optimality have convex relaxations too, so SDP is not distinctive to E-optimality.

**The convex artifact actually worth your time is not this program — it is Joshi and Boyd's bound.** Their
convex relaxation of sensor selection returns a subset *and a bound on the best performance achievable by
any selection* ("Sensor Selection via Convex Optimization", *IEEE Transactions on Signal Processing*, 2009;
[Boyd's page](https://stanford.edu/~boyd/papers/sensor_selection.html)). You solve the relaxation, get an
upper bound, and compare your chosen subset against it: if the gap is small you know your subset is
near-optimal **without appealing to any submodularity claim at all**. For a project whose standing rule is
to check against something outside the computation, an upper bound on the achievable optimum is worth more
than a second exact formulation of the same objective, and re-implementing the relaxation in CVXPY is a
small job. The reference code is MATLAB from May 2008 (`sens_sel_ex1.m`, `sens_sel_loc.m`) and no Python
port of `sens_sel_approxnt` was located; the original method's O(n^3) cost is irrelevant at your size.

**And now the caveat on the MIQCP.** None of it reaches your objective if `A` is the simulator. `A(S, r)`
is then a Monte Carlo accuracy from a synthetic-column simulator; there is no algebraic form to hand a
solver, and the closed-form Mahalanobis score is a *surrogate* for it, not the same function. Substituting
the one for the other would be the same class of error as substituting a maximum extent for a diameter. If
you want the MIQCP, you want it as an independent cross-check on the closed-form surrogate — a second
implementation of a quantity you can also compute by enumeration — not as the thing that answers your
question.

## Adopt sim-tools; write your own tests; ignore the rest

The honest finding about the industry-trusted tier is that **it does not contain the selection rule** —
the live commercial and national-lab tools in this space are orchestration layers, and the procedures
themselves live as modules inside maintained general-purpose simulation packages. Do not pad that into a
survey.

| Priority | Package | Version / date | Licence | What it gives you |
|---|---|---|---|---|
| **1. Adopt** | `sim-tools` | PyPI 1.3.0, **2026-06-24**; repo pushed 2026-07-17; 8 releases since 2025-11 | MIT | OCBA, OCBA-m, KN, KN++ as `sim_tools.ovs.fixed_budget` and `sim_tools.ovs.indifference_zone` |
| 2. Harness + CRN | `simoptlib` / `mrg32k3a` | simoptlib 1.2.4, 2026-05-22; repo pushed 2026-10-15. **`mrg32k3a`'s own release date was not verified** | MIT | Macroreplication bookkeeping and stream/substream CRN. **No R&S solvers** |
| 3. Orchestration | libEnsemble / Ray / `joblib` | libEnsemble 1.6.1, **2026-07-20** / ray 2.59.0, 2026-10-02. **libEnsemble's licence was not confirmed; `joblib`'s version was not checked** | — | Fan replications across Slurm nodes or one node |
| 4. Cross-check (R) | `irace` | CRAN 4.5, **2026-09-15**; GitHub HEAD 2026-10-22 | GPL | Racing elimination (Friedman, Wilcoxon, corrected paired t) |
| 5. Surrogate check | `spectral` | PyPI 0.25, 2026-07-25; repo 2026-09-04 | MIT | `bdist` / `bdist_terms`, Gaussian Bhattacharyya |
| 6. Conic cross-check | CVXPY + Gurobi 13.0 / MOSEK 11.2 / SCIP 10.1 | 1.9.3, 2026-09-19 / 2025-11-18 / 11.2.6, 2026-10-08 / 2026-09-18 | Apache / free academic / Apache-2.0 | The MIQCP and the Joshi-Boyd bound, on the closed-form surrogate only |
| 7. Reporting (R) | `multcomp` | 1.4-26 / 1.4-30 | GPL | Simultaneous intervals via `glht()`. **Hsu's MCB is not a shipped procedure** — build the contrast matrix yourself |

One more package, `PyPRS` (PyPI 1.0.0, 2025-07-19; no commit since 2025-10-20; MIT), advertises GSP,
PASS, KT, FBKT and Rinott constants with an INFORMS JoC artifact. It appears nowhere in the research notes
and **it was not installed or run here, and its artifact claim was not checked** — so it is a lead, not a
recommendation. Verify it yourself before leaning on it, and until then treat `sim-tools` plus your own
code as the whole stack.

`sim-tools` is the correction that most changes the advice in these notes, which had concluded there was no
package for the selection rule. There is. OCBA, OCBA-m, KN and KN++ are the package's advertised feature
number one, with a current user-guide tutorial, a Zenodo DOI (10.5281/zenodo.4553641), CI and a changelog.
Verification installed the wheel and ran it on a known-truth instance of five Gaussian designs with true
means 1 through 5: **KN returned index 4 — the fifth design, true mean 5 — with allocations 9/10/12/56/57,
screening out the inferior designs and concentrating the budget on the two contenders; OCBA returned the
same, and OCBA-m with `m=2` returned the true top-2.** The OCBA allocation ratios matched an independent
derivation of Chen and Lee's formulas and matched `spotpython.get_ocba` exactly. **Then write your own
tests**: a smoke test on one seed is not validation of the stopping rule or the attained probability of
correct selection, and the `ovs` module carries the trap in the first row of the table below. Two further
honesty constraints on how you present it. **No source quantifies OCBA's budget saving over equal
allocation** — the commonly repeated claim that it needs a fraction of equal allocation's budget could not
be sourced, so adopt OCBA for the principle and do not attach a number to the benefit. And the surviving
negative claim worth a methods section is narrower than "no package exists": there is no maintained
*standalone* R&S or OCBA package, and the single-purpose efforts are all dormant or closed — `czhhbp/OCBA`
was created and abandoned on 2019-03-23, `jeffhonglab/PySOBA` last committed 2021-07-31, `spotPython`'s
repository was **archived 2026-01-12**, and the R sibling `SPOT` was **removed from CRAN on 2024-04-20**. A
keyword sweep of the complete CRAN index (25,529 packages) returned 41 hits and no OCBA or simulation-R&S
package; `irace` is the only live CRAN package implementing a noisy-selection elimination rule.

**The optimal-design and sensor-selection shelf: nothing to adopt, two things to cross-check against.**
This family is the closest-named software to your problem and it still does not fit. **PyOED** (Argonne,
BSD, GitLab-hosted, not on PyPI) advertises greedy, stochastic, constrained and robust binary optimizers,
which reads like exactly the right package — but its GitLab "last activity 2026-10-22" is the
`last_activity_at` field and the event behind it is an opened issue; its last **code** commit on `main` is
2026-08-24; and inside `pyoed/optimization/binary_optimization/` only the greedy optimizer is implemented
(1,486 lines, plus a Federov exchange optimizer), while the stochastic, constrained and robust modules are
29-line deprecation shims re-exporting binary-REINFORCE classes that now live under `policy_optimization/`.
Greedy on a non-submodular objective is the one thing this report tells you not to do, so PyOED is a
*stop*, not an adopt. **PySensors** (`python-sensors` 0.4.3, PyPI 2026-02-17, MIT, maintained; JOSS
10.21105/joss.09265) is the closest named problem in the whole inventory — its SSPOC mode is sparse sensor
placement *for classification* — but it is data-driven: it needs a POD/SVD basis and a fitted linear
classifier, so feeding it synthetic draws from your known Gaussians imports Monte Carlo error into a
problem that has a closed form. That leaves two genuine cross-checks if you ever reframe the objective as
D-, A- or I-optimality of a linear model: **`AlgDesign::optFederov`** (CRAN 1.2.1.2, 2025-04-06, GPL),
which picks `nTrials` points from a candidate list by D, A or I and reports the criterion rather than
inferring it — the natural independent implementation to check any design-criterion computation against —
and **`pyDOE3`** (PyPI 1.6.2, 2026-01-12) with its `doe_optimal` module, or **`skpr`** (CRAN 1.9.2,
2025-09-30) in R. Neither optimises class separability; mapping your question onto D/A/I is a modelling
decision, not a software one.

**Derivative-free optimization: one clean finding, and it closes the category.** The DFO column splits
and nothing in it does both halves of your problem. **Noise-aware but continuous**: Py-BOBYQA (1.5.0,
2024-09-16, GPL-3.0+) and DFO-LS (1.6.5, 2026-03-23, GPL-3.0+) both expose `objfun_has_noise` and
`nsamples` sample-averaging, and both are continuous-only — DFO-LS is also nonlinear least-squares, a
structural mismatch with a scalar accuracy. **Discrete-capable but noise-agnostic**: NOMAD has native
binary variables (`PyNomadBBO` 4.6.0, 2026-08-26, LGPL-3.0, wheels including `win_amd64`), RBFOpt 4.3.0
(2025-03-30) handles mixed-integer, and `scipy.optimize.differential_evolution` takes `integrality` — none
of them documents any stochastic-objective handling. The one useful consequence: with granularity 1 on a
binary variable NOMAD's mesh is the vertex set, so MADS on `{0,1}^d` degenerates to a Hamming-neighbourhood
search, which is a cheap, honest local baseline to run against your enumeration. Py-BOBYQA's `nsamples`
averaging is the same lever as raising your Monte Carlo count per evaluation, which you already control.

**Stop considering these, and say why in one line each if a reviewer asks.** *RSOME* (PyPI 1.3.1,
2024-10-29; last commit 2024-11-15; **GPL-3.0**) has the `minmax`/`maxmin` API that most directly expresses
your problem and is dormant for two years under a copyleft licence — and it needs an algebraic form to
reformulate, which you do not have. *Pyomo/PyROS* (6.10.1, 2026-06-04; repo 2026-10-23) is the only
maintained general-purpose robust-optimization solver and its documentation excludes discrete decisions.
*`dro`* (0.4.3, 2026-10-25, MIT) and *`skwdro`* (1.1.1, 2024-12-05) are good DRO libraries whose ambiguity
sets all need a *sample* of `r` that does not exist. *JuMPeR.jl* last committed 2019-02-24. *`apricot`* and
*`submodlib`* would let you claim a submodularity guarantee your objective does not have. *PyOED* and
*PySensors*: see above. *Gurobi/MOSEK/COPT/SCIP* on the simulated objective: there is nothing to hand them.
*MISDP* (SCIP-SDP, Pajarito): not the binding capability, and the one GPU SDP code in Mittelmann's table,
cuLoRADS 1.1.0, carries accuracy warnings on 29 of 75 instances, which inside a branch-and-bound would
prune the optimum. *Bayesian optimization* (BoTorch 0.18.1, PyPI 2026-06-08; Ax 1.3.1, 2026-06-09 — both
excellent, and the only stacks that accept a declared per-evaluation standard error, via `train_Yvar` and
`(mean, sem)`) earns its keep only when the budget is smaller than the number of candidates; the field's
own statement is that "if the discrete search space has low enough cardinality that the AF can be
evaluated at every discrete element, then acquisition optimization can be solved trivially" ([Daulton et
al., arXiv 2210.10199](https://arxiv.org/pdf/2210.10199)). At your counts you can afford replications per
candidate, so the surrogate borrows strength you do not need while adding a bias channel: a GP posterior
at the argmax is conditioned on the same noise realization that made it the argmax. *Neural methods* are
the clearest no: the published
subset-selection GFlowNet consumed **40,000 reward evaluations per problem instance** ([arXiv
2407.19736](https://arxiv.org/pdf/2407.19736)), which at your per-evaluation cost is 11 hours to 28 days of
simulator time for a space you can enumerate for less; the author of the field's standard amortized-
optimization reference explicitly excises discrete domains because "learning with derivative information
often becomes impossible" there ([arXiv 2202.00665](https://arxiv.org/html/2202.00665v5)); Concrete
Autoencoder training is documented unstable, with the instability manifesting as duplicate feature
selections ([Nilsson et al., ICML 2024](https://proceedings.mlr.press/v235/nilsson24b.html)); and
differentiable relaxations optimize a soft mixture under one network's training loss, which is a different
function from the Monte Carlo accuracy of a classifier retrained on the hard subset. The one neural tool
worth a single sentence is **LassoNet** (PyPI 0.0.21, 2026-10-24 — genuinely live), as a cheap screening
pass to shrink the ground set before you spend simulator budget, never as the thing that chooses the
answer — and note that **no study benchmarks LassoNet, STG and Concrete Autoencoders together on selection
stability**, i.e. on whether the chosen subset agrees across seeds or resamples. For a problem whose
priority is minimizing bias, the absence of a stability benchmark for this family is itself the finding, and
it is the reason LassoNet screens rather than decides. *SALib* (1.6.0, 2026-09-19) is a safe dependency if
you ever acquire a second nuisance parameter, but with one input the first-order Sobol index is 1 by
construction and the analysis is vacuous.

### Five traps in the software you will actually install

Each of these returns a finite, plausible, wrong result, or installs code other than the version string
you read.

| Where | The trap | What to do |
|---|---|---|
| `sim_tools.ovs` | `pip` gives 1.3.0 (2026-06-24), but **every commit touching `sim_tools/ovs/` since 2021-07-05 is formatting**, the last substantive change to `indifference_zone.py` was 2021-07-05, and `tests/` contains **no test for the `ovs` module at all**. Structurally identical to the `apricot` trap below: 2021 code under a 2026 version string | Use it, pin the commit, and write your own tests for the stopping rule and the attained PCS |
| `coptpy` | PyPI sits at **8.0.7 (2026-09-20)** while the solver in the 47-of-47 MISOCP row is **COPT 9.0.0**; the 9.x binary comes from Cardinal Operations, not PyPI | Do not quote COPT's benchmark standing as a property of what `pip` installs |
| `spectral.algorithms.log_det` | **Unguarded**: it silently discards non-positive eigenvalues and uses `eigvals` rather than `eigvalsh`, so on a rank-deficient covariance `bdist` returns a finite, plausible, wrong number — **2.3e16 where the true log-determinant was -149.1**, with a silently discarded imaginary part | Add a rank and conditioning guard before calling `bdist` |
| Reimplementing `bdist` | Tempting, because `bdist` takes `TrainingClass` objects with a `.stats` attribute rather than raw mean/covariance pairs. But **published Bhattacharyya conventions differ by a factor of 4 on the mean term (1/8 against 1/2)** — enough to move a separability verdict without looking wrong — and `spectral` pins Richards & Jia, the convention the remote-sensing JM thresholds were calibrated against | If you rewrite the twelve lines, pin the convention explicitly and check the rewrite against `spectral`, not against internal consistency |
| Any staleness judgement | A repository's `pushed_at` is **no evidence the submodule you import is maintained**. Pyro's was 2026-10-05, two days ahead of its own default-branch HEAD, while `pyro.contrib.oed` had six formatter/packaging commits and one functional change since 2021 — and that one (#2887) applied PyTorch's `upper=True` transpose-sandwich recipe to an `upper=False` Cholesky call in `glmm/guides.py`, so the stored `scale_tril` appears to be the transpose of the intended factor. PyOED's "last activity 2026-10-22" was an opened issue | Use **path-filtered** commit queries for any submodule claim, and read the field name behind a hosted "last activity" date |

Five further names install the wrong software outright, two of them silently. `pip install bounce` gets
`bounce` 0.7.1 (2026-10-14), a keyword search redirect engine by Jay Marcyes (`Jaymon/bounce`) that
**installs and imports cleanly**, not Papenmeier et al.'s combinatorial BO (`lpapenme/bounce`, MIT, HEAD
2024-04-30, **never on PyPI**). `pip install apricot-select` gets 0.6.1, an sdist from **2021-02-18**,
while `jmschrei/apricot` master HEAD is 2025-11-17 with 38 commits since — and `setup.py` on master
**still reads `version="0.6.1"`**; two of those commits change numerical behaviour (unstable `np.argsort`
tie-breaking, #47, and removal of a global `numpy.random.seed`, #49). That is the case that most resembles
your project's recurring failure: pip and git ship different code under one version string, and the
divergence touches tie-breaking and RNG state. `pip install submodlib` returns HTTP 404, from which the
notes concluded source-install-only; **it is on PyPI as `submodlib-py` 0.0.3** (2025-05-14, MIT, from the
submodlib authors) with 45 prebuilt wheels — but **wheels only, no sdist and no Windows build**, so it
installs on the Linux grid and fails with "no matching distribution" on your workstation. `pip install
PyNomad` gets the 2016 USNO NOMAD stellar catalogue, which at least **fails loudly** on Python 3.12 and
installs a module named `nomad`, so it cannot shadow `PyNomadBBO` 4.6.0. And `pip install
concrete-autoencoder` gets 0.0.1, wheel and sdist from **2019-06-10**, the only release ever, against a
`mfbalin/Concrete-Autoencoders` HEAD of 2022-05-24 with no licence reported by GitHub.

## The deficit is in the sweep's inference, not in the optimizer

Your pipeline — grid sweep over `r`, Monte Carlo standard errors, selection and scoring on different
seeds, a Manski identified set with an Imbens-Manski interval, and a claim about the sign of a difference
rather than its value — is the right architecture. **Be precise about what the seed split buys.** It gives
an honest, selection-free value for *the subset you selected*, which is the cleanest available answer to
the winner's curse and avoids depending on a correction package (the one directly usable one,
`winnerscurse`, is off CRAN at v0.1.1 with no commit since 2024-03-07, and `selectiveInference`'s last
release was 2019-09-07). It does **not** make the selection right, and it does not settle a claim about
the *best achievable* subset: the 2026 comparison of corrections distinguishes a "global" from a
"selective" winner's curse — which determines which correction is appropriate — and finds that **no method
dominates**, with plug-in best when treatment differences are large, cross-fitting best when they are
similar, and resampling best in between ([arXiv 2605.18887](https://arxiv.org/pdf/2605.18887)). Report the
split as what it is: a clean value for a chosen subset, not a resolution of the literature. Five additions
follow, in order of how much damage their absence does, then one number to confront and two free checks.

**First, the grid sweep is a relaxation, and it errs in the anti-conservative direction.** Dropping the
off-grid `r` values enlarges the feasible set, so `min over grid` **overstates** your worst-case accuracy.
The error lives in the objective, not in `r`, is bounded by `L*h/2`, and is **unbounded without a measured
Lipschitz constant**. The assertion that one-dimensionality makes discretization "close to exact" is
contradicted by a primary source whose own counterexample is a scalar nuisance on an interval and which
needs 28 adaptively chosen points to reach the optimum, with the state-of-the-art Blankenship-Falk bound
requiring more than 20 iterations to get within 10 percent ([arXiv
2303.00219](https://arxiv.org/pdf/2303.00219), p. 2 and Table 1). Worse, in a constructed bimodal case
verification found that grids of 11, 21, 41 and 51 points **all returned the identical wrong value**, 5.6
accuracy points optimistic — so the obvious sanity check, refine and see if it moves, **falsely confirms**.
Only 101 points found the dip, and at the true Lipschitz constant of 11.32 even a 101-point grid certifies
only plus-or-minus 0.057. So: **measure `L` or verify monotonicity of `A(S, .)` in `r`, and report the
certified error as `L*h/2` with `L` measured rather than assumed.** If `A(S, .)` turns out monotone in `r`
— plausible if higher between-measurement correlation means less independent information — the worst case
is at an endpoint, two evaluations replace the whole sweep, and the semi-infinite-programming question
evaporates. Verify it; do not assume it.

**Second, the two errors point in opposite directions and can cancel.** While the grid is optimistic, the
minimum of noisy estimates is **pessimistic**: Monte Carlo at sigma=0.01 over 60,000 replicates measured a
downward bias of **1.2 to 2.4 accuracy points, growing with grid density**. Agreement between two grids, or
between a grid and a bound, is therefore not evidence of correctness. State both directions explicitly,
which is also what distinguishes an Imbens-Manski interval from a naive `[min_r A-hat, max_r A-hat]`: the
latter conflates sampling noise with identification width and is wrong in both directions at once. One
sourcing caveat for the manuscript: the 1.2-to-2.4-point figure is this report's own measurement on a
constructed case. The *general* claim that the minimum of noisy estimates is downward biased is a standard
statistical fact for which **no citation was gathered**; source it, or state it as a measurement on your
own sweep, before it appears in a paper as a general fact. The published anchor for the magnitude of the
related selection-on-noisy-estimates bias is outside the OR literature: Cawley and Talbot show that the
*variance* of a selection criterion matters as much as its bias, that noisy criteria such as k-fold
cross-validation scores lead to over-fitting in selection, and that the resulting degradation "can be
surprisingly large" — comparable in size to the performance differences between the algorithms being
compared ([JMLR 11(70):2079-2107](https://www.jmlr.org/papers/v11/cawley10a.html)). That is the external
number your standing rule asks for, and it applies to any criterion optimized over a finite sample.

**Third, do not use `scipy.optimize.minimize_scalar` for the inner problem.** Its own documentation states
that "all methods are intended only for local minimization," and `method='bounded'` uses Brent to find a
local minimum in the interval. On a bimodal accuracy profile it returned a point **18.0 accuracy points too
optimistic**, and golden-section with one bracket did the same while another bracket raised `ValueError`.
"Minimax over a 1-D box is a line search" is exact only if `A(S, .)` is unimodal or quasiconvex in `r`,
which is the same unverified property as above. An exhaustive scan avoids this and inherits the grid error
instead — which is why the Lipschitz measurement is load-bearing.

**Fourth, compute the Imbens-Manski interval yourself, and know how it fails.** You have adopted the frame
and there is no package to import: `ivmte` (2021-09-17) and `ivitr` (2020-09-11) are five and six years
stale, `csabounds` was removed from CRAN on 2022-07-09, `rbounds` is Rosenbaum sensitivity and a different
method, `lpinfer` is not on CRAN, and the only Python option, `CausalBoundingEngine` (0.1.5, 2025-08-08),
has one star. For a scalar bound the construction is a short closed-form calculation — widen the endpoints
by their standard errors at a critical value chosen to cover the *true value* rather than the identified
set — and the readable reference implementation of the resampling version is **`medrobust`'s `bound_ci()`**
(`Data-Wise/medrobust`, commits 2026-10-11, version 0.1.0.9000, **not on CRAN, 0 stars, licence
unverified**), which is a model to copy rather than a dependency to take. Two things to carry with it.
`medrobust`'s own NEWS reports that **raw estimated bounds under-cover at small samples** and that the
correction brings coverage close to nominal at n = 500 (0.09 to 0.95 and 0.12 to 0.93 on its two
estimands) — so a sanity check of your own coverage by simulation is not optional. And Stoye (2009) argued
that Imbens and Manski's final result "implicitly assumes superefficient estimation of a nuisance
parameter" ([CeMMAP working paper](https://www.ifs.org.uk/sites/default/files/output_url_files/cwp251414.pdf)),
which is worth a footnote in any paper that leans on the interval. Finally, that negative is now as strong as the OCBA one. The
full-text sweep this report originally left undone **has been run**: the complete crandb index of all
**25,529 CRAN packages**, matching name, title and description against "Manski" and "Imbens", returns
**zero hits**. So there is no CRAN package implementing this, under any name, and the statement can go
into a methods section as a sweep rather than a named-candidate check.

**Fifth, keep the claim about the ranking separate from the claim about the value, and report the
crossover.** The reduction to `max_S min_r A(S,r)` also requires the reported metric to be a per-`r`
accuracy averaged over `r`. If instead a single decision threshold is tuned on the pooled cohort, the
functional becomes convex in the mixing distribution and the worst case lies strictly *inside* the simplex,
not at a point mass — in a worked three-point example the interior mixture was **13.6 accuracy points worse
than the best Dirac**, so the extreme-point argument fails outright. Check which metric you are reporting.
Then plot every candidate's profile across `r` with simultaneous bands: either `S*` wins everywhere, which
is a strong and citable claim, or there is a crossover `r_0`, and "the subset choice depends on `r` only
through whether `r` exceeds `r_0`" is far more informative than any range. If the worst-case ranking is flat
— plausible if accuracy degrades similarly for all candidates — break ties by maximum regret or best-case
performance ([arXiv 2011.14875](https://arxiv.org/pdf/2011.14875)). Note finally that the collapse of the
DRO layer applies only to the *inner* uncertainty: the outer maximization over `S` is untouched by any of
this, and if `S` ever stops being enumerable, a Blankenship-Falk cutting-set scheme over `r` is exactly
what would start buying something.

**The budget number to confront, at both ends of your candidate range.** If your objective is a probability
near 0.5, a single replication has variance 0.25, so detecting a 0.01 difference at a Bonferroni-corrected
two-sided level requires about `0.5 (z/0.01)^2` replications per candidate. **At 128 candidates** (`z`
about 3.48) that is roughly **60,000 per candidate, about 7.7 million total** under equal allocation. **At
131,071 candidates** (`z` about 5.07) it is roughly **130,000 per candidate and 1.7e10 in total** — three
orders of magnitude more, and the figure that decides whether the top of your range is reachable at all. A
single pairwise comparison at `z` about 2.8 needs about 39,000, and at `p` near 0.9 the requirement falls
by roughly 2.8 times. This is elementary arithmetic rather than a literature recommendation and should be
checked, not cited — no source gives a per-design replication count for a 0.01 indifference zone — but if
it is near-right it is the most important number in your analysis. The two levers that change it by an
order of magnitude are **common random numbers across candidates** (which is why `mrg32k3a`'s substream
structure is not a nicety) and **widening the indifference zone to report a best *set* rather than a single
winner**. That second lever is what multiple-comparisons-with-the-best intervals deliver, and the route to
them is specific: `multcomp` is maintained (1.4-26 / 1.4-30) and provides simultaneous intervals, but
**Hsu's MCB is not among its hard-coded procedures** — any sentence saying `multcomp` implements Hsu's MCB
would be wrong. Build a contrast matrix comparing each candidate to the best and pass it to `glht()` with
single-step adjustment; the treatments whose intervals include zero are the "best set." The one vendor
documentation describing that equivalence was not verified against Hsu (1984/1996), so check the critical
value yourself.

**Two outside checks that cost almost nothing.** Since your distributions are fully specified, the exact
Bayes error for two equal-covariance equal-prior Gaussians is `Phi(-d/2)` with `d` the Mahalanobis distance
between means — a closed-form unit test for any separability implementation (standard textbook material,
but cite Fukunaga or Duda and Hart rather than leaving it unsourced). And the closed-form bounds should
**bracket** a Monte Carlo estimate of the multiclass Bayes error drawn from the same known Gaussians; if
they do not, the implementation is wrong, not the anatomy. That is not simulation in place of a closed
form — it is a validation of the closed form against something outside it. Watch the known failure at your
class count: the pairwise or union bound over `C(C-1)/2` pairs becomes loose as `C` grows, and at 276 pairs
it can exceed 1 and go vacuous, so report the **minimum pairwise** separability (which names the confusable
pair, e.g. L5 against S1) alongside any union bound and treat the union bound as an upper bound that may be
uninformative rather than as an estimate.

## Conclusion

The most useful thing this report can tell you is that the search you commissioned has a negative answer
and that the negative answer is good news. There is no solver to buy, no mixed-integer or conic or GPU
capability you lack, and no neural method whose bias channels you should accept. At `m` of 17 or below the
optimization is a loop on either branch — what differs is what the loop costs — the only genuinely missing
component is a replication-budget rule that `sim-tools` 1.3.0 ships and you should install, test yourself
and cite, the two-solver cross-check runs on free academic licences or on SCIP for nothing, and the compute
you were going to spend on a licence belongs in a bootstrap over the enumeration instead. What remains
genuinely open divides into three kinds. The first is three of the four parameters above: `m`, `k` and
`C`. The per-evaluation cost is settled — 7.24 s, measured — and with it the choice of regime; the other
three are asserted inconsistently in the notes, every model size here scales off them, and nobody outside
your project can resolve them. The second is about your objective, and two of its four parts are now
closed by measurement: `A(S, .)` is **not** monotone in `r` (measured at both junctions and both measure
sets), and its secant Lipschitz constant is at most 0.033 with the implied grid gap at 0.3 to 0.5 Monte
Carlo standard errors — a *lower* bound, so the gap is indicative and not certified. Two parts remain
open and only you can close them: whether your reported metric is a per-`r` accuracy or a pooled quantity
with a tuned threshold, and whether `A(., r)` is monotone in `S`. The
third is about the literature: no published paper poses "maximize the minimum pairwise Mahalanobis distance
between class means over subsets of coordinates" as a mixed-integer conic program, and that negative is
only weakly tested (eight arXiv phrase searches, zero hits; the statistics and operations-research journal
literature on cardinality-constrained discriminant analysis was not searched, and the structure has a
published name under which a prior formulation could exist in different wording). Treat the absence of a
citation as unrefuted rather than established, and if you publish the reformulation, publish it as routine
machinery applied to a new objective rather than as a new method.

The deeper point is a correction to the framing of the question itself. "Which solver searches a
higher-dimensional space for the optimum" presupposes that the hard part is the search, and in your problem
it is not. The combinatorics are small, the inner minimization is one-dimensional, and the structure is
benign. What is hard is that the worst-case operator and the Monte Carlo noise push the same number in
opposite directions, that the grid error is unbounded without a measurement you have not made, and that a
refinement check which ought to catch this falsely confirms. Three layers of optimization machinery — DRO,
robust optimization, semi-infinite programming — all collapse onto the sweep you already run, and all three
collapse for *conditions* rather than automatically. Naming those conditions and measuring them is the
whole job. Your project's standing rule applies with unusual force here: every number in this analysis can
be finite, plausible and wrong in at least two independent ways, and the only defence is a check from
outside the computation — a second solver on the same model, Joshi and Boyd's upper bound against your
chosen subset, `Phi(-d/2)` against your separability code, a Monte Carlo Bayes error bracketed by your
closed-form bounds, `sim-tools`' OCBA against your own derivation of the Chen-Lee ratios, and a rendered
profile of `A(S, .)` rather than its summary.
