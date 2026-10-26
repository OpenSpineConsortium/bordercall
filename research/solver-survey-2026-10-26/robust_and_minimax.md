# Robust optimization, DRO and minimax design over an unknown scalar nuisance parameter (state of software, October 2026)

Scope note for the report-writer: the user's problem is maximise a classification accuracy `A(S, r)`
over subsets `S`, where `r` is a between-measurement correlation confined to `[0, 1]` and never
published. That is (i) a **one-dimensional** uncertainty set, (ii) a **discrete** (subset-selection)
decision space, and (iii) a **noisy** objective. Each of those three properties independently rules
out most of the packages named in the assignment, and the notes below say which and why.

## Verification table (all dates checked against primary APIs on 2026-10-26)

Repository `pushed_at` is from the GitHub REST API (last commit to any branch); release dates are from
the PyPI JSON API and the CRAN database (crandb.r-pkg.org). Anything not verified this way is marked
**unverified** and should not be presented as fact.

| Package | Latest release | Release date | Last commit (any branch) | Licence | Verdict |
|---|---|---|---|---|---|
| Pyomo (incl. PyROS) | 6.10.1 | 2026-06-04 | 2026-10-23 | NOASSERTION on GitHub | **Maintained** |
| `dro` (Python) | 0.4.3 | 2026-10-25 | 2026-10-25 | MIT | **Maintained, actively** |
| SALib | 1.6.0 | 2026-09-19 | 2026-10-18 | MIT | **Maintained** |
| OpenTURNS | 1.27.post1 | 2026-06-19 | 2026-10-25 | LGPL | **Maintained** |
| Dakota | 6.24.0 / nightly `stable_2026_10_25` | 2026-10-25 (nightly) | 2026-10-25 | NOASSERTION on GitHub | **Maintained** |
| SimOpt (`simoptlib`) | 1.2.4 | 2026-05-22 | 2026-10-15 | MIT | **Maintained** |
| UQpy | 4.2.1 | 2025-08-19 | 2026-10-06 | MIT | **Maintained** |
| `sensitivity` (R) | 1.31.0 | 2026-02-27 | n/a (CRAN) | GPL-2 | **Maintained** |
| GJRM (R) | 0.2-6.9 | 2026-06-15 | n/a (CRAN) | GPL (>= 2) | **Maintained** |
| ATbounds (R) | 0.1.1 | 2026-05-07 | n/a (CRAN) | GPL-3 | **Maintained** |
| `medrobust` (R) | 0.1.0.9000 (dev) | not on CRAN | 2026-10-11 | unverified | Active but pre-release, 0 stars |
| Chaospy | 4.3.21 | 2025-08-29 | 2025-09-04 | MIT | Quiet ~14 months |
| `skwdro` | 1.1.1 | 2024-12-05 | 2026-03-12 | BSD-3-Clause | Repo alive, **no release in ~23 months** |
| `causalboundingengine` | 0.1.5 | 2025-08-08 | 2025-08-09 | MIT | Research code, **1 star** |
| **RSOME** | 1.3.1 | **2024-10-29** | **2024-11-15** | **GPL-3.0** | **DORMANT ~24 months** |
| ivmte (R) | 1.4.0 | 2021-09-17 | n/a (CRAN) | GPL-2 \| GPL-3 | **Stale (5 yr), still on CRAN** |
| ivitr (R) | 0.1.0 | 2020-09-11 | n/a (CRAN) | GPL-3 | **Stale (6 yr), still on CRAN** |
| **JuMPeR.jl** | v0.6.0 | — | **2019-02-24** | NOASSERTION | **DEAD (7.5 yr)** |
| csabounds (R) | 1.0.0 | 2017-09-06 | — | GPL-2 | **REMOVED from CRAN 2022-07-09** |
| `lpinfer` (R) | — | — | — | — | **No CRAN record** |
| `DRO.jl`, `mlr3dro` | — | — | — | — | **No evidence either exists** |

Two corrections to flag loudly for the report: **RSOME is dormant, not maintained** (no release or
commit in ~24 months) and **it is GPL-3.0**, which matters for anyone embedding it. And **UQpy is not
stale** — a third-party tracker reporting 4.1.5/Nov-2023 was wrong; the real state is 4.2.1 with
commits this month.

---

## Q1. Trusted robust-optimization modelling packages in 2026 (RSOME, ROME, JuMPeR, PyROS, cvxpy, Gurobi/MOSEK)

### Takeaway

Only **one** general-purpose robust-optimization tool is genuinely maintained in October 2026:
**Pyomo/PyROS** (commits 2026-10-23). **RSOME is dormant** — last release 2024-10-29, last commit
2024-11-15, and GPL-3.0 licensed. **ROME** is MATLAB and academic-use-only; **JuMPeR.jl is dead**
(last commit February 2019). No major commercial solver exposes a native uncertainty-set modelling
object — Gurobi and MOSEK are the conic back-ends that RSOME reformulates *into*. Crucially, every one
of these assumes the uncertainty enters **constraints or a linear/conic objective**, not a black-box
simulated accuracy, and PyROS explicitly does not handle discrete decisions.

### Cited Findings

**RSOME (Python) — real, well-cited, GPL-3.0, and DORMANT**

- RSOME is "an open-source Python package for modeling robust and distributionally robust
  optimization problems", published in *INFORMS Journal on Computing* 2023, 35(4), 717–724 — [RSOME in Python (IJOC)](https://pubsonline.informs.org/doi/fpi/10.1287/ijoc.2023.1291); preprint at [Optimization Online 2021](https://optimization-online.org/2021/06/8443/)
