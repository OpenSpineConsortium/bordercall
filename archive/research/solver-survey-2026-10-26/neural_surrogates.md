# Neural-network approaches to approximating and optimizing an expensive noisy simulation objective over subset decision spaces (state as of 2026-10-26)

**Framing note for the report writer.** Everything in this file is *research-grade* unless
explicitly flagged otherwise. Four packages here are credible engineering tools that a careful
scientist can depend on: **`sbi`**, **`pymoo`**, **`SMT`**, **`LassoNet`** (plus **GPyTorch** and
**PyTorch Geometric** as libraries rather than methods). Almost everything else named in the
assignment is a paper with a repository that stopped moving between 2020 and 2024. The
single most decision-relevant finding is the staleness table in the first section below.

**Repository status was measured, not recalled.** All "last push", star counts, archive flags and
PyPI upload dates below come from direct GitHub REST API (`/repos/{owner}/{repo}`, authenticated)
and PyPI JSON API queries executed 2026-10-26, routed through WSL. `pushed_at` is the last commit
to any branch; `archived: true` is the authors having made the repo read-only. The priority
repositories (Concrete Autoencoders, STG, L0_regularization, LassoNet, torchgfn, the
amortized-optimization tutorial, Open-L2O, attention-learn-to-route, rl4co, DeepSets,
set_transformer, pySOT, subsets) were queried twice in independent passes and returned identical
dates. Every repository named anywhere in this file has a measured date; nothing below is inferred
or recalled. Where a repo and its PyPI package disagree (apricot, nevergrad), both dates are given,
because an active git history with a stale release means `pip install` does not get you the
maintained code.

### Master staleness table (measured 2026-10-26)

