# Exact mathematical-programming solvers for cardinality-constrained best-subset selection and Gaussian class-separability feature choice (state as of 26 October 2026)

Scope note for the report writer: every version number and date below was checked live on
2026-10-26 against the vendor page, the package registry (PyPI JSON API / CRAN `crandb` / Julia), the
**authenticated GitHub REST API**, or Hans Mittelmann's benchmark pages. Where I could not verify a
claim I have put it in **Gaps** rather than guessing.

Staleness convention used throughout: I report **both** the latest release date and `pushed_at` (the
last commit to any branch), because for several packages here the two disagree sharply and the
disagreement is the decision-relevant fact — `coin-or/SHOT` and `mazumder-lab/l0bnb` both have live
repositories and release artefacts from 2021. Anything whose most recent *release* predates 2024 is
flagged **STALE** explicitly. `archived: true` would be decisive evidence a project is dead; **no
repository checked for this note is archived.**

---

## Q1. Which commercial solvers lead for mixed-integer quadratic and conic problems in 2026? Versions, licensing, benchmark standing

### Takeaway

The Mittelmann benchmarks are alive and were refreshed in the week of 20–25 October 2026, but
Gurobi, IBM CPLEX and FICO Xpress are **absent from all of them** (IBM and FICO demanded removal
in 2018; Gurobi withdrew in August 2024), so there is no independent 2026 ranking that includes
the three best-known commercial solvers. Among solvers that still participate, **COPT 9.0 is the
fastest on MILP, MISOCP, convex discrete QPLIB and sparse SDP**, and **SHOT 1.1 (driving Gurobi)
solves the most convex discrete MIQCPs**. No commercial solver on this list solves mixed-integer
SDP.

### Cited findings — benchmark infrastructure

- The benchmark index carries the banner "END OF A BENCHMARKING ERA … Through an action by Gurobi
  at the 2018 INFORMS Annual Meeting this has come to an end. IBM and FICO demanded that results
  for their solvers be removed … In August 2024 Gurobi decided to withdraw from the benchmarks as
  well and their results have been removed. On 12/24/2024 MindOpt followed suit." — [plato.asu.edu/bench.html](https://plato.asu.edu/bench.html)
