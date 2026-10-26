# Submodular subset selection, sensor selection, optimal experimental design, and class-separability / Bayes-error feature selection — software inventory as of October 2026

Scope note for the report writer: the user's problem is *small*. Known Gaussian class means (12–24 vertebral
classes, from published anatomical tables), covariance known up to one unknown scalar, and a modest number of
candidate measurements. Several of the heavyweight packages below are built for ground sets of 10^5–10^7 and
solve a problem the user does not have. I have flagged that mismatch where it matters, because the central
risk here is adopting a greedy approximation (and its guarantee caveats) for a problem that enumeration solves
exactly.

## Repository and release verification table (all fields queried 2026-10-26)

Every date below was read directly from the GitHub REST API (`pushed_at` = last commit to any branch), the
GitLab API (`last_activity_at`), the PyPI JSON API, or crandb.r-pkg.org. Nothing in this table is inferred.
No repository listed here is archived.

| Package | Code host | Last commit | Latest release | Licence | Stars | Verdict |
|---|---|---|---|---|---|---|
| `apricot` / `apricot-select` | github.com/jmschrei/apricot | **2025-11-17** | PyPI 0.6.1, **2021-02-18** | MIT | 537 | Alive, not actively developed; **pip ships 2021 code** |
| `submodlib` | github.com/decile-team/submodlib | **2025-05-14** | **not on PyPI at all** | MIT | 136 | Source install only; no release channel |
| SFO (Krause, MATLAB) | MathWorks FEX 20504 | — | **v2.0, March 2010** | — | — | **Abandoned 16 years** |
| PySensors / `python-sensors` | github.com/dynamicslab/pysensors | **2026-02-17** | PyPI 0.4.3, **2026-02-17** | MIT | 124 | **Maintained** |
| PyOED | **gitlab.com/ahmedattia/pyoed** | **2026-10-22** | v1.0 (CHANGELOG); not on PyPI | BSD (Argonne SF-23-005) | 0 (5 forks) | **Actively maintained** |
| `pyDOE3` | github.com/pydoe/pydoe | **2026-10-21** | PyPI 1.6.2, **2026-01-12** | ? | 345 | **Maintained** |
| `dexpy` | — | — | PyPI 0.12, **2017-06-12** | Apache | — | **Dead 9 years** |
| AlgDesign (R) | CRAN | — | **1.2.1.2, 2025-04-06** | GPL (>= 2) | — | Maintained |
| `skpr` (R) | github.com/tylermorganwall/skpr | **2026-09-15** | CRAN **1.9.2, 2025-09-30** | GPL-3 | 121 | **Maintained** |
| Pyro (`pyro.contrib.oed`) | github.com/pyro-ppl/pyro | **2026-10-05** | PyPI `pyro-ppl` 1.9.2, **2026-10-03** | — | 9073 | **Maintained** (module-level status separate) |
| BoTorch | **github.com/meta-pytorch/botorch** (moved from pytorch/) | **2026-10-16** | PyPI 0.18.1, **2026-06-08** | — | 3635 | **Maintained** |
| `sbi` | github.com/sbi-dev/sbi | **2026-10-23** | PyPI 0.27.0, **2026-08-04** | Apache-2.0 | 877 | **Very active** |
| iDAD | github.com/desi-ivanova/idad | **2021-12-30** | none | — | 26 | **Dead 5 years** |
| `spectral` (spectralpython) | github.com/spectralpython/spectral | **2026-09-04** | PyPI 0.25, **2026-07-25** | MIT | 688 | **Maintained — and has `bdist`** |
| `pysptools` | github.com/ctherien/pysptools | **2018-02-10** | PyPI 0.15.0, **2018-10-12** | Apache-2.0 | 55 | **Dead 8 years** |
| `scikit-feature` | github.com/jundongl/scikit-feature | **2024-07-11** | **not on PyPI** as `skfeature` | GPL-2.0 | 1588 | Stalled 2 years |
| `skfeature-gli` (fork) | — | — | PyPI 1.1.2, **2023-11-08** | ? | — | Stale |
| `mrmr-selection` | github.com/smazzanti/mrmr | **2024-11-19** | PyPI 0.2.8, **2023-06-30** | GPL-3.0 | 631 | **Stale by the >2023 criterion** |
| `feature-engine` | github.com/feature-engine/feature_engine | **2026-09-19** | PyPI 1.9.4, **2026-02-27** | BSD-3 | 2292 | **Maintained, production-grade** |
| `arfs` | github.com/ThomasBury/arfs | **2026-10-21** | PyPI 3.0.0, 2025-04-02 | MIT | 145 | **Maintained** |
| `pyitlib` | — | — | PyPI 0.3.1, **2025-05-17** | MIT | — | Quiet but within 2 years |
| `dit` | — | — | PyPI 2.3, **2026-09-26** | ? | — | **Maintained** |

Sources for the table: GitHub REST API `/repos/{owner}/{repo}`; GitLab API `/projects/ahmedattia%2Fpyoed`;
PyPI JSON API `/pypi/{package}/json`; crandb.r-pkg.org. Queried 2026-10-26.

**Two material corrections this verification produced**, both of which change the recommendation:
1. **PyOED is not missing — it is on GitLab and was committed to four days ago**, and it contains a
   `pyoed/optimization/binary_optimization/` module. It is the best-fit maintained OED package for this user.
2. **`spectral` (spectralpython) does implement the Gaussian Bhattacharyya distance** (`bdist`), it is MIT,
   and it was released in July 2026. The claim that no maintained Python package computes Gaussian class
   separability is **wrong** and must not appear in the report.

---

## Q1. Submodular optimization software: what is maintained and trusted in 2026?

### Takeaway

There is no production-grade, industry-trusted submodular optimization library. The field's two best-known
Python packages — `apricot` and `submodlib` — are academic research code with no tagged releases. Verified
2026-10-26: `apricot`'s last commit is **2025-11-17** but its last PyPI release is **2021-02-18**, so
`pip install apricot-select` delivers code 4.5 years older than the repository. `submodlib`'s last commit is
**2025-05-14** and it **is not on PyPI at all** — it must be built from source with its C++ engine. Krause's
SFO MATLAB toolbox is **abandoned (v2.0, March 2010 — 16 years)**. Both Python packages do implement lazy
greedy, stochastic greedy and cardinality-constrained maximization, and `apricot` states the (1 − 1/e) bound
explicitly.

### Cited Findings