| Package / repo | Last git push | Latest PyPI | Verdict |
|---|---|---|---|
| `SMTorg/smt` (Surrogate Modeling Toolbox) | 2026-10-26 | smt 2.15.0, 2026-09-08 | **Production-quality, actively maintained** |
| `lasso-net/lassonet` | 2026-10-24 | lassonet 0.0.21, 2026-10-24 | **Production-quality for its narrow job** |
| `sbi-dev/sbi` | 2026-10-23 | sbi 0.27.0, 2026-08-04 | **Production-quality** |
| `bayesflow-org/bayesflow` | 2026-10-23 | bayesflow 2.1.0, 2026-10-23 | Active, research-grade-plus |
| `pyg-team/pytorch_geometric` | 2026-10-21 | (frequent) | **Production-quality library** (hosts DeepSets/Set Transformer) |
| `cornellius-gp/gpytorch` | 2026-10-02 | gpytorch 1.15.2, 2026-02-28 | **Production-quality** |
| `shb84/jenn` (SMT's GENN upstream) | 2026-09-20 | jenn 2.1.1, 2026-09-20 | Active but tiny (10 stars) — single-maintainer risk |
| `phlippe/uvadlc_notebooks` (Gumbel top-k teaching code) | 2026-06-01 | — | Maintained teaching material (3,203 stars) |
| `ai4co/rl4co` | 2026-09-14 | rl4co 0.7.0, 2026-09-14 | Active research framework |
| `anyoptimization/pymoo` | 2026-07-07 | pymoo 0.6.2, 2026-06-28 | **Production-quality** |
| `DEAP/deap` | 2026-04-17 | deap 1.4.4, 2026-04-17 | **Production-quality** (but no surrogate machinery) |
| `alexhernandezgarcia/gflownet` | 2026-10-22 | — | Active research code |
| `GFNOrg/torchgfn` | 2026-08-22 | torchgfn 2.4.1, 2026-04-05 | Active research library |
| `recursionpharma/gflownet` | 2026-09-15 | — | Active, graph/molecule-specialised |
| `PKU-DAIR/open-box` | 2026-03-28 | openbox 0.9.0, 2026-03-27 | Semi-active (7 months quiet) |
| `facebookresearch/amortized-optimization-tutorial` | 2025-10-05 | — | Monograph LaTeX source, **not a library** |
| `jmschrei/apricot` | 2025-11-17 | apricot-select 0.6.1, **2021-02-18** | Git alive, **release 5.5 years stale** |
| `decile-team/submodlib` | 2025-05-14 | not on PyPI under that name | Research code |
| `wesselb/neuralprocesses` | 2024-12-17 | NeuralProcesses 0.2.7, 2024-12-17 | **Quiet ~22 months** |
| `wouterkool/attention-learn-to-route` | 2024-08-04 | — | **Reference code, frozen** |
| `probabilists/lampe` | 2024-08-21 | lampe 0.9.0, 2024-07-20 | **Quiet ~2 years** |
| `undark-lab/swyft` | 2024-03-30 | swyft 0.4.5, 2023-09-15 | **Stale** |
| `ermongroup/subsets` (Gumbel top-k) | 2023-10-03 | — | **Stale (post-2023 cutoff, barely)** |
| `manzilzaheer/DeepSets` | **2023-01-21** | — | **STALE — no commit since Jan 2023** |
| `VITA-Group/Open-L2O` | **2023-06-09** | — | **STALE — the L2O benchmark is abandoned** |
| `mfbalin/Concrete-Autoencoders` | **2022-05-24** | concrete-autoencoder 0.0.1, **2019-06-10** | **ABANDONED** |
| `runopti/stg` (Stochastic Gates) | **2022-02-18** | stg 0.1.2, **2020-07-22** | **ABANDONED** |
| `dme65/pySOT` | **2021-10-27** | pySOT 0.3.3, **2020-06-22** | **ABANDONED** |
| `juho-lee/set_transformer` | **2020-02-11** | — | **ABANDONED (6.7 years)** |
| `AMLab-Amsterdam/L0_regularization` | **2020-07-17** | — | **ARCHIVED (read-only) by the authors** |
| Deep Submodular Functions (Bilmes/Bai) | — | — | **No code ever released** |

---

## SET-FUNCTION LEARNING: DeepSets, Set Transformer, learned/deep submodular functions

### Takeaway
Permutation-invariant architectures are the right *inductive bias* for a surrogate of A(S, r), but
every canonical author repository is dead: DeepSets has had no commit since January 2023 and Set
Transformer none since February 2020. The only maintained route is PyTorch Geometric, which ships
`DeepSetsAggregation` and `SetTransformerAggregation` as supported library components. Deep
submodular functions (Bilmes/Bai) have never had code and would have to be written from the paper.

### Cited Findings
- `manzilzaheer/DeepSets` (the NeurIPS 2017 reference implementation, 322 stars, not archived) last received a push on **2023-01-21** — GitHub REST API, queried 2026-10-26 — [repo](https://github.com/manzilzaheer/DeepSets)
- `juho-lee/set_transformer` (the ICML 2019 PyTorch reference implementation, 692 stars) last received a push on **2020-02-11** — GitHub REST API, queried 2026-10-26 — [repo](https://github.com/juho-lee/set_transformer)
- No PyPI package exists under `set-transformer`, `deepsets`, or `pytorch-set-transformer` (all return 404 from the PyPI JSON API, queried 2026-10-26) — [PyPI](https://pypi.org/)
- PyTorch Geometric (24,130 stars, last push 2026-10-21) exports from `torch_geometric.nn.aggr`: `DeepSetsAggregation`, `SetTransformerAggregation`, `Set2Set`, `GraphMultisetTransformer`, `MLPAggregation`, `SortAggregation`, `AttentionalAggregation`, `EquilibriumAggregation`, `LCMAggregation`, `PatchTransformerAggregation`, plus basic sum/mean/max/var/std/softmax/power-mean aggregations — [source](https://raw.githubusercontent.com/pyg-team/pytorch_geometric/master/torch_geometric/nn/aggr/__init__.py)
- Papers With Code lists the Bilmes & Bai deep submodular functions work (arXiv:1701.08939) and the Bai, Noble & Bilmes NeurIPS 2018 follow-on as having **no code implementations** — [Papers With Code](https://paperswithcode.com/author/wenruo-bai); [arXiv:1701.08939](https://arxiv.org/abs/1701.08939)
- The original class is Dolhansky & Bilmes, "Deep Submodular Functions: Definitions and Learning", NeurIPS 2016, which proposes the class and a max-margin learning method; no implementation is distributed with it — [NeurIPS](https://papers.nips.cc/paper/6361-deep-submodular-functions-definitions-and-learning)
- The architecture is described well enough to reimplement in later work: a DSF is a layered network of concave functions with non-negative weights applied to modular features — [Deep Submodular Peripteral Networks, arXiv:2403.08199](https://arxiv.org/pdf/2403.08199); see also [Extended Deep Submodular Functions, arXiv:2409.12053](https://arxiv.org/pdf/2409.12053)
- For *maximizing* an already-known submodular function (as opposed to learning one), two libraries exist: `jmschrei/apricot` (537 stars, git push 2025-11-17) but whose PyPI release `apricot-select` 0.6.1 dates from **2021-02-18**; and `decile-team/submodlib` (136 stars, git push 2025-05-14) — [apricot](https://github.com/jmschrei/apricot); [submodlib](https://github.com/decile-team/submodlib)

### Inferences
- The practical recommendation for a permutation-invariant surrogate in 2026 is *not* to clone either canonical repo. It is 30 lines of PyTorch (a per-element MLP, a sum/mean pool, a head MLP) or one import from PyG. Both canonical papers are short and the architectures are small; the repos add nothing a maintained library does not.
- For the user's problem the "set" is a subset of a *fixed, small* ground set of 7-30 named measurements. That means the set is losslessly encodable as a fixed-length binary vector, and a plain MLP on that binary vector is already permutation-invariant in the only sense that matters (the measurement identities are fixed, not exchangeable tokens). The DeepSets/Set Transformer machinery earns its keep when the ground set is large, variable, or when you want to generalize to measurements never seen in training. If the user's ground set is fixed, **the permutation-invariance argument for these architectures largely evaporates** and the honest baseline is a 2-layer MLP or a GP with a suitable kernel on the binary vector.
- Deep submodular functions would be the theoretically attractive surrogate — they are submodular *by construction*, so the greedy algorithm's 1 - 1/e guarantee applies to the fitted surrogate — but with no code and no maintained reimplementation this is a multi-week build with no reference to validate against. That is a poor trade for a 7-30 variable problem.

### Gaps
- I found no benchmark comparing a DeepSets/Set Transformer surrogate against a plain GP or MLP on a *small fixed* ground set with binary indicators. The literature on these architectures is about large and variable-cardinality sets. The user's regime is not the regime the papers were written for, and nobody appears to have measured the gap.
- I did not locate a third-party maintained reimplementation of deep submodular functions. I did not exhaustively search GitHub for one; the search tool reported only the papers.

---

## AMORTIZED OPTIMIZATION / LEARNING TO OPTIMIZE (L2O)

### Takeaway
Amos's tutorial is a monograph, not a library, and it **explicitly declares discrete and
combinatorial domains out of scope** — which is exactly the user's problem. The main L2O benchmark
repository (Open-L2O) has had no commit since June 2023. None of this is production-usable; it is a
reading list.

### Cited Findings
- The tutorial's arXiv v1 title is "Tutorial on amortized optimization **for learning to optimize over continuous domains**"; later versions drop the qualifier from the title but not the scope — [arXiv:2202.00665](https://arxiv.org/abs/2202.00665v1)
- Section 5.6.2, "Amortized optimization over discrete domains", states that discrete and mixed discrete-continuous problems are a significant generalization and that the author **chose not to include these works**, because many discrete optimization methods differ significantly from the ones considered and "learning with derivative information often becomes impossible" — [arXiv:2202.00665 (v4/v5 HTML)](https://arxiv.org/html/2202.00665v5)
- That section points the reader instead to Khalil et al., Bertsimas & Stellato, Cappart et al., and to surveys by Lodi & Zarpellon, Bengio et al., and Kotary et al. — [arXiv:2202.00665](https://arxiv.org/html/2202.00665v5)
- Published as Brandon Amos, "Tutorial on Amortized Optimization", *Foundations and Trends in Machine Learning* 16(5): 592-732, 2023 — [Emerald/FnT](https://www.emerald.com/ftmal/article/16/5/592/1332424/Tutorial-on-Amortized-Optimization); [Meta AI](https://ai.meta.com/research/publications/tutorial-on-amortized-optimization/)
- `facebookresearch/amortized-optimization-tutorial` (267 stars) last push **2025-10-05**; its GitHub description is "Tutorial on amortized optimization for learning to optimize over continuous domains" — i.e. the repo is the monograph's source and figure code — GitHub REST API, queried 2026-10-26 — [repo](https://github.com/facebookresearch/amortized-optimization-tutorial)
- `VITA-Group/Open-L2O`, described as "a comprehensive and reproducible benchmark for Learning to Optimize algorithms" (298 stars), last push **2023-06-09** — GitHub REST API, queried 2026-10-26 — [repo](https://github.com/VITA-Group/Open-L2O)
- **There is no `learn2opt` package.** A GitHub repository search for `learn2opt` returns 5 results, the largest with **3 stars** (`multimodallearning/Learn2Optimise`, last push 2022-07-12); the others have 0-1 stars and the most recent non-trivial one is a personal project. Nothing by that name is usable — GitHub Search API, queried 2026-10-26
- A GitHub search for "learning to optimize L2O" sorted by stars confirms Open-L2O (298 stars, stale 2023-06-09) is the ecosystem's largest repo, and that the next tier is also mostly stale: `VITA-Group/L2O-Training-Techniques` (30 stars, **2021-12-30**), `Shen-Lab/Bayesian-L2O` (14 stars, **2022-08-19**), `LearningToOptimize/LearningToOptimize.jl` (16 stars, 2025-04-01, Julia) — GitHub Search API, queried 2026-10-26
- **The one actively maintained L2O strand relevant to a discrete decision space** is mixed-integer: `pnnl/L2O-MINLP` ("Learning-to-Optimize for Mixed-Integer Non-Linear Programming", 72 stars, last push **2026-03-10**) and `LucasBoTang/REINS` ("A Learning-to-Optimize package for Mixed-Integer Nonlinear Programming", 12 stars, last push **2026-03-15**) — GitHub REST/Search API, queried 2026-10-26

### Inferences
- When the author of the field's standard reference deliberately excises the discrete case because gradients are unavailable, that is a strong signal that the amortized-optimization toolkit does not transfer to subset selection without replacing its core mechanism (which is what GFlowNets and the differentiable relaxations below do).
- Amortization pays off when you will solve *many* instances of the same problem family. The user's framing — one objective A(S, r), with r a parameter — does admit an amortization story (train once, query for any r). But the amortization is only worth the training cost if the number of distinct r values is large. For a handful of r values, solving each separately with a classical method is cheaper and carries a certificate.

- The two live MINLP repos are the honest answer to "is any of it production-usable": at 72 and 12 stars with ~7 months since the last commit, they are credible *research* code by identifiable groups (PNNL; Lucas Tang), not production software. They also solve constrained MINLP with known algebraic constraints, which is not the user's black-box noisy-simulator setting.

### Gaps
- I did not fetch the Chen et al. L2O survey directly, so I cannot quote its figures. Its existence and framing are well established but I have no citable statistic from it here.

---

## NEURAL COMBINATORIAL OPTIMIZATION for subset choice, including GFlowNets

### Takeaway
`torchgfn`, `alexhernandezgarcia/gflownet` and `rl4co` are all genuinely alive in 2026, and
GFlowNets are the one neural family *designed* for the user's stated want ("find all subsets that
work"). But the published subset-selection application needed 40,000 reward evaluations per problem
instance, the field's own 2026 papers document mode collapse and over-sampling of low-reward
regions, and the pointer-network / Kool attention lineage is frozen reference code with documented
generalization failures.

### Cited Findings
- `GFNOrg/torchgfn` (318 stars) last push **2026-08-22**; PyPI `torchgfn` 2.4.1 uploaded **2026-04-05**; requires Python >= 3.10; `pip install torchgfn`, with extras `dev`/`scripts`/`all` — GitHub REST API + PyPI JSON, queried 2026-10-26; [README](https://raw.githubusercontent.com/GFNOrg/torchgfn/master/README.md)
- `torchgfn` ships discrete environments (Discrete Energy Based Model, HyperGrid, Graph Generation) and continuous ones (Box); losses cover TB, DB, SubTB, FM, ZVar and RTB; it documents **conditional GFlowNets** for "learning families of distributions parameterized by external conditions", off-policy training with replay buffers, and explicit exploration strategies (epsilon-greedy, temperature scaling, noisy layers, local search, variance annealing) "for mode discovery" — [torchgfn README](https://raw.githubusercontent.com/GFNOrg/torchgfn/master/README.md)
- The `torchgfn` README states the repo "serves the purpose of **fast prototyping** GFlowNet related algorithms" and "aims to accompany researchers and engineers in learning about GFlowNets" — i.e. the maintainers position it as research software — [torchgfn README](https://raw.githubusercontent.com/GFNOrg/torchgfn/master/README.md)
- Other live GFlowNet codebases: `alexhernandezgarcia/gflownet` (352 stars, last push **2026-10-22**) and `recursionpharma/gflownet` (294 stars, last push **2026-09-15**, "specialized for graph & molecular data") — GitHub REST API, queried 2026-10-26
- The closest published analogue to the user's problem is sensor selection: choosing k of m elements to optimize a generic quality-of-service metric, framed as a deterministic MDP whose terminal states are size-k subsets, with a GFlowNet sampling subsets with probability proportional to subset performance. It reports outperforming convex-relaxation and greedy baselines, and a multiobjective variant — [arXiv:2407.19736](https://arxiv.org/abs/2407.19736)
- That sensor-selection work trains for **40,000 root-to-leaf MDP trajectories for every instantiation of the problem** — [arXiv:2407.19736 (PDF)](https://arxiv.org/pdf/2407.19736)
- A related Rutgers workshop version reports training on **less than 0.0001% of the possible subsets** — [NSF PAR](https://par.nsf.gov/servlets/purl/10539257)
- GFlowNet Foundations states GFlowNets can represent distributions over composite objects including sets and graphs, and covers estimating marginal probabilities over subsets of variables — [arXiv:2111.09266](https://arxiv.org/pdf/2111.09266)
- Mode collapse is an acknowledged failure mode: GFlowNets "can get stuck on modes found early and need long training to find diverse solutions", and existing exploration methods "usually depend on heuristic novelty signals" (Loss-Guided GFlowNets, AAAI 2026) — [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/39613); [arXiv:2505.15251](https://arxiv.org/html/2505.15251v2)
- A February 2026 paper states plainly that "existing GFlowNets often suffer from excessive exploration over vast state spaces, leading to over-sampling of low-reward regions and convergence to suboptimal distributions" and that "effectively biasing GFlowNets toward high-reward solutions remains a non-trivial challenge" — [arXiv:2602.11491](https://arxiv.org/abs/2602.11491)
- `wouterkool/attention-learn-to-route` (the ICLR 2019 attention solver, 1,389 stars) last push **2024-08-04** — frozen reference code — GitHub REST API, queried 2026-10-26
- The maintained successor framework is `ai4co/rl4co` (917 stars, last push **2026-09-14**; PyPI `rl4co` 0.7.0 uploaded **2026-09-14**), "a PyTorch library for all things Reinforcement Learning for Combinatorial Optimization" — GitHub REST API + PyPI JSON, queried 2026-10-26; also `Thinklab-SJTU/ML4CO-Bench-101` (54 stars, last push 2026-09-05)
- NCO generalizes poorly: a comprehensive vehicle-routing survey reports that most NCO solvers generalize poorly across data distributions, with solvers trained on uniform instances failing on normally distributed ones — [arXiv:2406.00415](https://arxiv.org/pdf/2406.00415)
- Learned solvers match classical solvers only on very small instances and fail to generalize to practically sized ones; the authors argue the whole pipeline needs rethinking — [Constraints, 10.1007/s10601-022-09327-y](https://link.springer.com/article/10.1007/s10601-022-09327-y)
- Neural solvers generalize poorly to small perturbations of problem instances — [arXiv:2110.10942](https://arxiv.org/abs/2110.10942v1)
- Evaluation practice in this field has been criticised: a study of learned local search argues weak baselines and missing ablations have inflated results, and that a simple Tabu Search heuristic beats state-of-the-art learned heuristics on both performance and generalizability — [Papers With Code](https://paperswithcode.com/paper/unveiling-the-limits-of-learned-local-search)
- A 2026 critical review exists — "Beyond Neural Solvers: A Critical Review of Machine Learning for Combinatorial Optimization", *Mathematics* 14(12):2208, DOI 10.3390/math14122208 — [CiteDrive record](https://www.citedrive.com/en/discovery/beyond-neural-solvers-a-critical-review-of-machine-learning-for-combinatorial-optimization/)

### Inferences
- The GFlowNet pitch fits the user's phrasing almost suspiciously well: a GFlowNet trained with reward A(S, r) samples subsets with probability proportional to reward, which is literally "all subsets that work, weighted by how well they work" rather than a single argmax. If the user's real question is *which measurements are robustly useful across many good subsets*, that is the right object.
- But the cost accounting kills it at this problem size. The published subset-selection GFlowNet consumed 40,000 reward evaluations per problem instance. At the user's stated seconds-to-minutes per evaluation, 40,000 evaluations is roughly **11 hours (at 1 s) to 28 days (at 60 s)** of simulator time. A 7-20 variable space can be *fully enumerated* for less than that. The GFlowNet would have to be driven by a surrogate, at which point the GFlowNet is sampling the surrogate's errors, not the anatomy.
- `rl4co` is the repo to name if an NCO framework is wanted, not Kool's original. Pointing a reader at `attention-learn-to-route` in 2026 points them at code last touched in August 2024, built for routing, with no subset-selection environment.

### Gaps
- I found no paper applying GFlowNets to *feature subset selection for a classifier* specifically. The search returned sensor selection, antenna array design, and non-GFlowNet differentiable methods (e.g. GFSNetwork with Gumbel-Sigmoid, Google's Sequential Attention). Sensor selection is structurally the same problem, but the transfer is my inference, not a published result.
- I could not retrieve the full text of the *Mathematics* 2026 critical review (MDPI returned an Akamai access-denied to a direct fetch), so I can report its existence and title but not its findings.

---

## SURROGATE-ASSISTED EVOLUTIONARY / SIMULATION OPTIMIZATION

### Takeaway
Three of the named packages are credible engineering tools (**SMT**, **pymoo**, **DEAP**) and two
are not (**pySOT** is abandoned since 2020-2021; **openbox** is semi-active). But note what the
credible ones actually give you: pymoo and DEAP give you the *evolutionary* half and expect you to
bring your own surrogate; SMT gives you the *surrogate* half, including mixed-integer/hierarchical
Gaussian processes and EGO, and is the single best-engineered item in this entire file.

### Cited Findings
- `SMTorg/smt` (924 stars) last push **2026-10-26** (the day of this survey); PyPI `smt` 2.15.0 uploaded **2026-09-08**; docs build is "SMT 2.15.1.dev8" — GitHub REST API + PyPI JSON, queried 2026-10-26; [docs](https://smt.readthedocs.io/en/latest/)
- SMT's surrogate list: least-squares, second-order polynomial, Kriging (KRG), KPLS, KPLSK, GPX, GEKPLS, Marginal GP (MGP), Sparse GP (SGP), Cooperative Components Kriging, radial basis functions, inverse-distance weighting, regularized minimal-energy tensor-product splines, **GENN** (gradient-enhanced neural networks), and knowledge-enhanced RBF — [SMT docs](https://smt.readthedocs.io/en/latest/)
- SMT's Applications section includes "Mixed Integer and Hierarchical Design Spaces (Variables, Sampling and Context)", "Mixed Integer and hierarchical Surrogates", mixture of experts, several multi-fidelity Kriging variants, and **Efficient Global Optimization (EGO)** — [SMT docs](https://smt.readthedocs.io/en/latest/)
- SMT ships a neural-network surrogate: GENN, "fully connected multi-layer perceptrons whose training process is modified to predict partial derivatives accurately", relying on an upstream library `jenn`; the stated benefit is "better accuracy with fewer training points compared to standard fully connected neural nets" — [SMT GENN](https://smt.readthedocs.io/en/latest/_src_docs/surrogate_models/genn.html)
- That upstream dependency is itself maintained but very small: `shb84/jenn` ("Jacobian-Enhanced Neural Nets") last push **2026-09-20**, **10 stars**; PyPI `jenn` 2.1.1 uploaded **2026-09-20** — GitHub REST API + PyPI JSON, queried 2026-10-26. GENN also requires **gradients of the objective**, which the user's Monte Carlo accuracy does not supply, so inside SMT the relevant surrogates for this problem are the Kriging family, not GENN.
- SMT states it is "developed and maintained by contributors worldwide and supported by research institutions", with companion toolboxes `smt-optim` (multi-fidelity and multi-objective Bayesian optimization with or without constraints), `smt-design-space-ext` (hierarchical variables) and `smt-explainability` — [SMT docs](https://smt.readthedocs.io/en/latest/)
- SMT 2.0 citation: Saves, Lafage, Bartoli, Diouane, Bussemaker, Lefebvre, Hwang, Morlier & Martins, "SMT 2.0: A Surrogate Modeling Toolbox with a focus on Hierarchical and Mixed Variables Gaussian Processes", *Advances in Engineering Software* 188:103571, 2024 — [DOI](https://doi.org/10.1016/j.advengsoft.2023.103571)
- `anyoptimization/pymoo` (2,980 stars) last push **2026-07-07**; PyPI `pymoo` 0.6.2 uploaded **2026-06-28** — GitHub REST API + PyPI JSON, queried 2026-10-26
- pymoo supports **native binary decision variables**: `MixedVariableProblem` with `vars = {"b": Binary(), "x": Choice(options=[...]), "y": Integer(bounds=...), "z": Real(bounds=...)}`, solved with `MixedVariableGA`, "which defines different operators for each variable type" — [pymoo docs](https://pymoo.org/customization/mixed.html)
- `DEAP/deap` (6,456 stars) last push **2026-04-17**; PyPI `deap` 1.4.4 uploaded **2026-04-17** — GitHub REST API + PyPI JSON, queried 2026-10-26
- `dme65/pySOT` "Surrogate Optimization Toolbox for Python" (217 stars) last push **2021-10-27**; PyPI `pySOT` 0.3.3 uploaded **2020-06-22**. **Abandoned by the criterion the user set.** — GitHub REST API + PyPI JSON, queried 2026-10-26
- `PKU-DAIR/open-box` (448 stars) last push **2026-03-28**; PyPI `openbox` 0.9.0 uploaded **2026-03-27**; described as "towards generalized and efficient blackbox optimization system/package (KDD 2021 & JMLR 2024)" — GitHub REST API + PyPI JSON, queried 2026-10-26
- Adjacent tools that are more active than pySOT/openbox, for context: `automl/SMAC3` (last push 2026-10-26), `optuna/optuna` (2026-10-23), `facebookresearch/nevergrad` (git 2026-10-20 but PyPI `nevergrad` 1.0.12 from **2025-04-23** — an 18-month release lag), `huawei-noah/HEBO` (2026-10-12), `secondmind-labs/trieste` (2026-10-15), BoTorch — **note the repo moved from `pytorch/botorch` to `meta-pytorch/botorch`** (last push 2026-10-16) — GitHub REST API, queried 2026-10-26
- A February 2026 *IEEE Transactions on Evolutionary Computation* (vol. 30 no. 1) review of relation models for expensive optimization states there has been "a notable lack of systematic organization or comprehensive summary of relation models", defines a research framework, and says the strategies will be open-sourced on GitHub — [ECNU record](https://pure.ecnu.edu.cn/en/publications/expensive-optimization-via-relation/)
- Surrogate models in evolutionary single-objective optimization divide into **absolute fitness models** (directly approximating fitness values) and **relative fitness models** (estimating relative rank or preference of candidates) — [Lingnan / Birmingham records](https://research.birmingham.ac.uk/en/publications/surrogate-models-in-evolutionary-single-objective-optimization-a-/)
- Expensive *combinatorial* optimization problems "receive far less attention than continuous problems" — 2024 survey in *Complex & Intelligent Systems* — [DOAJ](https://doaj.org/article/67ec245433a94c61bf74825c719b6855)
- A 2023 review in *Expert Systems with Applications* calls surrogate-assisted EAs "a hot technology for expensive optimization problems" — [catalogue record](https://katalog.hcu-hamburg.de/vufind/Search2Record/ELV062744682)

### Inferences
- **The report should name SMT, not pySOT.** The assignment listed pySOT as a candidate; it has been dead since 2021 (git) and 2020 (PyPI). SMT occupies the same niche, is actively developed, has a peer-reviewed citation in *Advances in Engineering Software*, explicitly handles mixed-integer design spaces, and ships EGO. It is also the one place in this file where a *neural* surrogate (GENN) comes inside an engineering-quality package rather than a paper repo.
- pymoo's `Binary()` variable type plus `MixedVariableGA` is the lowest-friction way to run a genetic algorithm over the user's subset space with production-quality code. pymoo does not, however, provide a built-in surrogate-assisted loop for this; wiring a surrogate in is the user's code.
- The "relative fitness model" distinction matters for this problem specifically. For a noisy A(S, r), learning to *rank* two subsets is a far easier and far more noise-tolerant learning problem than regressing accuracy to three decimal places, and it is what the optimizer actually needs. If a neural surrogate is used at all, a pairwise ranking surrogate is the better-posed choice, and the SAEA literature has a name and a taxonomy for it.
- The 2024 survey's observation that expensive *combinatorial* problems get far less attention than continuous ones explains the pattern across this whole file: the mature engineering tools (SMT, BoTorch, nevergrad, trieste) were built for continuous design spaces, and the subset-specific neural methods are the ones with dead repositories.

### Gaps
- I could not confirm whether pymoo ships any built-in surrogate-assisted algorithm in 0.6.2; its "Miscellaneous" docs index lists reference directions, convergence, decomposition, KKTPM, checkpoints and lexicographic selection, with no surrogate entry. Absence from that index is suggestive but not proof.
- The February 2026 TEVC relation-model review's promised GitHub release could not be located; I have only the publisher's record, not the code.

---

## SIMULATION-BASED INFERENCE (SBI) as a surrogate route

### Takeaway
`sbi` and `BayesFlow` are both genuinely well maintained and are the two best-engineered neural
packages in this file after SMT; `LAMPE` has been quiet two years and `swyft` is stale. But the
honest answer on applicability is that all four solve the *inverse* problem (given data, what are
the simulator's parameters?), and the user's problem is a *design* problem (which subset should I
measure?). The bridge exists and has a 2025-2026 literature — amortized Bayesian experimental
design — but none of it is in `sbi`'s or `BayesFlow`'s shipped feature set, and the strongest recent
method requires a differentiable simulator.

### Cited Findings
- `sbi-dev/sbi` (877 stars) last push **2026-10-23**; PyPI `sbi` 0.27.0 uploaded **2026-08-04** — GitHub REST API + PyPI JSON, queried 2026-10-26
- `sbi` implements Neural Posterior Estimation (amortized NPE and sequential SNPE), Neural Likelihood Estimation ((S)NLE) and Neural Ratio Estimation ((S)NRE); the documented workflow is `NPE().append_simulations(θ, x).train()` then `build_posterior().sample()` — [sbi docs](https://sbi.readthedocs.io/en/latest/)
- **The sbi documentation has moved.** The old site now carries a banner: "This documentation is deprecated. Please visit our new documentation at https://sbi.readthedocs.io/en/latest/. The documentation below is no longer maintained and may contain outdated information." — [old site](https://sbi-dev.github.io/sbi/latest/)
- `sbi`'s own framing of its goal is "algorithmically identify mechanistic models that are consistent with data"; amortized methods "return a posterior that can be applied to many different observations without retraining", sequential methods "focus the inference on one particular observation" — [sbi docs](https://sbi.readthedocs.io/en/latest/)
- `bayesflow-org/bayesflow` (782 stars) last push **2026-10-23**; PyPI `bayesflow` 2.1.0 uploaded **2026-10-23**; described as "amortizing Bayesian inference with neural networks" — GitHub REST API + PyPI JSON, queried 2026-10-26
- `probabilists/lampe` (137 stars) last push **2024-08-21**; PyPI `lampe` 0.9.0 uploaded **2024-07-20** — **quiet ~2 years** — GitHub REST API + PyPI JSON, queried 2026-10-26. Its normalizing-flow backend `probabilists/zuko` is more active (git 2026-03-10, PyPI `zuko` 1.6.0 2026-03-10).
- `undark-lab/swyft` (172 stars, "a system for scientific simulation-based inference at scale") last push **2024-03-30**; PyPI `swyft` 0.4.5 uploaded **2023-09-15** — **stale** — GitHub REST API + PyPI JSON, queried 2026-10-26
- The design-side literature: Deep Adaptive Design (DAD) is the foundational amortized sequential Bayesian experimental design work — [arXiv:2103.02438](https://ar5iv.labs.arxiv.org/html/2103.02438)
- "Amortized Bayesian Experimental Design for Decision-Making" (Huang, Guo, Acerbi & Kaski) proposes a Transformer Neural Decision Process that proposes designs while also inferring the downstream decision — [arXiv:2411.02064v2](https://arxiv.org/html/2411.02064v2)
- A 2025 paper unifies SBI and Bayesian optimal experimental design with an InfoNCE-regularized mutual-information objective, reporting that on a SIR task it beats the iDAD baseline's accuracy with roughly **50x fewer simulator calls** — [arXiv:2502.08004](https://arxiv.org/pdf/2502.08004)
- Step-DAD (July 2025) is a semi-amortized, policy-based design method that trains a design policy before the experiment — [arXiv:2507.14057](https://arxiv.org/abs/2507.14057v1)
- JADAI (December 2025) jointly amortizes adaptive design and Bayesian inference, arguing that policy-based design methods "have mostly been developed separately from SBI" — [arXiv:2512.22999](https://arxiv.org/html/2512.22999v1)
- "Supercharging Simulation-Based Inference" (February 2026) **assumes differentiable simulators** so that expected information gain can be optimized with gradients, and distinguishes policy-based approaches (fast deployment) from per-trajectory approaches (re-optimize after each measurement) — [arXiv:2602.06900](https://arxiv.org/html/2602.06900v1)

### Inferences
- There are two coherent ways to point `sbi` at a design question, and they should be distinguished in the report.
  (1) **Reframe the subset as a parameter.** Treat the binary indicator vector as part of θ and use amortized NPE to learn p(θ | high accuracy) — i.e. ask the posterior "conditioned on the simulation having produced a good classifier, which measurement sets were in play?". This is a legitimate use of the machinery (it is simulation-based *calibration* turned around) but it answers a question about the *distribution* of good subsets, not "which subset is best", and the posterior's concentration is a property of the flow's fit, not a confidence interval on accuracy.
  (2) **Use the amortized BOED literature properly**, which is the designed-for answer but is *not* in `sbi` or `BayesFlow`. It lives in standalone paper repositories.
- The February 2026 "Supercharging SBI" requirement of a **differentiable** simulator is likely disqualifying for the user: a pipeline that trains a classifier on synthetic anatomical columns and reports accuracy is not differentiable end to end in any practical sense.
- `sbi` and `BayesFlow` being well maintained does not make them the right tool here. They are the right tool if the user's question becomes "what simulator parameters are consistent with my real CT cohort?" — which, given the project's standing concern about whether the synthetic columns resemble the anatomy, is arguably a *more valuable* question than the subset-selection one. That is worth saying in the report as a reframing rather than a recommendation.

### Gaps
- I did not find an `sbi` or `BayesFlow` module for experimental design, model comparison or sensitivity analysis. The documentation fetch covered the landing page and method taxonomy only; I cannot assert from this evidence that no such submodule exists, only that it is not presented as a headline capability.
- I did not verify whether maintained, installable code exists for DAD, Step-DAD, JADAI or the InfoNCE/MI method. All are papers; their repository status is unchecked, which given the pattern in the rest of this file should be assumed poor until verified.

---

## NEURAL PROCESSES and deep kernel learning as noise-aware surrogates

### Takeaway
No — at 7 to 30 binary inputs they will not beat a plain GP, and the honest answer is that nobody
has even benchmarked the comparison because the regime is outside what these methods were built
for. `neuralprocesses` has been quiet ~22 months; GPyTorch's deep kernel learning is maintained but
deep kernels are a large-data tool.

### Cited Findings
- `wesselb/neuralprocesses` (92 stars) last push **2024-12-17**; PyPI `NeuralProcesses` 0.2.7 uploaded **2024-12-17** — **quiet ~22 months** — GitHub REST API + PyPI JSON, queried 2026-10-26
- `cornellius-gp/gpytorch` (3,930 stars) last push **2026-10-02**; PyPI `gpytorch` 1.15.2 uploaded **2026-02-28** — actively maintained — GitHub REST API + PyPI JSON, queried 2026-10-26
- The Neural Process Family survey states that GPs have advantages over Bayesian neural networks for uncertainty estimation when data is scarce: the prior is set analytically through a kernel and the posterior mean is a simple weighted sum of kernel values at the training points. The survey does **not** compare NPs to GPs directly — [arXiv:2209.00517](https://arxiv.org/pdf/2209.00517)
- Work on deep kernels with probabilistic embeddings notes that neural networks "require huge amounts of data, which makes them ineffective in small data settings" — [PMLR v161 (Mallick et al.)](https://proceedings.mlr.press/v161/mallick21a.html); [arXiv:1910.05858](https://ar5iv.labs.arxiv.org/html/1910.05858)
- A GP-recurrent-network dynamics study found that "a Gaussian process provides a superior mapping function for smaller datasets", with neural mappings becoming competitive only once there are more time points — [arXiv:1907.00650](https://arxiv.org/pdf/1907.00650)

### Inferences
- Neural processes are *amortized across tasks*: they are trained on many related functions and then condition cheaply on a context set. The user has **one** function, A(·, r). With one task there is nothing to amortize over, and the NP degenerates into a worse-calibrated GP with more hyperparameters and no closed-form marginal likelihood. This is a structural mismatch, not a tuning problem.
- Deep kernel learning's selling point is learning a representation when the input space has structure the kernel cannot express (images, sequences). A 7-30 dimensional binary vector has essentially no such structure to learn; the natural kernels on binary vectors (Hamming/ARD over indicators, or a categorical-overlap kernel) are already expressive enough, and SMT's mixed-integer Kriging implements that class in maintained code — [SMT docs](https://smt.readthedocs.io/en/latest/)
- The user's noise is the real modelling problem, and a GP handles it directly through the nugget/noise term with a closed-form marginal likelihood for fitting it. A neural surrogate has no equivalent principled handle, and the noise-aware claim for NPs rests on the amortization that the user cannot supply.

### Gaps
- **I found no head-to-head benchmark of Neural Processes against exact GPs on small, low-dimensional regression tasks.** The supporting evidence above is indirect (GPs beat BNNs at small N; NNs need large N) plus one anecdotal practitioner report, and I am flagging it as indirect rather than presenting it as a measured result. If the report needs a hard number for this claim, it does not exist in what I found.
- I found no benchmark of any neural surrogate on *binary* inputs at this dimensionality. The honest statement is that the comparison is unmeasured, and that the burden of proof sits with the neural method.

---

## DIFFERENTIABLE RELAXATION of subset selection

### Takeaway
This is the most serious neural contender for the user's problem — and the code situation is the
worst in this file except one bright spot. `L0_regularization` is **archived read-only** by its own
authors; Concrete Autoencoders' repo stopped in 2022 and its PyPI package is version 0.0.1 from
2019; Stochastic Gates stopped in 2022 with a 2020 PyPI release. Only **LassoNet** is alive, and it
was pushed two days before this survey. Separately, the ICML 2024 IP-CAE paper documents that
Concrete Autoencoder training is *unstable* — a specific, published reason to distrust the method
the assignment named as explicitly built for feature selection.

### Cited Findings
- `AMLab-Amsterdam/L0_regularization` (the Louizos, Welling & Kingma ICLR 2018 reference code, 250 stars) last push **2020-07-17** and is **`archived: true`** — the authors have made it read-only — GitHub REST API, queried 2026-10-26 — [repo](https://github.com/AMLab-Amsterdam/L0_regularization)
- `mfbalin/Concrete-Autoencoders` (126 stars) last push **2022-05-24**; PyPI `concrete-autoencoder` is at version **0.0.1, uploaded 2019-06-10** — GitHub REST API + PyPI JSON, queried 2026-10-26
- Concrete Autoencoders (Balin, Abid & Zou, ICML 2019) use a temperature schedule on a concrete/Gumbel-Softmax selector layer to settle on a fixed number of features, reporting gains over other feature selection methods on several datasets — [PMLR v97](https://proceedings.mlr.press/v97/balin19a.html); [arXiv:1901.09346](https://arxiv.org/pdf/1901.09346)
- **Documented instability:** the Indirectly Parameterized CAE paper (Nilsson et al., ICML 2024) argues CAE training can be unstable and ties that instability to **duplicate feature selections**; its fix is an indirect parameterization of the Gumbel-Softmax parameters, which it reports improves generalization and training time — [PMLR v235](https://proceedings.mlr.press/v235/nilsson24b.html); [arXiv:2403.00563](https://www.arxiv.org/abs/2403.00563)
- `runopti/stg` (Stochastic Gates, Yamada et al. ICML 2020; Python/R library, 115 stars) last push **2022-02-18**; PyPI `stg` 0.1.2 uploaded **2020-07-22** — GitHub REST API + PyPI JSON, queried 2026-10-26
- STG uses a continuous relaxation of Bernoulli gates trained by gradient descent with an L0-style objective — [alphaXiv/arXiv:1810.04247](https://alphaxiv.org/abs/1810.04247)
- **LassoNet is the bright spot:** `lasso-net/lassonet` (260 stars) last push **2026-10-24** (two days before this survey); PyPI `lassonet` 0.0.21 uploaded **2026-10-24**, "Reference implementation of LassoNet" — GitHub REST API + PyPI JSON, queried 2026-10-26 — [repo](https://github.com/lasso-net/lassonet); project site [lassonet.ml](https://lassonet.ml)
- LassoNet extends the Lasso to neural networks by adding residual connections from the inputs with an L1 penalty on them; **a feature is selected only if the residual layer also selects it** — [arXiv:2403.00563 (related work)](https://arxiv.org/pdf/2403.00563)
- The Gumbel top-k / relaxed subset sampling primitive: Xie & Ermon (IJCAI 2019) extend the Gumbel-max trick to subsets by perturbing log-probabilities with Gumbel noise, taking the top-k, and relaxing top-k (via the Plötz & Roth 2018 sequence-of-softmaxes construction) so gradients flow — [arXiv:1901.10517](https://arxiv.org/pdf/1901.10517)
- Its reference code `ermongroup/subsets` (58 stars) last push **2023-10-03** — GitHub REST API, queried 2026-10-26
- A maintained *teaching* implementation of Gumbel-top-k subset sampling exists in the UvA deep learning notebooks (Adeel Pervez), with a k-nearest-neighbour application — [UvA DL2 notebook](https://uvadlc-notebooks.readthedocs.io/en/latest/tutorial_notebooks/DL2/sampling/subsets.html). Its repository `phlippe/uvadlc_notebooks` (3,203 stars) last push **2026-06-01** — GitHub REST API, queried 2026-10-26 — making the notebook, oddly, the most actively maintained relaxed-subset-sampling code available.
- Google's Sequential Attention code lives as a subdirectory of the `google-research/google-research` monorepo (39,026 stars, last push **2026-10-26**), not as a standalone installable package — GitHub REST API, queried 2026-10-26
- Later differentiable feature selection: GFSNetwork (2025) uses Gumbel-Sigmoid sampling and selects the number of features automatically end-to-end — [arXiv:2503.13304](https://arxiv.org/html/2503.13304v1); Google Research's Sequential Attention treats subset selection as a sequential decision process — [Google Research blog](https://www.research.google/blog/sequential-attention-making-ai-models-leaner-and-faster-without-sacrificing-accuracy/)
- No PyPI package is published under `sequential-attention` (404 from the PyPI JSON API, queried 2026-10-26) — [PyPI](https://pypi.org/)
- The Gumbel-Softmax relaxation primitive itself is in PyTorch core as `torch.nn.functional.gumbel_softmax`, so the mechanism does not depend on any of the dead repos above.

### Inferences
- **These methods solve a different problem from the user's, and this is the deepest point in this section.** L0 gates, Concrete Autoencoders, STG and LassoNet all select features *inside* a single differentiable model by gradient descent on a training loss. The user's objective A(S, r) is the accuracy of a classifier *retrained from scratch* on each subset, estimated by Monte Carlo over synthetic columns. Those are not the same function. A gate that is useless to one particular network's optimizer is not the same as a measurement that carries no anatomical information, and the differentiable-relaxation family cannot see the Monte Carlo average at all — it sees one network's loss surface. Substituting the one for the other is exactly the class of substitution this project has been bitten by before (a maximum extent for a diameter, a first-slice-that-works for a plane).
- LassoNet is nonetheless the one to try if the user wants a *fast screening pass* to rank the 7-30 measurements and prune obvious non-contributors before spending simulator budget. It is maintained, documented, trivially installable, has a JMLR paper behind it, and its feature path gives a nested sequence of subsets — which is a genuinely useful ordering to hand to a classical exact method afterwards. Use it to shrink the ground set, not to choose the answer.
- The archived status of `L0_regularization` is a stronger signal than mere staleness: the authors chose read-only. Reporting a method whose reference implementation its own authors have closed is reporting a historical artifact.
- IP-CAE's finding that CAE instability manifests as duplicate feature selections is directly diagnostic for the user: if a run of CAE returns a subset with repeated entries or wildly different subsets across seeds, that is the known failure, not a property of the anatomy.

### Gaps
- I found no study benchmarking LassoNet, STG and Concrete Autoencoders together on **selection stability** (agreement of selected subsets across seeds or resamples). The IP-CAE paper is the closest, and a 2023 quantitative benchmark of NN interpretation methods ([arXiv:2304.02383](https://arxiv.org/pdf/2304.02383)) includes both LassoNet and CAE, but the retrieved material does not report stability results. For a problem whose stated priority is minimizing bias, the absence of a stability benchmark for this family is itself the finding.
- I could not verify whether any maintained PyTorch package wraps relaxed subset sampling (Gumbel top-k). The search returned the paper, the stale `ermongroup/subsets`, a Keras implementation inside the `zea` library, and a teaching notebook — no maintained PyTorch package.

---

## GPU: does the user's problem justify one?

### Takeaway
No. At 7-30 binary variables the networks involved are small enough to train on a laptop CPU in
seconds to minutes, and the cost is entirely in the simulator, not the network. The one published
subset-selection GFlowNet needed 40,000 reward evaluations per problem instance; at the user's
stated seconds-to-minutes per evaluation that is 11 hours to 28 days of *simulator* time, and a GPU
does not touch it. Buy simulator throughput (the grid's `reqp` CPU partition), not a GPU.

### Cited Findings
- The GFlowNet sensor-selection work trains for **40,000 root-to-leaf trajectories for every instantiation of the problem** — each trajectory terminating in a subset whose reward must be evaluated — [arXiv:2407.19736 (PDF)](https://arxiv.org/pdf/2407.19736)
- `torchgfn`'s README states no hardware requirement beyond Python >= 3.10 and lists CPU-tractable toy environments (HyperGrid, Discrete EBM) among its gym — [torchgfn README](https://raw.githubusercontent.com/GFNOrg/torchgfn/master/README.md)
- SMT's GENN neural surrogate is configured in the docs with `hidden_layer_sizes = [6, 6]` and `num_iterations = 1000` trained on **4 training points** — the scale at which these surrogates are actually used in engineering practice — [SMT GENN](https://smt.readthedocs.io/en/latest/_src_docs/surrogate_models/genn.html)
- Deep-kernel work notes that neural networks "require huge amounts of data, which makes them ineffective in small data settings" — the data regime, not the compute regime, is the binding constraint — [PMLR v161](https://proceedings.mlr.press/v161/mallick21a.html)

### Inferences
- The arithmetic of the decision space settles this. 2^7 = 128 subsets; 2^10 = 1,024; 2^15 = 32,768; 2^20 = 1,048,576; 2^30 = 1,073,741,824. At one second per Monte Carlo evaluation, **the whole space is enumerable up to about 15-17 variables in under a day of single-core time**, and trivially parallel across cores. A surrogate network with 7-30 inputs and a few hundred hidden units has on the order of 10^4 parameters; training it on a few thousand observed (S, A) pairs is a sub-minute CPU job. There is no GPU-shaped bottleneck anywhere in this pipeline.
- The only honest GPU case would be if the *simulator itself* (training the classifier on synthetic columns) is GPU-bound. If it is, the right spend is GPU throughput for the simulator on `gmsap`/`gvohp`, which has nothing to do with any method in this file.

### Gaps
- None material. This question is answerable from the arithmetic plus the one published trajectory count.

---

## THE BIAS RISK: how each neural approach can make a wrong-but-plausible number

### Takeaway
Every method in this file introduces at least one bias channel that produces a finite, plausible,
wrong answer with no internal signal that anything is wrong — the exact failure mode this project
has already paid for three times. The decisive point is that **none of these methods carries an
optimality certificate**, where the classical alternative does: greedy maximization of a submodular
set function has the 1 - 1/e guarantee, and exhaustive enumeration has a proof. At 7-30 binary
variables with a cheap-to-moderate simulator, giving up a certificate buys nothing.

### Cited Findings
- Selecting on noisy estimates overfits the selection criterion: Cawley & Talbot show that the *variance* of a model selection criterion matters as much as its bias, that noisy estimates such as k-fold cross-validation scores lead to over-fitting in model selection, and that the resulting degradation "can be surprisingly large" — comparable in size to the performance differences between the learning algorithms being compared — [JMLR 11(70):2079-2107](https://www.jmlr.org/papers/v11/cawley10a.html)
- Cawley & Talbot state their findings apply to **any** model selection practice involving optimisation of a criterion evaluated over a finite sample, including maximisation of the Bayesian evidence and optimisation of performance bounds; and that some common performance-evaluation practices are themselves susceptible to the resulting selection bias — [JMLR 11(70)](https://www.jmlr.org/papers/v11/cawley10a.html)
- Surrogate systematic error on unexplored regions is the documented NCO failure: most neural CO solvers generalize poorly across data distributions, with solvers trained on uniform instances failing on normally distributed ones — [arXiv:2406.00415](https://arxiv.org/pdf/2406.00415)
- Neural solvers also generalize poorly to **small perturbations** of problem instances — [arXiv:2110.10942](https://arxiv.org/abs/2110.10942v1)
- Learned solvers match classical ones only on very small instances and fail to generalize to practical sizes — [Constraints, 10.1007/s10601-022-09327-y](https://link.springer.com/article/10.1007/s10601-022-09327-y)
- The field's evaluation practice has been criticised for weak baselines and missing ablations inflating results, with a simple Tabu Search heuristic reported to beat state-of-the-art learned heuristics on performance *and* generalizability — [Papers With Code](https://paperswithcode.com/paper/unveiling-the-limits-of-learned-local-search)
- GFlowNets specifically: they "can get stuck on modes found early and need long training to find diverse solutions", and existing exploration fixes rely on heuristic novelty signals — [AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/39613); [arXiv:2505.15251](https://arxiv.org/html/2505.15251v2)
- And: "existing GFlowNets often suffer from excessive exploration over vast state spaces, leading to over-sampling of low-reward regions and convergence to suboptimal distributions" — [arXiv:2602.11491](https://arxiv.org/abs/2602.11491)
- Concrete Autoencoder training is unstable, and the instability manifests as duplicate feature selections — [PMLR v235 (IP-CAE)](https://proceedings.mlr.press/v235/nilsson24b.html)
- Amos excludes discrete domains from the amortized-optimization tutorial in part because "learning with derivative information often becomes impossible" there — i.e. the gradient signal that makes amortization work is absent in the user's setting — [arXiv:2202.00665](https://arxiv.org/html/2202.00665v5)

### Inferences — the specific bias channel, method by method
- **Set-function surrogate (DeepSets / Set Transformer / MLP on indicators).** A neural surrogate interpolates where it has data and extrapolates arbitrarily where it does not, with no calibrated uncertainty to warn you. Subset search then drives straight into the region of largest surrogate error, because the optimizer's job is to find the surrogate's maximum and the surrogate's maximum is wherever it is most optimistically wrong. A GP's posterior variance at least grows away from the data; an MLP's does not. **This is the "wrong bone" failure in surrogate form: a finite, plausible accuracy for a subset that was never simulated.**
- **Selection on the same draws used for fitting.** If the surrogate is fitted on Monte Carlo estimates of A and then the best subset is reported with *that same* estimate, the reported accuracy is biased upward by the maximum of the noise, and Cawley & Talbot's result says the bias can be the size of the effect being measured. The fix is not neural: hold out fresh Monte Carlo draws for the chosen subset and report those. Any method in this file that does not do this reports a winner's-curse number.
- **Overfitting the simulator's quirks rather than the anatomy.** Every method here optimizes A(S, r) as computed by the synthetic-column simulator. A neural surrogate has far more capacity to latch onto a simulator artifact than a GP with a Hamming kernel does, and a GFlowNet trained to sample proportional to reward will *concentrate* on the artifact, by design. For this project specifically — where the synthetic columns are the thing whose fidelity to real anatomy is in question — a high-capacity surrogate converts a simulator defect into a confident anatomical claim.
- **Differentiable relaxation (L0 / CAE / STG / LassoNet).** The relaxation changes the objective. Gradient descent through a relaxed gate optimizes a *soft* mixture of subsets, and the hard subset recovered at the end is not the argmax of the original A(S, r). Worse, the gated model's training loss is a different function from the Monte Carlo accuracy of a classifier retrained on the hard subset, so the method's answer is not an estimate of the user's objective at all. Add the documented CAE instability and a report of selected features that differs across seeds becomes indistinguishable from a report that the anatomy is ambiguous.
- **GFlowNets.** The reward-proportional sampling that makes GFlowNets attractive here is also the bias channel: the sampler's distribution is only proportional to reward *at convergence*, and the 2026 literature says convergence to suboptimal distributions and mode collapse are the normal case, not the exception. A GFlowNet that returns "these are the subsets that work" when it has collapsed onto the modes it found first produces a diversity claim that is a property of the training run.
- **Amortized optimization / L2O.** Beyond the gradient problem, amortization introduces an approximation gap between the network's output and the true optimum that is generally unquantified. There is no residual to inspect and no bound.
- **Absence of a certificate, stated plainly.** Exhaustive enumeration over 2^k subsets gives a proof. Greedy on a submodular objective gives 1 - 1/e. A fitted neural surrogate gives neither, and a fitted *deep submodular* function would give 1 - 1/e only with respect to the surrogate, not the simulator — which is a guarantee about the wrong function.

### Recommendation on fitness for purpose
- **At 7 to ~17 binary variables, neural methods are the wrong tool and should be named as such.** The space is 128 to ~131,000 subsets. With a simulator at seconds per evaluation and embarrassingly parallel Monte Carlo on a CPU partition, exhaustive or near-exhaustive evaluation with a fixed, pre-registered Monte Carlo budget per subset is affordable and gives an exact answer with an honest standard error on every subset. Every neural method in this file trades that certainty for speed the user does not need, and pays in bias channels that are invisible from inside the computation. The 2024 survey finding that expensive *combinatorial* problems get far less attention than continuous ones ([DOAJ](https://doaj.org/article/67ec245433a94c61bf74825c719b6855)) is the field admitting it has not built the tool for this corner.
- **The size at which they become right.** Three conditions, all of which must hold: (1) the ground set exceeds roughly 25-30 elements *and* is not reducible by a cheap screening pass, so that 2^k is beyond 10^7-10^9 and even k-constrained enumeration is out of reach; (2) the per-evaluation cost times the enumeration count exceeds the available compute by more than an order of magnitude, so a surrogate is the only way to get any answer at all; and (3) the question genuinely requires *many* solved instances — many r values, many cohorts, many constraint budgets — so the amortization cost is spread. Below all three, the honest recommendation is a classical exact or greedy method with a certificate, and if a neural component is used at all it should be **LassoNet as a screening pass to shrink the ground set**, with the final selection and the final accuracy both computed by direct simulation on held-out Monte Carlo draws.
- **One reframing worth putting in the report.** `sbi` is the best-maintained package in this file and it answers a different and arguably more important question: whether the synthetic anatomical columns are consistent with the real CT cohort. Using a neural method to pick a subset inside a simulator whose fidelity has not been established optimizes the wrong thing confidently. Validating the simulator against the cohort first is the step that checks the computation against something outside it.

### Gaps
- I found no paper that *measures* surrogate-induced bias in subset selection with a noisy simulated objective — i.e. a study that reports the gap between the surrogate-chosen subset's true value and the enumerated optimum. The Cawley & Talbot result is the closest rigorous statement and it is about model selection on cross-validation estimates, not surrogate-assisted combinatorial search. The transfer is an inference.
- No source quantifies the bias of any specific package named here on a problem of the user's shape. Every bias channel above is reasoned from the method's mechanism plus a documented failure in the method's own literature, not from a measured number on this problem class.