- The site is actively maintained: current update stamps are MILP 10-25-2026, LPfeas 10-25-2026,
  LPopt 10-22-2026, MISOCP 10-23-2026, Convex Discrete QPLIB 10-24-2026, sparse SDP 10-22-2026,
  MINLP 2-26-2026, MPEC 7-19-2026. The site uses the **shifted geometric mean**, not performance
  profiles. — [plato.asu.edu/bench.html](https://plato.asu.edu/bench.html)
- There is **no MISDP benchmark on the site at all.** The semidefinite section lists only
  continuous SDP, infeasible SDP, large SOCP and MISOCP. — [plato.asu.edu/bench.html](https://plato.asu.edu/bench.html)
- Mittelmann's October 2025 INFORMS talk says the benchmarks are "at a turning point in the age of
  AI", with concerns about over-tuning, and that only benchmarks with undisclosed datasets (LP,
  MIPLIB) are less exposed. — [plato.asu.edu/talks/informs2025.pdf](https://plato.asu.edu/talks/informs2025.pdf)

### Cited findings — MILP benchmark (MIPLIB2017, 25 Oct 2026)

240 preprocessed MIPLIB2017 benchmark instances, AMD Ryzen 9 5900X (12 cores, 128 GB), 2-hour
limit, 12 threads. Scaled shifted geometric mean of runtime (1 = fastest) and instances solved:

| Solver | scaled SGM | solved / 240 |
|---|---|---|
| COPT 9.0.0 | **1** | **225** |
| Optverse 2.0.1 | 2.43 | 210 |
| HiGHS 1.15.1 (parallel) | 7.69 | 179 |
| XSMOO / Smoothie [FiberSCIP-cpx+HiGHS] | 7.28 | 174 |
| HiGHS 1.15.0 | 10.7 | 158 |
| SCIPCO/spx 11.0.0 (SCIP-conc, parallel, "forthcoming") | 8.21 | 160 |
| SCIP/spx 10.0.0 | 14.0 | 136 |

— [plato.asu.edu/ftp/milp.html](https://plato.asu.edu/ftp/milp.html)

### Cited findings — MISOCP benchmark (23 Oct 2026)

47 MISOCP instances from CBLIB2014 and Mittelmann's own set, Intel i7-11700K, 1-hour limit,
mipgap = 0:

| Solver | scaled SGM | solved / 47 |
|---|---|---|
| COPT 9.0.0 | **1** | **47** |
| MOSEK 11.2.3 | 5.89 | 37 |
| SCIP 10.0.0 + CPLEX | 6.80 | 39 |
| KNITRO 16.0.0 | 17.5 | 33 |

Individual times span 1 s to 3,321 s; 10 of 47 instances time out at 1 h for MOSEK and SCIP.
— [plato.asu.edu/ftp/misocp.html](https://plato.asu.edu/ftp/misocp.html)

### Cited findings — convex discrete (mixed-integer) QP/QCP benchmark (24 Oct 2026)

31 discrete convex QPLIB problems, AMD Ryzen 9 5900X, 2 h, mipgap 0, 12 threads (SCIP and
Minotaur 1 thread):

| Solver | scaled SGM | solved / 31 |
|---|---|---|
| COPT 9.0.0 | **1** | 24 |
| SHOT 1.1 (with Gurobi) | 1.14 | **25** |
| BARON 25.12.10 | 4.04 | 22 |
| MOSEK 11.2.3 | 7.83 | 20 |
| KNITRO 16.0.0 | 14.6 | 15 |
| SCIP 10.0.0 + CPLEX | 22.6 | 14 |
| Bonmin 1.8.7 (CPLEX + Ipopt) | 58.1 | 7 |
| MINOTAUR 0.4.0 | 68.1 | 8 |

— [plato.asu.edu/ftp/convex.html](https://plato.asu.edu/ftp/convex.html)

### Cited findings — versions and licences (checked 2026-10-26)

- **Gurobi 13.0**, released 18 November 2025, supported until November 2028. Python wheel
  `gurobipy` 13.0.3 uploaded 2026-08-25 ([PyPI, checked 2026-10-26](https://pypi.org/pypi/gurobipy/json)).
  MIP 8.2 % faster than 12.0 overall (models > 1 s) and 15.9 % faster on hard models (> 100 s);
  MIQCP 13.2 % / 25.8 %; LP 0.6 % / 3.9 %. Adds "a new Primal-Dual Hybrid Gradient (PDHG)
  implementation … allows users to solve some large-scale linear programming problems faster, with
  CPU and GPU support available", plus a nonlinear barrier method. — [Gurobi newsroom](https://www.gurobi.com/company/newsroom/gurobi-releases-version-13-0-with-improved-performance-and-new-solving-capabilities)
- **Gurobi does not do SDP.** Gurobi staff: the company "currently does not support any SDP
  algorithms or interfaces"; another reply: "Gurobi currently does not provide any SDP algorithms.
  Our development team is considering this feature, but we cannot make any promises." Staff
  repeatedly point users to the SCIP SDP plugin instead. — [support.gurobi.com](https://support.gurobi.com/hc/en-us/community/posts/25994175962769-Does-Gurobi-support-linear-semidefinite-programs)
- **Gurobi academic licence: free, and the relevant one for a medical centre.** "Gurobi's goal is to
  provide free academic licenses to qualified students, faculty, and staff at recognized
  degree-granting academic institutions", limited to research, teaching or coursework.
  *Named-User*: one user, one machine, no containers, 1 year, renewable, **no limit on the number
  of free academic named-user licences**, activation must happen on the academic network.
  *Academic WLS*: multiple machines and users, containers allowed, 90 days extendable, **two
  concurrent Gurobi sessions**, needs a live internet connection, registered to one person.
  — [Gurobi academic program](https://www.gurobi.com/academia/academic-program-and-licenses/);
  [As an academic user, how do I get a free Gurobi license?](https://support.gurobi.com/hc/en-us/articles/25770868793105)
- **MOSEK**: current release 11.2, with 12.0 in beta; `mosek` 11.2.6 on PyPI uploaded 2026-10-08
  ([PyPI, checked 2026-10-26](https://pypi.org/pypi/mosek/json)). *Personal Academic License*:
  **free, 365 days, renewable, "includes all features except the AMPL shell", not size
  restricted**, academic e-mail required, for faculty/students/staff at degree-granting
  institutions. *Institutional Academic License*: floating licence served to a network, 2 years,
  renewable. — [mosek.com/products/academic-licenses](https://www.mosek.com/products/academic-licenses/)
  (Note a version inconsistency across Mittelmann pages: MISOCP/SDP/QPLIB runs use MOSEK 11.2.3
  while LPfeas uses MOSEK 11.3.2.)
- **MOSEK does not solve MISDP.** A February 2026 arXiv paper states the MOSEK Fusion API does not
  support mixed-integer SDPs — [arXiv 2602.14136](https://arxiv.org/pdf/2602.14136); MOSEK's own
  error message is that the global optimizer "can only be applied to problems without semidefinite
  variables" — [MOSEK/CVX forum](https://ask.cvxr.com/t/error-using-mosek-solver-with-binary-constraints/3398).
- **IBM CPLEX**: the Python wheel `cplex` is at **22.2.0.1**, uploaded 2026-07-15
  ([PyPI, checked 2026-10-26](https://pypi.org/pypi/cplex/json)) — i.e. there is a 22.2 line
  newer than the 22.1.2 that academic download pages still mostly serve. Academic distribution is
  through the IBM Academic Initiative: "faculty members, research professionals at accredited
  institutions, and qualifying members of standards organizations" can join and get full versions
  of CPLEX at no charge. Community forum posts from 2025–2026 report users receiving only the
  1,000-variable Community Edition or hitting download errors; an IBM community staffer replied
  that the academic installation "should not be limited". — [IBM Decision Optimization community](https://community.ibm.com/community/user/discussion/cplex-academic-license);
  [M4OPT CPLEX install guide](https://m4opt.readthedocs.io/en/stable/_sources/install/cplex.rst.txt)
- **FICO Xpress**: the Python wheel `xpress` is at **9.9.1**, uploaded 2026-07-03
  ([PyPI, checked 2026-10-26](https://pypi.org/pypi/xpress/json)).
- **COPT (Cardinal Optimizer)**: Mittelmann runs **COPT 9.0.0** as of October 2026, but PyPI
  `coptpy` is at **8.0.7** (2026-09-20) ([PyPI, checked 2026-10-26](https://pypi.org/pypi/coptpy/json)) —
  flag this discrepancy; the 9.x binary may be distributed only from Cardinal Operations directly.
  COPT.jl documents "a free personal license" from the COPT application page, and without a licence
  "you can solve small models for non-commercial purpose"; after a COPT upgrade the licence files
  must be reapplied. — [COPT.jl docs](https://docs.juliahub.com/COPT/EUGW6/1.1.4);
  [JuMP COPT page](https://jump.dev/JuMP.jl/stable/packages/COPT/).
  COPT's documented mixed-integer classes are **MILP, MISOCP, MIQP, MIQCP**; SDP is supported in the
  continuous case (Barrier and ADMM); MISDP is **not** listed. — [COPT User Guide](https://guide.coap.online/copt/en-doc/intro.html);
  [GAMS COPT interface](https://gams.com/52/docs/S_COPT.html)
- **Hexaly (formerly LocalSolver)**: a vendor page lists "Version 15.0 last release: 2026-08-11",
  while spring-2026 conference pages promote 14.5 — conflicting, flag it. Hexaly 14.5 adds
  structure detection, "a new modular interior-point algorithm", and "a branch-and-reduce method
  with cut generation". Academic terms: "3-month licenses for free, renewable, to individual
  students" and "FREE annual unlimited academic licenses to educators and researchers"; "any
  commercial use of Trial, or Academic licenses is strictly prohibited"; academic licences come
  without support. Vendor pages disagree on whether educators get 3 months or a year.
  — [hexaly.com/download](https://www.hexaly.com/download); [hexaly.com/pricing](https://www.hexaly.com/pricing);
  [Hexaly blog/new release](https://www.hexaly.com/blog)
- Hexaly appears in Mittelmann's **combinatorial** benchmarks only (ATSP 10-16-2026, TSPLIB
  7-28-2026), not in MILP, MISOCP, QPLIB or SDP. — [plato.asu.edu/bench.html](https://plato.asu.edu/bench.html)

### Inferences

- For this user's problem the binding commercial question is not "who is fastest on MIPLIB" but
  "who has a free academic licence and a good Python API". Gurobi and MOSEK both give a genuinely
  unrestricted free academic licence with a one-line application; both are production-grade; both
  have first-class Python APIs. That makes them the default pair to try.
- COPT's clean sweep of the Mittelmann MILP, MISOCP and convex-discrete-QPLIB tables is striking,
  but note that COPT is one of the few vendors still *choosing* to participate, so the table is
  "best among participants", not "best available". The absence of Gurobi/CPLEX/Xpress means no
  honest 2026 head-to-head exists. Do not present COPT as "the fastest MIP solver in the world".
- Hexaly is a local-search/hybrid engine marketed on time-to-good-solution, not on certificates of
  optimality for conic models. It is the wrong tool when the requirement is *proven* optimality of
  a conic objective.

### Gaps

- FICO Xpress Community Edition size limits for the **solver** (the commonly quoted 5,000
  rows/columns figure) could not be verified; my search returned only the Xpress Insight 5
  Community Edition restrictions, which are a different product.
- No FICO Xpress or IBM CPLEX academic-licence page was retrieved directly, only the IBM Academic
  Initiative description and third-party install guides.
- Whether CPLEX 22.2 or Xpress 9.9 added any conic/semidefinite capability could not be verified —
  no release notes were retrieved.
- Current list prices for any commercial solver: not retrieved. All vendors quote on request.

---

## Q2. Credible open-source substitutes, and which ones actually handle MISDP

### Takeaway

For MILP the credible open-source choice is **HiGHS** (MIT, very actively maintained, 7.7×
Mittelmann-scaled behind COPT) or **SCIP 10.1** (Apache 2.0, broader: MINLP and MIQCP). For MISDP —
the rarest capability — only two open-source routes were **verified**: **SCIP-SDP 4.4.0** (branch
and bound with interior-point SDP relaxations, or an LP cutting-plane method with eigenvector cuts)
and **Pajarito.jl 0.8.3** (conic outer approximation; I confirmed `MOI.PositiveSemidefiniteConeTriangle`
in its v0.8.3 source). CBC, Couenne, Bonmin, Juniper and Alpine do **not** do MISDP.

### Cited findings — maintenance status, verified against the GitHub REST API on 2026-10-26

`pushed_at` is the last commit to any branch; `archived: true` would be decisive evidence of death.
**No repository in this table is archived.** Queried authenticated via
`GET https://api.github.com/repos/{owner}/{repo}` and `/releases/latest` on 2026-10-26.

| Package | Latest release | Last commit (`pushed_at`) | Stars | Verdict |
|---|---|---|---|---|
| ERGO-Code/HiGHS | v1.15.1, 2026-07-02 | **2026-10-25** | 1,899 | active |
| scipopt/scip | v10.1.0, 2026-09-18 | **2026-10-25** | 671 | active |
| scipopt/PySCIPOpt (Python API) | — | **2026-10-25** | 1,001 | active |
| scipopt/scip-sdp | SCIP-SDP 4.4.0, Nov 2025 | **2026-09-21** | 21 | active, niche |
| coin-or/Cbc | releases/2.10.13, 2026-03-11 | **2026-10-24** | 1,021 | active |
| coin-or/Clp | — | **2026-10-23** | 499 | active |
| coin-or/Couenne | no GitHub release | **2026-10-20** | 91 | maintained, unreleased |
| coin-or/Bonmin | no GitHub release | **2026-10-19** | 149 | maintained, unreleased |
| coin-or/SHOT | releases/1.1.0, **2021-10-20** | **2026-10-25** | 135 | **release STALE**, dev active |
| coin-or/Csdp (SDP backend) | — | **2022-08-12** | 66 | **STALE** (4 years) |
| cvxgrp/scs (conic backend) | — | **2026-10-19** | 638 | active |
| google/or-tools (PDLP, CP-SAT) | — | **2026-10-23** | 14,268 | active |
| jump-dev/Pajarito.jl | v0.8.3, 2026-07-08 | **2026-10-12** | 141 | active |
| jump-dev/Pavito.jl (NLP sibling) | — | **2025-04-11** | 61 | **going stale** (18 months) |
| jump-dev/Hypatia.jl | — | **2026-10-25** | 151 | active (continuous conic only) |
| lanl-ansi/Juniper.jl | v0.9.5, 2026-10-02 | **2026-10-02** | 188 | active |
| lanl-ansi/Alpine.jl | v0.5.8, 2026-02-12 | **2026-02-12** | 251 | active |
| ZIB-IOL/Boscia.jl | — | **2026-09-30** | 47 | active |
| ZIB-IOL/FrankWolfe.jl (Boscia dep.) | — | **2026-10-03** | 117 | active |
| ZIB-IOL/OptimalDesignWithBoscia | — | **2026-09-18** | 0 | active; paper code, 0 stars |
| COPT-Public/cuLoRADS (GPU SDP) | v1.1.0 | **2026-10-02** | 19 | active, research-grade |
| NVIDIA/cuopt | release published 2026-10-14 | **2026-10-24** | 1,075 | active |

(`ERGO-Code/highspy` does not exist as a separate repository — the `highspy` wheel is published from
inside `ERGO-Code/HiGHS`. `highspy` 1.15.1 was uploaded to PyPI 2026-07-02.)

- **SCIP-SDP 4.4.0** was released in November 2025 "for SCIP 10.0.0 and DSDP 5.8 or SDPA 7.4.4 or
  MOSEK 9 or higher". It solves MISDPs "through a nonlinear branch-and-bound method, which is the
  default, or through a linear-programming cutting-plane method"; the first uses interior-point SDP
  solvers for relaxations, the second generates eigenvector-based cuts. Input is an extended SDPA
  format or CBF. The previous release, 4.3.0, was February 2024 for SCIP 9.0.0.
  — [SCIP-SDP project page](https://www.opt.tu-darmstadt.de/scipsdp);
  [SCIP-SDP 4.4.0 docs](https://www.opt.tu-darmstadt.de/scipsdp/doc-4.4.0/html/)
- The SCIP-SDP framework paper (dual fixing, branching, primal heuristics) is Gally, Pfetsch and
  Ulbrich, "A Framework for Solving Mixed-Integer Semidefinite Programs" —
  [optimization-online.org](https://optimization-online.org/2016/04/5394/). Gally's thesis reports
  that "numerical results for multiple applications, in particular robust truss topology design,
  are presented, showing that SCIP-SDP is currently one of the fastest solvers for mixed-integer
  semidefinite programming" — [Gally, Computational Mixed-Integer Semidefinite Programming](https://buchnah.de/buch/9783965480261)
  (vendor listing of the published thesis).
- **Pajarito.jl handles MISDP (verified).** The pre-MathOptInterface README states plainly:
  "It currently accepts mixed-integer conic problems with second-order, rotated second-order,
  (primal) exponential, and positive semidefinite cones. MISOCP and MISDP are two established
  sub-classes of MICPs that Pajarito can solve." — [Pajarito README (master)](https://raw.githubusercontent.com/jump-dev/Pajarito.jl/master/README.md).
  The current v0.8.3 README no longer restates the cone list, but I confirmed directly in the
  v0.8.3 source that `src/Cones/Cones.jl` includes `positivesemidefiniteconetriangle.jl` and
  registers `MOI.PositiveSemidefiniteConeTriangle` —
  [v0.8.3 src/Cones/Cones.jl](https://raw.githubusercontent.com/jump-dev/Pajarito.jl/v0.8.3/src/Cones/Cones.jl).
  Pajarito needs two sub-solvers: an `oa_solver` (MILP, e.g. Gurobi/HiGHS) and a `conic_solver`
  (e.g. Hypatia, SCS, MOSEK, CSDP). Licence MPL 2.0.
  — [Pajarito v0.8.3 README](https://raw.githubusercontent.com/jump-dev/Pajarito.jl/v0.8.3/README.md)
- **GravitySDP** is a second MISDP code: C++ inside the Gravity modelling platform, sparse
  eigenvalue-based cutting planes, MILP subproblems solved with Gurobi, presented at AIChE 2024.
  — [AIChE 2024 proceedings](https://proceedings.aiche.org/conferences/aiche-annual-meeting/2024/proceeding/paper/251d-branch-and-cut-solver-mixed-integer-semidefinite-programming-new-sparse-cutting-planes)
- **Boscia.jl** solves convex *integer* problems by branch and bound with Frank-Wolfe node
  relaxations, keeping the original constraint polytope rather than an epigraph reformulation; it
  was applied specifically to optimal experiment design and compared against generic and
  specialised convex MI solvers. Code: github.com/ZIB-IOL/Boscia.jl and
  github.com/ZIB-IOL/OptimalDesignWithBoscia.
  — [Hendrych, Besançon & Pokutta, SEA 2024 / arXiv 2312.11200](https://arxiv.org/html/2312.11200v7);
  framework paper [arXiv 2208.11010 (Math. Prog. Computation)](https://arxiv.org/html/2312.11200v7)
- **SDP sub-solvers** available to SCIP-SDP/Pajarito, with Mittelmann timings on 75 continuous SDP
  problems (22 Oct 2026, AMD Ryzen 9 5900X): COPT 9.0.0 scaled 1 / 75 solved; MOSEK 11.2.3 3.61 /
  73; SDPT3-4.0 6.64 / 69; CSDP 6.2.0 6.73 / 70; SDPA 7.4.4 9.96 / 61; SeDuMi 1.3.5 37.3 / 62;
  **cuLoRADS 1.1.0 (GPU) 1.79 / 73 but with 29 accuracy warnings out of 75**.
  — [plato.asu.edu/ftp/sparse_sdp.html](https://plato.asu.edu/ftp/sparse_sdp.html)

### Inferences

- The practical open-source MISDP stack in 2026 is: **JuMP → Pajarito (oa_solver = HiGHS or Gurobi,
  conic_solver = Hypatia or SCS/CSDP)**, or **SCIP + SCIP-SDP + DSDP/SDPA/MOSEK**. Both require a
  build step; SCIP-SDP is a C plugin you compile, Pajarito is a `Pkg.add`. For a user who does not
  already write Julia, SCIP-SDP's CBF-file route is probably less work than learning JuMP, but
  Pajarito is the lower-friction path if any Julia is acceptable.
- SHOT's *release* tag is from 2021 while its repository was pushed yesterday. Mittelmann still
  benchmarks "Shot-1.1". That combination means the released artefact is stale even though the
  project is not; anyone depending on SHOT should build from source and say which commit.
- Bonmin's 7/31 on convex discrete QPLIB and Couenne's absence from the 2026 convex table are
  evidence that the COIN-OR MINLP codes are no longer competitive for this class. Treat them as
  reference implementations, not production choices.
- **Backend choice matters for staleness too.** If Pajarito is used for MISDP, its conic backend
  should be SCS (last commit 2026-10-19) or Hypatia (2026-10-25), not CSDP — `coin-or/Csdp` has had
  no commit since 2022-08-12, and Mittelmann's own SDP table has it at 6.73× COPT with 70/75 solved.
  Pavito.jl, Pajarito's NLP sibling, has had no commit since 2025-04-11 and should not be relied on.

### Gaps

- I could not verify whether HiGHS 1.15 has any mixed-integer *quadratic* capability. HiGHS appears
  only in the MILP and LP benchmarks on plato.asu.edu, and I did not retrieve the HiGHS feature
  matrix. Do not assert MIQP support for HiGHS.
- SCIP's licence (Apache 2.0 since SCIP 8) was not re-verified in this session.
- No independent benchmark of MISDP solvers exists (there is no MISDP table on plato.asu.edu), so
  no claim about SCIP-SDP vs Pajarito vs GravitySDP speed can be sourced.
- Whether COPT 9.0 added MISDP: not verified either way; the user guide's mixed-integer list omits
  it, which is suggestive but not a statement.

---

## Q3. GPU acceleration in 2026 — exactly what is accelerated

### Takeaway

GPU acceleration in 2026 is real and competitive **for LP relaxations and first-order LP/SDP
methods only**. Mittelmann now runs a separate GPU column in the LP-feasibility benchmark, and the
GPU codes are at parity with or ahead of the best CPU codes there. There is **no production
GPU branch-and-bound**: NVIDIA's own FAQ says cuOpt's MILP is still beta and that "full MIP
optimality remains in active development", and cuOpt's MILP design is GPU primal heuristics with
the *dual bound computed on the CPU*. For m ≤ 30 this is all irrelevant — the models are tiny.

### Cited findings

- **Mittelmann's LPfeas benchmark (25 Oct 2026)** now reports CPU and GPU groups side by side on 65
  problems (i7-11700K; GPU limit 30 min). Scaled shifted geometric means, "1" = fastest within each
  group, with instances solved:
  CPU — COPT 9.0.0 **1** / 65 solved; MOSEK 11.3.2 3.56 / 56; XOPT 0.0.8 5.77 / 59; HiGHS 1.15.0
  10.2 / 55; KNITRO 16.0.0 14.8 / 48; OR-Tools 9.10 PDLP 16.6 / 50.
  GPU — **COPTG 1 / 64**; HPR-LP-C 0.1.4 1.34 / 63; cuOpt 26.10 1.37 / 62; cuPDLPx 0.3.0 3.55 / 57.
  — [plato.asu.edu/ftp/lpfeas.html](https://plato.asu.edu/ftp/lpfeas.html)
- **Gurobi 13.0** adds "a new Primal-Dual Hybrid Gradient (PDHG) implementation … allows users to
  solve some large-scale linear programming problems faster, with CPU and GPU support available".
  The press page gives no GPU speed-up numbers and does not claim any GPU role in MIP.
  — [Gurobi newsroom](https://www.gurobi.com/company/newsroom/gurobi-releases-version-13-0-with-improved-performance-and-new-solving-capabilities)
- **NVIDIA cuOpt MILP architecture**: cuOpt "runs primal heuristics on the GPU and improves the dual
  bound on the CPU". A July 2026 NVIDIA FAQ states MILP is **still in beta**, that "full MIP
  optimality remains in active development", and that the focus is on quickly finding feasible
  solutions. — [NVIDIA cuOpt FAQ: MILP tools, GPU primal heuristics](https://perspectives.nvidia.com/cuopt/task/faq/milp-tools-gpu-primal-heuristics-fast-solutions/);
  [cuOpt user guide 26.02](https://docs.nvidia.com/cuopt/user-guide/26.02.00/introduction.html)
- cuOpt is open source and very active: `NVIDIA/cuopt`, 1,075 stars, last push 2026-10-24, latest
  release published 2026-10-14 (GitHub API, checked 2026-10-26). It can back AMPL, GAMS, GAMSPy,
  PuLP, JuMP, Pyomo and CVXPY, and deploys as a microservice via Docker or Kubernetes.
  — [NVIDIA cuOpt FAQ: integrating with commercial CPU solvers](https://perspectives.nvidia.com/cuopt/task/faq/integrate-nvidia-cuopt-commercial-cpu-solvers/)
- GAMS updated its cuOpt link for **cuOpt 26.04**, adding a `pdlp_precision` option plus new and
  updated MIP options. — [GAMS blog, Sep 2025](https://gams.com/blog/2025/09/gpu-accelerated-optimization-with-gams-and-nvidia-cuopt/)
- An independent community test (cuOpt 25.8 on a Tesla T4 vs SCIP and HiGHS, 300 s limit) found
  cuOpt "consistently returns Feasible very quickly, but it never output an 'Optimal' status".
  — [community benchmark post](https://ru.linkedin.com/in/semen-kosyachenko-7a110151) (single-author
  LinkedIn post; treat as anecdote, not evidence).
- A vendor-partner LP result (not MILP): cuOpt 26.06 on a B200 GPU solved a large supply-chain LP in
  about 57 s versus about 662 s for a commercial CPU solver. — [o9 Solutions](https://o9solutions.com/articles/gpu-accelerated-supply-chain-optimization-nvidia)
- **GPU SDP**: cuLoRADS 1.1.0 (COPT-Public) is in the sparse-SDP table at scaled 1.79 vs COPT's 1,
  solving 73/75 — but with accuracy warnings on 29 of 75 instances. Mittelmann also notes
  "(cu)HALLaR is not applicable to general SDP problems since it requires prior knowledge of a
  tracebound." — [plato.asu.edu/ftp/sparse_sdp.html](https://plato.asu.edu/ftp/sparse_sdp.html)

### Inferences

- The honest 2026 statement is: GPUs have arrived for **LP and SDP first-order methods**, and for
  **MIP heuristics**. Nothing in the record supports a claim that any solver proves MIP optimality on
  a GPU. A GPU is therefore worthless for a provably-optimal subset-selection run.
- The GPU SDP accuracy warnings matter for this user specifically: an MISDP branch-and-bound whose
  node relaxations are solved to loose accuracy can prune the optimum. That is exactly the
  "plausible but wrong number" failure mode this project keeps hitting. If MISDP is ever used,
  the relaxation solver should be an interior-point code (MOSEK, COPT, CSDP), not a first-order
  GPU code.

### Gaps

- No 2026 peer-reviewed cuPDLP / cuPDLP-C paper was retrieved; cuPDLPx 0.3.0's only appearance here
  is as a row in Mittelmann's table.
- Whether Gurobi's PDHG GPU path is usable inside the MIP's node LPs: not stated anywhere I found.
  Do not assume it is.

---

## Q4. Bertsimas-style MIO best-subset selection, and which packages implement it

### Takeaway

The exact-MIO line of work is mature and the *papers* are strong, but almost all of the
**reference implementations are stale**: `L0Learn` (last push Jan 2024, last CRAN release 2021),
`l0bnb` (PyPI 2021, repo 2020), `bestsubset` (2023), `SubsetSelection.jl` (2022, release 2019).
The one genuinely maintained best-subset package in 2026 is **abess** (0.4.11, CRAN Dec 2025, PyPI
Mar 2026) — but abess is a *splicing heuristic with probabilistic guarantees*, not a certificate of
optimality, and even it shows intermittent CRAN check failures in mid-2026. `MIPLearn` is not a
best-subset package at all.

### Cited findings — the papers

- **Bertsimas, King & Mazumder, "Best Subset Selection via a Modern Optimization Lens", Annals of
  Statistics 44(2), 2016.** Formulates best-k-of-p linear regression as a mixed-integer
  optimization; develops a discrete first-order method for warm starts. Claimed scale: "solves
  problems with n in the 1000s and p in the 100s to provable optimality in minutes", and finds
  near-optimal solutions for n in the 100s and p in the 1000s in minutes. The algorithm "provides a
  solution with a suboptimality guarantee even if terminated early", accommodates side constraints,
  and extends to least-absolute-deviation loss.
  — [arXiv 1507.03133](https://arxiv.org/pdf/1507.03133);
  [Project Euclid](https://projecteuclid.org/journals/annals-of-statistics/volume-44/issue-2/Best-subset-selection-via-a-modern-optimization-lens/10.1214/15-AOS1388.full)
- A later study "found that best subset did not consistently outperform the lasso and forward
  stepwise selection in prediction accuracy" (this is the Hastie–Tibshirani–Tibshirani *Statistical
  Science* comparison whose code is the `bestsubset` R package). — reported in the search summary of
  [arXiv 1507.03133](https://arxiv.org/pdf/1507.03133) material; primary paper not fetched (see Gaps).
- **Hazimeh, Mazumder & Saab, "Sparse Regression at Scale: Branch-and-Bound rooted in First-Order
  Optimization", arXiv 2004.06152, Mathematical Programming 2022.** Problem is least squares with
  combined ℓ0 and squared-ℓ2 penalties. "Exact solutions have been hard to get, since mixed integer
  programming (MIP) methods struggle at around p ≈ 10^4 features"; their framework "reaches about
  p ≈ 10^7 with speedups of at least 5000× over earlier exact methods". It does **not** use a
  commercial MIP solver — it is a custom nonlinear branch-and-bound whose node relaxations are
  solved by coordinate descent with warm starts, active sets and gradient screening, plus a way to
  get dual bounds from primal CD solutions. Released as the **L0BnB** toolkit. The v1 preprint said
  "over 3600×", the journal version "at least 5000×" — cite whichever version you quote.
  — [arXiv 2004.06152](https://arxiv.org/pdf/2004.06152); [PyPI l0bnb](https://pypi.org/project/l0bnb)
- **Bertsimas, Pauphilet & Van Parys, "Sparse Regression: Scalable algorithms and empirical
  performance", arXiv 1902.06547** (Statistical Science) is the cutting-plane / outer-approximation
  line; `SubsetSelection.jl` is described there as a Julia tool for sparse regression that
  "favors statistically relevant features over an L1-penalized approach, competing with glmnet's
  Lasso on computation time", and `SubsetSelectionCIO.jl` as "a Julia package that computes sparse
  L2-regularized estimators". — [arXiv 1902.06547](https://arxiv.org/pdf/1902.06547);
  [github.com/jeanpauphilet/SubsetSelectionCIO.jl](https://github.com/jeanpauphilet/SubsetSelectionCIO.jl)
- **abess**: the method is sequencing-and-splicing from Zhu, Wen, Zhu, Zhang & Wang, "A polynomial
  algorithm for best-subset selection problem", **PNAS, December 2020** — "under reasonable
  conditions … runs in polynomial time, recovers the true subset with high probability, and returns
  a globally optimal solution", with an information criterion to pick the sparsity level.
  — [PNAS via PMC7777147](https://pmc.ncbi.nlm.nih.gov/articles/PMC7777147).
  The software paper is **JMLR vol. 23, paper 21-1060** (arXiv 2110.09697): a C++ core with R and
  Python interfaces. — [arXiv 2110.09697](https://ar5iv.labs.arxiv.org/html/2110.09697)
- **Harman & Rosa** argue the MILP route (McCormick relaxation, requiring finite interval bounds on
  the covariance-matrix elements) is an improvement over the MISOCP route for A-, I-, G- and
  MV-optimality — relevant because the same reformulation trick applies to subset scores.
  — [arXiv 2305.17562](https://arxiv.org/html/2305.17562v2)

### Cited findings — maintenance, verified 2026-10-26

Release dates from the PyPI JSON API and the CRAN database (`crandb.r-pkg.org`); last-commit dates
(`pushed_at`) from the authenticated GitHub REST API. **No repository below is archived.**
Two corrections to common assumptions came out of this check and are flagged in bold.

| Package | Latest release | Last commit (`pushed_at`) | Stars | Verdict |
|---|---|---|---|---|
| abess (R, CRAN) | 0.4.11, published **2025-12-08** | — | — | maintained |
| abess (Python, PyPI) | 0.4.11, uploaded **2026-03-04** | abess-team/abess **2026-03-15** | 468 | maintained; slowing |
| L0Learn (R, CRAN) | **2.1.0, published 2023-03-07** (*not* 2.0.3/2021 — the 2021 tarball is the newest in the CRAN *archive*; 2.1.0 is the live version) | hazimehh/L0Learn **2024-01-22** | 108 | **STALE**: no release in 3½ yrs, no commit in 21 months |
| l0learn (Python, PyPI) | 0.4.3, uploaded **2024-01-22** | (same repo) | — | **STALE** |
| l0bnb (PyPI) | **1.0.0, 2021-04-20** | **mazumder-lab/l0bnb 2026-02-02** — the canonical repo is in the Mazumder Lab org, *not* the abandoned `hazimehh/l0bnb` (last commit 2020-09-17, 0 stars); `alisaab/l0bnb` on PyPI redirects there | 44 | **mixed: repo alive in 2026, PyPI release 5½ yrs old** |
| ryantibs/best-subset (R `bestsubset`) | no release | **2023-07-24** | 91 | **STALE** |
| jeanpauphilet/SubsetSelection.jl | **v0.1.1, 2019-06-15** | **2022-03-24** | 17 | **STALE** (4½ yrs) |
| jeanpauphilet/SubsetSelectionCIO.jl | no release | **2021-08-17** | 11 | **STALE** (5 yrs) |
| ANL-CEEESA/MIPLearn | v0.4.3, 2025-06-10 | **2026-07-21** | 197 | maintained, but *not* a best-subset package |

The Mazumder Lab org is where this line of work actually lives now: `l0bnb` 2026-02-02,
`GraphL0Learn` 2026-02-05, `ALPS` 2026-02-03, `3BASiL` 2026-04-15, `BnB-screening` 2025-01-20,
`admm-q` 2026-10-09 (GitHub org repo listing, sorted by push, queried 2026-10-26). So the *research
programme* is active even though the two packages the brief names by their old URLs are not.

(Sources: [PyPI abess](https://pypi.org/pypi/abess/json), [PyPI l0bnb](https://pypi.org/pypi/l0bnb/json),
[PyPI l0learn](https://pypi.org/pypi/l0learn/json), queried 2026-10-26;
[CRAN abess page](https://cloud.r-project.org/web/packages/abess/index.html);
[crandb L0Learn](https://crandb.r-pkg.org/L0Learn);
[CRAN L0Learn archive](https://cran.r-project.org/src/contrib/Archive/L0Learn/);
[conda-forge abess files](https://anaconda.org/channels/conda-forge/packages/abess/files);
GitHub REST API.)

- abess 0.4.11 covers linear, logistic, Poisson, Cox, Gamma, multi-response, multinomial and ordinal
  models, plus Ising-model reconstruction, sequential and robust PCA, group best-subset selection
  and sure independence screening. conda-forge builds for Linux/Windows/macOS were updated
  2026-03-05. — [CRAN abess](https://cloud.r-project.org/web/packages/abess/index.html);
  [conda-forge](https://anaconda.org/channels/conda-forge/packages/abess/files)
- An R-package health tracker shows abess passing with 13 OK checks on 2026-07-08, but **several
  snapshots in June and early July 2026 show a single ERROR** — intermittent check failures.
  — [r-observatory abess page](https://r-observatory.thecoatlessprofessor.com/packages/abess/)
- abess's own literature uses "globally optimal" and "with high probability", **not** "certifiably
  optimal". None of the retrieved abess sources claims a suboptimality certificate in the MIP sense.
  — [PNAS via PMC7777147](https://pmc.ncbi.nlm.nih.gov/articles/PMC7777147)

### Inferences

- The brief's list conflates three different things. (a) **Certificate-producing MIO**: Bertsimas–King–
  Mazumder via Gurobi/CPLEX, and L0BnB's custom B&B. (b) **Fast heuristics with statistical
  guarantees but no certificate**: abess, L0Learn's coordinate-descent/local-combinatorial search,
  glmnet's L1. (c) **ML-for-MIP tooling**: MIPLearn, which learns warm starts and cuts for MIP
  solvers and has nothing to do with best subset. Mixing (a) and (b) is exactly the kind of
  substitution that produces a plausible-but-wrong answer.
- Every *packaged* implementation in category (a) is stale as a release artefact. `l0bnb` is the one
  worth a second look: its repository is live (mazumder-lab, Feb 2026) even though `pip install
  l0bnb` still gets you the April 2021 wheel — so install from git, not PyPI, and record the commit.
  Otherwise, if the user wants a certificate they will have to write the model themselves against a
  live solver (Gurobi/MOSEK/COPT via CVXPY, Pyomo or JuMP) rather than install a package. For
  m ≤ 30 that is a dozen lines.
- "Stale package, live research group" is the pattern across this whole literature. Treat the Mazumder
  Lab repository list as the index of what is current, and treat anything installed from PyPI/CRAN in
  this area as pinned 2021–2024 code. For reproducibility that is arguably a feature; for getting the
  latest method it is not.
- The claimed scales (p ≈ 10^3 to 10^7) are two to five orders of magnitude above m = 30. None of
  this machinery is needed at the user's size; it exists to make p = 10^5 tractable.

### Gaps

- I did not fetch the Hastie–Tibshirani–Tibshirani *Statistical Science* "Best subset, forward
  stepwise, or lasso?" paper directly, only a secondary characterisation of its conclusion. Verify
  before quoting it.
- No 2024–2026 survey of mixed-integer conic optimization was located.
- I could not find any 2025–2026 follow-up paper in the Bertsimas best-subset line; absence of
  search hits is weak evidence, so do not state that the line has stopped.
- Resolved, no longer a gap: `l0bnb` lives at `mazumder-lab/l0bnb` (last commit 2026-02-02, 44
  stars, not archived). `alisaab/l0bnb` — the URL on PyPI — redirects there; `hazimehh/l0bnb` (0
  stars, 2020) is a dead copy.
- What changed between l0bnb 1.0.0 (PyPI, 2021) and the current `mazumder-lab/l0bnb` HEAD was not
  checked; there is no CHANGELOG I retrieved.
- Whether `mazumder-lab/GraphL0Learn` (last commit 2026-02-05) supersedes `L0Learn` for ordinary
  (non-graph) best-subset problems: not verified. It is the most recently touched L0Learn-adjacent
  repository and worth one look before concluding L0Learn is dead.

---

## Q5. Can "maximize the minimum pairwise Mahalanobis distance between class means over subsets of coordinates" be posed exactly?

### Takeaway

Yes — and importantly, **it does not need a semidefinite program.** The literature confirms that
A-optimality-type criteria are second-order-cone representable while E-optimality genuinely needs
SDP, and that exact (integer) optimal design has been written as both MISOCP and MISDP with named
solvers. For this specific max-min Mahalanobis objective there is a standard variational
reformulation that lands in **convex MIQCP / MISOCP** territory, i.e. in Gurobi / MOSEK / COPT /
CPLEX / Xpress / SCIP's native class. I found **no published paper** that poses exactly this
objective as a mixed-integer conic program.

### Cited findings

- **A-, A_K-, G- and I-optimality are second-order-cone representable**, so exact optimal designs can
  be computed by branch-and-cut conic solvers; Sagnol & Harman, "Computing exact D-optimal designs
  by mixed integer second-order cone programming", *Annals of Statistics* 43(5), 2015. Their
  bibliography cites MOSEK. — [Project Euclid / AoS 43(5)](https://projecteuclid.org/journals/annals-of-statistics/volume-43/issue-5/Computing-exact-D-optimal-designs-by-mixed-integer-second-order/10.1214/15-AOS1339.pdf);
  [ZIB record](https://opus4.kobv.de/opus4-zib/frontdoor/index/index/year/2016/docId/5955)
- **Harman & Rosa** give a MILP alternative for A-, I-, G- and MV-optimality using McCormick
  relaxation, which "depends on finite interval bounds for the elements of the covariance matrix",
  and present it as an improvement over the MISOCP approach.
  — [arXiv 2305.17562](https://arxiv.org/html/2305.17562v2)
- **E-optimality as an SDP**: Ye, Zhou & Zhou (2015) "show in detail how to formulate A-optimal and
  E-optimal design problems as SDP problems and solve them by SeDuMi" — but for *approximate*
  designs on discrete design spaces, i.e. no integer variables. A companion UVic thesis uses SeDuMi
  and CVX. — [Computing A-optimal and E-optimal designs for regression models via semidefinite programming (UVic)](https://dspace.library.uvic.ca/items/3e0c502d-ef9d-4e53-9eb5-11314cf324e0)
- **Exact (integer) designs as MISDP**: Duarte (2023) "proposes mixed-integer semidefinite
  programming formulations to find exact D-, A- and I-optimal designs for linear models, and locally
  optimal designs for nonlinear models when the design domain is a finite set of points".
  — [Exact Optimal Designs of Experiments for Factorial Models via Mixed-Integer Semidefinite Programming](https://estudogeral.sib.uc.pt/bitstream/10316/113975/1/Exact-Optimal-Designs-of-Experiments-for-Factorial-Models-via-MixedInteger-Semidefinite-ProgrammingMathematics.pdf)
- **Sensor selection is formally an MISDP.** "In [6], it was shown that the sensor selection problem
  for static systems (or dynamic systems without process noise) over finite time horizons is a mixed
  integer semidefinite programming problem (MISDP). The same classification was subsequently made
  for dynamic systems with process noise in [7]." — [Taha, Gatsis, Summers & Nugroho (UT Dallas preprint)](https://personal.utdallas.edu/~tyler.summers/papers/TahaGatsisSummersNugroho2018.pdf)
- **Exact sensor selection by outer approximation**: an *Optimization Letters* (2013)
  information-maximizing MISDP is solved by "an outer-approximation algorithm … that obtains the
  global optimal solution by solving a sequence of mixed-integer linear programs for which reliable
  solvers are available", and "compares favorably with branch-and-bound methods that use nonlinear
  programming relaxations". — [KAIST record for "An outer-approximation approach for information-maximizing sensor selection"](https://koasas.kaist.ac.kr/handle/10203/255033?mode=full)
- **Generalized Benders Decomposition** cuts the number of SDP solves, since branch-and-bound must
  solve an SDP at every node: "A simple reformulation of the MICP and subsequent application [of]
  the Generalized Benders Decomposition (GBD) will result in massive reductions in computational
  effort." — [AIChE 2014, Globally Optimal Sensor Network Design Revisited](https://www.aiche.org/conferences/aiche-annual-meeting/2014/proceeding/paper/569al-globally-optimal-sensor-network-design-revisited-application-generalized-bender-decomposition-1)
- **Scale precedent**: a unified mixed-integer formulation for Kalman-filter sensor scheduling and
  selection reports optimal solutions for systems with **30 to 50 states in seconds**.
  — [TU Delft record / ar5iv 2304.02692](https://ar5iv.labs.arxiv.org/html/2304.02692)
- **Mahalanobis class separability as a feature-subset criterion** is classical but has been attacked
  with sequential search, not exact optimization: Flusser & Suk define it as "the squared distance
  between class means, weighted by the inverse of the averaged covariance matrix" and use an ordered
  sequential search, noting the separability gain flattens and then features "become too
  noise-sensitive". — [Flusser & Suk, Kybernetika 34(4), 1998](https://www.kybernetika.cz/content/1998/4/411/paper.pdf)
- Mahalanobis is the right distance when classes share a covariance matrix; Bhattacharyya when they
  do not. — [Surrey GAMA feature-selection docs](https://ph-vssp-www.eps.surrey.ac.uk/gama/doc/html/feature.html)
- Scoring features one at a time ignores inter-feature correlation; subset methods account for it.
  — [RIT pattern-recognition lecture notes](https://cs.rit.edu/~rlaz/prec2010/slides/FeatureSelection(Part2).pdf)

### Inferences (my own derivation — label clearly as such, it is not from a source)

- The obstacle is that the subset score is `d²_S = Δμ_Sᵀ (Σ_SS)⁻¹ Δμ_S`, and a *submatrix inverse*
  is not a linear or conic function of the 0/1 selection vector z. Zeroing out unselected rows and
  columns makes Σ_SS singular, so the inverse cannot simply be masked.
- The standard fix is the variational identity `Δμ_Sᵀ (Σ_SS)⁻¹ Δμ_S = max_w { 2 wᵀΔμ − wᵀΣw }`
  subject to `w_i = 0` for every i ∉ S (the maximizer is w* = Σ_SS⁻¹ Δμ_S). Because the outer
  problem is also a maximization, the two maxima compose and the whole thing is exactly
  representable:

      maximize   t
      s.t.       t + w_pᵀ Σ w_p  ≤  2 w_pᵀ Δμ_p      for every class pair p
                 −M z_i ≤ w_{p,i} ≤ M z_i            for every p, i
                 Σ_i z_i = k,   z ∈ {0,1}^m

  Each pair constraint is a convex quadratic constraint (Σ ⪰ 0), hence rotated-second-order-cone
  representable. So the max-min Mahalanobis subset problem is a **convex MIQCP / MISOCP with m
  binaries and |pairs| × m continuous variables** — with 6 classes that is 15 w-blocks, so about
  15 × 30 = 450 continuous variables and 30 binaries at m = 30. **No SDP is required**, and
  therefore MISDP is *not* actually the binding capability for this objective. That matters: it
  moves the problem from the rarest solver class into the one every commercial solver handles
  natively and the one COPT solves 47/47 of in Mittelmann's table.
- The weakness of that formulation is the big-M on w. Loose M gives a weak relaxation and a slow
  branch-and-bound; perspective/indicator reformulations are the standard tightening, and Gurobi,
  CPLEX, Xpress, MOSEK and SCIP all support indicator constraints natively so the big-M can often be
  avoided entirely.
- If the user instead wants E-optimality of a subset-restricted information matrix (minimize the
  largest eigenvalue of the inverse), that genuinely does need MISDP, and then the only verified
  routes are SCIP-SDP and Pajarito. A-optimality (trace of inverse) stays in MISOCP per
  Sagnol & Harman.

### Gaps

- **No published paper poses "maximize the minimum pairwise Mahalanobis distance between class means
  over subsets of coordinates" as a mixed-integer conic program.** I searched for it from the
  feature-selection side, the class-separability side and the optimal-design side and found only
  sequential-search treatments of the objective and conic treatments of adjacent objectives. If the
  user wants a citation for the exact formulation, there may not be one; the reformulation above is
  routine but appears not to have been written down for this objective.
- Duarte (2023) may or may not include E-optimality; the snippet lists D-, A- and I- only.
- No source names a solver used for an *E-optimal* MISDP with computational results. Gally's thesis
  reports SCIP-SDP results on truss topology design, not design of experiments.
- Searches for "cardinality-constrained discriminant analysis" were not run (budget); that is the
  most likely place a published exact formulation would live.

---

## Q6. Modelling layers — which front end to use to try several solvers without rewriting

### Takeaway

If MISDP is ever needed, **JuMP (Julia) is the only front end verified to reach an MISDP solver**
(Pajarito, SCIP-SDP). If the problem stays in MILP / MIQP / MIQCP / MISOCP — which, per Q5, it
should — **CVXPY is the right Python front end**: it is the most actively maintained of the layers
checked, and it already talks to Gurobi, MOSEK, CPLEX, Xpress, SCIP, CBC, HiGHS/PDLP and COPT
behind one model. Pyomo is the alternative if the model is better expressed algebraically than as
disciplined convex expressions.

### Cited findings — maintenance and versions, checked 2026-10-26

| Layer | Latest release | Last push | Stars | Classes reached |
|---|---|---|---|---|
| CVXPY | **1.9.3, 2026-09-19** | 2026-10-24 | 6,376 | LP/QP/SOCP/SDP continuous; MILP/MIQP/MISOCP via backends |
| Pyomo | 6.10.1, 2026-06-04 | 2026-10-23 | 2,552 | general AML, any LP/MILP/MIQCP/NLP/MINLP solver |
| JuMP.jl | v1.32.1 | **2026-10-26** | 2,486 | first-class conic incl. PSD cone; MISDP via Pajarito |
| PuLP | **4.2.0, 2026-10-22** | 2026-10-22 | 2,495 | LP/MILP only |
| python-mip | v1.17.1 | 2026-09-25 | 605 | MILP (CBC, Gurobi) |
| linopy | **0.10.1, 2026-10-21** | 2026-10-26 | 262 | LP/MILP, xarray-based |
| gurobipy | 13.0.3, 2026-08-25 | — | — | Gurobi only |

(Sources: authenticated GitHub REST API `/repos/{owner}/{repo}` — `pushed_at` is the last commit to
any branch — and the PyPI JSON API, both queried 2026-10-26. **None of these repositories is
archived.** JuMP's v1.32.1 tag carries no GitHub release object, hence no release date; its last
commit is the most recent of any package in this note. Every layer here is actively maintained —
staleness is not the discriminator among front ends, capability is.)

- CVXPY installs solver backends as extras:
  `pip install "cvxpy[CBC,CVXOPT,GLOP,GLPK,GUROBI,MOSEK,PDLP,SCIP,XPRESS]"`; SCIP is reached through
  `pyscipopt`. A documented caveat: the SCIP interface "does not reliably recover dual variables for
  constraints". — [CVXPY install docs](https://cvxpy.readthedocs.io/en/functions-table/install/index.html)
- **No modelling layer gets you MISDP in Python.** A CVX (MATLAB) forum thread notes that CVX
  "supports mixed-integer SDPs, but the underlying solvers do not", so MISDP models are not solvable
  through it. — [ask.cvxr.com](https://ask.cvxr.com/t/mixed-integer-sdps-which-are-not-mixed-integer-socps/477)
  Nothing I found says CVXPY has an MISDP backend.
- NVIDIA cuOpt can back "AMPL, GAMS, GAMSPy, PuLP, JuMP, Pyomo and CVXPY".
  — [NVIDIA cuOpt FAQ](https://perspectives.nvidia.com/cuopt/task/faq/integrate-nvidia-cuopt-commercial-cpu-solvers/)
- GAMS ships a maintained cuOpt link (updated for cuOpt 26.04) and documents a COPT interface
  (SOS supported; no semicontinuous or semi-integer variables).
  — [GAMS blog](https://gams.com/blog/2025/09/gpu-accelerated-optimization-with-gams-and-nvidia-cuopt/);
  [GAMS COPT docs](https://gams.com/52/docs/S_COPT.html)
- Pajarito is driven from JuMP by setting `oa_solver` (a MILP solver) and `conic_solver`.
  — [Pajarito v0.8.3 README](https://raw.githubusercontent.com/jump-dev/Pajarito.jl/v0.8.3/README.md)

### Inferences

- Recommendation for this user: **write the MISOCP of Q5 in CVXPY**, solve with Gurobi (free
  academic named-user) and independently with MOSEK (free personal academic) — two different
  solvers on one model is exactly the "check against something outside the computation" discipline
  this project needs, and CVXPY makes it a one-argument change. If the answers disagree, that is the
  signal.
- PuLP, python-mip and linopy are all LP/MILP-only; none of them can express the conic constraint,
  so they are out for this objective even though all three are actively maintained.
- Pyomo is the right choice only if the user wants to go the Harman–Rosa MILP route (McCormick
  bounds) and keep the model in a general algebraic form.

### Gaps

- AMPL and GAMS versions and academic terms were not retrieved (both have academic programmes; I did
  not verify the 2026 terms).
- CVXPY's MIQCP/MISOCP support matrix per backend was not retrieved page-by-page; the extras list
  tells you which solvers are wired up, not which cones each wiring passes through.

---

## Q7. At m ≤ 30, is exhaustive enumeration with a fast closed-form score simply better?

### Takeaway

**Yes, decisively, and it is not close.** I measured it: a batched NumPy evaluator for exactly this
objective (max-min pairwise Mahalanobis across 6 class means, k×k solve per subset) runs at
37,000–63,000 subsets/s single-threaded on this Windows machine. The *entire* subset space at m = 30
for a fixed k = 15 — 155 million subsets, the worst case — takes about 70 minutes single-core, and
every smaller k is seconds to minutes. All 2^30 − 1 subsets of all sizes take about 8 hours
single-core, or roughly 40 minutes on 12 cores. For comparison, Mittelmann's MISOCP instances with
about 100 binaries take COPT 10–3,300 s and time out MOSEK and SCIP on 10 of 47 instances at a 1-hour
limit.

### Cited findings — my own measurement (not from a source; reproducible)

Measured on this machine (Windows 11, Python 3.12, NumPy, single thread), objective = minimum over
the 15 pairs of 6 class means of `Δμ_Sᵀ (Σ_SS)⁻¹ Δμ_S`, batched 20,000 subsets per `np.linalg.solve`
call:

| m | k | C(m,k) | measured rate | full sweep |
|---|---|---|---|---|
| 20 | 10 | 184,756 | 63,222 subsets/s | **2.9 s** (measured end-to-end) |
| 25 | 12 | 5,200,300 | 50,757 subsets/s | **102.5 s** (measured end-to-end) |
| 30 | 15 | 155,117,520 | 37,140 subsets/s (2,000,000 evaluated in 53.9 s) | **≈ 4,177 s ≈ 70 min** (extrapolated from the measured rate) |

`Σ_{k=1..30} C(30,k) = 2^30 − 1 = 1,073,741,823`, so the all-k sweep at 37,140/s is
≈ 28,910 s ≈ **8.0 h single-core**, ≈ 40 min on 12 cores (embarrassingly parallel over k and over
subset blocks).

Script: `C:\Users\grego\AppData\Local\Temp\claude\c--Users-grego-OneDrive-Desktop-CTSpinoPelvic1K-1\3b686022-ee08-4102-a3df-20b9ab7a8757\scratchpad\enum_bench2.py`
(scratchpad — copy it into the repo if the arithmetic is going into a paper).

A naive un-batched version of the same code ran at only 8,510 subsets/s, i.e. **7× slower**, so the
"fast closed-form score" claim depends on batching the linear solves; a per-subset Python loop is
what makes people reach for a solver unnecessarily.

### Cited findings — the comparison

- Mittelmann's MISOCP table: on 47 instances with roughly 50–100 binaries, COPT 9.0.0 solves all 47
  with individual times from 1 s to 3,321 s; MOSEK 11.2.3 solves 37 and SCIP 10.0.0 solves 39, with
  10 instances timing out at 1 h. — [plato.asu.edu/ftp/misocp.html](https://plato.asu.edu/ftp/misocp.html)
- Bertsimas et al.'s own MIO claim is "n in the 1000s and p in the 100s to provable optimality in
  minutes" — i.e. minutes at p an order of magnitude larger than m = 30, so the solver route is not
  *infeasible* here, just pointless. — [arXiv 1507.03133](https://arxiv.org/pdf/1507.03133)
- An exact sensor-selection formulation reports "optimal solutions for systems with 30 to 50 states
  in seconds". — [ar5iv 2304.02692](https://ar5iv.labs.arxiv.org/html/2304.02692)

### Inferences

- At m ≤ 30 with a fixed k, enumeration wins on every axis that matters here: it is **exact by
  construction** (no relaxation, no big-M, no numerical tolerance, no optimality gap to interpret);
  it needs **no licence**; it returns the **whole ranked list**, so you get the top-50 subsets, the
  score distribution, the sensitivity of the winner to perturbing Σ, and the gap between the best
  and second-best subset — none of which a MIP solver hands you. Given this project's documented
  history of plausible-but-wrong single numbers, the full distribution is worth more than the
  argmax.
- A solver only starts to earn its keep when (a) m grows past roughly 40–45, where C(m, m/2) crosses
  10^12 and enumeration dies; or (b) side constraints appear that break the clean enumeration (e.g.
  "at most one of these three correlated measurements", "this one must be included", a budget on
  acquisition time) — though note those constraints usually *shrink* the enumeration space too; or
  (c) the objective stops being computable in closed form per subset.
- The honest framing for a paper: do the enumeration, report that it is exhaustive, and cite the
  MIO/MISOCP literature as the method that *would* be needed at larger m. Do not frame a 30-feature
  enumeration as "we solved a mixed-integer program".
- One real risk at this size is the opposite of intractability: with 10^8 subsets evaluated against
  a noisy Σ estimated from a finite sample, the maximum of the score is badly upward-biased by
  selection. The binding problem at m = 30 is **statistical, not computational** — which is what
  Flusser & Suk already observed in 1998 when they noted that the separability gain flattens and
  then the chosen features "become too noise-sensitive". Nested cross-validation or a bootstrap over
  the whole enumeration (feasible at these timings) is the thing to spend compute on, not a solver.

### Gaps

- My timings are from one machine and one score implementation; they are a measurement, not a
  benchmark. A C or Numba implementation would likely be 10–100× faster again, which only
  strengthens the conclusion.
- I did not measure a solver on the same model, so the enumeration-vs-solver comparison rests on
  Mittelmann's MISOCP timings for differently-structured instances. A direct head-to-head would be a
  half-day of work and would make the claim airtight.