**apricot (Schreiber, Bilmes, Noble)**
- Published in JMLR vol. 21 (2020), authors Jacob Schreiber, Jeffrey Bilmes, William Stafford Noble — [JMLR v21/19-467](https://www.jmlr.org/beta/papers/v21/19-467.html)
- PyPI package name is `apricot-select`; **latest version 0.6.1, released 18 February 2021** (confirmed via PyPI JSON API, 2026-10-26). The PyPI page carries no project description and does not state supported Python versions (the only version string is the uploader's `CPython/3.6.9`) — [PyPI apricot-select](https://pypi.org/project/apricot-select/)
- GitHub `jmschrei/apricot`: MIT licence, 537 stars, 189 commits, 53 forks. **The Releases section is empty — no tagged release ever.** No deprecation notice — [github.com/jmschrei/apricot](https://github.com/jmschrei/apricot)
- **Verified via GitHub API 2026-10-26: `pushed_at` = 2025-11-17T15:02:57Z, `archived` = false, 537 stars.** So the repository received commits within the last year but the published package did not — [GitHub API /repos/jmschrei/apricot](https://api.github.com/repos/jmschrei/apricot)
- Submodular functions on the repo page: feature-based, max (set) coverage, facility location, graph cut, sum redundancy, saturated coverage, and mixtures of functions — [github.com/jmschrei/apricot](https://github.com/jmschrei/apricot)
- Optimizers on the repo page: **naive greedy, lazy greedy, two-stage greedy, approximate lazy greedy, stochastic greedy, sample greedy, GreeDi, modular approximation, bidirectional greedy** — [github.com/jmschrei/apricot](https://github.com/jmschrei/apricot)
- The repo states the guarantee directly: a greedy subset "cannot have an objective value $1 - e^{-1}$ worse than the optimal subset" — [github.com/jmschrei/apricot](https://github.com/jmschrei/apricot)
- Cardinality constraint: the API takes a target subset size, e.g. `FacilityLocationSelection(100, ...)` to reduce 5,000 examples to 100. The repo does not use the phrase "cardinality constraint", and does not document user-defined submodular functions — [github.com/jmschrei/apricot](https://github.com/jmschrei/apricot)
- The JMLR paper describes only two functions (facility location, which needs memory quadratic in dataset size, and a feature-based function that scales to millions of examples but applies to fewer problems) and reports lazy greedy plus numba acceleration — [arXiv 1906.03543](https://arxiv.org/pdf/1906.03543)

**submodlib (DECILE / IIT Bombay)**
- Introduced by Kaushal, Ramakrishnan and Iyer (2022) as "an open-source, easy-to-use, efficient and scalable Python library for submodular optimization with a C++ optimization engine" — [arXiv 2202.10680](https://arxiv.org/pdf/2202.10680)
- One module of the DECILE project, alongside CORDS, TRUST, DISTIL and SPEAR — [ICML 2021 workshop listing](https://icml.cc/virtual/2021/11094)
- GitHub `decile-team/submodlib`: MIT licence, 136 stars, 245 commits, **Releases section empty**, 14 open issues, 4 open pull requests. The Contributors section says the project is "Currently maintained by CARAML Lab" — [github.com/decile-team/submodlib](https://github.com/decile-team/submodlib)
- **Verified via GitHub API 2026-10-26: `pushed_at` = 2025-05-14T15:43:58Z, `archived` = false.** The repo metadata `updated_at` is 2026-10-24, but that field tracks stars/watches, not commits — [GitHub API /repos/decile-team/submodlib](https://api.github.com/repos/decile-team/submodlib)
- **Verified 2026-10-26: `submodlib` returns no result from the PyPI JSON API — the package is not published on PyPI.** Installation is from source, which requires compiling the C++ engine
- Functions: Facility Location, Disparity Sum, Disparity Min, **Log Determinant**, Set Cover, Probabilistic Set Cover, Graph Cut, Feature Based; plus submodular mutual information variants (Facility Location MI, Graph Cut MI, Log Determinant MI, Concave Over Modular, Set Cover MI, …), conditional gain variants, and conditional mutual information variants — [github.com/decile-team/submodlib](https://github.com/decile-team/submodlib)
- Optimizers: **NaiveGreedy, LazyGreedy, StochasticGreedy, LazierThanLazyGreedy** — all four — [github.com/decile-team/submodlib](https://github.com/decile-team/submodlib)
- Documentation at [submodlib.readthedocs.io](https://submodlib.readthedocs.io/)

**SFO — Krause's MATLAB toolbox (stale)**
- Described in JMLR vol. 11 (2010), pp. 1141–1144, "SFO: A Toolbox for Submodular Function Optimization" — [JMLR v11/krause10a](https://www.jmlr.org/beta/papers/v11/krause10a.html)
- MathWorks File Exchange lists **version 2.0, last updated March 2010** — [MathWorks FEX 20504](https://www.mathworks.com/matlabcentral/fileexchange/20504-submodular-function-optimization)
- Algorithms include Fujishige's minimum-norm-point and Queyranne's algorithm for minimization, and lazy greedy, CELF and SATURATE (robust optimization) for maximization — [mloss listing](https://mloss-static.ml.tu-berlin.de/software/view/201/index.html)
- Octave use requires the `sfo_octavize` helper; demo is `sfo_tutorial.m` — [tutorial page](https://www2.spsc.tugraz.at/people/stschia/NIPS/Codes/external/sfo/html/sfo_tutorial_pub.html)

**The guarantee itself**
- For monotone submodular functions under a cardinality constraint, greedy achieves (1 − 1/e), and "this approximation guarantee is optimal for any algorithm that uses polynomially-many value queries" — [UW lecture notes, Ribeiro](https://homes.cs.washington.edu/~marcotcr/blog/greedy-submodular)
- Recent work gives a 0.385-approximation for non-monotone submodular maximization under a cardinality constraint using O_ε(n + k²) queries — [arXiv 2405.13994](https://arxiv.org/pdf/2405.13994)

### Inferences

- Neither `apricot` nor `submodlib` has ever cut a tagged release. For a project whose stated priority is
  minimising statistical bias and error, that means the exact code version has to be pinned by commit hash, not
  by version number, and the numerical behaviour of the selection has to be checked against an independent
  implementation.
- The 4.5-year gap between `apricot`'s last commit (2025-11-17) and its last PyPI release (2021-02-18) is a
  concrete trap: `pip install apricot-select` and `pip install git+https://github.com/jmschrei/apricot` give
  **different code**, and only the latter has the last four years of fixes. The 2021 wheel predates NumPy 2.x
  and modern numba, which is a plausible source of silent numerical or dtype misbehaviour in a 2026
  environment. `submodlib` has no wheel at all, so its C++ engine must compile locally — a different failure
  mode, and one that will bite on Windows.
- `submodlib` is the better fit for this user *on functionality*, because it is the only one of the two with a
  **Log Determinant** function, which is the one objective in this whole inventory that is provably submodular
  and directly corresponds to D-optimality (see Q2).
- No Google- or Meta-origin open submodular library surfaced in any search. I found no evidence such a package
  exists as a named, installable artifact.

### Gaps

- Generic `submodular` pip packages: not investigated. I found no evidence of a widely used one, but I did not
  search PyPI exhaustively, so absence is not established.
- Google's/Meta's internal-turned-open submodular tooling: no results found. Cannot confirm or deny existence.
- Last-commit dates for `apricot` and `submodlib` are now **verified** (see table); the earlier gap is closed.

---

## Q2. Is the user's objective actually submodular? Which objectives carry which guarantee?

### Takeaway

This is the most consequential section. **log-determinant / D-optimality is submodular and carries the honest
(1 − 1/e) guarantee. A-optimality and decision-theoretic value of information are NOT submodular — and
decision-theoretic value of information, which is the closest formal relative of "Bayes error of a
classifier", is proved non-submodular even in Naive Bayes models.** Mutual information and information gain are
submodular only under stated conditions, with an explicit XOR counterexample in the general case. A greedy
guarantee claimed for a Bayes-error or A-optimality objective is a false guarantee unless it is routed through
Das & Kempe's submodularity ratio, which gives (1 − e^{−γ}) with γ that must itself be bounded.

### Cited Findings

**Submodular — guarantee holds**
- The D-optimality criterion defined using the log determinant is submodular; the standard justification is that the log determinant of a principal submatrix is a submodular function of the indices defining the submatrix — [arXiv 2407.16212, "Optimal experimental design: Formulations and computations"](https://arxiv.org/pdf/2407.16212)
- **Caveat on applying off-the-shelf solvers to it:** log-determinant evaluations may be non-positive, so most existing algorithms for submodular maximization are not directly applicable — [arXiv 2407.16212](https://arxiv.org/pdf/2407.16212)
- **Sign-convention trap:** sources state this from opposite sides. Some say the negative log-determinant (the covariance-side form, log det Σ) is submodular; others describe the D-optimal objective as supermodular, which implies greedy is (1 − e^{−1})-optimal. These are the same result — minimising log det of the posterior covariance corresponds to maximising log det of the information matrix — [arXiv 2407.16212](https://arxiv.org/pdf/2407.16212); [arXiv 1711.01501](https://arxiv.org/pdf/1711.01501)
- Greedy selection for D-optimal design therefore carries the classic (1 − 1/e) guarantee — [arXiv 1711.01501](https://arxiv.org/pdf/1711.01501)

**NOT submodular — guarantee does not hold**
- "The A-optimality criterion is not submodular", attributed to Krause et al. (2008) — [arXiv 2407.16212](https://arxiv.org/pdf/2407.16212)
- The A-optimal objective is not supermodular in general, and it is unclear why greedy methods work well for it in practice — [arXiv 1711.01501](https://arxiv.org/pdf/1711.01501)
- **Krause & Guestrin (JAIR 35, 2009, pp. 557–591): "Decision-theoretic value of information is not submodular, even in Naive Bayes models."** — [arXiv 1401.3474](https://arxiv.org/pdf/1401.3474); [JAIR record](https://resolver.caltech.edu/CaltechAUTHORS:20090808-142502030)
- Information gain is **not submodular in general**; the authors give an XOR counterexample. Under weak conditional independence assumptions — specifically that the variables in S are independent given U — information gain is guaranteed to be submodular — [Krause & Guestrin, UAI 2005, arXiv 1207.1394](https://arxiv.org/pdf/1207.1394)
- Entropic mutual information is not generally submodular. The *submodular* mutual information is submodular in one argument with the other held fixed, for the class of submodular functions whose third-order partial derivatives satisfy a non-negativity condition (examples given: facility location, set cover) — [Iyer, Khargonkar, Bilmes, Asnani, arXiv 2006.15412](https://arxiv.org/pdf/2006.15412)
- Krause, Singh & Guestrin (JMLR 9, 2008) prove that maximizing mutual information over sensor configurations is NP-complete, and give a polynomial-time approximation "within (1−1/e) of the optimum … by exploiting the submodularity of mutual information". **The abstract states no condition for that submodularity** — [JMLR v9/krause08a](https://jmlr.org/papers/v9/krause08a.html)
- Krause & Guestrin's UAI 2005 result is a *randomized* algorithm with a (1 − 1/e − ε) approximation guarantee, i.e. with an additive ε slack, not the clean (1 − 1/e) — [UAI 2005 record](https://mlanthology.org/uai/2005/krause2005uai-near/)

**Weak submodularity — the honest fallback**
- Das & Kempe (JMLR 19, 2018) introduce the **submodularity ratio** γ; when f has submodularity ratio γ, greedy gives a **(1 − e^{−γ})** approximation. γ = 1 for submodular functions and "becomes smaller as the function exhibits more and more non-submodular behavior" — [JMLR v19/16-534](https://jmlr.org/papers/v19/16-534.html)
- Harshaw et al. later showed this guarantee "is the best that can be achieved by any polynomial time algorithm" — [per TU Darmstadt review](https://www2.mathematik.tu-darmstadt.de/~disser/pdfs/DisserWeckbecker24.pdf)
- Bian et al. (2017) extended the analysis to a tight bound that depends on both the submodularity ratio and the objective's curvature, and bounded both for Bayesian A-optimal design — [arXiv 1711.01501](https://arxiv.org/pdf/1711.01501); [TU Darmstadt review](https://www2.mathematik.tu-darmstadt.de/~disser/pdfs/DisserWeckbecker24.pdf)
- **A concrete usable bound for A-optimality:** a spectral-norm bound on the observations gives a lower bound on the submodularity ratio of A-optimality, and when that norm (the highest signal-to-noise ratio) is low the bound approaches 1, so A-optimality behaves almost like a submodular function — [arXiv 1711.01501, "Approximate Supermodularity Bounds for Experimental Design"](https://arxiv.org/pdf/1711.01501)
- Avron & Boutsidis proposed a greedy algorithm for A-optimality with approximation ratio O(n/k) with respect to f(XᵀX) — a much weaker bound — [arXiv 2407.16212](https://arxiv.org/pdf/2407.16212)
- Das & Kempe's original motivation was sparse approximation; their Restricted Isometry Property results show RIP design matrices give bounded submodularity ratios, supporting greedy feature selection — [JMLR v19/16-534](https://jmlr.org/papers/v19/16-534.html)
- Because of the D/A gap, the D-optimal objective is often used as a surrogate for A-optimality, though this "is only justified when the problem has some inherent structure" — [arXiv 2407.16212](https://arxiv.org/pdf/2407.16212); [arXiv 1711.01501](https://arxiv.org/pdf/1711.01501)
- Weak-submodularity guarantees are almost all for **cardinality constraints only**. A 2026 preprint notes it "is not known whether the greedy algorithm achieves any non-trivial approximation ratio" for matroid constraints — [arXiv 2609.05008](https://arxiv.org/pdf/2609.05008)

### Inferences

- The user's natural objective — "how separable are the 12–24 classes under this measurement subset", scored by
  a Bayes-error bound — is a **decision-theoretic value-of-information objective**, and Krause & Guestrin's JAIR
  2009 result says exactly that family is not submodular even in Naive Bayes models. So: running `apricot` or
  `submodlib` greedy on a Bayes-error objective and reporting "(1 − 1/e)-optimal" would be an overclaim of
  precisely the kind the user said is worse than no guarantee.
- The two defensible routes to a *stated* guarantee are (a) reformulate the objective as log-det of the Fisher
  information / posterior precision for the chosen measurements, which is genuinely submodular, and accept that
  D-optimality is a surrogate for separability rather than separability itself; or (b) compute a submodularity
  ratio bound for the actual objective and report (1 − e^{−γ}) with the γ shown. Route (b) is honest but the
  published γ bounds are for A-optimality and sparse regression, not for Bayes error.
- For a small candidate set the whole question is moot — see Q9. Enumeration gives the exact optimum and no
  guarantee language is needed. This is the cleanest escape from the submodularity question.
- The "conditional suppressor-free" phrasing in the assignment did not appear in any search. The substantive
  caveat it points at is real and is sourced above (XOR counterexample; conditional-independence condition;
  value of information non-submodular in Naive Bayes). I would not put the phrase "conditional suppressor-free"
  in the report attributed to Krause & Guestrin without finding it in the paper text.

### Gaps

- **E-optimality**: I found no source addressing whether E-optimality (minimising the largest eigenvalue of the
  covariance) is submodular. The assignment asserts it is not submodular in general; I could not confirm that
  from a primary source and it should not be stated as sourced.
- I could not decode the Krause & Guestrin UAI 2005 PDF (arXiv 1207.1394) to quote the theorem and the XOR
  counterexample verbatim; the condition and counterexample above come from a search-snippet reading of that
  PDF, not from a direct quote.
- Whether Krause, Singh & Guestrin (JMLR 2008) prove mutual information *exactly* submodular or only
  *approximately* submodular (e.g. under a fine-enough-discretization condition) is **not resolvable from the
  abstract**, which simply says the approximation "exploits the submodularity of mutual information". The body
  of the paper would settle it. This matters: the UAI 2005 companion result carries a (1 − 1/e − ε) bound with
  an additive slack, which is the signature of approximate submodularity.

---

## Q3. Sensor placement / sensor selection software

### Takeaway

**PySensors is the one genuinely maintained, installable, scikit-learn-style package here (release 0.4.3,
February 2026, MIT), and its SSPOC mode solves sensor selection *for classification* — the closest named
problem to the user's.** Joshi & Boyd's convex relaxation is the method with the most useful property for this
user — it returns both a subset *and a bound on the best performance achievable by any selection* — but the
reference code is MATLAB from 2008.

### Cited Findings

**PySensors (Brunton group / dynamicslab)**
- "PySensors is a Python package for selecting and placing a sparse set of sensors for classification and reconstruction tasks. Specifically, PySensors implements algorithms for data-driven sparse sensor placement optimization for reconstruction (SSPOR) and sparse sensor placement optimization for classification (SSPOC)." — [python-sensors.readthedocs.io](https://python-sensors.readthedocs.io/en/latest/examples/pysensors_overview.html)
- Designed as a scikit-learn-style API — [python-sensors.readthedocs.io](https://python-sensors.readthedocs.io/)
- PyPI package name is **`python-sensors`**; **latest version 0.4.3, released 17 February 2026**, MIT licence. The page confirms "The SSPOC (Sparse Sensor Placement Optimization for Classification) class is used to solve classification problems", with an example that chooses sensor positions while training a linear classifier — [PyPI python-sensors](https://pypi.org/project/python-sensors/)
- **Verified via GitHub API 2026-10-26: `dynamicslab/pysensors`, `pushed_at` 2026-02-17T22:03:15Z, 124 stars, not archived** — the repository commit and the PyPI 0.4.3 release are the same day, consistent with the JOSS publication date — [GitHub API /repos/dynamicslab/pysensors](https://api.github.com/repos/dynamicslab/pysensors)
- **PySensors 2.0** adds spatially constrained placement: maximum or exact sensor counts in specified regions, predetermined (fixed) sensor locations, minimum distances between sensors; plus custom basis inputs and uncertainty heat maps — [arXiv 2509.08017](https://arxiv.org/html/2509.08017v2)
- The 2.0 paper was published in the Journal of Open Source Software on 17 February 2026, DOI 10.21105/joss.09265 — [JOSS paper](https://www.theoj.org/joss-papers/joss.09265/10.21105.joss.09265.pdf)
- Repository: [github.com/dynamicslab/pysensors](https://github.com/dynamicslab/pysensors)

**Joshi & Boyd convex relaxation**
- "Sensor Selection via Convex Optimization", IEEE Transactions on Signal Processing, 2009. Problem: choose k of m candidate sensors to minimise estimation error. The convex heuristic "gives a subset selection as well as **a bound on the best performance achievable by any selection**" — [Boyd's page](https://stanford.edu/~boyd/papers/sensor_selection.html); [paper PDF](https://automatica.dei.unipd.it/old/public/Schenato/PSC/2010_2011/gruppo4-Building_termo_identification/Bibliografia%20Casuale/Sensor%20Selection%20via%20Convex%20Optimization.pdf)
- MATLAB code on Boyd's site: the numerical example `sens_sel_ex1.m` is **dated May 2008**; `sens_sel_loc.m` implements a swap-based local search that updates the inverse covariance after each accepted swap. The paper describes a greedy swap method giving a 2-opt selection, i.e. one where no swap of a selected and an unselected sensor improves the objective — [sens_sel_ex1.m](https://web.stanford.edu/~boyd/papers/matlab/sensor_selection/sens_sel_ex1.m); [sens_sel_loc.m](https://stanford.edu/~boyd/papers/matlab/sensor_selection/sens_sel_loc.m)
- Later work notes the original method's O(n³) complexity limits it on many-degree-of-freedom / large candidate problems — [arXiv 2009.09315](https://arxiv.org/pdf/2009.09315)
- A 2020 line of work does data-driven sparse sensor placement based on **A-optimal** design with ADMM — [arXiv 2010.09329](https://arxiv.org/pdf/2010.09329)

**Krause's sensor placement**
- Krause, Singh & Guestrin, JMLR 9 (2008), "Near-Optimal Sensor Placements in Gaussian Processes" — the canonical formulation (maximize mutual information between selected and unselected locations), NP-completeness result and (1−1/e) approximation — [JMLR v9/krause08a](https://jmlr.org/papers/v9/krause08a.html)
- Krause's robust variant: "Robust Submodular Observation Selection", JMLR 9 (2008) — [JMLR v9/krause08b](https://www.jmlr.org/beta/papers/v9/krause08b.html)
- Krause's code distribution point is the SFO MATLAB toolbox (see Q1) — stale since March 2010, and includes SATURATE for the robust problem — [mloss listing](https://mloss-static.ml.tu-berlin.de/software/view/201/index.html)

### Inferences

- Joshi & Boyd's bound is the single most useful artifact in this section for a bias-conscious user: it is an
  *outside check*. You solve the relaxation, get an upper bound on achievable performance, and compare your
  chosen subset against it. If the gap is small you know your subset is near-optimal without appealing to any
  submodularity claim at all. Re-implementing the relaxation in CVXPY is a small job and avoids depending on
  2008 MATLAB.
- PySensors' SSPOC is a *data-driven* method: it needs training data to form a basis (POD/SVD) and fit a linear
  classifier. The user has analytic class-conditional distributions, not a data matrix. SSPOC can be fed
  synthetic draws from the known Gaussians, but that introduces Monte Carlo error into a problem that has a
  closed form — exactly the substitution the user is trying to avoid.

### Gaps

- I did not find a 2024–2026 sensor-selection package other than PySensors 2.0. Absence here is weakly
  established — I ran one targeted search.
- No Python port of Joshi & Boyd's `sens_sel_approxnt` was located.

---

## Q4. Optimal experimental design packages — which do discrete design-point selection from a candidate set?

### Takeaway

**PyOED (Argonne) is the best-fit package and it is actively maintained — it lives on GitLab, not GitHub or
PyPI, which is why it looks missing.** Verified 2026-10-26: last activity **2026-10-22**, BSD-licensed, and it
ships a `pyoed/optimization/binary_optimization/` module containing greedy, stochastic, constrained and robust
binary optimizers — i.e. discrete "which measurements do I take" optimization, backed by a 2024 ACM TOMS
paper. R's `AlgDesign` (CRAN 1.2.1.2, 2025-04-06) remains the most mature *classical* route: pick n points from
a candidate list, optimising D, A or I. `skpr` (CRAN 1.9.2, 2025-09-30) and `pyDOE3` (PyPI 1.6.2, 2026-01-12)
are both maintained. `dexpy` is **dead (last release 2017-06-12)**. OpenTURNS shows no D-optimal capability in
the evidence I found.

### Cited Findings

**AlgDesign (R) — strongest match**
- **CRAN version 1.2.1.2, published 2025-04-06, licence GPL (>= 2)** (verified via crandb.r-pkg.org, 2026-10-26) — [crandb AlgDesign](https://crandb.r-pkg.org/AlgDesign)
- `optFederov()` "calculates an exact or approximate algorithmic design using Federov's exchange algorithm" and can target D, A or I criteria — [rdrr.io AlgDesign/Federov](https://rdrr.io/cran/AlgDesign/man/Federov.html)
- The `data` argument **is the candidate list**; `frml` "may be omitted if data is the fully model expanded candidate list" — [rdrr.io AlgDesign/Federov](https://rdrr.io/cran/AlgDesign/man/Federov.html)
- `nTrials` sets the number of runs to select; `nRepeats` (default 5) and `maxIteration` (default 100) control the search — [rdrr.io AlgDesign/Federov](https://rdrr.io/cran/AlgDesign/man/Federov.html)
- Reported criteria: D is the kth root of the generalized variance; the package also reports average coefficient variance (A) and average prediction variance (I) — [RDocumentation AlgDesign 1.2.1.1 optFederov](https://www.rdocumentation.org/packages/AlgDesign/versions/1.2.1.1/topics/optFederov)
- Worked example: a 36-run candidate set from a 3×3×2×2 factorial, asking for a 12-run D-optimal subset, D-efficiency 0.866 — [r-statistics.co](https://r-statistics.co/Optimal-Experimental-Design-in-R.html)

**skpr (R) — maintained, previously a gap**
- **GitHub `tylermorganwall/skpr`: `pushed_at` 2026-09-15T23:28:20Z, 121 stars, not archived** (GitHub API, 2026-10-26) — [GitHub API /repos/tylermorganwall/skpr](https://api.github.com/repos/tylermorganwall/skpr)
- **CRAN version 1.9.2, published 2025-09-30, licence GPL-3** (crandb.r-pkg.org, 2026-10-26) — [crandb skpr](https://crandb.r-pkg.org/skpr)

**pyDOE3 (Python)**
- **GitHub `pydoe/pydoe`: `pushed_at` 2026-10-21T17:30:22Z, 345 stars, not archived; PyPI `pyDOE3` 1.6.2 released 2026-01-12** (GitHub + PyPI APIs, 2026-10-26) — [GitHub API /repos/pydoe/pydoe](https://api.github.com/repos/pydoe/pydoe); [PyPI pyDOE3](https://pypi.org/project/pyDOE3/)
- The `pyDOE3.doe_optimal` module "provides advanced algorithms for constructing optimal experimental designs", with `generate_candidate_set` and `optimal_design`, a `criterion="D"` option and `method="detmax"`, returning D-efficiency in an info dict — [pyDOE3 docs, doe_optimal](https://pydoe3.readthedocs.io/en/stable/reference/doe_optimal/)
- A third-party registry page for pyDOE3 1.3.0 documents `optimal_design` taking a candidate set of shape (N0, k), a requested run count, a model degree, and **criterion "D", "A" or "I"**, returning selected points plus a statistics dict — [Tessl registry, pypi-pydoe3 1.3.0](https://tessl.io/registry/tessl/pypi-pydoe3/1.3.0/files/docs/optimal-design.md) *(third-party registry, not upstream docs — verify against the installed package)*

**PyOED (Argonne / Attia) — located, and actively maintained**
- **Source repository is on GitLab, not GitHub: [gitlab.com/ahmedattia/pyoed](https://gitlab.com/ahmedattia/pyoed).** Verified via the GitLab API on 2026-10-26: description "Python-based tool for Optimal Experimental Design", `created_at` 2021-09-07, **`last_activity_at` 2026-10-22T03:00:21Z**, public, 5 forks, default branch `main`, not archived — [GitLab API /projects/ahmedattia%2Fpyoed](https://gitlab.com/api/v4/projects/ahmedattia%2Fpyoed)
- **Licence: BSD.** The repository root contains `LICENSE.txt` and `SF-23-005_BSD_License.pdf` (SF-23-005 is an Argonne software release number) — [GitLab repository tree](https://gitlab.com/api/v4/projects/ahmedattia%2Fpyoed/repository/tree)
- **It has a dedicated binary (discrete) optimization module.** `pyoed/optimization/binary_optimization/` contains `greedy_binary_optimization.py`, `stochastic_binary_optimization.py`, `constrained_binary_optimization.py`, `robust_binary_optimization.py` and `robust_constrained_binary_optimization.py`. Sibling modules are `core/`, `policy_optimization/`, `test_functions/` and `scipy_optimization.py` — [GitLab tree, pyoed/optimization/binary_optimization](https://gitlab.com/api/v4/projects/ahmedattia%2Fpyoed/repository/tree?path=pyoed/optimization/binary_optimization)
- Top-level package layout: `assimilation/`, `configs/`, `examples/`, `ml/`, `models/`, `oed/`, `optimization/`, `stats/`, `tests/`, `utility/` — [GitLab tree, pyoed](https://gitlab.com/api/v4/projects/ahmedattia%2Fpyoed/repository/tree?path=pyoed)
- The CHANGELOG reads "Initiating the changelog. This marks V 1.0 of the package." The repo also carries `pyproject.toml`, `pytest.ini`, `conftest.py`, `towncrier.toml`, `environment.yml` and `CONTRIBUTING.md` — ordinary software-engineering practice rather than a paper dump — [CHANGELOG](https://gitlab.com/ahmedattia/pyoed/-/raw/main/CHANGELOG)
- **Verified 2026-10-26: neither `pyoed` nor `PyOED` resolves on the PyPI JSON API — it is not pip-installable from PyPI.** Install is from the GitLab repository
- A related GitLab project, `abhijit-c/pyoed-fenicsx` (last activity 2025-07-18), couples PyOED to FEniCSx — [GitLab project search](https://gitlab.com/api/v4/projects?search=pyoed)
- Canonical reference: Chowdhary, Ahmed & Attia, "PyOED: An extensible suite for data assimilation and model-constrained optimal design of experiments", **ACM Transactions on Mathematical Software, 2024, DOI 10.1145/3653071** — [CrossRef record](https://api.crossref.org/works/10.1145%2F3653071); [CiteDrive record](https://citedrive.com/en/discovery/pyoed-an-extensible-suite-for-data-assimilation-and-model-constrained-optimal-design-of-experiments/)
- Began as a v1.0 release by Attia and Ahmed; the preprint is arXiv 2301.08336 with three versions — [arXiv 2301.08336v3](https://www.arxiv.org/abs/2301.08336v3)
- Targets researchers studying OED methods on simulation models; the authors note OED, Bayesian inversion and data assimilation are closely related with overlapping formulations — [arXiv 2301.08336v3](https://www.arxiv.org/pdf/2301.08336v3)
- Attia's related work includes **Bayesian A-optimal design with uncertain parameters** (with Leyffer and Munson) and robust design for nonlinear inverse problems (with Chowdhary and Alexanderian), described by Argonne as "utility-agnostic" — [Argonne MCS article](https://www.anl.gov/mcs/article/from-algorithms-to-software-making-optimal-experimental-design-easier-and-cheaper)
- Documentation is hosted at web.cels.anl.gov/~aattia/pyoed/ — [Key Concepts page](https://web.cels.anl.gov/~aattia/pyoed/concepts.html) *(returned HTTP 403 to automated fetch)*

**OpenTURNS**
- The GEMSEO wrapper enumerating OpenTURNS DOE algorithms lists Sobol, Halton, LHS, factorial, composite and similar — **no D-optimal algorithm appears** — [GEMSEO lib_openturns source](https://gemseo.readthedocs.io/en/5.3.0/_modules/gemseo/algos/doe/lib_openturns.html)

### Inferences

- **PyOED is the strongest single recommendation in this whole inventory for the user's problem**, and the
  reason is the `binary_optimization` module: the user's problem *is* binary optimization over a design vector
  (take this measurement or not), and PyOED offers greedy, stochastic, constrained and robust variants of it
  behind one interface, under a permissive BSD licence, with a TOMS-reviewed paper, a towncrier changelog, a
  pytest suite, and a commit four days old. Having greedy and a stochastic/robust alternative in the same
  package is also exactly the setup needed to check one optimizer against another, which is the outside check
  this project's history calls for.
- PyOED's GitLab hosting is the whole reason it reads as abandoned in a GitHub/PyPI-shaped search. This is
  worth stating in the report, because any reader repeating the obvious search will reach the wrong conclusion.
  The cost of GitLab hosting is real though: no wheel, 0 stars, and dependency pinning is on the user.
- `AlgDesign`'s `optFederov` is a drop-in for "choose k of m candidate measurements, scored by D, A or I", with
  the criteria reported rather than inferred. For a user with a Gaussian linear-model framing, this is the
  lowest-risk, best-documented *classical* path, and it is in R rather than Python — a real but small friction
  cost. It is also the natural independent implementation to check PyOED against.
- Neither AlgDesign nor pyDOE3 optimises a *class-separability* objective. They optimise regression-design
  criteria. Mapping "which measurements separate 12–24 vertebral classes" onto D/A/I requires framing the
  problem as parameter estimation in a linear model, which is a modelling decision, not a software one.

### Gaps

- **`skpr` (R)** is confirmed maintained (dates above) but I could not retrieve its API documentation, so I
  cannot report how its `gen_design`/`eval_design` handle a candidate set or which criteria they report. Only
  its maintenance state is verified.
- **`dexpy`** is **dead**: PyPI 0.12, released 2017-06-12, Apache licence (PyPI JSON API, 2026-10-26). Beyond
  that I have only a passing mention as a screening tool alongside pyDOE3 — [Smithery skill page](https://smithery.ai/skills/jkitchin/design-of-experiments). No API details.
- **`OptimalDesign.jl`**: not investigated.
- **Dakota's design capability**: not investigated.
- **PyOED's remaining unknowns**: which optimality criteria the `oed/` module exposes (A-, D-, Bayesian) is
  **not verified from source** — Attia's published work on Bayesian A-optimal design with uncertain parameters
  makes A-optimality very likely, and the module names confirm *discrete/binary* optimization, but I inspected
  only the directory listing, not the criterion implementations. The documentation at
  web.cels.anl.gov/~aattia/pyoed returned HTTP 403 to automated fetch.
- OpenTURNS: the GEMSEO wrapper is indirect evidence. OpenTURNS' own docs were not searched; a D-optimal module
  may exist outside the GEMSEO-wrapped set.

---

## Q5. Bayesian optimal experimental design (BOED) in 2026 — what has maintained code?

### Takeaway

`pyro.contrib.oed` ships inside a broadly used, maintained probabilistic programming library — Pyro's last
commit is 2026-10-05 — but **the OED module itself is functionally frozen: every commit touching
`pyro/contrib/oed/` since 2021 has been a repo-wide formatter or packaging change.** That is an important
distinction the repository-level date hides, and it means the library's maintenance does not transfer to this
module. It is still the implementation the Foster et al. NeurIPS 2019 variational-EIG paper points to.
`sbi` is very actively maintained (last commit 2026-10-23) but solves inference, not design. BoTorch is
maintained and **has moved to `meta-pytorch/botorch`**. The amortized/deep adaptive design line is research
code and **iDAD is dead: its last commit is 2021-12-30, five years ago, with 26 stars**; I found no RL-BOED
repository at all. All of it is heavy machinery for a problem the user may be able to solve in closed form.

### Cited Findings

- `pyro.contrib.oed` "provides tools for creating optimal experiment designs for Pyro models", including estimators for the expected information gain (EIG) criterion; named estimators include `vnmc_eig` and `laplace_eig`; EIG is maximized with optimizers from `pyro.optim` — [Pyro contrib.oed docs](https://pyro4ci.readthedocs.io/en/latest/contrib.oed.html)
- The canonical paper is Foster et al., "Variational Bayesian Optimal Experimental Design", NeurIPS 2019; it "introduce[s] several classes of fast EIG estimators by building on amortized variational inference" and its footnote links to docs.pyro.ai/en/stable/contrib.oed.html as the implementation — [alphaXiv 1903.05480](https://alphaxiv.org/abs/1903.05480); [NeurIPS 2019 metadata](https://papers.neurips.cc/paper_files/paper/2019/file/d55cbf210f175f4a37916eafe6c04f0d-Metadata.json)
- **`pyro.contrib.oed` is functionally frozen, despite Pyro itself being active.** The five most recent commits touching `pyro/contrib/oed/` are, in order (GitHub commits API filtered by path, queried 2026-10-26): `2026-09-05` "Switch formatting from Black to Ruff (#3474)", `2026-09-01` "Migrate packaging metadata to pyproject.toml (#3470)", `2023-02-03` "rerun newest black on repo (#3178)", `2022-02-24` "Update black formatting (#3020)", `2021-07-02` "Apply black code formatter (#2891)". **Every one is a repo-wide mechanical change — formatter runs and packaging migrations. There has been no functional commit to the OED module since 2021** — [GitHub API /repos/pyro-ppl/pyro/commits?path=pyro/contrib/oed](https://api.github.com/repos/pyro-ppl/pyro/commits?path=pyro/contrib/oed)
- The module contains just five entries: `__init__.py`, `eig.py`, `glmm/`, `search.py`, `util.py` — [GitHub API contents, pyro/contrib/oed](https://api.github.com/repos/pyro-ppl/pyro/contents/pyro/contrib/oed)
- Pyro's adaptive-design tutorial gives the sequential loop: write a Bayesian model with a design parameter, pick the design, collect data, fit with SVI, and use the learned model as the next round's prior — [pyro.ai/examples/working_memory.html](https://pyro.ai/examples/working_memory.html)
- The review of record: Rainforth, Foster, Ivanova & Bickford Smith, **"Modern Bayesian Experimental Design", Statistical Science 39(1), February 2024, pp. 100–114, DOI 10.1214/23-STS915**. It states that BOED's deployment "often poses substantial computational challenges that can undermine its practical use" — [Project Euclid](https://projecteuclid.org/journals/statistical-science/volume-39/issue-1/Modern-Bayesian-Experimental-Design/10.1214/23-STS915.full); [arXiv 2302.14545](https://arxiv.org/abs/2302.14545v1); [Oxford ORA, CC BY accepted manuscript](https://ora.ox.ac.uk/objects/uuid:83680674-e825-4818-9375-77246727482a)
- **iDAD** has an official repo at [github.com/desi-ivanova/idad](https://github.com/desi-ivanova/idad) for the NeurIPS 2021 implicit Deep Adaptive Design paper. Its README reports testing on Linux and macOS with **Python 3.8**, recommends a GPU for training, and **pins torch 1.8.0 with CUDA 11.1** — [github.com/desi-ivanova/idad](https://github.com/desi-ivanova/idad)
- **Verified via GitHub API 2026-10-26: `desi-ivanova/idad`, `pushed_at` 2021-12-30T18:40:36Z, 26 stars, not archived.** It has received no commits in five years; the torch 1.8.0 / CUDA 11.1 pin is therefore the only configuration it was ever tested in — [GitHub API /repos/desi-ivanova/idad](https://api.github.com/repos/desi-ivanova/idad)
- **Verified via GitHub + PyPI APIs 2026-10-26: Pyro — `pyro-ppl/pyro` `pushed_at` 2026-10-05T18:42:13Z, 9073 stars, not archived; PyPI `pyro-ppl` 1.9.2 released 2026-10-03** — [GitHub API /repos/pyro-ppl/pyro](https://api.github.com/repos/pyro-ppl/pyro); [PyPI pyro-ppl](https://pypi.org/project/pyro-ppl/)
- **BoTorch has moved: `pytorch/botorch` now redirects to [github.com/meta-pytorch/botorch](https://github.com/meta-pytorch/botorch), `pushed_at` 2026-10-16T15:49:43Z, 3635 stars, not archived; PyPI `botorch` 0.18.1 released 2026-06-08** (GitHub + PyPI APIs, 2026-10-26) — [GitHub API /repos/meta-pytorch/botorch](https://api.github.com/repos/meta-pytorch/botorch); [PyPI botorch](https://pypi.org/project/botorch/)
- DAD (Foster et al., ICML 2021) learns an amortized design network up front so adaptive experiments run quickly at deployment; iDAD extends this to implicit models — [NeurIPS 2021 paper](https://proceedings.nips.cc/paper_files/paper/2021/file/d811406316b669ad3d370d78b51b1d2e-Paper.pdf)
- **DAD's stated limits: it requires a continuous design space and a differentiable likelihood**, and exploration is an open issue; the proposed remedy is reinforcement learning framed as a hidden-parameter MDP (i.e. the RL-BOED line) — [ICML 2022 slides](https://icml.cc/media/icml-2022/Slides/17108.pdf)
- `sbi` (Macke group): repository [github.com/sbi-dev/sbi](https://github.com/sbi-dev/sbi), **Apache-2.0**, 71 open issues — [ecosyste.ms project record](https://summary.ecosyste.ms/projects/356235)
- **Verified via GitHub + PyPI APIs 2026-10-26: `sbi-dev/sbi` `pushed_at` 2026-10-23T23:51:24Z (three days before query), 877 stars, not archived; PyPI `sbi` 0.27.0 released 2026-08-04.** This is the most actively developed package in this section after Pyro — [GitHub API /repos/sbi-dev/sbi](https://api.github.com/repos/sbi-dev/sbi); [PyPI sbi](https://pypi.org/project/sbi/)
- The current `sbi` paper is "sbi reloaded: a toolkit for simulation-based inference workflows", describing community-driven development and diagnostics such as simulation-based calibration — [paper review summary](https://www.themoonlight.io/tw/review/sbi-reloaded-a-toolkit-for-simulation-based-inference-workflows) *(secondary summary, not the paper itself)*

### Inferences

- DAD's requirement of a **continuous** design space disqualifies it for the user's problem outright: choosing
  *which* measurements to take is a discrete combinatorial choice, not a continuous design parameter.
- `pyro.contrib.oed`'s EIG is an information-gain objective about *parameters*. The user's quantity of interest
  is a classification decision among 12–24 classes. Those differ, and the difference is exactly the one
  Krause & Guestrin's JAIR 2009 result turns on (information gain vs decision-theoretic value of information).
  Maximising EIG is not maximising class separability.
- `sbi` is the wrong tool category: it does simulation-based *inference* when the likelihood is intractable. The
  user's likelihood is a multivariate Gaussian with known means. There is nothing to simulate.
- The whole BOED stack exists to handle intractable posteriors and sequential adaptive designs. The user has a
  tractable posterior and (as stated) a one-shot design choice. Recommending BOED here would be importing
  Monte Carlo error into a closed-form problem.
- The frozen-module finding generalises into a method point worth stating in the report: **a repository-level
  `pushed_at` is not evidence that the subpackage you intend to import is maintained.** Pyro looks active at
  the top level and its OED module has had no functional change in five years. Any staleness claim about a
  submodule of a large library should be made with a path-filtered commit query, not the repo date.

### Gaps

- **BoTorch**: maintenance state now verified (above), but **its functionality was not investigated.** I cannot
  report whether its active-learning / information-theoretic acquisition functions cover discrete
  candidate-set design.
- **RL-BOED**: no public repository found. The method is described in ICML 2022 slides; whether maintained code
  exists is unresolved.
- `pyro.contrib.oed`'s module-level state is now **verified and it is worse than the repository-level date
  suggests** (see the finding above). What remains unknown is whether the module still *runs* against current
  Pyro — a frozen module in an evolving library is a plausible breakage, but I did not install and execute it.
- The docs page I reached for `contrib.oed` was a third-party mirror (`pyro4ci.readthedocs.io`), not
  docs.pyro.ai, so the API listing above should be confirmed against the official docs.

---

## Q6. Class separability and Bayes error — what software computes Bhattacharyya, Chernoff, JM, Mahalanobis?

### Takeaway

**Correction to my own first pass: there IS a maintained Python package. `spectral` (spectralpython) ships
`bdist`, a Gaussian Bhattacharyya distance between two classes, with the mean and covariance terms returned
separately by `bdist_terms`.** It is MIT, PyPI 0.25 released 2026-07-25, last commit 2026-09-04, 688 stars. It
does **not** implement Jeffries–Matusita (verified by code search: 0 hits for "jeffries" and 0 for
"separability"), and JM is a monotone transform of Bhattacharyya so that is a two-line addition. R has
`spatialEco::spectral.separability` (JM by default, Bhattacharyya optional) and `varSel` (SFFS + JM). Chernoff
information at general s is implemented nowhere I found — that part really is scipy plus a dozen lines.

### Cited Findings

**The measures and their relationships**
- The Bayes error "is often intractable to compute", so closed-form bounds are used instead; those bounds introduce similarity/divergence measures such as the Bhattacharyya coefficient and the associated Bhattacharyya distance — [Nielsen, arXiv 1401.4788](https://arxiv.org/pdf/1401.4788) (published in Pattern Recognition Letters, 2014)
- The Bhattacharyya upper bound "can be tightened using Chernoff information", which rests on the best error exponent — [Nielsen, arXiv 1401.4788](https://arxiv.org/pdf/1401.4788)
- Hellman & Raviv give simple derivations of both the Bhattacharyya bound and the more general Chernoff bound for the two-class problem — [Hellman & Raviv, Stanford EE](https://www-ee.stanford.edu/~hellman/publications/07.pdf)
- The Jeffries–Matusita distance is a scaled (0–2) version of Bhattacharyya; "J-M distance is asymptotic to 2, where 2 suggest[s] complete separability" — [spatialEco spectral.separability docs](https://www.rdocumentation.org/packages/spatialEco/versions/2.0-3/topics/spectral.separability)
- Separability measures "account for both the inter- and the intraclass distance implicitly" — [varSel manual](https://micheledalponte.r-universe.dev/varSel/doc/manual.html)

**Closed form for two multivariate Gaussians**
- The Bhattacharyya distance between two Gaussians is one eighth of the squared Mahalanobis distance between the means **using the averaged covariance**, plus one half the log of the determinant of that average divided by the square root of the product of the two covariance determinants — [arXiv 2508.05066](https://arxiv.org/pdf/2508.05066); same structure in [arXiv 2502.00168](https://arxiv.org/pdf/2502.00168)
- The Bhattacharyya distance is the negative log of the Bhattacharyya coefficient — [arXiv 2502.00168](https://arxiv.org/pdf/2502.00168)
- **With equal covariances the log-determinant term vanishes, leaving only the Mahalanobis term** — [arXiv 2502.00168](https://arxiv.org/pdf/2502.00168) describes the same-covariance case as the Mahalanobis distance scaled by the separation of the means; [arXiv 2602.14371](https://arxiv.org/pdf/2602.14371) gives this case for circular complex Gaussians with a different factor
- **Normalisation conventions differ across papers.** One source writes the mean term with a factor of 1/2 and a leading factor of 2 on the log-determinant term — [arXiv 1412.7146](https://arxiv.org/pdf/1412.7146). A 1-D form with a 1/4 factor on both terms also appears — [MetricGate docs](https://metricgate.com/docs/bhattacharyya-distance/) *(calculator marketing page; secondary)*
- Hellinger distance is linked to Bhattacharyya by a simple transform and also has a Gaussian closed form — [arXiv 2502.00168](https://arxiv.org/pdf/2502.00168)
- Closed-form formulas for these (dis)similarities across the exponential family — [Nielsen, arXiv 2003.02469](https://arxiv.org/pdf/2003.02469)

**Multiclass**
- Berisha et al.'s pairwise bound sandwiches the multiclass Bayes error between weighted sums of two-class pairwise Bayes risks; **the pairwise bounds become loose when the number of classes is large**. Sekeh et al. propose a generalized Henze–Penrose measure to address that; the Chernoff bound is one of several two-class pairwise bounds cited, alongside Bhattacharyya and Henze–Penrose — [Sekeh et al., arXiv 1811.06419](https://arxiv.org/pdf/1811.06419)
- A multiclass MAP error bound summing over **ordered class pairs**, with an infimum over s ∈ [0,1] for each pair, built from per-site Chernoff coefficients that multiply across conditionally independent sites — stated for **discrete** message distributions, not Gaussian — [arXiv 2607.11023](https://arxiv.org/pdf/2607.11023)

**Software that actually exists**

*Python — `spectral` (spectralpython), the one real find here*
- **Verified via GitHub API 2026-10-26: `spectralpython/spectral`, `pushed_at` 2026-09-04T16:45:13Z, 688 stars, not archived; PyPI `spectral` 0.25 released 2026-07-25, MIT licence** — [GitHub API /repos/spectralpython/spectral](https://api.github.com/repos/spectralpython/spectral); [PyPI spectral](https://pypi.org/project/spectral/)
- `spectral/algorithms/algorithms.py` defines **`bdist(class1, class2)`** — docstring: "Calculates the Bhattacharyya distance between two classes." It is "aliased to `bDistance`", and its stated reference is **Richards, J.A. & Jia, X., *Remote Sensing Digital Image Analysis: An Introduction* (Springer: Berlin, 1999)** — [algorithms.py](https://github.com/spectralpython/spectral/blob/master/spectral/algorithms/algorithms.py)
- **The exact implementation, read from source on 2026-10-26** (`bdist_terms`, which `bdist` sums):
  ```python
  m = a.stats.mean - b.stats.mean
  avg_cov = (a.stats.cov + b.stats.cov) / 2
  lin_term  = (1 / 8.) * np.dot(np.transpose(m), np.dot(np.linalg.inv(avg_cov), m))
  quad_term = 0.5 * (log_det(avg_cov) - 0.5 * a.stats.log_det_cov - 0.5 * b.stats.log_det_cov)
  return (lin_term, float(quad_term))
  ```
  — [algorithms.py, lines 1202-1224](https://github.com/spectralpython/spectral/blob/master/spectral/algorithms/algorithms.py)
- This is the **1/8 Mahalanobis + 1/2 log-determinant convention**, matching [arXiv 2508.05066](https://arxiv.org/pdf/2508.05066) and [arXiv 2502.00168](https://arxiv.org/pdf/2502.00168), and **not** the variant convention in [arXiv 1412.7146](https://arxiv.org/pdf/1412.7146)
- `spectral.algorithms` also exports `mean_cov`, `covariance`, `calc_stats`, `cov_avg`, `GaussianStats`, `linear_discriminant` and `create_training_classes` alongside `bdist` — i.e. the Gaussian class-statistics plumbing the user needs is already there — [algorithms/__init__.py](https://github.com/spectralpython/spectral/blob/master/spectral/algorithms/__init__.py)
- **Verified absent: a code search of the repository returned 0 hits for "jeffries" and 0 for "separability".** Jeffries–Matusita is not implemented; only Bhattacharyya (GitHub code search API, 2026-10-26)

*R*
- R `spatialEco::spectral.separability` "calculates spectral separability by class" and **returns JM by default, with Bhattacharyya as an option** — [RDocumentation](https://www.rdocumentation.org/packages/spatialEco/versions/2.0-3/topics/spectral.separability); [Quantargo NEWS](https://www.quantargo.com/help/r/latest/packages/spatialEco/NEWS/spectral.separability)
- R `varSel` provides "feature selection using Sequential Forward Floating feature Selection and Jeffries-Matusita distance" and "returns a suboptimal set of features to use for image classification" — [varSel manual](https://micheledalponte.r-universe.dev/varSel/doc/manual.html)

### Inferences

- `spectral.algorithms.bdist` is the single most directly usable piece of software in this entire inventory for
  the user's criterion. It is MIT, released three months ago, and `bdist_terms` returning the mean term and
  the covariance term **separately** is exactly what the user needs: under the equal-covariance assumption the
  quadratic term should be identically zero, so `bdist_terms` is a built-in assertion that the covariance
  assumption holds. If the quadratic term is non-zero, the equal-covariance simplification does not apply and
  the σ²-factors-out argument below fails. That is a free outside check.
- For the multiclass aggregation and the Chernoff bound at general s, "scipy plus a dozen lines" remains the
  right characterisation — and in the user's setting that is *better* than a package, not worse. With means
  fixed from published tables and covariance = σ²·(known structure), the per-pair
  Bhattacharyya distance under equal covariance collapses to (1/8)·Δμᵀ Σ⁻¹ Δμ, which is a single quadratic
  form. The one unknown scalar σ² then enters as a pure multiplicative factor on every pair simultaneously —
  meaning the *ranking* of measurement subsets by this criterion is independent of σ², and only the absolute
  error level depends on it. That is a strong structural simplification and should be checked numerically
  rather than assumed.
- The convention divergence in the Bhattacharyya formula is a concrete instance of the project's recurring
  failure mode: a finite, plausible number computed with the wrong factor. The sourced conventions differ by a
  factor of 4 on the mean term (1/8 vs 1/2) — enough to move a separability verdict without looking wrong.
  Any implementation should be checked against a two-class case with a known analytic Bayes error (e.g.
  equal-covariance, equal-prior Gaussians, where the exact Bayes error is Φ(−d/2) with d the Mahalanobis
  distance between means) rather than against internal consistency. `spectral`'s `bdist` is a second
  independent implementation to check a hand-rolled one against, and it pins the convention to Richards & Jia,
  which is the convention the remote-sensing JM thresholds were calibrated against.
- `varSel` is the closest existing software to the user's whole task: sequential feature selection driven by
  Jeffries–Matusita separability. It is R, and SFFS carries no approximation guarantee.

### Gaps

- The Python `spectral` library gap is now **closed and the earlier conclusion reversed** — `bdist` exists,
  sourced above. What `spectral` does *not* have: Jeffries–Matusita, Chernoff information at general s, any
  multiclass aggregation, and any subset-search driver. It computes one pairwise distance; the enumeration
  loop around it is the user's to write.
- `pyitlib` (PyPI 0.3.1, 2025-05-17, MIT) and `dit` (PyPI 2.3, 2026-09-26) are confirmed to exist and be
  reasonably current (PyPI JSON API, 2026-10-26), but **I did not inspect their APIs.** Both are
  entropy/mutual-information estimator libraries, which is a different computation from a Gaussian
  closed-form divergence, so I would not expect Gaussian Bhattacharyya/Chernoff in either.
- **The ITE toolbox could not be located.** GitHub repository searches for "ITE toolbox information theoretical
  estimators" returned no matching repository, and `szzoli/ITE` returned HTTP 404 (GitHub API, 2026-10-26). I
  cannot say whether it is dead, renamed, or hosted elsewhere (it was historically MATLAB code distributed from
  a personal page). The report should not assert it is available.
- Fukunaga's *Introduction to Statistical Pattern Recognition* could not be verified online. The Bhattacharyya
  and Chernoff bound treatments attributed to it in the assignment are standard, but I have sourced the formulas
  from arXiv papers instead and the report should cite those.
- No Gaussian-specific multiclass Chernoff refinement was found. The multiclass sources are either pairwise/
  union-bound style or stated for discrete distributions.

---

## Q7. Remote sensing band selection — mature tooling with separability criteria?

### Takeaway

The *criteria* are mature in remote sensing, but I found **no pip-installable Python package dedicated to band
*selection* with separability criteria**. The separability *metric* is available in maintained Python
(`spectral`'s `bdist`, Q6); the search driver around it is not. PySptools, often cited as the Python
hyperspectral toolbox, is **dead — no commit since 2018-02-10, no release since 2018-10-12** — and never
listed band selection anyway. What exists for selection in Python is per-paper research code.

### Cited Findings

- **PySptools is dead.** Verified 2026-10-26: `ctherien/pysptools` `pushed_at` **2018-02-10T19:58:24Z**, 55 stars, not archived; PyPI `pysptools` 0.15.0 released **2018-10-12**, Apache-2.0. Eight years without a commit — [GitHub API /repos/ctherien/pysptools](https://api.github.com/repos/ctherien/pysptools); [PyPI pysptools](https://pypi.org/project/pysptools/)
- PySptools is described as "a library of spectral algorithms" with "endmembers extraction, unmixing process, supervised classification, target detection, noise reduction, convex hull removal, features extraction at spectrum level and a scikit-learn bridge" — **band selection is not in that list** — [PyPI pysptools](https://pypi.org/project/pysptools)
- **The maintained hyperspectral package is `spectral` (spectralpython), not PySptools** — last commit 2026-09-04, PyPI 0.25 on 2026-07-25, MIT, 688 stars — and it is the one that carries the Bhattacharyya distance (see Q6) — [GitHub API /repos/spectralpython/spectral](https://api.github.com/repos/spectralpython/spectral)
- **HYPSO Toolbox** is a Python package for HYPSO satellite imagery; its spectral analysis tools "involve techniques related to band manipulation, spectral unmixing, and identification of specific materials" — aimed at HYPSO data — [NTNU Python for HYPSO](https://ntnu.edu/smallsat/python-for-hypso)
- **phyper** is "a toolbox [that] includes methods for reading hyperspectral images and provides an interface for basic machine learning algorithms like decomposition and clustering" — not band-selection focused — [PyPI phyper 1.1.3](https://pypi.org/project/phyper/1.1.3)
- Research code on GitHub rather than packages: **SRL-SOA** (self-representation learning with a sparse 1-D operational autoencoder), which also includes comparison methods PCA and SpaBS (Sparse Representation based Band Selection); **OPBS**, a third-party Python implementation of a geometry-based band selection approach; **hsi-cc**, correlation-based band selection — [repos.ecosyste.ms band-selection topic](https://repos.ecosyste.ms/topics/band-selection)
- Search strategy in the band-selection literature: "exhaustive search over all possible combinations of 1-4 bands or sequential forward selection" — [EARSeL 2006 paper](https://www.fc.up.pt/pessoas/andre.marcal/papers/EARSeL2006_265.pdf)
- A comparative study of band-selection metrics with search algorithms included Euclidean, Mahalanobis, divergence, Bhattacharyya, transformed divergence (TD) and JM distance — [SPIE JARS 11(4) 046010](https://astronomicaltelescopes.spiedigitallibrary.org/journals/journal-of-applied-remote-sensing/volume-11/issue-04/046010/Spectral-region-identification-versus-individual-channel-selection-in-supervised-dimensionality/10.1117/1.JRS.11.046010.full)
- An earlier IEEE paper covers a visual method for spectral band selection — [IEEE Xplore 1291391](https://ieeexplore.ieee.org/document/1291391/metrics)

### Inferences

- The most transferable thing from remote sensing is not a package but a *practice*: **exhaustive search over
  all combinations of 1–4 bands** is standard and accepted in that literature when the subset size is small.
  That is direct precedent for the user's Q9 plan, in a field that has been doing separability-driven subset
  selection for decades.
- The list of metrics in the SPIE comparison (Euclidean, Mahalanobis, divergence, Bhattacharyya, transformed
  divergence, JM) is a ready-made menu for a sensitivity analysis: compute the chosen subset under each
  criterion and see whether the answer moves. If several criteria agree, that is an outside check; if they
  disagree, the criterion choice is load-bearing and must be justified.

### Gaps

- I ran one search on Python band-selection packages. The absence of a dedicated package is weakly established;
  a PyPI/GitHub sweep would be needed to assert it confidently.
- ENVI / ERDAS commercial separability tooling (the industry-standard remote-sensing GUIs that compute JM and
  transformed divergence for training-class separability) was not investigated. These are the genuinely
  "industry-trusted" implementations in this field and are a notable omission.

---

## Q8. Information-theoretic feature selection with maintained code

### Takeaway

`scikit-feature` is **stalled — last commit 2024-07-11, GPL-2.0, not on PyPI under `skfeature`, still
documents Python 2.7** (its forks say so in their own READMEs). `mrmr-selection` last released **2023-06-30**,
which is **stale by the user's criterion**, though its repo saw commits to 2024-11-19. The maintained mRMR
implementations in 2026 are inside general-purpose feature-selection libraries — **`feature-engine` (BSD-3,
PyPI 1.9.4 on 2026-02-27, 2292 stars, last commit 2026-09-19) and `arfs` (MIT, last commit 2026-10-21)** —
rather than standalone mRMR packages. None of these carry any approximation guarantee.

### Cited Findings

- **scikit-feature** (`jundongl/scikit-feature`) contains around 40 popular feature selection algorithms, is **GPL-2.0**, and its install instructions "still list Python 2.7 alongside Python 3" — [github.com/jundongl/scikit-feature README](https://github.com/jundongl/scikit-feature/blob/master/README.md)
- A fork's README says "development seems to have stalled and various modules have be depreciated due to updates to scikit-learn", and that the fork author "will see if [it] should get reintegrated back into the original project if it ever gets revived again" — [github.com/8bit-pixies/scikit-feature README](https://github.com/8bit-pixies/scikit-feature/blob/master/README.md)
- **Verified via GitHub + PyPI APIs 2026-10-26: `jundongl/scikit-feature` `pushed_at` 2024-07-11T09:07:01Z, 1588 stars, not archived. The name `skfeature` does not resolve on PyPI — upstream was never published there.** A fork is published as `skfeature-gli`, version 1.1.2, released 2023-11-08 — [GitHub API /repos/jundongl/scikit-feature](https://api.github.com/repos/jundongl/scikit-feature); [PyPI skfeature-gli](https://pypi.org/project/skfeature-gli/)
- `8bit-pixies/scikit-feature` returns "Moved Permanently" from the GitHub API, i.e. the fork has been renamed or transferred (GitHub API, 2026-10-26)
- **mrmr-selection**: PyPI **latest version 0.2.8, released 2023-06-30T19:34:38**, **GPL-3.0**, author/maintainer Samuele Mazzanti. Provides `mrmr_classif` for categorical targets and `mrmr_regression` for numeric targets, across Pandas, Polars, Spark and Google BigQuery. The PyPI page does not name the specific relevance or redundancy measures — [PyPI mrmr-selection](https://pypi.org/project/mrmr-selection/)
- **Verified 2026-10-26: `smazzanti/mrmr` `pushed_at` 2024-11-19T11:17:46Z, 631 stars, not archived** — the repo is 17 months ahead of the published package — [GitHub API /repos/smazzanti/mrmr](https://api.github.com/repos/smazzanti/mrmr)
- **feature-engine's MRMR class** scores features by relevance minus redundancy, with relevance from **mutual information, an F-statistic, or random forest importance** — [feature-engine MRMR docs](https://feature-engine.trainindata.com/en/latest/api_doc/selection/MRMR.html)
- **Verified 2026-10-26: `feature-engine/feature_engine` `pushed_at` 2026-09-19T11:20:06Z, 2292 stars, not archived; PyPI `feature-engine` 1.9.4 released 2026-02-27, licence BSD-3.** This is the only genuinely production-shaped library in this section — permissive licence, real release cadence, large user base — [GitHub API /repos/feature-engine/feature_engine](https://api.github.com/repos/feature-engine/feature_engine); [PyPI feature-engine](https://pypi.org/project/feature-engine/)
- **arfs' MinRedundancyMaxRelevance** handles mixed categorical and numerical predictors without manual encoding, using correlation, correlation ratio, or Theil's U depending on dtype — [arfs mrmr source docs](https://arfs.readthedocs.io/en/latest/_modules/arfs/feature_selection/mrmr.html)
- **Verified 2026-10-26: `ThomasBury/arfs` `pushed_at` 2026-10-21T14:12:15Z (five days before query), 145 stars, not archived; PyPI `arfs` 3.0.0 released 2025-04-02, MIT** — [GitHub API /repos/ThomasBury/arfs](https://api.github.com/repos/ThomasBury/arfs); [PyPI arfs](https://pypi.org/project/arfs/)
- A third implementation, `MRMRSelector`, uses mutual information for relevance and Pearson correlation for redundancy — [endgame-ml docs](https://endgame-ml.readthedocs.io/en/latest/api/feature_selection.html)
- Das & Kempe's RIP results are what underwrite greedy *feature selection* with a guarantee — bounded submodularity ratio for RIP design matrices, giving (1 − e^{−γ}) — [JMLR v19/16-534](https://jmlr.org/papers/v19/16-534.html)

### Inferences

- mRMR, JMI and CMIM are heuristic criteria with no approximation guarantee attached to the greedy search that
  implements them. The only route to a guarantee for greedy feature selection in this family runs through Das &
  Kempe's submodularity ratio, and the published γ bounds there are for sparse linear regression under RIP, not
  for mutual-information criteria.
- For this user these are all the wrong tool shape: they are *empirical* selectors that estimate relevance and
  redundancy from a data matrix. The user has analytic distributions. Running a mutual-information estimator on
  samples drawn from a known Gaussian substitutes estimation error for a closed form.
- "Production-trusted" in this family means `sklearn.feature_selection.mutual_info_classif` and
  `feature-engine` — libraries with real release cadences — not the research packages.

### Gaps

- `pymrmr`: not investigated; maintenance status unknown.
- `BorutaPy` / `boruta_py`: not investigated. Boruta is a random-forest wrapper method and would not apply to
  analytic Gaussians anyway.
- `shap`-based selection: not investigated.
- `sklearn.feature_selection.mutual_info_classif`: not directly verified in this research round, though
  scikit-learn's maintenance is not in question.
- JMI and CMIM implementations: no maintained standalone package identified. `scikit-feature` is the usual
  source and it is stalled.
- `feature-engine`'s and `arfs`' maintenance is now verified by API (dates above); that gap is closed.
- **Licence caution worth flagging to the user:** `scikit-feature` is GPL-2.0 and `mrmr-selection` is GPL-3.0.
  For code that will ship alongside a published dataset and a possible 510(k) product, those are copyleft and
  materially different from the MIT/BSD licences of `spectral`, PySensors, PyOED, `apricot`, `submodlib` and
  `feature-engine`. This is a sourced licence fact (PyPI metadata, 2026-10-26), not legal advice.

---

## Q9. The decisive question — is exact enumeration with closed-form Bayes-error bounds standard practice?

### Takeaway

**Yes, with qualifications.** Exhaustive enumeration over small subsets with a closed-form separability
criterion is established practice in remote-sensing band selection, where "exhaustive search over all possible
combinations of 1–4 bands" is a documented method. For Gaussians the per-pair Bhattacharyya and Chernoff
bounds are closed-form, so no simulation is needed. The pitfalls are real and sourced: the multiclass
pairwise/union bound **becomes loose as the number of classes grows** — which bites directly at 12–24 classes —
the Bhattacharyya bound is strictly looser than the Chernoff bound, and the clean equal-covariance collapse to
a Mahalanobis term requires covariance equality across classes.

### Cited Findings

- Exhaustive enumeration is exact; greedy's (1 − 1/e) "approximation guarantee is optimal for any algorithm that uses polynomially-many value queries", i.e. greedy is only needed when enumeration is infeasible — [UW lecture notes](https://homes.cs.washington.edu/~marcotcr/blog/greedy-submodular)
- Maximizing a generic set function "becomes computationally infeasible as V grows" — the motivation for greedy is ground-set size, not principle — [submodlib paper, arXiv 2202.10680](https://arxiv.org/pdf/2202.10680)
- When the cardinality limit is constant, "no algorithm making a sub-linear number of function evaluations can guarantee any constant approximation ratio" — [arXiv 2405.13994](https://arxiv.org/pdf/2405.13994)
- Remote-sensing precedent for enumeration: band selection by "exhaustive search over all possible combinations of 1-4 bands or sequential forward selection" — [EARSeL 2006](https://www.fc.up.pt/pessoas/andre.marcal/papers/EARSeL2006_265.pdf)
- **Pitfall 1 — the union bound over class pairs.** Berisha et al.'s pairwise bound sandwiches the multiclass Bayes error between weighted sums of two-class pairwise Bayes risks, and "the pairwise bounds become loose when the number of classes is large" — [Sekeh et al., arXiv 1811.06419](https://arxiv.org/pdf/1811.06419)
- The proposed remedy for that looseness is a generalized Henze–Penrose measure — [Sekeh et al., arXiv 1811.06419](https://arxiv.org/pdf/1811.06419)
- The multiclass MAP error bound in a 2026 paper sums over **ordered** class pairs with a separate infimum over s ∈ [0,1] per pair — the explicit pairwise union-bound structure — [arXiv 2607.11023](https://arxiv.org/pdf/2607.11023)
- **Pitfall 2 — Chernoff vs Bhattacharyya tightness.** The Bhattacharyya upper bound "can be tightened using Chernoff information", which rests on the best error exponent, i.e. Bhattacharyya is the s = 1/2 special case and is strictly looser in general — [Nielsen, arXiv 1401.4788](https://arxiv.org/pdf/1401.4788)
- Both bounds have simple two-class derivations — [Hellman & Raviv](https://www-ee.stanford.edu/~hellman/publications/07.pdf)
- **Pitfall 3 — equal covariance.** The Gaussian Bhattacharyya distance has two terms: the Mahalanobis mean term using the *averaged* covariance, plus a log-determinant term. **With equal covariances the log-determinant term vanishes** and only the Mahalanobis term remains — [arXiv 2502.00168](https://arxiv.org/pdf/2502.00168); [arXiv 2508.05066](https://arxiv.org/pdf/2508.05066)
- The Bayes error itself "is often intractable to compute", which is why closed-form *bounds* rather than the exact error are the standard target — [Nielsen, arXiv 1401.4788](https://arxiv.org/pdf/1401.4788)
- Closed-form (dis)similarity formulas extend across the whole exponential family, not just Gaussians — [Nielsen, arXiv 2003.02469](https://arxiv.org/pdf/2003.02469)

### Inferences

- The user's problem is almost certainly enumerable. With d candidate measurements and a subset size k,
  enumeration costs C(d,k) evaluations of a criterion that is a sum of C(C−1)/2 quadratic forms over C classes.
  At C = 24 that is 276 pairs per subset, each a single Δμᵀ Σ⁻¹ Δμ. Even d = 30, k = 8 (≈5.9 million subsets)
  is minutes of vectorised NumPy. Enumeration removes the submodularity question entirely and with it every
  guarantee caveat in Q2. **This is the recommendation that best serves the stated priority of minimising
  bias and error.**
- The decisive structural point: if covariance is equal across classes and equals σ²·Σ₀ with Σ₀ known, then
  every pairwise Bhattacharyya distance scales as 1/σ², so σ² is a monotone transformation applied uniformly
  to all pairs and all subsets. The *argmax subset* is then independent of the unknown scalar, and σ² only sets
  the absolute separability level — i.e. the answer to "which measurements" does not require knowing σ², while
  the answer to "are the classes separable at all" does. This is an inference from the sourced closed form, not
  a sourced claim, and it should be verified numerically before being relied on. Note the caveat: if covariance
  is *not* equal across classes, the log-determinant term reappears and σ² no longer factors out cleanly.
- The looseness of the pairwise bound at 12–24 classes is the main threat to the "are they separable at all"
  question. A union bound over 276 pairs can exceed 1 and become vacuous. The practical fix is to report the
  **minimum pairwise** separability (which identifies the confusable pair and is the binding constraint, e.g.
  L5 vs S1) alongside the union bound, and to treat the union bound as an upper bound on error that may be
  uninformative rather than as an estimate.
- There is a second outside check available that costs almost nothing: since the distributions are fully
  specified, the exact multiclass Bayes error can be obtained to arbitrary precision by Monte Carlo over the
  known Gaussians. That is not "simulation in place of a closed form" — it is a validation of the closed-form
  bounds, and it is the kind of check against something *outside* the computation that this project's history
  argues for. The bounds should bracket the Monte Carlo estimate; if they do not, the implementation is wrong.
- Named terminology: the practice does not have one settled name. In remote sensing it is "band selection by
  exhaustive search with a separability criterion"; in pattern recognition it is "feature selection by
  divergence/separability criteria" (Fukunaga's framing); in the design literature it is "exact discrete
  optimal design by complete enumeration". The report should probably give all three rather than invent a
  single label.

### Gaps

- I found **no source that directly compares exhaustive enumeration against greedy for small ground sets**, and
  none that validates enumeration as "standard practice" in so many words outside the remote-sensing band-
  selection context. The claim rests on the EARSeL/SPIE band-selection precedent plus the general observation
  that greedy exists because of ground-set size.
- **No Gaussian-specific multiclass Chernoff bound was found.** The sourced multiclass bounds are either
  pairwise sums of two-class risks (Berisha/Sekeh) or stated for discrete distributions (arXiv 2607.11023).
  Whether a tighter multiclass Gaussian refinement exists in the literature is unresolved.
- Whether equal covariance across classes is strictly *required* for a usable closed form: the sources show
  the formula simplifies under equality, not that it fails without it (the unequal-covariance form is also
  closed form, just with the log-determinant term). The assignment's phrasing of this as a requirement is not
  supported by what I found — it is a simplification, not a requirement.
- The exact Bayes error for two equal-covariance equal-prior Gaussians (Φ(−d/2)) that I suggest as a unit test
  is standard textbook material but I did not source it; it should be cited to Fukunaga or Duda/Hart before
  appearing in the report as sourced.
- Whether published anatomical tables report covariance structure at all (as opposed to means and SDs) is
  outside my assigned scope but is a prerequisite for the whole plan.
