# Checkpoint — 2026-10-26

Everything from this session is in git. Nothing needed is held only in a thread, a scratch
folder or OneDrive. A new account continues from `git clone` alone.

**Start at `HANDOFF.md`, section "FOR THE NEXT ACCOUNT: run the measure-set study on the Wayne
State grid".** It is a numbered, runnable plan with the Slurm scripts in it. This file is the
record of what changed and why; the handoff is what to do next.

## What this session did

A literature survey asked what mathematical problem the measure-set search actually is and what
software solves it. The answer turned out to be that the software question was the wrong
question — the deficit was in the **inference**, not the optimiser — and fixing that is most of
what changed in the code.

### The problem has a name

**Robust (maximin) discrete optimisation via simulation**, and inside it a **fixed-budget
ranking-and-selection problem over an enumerable candidate set**. The inner continuum over `r`
is a one-variable **semi-infinite program**; the reporting frame is **Manski partial
identification**. The ML name for the same thing is best-arm identification.

### Six commits

| Commit | What changed |
|---|---|
| `0db2b14` | `r_between`: an exchangeable between-measure correlation in the generator, with the finding that the literature supplies no value for it and Kunkel 2010 is a near miss (parameter on parameter, but over sixteen *level means*, so reading a within-patient correlation from it is the ecological fallacy) |
| `116940d` | the command documented, and the upper-bound trap recorded as the fifth trap in the handoff |
| `cc8360f` | `r` is unidentified, so report a **Manski identified set** with an **Imbens-Manski** interval, and make the claim about the **sign** of a difference rather than its value; name the crossing `r` when a sign turns over |
| `bdcfd5b` | **measure** the grid's error rather than assert the assumption that bounds it — `A(S, ·)` turned out **not monotone** in `r`, the opposite of what the previous commit asserted |
| `7844707` | **measure** the interval's coverage rather than trust the formula. A 0.02 dip hidden between grid points takes coverage from 0.95 to **0.4242** |
| `400e73a` | one evaluation of `A(S, r)` costs **7.24 s**, measured, and the enumeration table that follows from it |

### The result, stated the honest way

The accuracy is **not** identified; the conclusion drawn from it **is**:

```
C7/T1    difference [+0.2750 at r=0.40, +0.2925 at r=0.00]   IM 95 % [+0.2521, +0.3152]
         worst case over r  +0.2750 +/- 0.0138   (20.0 s.e. from zero)
T12/L1   difference [+0.1154 at r=0.40, +0.1262 at r=0.90]   IM 95 % [+0.0934, +0.1481]
         worst case over r  +0.1154 +/- 0.0130   ( 8.9 s.e. from zero)
```

Seven SPINEPS-measurable measures beat three at **every** `r` on the grid. The *size* of the
gain is unknown; the *direction* is not. Quote the worst case over `r` and the interval, never
the `r = 0` figure alone.

### Three things measured that had been assumed

1. **`A(S, ·)` is not monotone in `r`** — at both junctions and for both measure sets. The code
   previously asserted "smooth and near-monotone" from expectation. Refining the grid is **not**
   the check: a narrow dip can survive four refinements identically, and Monte Carlo noise pushes
   the same quantity the other way, so agreement between a coarse and a fine grid is not evidence.
2. **A hidden dip of 0.02 destroys the interval's coverage** (0.95 → 0.4242). Two accuracy points,
   invisible in a printed table. This is why the accuracy interval is reported as **uncertified**.
   The *sign* claim survives, because overturning it would need a dip of 0.1154–0.2750 — five to
   fourteen times larger, and grossly visible. A test asserts that ratio.
3. **`A` is the simulator, at 7.24 s per evaluation.** The closed-form Gaussian separability runs
   about 290,000 times faster and is **a different function**, not a cheap version of this one. It
   screens; the simulator decides. Never quote them interchangeably — that substitution is the
   same shape as the two this project has already made (a maximum extent for a diameter, a
   first-slice-that-works for a plane).

### New in this checkpoint's commit

`run.py enumerate` — score **every** subset at every `r`, sharded for a Slurm array job, with
`--gather` to merge and rank. At these counts exhaustive enumeration is the right method: exact,
no optimality gap, and it returns the whole ranked distribution rather than an argmax. It also
answers whether `A` is monotone in `S`, counting only drops that clear 2 s.e. so that Monte Carlo
scatter is not reported as structure. A pilot at tiny `n` already shows **7 of 18 supersets
scoring lower by more than 2 s.e. at T12/L1**, worst −0.1028 — if that holds at full `n`, adding a
measure can hurt, and every submodular-greedy guarantee is ruled out on its own terms.

## The survey, committed

`research/solver-survey-2026-10-26/` — six parallel literature surveys, then seven adversarial
verifiers whose job was to **refute** the decision-changing claims. **All seven needed
correction.** `INDEX.md` is the map; `REPORT.md` is the synthesis with corrections folded in;
`adversarial-verification.txt` is the authority wherever it conflicts with a notes file.

The three findings most likely to save someone a day:

- **`sim-tools` 1.3.0 (MIT) is the one package to adopt**, for OCBA/OCBA-m/KN/KN++ — but every
  commit touching its `ovs` module since 2021-07-05 is formatting and the module has **no tests**.
  2021 code under a 2026 version string. Pin the commit and write your own tests.
- **Do not claim a `(1 - 1/e)` guarantee.** Value of information is not submodular even in Naive
  Bayes models (Krause & Guestrin, JAIR 35, Proposition 9), and measured submodularity ratios for
  this objective were 0.017–0.086, i.e. a guarantee of 2–9 % of optimum.
- **Package-name traps that install the wrong software**: `pip install bounce` gets a keyword
  search engine that imports cleanly; `apricot-select` ships 2021 code under the same version
  string as a 2025 master whose commits changed argsort tie-breaking and RNG seeding; `submodlib`
  is on PyPI as `submodlib-py` (wheels only, no Windows build); `spectral.algorithms.log_det` is
  unguarded and returned 2.3e16 where the true log-determinant was −149.1.

## Still open, and who can close it

| Question | Who | How |
|---|---|---|
| Is `A(·, r)` monotone in `S` at full `n`? | the grid | `run.py enumerate` then `--gather`, step 2-3 of the handoff |
| Is the reported metric a per-`r` accuracy, or a pooled quantity with a threshold tuned on the whole cohort? | the owner | decides whether the worst case sits at an endpoint or strictly inside |
| What is `A`'s true Lipschitz constant in `r`? | the grid | step 4, the 19-point grid |
| Does OCBA find the true best? | the grid | step 5, against the enumeration as ground truth |
| Has anyone published this objective as a mixed-integer conic program? | a literature search | eight arXiv phrase searches returned nothing; the statistics and OR journal literature on cardinality-constrained discriminant analysis was **not** searched. Treat as unrefuted, not established |

Two negatives that *are* settled, and can go into a methods section as sweeps rather than
spot-checks: **no CRAN package implements Imbens-Manski** (full-text sweep of all 25,529 packages
for "Manski" or "Imbens" — zero hits), and **no maintained standalone ranking-and-selection or
OCBA package exists** (sweep of the same index; `irace` is the only live CRAN package with a
noisy-selection elimination rule).

## State of the tests

70 tests, 69 passing. The one error is `test_junction_figures.JunctionFigures` in `setUpClass`, a
matplotlib colour fault present on `origin/main` independently of any of this work. It is not
ours to fix and it is not a regression.