- **Verified staleness**: PyPI latest is **1.3.1, uploaded 2024-10-29**; the GitHub repository
  `XiongPengNUS/rsome` has `pushed_at` of **2024-11-15**, `archived: false`, 349 stars. No release or
  commit for roughly 24 months — [PyPI JSON API, rsome](https://pypi.org/pypi/rsome/json); [GitHub REST API, XiongPengNUS/rsome](https://api.github.com/repos/XiongPengNUS/rsome)
- **Verified licence: GPL-3.0**, reported independently by the GitHub API (`spdx_id: GPL-3.0`) and the
  PyPI metadata (`license: GPL-3.0`). This resolves what earlier web sources left blank, and it
  contradicts a search-snippet claim of "academic use" — it is copyleft, not academic-only — [GitHub REST API](https://api.github.com/repos/XiongPengNUS/rsome); [PyPI JSON API](https://pypi.org/pypi/rsome/json)
- Models are "built from variables, constraints, and expressions formatted as N-dimensional arrays,
  consistent with the NumPy library in terms of syntax and operations". RSOME "transforms robust or
  distributionally robust optimization models into deterministic linear or conic programs, which
  external solvers then solve" — [RSOME README (GitHub)](https://github.com/XiongPengNUS/rsome)
- Uncertainty sets are *not* named classes; they are "a collection of constraints, written as an
  iterable Python object, such as `tuple` or `list`" over random variables from `model.rvar()`. The
  canonical three are norm bounds: box = `norm(z, np.inf) <= 1`, ellipsoidal = `norm(z, 2) <= 1.5`,
  budget/polyhedral = `norm(z, 1) <= 1.5` with `z >= 0, z <= 1` — [RSOME robust optimization docs](https://xiongpengnus.github.io/rsome/ro_rsome)
- Worst-case objectives via `model.minmax(obj, *args)` / `model.maxmin(obj, *args)`; constraint-wise
  sets via `.forall(...)`. Affine (adjustable) decision rules use `model.ldr(shape)` plus
  `y.adapt(z)`; coefficients recovered with `y.get()` and `y.get(z)` — [RSOME RO docs](https://xiongpengnus.github.io/rsome/ro_rsome)
- Solver interfaces and conic capability per the README table: `scipy.optimize` >= 1.9.0 (LP/MILP, no
  cones), CyLP >= 0.9.0, OR-Tools >= 7.5.7466, ECOS >= 2.0.10 (SOC + exp), Gurobi >= 9.1.0 (SOC),
  MOSEK >= 10.0.44 (SOC + exp + SDP), CPLEX >= 12.9.0.0 (SOC), COPT >= 7.2.2 (SOC + exp + SDP) — [RSOME README](https://github.com/XiongPengNUS/rsome)
- MATLAB predecessor: "Robust stochastic optimization made easy with RSOME", Chen, Sim & Xiong,
  *Management Science* (2020) — [PyPI rsome project page](https://pypi.org/project/rsome)
- Integer decisions: `do_math()` output "lists continuous, binary, and integer variable counts" and
  the SciPy interface supports `milp`, but the docs have **no dedicated section on integer modelling**
  and do not state what happens when integers meet a robust counterpart — [RSOME intro docs](https://xiongpengnus.github.io/rsome/)

**Pyomo PyROS — the only maintained general-purpose RO solver**

- **Verified maintenance**: Pyomo PyPI latest **6.10.1, uploaded 2026-06-04**; repository `Pyomo/pyomo`
  `pushed_at` **2026-10-23**, `archived: false`, 2,552 stars — [PyPI JSON API, Pyomo](https://pypi.org/pypi/Pyomo/json); [GitHub REST API, Pyomo/pyomo](https://api.github.com/repos/Pyomo/pyomo)
- PyROS is "a Pyomo-based meta-solver for non-convex, two-stage adjustable robust optimization
  problems"; the user supplies a deterministic model plus an uncertainty set and PyROS runs "a
  generalized cutting-set algorithm for nonconvex two-stage problems", so no hand reformulation is
  needed — [Pyomo PyROS docs](https://pyomo.readthedocs.io/en/stable/explanation/solvers/pyros/index.html); [PyROS: The Pyomo Robust Optimization Solver (Optimization Online, June 2026)](https://optimization-online.org/2026/06/pyros-the-pyomo-robust-optimization-solver/)
- It constructs **static, affine or quadratic decision rules** for second-stage variables
  automatically — [Optimization Online 2026 PyROS preprint](https://optimization-online.org/wp-content/uploads/2026/06/PyROS-Pyomo-RO-Solver.pdf)
- Built-in uncertainty set classes with mathematical forms: `BoxSet` ({q : qᴸ ≤ q ≤ qᵁ}),
  `EllipsoidalSet` ({q : (q−q⁰)ᵀP⁻¹(q−q⁰) ≤ s}), `AxisAlignedEllipsoidalSet`, `BudgetSet`,
  `CardinalitySet` (Bertsimas–Sim Γ-budget on ξ⁺, ξ⁻), `FactorModelSet` (q = q⁰ + Ψξ, ξ ∈ [−1,1]^f,
  |Σξⱼ| ≤ βF), `PolyhedralSet` ({q : Aq ≤ b}, bounded), `DiscreteScenarioSet` (finite {q¹,…,qˢ}),
  `CartesianProductSet`, `IntersectionSet`, and abstract base `UncertaintySet` — [PyROS uncertainty sets](https://pyomo.readthedocs.io/en/stable/explanation/solvers/pyros/uncertainty_sets.html)
- Custom sets by subclassing `UncertaintySet`, "but this works only when all uncertain parameters are
  continuous. For discrete sets, the documentation recommends `DiscreteScenarioSet`… PyROS does not
  support mixed-integer uncertainty sets" — [PyROS uncertainty sets](https://pyomo.readthedocs.io/en/stable/explanation/solvers/pyros/uncertainty_sets.html)
- Pyomo's scope statement: PyROS "suits continuous-variable models with nonlinearities and
  non-convexities in both variables and uncertain parameters, and it can handle state variables
  defined by equality constraints" — [Pyomo PyROS docs 6.7.2](https://pyomo.readthedocs.io/en/6.7.2/contributed_packages/pyros.html)
- A 2024 paper reports extension to uncertain variable bounds, a benchmark over **more than 8,500
  small instances**, and a carbon-capture case study — [LAPSE:2024.1528](https://psecommunity.org/LAPSE:2024.1528)

**ROME (MATLAB) — real, published, academic-use only**

- "Robust Optimization Made Easy with ROME", Goh & Sim, *Operations Research* 2011, 59(4), 973–985.
  ROME "acts as a modeling layer between the user and solver engines" inside MATLAB — [INFORMS](https://pubsonline.informs.org/doi/10.1287/opre.1110.0944); [IDEAS record](https://ideas.repec.org/a/inm/oropre/v59y2011i4p973-985.html)
- "ROME is freely distributed for academic use at robustopt.com", which hosts releases and the User's
  Guide — [robustopt.com](https://www.robustopt.com)
- Rahimian & Mehrotra describe ROME as "a MATLAB-based algebraic modeling toolbox for a class of DRO
  problems with conic-representable sets for the support and mean" — [DRO: A Review (arXiv 1908.05659)](https://arxiv.org/pdf/1908.05659)

**JuMPeR.jl (Julia) — DEAD, now verified by commit date**

- **Verified**: the repository is `IainNZ/JuMPeR.jl` (the `IainNZ/JuMPeR` path 301-redirects to it) with
  `pushed_at` of **2019-02-24T16:49:41Z** — no commit to any branch in over seven and a half years.
  `archived: false` (never formally archived), 53 stars — [GitHub REST API, IainNZ/JuMPeR.jl](https://api.github.com/repos/IainNZ/JuMPeR.jl)
- Its only release is **v0.6.0**, built against JuMP v0.18.6 — [ecosyste.ms JuMPeR](https://repos.ecosyste.ms/usage/julia/JuMPeR); [libraries.io JuMPeR](https://libraries.io/julia/JuMPeR)
- A maintainer said moving it to JuMP v0.19's MathOptInterface "would need work"; another reply said it
  "has not been maintained for two years and cannot be used with Gurobi 9.1" — [Julia Discourse: JuMPeR and Grisu](https://discourse.julialang.org/t/jumper-and-grisu/102258); [Julia Discourse: Gurobi build error](https://discourse.julialang.org/t/error-building-gurobi/59852/6)
- The JuMP-dev GSoC 2022 project list states recent JuMP versions do not support robust optimization
  and calls JuMPeR unmaintained, proposing a replacement extension; **no evidence was found that the
  replacement was completed** — [jump-dev/GSOC2022](https://github.com/jump-dev/GSOC2022)
- The JuMPeR documentation still claims the project is "under active development" — stale text that the
  2019 commit date definitively refutes — [JuMPeR docs](https://jumper.readthedocs.io/en/latest/jumper.html)
- Forum suggestions for Julia users are `InfiniteOpt` (not designed for RO) or hand-writing the robust
  counterpart — [Julia Discourse](https://discourse.julialang.org/t/jumper-using-solver-clp-glpk/115206)

**cvxpy and native commercial solver support**

- No source was found showing Gurobi, MOSEK, CPLEX or COPT exposing a first-class uncertainty-set
  modelling object. In the RSOME architecture these are strictly the conic back-ends receiving the
  *already reformulated* deterministic program — [RSOME README solver table](https://github.com/XiongPengNUS/rsome)
- A semi-infinite program can sometimes become an exactly equivalent SDP when the function is closely
  approximable by a polynomial or rational function, making a standard SDP solver (hence cvxpy) usable
  — but the source names no Python tool that performs the reduction — [Papp & Alizadeh, SIP via polynomial interpolants](https://ar5iv.arxiv.org/html/1512.06796)

### Inferences

- RSOME and PyROS occupy different niches: RSOME is a *modelling layer* emitting an exact robust
  counterpart (so uncertainty must enter affinely/conically), PyROS is a *solver* iterating a
  worst-case separation oracle (so it tolerates nonconvex dependence on the uncertain parameter). For a
  black-box `A(S, r)` with no algebraic form, neither works off the shelf: RSOME has nothing to
  reformulate, PyROS needs a continuous-variable Pyomo model.
- PyROS' documented restriction to continuous decisions plus continuous uncertainty sets is the
  decisive blocker for subset selection. `DiscreteScenarioSet` applies to the *uncertainty*, not the
  decision.
- RSOME's dormancy is a genuine adoption risk that the published IJOC paper conceals: a 2023 INFORMS
  paper and 349 stars read as healthy, and the commit log says otherwise. Anyone building on it should
  know they are building on a two-year-old tree under GPL-3.0.
- "Robust optimization software" in 2026 is effectively **Pyomo/PyROS, or write it yourself**. The
  Julia option is dead, the MATLAB option is academic-licence legacy, and the Python modelling layer is
  dormant.

### Gaps

- Whether RSOME supports integer decision variables *inside a robust counterpart* (as opposed to in a
  deterministic model) is not documented on the pages fetched. **Unverified.**
- No primary source was found for native robust-conic support in current Gurobi or MOSEK. Treat "no
  native support" as unconfirmed-but-unrefuted.
- Pyomo's and Dakota's GitHub licence fields both return `NOASSERTION`, meaning GitHub could not
  auto-classify the licence file. The exact licence of each is therefore **unverified** here (both are
  widely described as BSD-family / LGPL respectively, but I did not confirm this from a primary source).
- Bertsimas & den Hertog, *Robust and Adaptive Optimization* (2022) and Ben-Tal–El Ghaoui–Nemirovski
  were not fetched; the open survey located is Bertsimas, Brown & Caramanis, "Theory and Applications
  of Robust Optimization" — [arXiv 1010.5445](https://arxiv.org/pdf/1010.5445)

---

## Q2. Distributionally robust optimization: Wasserstein-ball and moment-based (Delage–Ye) implementations

### Takeaway

**`dro`** (Namkoong/Blanchet/Lam group, MIT, 0.4.3 released 2026-10-25 with commits the same day) is
the one DRO library that is unambiguously maintained and is the right one to name first. **`skwdro`**
is published in JMLR 2026 but has had **no release since 2024-12-05**. RSOME's `dro` module is in a
dormant package. **`DRO.jl` and `mlr3dro` could not be shown to exist.** For a *single scalar* nuisance
parameter, all of this machinery is overkill: Wasserstein and φ-divergence balls hedge against an
unknown *distribution estimated from samples*, and the user has no sample of `r` at all.

### Cited Findings

**`dro` (Python) — the most complete and most actively maintained DRO library**

- PyPI description: "A package of distributionally robust optimization (DRO) methods. Implemented via
  cvxpy and PyTorch." **Verified: version 0.4.3, uploaded 2026-10-25T16:06:47; MIT licence** — [PyPI JSON API, dro](https://pypi.org/pypi/dro/json); [PyPI dro](https://pypi.org/project/dro/)
- **Verified maintenance**: repository `namkoong-lab/dro`, `pushed_at` **2026-10-25T16:37:39Z** (commits
  the same day as the release), `archived: false`, 163 stars, `spdx_id: MIT` — [GitHub REST API, namkoong-lab/dro](https://api.github.com/repos/namkoong-lab/dro)
- The library "implements 14 DRO formulations and 9 backbone models, enabling 79 distinct DRO methods";
  docs at `python-dro.org` — [DRO library paper, NeurIPS 2025](https://neurips.cc/virtual/2025/124373)
- Linear-model ambiguity sets (via cvxpy): `Chi2DRO` (χ²), `KLDRO` (Kullback–Leibler), `TVDRO` (total
  variation), CVaR including marginal-X and conditional-(Y|X) variants, `MMD_DRO` (maximum mean
  discrepancy), `WassersteinDRO` and `WassersteinDROsatisficing` (robust satisficing),
  `SinkhornLinearDRO`, `MOTDRO` (optimal transport with conditional moment constraints), `ORWDRO`
  (outlier-robust Wasserstein), `HR_DRO_LR` (holistic robust), `GroupDRO` — [PyPI dro](https://pypi.org/project/dro/)
- Neural-network variants (PyTorch): χ², Wasserstein, holistic robust, Sinkhorn, group DRO. Tree
  ensembles (LightGBM, XGBoost): KL, χ², CVaR — [PyPI dro](https://pypi.org/project/dro/)
- Paper authors (arXiv 2505.23565): Tianyu Wang, Jiashuo Liu, Henry Lam, Hongseok Namkoong, Jose
  Blanchet — this **is** the Blanchet-group code the assignment asked about — [PyPI dro](https://pypi.org/project/dro/)
- Coverage gap: the PyPI page "does not mention moment-based or Delage–Ye ambiguity sets by name"; the
  nearest item is `MOTDRO`, and φ-divergence is exposed only through specific χ² and KL classes, not a
  general φ interface — [PyPI dro](https://pypi.org/project/dro/)

**`skwdro` (Python) — published, BSD-3, but no release in ~23 months**

- "A library for Wasserstein distributionally robust machine learning", *Journal of Machine Learning
  Research* vol. 27 (2026), paper 24-1840 — [JMLR](https://jmlr.org/papers/v27/24-1840.html); preprint [arXiv 2410.21231](https://arxiv.org/abs/2410.21231v2)
- It "offers WDRO versions for a large range of estimators, either by extending scikit-learn estimators
  or by providing a wrapper for pytorch modules"; "its core relies on an entropic smoothing of the
  original robust objective". Install `pip install skwdro` — [skwdro docs](https://skwdro.readthedocs.io)
- **Verified**: PyPI latest **1.1.1, uploaded 2024-12-05**; repository `iutzeler/skwdro` `pushed_at`
  **2026-03-12**, `archived: false`, 25 stars, **BSD-3-Clause** — [PyPI JSON API, skwdro](https://pypi.org/pypi/skwdro/json); [GitHub REST API, iutzeler/skwdro](https://api.github.com/repos/iutzeler/skwdro)

**RSOME's `dro` module — event-wise ambiguity (Wiesemann–Chen–Sim), inside a dormant package**

- `dro.Model(scens)` takes a scenario count or labels; `model.ambiguity()` builds an ambiguity set with
  three components: `exptset` (constraints on conditional expectations, e.g. `E(z) == 0`), `suppset`
  (support constraints per scenario, e.g. `norm(z, 1) <= 1.5`) and `probset` (constraints on the
  scenario probability vector `p`, with non-negativity and sum-to-one built in). Worst-case objectives
  via `minsup(obj, ambset)` / `maxinf()`; `showevents()` prints what is defined per scenario; an
  ambiguity set "is only valid if every scenario has a defined support" — [RSOME dro docs](https://xiongpengnus.github.io/rsome/dro_rsome)
- The RSOME `dro` page shows **only mean-type moment information** through `exptset` — no variance or
  second-moment constraints documented — and exposes **no Wasserstein, φ-divergence or KL ambiguity-set
  API**; Wasserstein appears only in application examples and the cited Wiesemann et al. (2014)
  reference — [RSOME dro docs](https://xiongpengnus.github.io/rsome/dro_rsome)
- Staleness and licence as verified above: last release 2024-10-29, last commit 2024-11-15, GPL-3.0 — [PyPI JSON API](https://pypi.org/pypi/rsome/json); [GitHub REST API](https://api.github.com/repos/XiongPengNUS/rsome)

**Surveys / theory anchors**

- Rahimian & Mehrotra, "Distributionally Robust Optimization: A Review", arXiv August 2019; published
  as "Frameworks and Results in Distributionally Robust Optimization", *Open Journal of Mathematical
  Optimization* vol. 3 (2022), article 4, **85 pages**, DOI 10.5802/ojmo.15 (submitted 13 Dec 2021,
  accepted 11 Jul 2022), adding a treatment of solution techniques. **No newer update from these
  authors was found** — [arXiv 1908.05659](https://arxiv.org/pdf/1908.05659); [OJMO 10.5802/ojmo.15](https://ojmo.centre-mersenne.org/articles/10.5802/ojmo.15/)
- The current Kuhn-group survey is Kuhn, Shafiee & Wiesemann, "Distributionally robust optimization",
  *Acta Numerica* 34:579–804 (2025) — [EPFL Infoscience record](https://infoscience.epfl.ch/entities/publication/bd537ca0-065f-4148-91c1-7baedf3c131b)

### Inferences

- **The heavyweight DRO machinery buys nothing here, and this should be stated plainly.** Every
  ambiguity set above (Wasserstein ball, χ²/KL ball, MMD, Sinkhorn) is parameterised by a *radius*
  around an *empirical distribution* built from data. The user has no data on `r`: they have a support
  set, `[0, 1]`, and nothing else. A DRO problem whose ambiguity set is "all distributions supported on
  [0, 1]" collapses exactly to the classical robust problem `max_S min_{r ∈ [0,1]} A(S, r)`, because
  the worst-case distribution is a point mass at the worst `r`. The radius, the transport cost and the
  divergence all become inert. Choosing a radius would mean choosing an unjustifiable second free
  parameter on top of the one that is already unknown.
- The one DRO formulation that is *not* inert is a **moment-based / Delage–Ye** set, if the user were
  willing to assert something like "E[r] is around 0.5" — but that assertion has no more support in the
  literature than `r` itself does, so it imports an assumption rather than removing one.
- `dro` is the right package to name if the user ever *does* acquire a sample of `r` across sites or
  cohorts; `skwdro` is the right one if the goal is a robustified classifier rather than a robust subset
  choice — with the caveat that skwdro's last release predates its own JMLR publication.

### Gaps

- **`DRO.jl` (Julia): no evidence found that this package exists** — searches returned nothing under
  that name — [search outcome](https://science.ecosyste.ms/projects/56340). Do not describe it.
- **`mlr3dro` (R): no evidence found that this package exists.** Same search, same result. It is also
  absent from the CRAN database checks run for this task.
- No package exposes a **Delage–Ye (2010) moment ambiguity set** as a named, documented class. RSOME's
  `exptset` is the closest primitive and covers first moments only.

---

## Q3. Scalar-nuisance minimax: grid sweep vs bilevel vs semi-infinite programming

### Takeaway

With a one-dimensional interval the robust problem is a semi-infinite program in a single parameter —
and **there is no maintained Python-native semi-infinite programming solver**. A grid sweep over `r`,
with cutting-plane refinement around the argmin if the inner problem is cheap, is not a shortcut: it
*is* the standard discretisation method for SIP, and in one dimension it is close to exact.

### Cited Findings

- No current Python-native SIP solver was found. The MATLAB option is `fseminf`, "a nonlinear
  programming solver that finds the minimum of a problem subject to semi-infinite constraints" — [MathWorks fseminf](https://www.mathworks.com/help/optim/ug/fseminf.html)
- Julia's EAGO provides `sip_solve`, returning "the optimal value, the solution, and a boolean
  feasibility value"; the EAGO docs note that "nonconvex semi-infinite constraints are extremely
  challenging to solve in general" — [EAGO semi-infinite docs](https://docs.juliahub.com/General/EAGO/stable/SemiInfinite/semiinfinite/)
- A 2018 JuMP forum thread asked about wiring an SIP solver such as NSIPS into JuMP; the reply said the
  interface is extensible by design, but the thread shows no completed SIP solver and no Python
  equivalent — [Julia Discourse: SIP with JuMP](https://discourse.julialang.org/t/semi-infinite-programming-with-jump/16953.md)
- SIP can be reformulated as an equivalent SDP when the relevant function is "sufficiently closely
  approximable by a polynomial or a rational function", making standard SDP solvers applicable — [Papp & Alizadeh](https://ar5iv.arxiv.org/html/1512.06796)
- PyROS is itself an exchange/cutting-set method for exactly this structure: the user supplies the
  deterministic model and the uncertainty set, and PyROS runs "a generalized cutting-set algorithm for
  nonconvex two-stage problems" rather than enumerating the uncertainty — [PyROS preprint 2026](https://optimization-online.org/2026/06/pyros-the-pyomo-robust-optimization-solver/)
- A one-dimensional interval is directly expressible as a PyROS `BoxSet` ({q : qᴸ ≤ q ≤ qᵁ}) with
  n = 1 — [PyROS uncertainty sets](https://pyomo.readthedocs.io/en/stable/explanation/solvers/pyros/uncertainty_sets.html)

### Inferences

- A grid sweep on `r` is the discretisation (outer approximation) of a semi-infinite program. For a
  scalar `r` the usual objection to discretisation — exponential grid size in the dimension of the
  uncertainty — does not apply at all. With 101 points on `[0, 1]` the user has already solved a
  101-constraint relaxation of the SIP; the only error is the variation of `A(S, ·)` between adjacent
  grid points, bounded by the modulus of continuity and expressible explicitly.
- Therefore **the upgrade from "grid sweep" to "formal robust optimization" is not a change of solver.
  It is a change of reporting**: report `min_r A(S, r)` as the objective and defend the grid with (a) a
  Lipschitz or monotonicity argument on `A(S, ·)` in `r`, and (b) a check of whether the argmin over `r`
  is interior or at an endpoint. If `A(S, ·)` is monotone in `r` — plausible for an accuracy that
  degrades as measurements become more redundant — the worst case is at an **endpoint**, the sweep
  reduces to **two** evaluations (`r = 0`, `r = 1`), and the SIP question evaporates.
- Bilevel optimisation is the wrong frame: bilevel buys something when the inner player optimises a
  *different* objective subject to its own constraints. Here the inner player minimises the same `A`
  over a box, which is a minimax, and minimax over a 1-D box is a line search.

### Gaps

- **`SIPAMPL`, `nsips` and GAMS' SIP support remain unverified.** `nsips` appears only as a name in a
  2018 JuMP forum post; no release, repository or maintenance evidence was found for `SIPAMPL` or
  `nsips`, and nothing was found on GAMS. Neither name resolved to a GitHub repository in the API checks
  run for this task. Treat all three as **unverified and probably stale research code**.
- Whether PyROS can be driven with a 1-D `BoxSet` around a *simulated* (noisy, non-Pyomo-expressible)
  objective was not established; the documented restriction to Pyomo algebraic models suggests not.

---

## Q4. Robust simulation optimization and ranking-and-selection under input uncertainty

### Takeaway

This is the literature that actually matches the user's problem — finite candidate set, noisy
objective, nuisance input parameter — and it is **almost entirely paper-only**. SimOpt is real,
MIT-licensed and **verified maintained** (`simoptlib` 1.2.4, 2026-05-22; commits 2026-10-15), but a
SimOpt paper states ranking-and-selection was "a class not present in the library", and no SimOpt
module for input uncertainty was found. No released implementation of Song–Nelson–Hong, Corlu–Biller,
or the "most probable best" procedures was located.

### Cited Findings

- **Verified maintenance**: `simoptlib` PyPI latest **1.2.4, uploaded 2026-05-22**, MIT licence
  ("Copyright (c) 2025 simopt-a…"); repository `simopt-admin/simopt` `pushed_at` **2026-10-15**,
  `archived: false`, 79 stars, `spdx_id: MIT`. This closes the maintenance question the GitHub README
  left open (its Releases section is empty) — [PyPI JSON API, simoptlib](https://pypi.org/pypi/simoptlib/json); [GitHub REST API, simopt-admin/simopt](https://api.github.com/repos/simopt-admin/simopt)
- SimOpt is "a testbed of simulation-optimization problems and solvers", intended "to encourage the
  development and constructive comparison of simulation-optimization (SO) solvers (algorithms)", with a
  web interface launched by `simopt web` and 1,626 commits on master — [simopt-admin/simopt](https://github.com/simopt-admin/simopt)
- A SimOpt paper states that ranking-and-selection procedures — "designed for problems for which the
  feasible region is finite and all solutions can be simulated to some degree within the available
  budget" — "were a class not present in the library"; its solver library was mostly continuous
  optimization, direct-search, gradient-based and metamodel methods. The redesign "is available on a
  GitHub repository under a permissive open-source license and as a Python package" and adds common
  random numbers and bootstrapping for error estimates — [SimOpt redesign paper (NSF PAR)](https://par.nsf.gov/servlets/purl/10201012)
- The SimOpt README makes **no mention of ranking-and-selection solvers and no mention of input
  uncertainty or input model uncertainty** — [simopt-admin/simopt](https://github.com/simopt-admin/simopt)
- "Most probable best" (MPB): under a probability distribution over possible input parameters, the MPB
  is "the solution whose probability of being optimal is the largest". For a finite set of candidate
  input models it becomes a **nested** R&S problem: an inner R&S per input model finds the conditional
  best, and the outer level picks the solution with the highest preference probability. The authors
  derive a large-deviation rate for false selection, use it to set an optimal computing budget
  allocation (OCBA), then propose sequential sampling rules approximating it — [Kim, Kim & Song, arXiv 2207.07533](https://arxiv.org/pdf/2207.07533)
- Published as Kim, Kim & Song, "Selection of the Most Probable Best", *Operations Research* (2024),
  DOI 10.1287/opre.2022.0343; the Bayesian framing (posterior probability of being best given the
  real-world data) is in the WSC 2021 version — [Penn State Pure record](https://pure.psu.edu/en/publications/selection-of-the-most-probable-best-under-input-uncertainty/); [WSC 2021 paper 179](https://www.informs-sim.org/wsc21papers/179.pdf)
- Corlu & Biller's subset-selection procedure accounting for input parameter uncertainty is WSC 2015 — [WSC 2015 paper 037](https://www.informs-sim.org/wsc15papers/037.pdf)
- Song, Nelson & Hong formulate R&S with input uncertainty in an indifference-zone framework — [Penn State Pure record](https://pure.psu.edu/en/publications/input-uncertainty-and-indifference-zone-ranking-and-selection/)
- Eckman and co-authors, "Optimizing Input Data Collection for Ranking and Selection" (2025), treats
  how much input data to gather — the complementary decision — [arXiv 2502.16659](https://arxiv.org/pdf/2502.16659)
- A robust R&S strand exists in which "an ambiguity set covers several possible input distributions,
  and the goal is to pick the alternative with the best worst-case mean performance", with fixed-budget
  procedures that reduce the probability of incorrect selection — [search summary of robust R&S work (catalyzex author pages)](https://www.catalyzex.com/author/Zaile%20Li)

### Inferences

- The MPB formulation is the closest formal match *if* the user will put a prior on `r`; the robust R&S
  formulation is the closest match if they will not. Both supply a vocabulary and a correctness target
  ("probability of correct selection", "probability of incorrect selection under the worst-case input
  distribution") that a grid sweep plus a reported range does not.
- Because the implementations are paper-only while SimOpt itself is alive, the practical route is to
  **borrow the vocabulary and the budget-allocation idea, not the code**: allocate more replications to
  candidate subsets whose worst-case accuracy is close to the leader's, which is what OCBA-style rules
  do, and state the probability-of-correct-selection target explicitly.
- A noisy objective interacts badly with a worst-case operator: `min_r Â(S, r)` over a grid is a
  minimum of noisy estimates and is therefore **downward biased**, with bias growing in the number of
  grid points. Any formal statement must account for this; it is the single most likely source of a
  "wrong but plausible" number in this analysis.

### Gaps

- No code repository, supplementary material or package was found for Song–Nelson–Hong, Corlu–Biller,
  or Kim–Kim–Song MPB. Multiple searches returned only papers. The GitHub searches run for this task
  did not surface implementations either.
- Whether current SimOpt has since added R&S solvers is **unverified**: the claim that R&S was absent
  comes from the redesign paper, and the README does not list the current solver inventory. The repo is
  demonstrably active, so this could have changed — it needs a look at the solver directory.

---

## Q5. Sensitivity analysis as the cheaper alternative (SALib, OpenTURNS, UQpy, Dakota, Chaospy, R `sensitivity`, UQLab)

### Takeaway

**This family is in much better health than third-party trackers suggest** — SALib, OpenTURNS, Dakota,
UQpy and R's `sensitivity` are all verified maintained, and my earlier "UQpy is stale" note was wrong.
But none of these tools answers the user's actual question: they are built for *variance decomposition
over many inputs*, and the user has one input and wants an *invariance-of-ranking* statement, which
global sensitivity analysis does not produce.

### Cited Findings

- **SALib: v1.6.0, uploaded 2026-09-19; repo `SALib/SALib` `pushed_at` 2026-10-18, MIT, 1,021 stars.**
  Methods: Sobol; Method of Morris (incl. groups and optimal trajectories); Radial OAT; eFAST;
  RBD-FAST; Delta moment-independent measure; DGSM; Shapley effects; fractional factorial; HDMR; PAWN;
  Regional Sensitivity Analysis — [PyPI JSON API, SALib](https://pypi.org/pypi/SALib/json); [GitHub REST API, SALib/SALib](https://api.github.com/repos/SALib/SALib)
- Prior release v1.5.2 (12 October 2025) fixed PAWN for grouped problems, added a standard deviation to
  the reported statistic, and moved to `numpy.random.Generator` with a harmonised `seed` argument — [SALib changelog](https://salib.readthedocs.io/en/main/changelog.html); [Zenodo record 17330349](https://zenodo.org/records/17330349)
- **Dakota (Sandia): versioned release 6.24.0; nightly `stable_2026_10_25` dated 25 October 2026; repo
  `snl-dakota/dakota` `pushed_at` 2026-10-25, 161 stars.** The project notes the daily "stable" builds
  "are not recommended for most users" — [GitHub REST API, snl-dakota/dakota](https://api.github.com/repos/snl-dakota/dakota); [snl-dakota/dakota releases](https://github.com/snl-dakota/dakota/releases)
- Dakota's stated scope covers "uncertainty quantification with sampling, reliability, stochastic
  expansion, and epistemic methods; … mixed aleatory-epistemic UQ; and optimization under
  uncertainty" — [SciDAC FASTMath software catalog entry for Dakota](https://scidac-fastmath.lbl.gov/software-catalog/software_dakota)
- **OpenTURNS: `openturns` 1.27.post1, uploaded 2026-06-19, LGPL; repo `pushed_at` 2026-10-25, 353
  stars.** A 2026 JOSS paper describes the library; stable releases are "published on a semiannual
  basis", distributed through Conda, pip and Debian — [PyPI JSON API, openturns](https://pypi.org/pypi/openturns/json); [GitHub REST API, openturns/openturns](https://api.github.com/repos/openturns/openturns); [JOSS 10.21105/joss.10484](https://joss.theoj.org/papers/10.21105/joss.10484)
- **UQpy — CORRECTION, it is maintained: 4.2.1 uploaded 2025-08-19, MIT; repo `SURGroup/UQpy`
  `pushed_at` 2026-10-06, 362 stars.** A third-party tracker listing 4.1.5 with a November 2023 date is
  **stale and should not be cited** — [PyPI JSON API, UQpy](https://pypi.org/pypi/UQpy/json); [GitHub REST API, SURGroup/UQpy](https://api.github.com/repos/SURGroup/UQpy); stale source: [safetycli UQpy tracker](https://data.safetycli.com/packages/pypi/uqpy/)
- **Chaospy: 4.3.21 uploaded 2025-08-29, MIT; repo `jonathf/chaospy` `pushed_at` 2025-09-04, 480
  stars** — quiet for about 14 months, the softest of the group but not dead. A tracker citing v4.3.18
  / March 2025 is also out of date — [PyPI JSON API, chaospy](https://pypi.org/pypi/chaospy/json); [GitHub REST API, jonathf/chaospy](https://api.github.com/repos/jonathf/chaospy)
- **R `sensitivity`: version 1.31.0, published to CRAN 2026-02-27, GPL-2** — verified current, closing
  an earlier gap — [CRAN database, sensitivity](https://crandb.r-pkg.org/sensitivity)
- Interval/epistemic robust design in the engineering literature replaces objective and constraint
  functions with interval-valued versions bounding the output under uncertainty; a 2023 KU
  Leuven / TU Dortmund paper defines robustness as "the minimal width of the output interval" for
  lack-of-knowledge uncertainty — [Nonlinear/robust design preprint, TU Dortmund](https://lre.mb.tu-dortmund.de/storages/lre-mb/r/Pre-prints/2023_11.pdf)
- A 2013 paper handles epistemic inputs with **box-constrained optimization** and aleatory inputs with
  sampling — structurally the same inner worst-case-over-a-box a minimax uses, though the source does
  not call it minimax — [JUAA 10.1186/2195-5468-1-7](https://juaa-journal.springeropen.com/articles/10.1186/2195-5468-1-7)

### Inferences

- Global sensitivity analysis in the SALib/Sobol sense is **the wrong instrument for one input**. Sobol
  indices apportion output variance among several inputs; with a single input the first-order index is 1
  by construction and the analysis is vacuous. Morris screening likewise exists to rank many inputs
  cheaply.
- What the user actually wants from this family is simpler and has no package: a **one-dimensional
  profile** of `A(S, r)` for each candidate `S` across `r ∈ [0, 1]`, with the rank order of candidates
  overplotted. That is a few lines of matplotlib over the sweep they already run. SALib's value here is
  only as a citable, maintained framing if the analysis ever gains more nuisance parameters — and on
  that count it is a safe dependency (MIT, commits this month).
- **None of these tools emits a statement of the form "the ranking of designs is invariant over this
  interval."** The engineering epistemic-uncertainty literature gets closest, computing an
  interval-valued objective per design and comparing intervals — exactly the right object — but it
  computes it, it does not certify it.

### Gaps

- **Dakota's licence is unverified**: the GitHub API returns `NOASSERTION` and no primary licence
  source was located.
- **MATLAB `UQLab` was not investigated.** No release, version or maintenance information was gathered;
  it is not on PyPI or CRAN, so the checks run here could not reach it. The report should not
  characterise it.
- No tool in this family provides a formal invariance certificate; this is the central negative result
  of the section and is deliberate, not an omission.

---

## Q6. Formal machinery for "the conclusion is invariant over the whole uncertainty set" (robust ranking, stability of the optimal solution set, stochastic dominance)

### Takeaway

The formal machinery exists in fragments and **no package implements it**. The two useful published
ideas are (i) when several designs tie on worst-case performance, rank them by a secondary criterion
such as maximum regret or best-case performance, and (ii) build a *confidence set of designs
indistinguishable from the optimum* rather than naming a single winner. Both are directly implementable
on the user's existing sweep.

### Cited Findings

- Different uncertainty sets can produce robustly optimal solutions that **tie on worst-case
  performance**, and tied solutions can then be ranked by **maximum regret, best-case performance, or
  predictability** — [Uncertainty Preferences in Robust Mixed-Integer Linear Optimization with Endogenous Uncertainty, arXiv 2011.14875](https://arxiv.org/pdf/2011.14875)
- A 2025 paper on nonparametric comparison under input uncertainty "builds a confidence set of
  solutions that are indistinguishable from the optimum" — [Nonparametric Robust Comparison of Solutions under Input Uncertainty, arXiv 2511.04457](https://arxiv.org/pdf/2511.04457)
- A "robust ranking heuristic" for R&D project selection ranks projects by density or NPV while
  accounting for budgets of uncertainty, **without solving an optimization problem**; the NPV-based
  version found the true optimum more often — [Robust Optimization with Multiple Ranges: Theory and Application to R&D Project Selection](https://optimization-online.org/2010/07/2674/)
- Robust R&S frames this as choosing "the alternative with the best worst-case mean performance" over an
  ambiguity set of input distributions, with fixed-budget procedures targeting the probability of
  incorrect selection — [search summary of robust R&S work](https://www.catalyzex.com/author/Zaile%20Li)
- Background on the general trade-off (price of robustness; conservatism of budget uncertainty sets) is
  in Bertsimas, Brown & Caramanis — [arXiv 1010.5445](https://arxiv.org/pdf/1010.5445)

### Inferences

- The user's invariance statement is cheap to make rigorous **without any new software**, because the
  uncertainty set is one-dimensional. The construction: for each candidate subset `S`, compute the
  profile `r ↦ Â(S, r)` on a grid with replication; form a simultaneous confidence band for each
  profile; then "`S*` is the argmax for every `r ∈ [0, 1]`" is supported exactly when `S*`'s lower band
  lies above every competitor's upper band at every grid point. If the bands cross somewhere, the honest
  statement is "`S*` is optimal for `r < r₀` and `S'` for `r > r₀`" — a **partition of the uncertainty
  set by the identity of the winner**, which is a stronger and more interesting result than a range.
- The crossing point `r₀`, if one exists, is the most informative number in the whole analysis, and
  reporting it converts an admission of ignorance into a testable claim: "the choice of subset depends
  on `r` only through whether `r` exceeds `r₀`."
- The "tied on worst case, break ties by max regret" result from arXiv 2011.14875 is the right secondary
  criterion to name if the worst-case ranking is flat, which it may well be if `A(S, ·)` degrades
  similarly for all candidate subsets.

### Gaps

- **No software was found that certifies optimal-solution-set stability or produces a robust-ranking
  invariance statement.** Searches for "robust ranking" with invariance returned no matching paper and
  no package; no such package appeared in the PyPI or CRAN checks run for this task.
- No source connected **stochastic dominance of designs** to a released implementation; the term did not
  surface in any result.
- arXiv 2511.04457 was seen only at search-snippet depth (full text not fetched), so its confidence-set
  construction should be verified before the final report relies on it. **Unverified.**

---

## Q7. Partial identification as the honest framing: Manski bounds, Imbens–Manski intervals, and what is implemented

### Takeaway

Partial identification **is** the right framing — the parameter is not identified, so you report the
identified set — and the econometrics literature is mature. The coordinator's suspicion was correct:
**this software is largely a decade old**. `ivmte` last shipped 2021-09-17, `ivitr` 2020-09-11, and
`csabounds` was **removed from CRAN on 2022-07-09**. The only *currently maintained* options are
`ATbounds` (CRAN 2026-05-07) and `medrobust` (commits 2026-10-11 but **not on CRAN, 0 stars**);
`CausalBoundingEngine` is one-star research code last touched 2025-08-09. **No mainstream, maintained
package implements Manski bounds plus Imbens–Manski confidence intervals as a general tool.**

### Cited Findings

**The methods**

- Imbens & Manski, "Confidence Intervals for Partially Identified Parameters", *Econometrica* vol. 72,
  no. 6 (November 2004), pp. 1845–1857. The key distinction: "Rather than cover the entire
  identification region with fixed probability, they propose CIs that asymptotically cover the true
  value of the parameter with this probability." The paper also modifies the simplest version to fix
  non-uniform coverage near point identification — [Econometric Society record](https://econometricsociety.org/publications/econometrica/2004/11/01/confidence-intervals-partially-identified-parameters); [full text (Imbens, Harvard)](https://scholar.harvard.edu/sites/scholar.harvard.edu/files/imbens/files/confidence_intervals_for_partially_identified_parameters.pdf)
- Stoye (2009) argued that the paper's final result "implicitly assumes superefficient estimation of a
  nuisance parameter" — a caveat worth carrying — [CeMMAP working paper](https://www.ifs.org.uk/sites/default/files/output_url_files/cwp251414.pdf)
- Manski's no-assumption bounds are "the worst-case, no-assumption intervals"; they "derive sharp
  intervals for E[Y(1)] and E[Y(0)] using only observable conditional means and treatment
  probability" — [MetricGate partial identification docs](https://metricgate.com/docs/bounds-analysis-partial-identification/)
- Partial identification is described as a "School of Thought in Econometrics", associated with Manski,
  Tamer and Molinari, with its own inference theory — [Stoye, ISIPTA 2009 talk](https://isipta09.sipta.org/proceedings/papers/t050stoye_talk.pdf)
- Manski's reviews and books "catalogue much of this development", spanning econometrics, epidemiology
  and machine learning — [Bounding Causal Effects and Counterfactuals, arXiv 2508.13607](https://arxiv.org/pdf/2508.13607)

**The software, with every date verified**

- **`ATbounds` (R) — the one currently maintained CRAN bounds package. Version 0.1.1, published
  2026-05-07, GPL-3.** Its description: "Estimation and inference methods for bounding average
  treatment effects (on the treated) that are valid under an unconfoundedness assumption. The bounds
  are designed to be robust in challenging situations, for example, when the conditioning variables
  take on a large number of different values in the observed sample, or when the overlap condition is
  violated. This robustness is achieved by only using limited 'pooling' of information across
  observations." Implements Lee & Weidner, "Bounding Treatment Effects by Pooling Limited Information
  across Observations", *Journal of Econometrics*; code at github.com/ATbounds/ATbounds-r — [CRAN database, ATbounds](https://crandb.r-pkg.org/ATbounds)
- **`medrobust` (R) — active but pre-release and unadopted.** Repository `Data-Wise/medrobust`
  `pushed_at` **2026-10-11**, `archived: false`, **0 stars**; **no CRAN record**. Version 0.1.0.9000
  adds `bound_ci()`, which "applies the Imbens & Manski (2004) construction, widening the endpoints by
  standard errors obtained by re-evaluating the effect at the fixed optimal sensitivity parameter on
  resampled data." Its own NEWS reports raw estimated bounds **under-cover at small samples** and that
  the correction brings coverage close to nominal at n = 500 (exposure NDE 0.09 → 0.95, NIE
  0.12 → 0.93) — [GitHub REST API search, medrobust](https://api.github.com/search/repositories?q=medrobust); [medrobust NEWS (r-universe)](https://data-wise.r-universe.dev/medrobust/NEWS)
- **`CausalBoundingEngine` (Python) — research code, essentially unadopted.** Repository
  `tmaringgele/CausalBoundingEngine` `pushed_at` **2025-08-09**, `archived: false`, **1 star**; PyPI
  `causalboundingengine` **0.1.5, uploaded 2025-08-08, MIT**. It computes "Manski no-assumption bounds,
  autobound linear-programming bounds, entropy-regularized bounds, and Tian-Pearl bounds" for PNS; a
  closed-form Manski ATE is called as `scenario.ATE.manski()`, which the tutorial author reports
  matches a hand computation — [GitHub REST API search](https://api.github.com/search/repositories?q=CausalBoundingEngine); [PyPI JSON API, causalboundingengine](https://pypi.org/pypi/causalboundingengine/json); [Mendez, Introduction to Partial Identification (Python)](https://carlos-mendez.rbind.io/post/python_partial_identification/)
- **`ivmte` (R) — stale, 5 years: version 1.4.0 published 2021-09-17, GPL-2 | GPL-3; still live on
  CRAN** (its CRAN page is current, not an archive notice). Its `boundPvalue` "estimates the p-value for
  the treatment effect under partial identification" and can return forward, backward or both types of
  confidence intervals — [CRAN database, ivmte](https://crandb.r-pkg.org/ivmte); [ivmte boundPvalue reference](https://search.r-project.org/CRAN/refmans/ivmte/html/boundPvalue.html)
- **`ivitr` (R) — stale, 6 years: version 0.1.0 published 2020-09-11, GPL-3; still live on CRAN.** Its
  `estimate_Sid_bound` implements the Siddique (2013) partial identification bound for a binary
  instrument, treatment and outcome, with covariates — [CRAN database, ivitr](https://crandb.r-pkg.org/ivitr); [ivitr reference](https://search.r-project.org/CRAN/refmans/ivitr/html/estimate_Sid_bound.html)
- **`csabounds` (R) — DEAD, and the primary source confirms it.** The CRAN page reads: "Package
  'csabounds' was removed from the CRAN repository… Archived on 2022-07-09 as requires archived package
  'BMisc'." Its last published version was 1.0.0 on 2017-09-06. It provided "tight bounds on
  distributional treatment effect parameters when panel data is available" — [CRAN page, csabounds](https://cran.r-project.org/web/packages/csabounds/index.html); [CRAN database, csabounds](https://crandb.r-pkg.org/csabounds)
- **Noteworthy**: the dependency that killed `csabounds`, `BMisc`, is **back on CRAN at 1.4.10 published
  2026-08-22**, so the stated reason for the archival no longer holds — yet `csabounds` remains removed — [CRAN database, BMisc](https://crandb.r-pkg.org/BMisc)
- **`rbounds` (R) — the package the assignment named as "RBounds", and it is a different method.**
  Version 2.2, published 2022-04-29; its title is "Perform Rosenbaum Bounds Sensitivity Tests for
  Matched and Unmatched Data". Rosenbaum bounds test sensitivity to unobserved confounding in matched
  designs; they are not Manski no-assumption bounds and not an Imbens–Manski interval — [CRAN database, rbounds](https://crandb.r-pkg.org/rbounds)
- **`lpinfer` (R) — no CRAN record.** The Shi/Torgovitsky-style partial-identification inference code is
  not a CRAN package — [CRAN database query, lpinfer](https://crandb.r-pkg.org/lpinfer)
- **`GJRM` (R) — maintained: 0.2-6.9 published 2026-06-15, GPL (>= 2).** It cites Imbens & Manski in its
  `mb` help page but was not shown to implement the bounds as a general tool — [CRAN database, GJRM](https://crandb.r-pkg.org/GJRM); [GJRM mb reference](https://search.r-project.org/CRAN/refmans/GJRM/html/mb.html)
- **Stata `clrbound` — a different method.** "clrbound provides bound estimates for one-sided lower or
  upper intersection bounds on a parameter, while clr2bound and clr3bound provide two-sided bound
  estimates based on both lower and upper intersection bounds"; install with `ssc install clrbound`.
  Its method rests on **conditional moment inequalities** as in Chernozhukov et al. (2013), **not** on
  Imbens–Manski — [CeMMAP working paper on clrbound](https://www.ifs.org.uk/sites/default/files/output_url_files/cwp251414.pdf)
- Adjacent sensitivity-analysis packages that are maintained but solve a *different* problem (unmeasured
  confounding, not an unidentified structural scalar): `EValue` 4.1.4 published 2025-08-28, `sensemakr`
  0.1.6 published 2024-07-22 — [CRAN database, EValue](https://crandb.r-pkg.org/EValue); [CRAN database, sensemakr](https://crandb.r-pkg.org/sensemakr)
- A browser calculator for Manski and Imbens–Manski bounds on binary outcome/treatment data exists at
  MetricGate; it is **not** a package — [MetricGate bounds calculator](https://metricgate.com/calculator/bounds-analysis-partial-identification)

### Inferences

- **Partial identification is the correct framing of the user's situation, and also the easiest to
  execute, because the identified set is a one-dimensional projection.** The partially identified object
  is `A(S)` for each candidate `S`; its identified set is
  `[min_{r ∈ [0,1]} A(S, r), max_{r ∈ [0,1]} A(S, r)]`. Reporting that interval *is* the Manski-style
  no-assumption bound, and "report the range" — what the user already does — is literally the
  identified-set report. The user is doing partial identification; they are just not calling it that,
  and so are not getting the credit or the statistical apparatus that comes with the name.
- The one thing the user is missing is the **Imbens–Manski distinction**, and it matters because the
  objective is noisy. There are two different intervals: one covering the *identified set* with
  probability 1−α, and one (narrower) covering the *true value* with probability 1−α. With noisy
  `Â(S, r)`, naively taking `[min_r Â, max_r Â]` conflates sampling noise with identification width and
  is wrong in both directions — too wide because noise inflates the spread, too narrow at the endpoints
  because the min of noisy estimates is downward biased. The Imbens–Manski construction is the published
  fix.
- **The verified dates make the recommendation sharper, not softer: there is no package to adopt, so
  implement the formula.** `ivmte` and `ivitr` are 5–6 years stale, `csabounds` is removed, `rbounds` is
  a different method, `lpinfer` is not on CRAN, and the two things that *do* target Imbens–Manski
  (`medrobust`) or Manski (`CausalBoundingEngine`) have zero and one star respectively and are
  mediation- and binary-causal-specific. The Imbens–Manski interval for a scalar bound is a short
  closed-form calculation; `medrobust`'s `bound_ci()` is a readable reference implementation of the
  resampling version, best used as a model to copy rather than a dependency to take.
- The staleness pattern itself is informative: partial-identification *theory* is mature and still
  actively published, while the *tooling* never consolidated, because each paper's bounds are
  model-specific. That is an argument for hand-implementing the one formula the user needs, not for
  hunting further for a package.

### Gaps

- **No mature, econometrics-focused Python library for partial identification with documented inference
  methods exists**, as far as these checks reach. `CausalBoundingEngine` is the only confirmed Python
  option, and its one star and single-contributor repository make it unsuitable as a cited dependency.
- CRAN was queried only through the package database (crandb) for a named candidate list
  (`ivmte`, `ivitr`, `csabounds`, `GJRM`, `rbounds`, `ATbounds`, `lpinfer`, `sensitivity`, `BMisc`,
  `EValue`, `sensemakr`). **A full-text search of CRAN descriptions for "Manski" or "Imbens" was not
  run**, so a maintained package implementing Imbens–Manski generally is **not excluded**. This is the
  one remaining five-minute check worth doing.
- No Stata or R command was confirmed to implement the Imbens–Manski interval as a named, documented
  command; one search summary concluded "you would likely have to implement it yourself" and explicitly
  did not verify whether a community package does it.
- Tamer's *Annual Review of Economics* survey on partial identification was not located; only Stoye's
  ISIPTA talk and the arXiv bounding review were found as overviews.
- `medrobust`'s licence is **unverified** (not on CRAN; the GitHub search result did not expose a licence
  field).

---

## Q8. Practical recommendation: a single scalar nuisance in [0, 1] with a noisy objective

### Takeaway

Do not reach for RSOME, PyROS, `dro`, skwdro, or an SIP solver. **Keep the grid sweep, and change what
you compute from it and what you call it.** The grid sweep is already the standard discretisation of
the semi-infinite program and already produces the Manski identified set. What is missing costs no new
software: a worst-case objective reported as the decision criterion, a noise-aware interval on the
bounds (Imbens–Manski), and an explicit statement of whether the *ranking* of subsets is invariant over
`[0, 1]` — and if not, where it flips. The verified maintenance picture reinforces this: the one tool
that formally fits (RSOME) is dormant and GPL-3.0, and the one that is maintained (PyROS) excludes
discrete decisions by documentation.

### Cited Findings

- The grid is the discretisation of a semi-infinite program, and PyROS — the only maintained
  general-purpose RO solver (commits 2026-10-23) — is itself a cutting-set (iterative discretisation)
  method — [PyROS preprint 2026](https://optimization-online.org/2026/06/pyros-the-pyomo-robust-optimization-solver/); [GitHub REST API, Pyomo/pyomo](https://api.github.com/repos/Pyomo/pyomo)
- A one-dimensional interval is a `BoxSet` with n = 1 in that solver's taxonomy — so the "right"
  uncertainty set for this problem is the simplest one that exists — [PyROS uncertainty sets](https://pyomo.readthedocs.io/en/stable/explanation/solvers/pyros/uncertainty_sets.html)
- PyROS "does not support mixed-integer uncertainty sets", custom sets work "only when all uncertain
  parameters are continuous", and its documented scope is continuous-variable models — which excludes a
  subset-selection decision space — [PyROS uncertainty sets](https://pyomo.readthedocs.io/en/stable/explanation/solvers/pyros/uncertainty_sets.html); [Pyomo PyROS docs](https://pyomo.readthedocs.io/en/6.7.2/contributed_packages/pyros.html)
- RSOME, the package whose `minmax`/`maxmin` API most directly expresses this problem, last released
  2024-10-29, last received a commit 2024-11-15, and is GPL-3.0 — [PyPI JSON API, rsome](https://pypi.org/pypi/rsome/json); [GitHub REST API, XiongPengNUS/rsome](https://api.github.com/repos/XiongPengNUS/rsome)
- Every DRO ambiguity set in the maintained libraries is defined relative to an empirical distribution
  and a radius/divergence budget (Wasserstein, χ², KL, TV, MMD, Sinkhorn, holistic robust) — [PyPI dro](https://pypi.org/project/dro/); [skwdro docs](https://skwdro.readthedocs.io)
- Imbens & Manski distinguish intervals covering the identification region from intervals covering the
  true value, and provide the latter — [Econometrica 2004](https://econometricsociety.org/publications/econometrica/2004/11/01/confidence-intervals-partially-identified-parameters)
- Designs that tie on worst-case performance can be ranked by maximum regret, best-case performance or
  predictability — [arXiv 2011.14875](https://arxiv.org/pdf/2011.14875)
- SALib (MIT, v1.6.0 released 2026-09-19, commits 2026-10-18) is a safe dependency if the analysis ever
  acquires more than one nuisance parameter — [PyPI JSON API, SALib](https://pypi.org/pypi/SALib/json); [GitHub REST API, SALib/SALib](https://api.github.com/repos/SALib/SALib)

### Inferences

The recommendation, in order, with the reasoning attached:

1. **Rename what you are doing: this is partial identification.** `A(S)` is partially identified; the
   identified set is the sweep's range. Cite Manski; cite Imbens & Manski (2004) for the interval. This
   is the highest-value change and it is editorial, not computational.
2. **Check monotonicity in `r` first.** If `A(S, ·)` is monotone for every candidate `S` — plausible if
   larger between-measurement correlation means less independent information — the worst case is at an
   endpoint, and two evaluations (`r = 0`, `r = 1`) replace the whole sweep *and* the whole
   semi-infinite-programming question. Verify it empirically on the sweep already in hand; do not assume
   it.
3. **Report the worst case as the criterion, not the range as a caveat.** `S* = argmax_S min_r A(S, r)`
   is a defensible decision rule with a name (robust / minimax design) and a one-line justification. The
   range becomes supporting evidence, not an apology.
4. **Handle the noise explicitly, because `min_r Â` is downward biased.** The minimum of noisy estimates
   across grid points is biased low, and the bias grows with grid density. Use replication plus a
   simultaneous band across `r`, or Imbens–Manski endpoint widening, and say which. This is where this
   analysis would otherwise produce a number that is wrong but plausible.
5. **Make the invariance claim about the ranking, not the value.** Plot every candidate's profile over
   `r` on one axes with confidence bands. Either `S*` wins everywhere — a strong, citable claim — or
   there is a crossing point `r₀`, and reporting `r₀` ("the subset choice depends on `r` only through
   whether `r` exceeds `r₀`") is more informative than any range. If the worst-case ranking is flat,
   break ties by maximum regret per arXiv 2011.14875.
6. **Software: numpy/scipy plus matplotlib. Nothing else is required, and the maintenance data says so
   too.** Name RSOME and PyROS in the related-work sentence to show the robust-optimization machinery
   was considered and why it does not apply (no algebraic form for `A`; discrete decisions; 1-D
   uncertainty) — and note that RSOME is GPL-3.0 and dormant since late 2024, which is an independent
   reason not to take it as a dependency. Name `dro`/skwdro only to say DRO ambiguity sets need a sample
   of `r` that does not exist. Name SALib only if more nuisance parameters appear. For the Imbens–Manski
   interval, copy the formula; there is no maintained package to import.

**Why the heavyweight machinery buys nothing, stated plainly:** with a one-dimensional interval and no
distributional data, a Wasserstein or φ-divergence ball over distributions on `[0, 1]` has its worst
case at a point mass, so DRO collapses to the robust problem; the robust problem over a 1-D box has its
worst case found by a line search, so RO collapses to the sweep; and the sweep over a scalar is an
exact-to-the-grid solution of the semi-infinite program, so SIP collapses to the sweep too. Three layers
of machinery, and all three reduce to what the user already runs. The deficit is not in the
optimisation. It is in the inference (noise in the bounds) and in the reporting (invariance of the
ranking) — and those are the two things to fix.

### Gaps

- No source *prescribes* this exact workflow end to end; items 1–6 are an inference assembled from the
  cited partial-identification, robust-optimization and robust-R&S results, not a recommendation lifted
  from a single paper. Present it as a synthesis.
- The claim that `min_r Â(S, r)` over a grid is downward biased is a standard statistical fact about the
  minimum of noisy estimates (the same mechanism as the winner's curse in R&S), but **no specific
  citation for it was gathered**. It should be sourced before appearing as a stated fact in a
  manuscript.
